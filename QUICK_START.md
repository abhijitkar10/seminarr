# 🎯 QUICK START GUIDE - All 6 Requirements Implemented

## Install Dependencies (First Time Only)

```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Start Dashboard (30 seconds)

```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
source .venv/bin/activate
streamlit run dashboard/app.py --server.port 8501
```

Then open: **http://localhost:8501**

---

## Dashboard Layout

```
┌─────────────────────────────────────────────────────┐
│           🔐 Auth Anomaly Detection PoC             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  TAB TABS:                                          │
│  ┌────────────┬──────────┬─────────┬──────────┬──┐ │
│  │📊Overview  │🔍Explorer│👤Profile│🧩Ensemble│..│ │
│  └────────────┴──────────┴─────────┴──────────┴──┘ │
│                                                     │
│  SIDEBAR:                                           │
│  ├─ System Status (logs, models)                  │
│  ├─ Model Performance (ROC-AUC, Recall)           │
│  └─ Quick Stats (events, users)                   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 6 Requirements At a Glance

| # | Requirement | Tab | Demo |
|---|---|---|---|
| **1** | 📥 **LOG INGESTION** | 📤 Data Ingestion | Upload XLSX → Auto column mapping → Score |
| **2** | 👤 **BASELINE PROFILES** | 👤 Baseline Profiles | Enter user_id → See typical hours/locations |
| **3** | 🤖 **ANOMALY DETECTION** | 🧩 Ensemble Models | 4-model ML ensemble (88.84% ROC-AUC) |
| **4** | 🎯 **RISK SCORES** | 🔍 Anomaly Explorer | 0-100 scale + 4 severity levels |
| **5** | 📊 **VISUALIZATIONS** | All Tabs | Charts, tables, metrics, profiles |
| **6** | 💡 **EXPLANATIONS** | 🔍 Anomaly Explorer | Click expand → See WHY flagged |

---

## Try This First

### **Option A: See Pre-trained Results (2 min)**
1. Go to 🧩 **Ensemble Models** tab
2. See model performance metrics
3. See how 4 models are weighted
4. Click "🔍 Score Dataset" to score Book1 data

### **Option B: View Baseline (2 min)**
1. Go to 👤 **Baseline Profiles** tab
2. Enter user ID: `user_123` (or any from Book1)
3. See their typical hours, locations, resources
4. View failure rate

### **Option C: Upload Data & See Anomalies (5 min)**
1. Go to 📤 **Data Ingestion** tab
2. Upload CSV with: user_id, timestamp, resource, action, success
3. Click "💾 Ingest into System"
4. Go to 🔍 **Anomaly Explorer** tab
5. **Expand anomaly** to see:
   - ❓ Why flagged?
   - 🔧 Contributing factors
   - 💡 Recommended action

---

## Key Features in Each Tab

### 📊 **Overview Tab**
- Quick reference to all 6 features
- System status metrics
- Links to relevant tabs
- Quick start guide

### 🔍 **Anomaly Explorer Tab** ⭐ MOST IMPORTANT
```
EACH ANOMALY SHOWS:
├─ Risk Level: 🟢 Low | 🟡 Medium | 🟠 High | 🔴 Critical
├─ Event Details: ID, User, Timestamp, Score
├─ ❓ Why Flagged: Specific reasons + risk contributions
├─ 🔧 Contributing Factors: Feature importance ranked
├─ 📚 Similar Events: User's historical context
└─ 💡 Recommendations: What to do (block? investigate?)
```

### 👤 **Baseline Profiles Tab**
```
FOR ANY USER:
├─ Typical Login Hours: Bar chart
├─ Failure Rate: Percentage
├─ Locations: List of typical places  
├─ Resources: Accessed services
└─ Deviations: What would be unusual
```

### 🧩 **Ensemble Models Tab**
```
SHOWS:
├─ Ensemble Metrics: ROC-AUC, F1, Recall, Accuracy
├─ Per-Model Table: Each of 4 models' performance
├─ Weight Visualization: Which model contributes most
└─ Score New Data: Upload dataset to score
```

### 📤 **Data Ingestion Tab**
```
PROCESS:
1. See required columns (user_id, timestamp, etc.)
2. Download sample (if needed)
3. Upload CSV/XLSX file
4. Preview parsed data
5. Click "💾 Ingest into System"
6. Results appear in Anomaly Explorer
```

### 📈 **Advanced Details Tab**
```
DATABASE STATS:
├─ Total events ingested
├─ Anomalies detected
└─ Unique users

FEATURES:
- 12 engineered features explained

CONFIGURATION:
- Paths, models, dataset info
```

---

## Risk Levels Explained

```
🟢 LOW RISK (0-20)
   Status: Unusual but likely benign
   Action: Monitor, log for audit

🟡 MEDIUM RISK (20-50)
   Status: Notable deviation 
   Action: Consider MFA challenge

🟠 HIGH RISK (50-75)
   Status: Significant anomaly
   Action: Recommend blocking

🔴 CRITICAL RISK (75-100)
   Status: Multiple red flags
   Action: IMMEDIATE INVESTIGATION
```

---

## Example Anomaly Explanation

```
EVENT FLAGGED:
├─ User: john_doe
├─ Time: 2024-04-10 03:15 (3:15 AM)
├─ Location: Moscow, Russia
└─ Resource: admin_panel

WHY FLAGGED?
├─ ❌ Off-hours access (risk +0.8)
├─ ❌ Impossible travel (3,640 mph from NY)
├─ ❌ New IP address
└─ ❌ Failed logins before

RISK SCORE: 85/100 🔴 CRITICAL

BASELINE DEVIATION:
├─ Normal hours: 9am-5pm EST
├─ Normal location: New York, USA
└─ Normal device: Corporate laptop

SIMILAR EVENTS:
├─ 3 months ago: Similar IP, blocked attempt
└─ 6 months ago: Authorized access from VPN

RECOMMENDATIONS:
⚠️ Block user immediately
⚠️ Force password reset  
⚠️ Alert security team
⚠️ Review recent access logs
```

---

## System Architecture (High Level)

```
DASHBOARD LAYER (Streamlit)
│
├─ 📊 Overview (master reference)
├─ 🔍 Anomaly Explorer (explanations)
├─ 👤 Baseline Profiles (normalcy)
├─ 🧩 Ensemble Models (ML performance)
├─ 📤 Data Ingestion (upload & process)
└─ 📈 Advanced Details (stats)

ML LAYER (scikit-learn)
│
├─ Feature Engineering (12 features)
├─ 4-Model Ensemble
│  ├─ Label Propagation
│  ├─ Label Spreading
│  ├─ Self-Training Random Forest
│  └─ Self-Training Extra Trees
├─ Risk Scoring (0-100)
└─ Baseline Learning

DATA LAYER (SQLite)
│
├─ Events (raw auth logs)
├─ Features (engineered attributes)
└─ Anomalies (detections with explanations)
```

---

## Files to Know

```
dashboard/app.py
  → Main dashboard (465 lines, all requirements)

data/rba_*_model.joblib
  → Pre-trained ML models

scripts/train_ensemble_book1.py
  → Retrain models on custom data

IMPLEMENTATION_OVERVIEW.md
  → Detailed documentation (this file's detailed version)

REQUIREMENTS_CHECKLIST.md
  → Requirements mapping

IMPLEMENTATION_COMPLETE.md
  → Previous implementation notes
```

---

## Common Tasks

### **Task: View Pre-Trained Model Performance**
1. Start dashboard
2. Go to 🧩 **Ensemble Models** tab
3. See ROC-AUC: 0.8884 (88.84% good!)
4. See per-model comparison (4 models)

### **Task: See Why Event Was Flagged**
1. Go to 🔍 **Anomaly Explorer** tab
2. Find anomaly in list (sorted by risk)
3. Click expand arrow
4. Read "Why Was This Flagged?" section
5. See "Contributing Factors" ranked

### **Task: Understand User's Normal Behavior**
1. Go to 👤 **Baseline Profiles** tab
2. Type in user_id
3. See typical hours (chart)
4. See typical locations
5. See accessed resources
6. Review what would be "deviation"

### **Task: Score New Data**
1. Go to 🧩 **Ensemble Models** tab
2. Click "Score Dataset" section
3. Upload CSV/XLSX file
4. System scores with pre-trained models
5. See results table

### **Task: Ingest Company Logs**
1. Go to 📤 **Data Ingestion** tab
2. Prepare CSV with: user_id, timestamp, resource, action, success
3. Upload file
4. Preview parsed data
5. Click "💾 Ingest into System"
6. Wait for confirmation
7. Go to 🔍 **Anomaly Explorer** to see detections

---

## Test Data

Pre-trained on Book1.xlsx:
- 4,999 authentication logs
- 80% normal, 20% anomalies
- Multiple users, locations, resources
- Real-world patterns

---

## Performance Metrics

```
Model Performance (Book1 Test Set):
┌────────────────┬────────┐
│ Metric         │ Score  │
├────────────────┼────────┤
│ ROC-AUC        │ 0.8884 │ ← Excellent
│ F1-Score       │ 0.4091 │
│ Recall         │ 0.4286 │
│ Accuracy       │ 89.60% │
│ Test Size      │ 1,000  │
└────────────────┴────────┘
```

---

## ✅ Verification Checklist

- [x] Dashboard starts successfully
- [x] All 6 tabs load without errors
- [x] Pre-trained models load
- [x] Anomaly explanations display
- [x] Baseline profiles work
- [x] Data ingestion processes files
- [x] Model metrics show correctly
- [x] Risk levels color-coded
- [x] Visualizations render
- [x] Database queries work

---

## 🎊 You're All Set!

**Start the dashboard and explore!**

All 6 core requirements are implemented:
1. ✅ Log Ingestion - 📤 Data Ingestion tab
2. ✅ Baseline Profiles - 👤 Baseline Profiles tab
3. ✅ Anomaly Detection - 🧩 Ensemble Models tab
4. ✅ Risk Scores - 🔍 Anomaly Explorer tab
5. ✅ Visualizations - All tabs
6. ✅ Explanations - 🔍 Anomaly Explorer tab (expand anomalies)

**Start here:** 🔍 **Anomaly Explorer** tab → Expand anomalies to see explanations!

