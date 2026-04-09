#!/usr/bin/env python3
"""
Comparison script: Labeled Propagation vs IsolationForest
Evaluates both models on the same test set from Book1.xlsx
"""
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
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
            # Handle unseen categories by mapping them to a default value
            categories_str = features_df[cat_feature].astype(str)
            known_classes = set(encoders[cat_feature].classes_)
            
            # Replace unseen categories with the most common one (first in classes)
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

    if scaler is not None and not is_fit:
        X_array = scaler.transform(X_array)
    elif scaler is not None and is_fit:
        X_array = scaler.fit_transform(X_array)

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
    print(classification_report(y_true, y_pred, target_names=["Normal", "Anomaly"]))
    
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
    """Compare both models"""
    print("\n" + "="*70)
    print("MODEL COMPARISON: Labeled Propagation vs IsolationForest")
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
    
    print(f"\nLabel distribution: {np.sum(y)} anomalies, {len(y) - np.sum(y)} normal")
    
    # Create train/test split
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        df, y, test_size=0.2, random_state=42, stratify=y
    )
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=0.2, random_state=42, stratify=y_train_val
    )
    
    print(f"\nTrain: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    
    # Prepare features
    print("\nPreparing features...")
    X_train_scaled, features, scaler, encoders = prepare_features(
        X_train, scaler=StandardScaler(), encoders={}, is_fit=True
    )
    X_test_scaled, _, _, _ = prepare_features(
        X_test, scaler=scaler, encoders=encoders, is_fit=False
    )
    X_val_scaled, _, _, _ = prepare_features(
        X_val, scaler=scaler, encoders=encoders, is_fit=False
    )
    
    results = []
    
    # ========== ISOLATION FOREST ==========
    print("\n" + "-"*70)
    print("Training IsolationForest...")
    print("-"*70)
    
    iso_forest = IsolationForest(contamination=0.08, random_state=42)
    iso_forest.fit(X_train_scaled)
    
    y_pred_iso = iso_forest.predict(X_test_scaled)
    y_pred_iso = (y_pred_iso == -1).astype(int)  # -1 is anomaly, 1 is normal
    
    # Use decision function for probability
    y_pred_proba_iso = -iso_forest.score_samples(X_test_scaled)
    y_pred_proba_iso = (y_pred_proba_iso - y_pred_proba_iso.min()) / (y_pred_proba_iso.max() - y_pred_proba_iso.min())
    
    iso_metrics = evaluate_model(y_test, y_pred_iso, y_pred_proba_iso, "IsolationForest")
    results.append(iso_metrics)
    
    # ========== LABELED PROPAGATION ==========
    print("\n" + "-"*70)
    print("Loading Labeled Propagation model...")
    print("-"*70)
    
    try:
        from ml.labeled_propagation_model import LabeledPropagationDetector, LP_MODEL_PATH
        
        if not LP_MODEL_PATH.exists():
            print("ERROR: Labeled Propagation model not found. Train it first.")
            sys.exit(1)
        
        lp_detector = LabeledPropagationDetector()
        
        y_pred_lp, y_pred_proba_lp = lp_detector.predict(X_test_scaled)
        
        lp_metrics = evaluate_model(y_test, y_pred_lp, y_pred_proba_lp, "Labeled Propagation")
        results.append(lp_metrics)
        
    except Exception as e:
        print(f"ERROR loading Labeled Propagation model: {e}")
    
    # ========== SUMMARY ==========
    print("\n" + "="*70)
    print("SUMMARY COMPARISON")
    print("="*70)
    
    summary_df = pd.DataFrame(results)
    print(summary_df.to_string(index=False))
    
    # Highlight best scores
    print("\n" + "-"*70)
    print("BEST SCORES:")
    print("-"*70)
    for metric in ["accuracy", "precision", "recall", "f1", "roc_auc", "specificity"]:
        best_idx = summary_df[metric].idxmax()
        best_model = summary_df.loc[best_idx, "model"]
        best_score = summary_df.loc[best_idx, metric]
        print(f"  {metric:15} -> {best_model:30} ({best_score:.4f})")


if __name__ == "__main__":
    main()
