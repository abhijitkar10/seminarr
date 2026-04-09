from __future__ import annotations
import argparse
import random
import time
from datetime import datetime, UTC
import uuid
import requests

DEFAULT_USERS = ["alice", "bob", "carol", "dave"]
RESOURCES = ["crm", "erp", "hr_portal", "code_repo", "payments"]
LOCATIONS = [
    ("San Francisco, US", 37.7749, -122.4194),
    ("New York, US", 40.7128, -74.0060),
    ("London, UK", 51.5074, -0.1278),
    ("Bengaluru, IN", 12.9716, 77.5946),
    ("Sydney, AU", -33.8688, 151.2093),
]
UA = ["Mozilla/5.0", "Chrome/120", "Safari/16", "Edge/120"]


def gen_event(now: datetime, user: str, anomaly_prob: float) -> dict:
    anomalous = random.random() < anomaly_prob
    location, lat, lon = random.choice(LOCATIONS)
    device_id = None if random.random() < 0.2 else f"device-{user}-{random.randint(1,3)}"
    ts = now if not anomalous else now.replace(hour=random.choice([0, 1, 2, 3, 4, 23]))
    if anomalous and random.random() < 0.5:
        device_id = f"new-device-{uuid.uuid4().hex[:6]}"
    success = not anomalous or random.random() > 0.3
    action = "user.authentication.auth_via_mfa" if anomalous else random.choice([
        "user.session.start",
        "user.authentication.authenticate_user",
    ])
    resource = "Authentication of user via MFA" if anomalous else random.choice([
        "User login to app",
        "Auth service",
    ])
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8000/ingest")
    ap.add_argument("--rps", type=float, default=2.0, help="events per second")
    ap.add_argument("--users", nargs="*", default=DEFAULT_USERS)
    ap.add_argument("--anomaly-prob", type=float, default=0.1)
    args = ap.parse_args()

    idx = 0
    print(f"Streaming to {args.url} at ~{args.rps} eps for users={args.users}")
    while True:
        now = datetime.now(UTC).replace(tzinfo=None)
        user = args.users[idx % len(args.users)]
        evt = gen_event(now, user, args.anomaly_prob)
        r = requests.post(args.url, json=[evt], timeout=5)
        if r.status_code != 200:
            print(f"POST failed: {r.status_code} {r.text}")
        else:
            pass
        idx += 1
        time.sleep(max(1.0 / args.rps, 0.01))


if __name__ == "__main__":
    main()
