# Project Structure

```
seminarr/
├── README.md                        # Quick start & overview ⭐ START HERE
├── QUICK_START.md                   # Quick reference guide
├── IMPLEMENTATION_OVERVIEW.md       # Detailed implementation
├── REQUIREMENTS_CHECKLIST.md        # Requirements verification
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Container build
├── docker-compose.yml               # Multi-service orchestration
├── problemStatement.md              # Original problem statement
│
├── app/
│   ├── __init__.py
│   └── main.py                      # FastAPI app
│
├── dashboard/
│   └── app.py                       # Streamlit dashboard (6 tabs) ⭐ CORE
│
├── ml/
│   ├── __init__.py
│   ├── detector.py                  # Anomaly detection
│   ├── features.py                  # Feature engineering (12 features)
│   ├── baseline.py                  # User baseline profiles
│   ├── rba_ensemble.py              # 4-model ensemble
│   └── labeled_propagation_model.py # LP model
│
├── adapters/
│   ├── __init__.py
│   ├── csv_parser.py                # CSV parser + validator
│   └── okta.py                      # Okta normalizer
│
├── alerting/
│   ├── __init__.py
│   └── alerts.py                    # Risk-based alerting
│
├── models/
│   ├── __init__.py
│   └── schemas.py                   # Pydantic models
│
├── data/
│   ├── __init__.py
│   ├── db.py                        # Database layer
│   ├── store.sqlite                 # Database file
│   ├── rba_*.joblib                 # Pre-trained ensemble ⭐
│   └── sample_logs.csv              # Sample data
│
├── scripts/
│   ├── train_rba_ensemble.py        # Train 4-model ensemble
│   ├── train_labeled_propagation.py # Train LP
│   ├── generate_sample_csv.py       # Generate samples
│   ├── stream_simulator.py          # Event stream
│   └── ...
│
├── tests/
│   ├── conftest.py
│   ├── test_detector.py
│   ├── test_features.py
│   └── test_okta_hook.py
│
└── docs/
    ├── architecture.md              # System design ⭐ UPDATED
    ├── project-structure.md         # This file
    ├── workflow.md                  # User workflows ⭐ UPDATED
    ├── api-reference.md
    ├── setup.md                     # Setup guide ⭐ UPDATED
    ├── okta_event_hook_setup.md
    ├── labeled_propagation_deployment.md
    └── model_evaluation_report.md
```
