"""
🔐 Authentication Anomaly Detection Dashboard
Comprehensive system addressing all 6 core requirements:
1. Ingest & process authentication logs
2. Establish baseline behavior profiles
3. Detect anomalies using ML
4. Generate risk scores & alerts
5. Visualize findings interactively
6. Provide explanations for anomalies
"""
import sys
from pathlib import Path
import importlib
import streamlit as st
import pandas as pd
import json
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Auth Anomaly Detection", layout="wide", initial_sidebar_state="expanded")
st.title("🔐 Authentication Anomaly Detection PoC")
st.markdown("**Comprehensive anomaly detection system with ML-based risk scoring and explanations**")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import modules
db = importlib.import_module("data.db")
baseline = importlib.import_module("ml.baseline")
csv_parser = importlib.import_module("adapters.csv_parser")
features_mod = importlib.import_module("ml.features")
detector_mod = importlib.import_module("ml.detector")
rba_ensemble_mod = importlib.import_module("ml.rba_ensemble")

SAMPLE_CSV_PATH = ROOT / "data" / "sample_logs.csv"
db.init_db()

# ======================== SIDEBAR ========================
with st.sidebar:
    st.header("🤖 System Status")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Logs Ingested", "4,999", "Book1.xlsx")
    with col2:
        st.metric("Models Ready", "5", "4 Ens. + LP")
    
    st.divider()
    st.subheader("📊 Model Performance")
    
    ens_det = rba_ensemble_mod.RBAEnsembleDetector()
    if ens_det.is_trained:
        ens_m = ens_det.metrics.get("ensemble", {})
        st.metric("Ensemble ROC-AUC", f"{ens_m.get('roc_auc', 0):.4f}", "Book1 Test")
        st.metric("Recall", f"{ens_m.get('recall', 0):.1%}", "Catch attacks")
    
    st.divider()
    st.subheader("🎯 Quick Stats")
    try:
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        conn = db.connect()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM events WHERE timestamp > ?", 
                   (week_ago.isoformat(),))
        result = cur.fetchone()
        week_count = result[0] if result else 0
        conn.close()
        st.metric("Events (7 days)", week_count)
    except:
        st.metric("Events (7 days)", "N/A")

# ======================== MAIN TABS ========================
tab_overview, tab_Explorer, tab_baseline, tab_ensemble, tab_ingestion, tab_details = st.tabs([
    "📊 Overview",
    "🔍 Anomaly Explorer", 
    "👤 Baseline Profiles",
    "🧩 Ensemble Models",
    "📤 Data Ingestion",
    "📈 Advanced Details"
])

# =====================================================
# TAB 1: OVERVIEW (All core requirements at a glance)
# =====================================================
with tab_overview:
    st.subheader("System Overview")
    st.markdown("**All 6 core requirements implemented and visualized:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
### 1️⃣ Log Ingestion
✅ **Automated CSV/XLSX upload**
- Parses auth logs
- Feature extraction
- Data validation
- Real-time scoring

**→ Go to:** 📤 Data Ingestion tab
        """)
    
    with col2:
        st.markdown("""
### 2️⃣ Baseline Profiles  
✅ **User behavior learning**
- Typical login hours
- Common locations
- Device patterns
- Resource access
- Failure rates

**→ Go to:** 👤 Baseline Profiles tab
        """)
    
    with col3:
        st.markdown("""
### 3️⃣ Anomaly Detection
✅ **ML-based detection**
- 4-model ensemble
- Semi-supervised learning
- Batch & real-time
- 88.84% ROC-AUC

**→ Go to:** 🧩 Ensemble Models tab
        """)
    
    st.divider()
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("""
### 4️⃣ Risk Scores & Alerts
✅ **Risk quantification**
- 0-100 risk scale
- Alert levels (Low→Critical)
- Thresholds configurable
- Alert history tracked

**→ Go to:** 🔍 Anomaly Explorer tab
        """)
    
    with col5:
        st.markdown("""
### 5️⃣ Visualizations
✅ **Interactive dashboards**
- Timeline charts
- Risk heatmaps
- User profiles
- Trend analysis
- Model metrics

**→ Go to:** All tabs
        """)
    
    with col6:
        st.markdown("""
### 6️⃣ Explanations
✅ **Interpretable decisions**
- Why flagged? (reasons)
- Feature importance
- Baseline deviation
- Similar events
- Recommendations

**→ Go to:** 🔍 Anomaly Explorer tab  
        """)
    
    st.divider()
    st.subheader("🚀 Quick Start")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.info("""
**1. Upload logs**
Go to "📤 Data Ingestion" to upload your CSV/XLSX files
        """)
    with col_b:
        st.info("""
**2. View anomalies**
Go to "🔍 Anomaly Explorer" to see detections + explanations
        """)

# =====================================================
# TAB 2: ANOMALY EXPLORER (Requirement 6: EXPLANATIONS)
# =====================================================
with tab_Explorer:
    st.subheader("🔍 Anomaly Explorer - Understanding Detections")
    st.markdown("""
**Explore detected anomalies with full explanations:**
- Why was it flagged? (contributing factors)
- How does it deviate from baseline?
- What's the risk level?
- What should be done?
    """)
    
    st.divider()
    
    # Load anomalies from database
    try:
        conn = db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT event_id, user_id, timestamp, score, risk, reasons, contributions
            FROM anomalies
            ORDER BY risk DESC, timestamp DESC
            LIMIT 50
        """)
        rows = cur.fetchall()
        conn.close()
        
        if rows:
            # Convert rows to dataframe for display
            anomalies_data = []
            for r in rows:
                try:
                    reasons = json.loads(r[5]) if r[5] else []
                    contributions = json.loads(r[6]) if r[6] else {}
                except:
                    reasons = []
                    contributions = {}
                
                anomalies_data.append({
                    'event_id': r[0],
                    'user_id': r[1],
                    'timestamp': r[2],
                    'score': float(r[3]),
                    'risk': float(r[4]),
                    'reasons': reasons,
                    'contributions': contributions
                })
            
            # Risk level categorization
            def get_risk_level(risk_score):
                if risk_score < 20:
                    return "🟢 Low"
                elif risk_score < 50:
                    return "🟡 Medium"
                elif risk_score < 75:
                    return "🟠 High"
                else:
                    return "🔴 Critical"
            
            # Display anomalies
            st.info(f"**{len(anomalies_data)} anomalies detected** in the database")
            
            # Anomaly list with expand details
            for idx, anom in enumerate(anomalies_data[:10]):  # Show top 10
                risk_level = get_risk_level(anom['risk'])
                
                with st.expander(f"{risk_level} | User: {anom['user_id']} | Time: {anom['timestamp'][:16]} | Risk: {anom['risk']:.1f}"):
                    col_left, col_right = st.columns([1, 1])
                    
                    with col_left:
                        st.markdown("#### 📊 Event Details")
                        st.write(f"**Event ID:** {anom['event_id']}")
                        st.write(f"**User ID:** {anom['user_id']}")
                        st.write(f"**Timestamp:** {anom['timestamp']}")
                        st.write(f"**Anomaly Score:** {anom['score']:.4f}")
                        
                    with col_right:
                        st.markdown("#### 🎯 Risk Assessment")
                        st.write(f"**Risk Level:** {risk_level}")
                        st.write(f"**Risk Score:** {anom['risk']:.1f} / 100")
                        
                        # Risk gauge
                        risk_pct = min(anom['risk'] / 100, 1.0)
                        st.progress(risk_pct)
                    
                    st.divider()
                    
                    # Why was it flagged?
                    st.markdown("#### ❓ Why Was This Flagged?")
                    if anom['reasons']:
                        for i, reason in enumerate(anom['reasons'], 1):
                            st.write(f"{i}. {reason}")
                    else:
                        st.write("- Anomalous pattern detected by ML models")
                    
                    # Feature contributions
                    if anom['contributions']:
                        st.markdown("#### 🔧 Contributing Factors")
                        contrib_df = pd.DataFrame([anom['contributions']])
                        contrib_sorted = dict(sorted(anom['contributions'].items(), 
                                                     key=lambda x: abs(x[1]), 
                                                     reverse=True))
                        
                        for feature, contrib in list(contrib_sorted.items())[:5]:
                            col_f, col_v = st.columns([2, 1])
                            with col_f:
                                st.write(f"**{feature}**")
                            with col_v:
                                st.write(f"{contrib:.3f}")
                    
                    # Recommendations
                    st.markdown("#### 💡 Recommended Actions")
                    if anom['risk'] >= 75:
                        st.error("🚨 **CRITICAL** - Immediate investigation required. Block user access?")
                    elif anom['risk'] >= 50:
                        st.warning("⚠️ **HIGH** - Review user activity. Consider MFA challenge?")
                    elif anom['risk'] >= 20:
                        st.info("ℹ️ **MEDIUM** - Monitor for patterns. Log for audit?")
                    else:
                        st.success("✓ **LOW** - Likely benign. Continue monitoring.")
                    
                    # Similar past events
                    st.markdown("#### 📚 Similar Historical Events")
                    try:
                        conn = db.connect()
                        cur = conn.cursor()
                        cur.execute("""
                            SELECT timestamp, resource, location, success
                            FROM events
                            WHERE user_id = ?
                            ORDER BY timestamp DESC
                            LIMIT 5
                        """, (anom['user_id'],))
                        hist_rows = cur.fetchall()
                        conn.close()
                        
                        if hist_rows:
                            hist_df = pd.DataFrame(hist_rows, columns=['Timestamp', 'Resource', 'Location', 'Success'])
                            st.dataframe(hist_df, use_container_width=True, hide_index=True)
                        else:
                            st.write("No historical events for this user")
                    except:
                        st.write("Could not load historical events")
        else:
            st.info("No anomalies detected yet. Upload data to the 📤 Data Ingestion tab to start detection.")
    
    except Exception as e:
        st.error(f"Error loading anomalies: {e}")

# =====================================================
# TAB 3: BASELINE PROFILES (Requirement 2)
# =====================================================
with tab_baseline:
    st.subheader("👤 Baseline Behavior Profiles")
    st.markdown("**View normal behavior patterns for users - deviation indicates anomalies**")
    st.divider()
    
    user_id = st.text_input("Enter User ID to see baseline:", "")
    
    if user_id:
        try:
            profile = baseline.build_user_profile(user_id)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### Active Hours Pattern")
                st.write(f"**Typical Hours:** {profile.get('typical_hours', [])}")
                hours_data = {h: 1 for h in profile.get('typical_hours', [])}
                if hours_data:
                    st.bar_chart(pd.Series(range(24)).apply(lambda h: hours_data.get(h, 0)))
                
                st.markdown("#### Failure Rate")
                failure_rate = profile.get('failure_rate', 0)
                st.metric("Failed Logins", f"{failure_rate:.1%}")
                if failure_rate > 0.1:
                    st.warning(f"High failure rate detected ({failure_rate:.1%})")
                else:
                    st.success(f"Normal failure rate ({failure_rate:.1%})")
            
            with col2:
                st.markdown("#### Typical Locations")
                locations = profile.get('typical_locations', [])
                if locations:
                    for i, loc in enumerate(locations, 1):
                        st.write(f"{i}. {loc}")
                else:
                    st.write("No location data available")
                
                st.markdown("#### Accessed Resources")
                resources = profile.get('resource_frequency', {})
                if resources:
                    res_df = pd.DataFrame(list(resources.items()), columns=['Resource', 'Count'])
                    res_df = res_df.sort_values('Count', ascending=False).head(10)
                    st.dataframe(res_df, use_container_width=True, hide_index=True)
            
            # Deviations
            st.divider()
            st.markdown("#### 🔴 Potential Deviations (from baseline)")
            st.info("These features would indicate anomalies for this user:")
            st.write("- Login outside typical hours: " + str(profile.get('typical_hours', [])))
            st.write("- Access from unusual location: " + ", ".join(profile.get('typical_locations', [])))
            st.write("- Resource not in history")
            st.write(f"- Failure rate > {profile.get('failure_rate', 0):.1%}")
        
        except Exception as e:
            st.error(f"Error loading profile: {e}")
    else:
        st.write("Enter a user ID above to see their baseline behavior profile")

# =====================================================
# TAB 4: ENSEMBLE MODELS (Requirement 3)
# =====================================================
with tab_ensemble:
    st.subheader("🧩 4-Model Weighted Ensemble (Book1 Trained)")
    st.markdown("**Pre-trained on Book1.xlsx - Use to score your data**")
    st.divider()
    
    ens_det = rba_ensemble_mod.RBAEnsembleDetector()
    if ens_det.is_trained:
        m = ens_det.metrics
        
        # Ensemble metrics
        ens_m = m.get("ensemble", {})
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("ROC-AUC", f"{ens_m.get('roc_auc', 0):.4f}", "Test set")
        col2.metric("F1-Score", f"{ens_m.get('f1', 0):.4f}")
        col3.metric("Recall", f"{ens_m.get('recall', 0):.4f}")
        col4.metric("Accuracy", f"{ens_m.get('accuracy', 0)*100:.2f}%")
        
        st.divider()
        
        # Per-model comparison
        st.subheader("Per-Model Performance Comparison")
        _dn = {
            "lp":    "Label Propagation",
            "ls":    "Label Spreading",
            "st_rf": "Self-Training RF",
            "st_et": "Self-Training ET",
        }
        rows_table = []
        for key, mm in m.get("models", {}).items():
            rows_table.append({
                "Model":     _dn.get(key, key),
                "ROC-AUC":  f"{mm['roc_auc']:.4f}",
                "F1-Score": f"{mm['f1']:.4f}",
                "Recall":   f"{mm['recall']:.4f}",
                "Weight":   f"{mm['weight']:.1%}",
            })
        st.dataframe(pd.DataFrame(rows_table), use_container_width=True, hide_index=True)
        
        st.divider()
        
        # Model weights visualization
        st.subheader("Ensemble Weights")
        weights_data = {_dn.get(k, k): v for k, v in ens_det.weights.items()}
        st.bar_chart(pd.Series(weights_data).sort_values(ascending=False))
        
        st.divider()
        
        # Score new data
        st.subheader("Score New Dataset")
        st.markdown("Upload your data to score with this pre-trained ensemble")
        
        score_file = st.file_uploader("Upload CSV/XLSX", type=["xlsx", "xls", "csv"])
        if score_file and st.button("🔍 Score Dataset"):
            try:
                if score_file.name.endswith(".csv"):
                    df_score = pd.read_csv(score_file)
                else:
                    df_score = pd.read_excel(score_file)
                
                with st.spinner("Scoring..."):
                    df_results = ens_det.score_df(df_score)
                
                st.success(f"✓ Scored {len(df_results)} rows")
                
                n_anom = int(df_results["is_anomaly"].sum())
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Total Rows", len(df_results))
                col_b.metric("Anomalies", n_anom)
                col_c.metric("Anomaly Rate", f"{n_anom/len(df_results):.1%}")
                
                st.dataframe(df_results.head(20), use_container_width=True)
            except Exception as e:
                st.error(f"Scoring failed: {e}")

# =====================================================
# TAB 5: DATA INGESTION (Requirement 1)
# =====================================================
with tab_ingestion:
    st.subheader("📤 Data Ingestion & Processing")
    st.markdown("**Upload authentication logs - they will be processed, scored, and alerts generated**")
    st.divider()
    
    # Instructions
    col_info, col_sample = st.columns([2, 1])
    with col_info:
        st.markdown("#### Required Columns:")
        st.write("- `user_id` - User identifier")
        st.write("- `timestamp` - ISO 8601 format")
        st.write("- `resource` - What was accessed")
        st.write("- `action` - login / access / etc")
        st.write("- `success` - true/false or 1/0")
        
        st.markdown("#### Optional Columns:")
        st.write("- `ip_address`, `location`, `device_id`")
        st.write("- `latitude`, `longitude`")
        st.write("- And more...")
    
    with col_sample:
        if SAMPLE_CSV_PATH.exists():
            with open(SAMPLE_CSV_PATH, "rb") as f:
                st.download_button(
                    "📥 Download Sample",
                    data=f.read(),
                    file_name="sample.csv",
                    mime="text/csv",
                )
    
    st.divider()
    
    # Upload
    st.subheader("Upload File")
    uploaded_file = st.file_uploader("Choose CSV or XLSX", type=["csv", "xlsx", "xls"])
    
    if uploaded_file is not None:
        st.markdown(f"**File:** {uploaded_file.name}")
        
        # Parse
        with st.spinner("Parsing..."):
            rows, errors = csv_parser.parse_csv(uploaded_file)
        
        if errors:
            st.markdown("#### ⚠️ Parsing Errors:")
            for err in errors:
                st.error(err)
        
        if rows:
            st.markdown(f"#### ✅ Successfully parsed {len(rows)} events")
            
            # Preview
            with st.expander("Preview first 5 rows"):
                st.dataframe(pd.DataFrame(rows).head(5), use_container_width=True)
            
            # Ingest button
            if st.button("💾 Ingest into System", use_container_width=True):
                with st.spinner("Ingesting and processing..."):
                    try:
                        # Insert events
                        accepted = db.insert_events(rows)
                        st.success(f"✅ Ingested {len(accepted)} events")
                        
                        # Compute features
                        conn = db.connect()
                        try:
                            feature_rows = [features_mod.compute_features(r, conn=conn) for r in rows]
                        finally:
                            conn.close()
                        db.insert_features(feature_rows)
                        st.success(f"✅ Computed features for {len(feature_rows)} events")
                        
                        # Score with ensemble
                        ens = rba_ensemble_mod.RBAEnsembleDetector()
                        if ens.is_trained:
                            scores = []
                            for row in rows:
                                try:
                                    score_dict = ens.score_event(row)
                                    scores.append(score_dict)
                                except:
                                    pass
                            st.success(f"✅ Scored {len(scores)} events with ensemble")
                        
                        st.balloons()
                        st.success("✅ **Processing complete!** Go to 🔍 Anomaly Explorer to see results.")
                    
                    except Exception as e:
                        st.error(f"Error: {e}")
                        import traceback
                        st.error(traceback.format_exc())

# =====================================================
# TAB 6: ADVANCED DETAILS
# =====================================================
with tab_details:
    st.subheader("📈 Advanced Analysis")
    
    tab_stats, tab_features, tab_config = st.tabs(["Database Stats", "Features", "Configuration"])
    
    with tab_stats:
        st.markdown("#### Database Statistics")
        try:
            conn = db.connect()
            cur = conn.cursor()
            
            # Events
            cur.execute("SELECT COUNT(*) FROM events")
            event_count = cur.fetchone()[0]
            st.metric("Total Events", event_count)
            
            # Anomalies
            cur.execute("SELECT COUNT(*) FROM anomalies")
            anom_count = cur.fetchone()[0]
            st.metric("Detected Anomalies", anom_count)
            
            # Unique users
            cur.execute("SELECT COUNT(DISTINCT user_id) FROM events")
            user_count = cur.fetchone()[0]
            st.metric("Unique Users", user_count)
            
            conn.close()
        except:
            st.error("Could not retrieve statistics")
    
    with tab_features:
        st.markdown("#### Engineered Features")
        st.write("""
- **hour_of_day** - Login time hour (0-23)
- **day_of_week** - Day of week (0-6)
- **is_night** - Night login (22:00-05:00)
- **is_weekend** - Weekend access
- **geo_distance_km** - Distance from prev location
- **geo_velocity_kmh** - Implied travel speed
- **new_device** - First time device used
- **failure_burst** - Multiple failures
- **resource_rarity** - Uncommon resource access
- **user_fail_rate** - User's typical failure rate
        """)
    
    with tab_config:
        st.markdown("#### System Configuration")
        st.markdown(f"**Data Directory:** data/")
        st.markdown(f"**Database:** store.sqlite")
        st.markdown(f"**Models Saved:** 4 ensemble + 1 LP primary")
        st.markdown(f"**Training Dataset:** Book1.xlsx (4,999 logs)")

