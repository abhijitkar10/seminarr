"""Generate a small sample CSV demonstrating the expected log format.

Outputs data/sample_logs.csv with ~58 events (50 normal + 8 anomalous).
"""
from __future__ import annotations
import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

OUTFILE = Path(__file__).resolve().parents[1] / "data" / "sample_logs.csv"

USERS = [
    {"id": "alice@corp.com", "lat": 37.7749, "lon": -122.4194, "loc": "San Francisco, US", "device": "dev-alice-1"},
    {"id": "bob@corp.com",   "lat": 40.7128, "lon": -74.0060,  "loc": "New York, US",      "device": "dev-bob-1"},
    {"id": "carol@corp.com", "lat": 51.5074, "lon": -0.1278,   "loc": "London, UK",         "device": "dev-carol-1"},
]

RESOURCES = [
    "User login to app",
    "Authentication of user via MFA",
    "Auth service",
    "Session start",
    "Resource access",
]
ACTIONS = [
    "user.session.start",
    "user.authentication.auth_via_mfa",
    "user.authentication.authenticate_user",
    "user.authentication.invalid_password",
]

FIELDNAMES = [
    "event_id", "user_id", "timestamp", "ip_address",
    "latitude", "longitude", "location", "user_agent",
    "device_id", "resource", "action", "success",
    "mfa_used", "failure_reason", "privilege_level",
]


def _normal_event(user: dict, ts: datetime) -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "user_id": user["id"],
        "timestamp": ts.isoformat(),
        "ip_address": f"10.0.{random.randint(0,255)}.{random.randint(1,254)}",
        "latitude": round(user["lat"] + random.gauss(0, 0.01), 6),
        "longitude": round(user["lon"] + random.gauss(0, 0.01), 6),
        "location": user["loc"],
        "user_agent": "Mozilla/5.0",
        "device_id": random.choice([user["device"], None]),
        "resource": random.choice(RESOURCES),
        "action": random.choice(ACTIONS),
        "success": "true",
        "mfa_used": random.choice(["true", "false"]),
        "failure_reason": None,
        "privilege_level": random.choice(["user", None]),
    }


def _anomalous_event(user: dict, ts: datetime, kind: str) -> dict:
    evt = _normal_event(user, ts)
    if kind == "off_hours":
        new_ts = ts.replace(hour=random.choice([2, 3, 4, 23]))
        evt["timestamp"] = new_ts.isoformat()
    elif kind == "impossible_travel":
        evt["latitude"] = round(-33.8688 + random.gauss(0, 0.01), 6)  # Sydney
        evt["longitude"] = round(151.2093 + random.gauss(0, 0.01), 6)
        evt["location"] = "Sydney, AU"
    elif kind == "burst_failure":
        evt["success"] = "false"
        evt["failure_reason"] = "invalid_password"
    elif kind == "new_device":
        evt["device_id"] = f"dev-unknown-{uuid.uuid4().hex[:6]}"
    elif kind == "mfa_auth":
        evt["action"] = "user.authentication.auth_via_mfa"
        evt["resource"] = "Authentication of user via MFA"
        evt["mfa_used"] = "true"
    return evt


def generate() -> None:
    OUTFILE.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    base = datetime(2026, 3, 28, 8, 0, 0)

    for user in USERS:
        for day_offset in range(3):
            day_base = base + timedelta(days=day_offset)
            # ~17 normal events per user per day
            for _ in range(17):
                hour = random.randint(8, 18)
                minute = random.randint(0, 59)
                ts = day_base.replace(hour=hour, minute=minute, second=random.randint(0, 59))
                rows.append(_normal_event(user, ts))

        # Anomalous events for this user
        anomaly_day = base + timedelta(days=2)
        rows.append(_anomalous_event(user, anomaly_day.replace(hour=10, minute=5), "off_hours"))
        rows.append(_anomalous_event(user, anomaly_day.replace(hour=10, minute=10), "impossible_travel"))
        if user["id"] == "bob@corp.com":
            # Bob gets extra burst failures
            for i in range(3):
                rows.append(_anomalous_event(user, anomaly_day.replace(hour=11, minute=i), "burst_failure"))
        rows.append(_anomalous_event(user, anomaly_day.replace(hour=12, minute=0), "new_device"))

    rows.sort(key=lambda r: r["timestamp"])

    with open(OUTFILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} events to {OUTFILE}")


if __name__ == "__main__":
    generate()
