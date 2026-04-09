"""
Train the 6-model RBA Ensemble from Book1.xlsx (or a CSV equivalent).

Usage:
    python scripts/train_rba_ensemble.py
    python scripts/train_rba_ensemble.py --file path/to/data.xlsx --label "Is Attack IP"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
from ml.rba_ensemble import RBAEnsembleDetector


def main() -> None:
    parser = argparse.ArgumentParser(description="Train 6-model RBA ensemble")
    parser.add_argument(
        "--file",
        default=str(ROOT / "data" / "Book1.xlsx"),
        help="Path to dataset (.xlsx or .csv)  [default: data/Book1.xlsx]",
    )
    parser.add_argument(
        "--label",
        default="Is Attack IP",
        help="Label column name  [default: 'Is Attack IP']",
    )
    args = parser.parse_args()

    data_path = Path(args.file)
    if not data_path.exists():
        print(f"✗ File not found: {data_path}")
        print("  Provide the path with --file <path>")
        sys.exit(1)

    print(f"Loading data from {data_path} ...")
    if data_path.suffix in (".xlsx", ".xls"):
        df = pd.read_excel(data_path)
    else:
        df = pd.read_csv(data_path)

    print(f"  Rows: {len(df):,}  |  Columns: {df.shape[1]}")
    if args.label not in df.columns:
        print(f"✗ Label column '{args.label}' not found.")
        print(f"  Available columns: {list(df.columns)}")
        sys.exit(1)

    print(f"  Attack rate: {df[args.label].astype(bool).mean():.2%}\n")

    det = RBAEnsembleDetector()
    metrics = det.train(df, label_column=args.label)

    ens = metrics["ensemble"]
    print(f"\n✓ Training complete!")
    print(f"  Ensemble ROC-AUC  : {ens['roc_auc']:.4f}")
    print(f"  Ensemble F1-Score : {ens['f1']:.4f}")
    print(f"  Ensemble Recall   : {ens['recall']:.4f}")
    print(f"  Ensemble Accuracy : {ens['accuracy']*100:.2f}%")
    print(f"\n  Saved to data/rba_ensemble_*.joblib")


if __name__ == "__main__":
    main()
