#!/usr/bin/env python
"""
Test the purpose code classifier with problematic purpose codes.

This script tests the purpose code classifier with problematic purpose codes
such as VATX, WHLD, TREA, CORT, CCRD, DCRD, ICCP, IDCP, INTE, etc.
"""

import os
import sys
import json
import argparse
import pandas as pd
from pathlib import Path

# Add the parent directory to the path so we can import the purpose_classifier package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier

def load_purpose_codes(filepath):
    """Load purpose codes from JSON file"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            # Check if the data is a dictionary
            if isinstance(data, dict):
                return data
            else:
                print(f"Data in {filepath} is not a dictionary")
                return {}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Failed to load purpose codes from {filepath}: {str(e)}")
        return {}

def get_purpose_description(purpose_code, purpose_codes):
    """Get purpose code description"""
    if isinstance(purpose_codes, dict):
        return purpose_codes.get(purpose_code, 'Unknown')
    return 'Unknown'

def get_category_purpose_description(category_purpose_code, category_purpose_codes):
    """Get category purpose code description"""
    if isinstance(category_purpose_codes, dict):
        return category_purpose_codes.get(category_purpose_code, 'Unknown')
    return 'Unknown'

def test_problematic_purpose_codes(classifier, purpose_codes=None, category_purpose_codes=None):
    """Test the classifier with problematic purpose codes"""
    # Define problematic purpose codes
    problematic_codes = [
        'VATX', 'WHLD', 'TREA', 'CORT', 'CCRD', 'DCRD', 'ICCP', 'IDCP', 'INTE', 'CBLK', 'GOVI', 'DIVI', 'GOVT', 'GBEN'
    ]

    # Define test narrations for each purpose code
    test_narrations = {
        'VATX': [
            "VALUE ADDED TAX PAYMENT FOR Q1 2025",
            "VAT PAYMENT FOR Q2 2025",
            "PAYMENT OF VALUE ADDED TAX FOR 2025",
            "VAT REMITTANCE FOR JANUARY 2025",
            "QUARTERLY VAT PAYMENT - Q3 2025"
        ],
        'WHLD': [
            "WITHHOLDING TAX PAYMENT FOR Q1 2025",
            "WITHHELD TAX PAYMENT FOR Q2 2025",
            "PAYMENT OF WITHHOLDING TAX FOR 2025",
            "WITHHOLDING TAX REMITTANCE FOR JANUARY 2025",
            "QUARTERLY WITHHOLDING TAX PAYMENT - Q3 2025"
        ],
        'TREA': [
            "TREASURY PAYMENT FOR BOND PURCHASE",
            "TREASURY TRANSFER FOR SECURITIES",
            "TREASURY SETTLEMENT FOR LIQUIDITY MANAGEMENT",
            "TREASURY TRANSACTION FOR CASH MANAGEMENT",
            "TREASURY MANAGEMENT PAYMENT FOR TREASURY MANAGEMENT"
        ],
        'CORT': [
            "TRADE SETTLEMENT PAYMENT FOR SECURITIES",
            "SETTLEMENT OF TRADE FOR EXPORT",
            "SETTLEMENT FOR TRADE FOR IMPORT",
            "SETTLEMENT OF TRANSACTION FOR GOODS",
            "SETTLEMENT FOR TRANSACTION FOR SERVICES"
        ],
        'CCRD': [
            "CREDIT CARD PAYMENT FOR MONTHLY BILL",
            "CREDIT CARD BILL PAYMENT FOR RETAIL PURCHASE",
            "PAYMENT FOR CREDIT CARD BILL FOR APRIL 2025",
            "CREDIT CARD PAYMENT - ACCOUNT 12345",
            "CREDIT CARD BILL - ACCOUNT 67890"
        ],
        'DCRD': [
            "DEBIT CARD PAYMENT FOR ONLINE PURCHASE",
            "DEBIT CARD BILL PAYMENT FOR RETAIL PURCHASE",
            "PAYMENT FOR DEBIT CARD BILL FOR APRIL 2025",
            "DEBIT CARD PAYMENT - ACCOUNT 12345",
            "DEBIT CARD BILL - ACCOUNT 67890"
        ],
        'ICCP': [
            "IRREVOCABLE CREDIT CARD PAYMENT FOR MONTHLY BILL",
            "IRREVOCABLE CREDIT CARD BILL PAYMENT FOR RETAIL PURCHASE",
            "PAYMENT FOR IRREVOCABLE CREDIT CARD BILL FOR APRIL 2025",
            "IRREVOCABLE CREDIT CARD PAYMENT - ACCOUNT 12345",
            "IRREVOCABLE CREDIT CARD BILL - ACCOUNT 67890"
        ],
        'IDCP': [
            "IRREVOCABLE DEBIT CARD PAYMENT FOR ONLINE PURCHASE",
            "IRREVOCABLE DEBIT CARD BILL PAYMENT FOR RETAIL PURCHASE",
            "PAYMENT FOR IRREVOCABLE DEBIT CARD BILL FOR APRIL 2025",
            "IRREVOCABLE DEBIT CARD PAYMENT - ACCOUNT 12345",
            "IRREVOCABLE DEBIT CARD BILL - ACCOUNT 67890"
        ],
        'INTE': [
            "INTEREST PAYMENT FOR LOAN",
            "INTEREST PAYMENT ON DEPOSIT",
            "PAYMENT OF INTEREST FOR Q1 2025",
            "INTEREST PAYMENT - ACCOUNT 12345",
            "INTEREST PAYMENT FOR APRIL 2025"
        ],
        'CBLK': [
            "CARD BULK CLEARING FOR MONTHLY BILL",
            "CARD BULK SETTLEMENT FOR RETAIL PURCHASE",
            "CARD BULK PROCESSING FOR APRIL 2025",
            "CARD BULK RECONCILIATION FOR ACCOUNT 12345",
            "CARD BULK PAYMENT FOR ACCOUNT 67890"
        ],
        'GOVI': [
            "GOVERNMENT INSURANCE PAYMENT FOR HEALTH",
            "GOVERNMENT INSURANCE PREMIUM FOR LIFE",
            "PAYMENT FOR GOVERNMENT INSURANCE FOR APRIL 2025",
            "GOVERNMENT INSURANCE PAYMENT - ACCOUNT 12345",
            "GOVERNMENT INSURANCE PREMIUM - ACCOUNT 67890"
        ],
        'DIVI': [
            "DIVIDEND PAYMENT FOR Q1 2025",
            "DIVIDEND DISTRIBUTION FOR Q2 2025",
            "PAYMENT OF DIVIDEND FOR 2025",
            "DIVIDEND PAYMENT - ACCOUNT 12345",
            "DIVIDEND PAYMENT FOR APRIL 2025"
        ],
        'GOVT': [
            "GOVERNMENT PAYMENT FOR HEALTH",
            "PAYMENT FROM GOVERNMENT FOR APRIL 2025",
            "GOVERNMENT PAYMENT - ACCOUNT 12345",
            "GOVERNMENT PAYMENT FOR SERVICES",
            "GOVERNMENT PAYMENT FOR INFRASTRUCTURE"
        ],
        'GBEN': [
            "GOVERNMENT BENEFIT PAYMENT FOR LIFE",
            "GOVERNMENT BENEFIT - ACCOUNT 67890",
            "SOCIAL SECURITY BENEFIT PAYMENT",
            "UNEMPLOYMENT BENEFIT PAYMENT",
            "GOVERNMENT WELFARE PAYMENT"
        ]
    }

    # Test each purpose code
    results = {}
    for purpose_code in problematic_codes:
        print(f"\nTesting purpose code: {purpose_code}")
        purpose_description = get_purpose_description(purpose_code, purpose_codes) if purpose_codes else 'Unknown'
        print(f"Purpose Code Description: {purpose_description}")

        narrations = test_narrations.get(purpose_code, [])
        if not narrations:
            print(f"No test narrations found for purpose code: {purpose_code}")
            continue

        correct_predictions = 0
        correct_category_predictions = 0
        total_predictions = len(narrations)

        for narration in narrations:
            print(f"\nTesting narration: \"{narration}\"")
            result = classifier.predict(narration)

            predicted_purpose_code = result['purpose_code']
            confidence = result['confidence']
            category_purpose_code = result['category_purpose_code']
            category_confidence = result['category_confidence']

            predicted_purpose_description = get_purpose_description(predicted_purpose_code, purpose_codes) if purpose_codes else 'Unknown'
            category_purpose_description = get_category_purpose_description(category_purpose_code, category_purpose_codes) if category_purpose_codes else 'Unknown'

            print(f"Predicted Purpose Code: {predicted_purpose_code} - {predicted_purpose_description}")
            print(f"Confidence: {confidence:.4f}")
            print(f"Category Purpose Code: {category_purpose_code} - {category_purpose_description}")
            print(f"Category Confidence: {category_confidence:.4f}")

            if predicted_purpose_code == purpose_code:
                correct_predictions += 1
                print("Result: PASS - Matched expected purpose code")
            else:
                print("Result: FAIL - Did not match expected purpose code")
                print(f"Expected: {purpose_code}, Got: {predicted_purpose_code}")

            if category_purpose_code == purpose_code:
                correct_category_predictions += 1
                print("Result: PASS - Matched expected category purpose code")
            else:
                print("Result: FAIL - Did not match expected category purpose code")
                print(f"Expected: {purpose_code}, Got: {category_purpose_code}")

        # Calculate accuracy
        purpose_accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
        category_accuracy = (correct_category_predictions / total_predictions * 100) if total_predictions > 0 else 0

        print(f"\nPurpose Code Accuracy for {purpose_code}: {correct_predictions}/{total_predictions} ({purpose_accuracy:.2f}%)")
        print(f"Category Purpose Code Accuracy for {purpose_code}: {correct_category_predictions}/{total_predictions} ({category_accuracy:.2f}%)")

        results[purpose_code] = {
            'purpose_accuracy': purpose_accuracy,
            'category_accuracy': category_accuracy,
            'correct_predictions': correct_predictions,
            'correct_category_predictions': correct_category_predictions,
            'total_predictions': total_predictions
        }

    # Calculate overall accuracy
    total_correct_predictions = sum(result['correct_predictions'] for result in results.values())
    total_correct_category_predictions = sum(result['correct_category_predictions'] for result in results.values())
    total_predictions = sum(result['total_predictions'] for result in results.values())

    overall_purpose_accuracy = (total_correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
    overall_category_accuracy = (total_correct_category_predictions / total_predictions * 100) if total_predictions > 0 else 0

    print("\n" + "-" * 75)
    print("\nOverall Results:")
    print(f"Total Predictions: {total_predictions}")
    print(f"Purpose Code Accuracy: {total_correct_predictions}/{total_predictions} ({overall_purpose_accuracy:.2f}%)")
    print(f"Category Purpose Code Accuracy: {total_correct_category_predictions}/{total_predictions} ({overall_category_accuracy:.2f}%)")

    return results

def main():
    parser = argparse.ArgumentParser(description='Test the purpose code classifier with problematic purpose codes')
    parser.add_argument('--model', type=str, default='models/combined_model.pkl', help='Path to the model file')

    args = parser.parse_args()

    # Load purpose codes and category purpose codes
    try:
        purpose_codes_path = 'data/purpose_codes.json'
        category_purpose_codes_path = 'data/category_purpose_codes.json'

        print(f"Loading purpose codes from {purpose_codes_path}")
        purpose_codes = load_purpose_codes(purpose_codes_path)

        print(f"Loading category purpose codes from {category_purpose_codes_path}")
        category_purpose_codes = load_purpose_codes(category_purpose_codes_path)

        if not isinstance(purpose_codes, dict):
            print(f"Warning: purpose_codes is not a dictionary, it's a {type(purpose_codes)}")
            purpose_codes = {}

        if not isinstance(category_purpose_codes, dict):
            print(f"Warning: category_purpose_codes is not a dictionary, it's a {type(category_purpose_codes)}")
            category_purpose_codes = {}
    except Exception as e:
        print(f"Error loading purpose codes: {str(e)}")
        purpose_codes = {}
        category_purpose_codes = {}

    # Initialize classifier
    print(f"Loading model from {args.model}")
    classifier = LightGBMPurposeClassifier(model_path=args.model)

    # Test problematic purpose codes
    test_problematic_purpose_codes(classifier, purpose_codes, category_purpose_codes)

if __name__ == '__main__':
    main()
