"""
Labeled Propagation Model for Anomaly Detection
Semi-supervised learning from authentication logs
"""
from __future__ import annotations
from typing import Dict, Any, Tuple
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.semi_supervised import LabelPropagation
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    confusion_matrix,
    roc_auc_score,
    roc_curve,
    f1_score,
    precision_score,
    recall_score,
    accuracy_score,
)
import joblib
import json
from datetime import datetime


LP_MODEL_PATH = Path(__file__).resolve().parents[1] / "data" / "labeled_propagation_model.joblib"
LP_SCALER_PATH = Path(__file__).resolve().parents[1] / "data" / "lp_scaler.joblib"
LP_ENCODERS_PATH = Path(__file__).resolve().parents[1] / "data" / "lp_encoders.joblib"
LP_EVAL_PATH = Path(__file__).resolve().parents[1] / "data" / "lp_evaluation.json"


class LabeledPropagationDetector:
    """Semi-supervised anomaly detection using Labeled Propagation"""

    def __init__(self):
        self.model: LabelPropagation | None = None
        self.scaler: StandardScaler | None = None
        self.encoders: Dict[str, LabelEncoder] = {}
        self.feature_names: list[str] = []
        self.metrics: Dict[str, Any] = {}
        self.trained = False
        self.optimal_threshold: float = 0.5
        self._try_load()

    @property
    def is_trained(self) -> bool:
        return self.trained

    def _try_load(self) -> None:
        """Try to load saved model"""
        if LP_MODEL_PATH.exists():
            self.load()

    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, list[str]]:
        """Extract and prepare features from authentication logs"""
        features_df = df.copy()

        # Extract temporal features from timestamp
        features_df["Login Timestamp"] = pd.to_datetime(features_df["Login Timestamp"])
        features_df["hour"] = features_df["Login Timestamp"].dt.hour
        features_df["day_of_week"] = features_df["Login Timestamp"].dt.weekday
        features_df["day_of_month"] = features_df["Login Timestamp"].dt.day

        # Encode categorical features
        categorical_features = ["Country", "Device Type", "Browser Name and Version"]
        for cat_feature in categorical_features:
            if cat_feature not in self.encoders:
                self.encoders[cat_feature] = LabelEncoder()
                features_df[cat_feature] = self.encoders[cat_feature].fit_transform(
                    features_df[cat_feature].astype(str)
                )
            else:
                features_df[cat_feature] = self.encoders[cat_feature].transform(
                    features_df[cat_feature].astype(str)
                )

        # Define features for training
        numeric_features = [
            "Round-Trip Time [ms]",
            "ASN",
            "hour",
            "day_of_week",
            "day_of_month",
            "Country",
            "Device Type",
            "Browser Name and Version",
        ]

        self.feature_names = numeric_features

        # Impute missing values with median
        X = features_df[numeric_features].fillna(features_df[numeric_features].median())
        return X.values.astype(np.float64), numeric_features

    def train(
        self,
        df: pd.DataFrame,
        label_column: str = "Is Attack IP",
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> Dict[str, Any]:
        """
        Train labeled propagation model with train/test split

        Args:
            df: DataFrame with data and labels
            label_column: Column name for labels
            test_size: Proportion of data for testing
            random_state: Random state for reproducibility

        Returns:
            Dictionary with evaluation metrics
        """
        print(f"Loading {len(df)} rows of authentication logs...")

        # Prepare features and labels
        X, feature_names = self.prepare_features(df)
        y = df[label_column].astype(int).values

        # Stratified train/test split
        X_train_val, X_test, y_train_val, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        # Further split training data into train and validation
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_val,
            y_train_val,
            test_size=test_size / (1 - test_size),
            random_state=random_state,
            stratify=y_train_val,
        )

        print(f"Train: {len(X_train)} ({y_train.sum()/len(y_train):.2%} anomalies)")
        print(f"Val:   {len(X_val)} ({y_val.sum()/len(y_val):.2%} anomalies)")
        print(f"Test:  {len(X_test)} ({y_test.sum()/len(y_test):.2%} anomalies)")

        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        X_test_scaled = self.scaler.transform(X_test)

        # Semi-supervised setup: mark 50% of negative samples as unlabeled
        y_train_semi = y_train.copy()
        negative_indices = np.where(y_train == 0)[0]
        n_unlabeled = int(len(negative_indices) * 0.5)
        unlabeled_idx = np.random.RandomState(random_state).choice(
            negative_indices, n_unlabeled, replace=False
        )
        y_train_semi[unlabeled_idx] = -1

        # Train Labeled Propagation model
        print("\nTraining Labeled Propagation model...")
        self.model = LabelPropagation(
            kernel="rbf",
            gamma=0.3,
            n_neighbors=10,
            max_iter=1000,
            tol=1e-3,
        )

        # Combine train and validation for semi-supervised training
        X_combined = np.vstack([X_train_scaled, X_val_scaled])
        y_combined = np.concatenate([y_train_semi, y_val])

        self.model.fit(X_combined, y_combined)

        # Find optimal decision threshold
        y_pred_proba_val = self.model.predict_proba(X_val_scaled)[:, 1]
        fpr, tpr, thresholds = roc_curve(y_val, y_pred_proba_val)
        optimal_idx = np.argmax(tpr - fpr)
        optimal_threshold = thresholds[optimal_idx]

        print(f"Optimal threshold: {optimal_threshold:.4f}")

        # Evaluate on test set
        y_pred_proba_test = self.model.predict_proba(X_test_scaled)[:, 1]
        y_pred = (y_pred_proba_test >= optimal_threshold).astype(int)

        # Calculate metrics
        metrics = self._calculate_metrics(
            y_test, y_pred, y_pred_proba_test, optimal_threshold
        )

        self.metrics = metrics
        self.trained = True
        self.optimal_threshold = optimal_threshold

        print("\n" + "="*60)
        print("EVALUATION RESULTS")
        print("="*60)
        self._print_metrics(metrics)

        return metrics

    def _calculate_metrics(
        self, y_true: np.ndarray, y_pred: np.ndarray, y_pred_proba: np.ndarray, threshold: float = 0.5
    ) -> Dict[str, Any]:
        """Calculate evaluation metrics"""
        cm = confusion_matrix(y_true, y_pred)

        # Handle edge cases with confusion matrix shape
        if cm.shape == (1, 2):
            tn, fp = cm[0]
            fn, tp = 0, 0
        elif cm.shape == (2, 1):
            fn, tn = cm[0, 0], 0
            tp, fp = cm[1, 0], 0
        elif cm.shape == (1, 1):
            if y_pred[0] == 0:
                tn = np.sum(y_true == 0)
                fp, fn, tp = 0, np.sum(y_true == 1), 0
            else:
                tp = np.sum(y_true == 1)
                tn, fp, fn = 0, np.sum(y_true == 0), 0
        else:
            tn, fp, fn, tp = cm.ravel()

        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        return {
            "timestamp": datetime.now().isoformat(),
            "threshold": float(threshold),
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, zero_division=0)),
            "f1": float(f1_score(y_true, y_pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_true, y_pred_proba)),
            "specificity": float(specificity),
            "sensitivity": float(sensitivity),
            "tp": int(tp),
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "confusion_matrix": cm.tolist(),
        }

    def _print_metrics(self, metrics: Dict[str, Any]) -> None:
        """Pretty print metrics"""
        print(f"Accuracy:  {metrics['accuracy']:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall:    {metrics['recall']:.4f}")
        print(f"F1 Score:  {metrics['f1']:.4f}")
        print(f"ROC-AUC:   {metrics['roc_auc']:.4f}")
        print(f"Specificity: {metrics['specificity']:.4f}")
        print(f"Sensitivity: {metrics['sensitivity']:.4f}")
        print(f"\nConfusion Matrix:")
        print(f"  TN: {metrics['tn']:5d}  FP: {metrics['fp']:5d}")
        print(f"  FN: {metrics['fn']:5d}  TP: {metrics['tp']:5d}")

    def save(self) -> None:
        """Save model and preprocessing objects"""
        joblib.dump(self.model, LP_MODEL_PATH)
        joblib.dump(self.scaler, LP_SCALER_PATH)
        joblib.dump(self.encoders, LP_ENCODERS_PATH)
        with open(LP_EVAL_PATH, "w") as f:
            json.dump(self.metrics, f, indent=2)
        print(f"Model saved to {LP_MODEL_PATH}")

    def load(self) -> None:
        """Load saved model and preprocessing objects"""
        if not LP_MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found at {LP_MODEL_PATH}")
        self.model = joblib.load(LP_MODEL_PATH)
        self.scaler = joblib.load(LP_SCALER_PATH)
        self.encoders = joblib.load(LP_ENCODERS_PATH)
        with open(LP_EVAL_PATH, "r") as f:
            self.metrics = json.load(f)
        self.trained = True
        print(f"Model loaded from {LP_MODEL_PATH}")

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Make predictions on new data"""
        if not self.trained:
            raise ValueError("Model not trained. Call train() first.")
        X, _ = self.prepare_features(df)
        X_scaled = self.scaler.transform(X)
        y_pred_proba = self.model.predict_proba(X_scaled)[:, 1]
        return (y_pred_proba >= self.optimal_threshold).astype(int)
