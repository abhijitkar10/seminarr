import sys
from pathlib import Path
import importlib
import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Auth Anomaly Detection", layout="wide")
st.title("Auth Anomaly Detection PoC Dashboard")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
db = importlib.import_module("data.db")
baseline = importlib.import_module("ml.baseline")

tab1, tab2, tab3, tab4 = st.tabs(["Activity", "Anomalies", "Users", "Trends"])

with tab1:
    st.subheader("Recent Events")
    limit = st.slider("Limit", 10, 500, 100)
    rows = db.fetch_recent_events(limit=limit)
    df = pd.DataFrame([dict(r) for r in rows])
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        st.map(df.dropna(subset=["latitude", "longitude"])[["latitude", "longitude"]].rename(columns={"latitude": "lat", "longitude": "lon"}))
    else:
        st.info("No events yet")

with tab2:
    st.subheader("Anomalies")
    limit = st.slider("Limit (anomalies)", 10, 500, 100, key="anlimit")
    rows = db.fetch_anomalies(limit=limit)
    df = pd.DataFrame([{
        **{k: r[k] for k in r.keys() if k not in ("reasons", "contributions")},
        "reasons": ", ".join(json.loads(r["reasons"])),
        "contributions": json.loads(r["contributions"])
    } for r in rows])
    if not df.empty:
        st.dataframe(df.drop(columns=["contributions"]), use_container_width=True)
        st.subheader("Feature Contributions")
        if not df.empty:
            idx = st.number_input("Row index", min_value=0, max_value=len(df)-1, value=0)
            contrib = df.iloc[idx]["contributions"]
            st.bar_chart(pd.Series(contrib).sort_values(ascending=False))
    else:
        st.info("No anomalies yet")

with tab3:
    st.subheader("User Profiles")
    user_id = st.text_input("User ID", "")
    if user_id:
        prof = baseline.build_user_profile(user_id)
        st.json(prof)
        rows = db.fetch_user_events(user_id=user_id, limit=500)
        df = pd.DataFrame([dict(r) for r in rows])
        if not df.empty:
            st.dataframe(df, use_container_width=True)
    else:
        st.info("Enter a user_id to view profile")

with tab4:
    st.subheader("Organization Trends")
    rows = db.fetch_recent_events(limit=1000)
    df = pd.DataFrame([dict(r) for r in rows])
    if not df.empty:
        df["date"] = pd.to_datetime(df["timestamp"]).dt.date
        st.line_chart(df.groupby("date")["success"].count(), use_container_width=True)
        st.bar_chart(df.groupby("resource")["success"].count().sort_values(ascending=False), use_container_width=True)
    else:
        st.info("No data yet")
