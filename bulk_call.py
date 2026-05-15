"""
bulk_call.py — Bulk outbound calling via CSV
Usage: python bulk_call.py --csv contacts.csv --persona school_receptionist --delay 5
"""
import argparse
import asyncio
import csv
import json
import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("bulk-caller")

from livekit import api as lkapi
import config
import database

database.init_db()


async def dispatch_call(lk: lkapi.LiveKitAPI, phone: str, persona_id: str, extra_meta: dict = None) -> str:
    """Create a LiveKit room and dispatch a job to the agent."""
    room_name = f"call-{phone.replace('+','')}-{int(datetime.utcnow().timestamp())}"
    
    metadata = {
        "phone_number": phone,
        "persona_id":   persona_id,
        **(extra_meta or {}),
    }

    # Create room
    await lk.room.create_room(
        lkapi.CreateRoomRequest(name=room_name, empty_timeout=120, max_participants=2)
    )

    # Dispatch agent job
    await lk.agent_dispatch.create_dispatch(
        lkapi.CreateAgentDispatchRequest(
            room=room_name,
            agent_name="enhanced-ai-voice",
            metadata=json.dumps(metadata),
        )
    )

    logger.info(f"✅ Dispatched: {phone} → Room: {room_name}")
    return room_name


async def run_bulk(csv_path: str, persona_id: str, delay: int, dry_run: bool):
    """Read CSV and dispatch calls with delay between each."""
    # Validate persona
    if persona_id not in config.PERSONAS:
        logger.error(f"Unknown persona: {persona_id}. Choose from: {list(config.PERSONAS.keys())}")
        sys.exit(1)

    # Read contacts
    contacts = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            phone = row.get("phone") or row.get("Phone") or row.get("phone_number") or row.get("PhoneNumber")
            if phone:
                phone = phone.strip()
                if not phone.startswith("+"):
                    phone = "+91" + phone  # default India
                contacts.append({"phone": phone, **row})

    if not contacts:
        logger.error("No contacts found. CSV must have a 'phone' column.")
        sys.exit(1)

    logger.info(f"📋 Loaded {len(contacts)} contacts | Persona: {persona_id} | Delay: {delay}s")
    
    if dry_run:
        logger.info("🔍 DRY RUN — no calls will be made:")
        for c in contacts:
            logger.info(f"  → {c['phone']}")
        return

    # Create bulk job record
    job_id = database.create_bulk_job(
        job_name   = os.path.basename(csv_path),
        persona_id = persona_id,
        total      = len(contacts),
    )
    logger.info(f"Bulk job #{job_id} created")

    # Connect to LiveKit
    lk = lkapi.LiveKitAPI(
        url    = os.getenv("LIVEKIT_URL"),
        api_key    = os.getenv("LIVEKIT_API_KEY"),
        api_secret = os.getenv("LIVEKIT_SECRET"),
    )

    completed, failed = 0, 0

    for i, contact in enumerate(contacts, 1):
        phone = contact["phone"]
        logger.info(f"[{i}/{len(contacts)}] Calling {phone}...")

        try:
            extra = {k: v for k, v in contact.items() if k != "phone"}
            await dispatch_call(lk, phone, persona_id, extra)
            completed += 1
        except Exception as e:
            logger.error(f"❌ Failed to dispatch {phone}: {e}")
            failed += 1

        database.update_bulk_job(
            job_id,
            completed_calls = completed,
            failed_calls    = failed,
            status = "running" if i < len(contacts) else "completed",
        )

        if i < len(contacts):
            logger.info(f"⏳ Waiting {delay}s before next call...")
            await asyncio.sleep(delay)

    database.update_bulk_job(job_id, status="completed")
    logger.info(f"\n🏁 Bulk job #{job_id} done | ✅ {completed} dispatched | ❌ {failed} failed")
    await lk.aclose()


def main():
    parser = argparse.ArgumentParser(description="Bulk AI Voice Caller")
    parser.add_argument("--csv",     required=True,  help="Path to CSV file with 'phone' column")
    parser.add_argument("--persona", default=config.DEFAULT_PERSONA, help=f"Persona ID. Options: {list(config.PERSONAS.keys())}")
    parser.add_argument("--delay",   type=int, default=5, help="Seconds between calls (default: 5)")
    parser.add_argument("--dry-run", action="store_true", help="Preview contacts without making calls")
    args = parser.parse_args()

    asyncio.run(run_bulk(args.csv, args.persona, args.delay, args.dry_run))


if __name__ == "__main__":
    main()
