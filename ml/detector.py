from __future__ import annotations
from typing import Dict, Any, Tuple, List
from pathlib import Path
import numpy as np
from sklearn.ensemble import IsolationForest
from data.db import connect, insert_anomaly
import json
import joblib


FEATURE_KEYS = (
    "hour",
    "day_of_week",
    "geo_distance_km",
    "geo_velocity_kmh",
    "failure_burst",
    "resource_rarity",
    "new_device",
    "off_hours",
)

MODEL_PATH = Path(__file__).resolve().parents[1] / "data" / "model.joblib"


class AnomalyDetector:
    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        self.model = IsolationForest(contamination=contamination, random_state=random_state)
        self.trained = False
        self.means: np.ndarray | None = None
        self.stds: np.ndarray | None = None
        self._try_load()

    @property
    def is_trained(self) -> bool:
        return self.trained

    def _try_load(self) -> None:
        if MODEL_PATH.exists():
            self.load()

    def save(self) -> None:
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {"model": self.model, "means": self.means, "stds": self.stds},
            MODEL_PATH,
        )

    def load(self) -> None:
        data = joblib.load(MODEL_PATH)
        self.model = data["model"]
        self.means = data["means"]
        self.stds = data["stds"]
        self.trained = True

    def train(self) -> None:
        conn = connect()
        rows = conn.execute("SELECT * FROM features ORDER BY timestamp DESC LIMIT 2000").fetchall()
        conn.close()
        if len(rows) < 50:
            return
        X = np.array([[self._safe_float(r[k]) for k in FEATURE_KEYS] for r in rows], dtype=float)
        col_means = np.where(np.isnan(X), 0.0, X).mean(axis=0)
        X = np.where(np.isnan(X), col_means, X)
        self.model.fit(X)
        self.trained = True
        self.means = np.nanmean(X, axis=0)
        self.stds = np.nanstd(X, axis=0) + 1e-6
        self.save()

    def score_event(self, feature_row: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        if not self.trained:
            self._try_load()
        x = np.array([self._safe_float(feature_row.get(k)) for k in FEATURE_KEYS], dtype=float)
        x = np.where(np.isnan(x), 0.0, x)
        score = -float(self.model.score_samples([x])[0]) if self.trained else 0.0
        if self.means is None or self.stds is None:
            return score, {k: float(v) for k, v in zip(FEATURE_KEYS, x)}
        z = np.abs((x - self.means) / self.stds)
        return score, {k: float(v) for k, v in zip(FEATURE_KEYS, z)}

    def risk_score(self, s: float, f: Dict[str, Any]) -> Tuple[float, List[str]]:
        reasons = []
        risk = 0.0
        # weights
        risk += 0.5 * s
        if f.get("off_hours"):
            risk += 0.8
            reasons.append("Off-hours access")
        if (f.get("geo_velocity_kmh") or 0) > 600:
            risk += 1.2
            reasons.append("Unrealistic geo-velocity")
        if (f.get("failure_burst") or 0) > 0.5:
            risk += 1.0
            reasons.append("Failure burst before event")
        if (f.get("resource_rarity") or 0) > 0.8:
            risk += 0.7
            reasons.append("Unusual resource access")
        if f.get("new_device"):
            risk += 0.6
            reasons.append("New device detected")
        return risk, reasons

    def record_anomaly(self, feature_row: Dict[str, Any], score: float, risk: float, reasons: List[str], contributions: Dict[str, float]) -> None:
        if risk >= 1.0 or score > 0.5:
            insert_anomaly(
                event_id=feature_row["event_id"],
                user_id=feature_row["user_id"],
                timestamp=feature_row["timestamp"],
                score=score,
                risk=risk,
                reasons=json.dumps(reasons),
                contributions=json.dumps(contributions),
            )

    @staticmethod
    def _safe_float(x: Any) -> float:
        try:
            if x is None:
                return np.nan
            return float(x)
        except Exception:
            return np.nan
