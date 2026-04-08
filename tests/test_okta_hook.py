import uuid

from fastapi.testclient import TestClient

from app.main import app


def test_okta_hook_verification() -> None:
    client = TestClient(app)
    r = client.get("/hooks/okta", headers={"x-okta-verification-challenge": "abc"})
    assert r.status_code == 200
    assert r.json() == {"verification": "abc"}


def test_okta_hook_ingests_event(monkeypatch) -> None:
    monkeypatch.delenv("OKTA_EVENT_HOOK_AUTH_SECRET", raising=False)
    monkeypatch.delenv("OKTA_EVENT_HOOK_AUTH_HEADER", raising=False)

    client = TestClient(app)
    evt = {
        "uuid": str(uuid.uuid4()),
        "published": "2026-03-28T09:00:00Z",
        "eventType": "user.session.start",
        "displayMessage": "User login to app",
        "actor": {"alternateId": "alice@corp.com"},
        "outcome": {"result": "SUCCESS"},
        "client": {
            "ipAddress": "203.0.113.10",
            "geographicalContext": {
                "city": "San Francisco",
                "country": "US",
                "geolocation": {"lat": 37.7749, "lon": -122.4194},
            },
            "userAgent": {"rawUserAgent": "Mozilla/5.0"},
        },
    }
    r = client.post("/hooks/okta", json={"data": {"events": [evt]}})
    assert r.status_code == 200
    body = r.json()
    assert body["accepted"] == 1
