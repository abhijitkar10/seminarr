"""
Train the 4-model RBA Ensemble from Book1.xlsx

Usage:
    python scripts/train_ensemble_book1.py
    python scripts/train_ensemble_book1.py --file path/to/data.xlsx --label "Is Attack IP"
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
    parser = argparse.ArgumentParser(description="Train 4-model RBA ensemble on Book1")
    parser.add_argument(
        "--file",
        default=str(ROOT / "Book1.xlsx"),
        help="Path to dataset (.xlsx or .csv)  [default: Book1.xlsx in project root]",
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

    print(f"📊 Loading data from {data_path} ...")
    if data_path.suffix in (".xlsx", ".xls"):
        df = pd.read_excel(data_path)
    else:
        df = pd.read_csv(data_path)

    print(f"  ✓ Rows: {len(df):,}  |  Columns: {df.shape[1]}")
    if args.label not in df.columns:
        print(f"✗ Label column '{args.label}' not found.")
        print(f"  Available columns: {list(df.columns)}")
        sys.exit(1)

    print(f"\n🚀 Training 4-model ensemble on {len(df):,} samples...")
    print(f"   Label column: '{args.label}'")
    
    detector = RBAEnsembleDetector()
    try:
        metrics = detector.train(df, label_column=args.label)
        
        print(f"\n✅ TRAINING COMPLETE!\n")
        print("=" * 70)
        print(f"{'MODEL':<20} {'ROC-AUC':<15} {'F1-Score':<15} {'Recall':<15}")
        print("=" * 70)
        
        for model_name in ["lp", "ls", "st_rf", "st_et"]:
            if model_name in metrics:
                m = metrics[model_name]
                print(f"{model_name:<20} {m.get('roc_auc', 0):<15.4f} {m.get('f1', 0):<15.4f} {m.get('recall', 0):<15.4f}")
        
        print("=" * 70)
        if "ensemble" in metrics:
            ens = metrics["ensemble"]
            print(f"\n🧩 ENSEMBLE METRICS:")
            print(f"   ROC-AUC: {ens.get('roc_auc', 0):.4f}")
            print(f"   F1-Score: {ens.get('f1', 0):.4f}")
            print(f"   Recall: {ens.get('recall', 0):.4f}")
            print(f"   Precision: {ens.get('precision', 0):.4f}")
            print(f"   Accuracy: {ens.get('accuracy', 0):.4f}")
        
        print(f"\n💾 Models saved to: {ROOT / 'data'}")
        print(f"   - rba_lp_model.joblib")
        print(f"   - rba_ls_model.joblib")
        print(f"   - rba_st_rf_model.joblib")
        print(f"   - rba_st_et_model.joblib")
        print(f"   - rba_ensemble_meta.joblib")
        print(f"   - rba_ensemble_eval.json")
        
    except Exception as e:
        print(f"\n✗ Training failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
