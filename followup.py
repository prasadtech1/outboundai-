"""
followup.py — WhatsApp & SMS follow-up via Twilio
"""
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("followup")

try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("Twilio not installed. Run: pip install twilio")

import database
import config


def _get_client():
    if not TWILIO_AVAILABLE:
        raise RuntimeError("Twilio not installed. pip install twilio")
    sid   = config.TWILIO_ACCOUNT_SID
    token = config.TWILIO_AUTH_TOKEN
    if not sid or not token:
        raise ValueError("TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN not set in .env")
    return TwilioClient(sid, token)


def send_whatsapp(to_number: str, message: str) -> str:
    """Send WhatsApp message. to_number should be E.164 format e.g. +919876543210"""
    client = _get_client()
    # Ensure format
    if not to_number.startswith("+"):
        to_number = "+" + to_number
    msg = client.messages.create(
        from_=config.TWILIO_WHATSAPP_FROM,
        to   =f"whatsapp:{to_number}",
        body =message,
    )
    logger.info(f"WhatsApp sent to {to_number}: SID={msg.sid}")
    return msg.sid


def send_sms(to_number: str, message: str) -> str:
    """Send SMS. to_number should be E.164 format."""
    client = _get_client()
    if not to_number.startswith("+"):
        to_number = "+" + to_number
    from_number = config.TWILIO_SMS_FROM
    if not from_number:
        raise ValueError("TWILIO_SMS_FROM not set in .env")
    msg = client.messages.create(
        from_=from_number,
        to   =to_number,
        body =message,
    )
    logger.info(f"SMS sent to {to_number}: SID={msg.sid}")
    return msg.sid


def send_followup(phone_number: str, message: str, call_id: int = None, method: str = "whatsapp"):
    """
    Send follow-up message after a call.
    method: 'whatsapp' | 'sms' | 'both'
    """
    if not TWILIO_AVAILABLE:
        logger.warning("Twilio not available — skipping follow-up")
        return

    success = False
    try:
        if method in ("whatsapp", "both"):
            send_whatsapp(phone_number, message)
            success = True
        if method in ("sms", "both"):
            send_sms(phone_number, message)
            success = True
    except Exception as e:
        logger.error(f"Follow-up failed for {phone_number}: {e}")

    if call_id and success:
        database.update_call(call_id, followup_sent=1)
        logger.info(f"Follow-up marked sent for call #{call_id}")


# ── CLI for testing ────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python followup.py <phone> <message> [whatsapp|sms|both]")
        sys.exit(1)

    phone   = sys.argv[1]
    message = sys.argv[2]
    method  = sys.argv[3] if len(sys.argv) > 3 else "whatsapp"
    send_followup(phone, message, method=method)
