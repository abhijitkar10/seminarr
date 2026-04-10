# 🎯 Ensemble-Based Anomaly Detection & Risk Scoring

## Overview

Your anomaly detection system now uses a **4-Model Weighted Ensemble** instead of a single Labeled Propagation model. This provides more robust and diverse attack detection.

---

## Ensemble Composition

The ensemble combines **four semi-supervised learning models**:

| Model                           | Type            | Input                | Purpose                                      |
| ------------------------------- | --------------- | -------------------- | -------------------------------------------- |
| **Label Propagation**           | Graph-based SSL | PCA-reduced features | Leverages manifold structure                 |
| **Label Spreading**             | Iterative SSL   | PCA-reduced features | Smooth label propagation with regularization |
| **Self-Training Random Forest** | Ensemble SSL    | Scaled features      | Tree-based confidence learning               |
| **Self-Training Extra Trees**   | Ensemble SSL    | Scaled features      | Highly randomized trees for robustness       |

---

## Risk Scoring Pipeline

### Step 1: Feature Engineering

```
Raw Event (user_id, timestamp, IP, etc.)
    ↓
Extract 40+ features:
  - Temporal: hour_of_day, day_of_week, is_night, is_weekend
  - Behavioral: user_fail_rate, user_login_count
  - Geographic: country_risky, asn_suspicious
  - Network: rtt_log, rtt_high
  - Encoded categoricals: Country, OS, Browser, Device Type
    ↓
Impute missing values
    ↓
Scale (StandardScaler)
    ↓
Reduce dimensionality (PCA 15 components)
```

### Step 2: Model Scoring

Each of the 4 models independently produces a probability (0.0 - 1.0):

```
Event Features (PCA/Scaled)
    ├─→ Label Propagation    → score_lp    (0.0-1.0)
    ├─→ Label Spreading      → score_ls    (0.0-1.0)
    ├─→ Self-Training RF      → score_st_rf (0.0-1.0)
    └─→ Self-Training ET      → score_st_et (0.0-1.0)
```

**Interpretation:** Higher score = model thinks event is more anomalous

### Step 3: Weighted Averaging

Weights are learned from the **labeled validation data** (40% of training set):

```python
ensemble_risk = (
    weight_lp    × score_lp    +
    weight_ls    × score_ls    +
    weight_st_rf × score_st_rf +
    weight_st_et × score_st_et
)
```

**Weight derivation:** Average Precision (AP) on labeled validation set

- Model with AP=0.85 → weight ≈ 0.30
- Model with AP=0.70 → weight ≈ 0.25
- Model with AP=0.60 → weight ≈ 0.20
- Total weights always sum to 1.0

**Result:** `ensemble_risk` (0.0 - 1.0)

### Step 4: Scale & Context Adjustments

```python
# Scale to 0-3.0 range
risk = ensemble_risk × 3.0

# Add context-based adjustments
if off_hours:           risk += 0.15
if high_geo_velocity:   risk += 0.25  (>900 km/h)
if failure_spike:       risk += 0.20
if rare_resource:       risk += 0.15
if new_device:          risk += 0.10

# Clip to safe range
risk = clip(risk, 0.0, 3.0)
```

**Final Result:** `risk` (0.0 - 3.0)

---

## Classification Thresholds

Based on final risk score (0.0 - 3.0):

| Risk Level      | Threshold | Meaning                 | Action            |
| --------------- | --------- | ----------------------- | ----------------- |
| 🔴 **Critical** | ≥ 2.0     | Highly confident attack | Alert immediately |
| 🟠 **High**     | ≥ 1.5     | Probable attack         | Alert soon        |
| 🟡 **Medium**   | ≥ 1.0     | Suspicious activity     | Log for review    |
| 🟢 **Low**      | < 1.0     | Likely normal           | No action         |

---

## How It Works in the Dashboard

### Training the Ensemble

1. **Upload data** with Book1.xlsx format (must have labels: "Is Attack IP" or "Is Account Takeover")
2. **Click "🧠 Train Model"** in Upload tab
3. System trains all 4 models on 80% of data, evaluates on 20%
4. Learns weights and threshold from labeled data
5. Saves all 4 models to disk for future use

### Scoring Events

1. **Click "🔍 Score All Events"** in Upload tab
2. For each event:
   - Extract features
   - Get 4 independent model scores
   - Compute weighted average
   - Apply context adjustments
   - Store final risk score + per-model contributions in database
3. Anomalies tab displays all scored events

### Visualization

**Per-Model Scores** (Feature Contributions tab):

- Shows bar chart of each model's probability (lp, ls, st_rf, st_et)
- Higher bar = model voted stronger for anomaly
- Helps debug which models agree/disagree

---

## Key Metrics Explained

### ROC-AUC (Receiver Operating Characteristic - Area Under Curve)

- **Range:** 0.0 - 1.0
- **Meaning:** Probability model ranks attack higher than normal
- **Threshold:** >0.8 is excellent, >0.7 is good
- **Formula:** Area under ROC curve plotting TPR vs FPR

### F1-Score

- **Range:** 0.0 - 1.0
- **Meaning:** Harmonic mean of precision and recall
- **Formula:** 2 × (precision × recall) / (precision + recall)
- **Use case:** Balances TP/FP tradeoff (good for imbalanced datasets)

### Recall

- **Range:** 0.0 - 1.0
- **Meaning:** % of actual attacks caught
- **Formula:** TP / (TP + FN)
- **Security context:** Higher is critical (catch more attacks)

### Accuracy

- **Range:** 0.0 - 1.0
- **Meaning:** % correct predictions overall
- **Formula:** (TP + TN) / Total
- **Caveat:** Misleading for imbalanced data (8.4% attacks)

### Average Precision (Weight Source)

- **Range:** 0.0 - 1.0
- **Meaning:** Average precision at different recall levels
- **Use:** Determines ensemble model weights
- **Advantage:** Better for imbalanced classification than ROC-AUC

---

## Example Walkthrough

### Event 1: Normal Login

```
Raw Event: User "alice", 2pm, NYC, Regular device

Features After Engineering:
  hour_of_day=14, day_of_week=3, is_night=0, is_weekend=0
  user_fail_rate=0.02, user_login_count=125
  country_risky=0, asn_suspicious=0, rtt_high=0, new_device=0

Model Scores:
  LP:       0.15  (low anomaly probability)
  LS:       0.12
  ST_RF:    0.18
  ST_ET:    0.14

Weighted Average: 0.15×0.25 + 0.12×0.26 + 0.18×0.24 + 0.14×0.25 = 0.15

Scaled Risk: 0.15 × 3.0 = 0.45

Context Adjustments: None (normal time, known device, low failure rate)

Final Risk: 0.45

Classification: 🟢 LOW (< 1.0)
```

### Event 2: Suspicious Attack

```
Raw Event: User "alice", 3am, Russia, New device, 5 failed logins

Features After Engineering:
  hour_of_day=3, day_of_week=2, is_night=1, is_weekend=0
  user_fail_rate=0.85 (spike!), user_login_count=1
  country_risky=1, asn_suspicious=1, geo_velocity=1200, new_device=1

Model Scores:
  LP:       0.82  (high anomaly probability)
  LS:       0.89
  ST_RF:    0.76
  ST_ET:    0.80

Weighted Average: 0.82×0.25 + 0.89×0.26 + 0.76×0.24 + 0.80×0.25 = 0.82

Scaled Risk: 0.82 × 3.0 = 2.46

Context Adjustments:
  + 0.15 (off-hours: 3am)
  + 0.25 (high geo-velocity: 1200 km/h)
  + 0.20 (failure burst)
  + 0.10 (new device)

Total Adjustments: +0.70

Final Risk: 2.46 + 0.70 = 3.16 → clipped to 3.0

Classification: 🔴 CRITICAL (≥ 2.0)
Reasons: ["Off-hours access", "Unrealistic geo-velocity", "Failure burst before event", "New device detected"]
```

---

## Production Deployment

### File Locations

- **Models:** `data/rba_lp_model.joblib`, `data/rba_ls_model.joblib`, etc.
- **Metadata:** `data/rba_ensemble_meta.joblib`
- **Metrics:** `data/rba_ensemble_eval.json`

### Database Storage

- **Events:** `store.sqlite` / `events` table
- **Features:** `store.sqlite` / `features` table
- **Anomalies:** `store.sqlite` / `anomalies` table

Each anomaly record stores:

- `event_id`, `user_id`, `timestamp`
- `risk` (final 0.0-3.0 score)
- `reasons` (list of context reasons)
- `contributions` (per-model scores: lp, ls, st_rf, st_et)

### API Integration

When running with Okta Event Hooks:

1. Hook receives event → API `/ingest/okta`
2. Extract features
3. Score with ensemble
4. Store in database
5. Send alert if risk ≥ 1.5

---

## Customization

### Adjust Risk Thresholds

Edit `ml/detector.py` → `risk_score()` method:

```python
def risk_score(self, ensemble_risk, feature_row):
    # Adjust these multipliers:
    risk = ensemble_risk × 3.0  # Change 3.0 to scale differently

    # Adjust these bonuses:
    if feature_row.get("off_hours"):
        risk += 0.15  # Change 0.15 to adjust off-hours weight
```

Edit classification thresholds in `dashboard/app.py`:

```python
def risk_level(risk):
    if risk >= 2.5:       # Change 2.5 to new Critical threshold
        return "🔴 Critical"
    elif risk >= 1.8:     # Change 1.8 to new High threshold
        return "🟠 High"
```

### Retrain Ensemble

```bash
# In dashboard: Upload tab → "🧠 Train Model"
# Or in code:
from ml.rba_ensemble import RBAEnsembleDetector
detector = RBAEnsembleDetector()
detector.train(df, label_column="Is Attack IP")
detector.save()
```

---

## Troubleshooting

### Models not loading?

```python
from ml.rba_ensemble import RBAEnsembleDetector
det = RBAEnsembleDetector()
print(det.is_trained)  # Should be True if models loaded
```

### Different risk scores after retraining?

- Thresholds may shift with new training data
- Weights change based on validation set AP
- Normal and expected behavior

### Anomalies not showing in dashboard?

1. Load data (Upload tab)
2. Train models (button at top)
3. Score events (button at top)
4. Go to Anomalies tab

---

## References

- **Semi-supervised Learning:** Scikit-learn docs on `LabelPropagation`, `LabelSpreading`, `SelfTrainingClassifier`
- **Feature Engineering:** ML/features.py for temporal, geographic, behavioral features
- **RBA (Risk-Based Authentication):** Book1.xlsx dataset with 4,999 events (8.4% attacks)
- **Ensemble Methods:** Weighted averaging, Average Precision weighting strategy
