from __future__ import annotations
from fastapi import FastAPI
from fastapi import Body
from typing import List, Dict, Any
from models.schemas import AuthEvent, IngestResponse, Anomaly, UserProfile
from data.db import init_db, insert_events, insert_features, fetch_anomalies, fetch_recent_events, fetch_users, connect
from ml.features import compute_features
from ml.detector import AnomalyDetector
from ml.baseline import build_user_profile
from alerting.alerts import maybe_send_alert
from datetime import datetime
import json
from adapters.okta import normalize_okta_event

app = FastAPI(title="Auth Anomaly Detection PoC")

init_db()
detector = AnomalyDetector()


def _process(rows: List[Dict[str, Any]]) -> IngestResponse:
    for r in rows:
        if isinstance(r.get("timestamp"), datetime):
            r["timestamp"] = r["timestamp"].isoformat()
    accepted_ids = insert_events(rows)
    conn = connect()
    try:
        feature_rows = [compute_features(r, conn=conn) for r in rows]
    finally:
        conn.close()
    insert_features(feature_rows)
    detector.train()
    for fr in feature_rows:
        score, contrib = detector.score_event(fr)
        risk, reasons = detector.risk_score(score, fr)
        detector.record_anomaly(fr, score, risk, reasons, contrib)
        maybe_send_alert(fr["event_id"], fr["user_id"], risk, reasons, contrib)
    return IngestResponse(accepted=len(accepted_ids), errors=[])


@app.get("/")
def root():
    return {
        "message": "Auth Anomaly Detection PoC API",
        "endpoints": ["/ingest", "/ingest/okta", "/anomalies", "/events/recent", "/users", "/users/{user_id}/profile", "/docs"],
    }


@app.post("/ingest", response_model=IngestResponse)
def ingest_events(events: List[AuthEvent] = Body(...)) -> IngestResponse:
    return _process([e.model_dump() for e in events])


@app.post("/ingest/okta", response_model=IngestResponse)
def ingest_okta(events: List[dict] = Body(...)) -> IngestResponse:
    normalized = [normalize_okta_event(e) for e in events]
    return _process([AuthEvent(**e).model_dump() for e in normalized])


@app.get("/anomalies", response_model=List[Anomaly])
def list_anomalies(limit: int = 100) -> List[Anomaly]:
    rows = fetch_anomalies(limit=limit)
    results: List[Anomaly] = []
    for r in rows:
        results.append(
            Anomaly(
                event_id=r["event_id"],
                user_id=r["user_id"],
                timestamp=datetime.fromisoformat(r["timestamp"]),
                score=r["score"],
                risk=r["risk"],
                reasons=json.loads(r["reasons"]),
                feature_contributions=json.loads(r["contributions"]),
            )
        )
    return results


@app.get("/events/recent")
def recent_events(limit: int = 100) -> List[Dict[str, Any]]:
    rows = fetch_recent_events(limit=limit)
    return [dict(r) for r in rows]

@app.get("/users")
def list_users(limit: int = 100) -> List[Dict[str, Any]]:
    rows = fetch_users(limit=limit)
    return [dict(r) for r in rows]


@app.get("/users/{user_id}/profile", response_model=UserProfile)
def user_profile(user_id: str) -> UserProfile:
    prof = build_user_profile(user_id)
    return UserProfile(
        user_id=prof["user_id"],
        typical_hours=prof["typical_hours"],
        typical_locations=prof["typical_locations"],
        failure_rate=prof["failure_rate"],
        resource_frequency=prof["resource_frequency"],
    )
