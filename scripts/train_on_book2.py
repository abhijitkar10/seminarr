#!/usr/bin/env python3

"""
Train Labeled Propagation model on Book2.xlsx (49,999 authentication logs)
"""
import sys
from pathlib import Path
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ml.labeled_propagation_model import LabeledPropagationDetector


def main():
    """Train and evaluate model on Book2.xlsx"""
    
    # Load Book2.xlsx data
    data_path = Path(__file__).parent.parent / "Book2.xlsx"
    if not data_path.exists():
        print(f"❌ Error: {data_path} not found")
        return False
    
    print(f"📊 Loading training data from {data_path}...")
    df = pd.read_excel(data_path)
    print(f"✓ Loaded {len(df):,} rows with {len(df.columns)} columns")
    
    # Check for label column
    if "Is Attack IP" not in df.columns:
        print("❌ Error: 'Is Attack IP' column not found in data")
        return False
    
    print(f"✓ Label distribution: {df['Is Attack IP'].value_counts().to_dict()}")
    print(f"✓ Anomaly rate: {df['Is Attack IP'].mean():.2%}")
    
    # Train model
    print("\n" + "="*60)
    print("TRAINING MODEL")
    print("="*60)
    
    detector = LabeledPropagationDetector()
    metrics = detector.train(df, label_column="Is Attack IP", test_size=0.2)
    
    # Save model
    print("\n💾 Saving model...")
    detector.save()
    
    # Print summary
    print("\n" + "="*60)
    print("TRAINING SUMMARY")
    print("="*60)
    print(f"Dataset:        Book1.xlsx ({len(df):,} rows)")
    print(f"Test Set Size:  {metrics['tp'] + metrics['fp'] + metrics['fn'] + metrics['tn']} samples")
    print(f"Recall:         {metrics['recall']:.2%}")
    print(f"F1 Score:       {metrics['f1']:.4f}")
    print(f"ROC-AUC:        {metrics['roc_auc']:.4f}")
    print(f"Precision:      {metrics['precision']:.2%}")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
