# Setup Guide

## Option 1: Local (venv)

### Prerequisites
- Python 3.10+

### Steps

```bash
# Clone / navigate to project
cd seminarr

# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Generate sample CSV (optional)
python scripts/generate_sample_csv.py
```

### Run

Terminal 1 — API:
```bash
uvicorn app.main:app --reload --port 8000
```

Terminal 2 — Dashboard:
```bash
streamlit run dashboard/app.py --server.port 8501
```

### Environment configuration

Copy the example environment file and set your Okta hook secret:

```bash
cp .env.example .env
```

Then edit `.env` and set:

```env
OKTA_EVENT_HOOK_AUTH_SECRET=your-okta-hook-secret
OKTA_EVENT_HOOK_AUTH_HEADER=authorization
```

### Access
- Dashboard: http://localhost:8501
- API Swagger: http://localhost:8000/docs

---

## Option 2: Docker

### Prerequisites
- Docker + Docker Compose

### Steps

```bash
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
