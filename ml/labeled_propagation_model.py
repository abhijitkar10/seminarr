"""
Labeled Propagation Model for Anomaly Detection
Uses semi-supervised learning with labels from Book1.xlsx dataset
"""
from __future__ import annotations
from typing import Dict, Any, Tuple, Optional, List
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.semi_supervised import LabelPropagation
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
    f1_score,
    precision_score,
    recall_score,
    accuracy_score,
    auc,
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

    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
        """Prepare features from raw data"""
        features_df = df.copy()

        # Convert timestamp to features
        features_df["Login Timestamp"] = pd.to_datetime(features_df["Login Timestamp"])
        features_df["hour"] = features_df["Login Timestamp"].dt.hour
        features_df["day_of_week"] = features_df["Login Timestamp"].dt.weekday
        features_df["day_of_month"] = features_df["Login Timestamp"].dt.day

        # Categorical features to encode
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

        # Select numeric features
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

        # Handle missing values
        X = features_df[numeric_features].fillna(features_df[numeric_features].median())

        # Convert to numpy
        X_array = X.values.astype(np.float64)

        self.feature_names = numeric_features
        return X_array, numeric_features

    def train(
        self,
        df: pd.DataFrame,
        label_column: str = "Is Account Takeover",
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
        print(f"Loading {len(df)} rows of data...")

        # Prepare features
        X, feature_names = self.prepare_features(df)
        y = df[label_column].astype(int).values

        # Split data with stratification to handle imbalanced data
        X_train_val, X_test, y_train_val, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        X_train, X_val, y_train, y_val = train_test_split(
            X_train_val,
            y_train_val,
            test_size=test_size / (1 - test_size),
            random_state=random_state,
            stratify=y_train_val,
        )

        print(f"Training set: {len(X_train)} samples ({(y_train.sum() / len(y_train)):.2%} anomalies)")
        print(f"Validation set: {len(X_val)} samples ({(y_val.sum() / len(y_val)):.2%} anomalies)")
        print(f"Test set: {len(X_test)} samples ({(y_test.sum() / len(y_test)):.2%} anomalies)")

        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        X_test_scaled = self.scaler.transform(X_test)

        # For semi-supervised learning, mark ~50% of non-anomaly training samples as unlabeled
        y_train_semi = y_train.copy()
        # Only mark negative class samples as unlabeled (keep anomalies labeled)
        negative_indices = np.where(y_train == 0)[0]
        n_unlabeled = int(len(negative_indices) * 0.5)
        unlabeled_idx = np.random.RandomState(random_state).choice(
            negative_indices, n_unlabeled, replace=False
        )
        y_train_semi[unlabeled_idx] = -1

        # Train labeled propagation model with optimized parameters
        print("\nTraining Labeled Propagation model...")
        self.model = LabelPropagation(
            kernel="rbf", 
            gamma=0.3,  # Increased gamma for tighter decision boundaries
            n_neighbors=10,  # More neighbors for better propagation
            max_iter=1000,
            tol=1e-3
        )

        # Combine train and validation for semi-supervised training
        X_train_combined = np.vstack([X_train_scaled, X_val_scaled])
        y_train_combined = np.concatenate([y_train_semi, y_val])

        self.model.fit(X_train_combined, y_train_combined)

        # Get probability outputs for better evaluation
        y_pred_proba_test = self.model.predict_proba(X_test_scaled)[:, 1]
        
        # Find optimal threshold using validation set
        y_pred_proba_val = self.model.predict_proba(X_val_scaled)[:, 1]
        fpr, tpr, thresholds = roc_curve(y_val, y_pred_proba_val)
        optimal_idx = np.argmax(tpr - fpr)  # Youden's index
        optimal_threshold = thresholds[optimal_idx]
        
        print(f"\nOptimal decision threshold: {optimal_threshold:.4f}")
        
        # Apply optimal threshold
        y_pred = (y_pred_proba_test >= optimal_threshold).astype(int)

        # Calculate metrics
        metrics = self._calculate_metrics(
            y_test, y_pred, y_pred_proba_test, "Test Set", optimal_threshold
        )

        # Also evaluate on full test set
        print("\n" + "="*60)
        print("EVALUATION RESULTS")
        print("="*60)

        self.metrics = metrics
        self.trained = True
        self.optimal_threshold = optimal_threshold

        return metrics

    def _calculate_metrics(
        self, y_true: np.ndarray, y_pred: np.ndarray, y_pred_proba: np.ndarray, set_name: str = "", threshold: float = 0.5
    ) -> Dict[str, Any]:
        """Calculate all evaluation metrics"""
        cm = confusion_matrix(y_true, y_pred)
        
        # Handle case where confusion matrix might be 1x2 or 2x1
        if cm.shape == (1, 2):
            tn, fp = cm[0]
            fn, tp = 0, 0
        elif cm.shape == (2, 1):
            fn, tn = cm[0, 0], 0
            tp, fp = cm[1, 0], 0
        elif cm.shape == (1, 1):
            # Only one class predicted
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
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "set_name": set_name,
            "threshold": float(threshold),
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, zero_division=0)),
            "f1": float(f1_score(y_true, y_pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_true, y_pred_proba)),
            "specificity": float(specificity),
            "sensitivity": float(sensitivity),
            "true_positives": int(tp),
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
        }

        metrics["confusion_matrix"] = cm.tolist()

        print(f"\n{set_name} Metrics:")
        print(f"  Accuracy:  {metrics['accuracy']:.4f}")
        print(f"  Precision: {metrics['precision']:.4f}")
        print(f"  Recall:    {metrics['recall']:.4f}")
        print(f"  F1 Score:  {metrics['f1']:.4f}")
        print(f"  ROC-AUC:   {metrics['roc_auc']:.4f}")
        print(f"  Specificity: {metrics['specificity']:.4f}")

        print(f"\nConfusion Matrix:\n{cm}")

        # Detailed classification report
        print(f"\nClassification Report:")
        print(classification_report(y_true, y_pred, target_names=["Normal", "Anomaly"]))

        return metrics

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Predict on new data using optimal threshold"""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        if self.scaler is None:
            raise ValueError("Scaler not initialized.")

        X_scaled = self.scaler.transform(X)
        probabilities = self.model.predict_proba(X_scaled)[:, 1]
        predictions = (probabilities >= self.optimal_threshold).astype(int)

        return predictions, probabilities

    def save(self) -> None:
        """Save model and artifacts"""
        LP_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump(self.model, LP_MODEL_PATH)
        joblib.dump(self.scaler, LP_SCALER_PATH)
        joblib.dump(self.encoders, LP_ENCODERS_PATH)

        with open(LP_EVAL_PATH, "w") as f:
            json.dump(self.metrics, f, indent=2, default=str)

        print(f"\nModel saved to {LP_MODEL_PATH}")
        print(f"Scaler saved to {LP_SCALER_PATH}")
        print(f"Encoders saved to {LP_ENCODERS_PATH}")
        print(f"Evaluation metrics saved to {LP_EVAL_PATH}")

    def load(self) -> None:
        """Load model and artifacts"""
        if LP_MODEL_PATH.exists():
            self.model = joblib.load(LP_MODEL_PATH)
            self.scaler = joblib.load(LP_SCALER_PATH)
            self.encoders = joblib.load(LP_ENCODERS_PATH)
            self.trained = True
            print(f"Model loaded from {LP_MODEL_PATH}")
