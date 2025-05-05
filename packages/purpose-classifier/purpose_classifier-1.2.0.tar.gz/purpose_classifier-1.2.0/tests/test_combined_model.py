#!/usr/bin/env python3
"""
Test script for the combined LightGBM purpose code classifier model
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
import argparse
import json
from tabulate import tabulate

# Add parent directory to path to import from purpose_classifier
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Test the combined purpose code classifier model')

    parser.add_argument('--model', type=str, default='models/combined_model.pkl',
                        help='Path to the trained model')

    parser.add_argument('--purpose-codes', type=str, default='data/purpose_codes.json',
                        help='Path to the purpose codes JSON file')

    parser.add_argument('--narrations', type=str, nargs='+',
                        help='Narrations to test (if not provided, will use sample narrations)')

    parser.add_argument('--file', type=str,
                        help='CSV file with narrations to test (should have a "narration" column)')

    parser.add_argument('--output', type=str,
                        help='Path to save results as CSV')

    parser.add_argument('--compare', type=str,
                        help='CSV file with ground truth to compare against (should have "narration" and "purpose_code" columns)')

    return parser.parse_args()

def load_purpose_codes(purpose_codes_path):
    """Load purpose codes and their descriptions"""
    try:
        with open(purpose_codes_path, 'r') as f:
            purpose_codes = json.load(f)
        return purpose_codes
    except Exception as e:
        print(f"Error loading purpose codes: {str(e)}")
        return {}

def get_code_description(code, purpose_codes):
    """Get description for a purpose code"""
    if code in purpose_codes:
        # Handle both simple string format and complex object format
        if isinstance(purpose_codes[code], str):
            return purpose_codes[code]
        elif isinstance(purpose_codes[code], dict):
            if 'name' in purpose_codes[code]:
                return purpose_codes[code]['name']
            elif 'description' in purpose_codes[code]:
                return purpose_codes[code]['description']
    return "Unknown"

def main():
    """Main function to test the model"""
    # Parse arguments
    args = parse_args()

    # Model path
    model_path = args.model

    # Check if model exists
    if not os.path.exists(model_path):
        print(f"Model not found: {model_path}")
        return 1

    # Load purpose codes
    purpose_codes = load_purpose_codes(args.purpose_codes)

    # Initialize the classifier
    print(f"Initializing LightGBM Purpose Classifier with model: {model_path}")
    classifier = LightGBMPurposeClassifier(model_path=model_path)

    # Get narrations to test
    if args.file:
        # Load narrations from file
        if not os.path.exists(args.file):
            print(f"File not found: {args.file}")
            return 1

        print(f"Loading narrations from {args.file}")
        df = pd.read_csv(args.file)

        if 'narration' not in df.columns:
            print(f"File does not have a 'narration' column")
            return 1

        narrations = df['narration'].tolist()
        print(f"Loaded {len(narrations)} narrations")
    elif args.narrations:
        # Use provided narrations
        narrations = args.narrations
    else:
        # Use sample narrations
        narrations = [
            "Payment for consulting services",
            "Salary payment for April 2025",
            "Invoice for office supplies",
            "University tuition fee",
            "Dividend payment for Q1 2025",
            "Loan repayment",
            "Rent payment for office space",
            "Insurance premium payment",
            "Charitable donation to Red Cross",
            "Payment for software license",
            "Electricity bill payment",
            "Tax payment for income tax",
            "Medical expenses reimbursement",
            "Travel expenses for business trip",
            "Subscription fee for online service",
            "Pension payment",
            "Child support payment",
            "Legal fees for contract review",
            "Commission payment for sales",
            "Bonus payment for performance",
            "Maintenance fee for property",
            "Membership fee for club",
            "Royalty payment for intellectual property",
            "Deposit for apartment rental",
            "Withdrawal from savings account",
            "Transfer to investment account",
            "Purchase of government bonds",
            "Payment for construction services",
            "Refund for returned merchandise",
            "Settlement for insurance claim"
        ]

    # Load ground truth if provided
    ground_truth = {}
    if args.compare:
        if not os.path.exists(args.compare):
            print(f"Comparison file not found: {args.compare}")
            return 1

        print(f"Loading ground truth from {args.compare}")
        gt_df = pd.read_csv(args.compare)

        if 'narration' not in gt_df.columns or 'purpose_code' not in gt_df.columns:
            print(f"Comparison file must have 'narration' and 'purpose_code' columns")
            return 1

        ground_truth = dict(zip(gt_df['narration'], gt_df['purpose_code']))
        print(f"Loaded {len(ground_truth)} ground truth labels")

    # Test each narration
    print("\nTesting model with narrations:")
    print("-" * 100)

    results = []
    correct = 0
    total = 0

    # Use batch prediction for efficiency
    batch_results = classifier.batch_predict(narrations)

    for narration, result in zip(narrations, batch_results):
        # Check if ground truth is available
        gt_code = ground_truth.get(narration, None)
        is_correct = gt_code == result['purpose_code'] if gt_code else None

        if is_correct is not None:
            total += 1
            if is_correct:
                correct += 1

        # Get descriptions
        pred_desc = get_code_description(result['purpose_code'], purpose_codes)

        # Add to results
        results.append({
            'narration': narration,
            'predicted_code': result['purpose_code'],
            'predicted_description': pred_desc,
            'confidence': result['confidence'],
            'category_purpose_code': result.get('category_purpose_code', 'N/A'),
            'category_confidence': result.get('category_confidence', 0.0),
            'ground_truth': gt_code,
            'correct': is_correct
        })

        # Print result
        print(f"Narration: {narration}")
        print(f"Predicted Purpose Code: {result['purpose_code']} - {pred_desc}")
        print(f"Confidence: {result['confidence']:.4f}")

        if 'category_purpose_code' in result:
            cat_desc = get_code_description(result['category_purpose_code'], purpose_codes)
            print(f"Category Purpose Code: {result['category_purpose_code']} - {cat_desc}")
            print(f"Category Confidence: {result['category_confidence']:.4f}")

        if gt_code:
            gt_desc = get_code_description(gt_code, purpose_codes)
            print(f"Ground Truth: {gt_code} - {gt_desc}")
            print(f"Correct: {'✓' if is_correct else '✗'}")

        print("-" * 100)

    # Print summary
    if total > 0:
        accuracy = correct / total
        print(f"\nAccuracy on provided ground truth: {accuracy:.4f} ({correct}/{total})")

    # Save results if requested
    if args.output:
        print(f"Saving results to {args.output}")
        results_df = pd.DataFrame(results)
        results_df.to_csv(args.output, index=False)

    return 0

if __name__ == "__main__":
    sys.exit(main())
