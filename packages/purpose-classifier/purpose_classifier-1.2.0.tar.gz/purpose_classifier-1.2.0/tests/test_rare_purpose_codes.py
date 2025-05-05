#!/usr/bin/env python
"""
Test script for rare and challenging purpose codes.

This script tests the classifier with rare and challenging purpose codes
that are often misclassified, focusing on edge cases and ambiguous narrations.
"""

import os
import sys
import logging
import pandas as pd
import warnings
from tabulate import tabulate

# Suppress scikit-learn warnings about feature names
warnings.filterwarnings("ignore", category=UserWarning,
                       message="X does not have valid feature names, but LGBMClassifier was fitted with feature names")

# Add the parent directory to the path so we can import the purpose_classifier package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the classifier
from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define rare and challenging purpose code test cases
RARE_PURPOSE_CODE_TESTS = [
    # VATX (Value Added Tax) - Often confused with TAXS
    {"narration": "VAT PAYMENT FOR Q1 2023", "message_type": "MT103", "expected_purpose": "VATX", "expected_category": "TAXS"},
    {"narration": "VALUE ADDED TAX REMITTANCE", "message_type": "MT103", "expected_purpose": "VATX", "expected_category": "TAXS"},
    {"narration": "QUARTERLY VAT SETTLEMENT", "message_type": "MT103", "expected_purpose": "VATX", "expected_category": "TAXS"},
    {"narration": "VAT PAYMENT TO TAX AUTHORITY", "message_type": "MT103", "expected_purpose": "VATX", "expected_category": "TAXS"},
    {"narration": "PAYMENT OF VALUE ADDED TAX", "message_type": "MT103", "expected_purpose": "VATX", "expected_category": "TAXS"},

    # WHLD (Withholding) - Often confused with TAXS
    {"narration": "WITHHOLDING TAX PAYMENT", "message_type": "MT103", "expected_purpose": "WHLD", "expected_category": "WHLD"},
    {"narration": "TAX WITHHOLDING REMITTANCE", "message_type": "MT103", "expected_purpose": "WHLD", "expected_category": "WHLD"},
    {"narration": "WITHHOLDING ON DIVIDEND PAYMENT", "message_type": "MT103", "expected_purpose": "WHLD", "expected_category": "WHLD"},
    {"narration": "STATUTORY WITHHOLDING PAYMENT", "message_type": "MT103", "expected_purpose": "WHLD", "expected_category": "WHLD"},
    {"narration": "WITHHOLDING ON CONTRACTOR PAYMENT", "message_type": "MT103", "expected_purpose": "WHLD", "expected_category": "WHLD"},

    # TREA (Treasury Payment) - Often confused with INTC
    {"narration": "TREASURY OPERATION", "message_type": "MT202", "expected_purpose": "TREA", "expected_category": "TREA"},
    {"narration": "TREASURY MANAGEMENT TRANSFER", "message_type": "MT202", "expected_purpose": "TREA", "expected_category": "TREA"},
    {"narration": "TREASURY SERVICES PAYMENT", "message_type": "MT202", "expected_purpose": "TREA", "expected_category": "TREA"},
    {"narration": "TREASURY OPERATION - LIQUIDITY MANAGEMENT", "message_type": "MT205", "expected_purpose": "TREA", "expected_category": "TREA"},
    {"narration": "TREASURY OPERATION COVER PAYMENT", "message_type": "MT202COV", "expected_purpose": "TREA", "expected_category": "TREA"},

    # CORT (Court Payment) - Rare purpose code
    {"narration": "COURT ORDERED PAYMENT", "message_type": "MT103", "expected_purpose": "CORT", "expected_category": "CORT"},
    {"narration": "PAYMENT AS PER COURT ORDER", "message_type": "MT103", "expected_purpose": "CORT", "expected_category": "CORT"},
    {"narration": "LEGAL SETTLEMENT TRANSFER", "message_type": "MT103", "expected_purpose": "CORT", "expected_category": "CORT"},
    {"narration": "COURT MANDATED PAYMENT", "message_type": "MT103", "expected_purpose": "CORT", "expected_category": "CORT"},
    {"narration": "PAYMENT FOR LEGAL SETTLEMENT", "message_type": "MT103", "expected_purpose": "CORT", "expected_category": "CORT"},

    # CCRD (Credit Card Payment) - Often confused with DCRD
    {"narration": "CREDIT CARD PAYMENT", "message_type": "MT103", "expected_purpose": "CCRD", "expected_category": "CCRD"},
    {"narration": "PAYMENT TO CREDIT CARD ACCOUNT", "message_type": "MT103", "expected_purpose": "CCRD", "expected_category": "CCRD"},
    {"narration": "CREDIT CARD BILL SETTLEMENT", "message_type": "MT103", "expected_purpose": "CCRD", "expected_category": "CCRD"},
    {"narration": "PAYMENT FOR CREDIT CARD STATEMENT", "message_type": "MT103", "expected_purpose": "CCRD", "expected_category": "CCRD"},
    {"narration": "CREDIT CARD MONTHLY PAYMENT", "message_type": "MT103", "expected_purpose": "CCRD", "expected_category": "CCRD"},

    # DCRD (Debit Card Payment) - Often confused with CCRD
    {"narration": "DEBIT CARD PAYMENT", "message_type": "MT103", "expected_purpose": "DCRD", "expected_category": "DCRD"},
    {"narration": "PAYMENT VIA DEBIT CARD", "message_type": "MT103", "expected_purpose": "DCRD", "expected_category": "DCRD"},
    {"narration": "DEBIT CARD TRANSACTION SETTLEMENT", "message_type": "MT103", "expected_purpose": "DCRD", "expected_category": "DCRD"},
    {"narration": "DEBIT CARD PURCHASE PAYMENT", "message_type": "MT103", "expected_purpose": "DCRD", "expected_category": "DCRD"},
    {"narration": "PAYMENT USING DEBIT CARD", "message_type": "MT103", "expected_purpose": "DCRD", "expected_category": "DCRD"},

    # INTE (Interest) - Often confused with other financial payments
    {"narration": "INTEREST PAYMENT ON LOAN", "message_type": "MT103", "expected_purpose": "INTE", "expected_category": "INTE"},
    {"narration": "INTEREST SETTLEMENT", "message_type": "MT103", "expected_purpose": "INTE", "expected_category": "INTE"},
    {"narration": "PAYMENT OF ACCRUED INTEREST", "message_type": "MT103", "expected_purpose": "INTE", "expected_category": "INTE"},
    {"narration": "MONTHLY INTEREST PAYMENT", "message_type": "MT103", "expected_purpose": "INTE", "expected_category": "INTE"},
    {"narration": "INTEREST ON FIXED DEPOSIT", "message_type": "MT103", "expected_purpose": "INTE", "expected_category": "INTE"},

    # ICCP (Irrevocable Credit Card Payment) - Very rare purpose code
    {"narration": "IRREVOCABLE CREDIT CARD PAYMENT", "message_type": "MT103", "expected_purpose": "ICCP", "expected_category": "CCRD"},
    {"narration": "GUARANTEED CREDIT CARD SETTLEMENT", "message_type": "MT103", "expected_purpose": "ICCP", "expected_category": "CCRD"},
    {"narration": "IRREVOCABLE PAYMENT TO CREDIT CARD", "message_type": "MT103", "expected_purpose": "ICCP", "expected_category": "CCRD"},
    {"narration": "SECURED CREDIT CARD PAYMENT", "message_type": "MT103", "expected_purpose": "ICCP", "expected_category": "CCRD"},
    {"narration": "IRREVOCABLE SETTLEMENT OF CREDIT CARD", "message_type": "MT103", "expected_purpose": "ICCP", "expected_category": "CCRD"},

    # IDCP (Irrevocable Debit Card Payment) - Very rare purpose code
    {"narration": "IRREVOCABLE DEBIT CARD PAYMENT", "message_type": "MT103", "expected_purpose": "IDCP", "expected_category": "DCRD"},
    {"narration": "GUARANTEED DEBIT CARD SETTLEMENT", "message_type": "MT103", "expected_purpose": "IDCP", "expected_category": "DCRD"},
    {"narration": "IRREVOCABLE PAYMENT VIA DEBIT CARD", "message_type": "MT103", "expected_purpose": "IDCP", "expected_category": "DCRD"},
    {"narration": "SECURED DEBIT CARD PAYMENT", "message_type": "MT103", "expected_purpose": "IDCP", "expected_category": "DCRD"},
    {"narration": "IRREVOCABLE SETTLEMENT OF DEBIT CARD", "message_type": "MT103", "expected_purpose": "IDCP", "expected_category": "DCRD"},

    # Ambiguous narrations that could be classified in multiple ways
    {"narration": "PAYMENT FOR TAX", "message_type": "MT103", "expected_purpose": "TAXS", "expected_category": "TAXS"},
    {"narration": "TRANSFER FOR FINANCIAL SERVICES", "message_type": "MT103", "expected_purpose": "FAND", "expected_category": "SUPP"},
    {"narration": "PAYMENT FOR SERVICES", "message_type": "MT103", "expected_purpose": "SCVE", "expected_category": "SUPP"},
    {"narration": "BUSINESS PAYMENT", "message_type": "MT103", "expected_purpose": "SUPP", "expected_category": "SUPP"},
    {"narration": "MONTHLY PAYMENT", "message_type": "MT103", "expected_purpose": "SUPP", "expected_category": "SUPP"},

    # MT202COV specific rare cases
    {"narration": "COVER FOR TREASURY PAYMENT", "message_type": "MT202COV", "expected_purpose": "TREA", "expected_category": "TREA"},
    {"narration": "COVER FOR COURT ORDERED PAYMENT", "message_type": "MT202COV", "expected_purpose": "CORT", "expected_category": "CORT"},
    {"narration": "COVER FOR INTEREST SETTLEMENT", "message_type": "MT202COV", "expected_purpose": "INTE", "expected_category": "INTE"},
    {"narration": "COVER FOR VAT PAYMENT", "message_type": "MT202COV", "expected_purpose": "VATX", "expected_category": "TAXS"},
    {"narration": "COVER FOR WITHHOLDING TAX", "message_type": "MT202COV", "expected_purpose": "WHLD", "expected_category": "WHLD"},

    # MT205COV specific rare cases
    {"narration": "COVER FOR FINANCIAL INSTITUTION TREASURY OPERATION", "message_type": "MT205COV", "expected_purpose": "TREA", "expected_category": "TREA"},
    {"narration": "COVER FOR FINANCIAL INSTITUTION INTEREST PAYMENT", "message_type": "MT205COV", "expected_purpose": "INTE", "expected_category": "INTE"},
    {"narration": "COVER FOR FINANCIAL INSTITUTION TAX PAYMENT", "message_type": "MT205COV", "expected_purpose": "TAXS", "expected_category": "TAXS"},
    {"narration": "COVER FOR FINANCIAL INSTITUTION VAT SETTLEMENT", "message_type": "MT205COV", "expected_purpose": "VATX", "expected_category": "TAXS"},
    {"narration": "COVER FOR FINANCIAL INSTITUTION COURT PAYMENT", "message_type": "MT205COV", "expected_purpose": "CORT", "expected_category": "CORT"},
]

def test_rare_purpose_codes():
    """Test the classifier with rare and challenging purpose codes."""
    # Initialize the classifier
    classifier = LightGBMPurposeClassifier()

    # Process each test case
    results = []
    correct_purpose = 0
    correct_category = 0
    total_count = len(RARE_PURPOSE_CODE_TESTS)

    for case in RARE_PURPOSE_CODE_TESTS:
        narration = case['narration']
        message_type = case['message_type']
        expected_purpose = case['expected_purpose']
        expected_category = case['expected_category']

        # Predict purpose code
        result = classifier.predict(narration, message_type)

        # Check if prediction matches expected values
        purpose_correct = result.get('purpose_code') == expected_purpose
        category_correct = result.get('category_purpose_code') == expected_category

        if purpose_correct:
            correct_purpose += 1
        if category_correct:
            correct_category += 1

        # Check if enhancement was applied
        enhanced = (result.get('enhancement_applied') is not None or
                   result.get('enhanced', False) or
                   result.get('category_enhancement_applied') is not None)

        # Add to results
        results.append({
            'Narration': narration,
            'Message Type': message_type,
            'Expected Purpose': expected_purpose,
            'Actual Purpose': result.get('purpose_code', 'UNKNOWN'),
            'Purpose Correct': 'Yes' if purpose_correct else 'No',
            'Purpose Confidence': f"{result.get('confidence', 0.0):.2f}",
            'Expected Category': expected_category,
            'Actual Category': result.get('category_purpose_code', 'UNKNOWN'),
            'Category Correct': 'Yes' if category_correct else 'No',
            'Category Confidence': f"{result.get('category_confidence', 0.0):.2f}",
            'Enhanced': 'Yes' if enhanced else 'No',
            'Enhancement': result.get('enhancement_applied',
                          result.get('enhancement_type',
                          result.get('category_enhancement_applied', 'N/A')))
        })

    # Calculate accuracy
    purpose_accuracy = (correct_purpose / total_count) * 100 if total_count > 0 else 0
    category_accuracy = (correct_category / total_count) * 100 if total_count > 0 else 0

    # Print results in a table
    print("\nRare Purpose Code Test Results:")
    print(tabulate(results, headers='keys', tablefmt='grid'))

    # Print accuracy
    print(f"\nPurpose Code Accuracy: {purpose_accuracy:.2f}% ({correct_purpose}/{total_count})")
    print(f"Category Purpose Code Accuracy: {category_accuracy:.2f}% ({correct_category}/{total_count})")

    # Group narrations by expected purpose code
    purpose_groups = {}
    for result in results:
        expected_purpose = result['Expected Purpose']

        if expected_purpose not in purpose_groups:
            purpose_groups[expected_purpose] = []

        purpose_groups[expected_purpose].append(result)

    # Calculate accuracy by expected purpose code
    purpose_stats = {}
    for purpose_code, purpose_results in purpose_groups.items():
        purpose_stats[purpose_code] = {
            'total': len(purpose_results),
            'purpose_correct': sum(1 for r in purpose_results if r['Purpose Correct'] == 'Yes'),
            'category_correct': sum(1 for r in purpose_results if r['Category Correct'] == 'Yes')
        }

    # Print accuracy by expected purpose code
    print("\nAccuracy by Expected Purpose Code:")
    purpose_table = []
    for purpose_code, stats in purpose_stats.items():
        purpose_accuracy = (stats['purpose_correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
        category_accuracy = (stats['category_correct'] / stats['total']) * 100 if stats['total'] > 0 else 0

        purpose_table.append([
            purpose_code,
            stats['total'],
            f"{purpose_accuracy:.2f}%",
            f"{category_accuracy:.2f}%"
        ])

    # Sort by purpose accuracy (ascending)
    purpose_table.sort(key=lambda x: float(x[2].replace('%', '')))

    print(tabulate(purpose_table, headers=["Purpose Code", "Total", "Purpose Accuracy", "Category Accuracy"], tablefmt="grid"))

    # Calculate enhancement rate
    enhancement_count = sum(1 for result in results if result['Enhanced'] == 'Yes')
    enhancement_rate = (enhancement_count / total_count) * 100 if total_count > 0 else 0

    print(f"\nEnhancement Rate: {enhancement_rate:.2f}% ({enhancement_count}/{total_count})")

    # Save results to CSV
    df = pd.DataFrame(results)
    df.to_csv('rare_purpose_code_results.csv', index=False)
    print("\nResults saved to rare_purpose_code_results.csv")

    return results

if __name__ == "__main__":
    test_rare_purpose_codes()
