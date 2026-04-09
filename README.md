# Auth Anomaly Detection PoC

AI-powered anomaly detection for authentication & authorization logs.  
Identifies compromised credentials, insider threats, privilege abuse, and account takeover attempts using **Labeled Propagation** semi-supervised machine learning.

## ML Model

### Labeled Propagation ⭐
- **Accuracy: 73.60%** - Classified correctly
- **Recall: 82.14%** - Catches most anomalies
- **Precision: 21.94%** - Manageable false positive rate
- **ROC-AUC: 0.8195** - Excellent discrimination
- Semi-supervised learning leverages both labeled and unlabeled data
- Trained on Book2.xlsx (49,999 authentication logs, 9.04% anomalies)

## Getting Started

1. Copy `.env.example` into `.env`.
2. Fill in your Okta hook secret in `.env`.
3. Start the API and dashboard locally.
4. Follow the detailed Okta setup guide in `docs/okta_event_hook_setup.md`.

## Training Model on Sample Data

### Train Labeled Propagation on Current Dataset
```bash
# Requires pre-labeled data (Is Attack IP, Is Account Takeover, etc.)
python scripts/train_on_book2.py
```

### Results from Book2.xlsx Dataset
- **Setup:** 49,999 authentication logs, stratified 80/20 train/test split
- **Performance:** 73.60% Accuracy, 82.14% Recall, 21.94% Precision
- **Anomaly Rate:** 9.04% (4,519 anomalies out of 49,999 events)

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
- [Okta Event Hook Setup](docs/okta_event_hook_setup.md)
- **[Model Evaluation Report](docs/model_evaluation_report.md)** ← Labeled Propagation Performance

## Environment setup

Copy `.env.example` to `.env` and set your local Okta hook secret before running the API:

```bash
cp .env.example .env
# then edit .env to add your real secret
```

Do not commit your real `.env` file to source control.
