# Auth Anomaly Detection PoC

AI-powered anomaly detection for authentication & authorization logs.  
Identifies compromised credentials, insider threats, privilege abuse, and account takeover attempts using **Labeled Propagation** semi-supervised ML (primary) and Isolation Forest (fallback).

## ML Models Available

### Labeled Propagation (Recommended) ⭐
- **Recall: 82.14%** - Catches most anomalies
- **F1 Score: 0.3433** - Best overall performance
- **ROC-AUC: 0.8195** - Excellent discrimination
- Semi-supervised learning leverages both labeled and unlabeled data
- Trained on Book1.xlsx (4,999 authentication logs)

### IsolationForest (Fallback)
- **Recall: 11.90%** - Conservative approach
- **F1 Score: 0.1124**
- **ROC-AUC: 0.5917**
- Unsupervised, works with any data

**See [Model Evaluation Report](docs/model_evaluation_report.md) for detailed comparison**

## Getting Started

1. Copy `.env.example` into `.env`.
2. Fill in your Okta hook secret in `.env`.
3. Start the API and dashboard locally.
4. Follow the detailed Okta setup guide in `docs/okta_event_hook_setup.md`.

## Training Models on Sample Data

### Train Labeled Propagation on Book1.xlsx
```bash
# Requires pre-labeled data (Is Attack IP, Is Account Takeover, etc.)
python scripts/train_labeled_propagation.py
```

### Train Both Models and Compare
```bash
# Trains IsolationForest AND Labeled Propagation on identical data
python scripts/train_both_models.py
```

### Results from Book1.xlsx Dataset
- **Setup:** 4,999 authentication logs, 80/20 train/test split
- **Winner:** Labeled Propagation with 205% better F1 score
- **Anomaly Rate:** 8.42% (421 attack IPs out of 4,579 normal)

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
- **[Model Evaluation Report](docs/model_evaluation_report.md)** ← Labeled Propagation vs IsolationForest

## Environment setup

Copy `.env.example` to `.env` and set your local Okta hook secret before running the API:

```bash
cp .env.example .env
# then edit .env to add your real secret
```

Do not commit your real `.env` file to source control.
