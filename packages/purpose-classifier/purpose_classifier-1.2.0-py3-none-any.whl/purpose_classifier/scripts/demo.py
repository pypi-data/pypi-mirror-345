#!/usr/bin/env python3
"""
Demonstration script for the Purpose Classifier package.
Shows how to use the predict.py functionality for classifying financial transactions.
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Import from predict.py
from purpose_classifier.scripts.predict import (
    setup_classifier,
    predict_purpose_code,
    format_prediction_result,
    load_purpose_codes
)
from purpose_classifier.config.path_helper import get_data_file_path, get_model_file_path
from purpose_classifier.config.settings import setup_logging, get_environment

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Demonstrate the Purpose Classifier package')

    parser.add_argument('--text', type=str, default=None,
                        help='Direct text input for prediction')

    parser.add_argument('--verbose', action='store_true',
                        help='Show verbose output')

    return parser.parse_args()

def main():
    """Main function to demonstrate the purpose classifier"""
    # Parse arguments
    args = parse_arguments()

    # Setup logging
    logger = setup_logging(get_environment())

    # Setup classifier
    print("Initializing LightGBM Purpose Classifier...")
    classifier = setup_classifier()

    if not classifier:
        print("Error: Failed to initialize classifier")
        return 1

    print("Model loaded successfully!")

    # Load purpose codes and category purpose codes
    purpose_codes, category_purpose_codes = load_purpose_codes()

    # Check if purpose codes and category purpose codes are loaded correctly
    print("\nChecking purpose codes and category purpose codes...")
    print(f"Purpose codes loaded: {len(classifier.purpose_codes)} codes")
    print(f"Category purpose codes loaded: {len(classifier.category_purpose_codes)} codes")

    # Sample narrations to test or use the one provided by the user
    if args.text:
        samples = [args.text]
    else:
        samples = [
            "TUITION PAYMENT FOR UNIVERSITY OF CALIFORNIA",
            "MONTHLY RENT PAYMENT FOR APARTMENT 301",
            "PAYMENT FOR SOFTWARE LICENSE RENEWAL",
            "CREDIT CARD PAYMENT - VISA ENDING 1234",
            "INTERBANK TRANSFER TO NOSTRO ACCOUNT",
            "PAYMENT FOR GOODS - INVOICE #12345",
            "INSURANCE PREMIUM FOR AUTO POLICY",
            "SALARY PAYMENT FOR MARCH 2025",
            "UTILITY BILL PAYMENT - ELECTRICITY",
            "FOREIGN EXCHANGE TRANSACTION USD/EUR"
        ]

    # Test each sample
    print("\nTesting sample narrations:")
    print("-" * 80)

    for i, sample in enumerate(samples, 1):
        print(f"\nSample {i}: {sample}")

        # Get prediction using predict.py functionality
        result = predict_purpose_code(classifier, sample, args.verbose)

        # Display results
        if args.verbose:
            # Detailed output is already shown by predict_purpose_code when verbose=True
            pass
        else:
            # Display a simplified version of the results
            print(f"Purpose Code: {result.get('purpose_code', 'N/A')}")
            print(f"Description: {purpose_codes.get(result.get('purpose_code', ''), 'N/A')}")
            print(f"Confidence: {result.get('confidence', 0):.4f}")

            if 'category_purpose_code' in result:
                print(f"Category Purpose Code: {result.get('category_purpose_code', 'N/A')}")
                print(f"Category Description: {category_purpose_codes.get(result.get('category_purpose_code', ''), 'N/A')}")
                print(f"Category Confidence: {result.get('category_confidence', 0):.4f}")

            # Show domain enhancement if applied
            if result.get('enhanced', False) or result.get('enhancement_applied'):
                print(f"Enhanced: YES - {result.get('enhancement_applied', 'Unknown')}")
                if 'original_purpose_code' in result:
                    print(f"Original Purpose Code: {result.get('original_purpose_code')}")
            else:
                print("Enhanced: NO")

            # Show enhancer decisions if available
            if 'enhancer_decisions' in result and result['enhancer_decisions']:
                print("\nEnhancer Decisions:")
                for decision in result['enhancer_decisions']:
                    applied = "✓" if decision.get('applied', False) else "✗"
                    print(f"  {applied} {decision.get('enhancer', 'Unknown')}: {decision.get('old_code', 'Unknown')} -> {decision.get('new_code', 'Unknown')} (conf: {decision.get('confidence', 0.0):.2f})")
                    if 'reason' in decision:
                        print(f"     Reason: {decision.get('reason')}")

            # Show top predictions if available
            if 'top_predictions' in result:
                print("\nTop Predictions:")
                for code, prob in result.get('top_predictions', []):
                    print(f"  {code}: {prob:.4f}")

        print("-" * 80)

    return 0

if __name__ == "__main__":
    sys.exit(main())
