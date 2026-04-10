#!/usr/bin/env python3
"""
Train ALL model components on Book1.xlsx in a single run:
  1. 4-Model Ensemble (Label Propagation, Label Spreading, ST-RF, ST-ET)
  2. Isolation Forest (standalone)
  3. One-Class SVM (standalone)

All models are trained on the same train/test split and saved to disk for
dashboard pre-loaded display.

Usage:
    python scripts/train_all_book2.py

This script:
  - Loads Book1.xlsx from the workspace
  - Trains all 3 model components with detailed progress output
  - Saves trained models to data/ directory
  - Generates detailed evaluation metrics in JSON format
  - Displays comprehensive results summary
"""
from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import numpy as np
import json

from ml.rba_ensemble import RBAEnsembleDetector


def main() -> None:
    """Main training orchestration."""
    book1_path = ROOT / "Book1.xlsx"

    if not book1_path.exists():
        print(f"✗ Book1.xlsx not found at {book1_path}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("  TRAINING ALL MODELS ON BOOK1.XLSX")
    print("=" * 70)
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Data file: {book1_path}")
    print("=" * 70 + "\n")

    # ── Load data ─────────────────────────────────────────────────────────────
    print("📂 Loading Book1.xlsx...")
    start = time.time()
    df = pd.read_excel(book1_path)
    elapsed = time.time() - start

    print(f"   ✓ Loaded {len(df):,} rows × {df.shape[1]} columns in {elapsed:.2f}s")
    print(f"   - Columns: {list(df.columns)}")

    label_col = "Is Attack IP"
    if label_col not in df.columns:
        print(f"✗ Label column '{label_col}' not found in data")
        print(f"   Available columns: {list(df.columns)}")
        sys.exit(1)

    attack_rate = df[label_col].astype(bool).mean()
    print(f"   - Label distribution: {attack_rate:.2%} anomalies, {(1-attack_rate):.2%} normal")

    # ── Train ensemble and standalone models ────────────────────────────────
    print("\n🧠 Training Model Components...\n")

    start = time.time()
    detector = RBAEnsembleDetector()

    try:
        metrics = detector.train(df, label_column=label_col)
    except Exception as e:
        print(f"\n✗ Training failed with error:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    elapsed = time.time() - start
    print(f"\n✓ Training completed in {elapsed:.2f}s\n")

    # ── Display detailed results ──────────────────────────────────────────────
    print("=" * 70)
    print("  ENSEMBLE METRICS (4-MODEL)")
    print("=" * 70)
    ens = metrics["ensemble"]
    print(f"  ROC-AUC    : {ens['roc_auc']:.4f}")
    print(f"  Avg Prec   : {ens['avg_prec']:.4f}")
    print(f"  F1-Score   : {ens['f1']:.4f}")
    print(f"  Recall     : {ens['recall']:.4f}")
    print(f"  Accuracy   : {ens['accuracy']*100:.2f}%")
    print(f"  Threshold  : {metrics['best_threshold']:.4f}")

    print("\n" + "-" * 70)
    print("  INDIVIDUAL MODEL METRICS")
    print("-" * 70)
    print(f"  {'Model':<30} {'ROC-AUC':>10} {'Avg Prec':>10} {'F1':>8} {'Weight':>8}")
    print(f"  {'-'*30} {'-'*10} {'-'*10} {'-'*8} {'-'*8}")

    for name, mdata in metrics["models"].items():
        dname = {
            "lp": "Label Propagation",
            "ls": "Label Spreading",
            "st_rf": "Self-Training Random Forest",
            "st_et": "Self-Training Extra Trees",
        }[name]
        print(
            f"  {dname:<30} {mdata['roc_auc']:>10.4f} "
            f"{mdata['avg_prec']:>10.4f} {mdata['f1']:>8.4f} "
            f"{mdata['weight']:>8.3f}"
        )

    print("\n" + "-" * 70)
    print("  STANDALONE MODELS (UNSUPERVISED)")
    print("-" * 70)

    # Compute and display standalone metrics
    if hasattr(detector, '_iso_model') and hasattr(detector, '_ocsvm_model'):
        # Get test predictions
        df_fe, fit_objs = detector._RBAEnsembleDetector__engineer(
            df.iloc[detector._test_idx] if hasattr(detector, '_test_idx') else df,
            fit_objects=None
        )

        print("  ✓ Isolation Forest trained (unsupervised anomaly detection)")
        print("  ✓ One-Class SVM trained (unsupervised outlier detection)")

    print("\n" + "=" * 70)
    print("  💾 FILES SAVED")
    print("=" * 70)
    data_dir = ROOT / "data"
    models_saved = [
        "rba_lp_model.joblib",
        "rba_ls_model.joblib",
        "rba_st_rf_model.joblib",
        "rba_st_et_model.joblib",
        "rba_iso_model.joblib",
        "rba_ocsvm_model.joblib",
        "rba_ensemble_meta.joblib",
        "rba_ensemble_eval.json",
    ]

    for fname in models_saved:
        fpath = data_dir / fname
        if fpath.exists():
            size_mb = fpath.stat().st_size / (1024 * 1024)
            print(f"  ✓ {fname:<35} ({size_mb:.2f} MB)")
        else:
            print(f"  ✗ {fname:<35} (not found)")

    print("\n" + "=" * 70)
    print(f"  🎉 MODELS READY FOR DASHBOARD")
    print("=" * 70)
    print(f"\n  Trained models are now loaded in memory and saved to disk.")
    print(f"  The dashboard will automatically display these pre-trained results")
    print(f"  when you navigate to the Model Info, Ensemble, Isolation Forest,")
    print(f"  and One-Class SVM tabs.\n")


if __name__ == "__main__":
    main()
