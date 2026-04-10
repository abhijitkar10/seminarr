from __future__ import annotations
from typing import Dict, Any, Tuple, List, Optional
from pathlib import Path
import numpy as np
from data.db import connect, insert_anomaly
import json
import joblib
import pandas as pd


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

# Ensemble model paths
ENSEMBLE_META_PATH = Path(__file__).resolve().parents[1] / "data" / "rba_ensemble_meta.joblib"
ENSEMBLE_EVAL_PATH = Path(__file__).resolve().parents[1] / "data" / "rba_ensemble_eval.json"


class AnomalyDetector:
    """
    Anomaly detector using 4-Model Ensemble (RBA-based).
    
    Ensemble models:
    - Label Propagation (semi-supervised)
    - Label Spreading (semi-supervised)
    - Self-Training Random Forest (semi-supervised)
    - Self-Training Extra Trees (semi-supervised)
    
    Risk Score Calculation:
    risk = weighted_avg(lp_score, ls_score, st_rf_score, st_et_score)
    where weights are derived from Average Precision on labeled validation data
    
    Classification (based on risk 0.0-1.0):
    - Critical: risk >= best_threshold + 0.25
    - High: risk >= best_threshold + 0.15
    - Medium: risk >= best_threshold + 0.05
    - Low: risk < best_threshold + 0.05
    """

    def __init__(self):
        self.ensemble = None
        self.trained = False
        self.best_threshold = 0.5
        self._try_load()

    @property
    def is_trained(self) -> bool:
        return self.trained

    def _try_load(self) -> None:
        """Try to load saved ensemble model"""
        try:
            from ml.rba_ensemble import RBAEnsembleDetector
            self.ensemble = RBAEnsembleDetector()
            if self.ensemble.is_trained:
                self.trained = True
                self.best_threshold = self.ensemble.best_threshold
        except Exception:
            pass

    def train(self) -> None:
        """Train 4-model ensemble on events with labels"""
        from ml.rba_ensemble import RBAEnsembleDetector

        conn = connect()
        rows = conn.execute(
            "SELECT * FROM events ORDER BY timestamp DESC LIMIT 5000"
        ).fetchall()
        conn.close()

        if len(rows) < 100:
            return

        # Convert to DataFrame with Book1-style column names
        data = [dict(r) for r in rows]
        df = pd.DataFrame(data)

        # Rename to Book1 style if needed
        column_mapping = {
            "timestamp": "Login Timestamp",
            "user_id": "User ID",
            "success": "Login Successful",
            "ip_address": "IP Address",
            "location": "Country",
        }
        for old, new in column_mapping.items():
            if old in df.columns and new not in df.columns:
                df[new] = df[old]

        # Check for label column
        label_col = None
        if "Is Attack IP" in df.columns:
            label_col = "Is Attack IP"
        elif "Is Account Takeover" in df.columns:
            label_col = "Is Account Takeover"
        else:
            # Assume some rows are attacks based on features
            return

        try:
            detector = RBAEnsembleDetector()
            metrics = detector.train(df, label_column=label_col)
            detector.save()
            self.ensemble = detector
            self.trained = True
            self.best_threshold = detector.best_threshold
            print("✓ Ensemble model trained and saved")
        except Exception as e:
            print(f"Ensemble training failed: {e}")

    def score_event(
        self, feature_row: Dict[str, Any]
    ) -> Tuple[float, Dict[str, float]]:
        """
        Score event using 4-model ensemble.
        
        Input: feature_row dict from features table or event dict
        Returns: (risk_score, per_model_scores)
        
        Per-model scores:
        - lp: Label Propagation probability (0.0-1.0)
        - ls: Label Spreading probability (0.0-1.0)
        - st_rf: Self-Training RF probability (0.0-1.0)
        - st_et: Self-Training ET probability (0.0-1.0)
        """
        if not self.trained:
            self._try_load()
            if not self.trained:
                # Fallback: return zero scores
                return 0.0, {"lp": 0.0, "ls": 0.0, "st_rf": 0.0, "st_et": 0.0}

        try:
            # Score using ensemble
            risk, per_model = self.ensemble.score_event(feature_row)
            return risk, per_model
        except Exception:
            # Fallback if ensemble scoring fails
            return 0.0, {"lp": 0.0, "ls": 0.0, "st_rf": 0.0, "st_et": 0.0}

    def risk_score(
        self, ensemble_risk: float, feature_row: Dict[str, Any]
    ) -> Tuple[float, List[str]]:
        """
        Interpret ensemble risk score and add contextual reasons.
        
        Inputs:
        - ensemble_risk: normalized score from ensemble (0.0-1.0)
        - feature_row: dict of features for context
        
        Returns: (final_risk_score, list_of_reasons)
        
        Final risk is ensemble_risk scaled to 0-3.0 with adjustments.
        """
        reasons = []
        # Scale ensemble risk to 0-3.0 range for classification
        risk = ensemble_risk * 3.0

        # Add context-based adjustments
        if feature_row.get("off_hours"):
            risk += 0.15
            reasons.append("Off-hours access")
        
        if (feature_row.get("geo_velocity_kmh") or 0) > 900:
            risk += 0.25
            reasons.append("Unrealistic geo-velocity")
        
        if (feature_row.get("failure_burst") or 0) > 0.7:
            risk += 0.20
            reasons.append("Failure burst before event")
        
        if (feature_row.get("resource_rarity") or 0) > 0.9:
            risk += 0.15
            reasons.append("Rare resource access")
        
        if feature_row.get("new_device"):
            risk += 0.10
            reasons.append("New device detected")

        return float(np.clip(risk, 0.0, 3.0)), reasons

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

