from __future__ import annotations
from typing import Dict, Any
from data.db import connect
from collections import Counter
from datetime import datetime, timezone


def _parse_event_timestamp(value: str) -> datetime:
    ts = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if ts.tzinfo is not None:
        return ts.astimezone(timezone.utc).replace(tzinfo=None)
    return ts


def build_user_profile(user_id: str, limit: int = 1000) -> Dict[str, Any]:
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT timestamp, location, resource, success FROM events WHERE user_id=? ORDER BY timestamp DESC LIMIT ?",
        (user_id, limit),
    )
    rows = cur.fetchall()
    if not rows:
        return {
            "user_id": user_id,
            "typical_hours": [],
            "typical_locations": [],
            "failure_rate": 0.0,
            "resource_frequency": {},
        }

    hours = []
    locations = []
    resources = []
    failures = 0
    total = 0
    for r in rows:
        try:
            ts = _parse_event_timestamp(r["timestamp"])
            hours.append(ts.hour)
        except Exception:
            pass
        if r["location"]:
            locations.append(r["location"])
        if r["resource"]:
            resources.append(r["resource"])
        total += 1
        failures += 0 if r["success"] else 1

    hour_counter = Counter(hours)
    typical_hours = [h for h, _ in hour_counter.most_common(5)]
    location_counter = Counter(locations)
    typical_locations = [loc for loc, _ in location_counter.most_common(5)]
    res_counter = Counter(resources)
    resource_frequency = dict(res_counter)

    failure_rate = (failures / total) if total > 0 else 0.0

    return {
        "user_id": user_id,
        "typical_hours": typical_hours,
        "typical_locations": typical_locations,
        "failure_rate": failure_rate,
        "resource_frequency": resource_frequency,
    }
