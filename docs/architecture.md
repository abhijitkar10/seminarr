# Architecture

## System Overview

```mermaid
graph LR
    subgraph Input Sources
        A[CSV Upload] -->|parse| B[CSV Parser]
        C[Stream Simulator] -->|HTTP POST| D[FastAPI /ingest]
        E[Okta Logs] -->|HTTP POST| F[FastAPI /ingest/okta]
    end

    subgraph Processing Pipeline
        B --> G[Event Ingestion]
        D --> G
        F --> G
        G -->|store| H[(SQLite DB)]
        G --> I[Feature Engineering]
        I -->|store| H
        I --> J[Anomaly Detector]
        J -->|Isolation Forest| K[Risk Scoring]
        K -->|store anomalies| H
        K --> L[Alert Engine]
    end

    subgraph Output
        L -->|console / email| M[Alerts]
        H --> N[Streamlit Dashboard]
        N --> O[Activity View]
        N --> P[Anomaly View]
        N --> Q[User Profiles]
        N --> R[Trend Charts]
    end
```

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant D as Dashboard
    participant P as CSV Parser
    participant DB as SQLite
    participant F as Feature Engine
    participant ML as Isolation Forest
    participant A as Alert Engine

    U->>D: Upload CSV
    D->>P: parse_csv(file)
    P-->>D: rows, errors
    D->>DB: insert_events(rows)
    D->>F: compute_features(row)
    F->>DB: query user history
    F-->>D: feature vectors
    D->>DB: insert_features()
    U->>D: Click "Train Model"
    D->>ML: train()
    ML->>DB: fetch features (≤2000)
    ML-->>D: model saved (joblib)
    U->>D: Click "Score All"
    D->>ML: score_event(features)
    ML-->>D: score, contributions
    D->>A: maybe_send_alert()
    D->>DB: record_anomaly()
```

## Components

| Component | Tech | Role |
|-----------|------|------|
| API | FastAPI + Uvicorn | REST endpoints for ingestion, scoring, queries |
| Dashboard | Streamlit | Web UI — upload, train, visualize |
| ML Engine | scikit-learn Isolation Forest | Unsupervised anomaly detection |
| Feature Engine | Python + SQLite queries | Temporal, geo, behavioral feature extraction |
| Storage | SQLite | Events, features, anomalies, alerts |
| Alerting | Console + SMTP | Risk-based notifications |
| Adapters | CSV parser, Okta normalizer | Multi-format log ingestion |

## ML Model

- **Algorithm:** Isolation Forest (unsupervised)
- **Contamination:** 5% (tunable)
- **Features (8):** hour, day_of_week, geo_distance_km, geo_velocity_kmh, failure_burst, resource_rarity, new_device, off_hours
- **Risk scoring:** Weighted sum of anomaly score + rule-based bonuses (off-hours, velocity, failures, rare resources, new devices)
- **Persistence:** joblib — train once, score repeatedly
