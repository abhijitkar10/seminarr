from ml.features import haversine_km, compute_features


def test_haversine_basic():
    # SF to NYC ~ 4125 km
    km = haversine_km(37.7749, -122.4194, 40.7128, -74.0060)
    assert 3800 < km < 4500


def test_compute_features_minimal(monkeypatch):
    event = {
        "event_id": "e1",
        "user_id": "u1",
        "timestamp": "2024-01-01T12:00:00",
        "resource": "crm",
        "action": "login",
        "success": True,
        "latitude": None,
        "longitude": None,
    }
    f = compute_features(event)
    assert f["event_id"] == "e1"
    assert "hour" in f and "day_of_week" in f
