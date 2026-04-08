from __future__ import annotations
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi import Body
from typing import List, Dict, Any
from models.schemas import AuthEvent, IngestResponse, Anomaly, UserProfile
from data.db import init_db, insert_events, insert_features, fetch_anomalies, fetch_recent_events, fetch_users, connect
from ml.features import compute_features
from ml.detector import AnomalyDetector
from ml.baseline import build_user_profile
from alerting.alerts import maybe_send_alert
from adapters.csv_parser import parse_csv
from datetime import datetime
import json
from adapters.okta import normalize_okta_event
import os

app = FastAPI(title="Auth Anomaly Detection PoC")

init_db()
detector = AnomalyDetector()


def _verify_okta_hook_auth(request: Request) -> None:
    secret = os.getenv("OKTA_EVENT_HOOK_AUTH_SECRET")
    if not secret:
        return
    header_name = os.getenv("OKTA_EVENT_HOOK_AUTH_HEADER", "authorization")
    actual = request.headers.get(header_name)
    if actual != secret:
        raise HTTPException(status_code=401, detail="Invalid Okta hook credentials")



def _process(rows: List[Dict[str, Any]], train: bool = True) -> IngestResponse:
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
    if train:
        detector.train()
    if detector.is_trained:
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


@app.api_route("/hooks/okta", methods=["GET", "POST"])
async def okta_event_hook(request: Request) -> Dict[str, Any]:
    _verify_okta_hook_auth(request)

    challenge = request.headers.get("x-okta-verification-challenge")
    if challenge:
        return {"verification": challenge}

    if request.method == "GET":
        return {"ok": True}

    try:
        payload = await request.json()
    except Exception:
        return {"accepted": 0, "errors": ["Invalid JSON payload"]}

    events: list[dict] = []
    if isinstance(payload, dict):
        data = payload.get("data") or {}
        maybe_events = data.get("events") if isinstance(data, dict) else None
        if isinstance(maybe_events, list):
            events = maybe_events
        elif isinstance(payload.get("events"), list):
            events = payload["events"]

    if not events:
        return {"accepted": 0, "errors": ["No events found in payload"]}

    normalized = [normalize_okta_event(e) for e in events]
    valid: list[dict[str, Any]] = []
    errors: list[str] = []
    for i, e in enumerate(normalized):
        try:
            valid.append(AuthEvent(**e).model_dump())
        except Exception as ex:
            errors.append(f"event {i}: {ex}")

    if not valid:
        return {"accepted": 0, "errors": errors or ["No valid events"]}

    res = _process(valid, train=False)
    return {"accepted": res.accepted, "errors": errors}


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


@app.post("/upload/csv", response_model=IngestResponse)
async def upload_csv(file: UploadFile = File(...)) -> IngestResponse:
    rows, errors = parse_csv(file.file)
    if errors:
        return IngestResponse(accepted=0, errors=errors)
    return _process(rows, train=False)


@app.post("/train")
def train_model() -> Dict[str, Any]:
    detector.train()
    return {"trained": detector.is_trained}


@app.post("/score")
def score_all() -> Dict[str, Any]:
    if not detector.is_trained:
        return {"scored": 0, "error": "Model not trained yet"}
    conn = connect()
    rows = conn.execute("SELECT * FROM features ORDER BY timestamp DESC LIMIT 2000").fetchall()
    conn.close()
    scored = 0
    for r in rows:
        fr = dict(r)
        score, contrib = detector.score_event(fr)
        risk, reasons = detector.risk_score(score, fr)
        detector.record_anomaly(fr, score, risk, reasons, contrib)
        maybe_send_alert(fr["event_id"], fr["user_id"], risk, reasons, contrib)
        scored += 1
    return {"scored": scored}
