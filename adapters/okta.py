from __future__ import annotations
from typing import Dict, Any
from datetime import datetime
import uuid


def normalize_okta_event(evt: Dict[str, Any]) -> Dict[str, Any]:
    # Okta System Log minimal fields (best effort)
    # Reference: https://developer.okta.com/docs/reference/api/system-log/
    actor = evt.get("actor", {}) or {}
    client = evt.get("client", {}) or {}
    outcome = evt.get("outcome", {}) or {}
    geoclient = client.get("geographicalContext", {}) or {}
    ip = client.get("ipAddress")
    lat = geoclient.get("geolocation", {}).get("lat")
    lon = geoclient.get("geolocation", {}).get("lon")
    location = geoclient.get("city") or geoclient.get("state") or geoclient.get("country")

    ts = evt.get("published") or evt.get("eventTime") or datetime.utcnow().isoformat()
    try:
        # normalize ISO format if needed
        _ = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        ts = datetime.utcnow().isoformat()

    user_id = actor.get("alternateId") or actor.get("id") or "unknown"
    resource = (evt.get("displayMessage") or evt.get("eventType") or "auth_event")[:64]
    action = evt.get("eventType") or "login"
    success = outcome.get("result") == "SUCCESS"
    mfa_used = (evt.get("transaction", {}) or {}).get("type") == "MFA"
    failure_reason = None if success else (outcome.get("reason") or outcome.get("result"))
    ua = client.get("userAgent", {}) or {}
    user_agent = ua.get("rawUserAgent") or ua.get("browser")
    device_id = client.get("device", {}).get("id") if isinstance(client.get("device"), dict) else None
    privilege_level = None

    return {
        "event_id": evt.get("uuid") or str(uuid.uuid4()),
        "user_id": user_id,
        "timestamp": ts.replace("Z", "+00:00") if isinstance(ts, str) else ts,
        "ip_address": ip,
        "latitude": lat,
        "longitude": lon,
        "location": location,
        "user_agent": user_agent,
        "device_id": device_id,
        "resource": resource,
        "action": action,
        "success": success,
        "mfa_used": mfa_used,
        "failure_reason": failure_reason,
        "privilege_level": privilege_level,
    }
