#!/usr/bin/env python3
"""
Training script for Labeled Propagation model on Book1.xlsx data
Trains model with train/test split and comprehensive evaluation
"""
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ml.labeled_propagation_model import LabeledPropagationDetector


def main():
    """Main training function"""
    print("\n" + "="*70)
    print("LABELED PROPAGATION MODEL TRAINING")
    print("="*70)
    
    # Load data
    excel_file = Path(__file__).parent.parent / "Book1.xlsx"
    print(f"\nLoading data from {excel_file}...")
    
    if not excel_file.exists():
        print(f"ERROR: File not found at {excel_file}")
        sys.exit(1)
    
    df = pd.read_excel(excel_file)
    print(f"Loaded {len(df)} rows with {len(df.columns)} columns")
    
    # Check for required label column
    label_column = "Is Attack IP"
    if label_column not in df.columns:
        print(f"ERROR: '{label_column}' column not found in data")
        print(f"Available columns: {df.columns.tolist()}")
        sys.exit(1)
    
    # Show label distribution
    print("\nLabel Distribution:")
    print(df[label_column].value_counts())
    print(f"Anomaly Rate: {df[label_column].mean():.2%}")
    
    # Initialize and train detector
    detector = LabeledPropagationDetector()
    metrics = detector.train(df, label_column=label_column)
    
    # Save model
    detector.save()
    
    print("\n" + "="*70)
    print("MODEL TRAINING COMPLETE")
    print("="*70)
    
    return detector, metrics


if __name__ == "__main__":
    detector, metrics = main()
