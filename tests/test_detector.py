from ml.detector import AnomalyDetector
from data.db import insert_features, init_db


def test_detector_train_and_score():
    init_db()
    # insert synthetic features
    rows = []
    for i in range(100):
        rows.append({
            "event_id": f"e{i}",
            "user_id": "u1",
            "timestamp": f"2024-01-01T12:{i%60:02d}:00",
            "hour": 12,
            "day_of_week": 1,
            "geo_distance_km": 0.5,
            "geo_velocity_kmh": 5.0,
            "failure_burst": 0.0,
            "resource_rarity": 0.2,
            "new_device": 0,
            "off_hours": 0,
        })
    insert_features(rows)
    det = AnomalyDetector()
    det.train()
    score, contrib = det.score_event(rows[-1])
    assert isinstance(score, float)
    assert "hour" in contrib
