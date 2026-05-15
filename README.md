# 🤖 OutboundAI — AI Voice Calling Platform

> Gemini Live AI · Outbound SIP Calls · Appointments · Campaigns · CRM · Dashboard

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎙 Gemini Live AI | Sub-100ms latency, no separate STT/TTS needed |
| 📞 Outbound Calls | Auto-dials via Vobiz SIP trunk |
| 📅 Appointments | Books into Supabase + Cal.com |
| 🚀 Campaigns | Bulk CSV calling with APScheduler |
| 🧠 CRM + Memory | Remembers each lead across calls |
| 🎙 Recording | Saves to S3-compatible storage |
| 📲 WhatsApp/SMS | Auto follow-up after each call (Twilio) |
| 🤖 Agent Profiles | Different voice/prompt/tools per campaign |
| 📊 Dashboard | 12-tab full SPA — Stats, Logs, CRM, Settings |
| 🗄 Supabase | PostgreSQL — zero local SQLite in production |
| 🐳 Docker | One-command deploy via Coolify |

---

## 📁 File Structure

```
OutboundAI/
├── agent.py              ← LiveKit worker — Gemini Live AI entrypoint
├── server.py             ← FastAPI REST API + APScheduler
├── db.py                 ← All Supabase async DB operations
├── tools.py              ← 9 LLM function tools
├── prompts.py            ← System prompt template
├── followup.py           ← WhatsApp/SMS follow-up (Twilio)
├── bulk_call.py          ← CSV bulk calling script
├── start.sh              ← Production startup script
├── Dockerfile            ← Docker build
├── requirements.txt      ← All Python dependencies
├── supabase_schema.sql   ← Run once in Supabase SQL Editor
├── .env.example          ← All environment variables
├── .gitignore
└── ui/
    └── index.html        ← Single-file dashboard (12 tabs)
```

---

## 🚀 Quick Start

### 1. Install
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Setup Database
- Supabase.com वर जा → SQL Editor → `supabase_schema.sql` paste करा → Run

### 3. Configure
```bash
cp .env.example .env
# .env file मध्ये API keys भरा
```

### 4. Run
```bash
# Terminal 1 — FastAPI Server
uvicorn server:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — AI Agent Worker
python agent.py start
```

### 5. Dashboard
Browser मध्ये उघडा: `http://localhost:8000`

---

## 📞 Calls

### Single Call (API)
```bash
curl -X POST http://localhost:8000/api/call \
  -H "Content-Type: application/json" \
  -d '{"phone":"+919876543210","lead_name":"Rahul","business_name":"My School","service_type":"Admission"}'
```

### Bulk Calling (CSV)
```bash
python bulk_call.py --csv contacts.csv --delay 5
```

**CSV Format:**
```csv
phone,lead_name,business_name,service_type
+919876543210,Rahul Sharma,My School,Admission
+919123456789,Priya Mehta,My School,Admission
```

### WhatsApp Follow-up Test
```bash
python followup.py +919876543210 "Your appointment is confirmed!" whatsapp
```

---

## 🔑 Required APIs

| Service | Purpose | Free Tier |
|---|---|---|
| [LiveKit Cloud](https://cloud.livekit.io) | Voice rooms + SIP | ✅ 100k min/mo |
| [Google AI Studio](https://aistudio.google.com) | Gemini Live AI | ✅ Free |
| [Supabase](https://supabase.com) | Database | ✅ Free |
| [Vobiz](https://vobiz.ai) | Phone calls (SIP) | Paid ~₹1/min |
| [Twilio](https://twilio.com) | WhatsApp/SMS | ✅ $15 trial |
| [Cal.com](https://cal.com) | Calendar | ✅ Optional |

**Total per call: ≈ ₹1.20–2.40**

---

## 🐳 Deploy (Coolify)

1. VPS वर Coolify install करा: `curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash`
2. New Resource → GitHub Repo → Dockerfile auto-detected
3. All `.env` variables set करा
4. Port: `8000`
5. Deploy → Dashboard उघडा → Settings → API keys fill करा → ⚡ Create SIP Trunk

---

## 🎙 Available AI Voices (Gemini Live)

**Female:** Aoede ⭐, Achernar, Autonoe, Callirrhoe, Despina, Erinome, Gacrux, Kore, Laomedeia, Leda, Pulcherrima, Sulafat, Vindemiatrix, Zephyr

**Male:** Achird, Algenib, Algieba, Alnilam, Charon, Enceladus, Fenrir, Iapetus, Orus, Perseus, Puck, Rasalgethi, Sadachbia, Sadaltager, Schedar, Umbriel, Zubenelgenubi
