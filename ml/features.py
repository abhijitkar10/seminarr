from __future__ import annotations
from typing import Dict, Any, Optional
from math import radians, sin, cos, asin, sqrt
from datetime import datetime, timedelta
import sqlite3
from data.db import connect


def haversine_km(lat1: Optional[float], lon1: Optional[float], lat2: Optional[float], lon2: Optional[float]) -> Optional[float]:
    if None in (lat1, lon1, lat2, lon2):
        return None
    # convert decimal degrees to radians
    assert lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None
    lat1r, lon1r, lat2r, lon2r = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    dlon = lon2r - lon1r
    dlat = lat2r - lat1r
    a = sin(dlat / 2)**2 + cos(lat1r) * cos(lat2r) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km


def compute_features(event: Dict[str, Any], conn: Optional[sqlite3.Connection] = None) -> Dict[str, Any]:
    ts = datetime.fromisoformat(event["timestamp"])
    hour = ts.hour
    day_of_week = ts.weekday()

    own_conn = conn is None
    conn = connect() if conn is None else conn
    cur = conn.cursor()

    cur.execute(
        "SELECT latitude, longitude, timestamp, device_id, success, resource FROM events WHERE user_id = ? ORDER BY timestamp DESC LIMIT 20",
        (event["user_id"],),
    )
    history = cur.fetchall()

    prev = None
    for h in history:
        try:
            if datetime.fromisoformat(h["timestamp"]) < ts:
                prev = h
                break
        except Exception:
            continue
    geo_distance_km = None
    geo_velocity_kmh = None
    new_device = 0
    failure_burst = 0.0
    resource_rarity = 0.0

    if prev:
        prev_lat = prev["latitude"]
        prev_lon = prev["longitude"]
        geo_distance_km = haversine_km(event.get("latitude"), event.get("longitude"), prev_lat, prev_lon)
        try:
            prev_ts = datetime.fromisoformat(prev["timestamp"])
            delta_hours = max((ts - prev_ts).total_seconds() / 3600.0, 1e-6)
            if geo_distance_km is not None:
                geo_velocity_kmh = geo_distance_km / delta_hours
        except Exception:
            geo_velocity_kmh = None
        new_device = 1 if (event.get("device_id") and prev["device_id"] and event["device_id"] != prev["device_id"]) else 0

    window_start = (ts - timedelta(minutes=15)).isoformat()
    row = cur.execute(
        "SELECT COUNT(*) as c, SUM(CASE WHEN success=0 THEN 1 ELSE 0 END) as f FROM events WHERE user_id=? AND timestamp>=? AND timestamp<?",
        (event["user_id"], window_start, event["timestamp"]),
    ).fetchone()
    total = row["c"] or 0
    failures = row["f"] or 0
    failure_burst = (failures / total) if total > 0 else 0.0

    # resource rarity: inverse frequency over last 7 days
    week_start = (ts - timedelta(days=7)).isoformat()
    total_week = cur.execute(
        "SELECT COUNT(*) FROM events WHERE user_id=? AND timestamp>=? AND timestamp<?",
        (event["user_id"], week_start, event["timestamp"]),
    ).fetchone()[0] or 0
    resource_count = cur.execute(
        "SELECT COUNT(*) FROM events WHERE user_id=? AND resource=? AND timestamp>=? AND timestamp<?",
        (event["user_id"], event["resource"], week_start, event["timestamp"]),
    ).fetchone()[0] or 0
    resource_rarity = (1.0 - (resource_count / total_week)) if total_week > 0 else 1.0

    off_hours = 1 if (hour < 6 or hour >= 22) else 0

    out = {
        "event_id": event["event_id"],
        "user_id": event["user_id"],
        "timestamp": event["timestamp"],
        "hour": hour,
        "day_of_week": day_of_week,
        "geo_distance_km": geo_distance_km,
        "geo_velocity_kmh": geo_velocity_kmh,
        "failure_burst": failure_burst,
        "resource_rarity": resource_rarity,
        "new_device": new_device,
        "off_hours": off_hours,
    }
    if own_conn:
        conn.close()
    return out
