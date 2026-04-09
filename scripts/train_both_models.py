#!/usr/bin/env python3
"""
Training script for both Labeled Propagation and IsolationForest
Ensures both models are trained on identical data splits
"""
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.semi_supervised import LabelPropagation
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    classification_report,
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

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def prepare_features(df: pd.DataFrame, scaler=None, encoders=None, is_fit=False):
    """Prepare features from raw data"""
    features_df = df.copy()
    
    if encoders is None:
        encoders = {}

    # Convert timestamp to features
    features_df["Login Timestamp"] = pd.to_datetime(features_df["Login Timestamp"])
    features_df["hour"] = features_df["Login Timestamp"].dt.hour
    features_df["day_of_week"] = features_df["Login Timestamp"].dt.weekday
    features_df["day_of_month"] = features_df["Login Timestamp"].dt.day

    # Categorical features to encode
    categorical_features = ["Country", "Device Type", "Browser Name and Version"]
    for cat_feature in categorical_features:
        if is_fit:
            encoders[cat_feature] = LabelEncoder()
            features_df[cat_feature] = encoders[cat_feature].fit_transform(
                features_df[cat_feature].astype(str)
            )
        else:
            categories_str = features_df[cat_feature].astype(str)
            known_classes = set(encoders[cat_feature].classes_)
            default_class = encoders[cat_feature].classes_[0]
            categories_str = categories_str.apply(
                lambda x: x if x in known_classes else default_class
            )
            features_df[cat_feature] = encoders[cat_feature].transform(categories_str)

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
    X_array = X.values.astype(np.float64)

    if is_fit and scaler is not None:
        X_array = scaler.fit_transform(X_array)
    elif scaler is not None:
        X_array = scaler.transform(X_array)

    return X_array, numeric_features, scaler, encoders


def evaluate_model(y_true, y_pred, y_pred_proba, model_name):
    """Print evaluation metrics"""
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_true, y_pred_proba)
    
    cm = confusion_matrix(y_true, y_pred)
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
    else:
        tn, fp, fn, tp = 0, 0, 0, 0
    
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0

    print(f"\n{'='*60}")
    print(f"{model_name} - TEST SET EVALUATION")
    print(f"{'='*60}")
    print(f"Accuracy:    {accuracy:.4f}")
    print(f"Precision:   {precision:.4f}")
    print(f"Recall:      {recall:.4f}")
    print(f"F1 Score:    {f1:.4f}")
    print(f"ROC-AUC:     {roc_auc:.4f}")
    print(f"Specificity: {specificity:.4f}")
    print(f"\nConfusion Matrix:\n{cm}")
    print(f"\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=["Normal", "Anomaly"], zero_division=0))
    
    return {
        "model": model_name,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc,
        "specificity": specificity,
    }


def main():
    """Train both models on identical data"""
    print("\n" + "="*70)
    print("TRAINING BOTH MODELS ON IDENTICAL DATA")
    print("="*70)
    
    # Load data
    excel_file = Path(__file__).parent.parent / "Book1.xlsx"
    print(f"\nLoading data from {excel_file}...")
    
    if not excel_file.exists():
        print(f"ERROR: File not found")
        sys.exit(1)
    
    df = pd.read_excel(excel_file)
    print(f"Loaded {len(df)} rows")
    
    # Prepare data
    label_column = "Is Attack IP"
    y = df[label_column].astype(int).values
    
    print(f"\nLabel distribution:")
    print(f"  Anomalies: {np.sum(y)} ({np.mean(y)*100:.2f}%)")
    print(f"  Normal:    {len(y) - np.sum(y)} ({(1-np.mean(y))*100:.2f}%)")
    
    # Create train/test split
    print("\nCreating train/test split (80/20)...")
    X_train_df, X_test_df, y_train, y_test = train_test_split(
        df, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Train: {len(X_train_df)} samples ({np.mean(y_train)*100:.2f}% anomalies)")
    print(f"Test:  {len(X_test_df)} samples ({np.mean(y_test)*100:.2f}% anomalies)")
    
    # Prepare features
    print("\nPreparing features...")
    scaler = StandardScaler()
    
    X_train, features, scaler, encoders = prepare_features(
        X_train_df, scaler=scaler, encoders={}, is_fit=True
    )
    X_test, _, scaler, encoders = prepare_features(
        X_test_df, scaler=scaler, encoders=encoders, is_fit=False
    )
    
    results = []
    
    # ========== ISOLATION FOREST ==========
    print("\n" + "="*70)
    print("TRAINING ISOLATIONFOREST")
    print("="*70)
    
    iso_forest = IsolationForest(contamination=0.10, random_state=42, n_jobs=-1)
    iso_forest.fit(X_train)
    
    y_pred_iso = iso_forest.predict(X_test)
    y_pred_iso = (y_pred_iso == -1).astype(int)  # -1 is anomaly, 1 is normal
    
    # Use decision function for probability
    y_pred_proba_iso = -iso_forest.score_samples(X_test)
    y_pred_proba_iso = (y_pred_proba_iso - y_pred_proba_iso.min()) / (y_pred_proba_iso.max() - y_pred_proba_iso.min() + 1e-10)
    
    iso_metrics = evaluate_model(y_test, y_pred_iso, y_pred_proba_iso, "IsolationForest")
    results.append(iso_metrics)
    
    # Save IsolationForest model
    iso_model_path = Path(__file__).parent.parent / "data" / "isolation_forest_model.joblib"
    iso_model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({
        "model": iso_forest,
        "scaler": scaler,
        "encoders": encoders,
        "metrics": iso_metrics,
        "timestamp": datetime.now().isoformat()
    }, iso_model_path)
    print(f"\nIsolationForest model saved to {iso_model_path}")
    
    # ========== LABELED PROPAGATION ==========
    print("\n" + "="*70)
    print("TRAINING LABELED PROPAGATION")
    print("="*70)
    
    # For semi-supervised learning, mark ~40% of negative samples as unlabeled
    y_train_semi = y_train.copy()
    negative_indices = np.where(y_train == 0)[0]
    n_unlabeled = int(len(negative_indices) * 0.4)
    unlabeled_idx = np.random.RandomState(42).choice(
        negative_indices, n_unlabeled, replace=False
    )
    y_train_semi[unlabeled_idx] = -1
    
    print(f"Training data setup:")
    print(f"  Labeled samples: {np.sum(y_train >= 0)}")
    print(f"  Unlabeled samples: {np.sum(y_train_semi == -1)}")
    print(f"  Anomalies (labeled): {np.sum(y_train == 1)}")
    
    # Train with optimized parameters
    lp_model = LabelPropagation(
        kernel="rbf",
        gamma=0.3,
        n_neighbors=10,
        max_iter=1000,
        tol=1e-3
    )
    
    lp_model.fit(X_train, y_train_semi)
    
    # Find optimal threshold using ROC curve
    y_pred_proba_train = lp_model.predict_proba(X_train[y_train >= 0])[:, 1]
    y_train_binary = y_train[y_train >= 0]
    
    fpr, tpr, thresholds = roc_curve(y_train_binary, y_pred_proba_train)
    optimal_idx = np.argmax(tpr - fpr)
    optimal_threshold = thresholds[optimal_idx]
    
    print(f"\nOptimal decision threshold: {optimal_threshold:.4f}")
    
    # Evaluate on test set
    y_pred_proba_test = lp_model.predict_proba(X_test)[:, 1]
    y_pred_lp = (y_pred_proba_test >= optimal_threshold).astype(int)
    
    lp_metrics = evaluate_model(y_test, y_pred_lp, y_pred_proba_test, "Labeled Propagation")
    results.append(lp_metrics)
    
    # Save Labeled Propagation model
    lp_model_path = Path(__file__).parent.parent / "data" / "labeled_propagation_ensemble_model.joblib"
    lp_model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({
        "model": lp_model,
        "scaler": scaler,
        "encoders": encoders,
        "optimal_threshold": optimal_threshold,
        "metrics": lp_metrics,
        "timestamp": datetime.now().isoformat()
    }, lp_model_path)
    print(f"\nLabeled Propagation model saved to {lp_model_path}")
    
    # ========== SUMMARY ==========
    print("\n" + "="*70)
    print("FINAL COMPARISON")
    print("="*70)
    
    summary_df = pd.DataFrame(results)
    print("\n" + summary_df.to_string(index=False))
    
    # Highlight best scores
    print("\n" + "-"*70)
    print("BEST PERFORMING MODEL FOR EACH METRIC:")
    print("-"*70)
    for metric in ["accuracy", "precision", "recall", "f1", "roc_auc", "specificity"]:
        best_idx = summary_df[metric].idxmax()
        best_model = summary_df.loc[best_idx, "model"]
        best_score = summary_df.loc[best_idx, metric]
        print(f"  {metric:15} -> {best_model:30} ({best_score:.4f})")
    
    # Recommendation
    print("\n" + "="*70)
    print("RECOMMENDATION")
    print("="*70)
    lp_f1 = lp_metrics["f1"]
    iso_f1 = iso_metrics["f1"]
    
    if lp_f1 > iso_f1:
        winner = "Labeled Propagation"
        margin = (lp_f1 - iso_f1) / iso_f1 * 100
        print(f"\n✓ Use Labeled Propagation (F1: {lp_f1:.4f} vs {iso_f1:.4f})")
        print(f"  Improvement: {margin:.1f}% better F1 score")
    else:
        winner = "IsolationForest"
        margin = (iso_f1 - lp_f1) / lp_f1 * 100
        print(f"\n✓ Use IsolationForest (F1: {iso_f1:.4f} vs {lp_f1:.4f})")
        print(f"  Improvement: {margin:.1f}% better F1 score")


if __name__ == "__main__":
    main()
