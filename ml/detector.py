from __future__ import annotations
from typing import Dict, Any, Tuple, List, Optional
from pathlib import Path
import numpy as np
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

LP_MODEL_PATH = Path(__file__).resolve().parents[1] / "data" / "labeled_propagation_model.joblib"
LP_SCALER_PATH = Path(__file__).resolve().parents[1] / "data" / "lp_scaler.joblib"
LP_ENCODERS_PATH = Path(__file__).resolve().parents[1] / "data" / "lp_encoders.joblib"
LP_EVAL_PATH = Path(__file__).resolve().parents[1] / "data" / "lp_evaluation.json"


class AnomalyDetector:
    """Anomaly detector using Labeled Propagation semi-supervised learning"""

    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoders = {}
        self.optimal_threshold = 0.5
        self.trained = False
        self.means: np.ndarray | None = None
        self.stds: np.ndarray | None = None
        self._try_load()

    @property
    def is_trained(self) -> bool:
        return self.trained

    def _try_load(self) -> None:
        """Try to load saved Labeled Propagation model"""
        if LP_MODEL_PATH.exists():
            self.load_labeled_propagation()

    def load_labeled_propagation(self) -> None:
        """Load labeled propagation model and preprocessing objects"""
        if LP_MODEL_PATH.exists():
            self.model = joblib.load(LP_MODEL_PATH)
            self.scaler = joblib.load(LP_SCALER_PATH) if LP_SCALER_PATH.exists() else None
            self.encoders = joblib.load(LP_ENCODERS_PATH) if LP_ENCODERS_PATH.exists() else {}

            # Load optimal threshold from evaluation metrics
            if LP_EVAL_PATH.exists():
                with open(LP_EVAL_PATH, "r") as f:
                    metrics = json.load(f)
                    self.optimal_threshold = metrics.get("threshold", 0.5)

            self.trained = True

    def train(self) -> None:
        """Train Labeled Propagation model on events with labels"""
        from ml.labeled_propagation_model import LabeledPropagationDetector
        import pandas as pd

        conn = connect()
        rows = conn.execute(
            "SELECT * FROM events ORDER BY timestamp DESC LIMIT 50000"
        ).fetchall()
        conn.close()

        if len(rows) < 50:
            return

        # Convert to DataFrame
        data = [dict(r) for r in rows]
        df = pd.DataFrame(data)

        # Check for label column
        label_col = None
        if "Is Attack IP" in df.columns:
            label_col = "Is Attack IP"
        elif "Is Account Takeover" in df.columns:
            label_col = "Is Account Takeover"
        else:
            return

        # Train model
        detector = LabeledPropagationDetector()
        detector.train(df, label_column=label_col)
        detector.save()
        self.load_labeled_propagation()

    def score_event(
        self, feature_row: Dict[str, Any]
    ) -> Tuple[float, Dict[str, float]]:
        """Score event using Labeled Propagation model"""
        if not self.trained:
            self._try_load()

        x = np.array(
            [self._safe_float(feature_row.get(k)) for k in FEATURE_KEYS], dtype=float
        )
        x = np.where(np.isnan(x), 0.0, x)

        # Anomaly score based on feature deviation
        score = float(np.sum(np.abs(x))) / len(x) if len(x) > 0 else 0.0

        if self.means is None or self.stds is None:
            # Initialize on first use
            self.means = np.zeros(len(x))
            self.stds = np.ones(len(x))

        z = np.abs((x - self.means) / self.stds)
        return score, {k: float(v) for k, v in zip(FEATURE_KEYS, z)}

    def risk_score(self, s: float, f: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Calculate risk score from anomaly score and features"""
        reasons = []
        risk = 0.0

        # Base score from anomaly detection
        risk += 0.5 * s

        # Feature-based risk factors
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
            reasons.append("Rare resource access")
        if not f.get("new_device"):
            risk -= 0.2

        return risk, reasons

    def record_anomaly(
        self,
        event: Dict[str, Any],
        score: float,
        risk: float,
        reasons: List[str],
        contributions: Dict[str, float],
    ) -> None:
        """Record detected anomaly in database"""
        conn = connect()
        conn.execute(
            "INSERT INTO anomalies (event_id, user_id, timestamp, score, risk, reasons, contributions) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                event.get("event_id"),
                event.get("user_id"),
                event.get("timestamp"),
                score,
                risk,
                json.dumps(reasons),
                json.dumps(contributions),
            ),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def _safe_float(v: Any) -> float:
        """Safely convert value to float"""
        if v is None:
            return np.nan
        try:
            return float(v)
        except (ValueError, TypeError):
            return np.nan


    def score_event(self, feature_row: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        if not self.trained:
            self._try_load()
        
        return self._score_event_lp(feature_row)

    def _score_event_lp(self, feature_row: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Score using Labeled Propagation model"""
        x = np.array([self._safe_float(feature_row.get(k)) for k in FEATURE_KEYS], dtype=float)
        x = np.where(np.isnan(x), 0.0, x)
        
        # For now, return a normalized anomaly score based on distance
        score = float(np.sum(np.abs(x))) / len(x) if len(x) > 0 else 0.0
        
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


# ─────────────────────────────────────────────────────────────────────────────
# Convenience accessor for the multi-model ensemble
# ─────────────────────────────────────────────────────────────────────────────

_ensemble_instance: Optional[Any] = None


def get_ensemble_detector():
    """
    Return a (cached) RBAEnsembleDetector instance.
    The ensemble covers 6 models trained on Book1-style RBA data:
      Label Propagation, Label Spreading, Self-Training RF,
      Self-Training Extra Trees, Isolation Forest, One-Class SVM.
    """
    global _ensemble_instance
    if _ensemble_instance is None:
        from ml.rba_ensemble import RBAEnsembleDetector
        _ensemble_instance = RBAEnsembleDetector()
    return _ensemble_instance
