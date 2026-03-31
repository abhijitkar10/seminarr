# Project Structure

```
seminarr/
├── README.md                   # Quick start & overview
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container build
├── docker-compose.yml          # Multi-service orchestration
├── problemStatement.md         # Original problem statement
│
├── app/
│   ├── __init__.py
│   └── main.py                 # FastAPI app — REST endpoints
│
├── dashboard/
│   └── app.py                  # Streamlit dashboard (5 tabs)
│
├── ml/
│   ├── __init__.py
│   ├── detector.py             # Isolation Forest training, scoring, persistence
│   ├── features.py             # Feature engineering (temporal, geo, behavioral)
│   └── baseline.py             # User behavior baseline profiles
│
├── adapters/
│   ├── __init__.py
│   ├── csv_parser.py           # CSV log file parser + validator
│   └── okta.py                 # Okta System Log normalizer
│
├── alerting/
│   ├── __init__.py
│   └── alerts.py               # Risk-based alerting (console + email)
│
├── models/
│   ├── __init__.py
│   └── schemas.py              # Pydantic models (AuthEvent, Anomaly, etc.)
│
├── data/
│   ├── __init__.py
│   ├── db.py                   # SQLite database layer
│   ├── store.sqlite            # Database file (auto-created)
│   ├── model.joblib            # Trained model (auto-created)
│   └── sample_logs.csv         # Sample CSV for upload demo
│
├── scripts/
│   ├── generate_sample_csv.py  # Generate sample_logs.csv
│   ├── generate_logs.py        # Batch seed via API
│   └── stream_simulator.py     # Continuous real-time event stream
│
├── tests/
│   ├── conftest.py             # Pytest path setup
│   ├── test_detector.py        # ML detector tests
│   └── test_features.py        # Feature engineering tests
│
└── docs/
    ├── architecture.md         # System architecture + Mermaid diagrams
    ├── project-structure.md    # This file
    ├── workflow.md             # User workflow walkthrough
    ├── api-reference.md        # API endpoint reference
    └── setup.md                # Setup & deployment guide
```
