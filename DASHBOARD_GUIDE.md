# 📊 Dashboard Guide: Web-Based Analytics Interface

## Dashboard Overview

The Streamlit dashboard provides a comprehensive web interface for:
- ✅ Viewing real-time authentication anomalies
- ✅ Understanding user baseline behaviors
- ✅ Evaluating ML model performance
- ✅ Uploading and processing logs
- ✅ Accessing system diagnostics

**Start:** `streamlit run dashboard/app.py --server.port 8501`  
**Access:** http://localhost:8501

---

## 🎨 Dashboard Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Sidebar                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │ 🔐 Auth Anomaly Detection PoC                    │  │
│  │ ─────────────────────────────────────────────────│  │
│  │ 📊 System Status:                               │  │
│  │    • Events ingested: 4,999                     │  │
│  │    • Anomalies detected: 78                     │  │
│  │    • Model trained: ✅                          │  │
│  │                                                 │  │
│  │ 🤖 Model Performance:                           │  │
│  │    • ROC-AUC: 0.8884                            │  │
│  │    • Recall: 42.86%                             │  │
│  │    • Ensemble: 4 Models (LP+LS+RF+ET)          │  │
│  │                                                 │  │
│  │ 📈 Quick Stats:                                 │  │
│  │    • Unique users: 234                          │  │
│  │    • Resources: 12                              │  │
│  │    • Locations: 45                              │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
│
├─ 📊 Overview                TAB 1 (Selected)
├─ 🔍 Anomaly Explorer        TAB 2 ⭐ CORE
├─ 👤 Baseline Profiles       TAB 3
├─ 🧩 Ensemble Models         TAB 4
├─ 📤 Data Ingestion          TAB 5
└─ 📈 Advanced Details        TAB 6
```

---

## TAB 1: 📊 Overview

**Purpose:** Quick reference to all 6 core requirements

### Content

```
┌─────────────────────────────────────────────────────────┐
│ 📊 OVERVIEW - System Status & Requirements              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 🎯 6 CORE REQUIREMENTS STATUS                          │
│ ─────────────────────────────────────────────────────  │
│                                                         │
│ 1️⃣  📥 INGEST & PROCESS LOGS                           │
│     ✅ Complete                                         │
│     • CSV/XLSX upload support                          │
│     • Automatic parsing & validation                   │
│     • Feature extraction (12 features)                 │
│     [Go to 📤 Data Ingestion →]                        │
│                                                         │
│ 2️⃣  👤 BASELINE BEHAVIOR PROFILES                      │
│     ✅ Complete                                         │
│     • Typical login hours (chart)                      │
│     • Typical locations (list)                         │
│     • Normal resources accessed                        │
│     • Failure rate tracking                            │
│     [Go to 👤 Baseline Profiles →]                     │
│                                                         │
│ 3️⃣  🤖 ANOMALY DETECTION (ML)                          │
│     ✅ Complete                                         │
│     • 4-model ensemble (88.84% ROC-AUC)               │
│     • Semi-supervised learning                        │
│     • Real-time scoring                               │
│     [Go to 🧩 Ensemble Models →]                       │
│                                                         │
│ 4️⃣  🎯 RISK SCORES & ALERTS                            │
│     ✅ Complete                                         │
│     • 0-100 risk scale                                 │
│     • 4 severity levels (🟢🟡🟠🔴)                     │
│     • Risk categorization logic                        │
│     [Go to 🔍 Anomaly Explorer →]                      │
│                                                         │
│ 5️⃣  📊 INTERACTIVE VISUALIZATIONS                      │
│     ✅ Complete                                         │
│     • Charts (line, bar, pie)                          │
│     • Tables (sortable, paginated)                     │
│     • Metrics (KPIs, gauges)                           │
│     • Expandable details                               │
│                                                         │
│ 6️⃣  💡 EXPLANATIONS FOR ANOMALIES                      │
│     ✅ Complete                                         │
│     • Why was it flagged? (reasons)                    │
│     • Contributing factors (feature importance)        │
│     • Similar historical events                        │
│     • Recommended actions                              │
│     [Go to 🔍 Anomaly Explorer →]                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Features

- Quick links to each tab
- System status indicators
- Model performance snapshot
- Instructions for first-time users

---

## TAB 2: 🔍 Anomaly Explorer ⭐ CORE FEATURE

**Purpose:** Display detected anomalies with detailed explanations

### Content Structure

```
┌─────────────────────────────────────────────────────────┐
│ 🔍 ANOMALY EXPLORER - Detected Anomalies               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Filters:                                                │
│ ├─ Severity: [All ▼] [🟢 🟡 🟠 🔴]                    │
│ ├─ Date range: [Start Date] [End Date]                 │
│ └─ User ID (optional): [________]                      │
│                                                         │
│ Top 50 Anomalies (sorted by risk):                     │
│ ─────────────────────────────────────────────────────  │
│                                                         │
│ ‣ RISK: 🔴 95/100  |  2024-01-15 03:15  |  user_123   │
│   EVENT DETAILS:                                        │
│   Resource: admin_panel | Action: login | Location: Moscow
│   
│   ▼ EXPAND ANOMALY DETAILS  ▼  ◄─── CLICK HERE       │
│   ┌──────────────────────────────────────────────────┐ │
│   │                                                  │ │
│   │ ❓ WHY WAS THIS FLAGGED?                         │ │
│   │ Multiple high-risk factors detected:            │ │
│   │ • Off-hours access (3 AM - risk +0.8)           │ │
│   │ • Impossible travel (Moscow from NY - risk +0.7)│ │
│   │ • New IP address (risk +0.3)                    │ │
│   │ • Failed attempts before (risk +0.2)             │ │
│   │                                                  │ │
│   │ 🔧 CONTRIBUTING FACTORS (Feature Importance):   │ │
│   │ 1. user_failure_rate:    0.18 (17.8%)           │ │
│   │ 2. temporal_is_off_hours: 0.16 (16.5%)          │ │
│   │ 3. geo_is_new_location:   0.14 (14.2%)          │ │
│   │ 4. resource_failure_rate: 0.13 (12.8%)          │ │
│   │ 5. user_typical_hours:    0.09 (9.5%)           │ │
│   │                                                  │ │
│   │ 📚 SIMILAR HISTORICAL EVENTS:                   │ │
│   │ • 2024-01-10: user_123 failed 3x from NY        │ │
│   │ • 2023-12-20: user_123 accessed from EU (VPN)   │ │
│   │ • Result: Both reviewed manually, benign        │ │
│   │                                                  │ │
│   │ 💡 RECOMMENDED ACTIONS:                         │ │
│   │ ⚠️  CRITICAL RISK - Recommended Actions:         │ │
│   │    1. Block user immediately                    │ │
│   │    2. Force password reset                      │ │
│   │    3. Alert security team                       │ │
│   │    4. Review recent access logs                 │ │
│   │    5. Check associated IPs                      │ │
│   │                                                  │ │
│   └──────────────────────────────────────────────────┘ │
│                                                         │
│ ‣ RISK: 🟠 72/100  |  2024-01-14 22:30  |  user_456   │
│   EVENT DETAILS:                                        │
│   Resource: database | Action: access | Location: London
│   [EXPAND] ▼                                            │
│                                                         │
│ ‣ RISK: 🟡 35/100  |  2024-01-14 19:15  |  user_789   │
│   ... (more anomalies below)                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Key Features

1. **Top 50 Anomalies List**
   - Sorted by risk score (highest first)
   - Quick event summary: time, user, resource
   - Color-coded severity: 🟢🟡🟠🔴

2. **Expandable Details (Click to Expand)**
   - Event details (ID, timestamp, resource)
   - Risk level with gauge visualization
   - ❓ Why flagged? (specific reasons + risk contributions)
   - 🔧 Contributing factors (feature importance ranked)
   - 📚 Similar historical events (given user context)
   - 💡 Recommended actions (context-aware: block? MFA? monitor?)

3. **Filters & Search**
   - By severity level (All, Low, Medium, High, Critical)
   - By date range
   - By user ID (optional)

4. **SQL Queries to Database**
   ```python
   # Fetch anomalies
   SELECT * FROM anomalies
   ORDER BY risk_score DESC
   LIMIT 50
   
   # Parse reasons from JSON
   reasons = json.loads(anomaly['reasons'])  # List of reasons
   
   # Parse contributing factors
   factors = json.loads(anomaly['contributing_factors'])  # Dict
   
   # Get similar historical events
   SELECT * FROM events
   WHERE user_id = 'user_123'
   ORDER BY timestamp DESC
   LIMIT 10
   ```

---

## TAB 3: 👤 Baseline Profiles

**Purpose:** View user behavior baselines and detect deviations

### Content Structure

```
┌─────────────────────────────────────────────────────────┐
│ 👤 BASELINE PROFILES - User Behavior Analysis           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Enter User ID: [____________] [Search]                 │
│                                                         │
│ USER: user_123                                          │
│ Last seen: 2024-01-15 14:30                            │
│ Total logins: 2,340                                    │
│ Account age: 1,234 days                                │
│ ─────────────────────────────────────────────────────  │
│                                                         │
│ 📊 TYPICAL LOGIN HOURS (Last 90 days):                 │
│ ┌──────────────────────────────────────────────────┐  │
│ │    %                                             │  │
│ │    40 │         ╱╲                               │  │
│ │    30 │        ╱  ╲        ╱╲                   │  │
│ │    20 │   ╱╲  ╱    ╲      ╱  ╲    ╱╲            │  │
│ │    10 │──╱  ╲╱      ╲────╱    ╲──╱  ╲──────      │  │
│ │     0 └────────────────────────────────────      │  │
│ │       0 4 8 12 16 20 24                          │  │
│ │       Hour of Day                                │  │
│ │                                                  │  │
│ │ Peak hours: 9-10 AM (38%) and 2-4 PM (35%)      │  │
│ │ Off-hours: <1% between midnight-6 AM            │  │
│ │ Typical weekday: 9 AM - 6 PM (business hours)   │  │
│ └──────────────────────────────────────────────────┘  │
│                                                         │
│ 📍 TYPICAL LOCATIONS (Geographic Distribution):        │
│ ├─ New York, USA:          85% (2,000 logins)         │
│ ├─ Chicago, USA:            10% (230 logins)          │
│ ├─ San Francisco, USA:       4% (90 logins)           │
│ ├─ Other:                    1% (20 logins)           │
│                                                         │
│ ⚠️  RARE LOCATIONS (Flagged as unusual):               │
│ • Moscow, Russia    (never before!)                   │
│ • London, UK        (1 occurrence - Jan 12)           │
│                                                         │
│ 🔧 TYPICAL RESOURCES ACCESSED:                         │
│ ├─ Salesforce:             450 accesses (38%)         │
│ ├─ SharePoint:             380 accesses (32%)         │
│ ├─ Slack:                  200 accesses (17%)         │
│ ├─ Admin panel:             78 accesses (7%)          │
│ ├─ Database:                42 accesses (4%)          │
│ └─ Other:                   12 accesses (1%)          │
│                                                         │
│ 📈 LOGIN STATISTICS:                                   │
│ ├─ Avg logins/day:         4.2                        │
│ ├─ Typical day:            Tuesday-Thursday           │
│ ├─ Failure rate:           0.8% (uncommon)            │
│ ├─ Days since last login:  1 day (very active)        │
│ └─ Most recent IP:         203.45.12.100              │
│                                                         │
│ 🚨 DEVIATION ALERTS:                                   │
│ ├─ ✓ Normal: Login at 9:30 AM from NYC office        │
│ ├─ ⚠️  Unusual: Login at 3:15 AM from Moscow          │
│ ├─ ⚠️  Unusual: Failed 5x in a row (rare)             │
│ └─ ✓ Normal: Access to Salesforce                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Key Features

1. **User Lookup**
   - Enter user_id to view profile
   - Shows user account details

2. **Visualizations**
   - Login hours distribution (line chart)
   - Geographic distribution (bar chart)
   - Resources accessed (pie chart)

3. **Baseline Statistics**
   - Typical login pattern
   - Normal failure rate
   - Frequency of access
   - Days between logins

4. **Deviation Alerts**
   - Highlights unusual patterns
   - Shows what would be anomalous

### SQL Queries

```python
# Get user baseline
SELECT * FROM users WHERE user_id = 'user_123'

# Parse typical hours from JSON
typical_hours = json.loads(user['typical_hours'])
# {0: 0.0, 1: 0.0, ..., 9: 0.38, 10: 0.35, ..., 23: 0.01}

# Get user's recent events
SELECT * FROM events
WHERE user_id = 'user_123'
ORDER BY timestamp DESC
LIMIT 100
```

---

## TAB 4: 🧩 Ensemble Models

**Purpose:** Review ML model performance and score new data

### Content Structure

```
┌─────────────────────────────────────────────────────────┐
│ 🧩 ENSEMBLE MODELS - ML Performance & Scoring           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 📊 ENSEMBLE PERFORMANCE METRICS                        │
│ ─────────────────────────────────────────────────────  │
│                                                         │
│ ┌────────────────┬────────────┐                        │
│ │ Metric         │ Score      │                        │
│ ├────────────────┼────────────┤                        │
│ │ ROC-AUC        │ 0.8884 ⭐ │ Excellent discrimination│
│ │ F1-Score       │ 0.4091     │ Balanced precision     │
│ │ Recall         │ 0.4286     │ Catches 43% anomalies  │
│ │ Precision      │ 0.3889     │ 39% are true anomalies │
│ │ Accuracy       │ 89.60%     │ Overall correctness    │
│ │ Test Set Size  │ 1,000      │ Well-balanced eval    │
│ └────────────────┴────────────┘                        │
│                                                         │
│ 🗳️  MODEL ENSEMBLE COMPOSITION                          │
│ ─────────────────────────────────────────────────────  │
│                                                         │
│ 4 Models Using Soft Voting:                           │
│                                                         │
│ 1️⃣  Label Propagation (LP)                            │
│    ROC-AUC: 0.8412 | Precision: 0.5625               │
│    Weight: 25% (semi-supervised, leverages unlabeled) │
│                                                         │
│ 2️⃣  Label Spreading (LS)                              │
│    ROC-AUC: 0.8201 | Precision: 0.6111               │
│    Weight: 25% (stable, smooth transitions)           │
│                                                         │
│ 3️⃣  Self-Training Random Forest (ST-RF)               │
│    ROC-AUC: 0.8654 | Precision: 0.6923               │
│    Weight: 25% (handles non-linear, high recall)      │
│                                                         │
│ 4️⃣  Self-Training Extra Trees (ST-ET)                 │
│    ROC-AUC: 0.8521 | Precision: 0.6522               │
│    Weight: 25% (reduces overfitting, generalization) │
│                                                         │
│ Combined Score = (LP + LS + ST-RF + ST-ET) / 4        │
│                                                         │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Per-Model Comparison Table                         │ │
│ ├──────────────┬────────┬──────────┬─────────────────┤ │
│ │ Model        │ Recall │ Precision│ ROC-AUC         │ │
│ ├──────────────┼────────┼──────────┼─────────────────┤ │
│ │ LP           │ 0.375  │ 0.5625   │ 0.8412         │ │
│ │ LS           │ 0.3125 │ 0.6111   │ 0.8201         │ │
│ │ ST-RF        │ 0.5625 │ 0.6923   │ 0.8654         │ │
│ │ ST-ET        │ 0.5625 │ 0.6522   │ 0.8521         │ │
│ │ ENSEMBLE ✅  │ 0.4286 │ 0.3889   │ 0.8884  ⬆️ │ │
│ └──────────────┴────────┴──────────┴─────────────────┘ │
│                                                         │
│ 🎯 SCORE NEW DATA                                      │
│ ─────────────────────────────────────────────────────  │
│                                                         │
│ Upload Dataset:                                        │
│ ┌────────────────────────────────────────────────────┐ │
│ │ 📁 Drop CSV/XLSX file here or click to browse     │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ Scoring will:                                          │
│ 1. Parse CSV file                                     │
│ 2. Validate rows (required columns)                   │
│ 3. Extract features (12 per event)                    │
│ 4. Score with 4-model ensemble                        │
│ 5. Display results in table                           │
│                                                         │
│ [Score Dataset] [Clear]                               │
│                                                         │
│ Sample Results:                                        │
│ ┌─────────────┬───────┬──────────────┬──────────┐     │
│ │ User        │ Risk# │ Severity     │ Ensemble │     │
│ ├─────────────┼───────┼──────────────┼──────────┤     │
│ │ user_123    │ 95    │ 🔴 CRITICAL  │ 0.95     │     │
│ │ user_456    │ 42    │ 🟡 MEDIUM    │ 0.42     │     │
│ │ user_789    │ 15    │ 🟢 LOW       │ 0.15     │     │
│ └─────────────┴───────┴──────────────┴──────────┘     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Key Features

1. **Performance Metrics**
   - ROC-AUC, F1, Recall, Precision, Accuracy
   - Color-coded interpretation

2. **Model Comparison**
   - Individual model performance
   - Why ensemble is better
   - Weight allocation

3. **Batch Scoring**
   - Upload CSV file
   - Get risk scores for all events
   - Export results

---

## TAB 5: 📤 Data Ingestion

**Purpose:** Upload and process new authentication logs

### Content Structure

```
┌─────────────────────────────────────────────────────────┐
│ 📤 DATA INGESTION - Upload & Process Logs               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 📋 REQUIRED COLUMNS:                                    │
│ • user_id       (required) - Username or email         │
│ • timestamp     (required) - ISO format (2024-01-15T10:30:00Z) │
│ • resource      (required) - System/app being accessed │
│ • action        (required) - login, access, modify     │
│ • success       (required) - true/false (1/0)          │
│                                                         │
│ Optional columns:                                       │
│ • device_type   - desktop, mobile, laptop              │
│ • location      - city/country                         │
│ • ip_address    - IPv4/IPv6 address                    │
│ • failure_reason- Why authentication failed            │
│                                                         │
│ [Download Sample CSV]                                   │
│                                                         │
│ 📁 UPLOAD FILE                                          │
│ ┌────────────────────────────────────────────────────┐ │
│ │ 📁 Drop CSV/XLSX file here or click to browse     │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ 👀 DATA PREVIEW (after upload)                         │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Parsed 1,234 rows from authentication_logs.csv    │ │
│ │ ✓ All columns valid                               │ │
│ │ ✓ All timestamps in valid format                  │ │
│ │ ✓ No missing required fields                      │ │
│ │                                                    │ │
│ │ Sample rows:                                       │ │
│ │ user_123 | 2024-01-15T10:30:00Z | admin | login | true │
│ │ user_456 | 2024-01-15T10:31:00Z | db    | access | false│
│ │ user_789 | 2024-01-15T10:32:00Z | slack | login | true  │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ 💾 INGEST INTO SYSTEM                                  │
│ [💾 Ingest & Score] [Cancel]                           │
│                                                         │
│ Processing:                                            │
│ ✓ Validating 1,234 events...                           │
│ ✓ Storing to database (events table)...                │
│ ✓ Extracting features (12 per event)...                │
│ ✓ Storing features (features table)...                 │
│ ✓ Scoring with 4-model ensemble...                     │
│ ✓ Storing anomalies (risk > threshold)...              │
│ ✓ Complete! 78 anomalies detected                      │
│                                                         │
│ 📊 INGESTION SUMMARY                                    │
│ ├─ Events processed:     1,234                         │
│ ├─ Events stored:        1,234                         │
│ ├─ Features extracted:   14,808 (1,234 × 12)          │
│ ├─ Anomalies detected:   78                            │
│ │  ├─ 🟢 LOW:      5                                  │
│ │  ├─ 🟡 MEDIUM:  28                                  │
│ │  ├─ 🟠 HIGH:    32                                  │
│ │  └─ 🔴 CRITICAL: 13                                 │
│ ├─ Users affected:       45                            │
│ ├─ Resources:            8                             │
│ ├─ Locations:            12                            │
│ └─ Processing time:      2.3 seconds                   │
│                                                         │
│ ✅ Anomalies now visible in 🔍 Anomaly Explorer tab   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Key Features

1. **Upload Interface**
   - Drag-and-drop or browse
   - Support for CSV and XLSX

2. **Data Validation**
   - Checks required columns
   - Validates data formats
   - Shows preview

3. **Processing Pipeline**
   - Store events to DB
   - Extract 12 features
   - Score with ensemble
   - Categorize anomalies

4. **Results Summary**
   - Processing statistics
   - Anomaly breakdown (by severity)
   - Link to Anomaly Explorer

### Processing Flow

```python
# Pipeline in dashboard/app.py
def ingest_data(file):
    # 1. Parse CSV
    events = csv_parser.parse(file)
    
    # 2. Validate
    for event in events:
        validate(event)
    
    # 3. Store events
    db.insert_events(events)
    
    # 4. Extract features
    for event in events:
        features = feature_engine.extract(event, db)
        db.insert_features(event_id, features)
    
    # 5. Score with ensemble
    for features in db.get_all_features():
        score = ensemble.score(features)
        risk_score = score * 100
        severity = categorize_risk(risk_score)
        if risk_score > 30:  # Threshold
            db.insert_anomaly(score, severity)
    
    return {
        'events_processed': len(events),
        'anomalies_detected': db.count_anomalies(),
        'by_severity': db.anomalies_by_severity()
    }
```

---

## TAB 6: 📈 Advanced Details

**Purpose:** System diagnostics and configuration reference

### Content Structure

```
┌─────────────────────────────────────────────────────────┐
│ 📈 ADVANCED DETAILS - System Info & Configuration       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 📊 DATABASE STATISTICS                                  │
│ ├─ Total events:           4,999                       │
│ ├─ Anomalies detected:     78                          │
│ ├─ Features computed:      59,988                      │
│ ├─ Unique users:           234                         │
│ ├─ Unique resources:       12                          │
│ ├─ Unique locations:       45                          │
│ ├─ Date range:        2024-01-01 to 2024-01-15        │
│ ├─ Database size:          2.3 MB                      │
│ └─ Last updated:       2024-01-15 15:30:00             │
│                                                         │
│ 🔧 FEATURE ENGINEERING (12 Features)                   │
│ ├─ Temporal Features (3)                               │
│ │  ├─ temporal_hour (0-23) - Hour of day              │
│ │  ├─ temporal_weekday (0-6) - Day of week            │
│ │  └─ temporal_is_off_hours - Business hours flag     │
│ │                                                      │
│ ├─ Geographic Features (2)                             │
│ │  ├─ geo_failed_count - Failed logins from location  │
│ │  └─ geo_is_new_location - Never seen before flag    │
│ │                                                      │
│ ├─ User Behavior Features (4)                          │
│ │  ├─ user_typical_hours - % logins at this hour      │
│ │  ├─ user_failure_rate - User's normal failure %     │
│ │  ├─ user_same_resource_count - Frequency access    │
│ │  └─ user_days_since_login - Activity gap            │
│ │                                                      │
│ ├─ Resource Features (2)                               │
│ │  ├─ resource_failure_rate - Resource's % failures   │
│ │  └─ resource_popularity - # users accessing         │
│ │                                                      │
│ └─ Device Features (1)                                  │
│    └─ device_type_encoded - Device category (coded)   │
│                                                         │
│ ⚙️  SYSTEM CONFIGURATION                                │
│ ├─ Model version:          v1.0 (April 2025)           │
│ ├─ Training dataset:        Book1.xlsx (4,999 rows)    │
│ ├─ Anomaly threshold:      0.30 (30% ensemble score)   │
│ ├─ Risk scale:             0-100                       │
│ ├─ Feature scaling:        Standardization (z-score)   │
│ ├─ Ensemble voting:        Soft voting (probabilities) │
│ │                                                      │
│ ├─ Model files location:                               │
│ │  ├─ rba_lp_model.joblib                              │
│ │  ├─ rba_ls_model.joblib                              │
│ │  ├─ rba_st_rf_model.joblib                           │
│ │  ├─ rba_st_et_model.joblib                           │
│ │  └─ rba_ensemble_meta.joblib                         │
│ │                                                      │
│ ├─ Database location:       data/store.sqlite           │
│ └─ API endpoint:           http://localhost:8000/docs  │
│                                                         │
│ 🚀 DEPLOYMENT INFO                                      │
│ ├─ Framework:              Streamlit                    │
│ ├─ Port:                   8501 (default)               │
│ ├─ Python version:         3.10+                        │
│ ├─ ML framework:           scikit-learn                 │
│ ├─ Database:               SQLite                       │
│ └─ API framework:          FastAPI (optional)           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Key Features

1. **Database Statistics**
   - Event counts, anomaly counts
   - User/resource/location diversity
   - Database size and last update

2. **Feature Reference**
   - All 12 features explained
   - How they're computed
   - Why they matter

3. **Configuration**
   - Model version and paths
   - Threshold settings
   - Deployment details

---

## 🎯 Usage Workflows

### Workflow 1: View Pre-Trained Results (5 min)

```
1. Start dashboard → streamlit run dashboard/app.py
2. Go to 🧩 Ensemble Models tab
3. Review model metrics (ROC-AUC: 0.8884)
4. See per-model comparison
5. Optional: Upload test CSV to score
```

### Workflow 2: Understand Why Event Was Flagged (10 min)

```
1. Go to 🔍 Anomaly Explorer tab
2. Find anomaly you're interested in
3. Click "EXPAND ANOMALY DETAILS"
4. Read:
   - ❓ Why was this flagged?
   - 🔧 Contributing factors
   - 📚 Similar historical events
   - 💡 Recommended actions
```

### Workflow 3: Check User Baseline (5 min)

```
1. Go to 👤 Baseline Profiles tab
2. Enter user_id (e.g., user_123)
3. View charts:
   - Typical login hours
   - Typical locations
   - Accessed resources
4. See what would be "unusual"
```

### Workflow 4: Ingest New Logs (10 min)

```
1. Go to 📤 Data Ingestion tab
2. Prepare CSV with: user_id, timestamp, resource, action, success
3. Upload file
4. Review preview
5. Click "💾 Ingest & Score"
6. Wait for processing (2-3 seconds)
7. View summary (anomalies detected)
8. Go to 🔍 Anomaly Explorer to see detections
```

---

## 📊 Sidebar Information

The sidebar displays:
- **System Status:** Events, anomalies, model status
- **Model Performance:** ROC-AUC, Recall, Ensemble composition
- ** Quick Stats:** Unique users, resources, locations

Updated dynamically as new data is ingested.

---

## 🔄 Data Refresh

- Dashboard refreshes on interaction (button clicks, tab changes)
- Real-time updates if streaming events
- Manual refresh: ⟳ button in Streamlit

---

## 💾 Export & Integration

Currently view-only in dashboard. For integration:
- API available at `http://localhost:8000/docs`
- Database accessible at `data/store.sqlite`
- Models available for direct import in Python

See [docs/api-reference.md](docs/api-reference.md) for API details.

---

## Next: See Documentation Strategy in [DOCUMENTATION_GUIDE.md](DOCUMENTATION_GUIDE.md)
