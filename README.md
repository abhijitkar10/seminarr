# Auth Anomaly Detection PoC

AI-powered anomaly detection for authentication & authorization logs.  
Identifies compromised credentials, insider threats, privilege abuse, and account takeover attempts using Isolation Forest ML.

## Quick Start

```bash
# 1. Create venv
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start API server
uvicorn app.main:app --reload --port 8000

# 4. Start dashboard (new terminal, same venv)
streamlit run dashboard/app.py --server.port 8501
```

**Then open:**
- Dashboard: http://localhost:8501
- API docs: http://localhost:8000/docs

## Usage

1. **Upload** — Go to the Upload tab, download the sample CSV, upload your logs
2. **Train** — Click "Train Model" (needs ≥50 events)
3. **Score** — Click "Score All Events"
4. **Review** — Check Anomalies, Activity, Users, and Trends tabs

## Docker

```bash
docker-compose up --build
```

## Docs

- [Architecture](docs/architecture.md)
- [Project Structure](docs/project-structure.md)
- [Workflow](docs/workflow.md)
- [API Reference](docs/api-reference.md)
- [Setup Guide](docs/setup.md)
