from __future__ import annotations
import random
from datetime import datetime, timedelta
import uuid
import requests

USERS = ["alice", "bob", "carol", "dave"]
RESOURCES = [
    "User login to app",
    "Authentication of user via MFA",
    "Auth service",
    "Session start",
]
LOCATIONS = [
    ("San Francisco, US", 37.7749, -122.4194),
    ("New York, US", 40.7128, -74.0060),
    ("London, UK", 51.5074, -0.1278),
    ("Bengaluru, IN", 12.9716, 77.5946),
    ("Sydney, AU", -33.8688, 151.2093),
]
UA = ["Mozilla/5.0", "Chrome/120", "Safari/16", "Edge/120"]


def gen_event(now: datetime, user: str, normal: bool = True) -> dict:
    location, lat, lon = random.choice(LOCATIONS)
    resource = random.choice(RESOURCES) if normal else "Authentication of user via MFA"
    success = True if normal else (random.random() > 0.3)
    action = random.choice([
        "user.session.start",
        "user.authentication.authenticate_user",
    ]) if normal else random.choice([
        "user.authentication.auth_via_mfa",
        "user.authentication.invalid_password",
    ])
    device_id = None if random.random() < 0.2 else f"device-{user}-{random.randint(1,3)}"
    if not normal and random.random() < 0.5:
        device_id = f"new-device-{uuid.uuid4().hex[:6]}"
    ts = now if normal else now.replace(hour=random.choice([0,1,2,3,4,23]))
    return {
        "event_id": uuid.uuid4().hex,
        "user_id": user,
        "timestamp": ts.isoformat(),
        "ip_address": f"10.0.{random.randint(0,255)}.{random.randint(0,255)}",
        "latitude": lat,
        "longitude": lon,
        "location": location,
        "user_agent": random.choice(UA),
        "device_id": device_id,
        "resource": resource,
        "action": action,
        "success": success,
        "mfa_used": bool(random.random() > 0.7),
        "failure_reason": None if success else "invalid_password",
        "privilege_level": random.choice(["user", None]),
    }


def main():
    base = datetime.utcnow() - timedelta(days=3)
    events = []
    for day in range(3):
        day_start = base + timedelta(days=day)
        for user in USERS:
            for i in range(50):
                ts = day_start + timedelta(minutes=random.randint(0, 60*24-1))
                events.append(gen_event(ts, user, normal=True))
            # inject anomalies
            for i in range(3):
                ts = day_start + timedelta(minutes=random.randint(0, 60*24-1))
                events.append(gen_event(ts, user, normal=False))
    print(f"Generated {len(events)} events")
    # send in batches
    url = "http://localhost:8000/ingest"
    batch = 100
    for i in range(0, len(events), batch):
        chunk = events[i:i+batch]
        r = requests.post(url, json=chunk, timeout=10)
        print(f"POST {i}-{i+batch}: {r.status_code} {r.text}")


if __name__ == "__main__":
    main()
