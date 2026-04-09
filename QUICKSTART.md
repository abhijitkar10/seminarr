# 🚀 Complete Quick-Start Guide: Run Everything

## 📋 What's Ready

✅ Refactored codebase (clean, removed useless code)
✅ Book2.xlsx dataset (49,999 rows for training)
✅ Training script ready (scripts/train_on_book2.py)
✅ Updated frontend with model selection
✅ API fully functional
✅ Okta integration working
✅ Documentation complete

---

## 🎯 Option 1: Quick Test (CSV Upload)

### Terminal 1 - Start API
```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 - Start Dashboard
```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
source .venv/bin/activate
streamlit run dashboard/app.py --server.port 8501
```

### In Browser
1. Open: http://localhost:8501
2. Go to **Model Info** tab → Review both models
3. Go to **Upload** tab
4. Download sample CSV or upload your own
5. Model is in sidebar (pick **Labeled Propagation ⭐**)
6. Click **🧠 Train Model**
7. Upload events (CSV)
8. Click **🔍 Score All Events**
9. Go to **Anomalies** tab to see results

---

## 🔒 Option 2: Full Setup with Okta Integration

### Terminal 1 - Start API
```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Expected output:**
```
Uvicorn running on http://127.0.0.1:8000
```

### Terminal 2 - Start ngrok Tunnel
```bash
ngrok http 8000
```

**Expected output:**
```
Session Status                online
Forwarding                    https://xyz-abc-def.ngrok-free.dev -> http://localhost:8000
```

📌 **COPY THIS HTTPS URL** - You'll use it in Okta

### Terminal 3 - Start Dashboard
```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
source .venv/bin/activate
streamlit run dashboard/app.py --server.port 8501
```

### Configure Okta Event Hook

1. **Log into Okta Admin Console**
   - Go to: https://integrator-2852306.okta.com/admin

2. **Navigate to Event Hooks**
   - Click: `Workflow` → `Event Hooks`
   - Click: `Create Event Hook`

3. **Fill in Hook Details**
   - **Name:** `Auth Anomaly Detection`
   - **URL:** `https://<your-ngrok-url>/hooks/okta`
     - Replace `<your-ngrok-url>` with the URL from ngrok (e.g., `https://xyz-abc-def.ngrok-free.dev`)
     - Full URL should be: `https://xyz-abc-def.ngrok-free.dev/hooks/okta`
   
4. **Set Authentication**
   - **Authentication field name:** `authorization`
   - **Authentication secret:** (copy from `.env` file `OKTA_EVENT_HOOK_AUTH_SECRET`)

5. **Subscribe to Events**
   - Select at least these events:
     - `user.authentication.auth_via_mfa`
     - `user.authentication.authenticate`
     - `user.authentication.authenticate_fail`
     - Or select all authentication events

6. **Save & Test**
   - Click `Create Event Hook`
   - Okta will send a verification request (auto-verified)

### Test the Integration

1. **Trigger an auth event in Okta**
   - Log out of Okta
   - Log back in
   - Use MFA if available

2. **Check Dashboard**
   - Go to: http://localhost:8501
   - Click: **Anomalies** tab
   - You should see events from Okta appearing

3. **Verify API Logs**
   - Terminal 1 should show POST requests to `/hooks/okta`
   - Should see event processing logs

---

## 📊 Training on Book2.xlsx (Optional but Recommended)

If model training finished, metrics will be in sidebar. To manually train:

### Option A: Via Dashboard
1. Open: http://localhost:8501
2. **Upload** tab
3. Upload any CSV with authentication data
4. Select **Labeled Propagation ⭐** model (sidebar)
5. Click **🧠 Train Model**

### Option B: Via Script
```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
source .venv/bin/activate
python3 scripts/train_on_book2.py
```

**Expected output:**
```
📊 Loading training data from Book2.xlsx...
✓ Loaded 49,999 rows with 16 columns
✓ Label distribution: {False: 45478, True: 4521}
✓ Anomaly rate: 9.04%

Training Labeled Propagation model...
[Model training...]

Optimal threshold: 0.1105
Accuracy:    0.7360
Precision:   0.2170
Recall:      0.8214
F1 Score:    0.3433
ROC-AUC:     0.8195

💾 Saving model...
Model saved to data/labeled_propagation_model.joblib
```

---

## 🎨 Dashboard Overview

### 📈 Model Info Tab
- Detailed model comparison
- Performance metrics
- Use case recommendations
- Integration status

### 📤 Upload Tab
- CSV upload
- Sample download
- Model selection (sidebar)
- Train & Score buttons

### 📊 Activity Tab
- Recent events
- Success/failure metrics
- Geographic map

### 🚨 Anomalies Tab
- Detected anomalies
- Risk levels (Low/Medium/High/Critical)
- Feature importance
- Okta event tracking

### 👥 Users Tab
- User profiles
- Typical login times
- Locations
- Resource usage

### 📉 Trends Tab
- Event volume over time
- Anomaly timeline
- Resource popularity

---

## ✅ Verification Checklist

Before declaring success:

- [ ] Terminal 1: API running on :8000 (green)
- [ ] Terminal 2: ngrok tunnel active (if using Okta)
- [ ] Terminal 3: Dashboard running on :8501 (blue)
- [ ] Browser: Dashboard opens (http://localhost:8501)
- [ ] Sidebar: Model selector visible with metrics
- [ ] Model Info tab: Shows comparison table
- [ ] Can upload CSV
- [ ] Can train model
- [ ] Can score events
- [ ] Anomalies appear in Anomalies tab
- [ ] (Optional) Okta events flowing in via ngrok

---

## 🐛 Troubleshooting

### Dashboard won't load
```bash
# Kill any existing streamlit process
pkill streamlit

# Start fresh
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
source .venv/bin/activate
streamlit run dashboard/app.py --server.port 8501
```

### API shows 500 error
```bash
# Check that venv is activated
source .venv/bin/activate

# Restart API
pkill python3
uvicorn app.main:app --reload --port 8000
```

### Okta events not flowing
1. Verify ngrok URL is correct in Okta hook
2. Check API logs for POST requests to `/hooks/okta`
3. Verify auth secret in `.env` matches Okta hook
4. Test with manual event: `curl http://localhost:8000/docs`

### Model training fails
1. Ensure enough data: Need ≥50 feature rows
2. Check data format - CSV must have required columns
3. Try training with sample data first

---

## 📱 API Endpoints (Health Check)

```bash
# Check API is running
curl http://localhost:8000

# View API documentation
open http://localhost:8000/docs

# List recent events
curl http://localhost:8000/events/recent

# List anomalies
curl http://localhost:8000/anomalies

# Manual ingest (POST)
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '[{"user_id":"user1","timestamp":"2026-04-09T12:00:00","resource":"app","action":"login","success":true}]'
```

---

## 🎓 Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI backend |
| `dashboard/app.py` | Streamlit frontend |
| `ml/labeled_propagation_model.py` | Main ML model |
| `adapters/okta.py` | Okta event normalization |
| `data/db.py` | Database operations |
| `docs/okta_event_hook_setup.md` | Detailed Okta setup |

---

## 🎯 Success Criteria

✅ You'll know it's working when:
1. Dashboard loads with model info tab
2. Can select models from sidebar
3. Can upload CSV and train
4. Events show up in Anomalies tab
5. Okta events flow in when configured
6. All 3 terminals running without errors

---

**You're all set! 🚀 Start with Option 1 for quick test, then add Okta setup when ready.**
