# 🔐 Auth Anomaly Detection PoC

AI-powered anomaly detection for authentication & authorization logs.  
Identifies compromised credentials, insider threats, privilege abuse, and account takeover attempts using **4-model ensemble** machine learning.

## 🤖 ML Models - 4-Model Ensemble

**Ensemble Performance:** ⭐ **ROC-AUC: 0.8884** (88.84% discrimination)

Combines 4 semi-supervised algorithms:

1. **Label Propagation** — Semi-supervised, leverages unlabeled data
2. **Label Spreading** — Similar to LP, smooth label transitions
3. **Self-Training Random Forest** — Iterative pseudo-labeling, strong baseline
4. **Self-Training Extra Trees** — Balanced, reduces overfitting

**Performance Metrics** (Book1 Test Set):

- **ROC-AUC:** 0.8884 ⭐ (excellent discrimination)
- **F1-Score:** 0.4091
- **Recall:** 0.4286 (catches ~43% of anomalies)
- **Accuracy:** 89.60%
- **Test Size:** 1,000 events

**Trained on:** Book1.xlsx (4,999 authentication logs, ~20% anomalies)

## 📋 6 Core Requirements - All Implemented

| #     | Requirement                       | How It Works                                                                        |
| ----- | --------------------------------- | ----------------------------------------------------------------------------------- |
| **1** | 📥 **Ingest & Process Logs**      | 📤 Data Ingestion tab — Upload CSV/XLSX, auto-parse, validate, extract features     |
| **2** | 👤 **Baseline Behavior Profiles** | 👤 Baseline Profiles tab — Enter user_id to see typical hours, locations, resources |
| **3** | 🤖 **Anomaly Detection (ML)**     | 🧩 Ensemble Models tab — 4-model ensemble with 88.84% ROC-AUC                       |
| **4** | 🎯 **Risk Scores & Alerts**       | 🔍 Anomaly Explorer tab — 0-100 scale, 4 severity levels (🟢🟡🟠🔴)                 |
| **5** | 📊 **Interactive Visualizations** | All tabs — Charts, tables, metrics, expandable details                              |
| **6** | 💡 **Explanations for Anomalies** | 🔍 Anomaly Explorer tab — Click expand to see WHY flagged + recommendations         |

## ⚡ Quick Start (2 minutes)

```bash
# Navigate to project
cd seminarr

# Activate virtual environment
source .venv/bin/activate    # Mac/Linux
.venv\Scripts\activate       # Windows

# Start dashboard (NB: pre-trained models included)
streamlit run dashboard/app.py --server.port 8501
```

Then open: **http://localhost:8501**

**Start with:** 🔍 **Anomaly Explorer** tab → Click expand to see explanations

## 🎯 Dashboard Tabs (All 6 Requirements)

### 📊 Overview Tab

- System status & quick reference
- Map of all 6 requirements
- Direct "Go to" links to relevant tabs

### 🔍 Anomaly Explorer Tab ⭐ **MOST IMPORTANT**

- Displays top 50 anomalies sorted by risk
- **Click expand** to see explanations:
  - ❓ Why was this flagged?
  - 🔧 Contributing factors (feature importance)
  - 📚 Similar historical events
  - 💡 Recommended actions
  - 🎯 Risk gauge (🟢🟡🟠🔴)

### 👤 Baseline Profiles Tab

- Enter any user_id
- See typical hours (chart)
- See typical locations & resources
- See normal failure rate
- Highlights deviations

### 🧩 Ensemble Models Tab

- Model performance metrics (ROC-AUC, F1, Recall, Accuracy)
- Per-model comparison (all 4 models)
- Weight allocation visualization
- Score new datasets

### 📤 Data Ingestion Tab

- Upload CSV/XLSX with your logs
- Automatic parsing & validation
- Feature extraction preview
- "Ingest into System" button
- Real-time scoring with ensemble

### 📈 Advanced Details Tab

- Database statistics
- Feature engineering reference
- System configuration

## 🔄 Retrain Ensemble on Custom Data

```bash
# Train 4-model ensemble on custom Book1 dataset
python scripts/train_rba_ensemble.py
```

## 🐳 Docker

```bash
docker-compose up --build
```

## 📚 Documentation

- [Quick Start Guide](QUICK_START.md) ⭐ **START HERE**
- [Implementation Overview](IMPLEMENTATION_OVERVIEW.md) — Detailed requirement mapping
- [Requirements Checklist](REQUIREMENTS_CHECKLIST.md) — Verification checklist
- [Architecture](docs/architecture.md)
- [Project Structure](docs/project-structure.md)
- [Workflow](docs/workflow.md)
- [API Reference](docs/api-reference.md)
- [Setup Guide](docs/setup.md)
- [Okta Event Hook Setup](docs/okta_event_hook_setup.md)
- [Model Evaluation Report](docs/model_evaluation_report.md) — Ensemble performance

## 🔑 Environment Setup

### For Dashboard Only (Recommended)

No environment variables needed. Pre-trained models included.

### For API + Okta Integration

```bash
cp .env.example .env
# Edit .env to add your Okta hook secret
```

Then set:

```env
OKTA_EVENT_HOOK_AUTH_SECRET=your-secret
OKTA_EVENT_HOOK_AUTH_HEADER=authorization
```

Do not commit your real `.env` file to source control.
