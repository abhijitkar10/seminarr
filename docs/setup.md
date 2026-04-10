# Setup Guide

## ⚡ Quick Start (30 seconds)

**Just want to see it work?**

```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
source .venv/bin/activate
streamlit run dashboard/app.py --server.port 8501
```

Then open: **http://localhost:8501**

Pre-trained models are included! Start with 🔍 **Anomaly Explorer** tab.

---

## Option 1: Local (venv)

### Prerequisites

- Python 3.10+
- macOS, Linux, or Windows

### Steps

```bash
# Clone / navigate to project
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr

# Create virtual environment
python3 -m venv .venv

# Activate
source .venv/bin/activate        # Mac/Linux
.venv\Scripts\activate           # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Run Dashboard Only (Recommended)

```bash
streamlit run dashboard/app.py --server.port 8501
```

Then open: http://localhost:8501

### Run API + Dashboard (Optional, for Okta integration)

Terminal 1 — API:

```bash
uvicorn app.main:app --reload --port 8000
```

Terminal 2 — Dashboard:

```bash
streamlit run dashboard/app.py --server.port 8501
```

Access:

- Dashboard: http://localhost:8501
- API Swagger: http://localhost:8000/docs

### Environment Configuration (Optional, for Okta)

```bash
cp .env.example .env
```

Then edit `.env` and set:

```env
OKTA_EVENT_HOOK_AUTH_SECRET=your-okta-hook-secret
OKTA_EVENT_HOOK_AUTH_HEADER=authorization
```

**Do NOT commit your real `.env` file to source control.**

---

## Option 2: Docker

### Prerequisites

- Docker + Docker Compose

### Steps

```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
docker-compose up --build
```

### Access

- Dashboard: http://localhost:8501
- API: http://localhost:8000/docs

### Stop

```bash
docker-compose down
```

---

## Optional: Email Alerts

Set these environment variables to enable email notifications:

```bash
ALERT_EMAIL_TO=security-team@corp.com
ALERT_EMAIL_FROM=anomaly-detector@corp.com
SMTP_HOST=smtp.corp.com
```

Without these, alerts are console-only (still stored in DB and visible in dashboard).

---

## Optional: Stream Simulator

Simulate real-time event flow against the API:

```bash
python scripts/stream_simulator.py --rps 2 --anomaly-prob 0.1
```

Flags:

- `--rps` — events per second (default: 2)
- `--anomaly-prob` — fraction of anomalous events (default: 0.1)
- `--url` — API endpoint (default: http://localhost:8000/ingest)
