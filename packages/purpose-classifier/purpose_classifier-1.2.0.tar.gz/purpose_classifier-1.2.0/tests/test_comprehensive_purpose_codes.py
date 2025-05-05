#!/usr/bin/env python
"""
Comprehensive test script for all purpose codes across different message types.

This script tests the classifier with a wide range of purpose codes,
including rare and edge cases, across all SWIFT message types.
"""

import os
import sys
import json
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
from purpose_classifier.config.settings import PURPOSE_CODES_PATH, CATEGORY_PURPOSE_CODES_PATH

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Message types to test
MESSAGE_TYPES = ['MT103', 'MT202', 'MT202COV', 'MT205', 'MT205COV']

def load_purpose_codes():
    """Load purpose codes and their descriptions from JSON file."""
    try:
        with open(PURPOSE_CODES_PATH, 'r') as f:
            purpose_codes = json.load(f)
        return purpose_codes
    except Exception as e:
        logger.error(f"Error loading purpose codes: {str(e)}")
        return {}

def load_category_purpose_codes():
    """Load category purpose codes and their descriptions from JSON file."""
    try:
        with open(CATEGORY_PURPOSE_CODES_PATH, 'r') as f:
            category_purpose_codes = json.load(f)
        return category_purpose_codes
    except Exception as e:
        logger.error(f"Error loading category purpose codes: {str(e)}")
        return {}

def generate_test_narrations(purpose_code, description, count=3):
    """Generate test narrations for a purpose code."""
    # Basic narration templates with more realistic patterns
    templates = [
        f"PAYMENT FOR {description.upper()} REF123456",
        f"{description.upper()} PAYMENT - INVOICE INV456789",
        f"TRANSFER FOR {description.upper()} - AGREEMENT AGR789012",
        f"{description.upper()} TRANSFER - CONTRACT CONT789012",
        f"SETTLEMENT FOR {description.upper()} - DOCUMENT DOC123456",
        f"{description.upper()} SETTLEMENT - REFERENCE REF123456",
        f"REMITTANCE FOR {description.upper()} - PAYMENT ID PAY123456",
        f"{description.upper()} REMITTANCE - ORDER ORD456789",
        f"DISBURSEMENT FOR {description.upper()} - TRANSACTION TXN789012",
        f"{description.upper()} DISBURSEMENT - PURCHASE ORDER PO123456"
    ]

    # Add purpose code specific templates
    if purpose_code == 'SALA':
        templates.extend([
            "MONTHLY SALARY PAYMENT",
            "PAYROLL TRANSFER FOR EMPLOYEES",
            "WAGE PAYMENT FOR STAFF"
        ])
    elif purpose_code == 'TAXS':
        templates.extend([
            "TAX PAYMENT TO REVENUE AUTHORITY",
            "CORPORATE TAX SETTLEMENT",
            "INCOME TAX PAYMENT"
        ])
    elif purpose_code == 'WHLD':
        templates.extend([
            "WITHHOLDING TAX PAYMENT",
            "TAX WITHHOLDING REMITTANCE",
            "STATUTORY WITHHOLDING PAYMENT"
        ])
    elif purpose_code == 'TRAD':
        templates.extend([
            "TRADE SETTLEMENT PAYMENT",
            "PAYMENT FOR INTERNATIONAL TRADE",
            "TRADE FINANCE TRANSACTION"
        ])
    elif purpose_code == 'INTC':
        templates.extend([
            "INTRA-COMPANY TRANSFER",
            "INTERNAL COMPANY PAYMENT",
            "TRANSFER BETWEEN AFFILIATED ENTITIES"
        ])
    elif purpose_code == 'FREX':
        templates.extend([
            "FOREIGN EXCHANGE SETTLEMENT USD/EUR",
            "FX TRANSACTION PAYMENT",
            "CURRENCY EXCHANGE SETTLEMENT"
        ])
    elif purpose_code == 'TREA':
        templates.extend([
            "TREASURY OPERATION PAYMENT",
            "TREASURY MANAGEMENT TRANSFER",
            "TREASURY SERVICES SETTLEMENT"
        ])
    elif purpose_code == 'XBCT':
        templates.extend([
            "CROSS-BORDER PAYMENT",
            "INTERNATIONAL WIRE TRANSFER",
            "CROSS-BORDER REMITTANCE"
        ])
    elif purpose_code == 'VATX':
        templates.extend([
            "VAT PAYMENT TO TAX AUTHORITY",
            "VALUE ADDED TAX SETTLEMENT",
            "VAT REMITTANCE"
        ])
    elif purpose_code == 'CORT':
        templates.extend([
            "COURT ORDERED PAYMENT",
            "LEGAL SETTLEMENT TRANSFER",
            "PAYMENT AS PER COURT ORDER"
        ])
    elif purpose_code == 'CCRD':
        templates.extend([
            "CREDIT CARD PAYMENT",
            "PAYMENT TO CREDIT CARD ACCOUNT",
            "CREDIT CARD BILL SETTLEMENT"
        ])
    elif purpose_code == 'DCRD':
        templates.extend([
            "DEBIT CARD PAYMENT",
            "PAYMENT VIA DEBIT CARD",
            "DEBIT CARD TRANSACTION SETTLEMENT"
        ])
    elif purpose_code == 'INTE':
        templates.extend([
            "INTEREST PAYMENT ON LOAN",
            "INTEREST SETTLEMENT",
            "PAYMENT OF ACCRUED INTEREST"
        ])
    elif purpose_code == 'ICCP':
        templates.extend([
            "IRREVOCABLE CREDIT CARD PAYMENT",
            "GUARANTEED CREDIT CARD SETTLEMENT",
            "IRREVOCABLE PAYMENT TO CREDIT CARD"
        ])
    elif purpose_code == 'IDCP':
        templates.extend([
            "IRREVOCABLE DEBIT CARD PAYMENT",
            "GUARANTEED DEBIT CARD SETTLEMENT",
            "IRREVOCABLE PAYMENT VIA DEBIT CARD"
        ])

    # Return the specified number of templates
    return templates[:count]

def generate_message_type_specific_narrations(purpose_code, message_type):
    """Generate message type specific narrations for a purpose code."""
    narrations = []

    # Common reference patterns to make narrations more realistic
    references = [
        "REF123456", "INV456789", "AGR789012", "CONT789012",
        "DOC123456", "PAY123456", "ORD456789", "TXN789012", "PO123456"
    ]

    # Add a random reference to make narrations more realistic
    import random
    ref = random.choice(references)

    if message_type == 'MT103':
        if purpose_code == 'SALA':
            narrations.extend([
                f"SALARY PAYMENT FOR EMPLOYEE JOHN DOE - {ref}",
                f"MONTHLY PAYROLL TRANSFER - {ref}",
                f"WAGES TRANSFER FEBRUARY 2024 - {ref}"
            ])
        elif purpose_code == 'TAXS':
            narrations.extend([
                f"TAX PAYMENT TO GOVERNMENT AUTHORITY - {ref}",
                f"QUARTERLY TAX SETTLEMENT Q1 2024 - {ref}",
                f"INCOME TAX PAYMENT FY2023 - {ref}"
            ])
        elif purpose_code == 'TRAD':
            narrations.extend([
                f"PAYMENT FOR GOODS AND SERVICES - {ref}",
                f"TRADE PAYMENT - SHIPMENT {ref}",
                f"INTERNATIONAL TRADE SETTLEMENT - {ref}"
            ])
        elif purpose_code == 'WHLD':
            narrations.extend([
                f"WITHHOLDING TAX ON CONTRACTOR PAYMENT - {ref}",
                f"TAX WITHHOLDING REMITTANCE - {ref}",
                f"WITHHOLDING TAX PAYMENT Q1 2024 - {ref}"
            ])
        elif purpose_code == 'VATX':
            narrations.extend([
                f"VAT PAYMENT FOR Q1 2023 - {ref}",
                f"VALUE ADDED TAX SETTLEMENT - {ref}",
                f"QUARTERLY VAT PAYMENT - {ref}"
            ])
        elif purpose_code == 'GDDS':
            narrations.extend([
                f"PAYMENT FOR GOODS DELIVERED - {ref}",
                f"PURCHASE OF MERCHANDISE - INVOICE {ref}",
                f"GOODS PROCUREMENT PAYMENT - {ref}"
            ])
        elif purpose_code == 'SCVE':
            narrations.extend([
                f"PAYMENT FOR PROFESSIONAL SERVICES - {ref}",
                f"CONSULTING SERVICES INVOICE - {ref}",
                f"SERVICE PROVIDER PAYMENT - {ref}"
            ])
        elif purpose_code == 'DIVD':
            narrations.extend([
                f"DIVIDEND PAYMENT Q1 2024 - {ref}",
                f"SHAREHOLDER DIVIDEND DISTRIBUTION - {ref}",
                f"QUARTERLY DIVIDEND PAYOUT - {ref}"
            ])
        elif purpose_code == 'LOAN':
            narrations.extend([
                f"LOAN DISBURSEMENT - AGREEMENT {ref}",
                f"LOAN PAYMENT TO BORROWER - {ref}",
                f"CREDIT FACILITY DRAWDOWN - {ref}"
            ])
        elif purpose_code == 'INSU':
            narrations.extend([
                f"INSURANCE PREMIUM PAYMENT - POLICY {ref}",
                f"ANNUAL INSURANCE SETTLEMENT - {ref}",
                f"HEALTH INSURANCE PREMIUM - {ref}"
            ])
        elif purpose_code == 'EDUC':
            narrations.extend([
                f"TUITION FEE PAYMENT - {ref}",
                f"EDUCATION EXPENSES - UNIVERSITY {ref}",
                f"SCHOOL FEE SETTLEMENT - {ref}"
            ])
        elif purpose_code == 'BONU':
            narrations.extend([
                f"ANNUAL BONUS PAYMENT - {ref}",
                f"PERFORMANCE BONUS TRANSFER - {ref}",
                f"EMPLOYEE BONUS PAYOUT - {ref}"
            ])
        elif purpose_code == 'COMM':
            narrations.extend([
                f"COMMISSION PAYMENT - AGENT {ref}",
                f"SALES COMMISSION TRANSFER - {ref}",
                f"BROKER COMMISSION SETTLEMENT - {ref}"
            ])
        elif purpose_code == 'SUPP':
            narrations.extend([
                f"SUPPLIER PAYMENT - INVOICE {ref}",
                f"VENDOR SETTLEMENT - {ref}",
                f"PAYMENT TO SUPPLIER - CONTRACT {ref}"
            ])

    elif message_type == 'MT202':
        if purpose_code == 'INTC':
            narrations.extend([
                f"INTERBANK TRANSFER FOR LIQUIDITY - {ref}",
                f"INTRAGROUP PAYMENT - SUBSIDIARY {ref}",
                f"INTERNAL COMPANY SETTLEMENT - {ref}"
            ])
        elif purpose_code == 'FREX':
            narrations.extend([
                f"FOREX SETTLEMENT USD/EUR - {ref}",
                f"FX TRANSACTION PAYMENT - TRADE {ref}",
                f"CURRENCY EXCHANGE SETTLEMENT - {ref}"
            ])
        elif purpose_code == 'TREA':
            narrations.extend([
                f"TREASURY OPERATION - {ref}",
                f"TREASURY MANAGEMENT TRANSFER - {ref}",
                f"INTERBANK TREASURY SETTLEMENT - {ref}"
            ])
        elif purpose_code == 'CORT':
            narrations.extend([
                f"COURT ORDERED PAYMENT - CASE {ref}",
                f"LEGAL SETTLEMENT TRANSFER - {ref}",
                f"PAYMENT AS PER COURT ORDER - {ref}"
            ])
        elif purpose_code == 'XBCT':
            narrations.extend([
                f"CROSS-BORDER PAYMENT - {ref}",
                f"INTERNATIONAL TRANSFER SETTLEMENT - {ref}",
                f"OVERSEAS PAYMENT - {ref}"
            ])

    elif message_type == 'MT202COV':
        if purpose_code == 'INTC':
            narrations.extend([
                f"COVER PAYMENT FOR CUSTOMER TRANSFER - {ref}",
                f"INTRAGROUP COVER PAYMENT - {ref}",
                f"COVER FOR AFFILIATED COMPANY - {ref}"
            ])
        elif purpose_code == 'TRAD':
            narrations.extend([
                f"COVER FOR TRADE FINANCE TRANSACTION - {ref}",
                f"TRADE SETTLEMENT COVER PAYMENT - {ref}",
                f"COVER FOR INTERNATIONAL TRADE - {ref}"
            ])
        elif purpose_code == 'XBCT':
            narrations.extend([
                f"CROSS-BORDER TRANSFER COVER - {ref}",
                f"COVER FOR INTERNATIONAL PAYMENT - {ref}",
                f"OVERSEAS TRANSFER COVER - {ref}"
            ])
        elif purpose_code == 'FREX':
            narrations.extend([
                f"FOREIGN EXCHANGE SETTLEMENT EUR/GBP - {ref}",
                f"COVER FOR FX TRANSACTION - {ref}",
                f"FOREX COVER PAYMENT - {ref}"
            ])
        elif purpose_code == 'TREA':
            narrations.extend([
                f"TREASURY OPERATION COVER PAYMENT - {ref}",
                f"COVER FOR TREASURY MANAGEMENT - {ref}",
                f"TREASURY SERVICES COVER - {ref}"
            ])

    elif message_type == 'MT205':
        if purpose_code == 'INTC':
            narrations.extend([
                f"FINANCIAL INSTITUTION TRANSFER - {ref}",
                f"INTERBANK SETTLEMENT - {ref}",
                f"BANK-TO-BANK PAYMENT - {ref}"
            ])
        elif purpose_code == 'TREA':
            narrations.extend([
                f"TREASURY OPERATION - LIQUIDITY MANAGEMENT - {ref}",
                f"TREASURY SERVICES PAYMENT - {ref}",
                f"INTERBANK TREASURY TRANSFER - {ref}"
            ])
        elif purpose_code == 'FREX':
            narrations.extend([
                f"FINANCIAL INSTITUTION FOREX SETTLEMENT - {ref}",
                f"INTERBANK FX TRANSACTION - {ref}",
                f"BANK-TO-BANK CURRENCY EXCHANGE - {ref}"
            ])
        elif purpose_code == 'CORT':
            narrations.extend([
                f"COURT MANDATED FINANCIAL TRANSFER - {ref}",
                f"LEGAL SETTLEMENT BETWEEN INSTITUTIONS - {ref}",
                f"JUDICIAL PAYMENT ORDER - {ref}"
            ])
        elif purpose_code == 'XBCT':
            narrations.extend([
                f"CROSS-BORDER INTERBANK PAYMENT - {ref}",
                f"INTERNATIONAL FINANCIAL INSTITUTION TRANSFER - {ref}",
                f"OVERSEAS BANK SETTLEMENT - {ref}"
            ])

    elif message_type == 'MT205COV':
        if purpose_code == 'INTC':
            narrations.extend([
                f"COVER FOR FINANCIAL INSTITUTION TRANSFER - {ref}",
                f"INTERBANK COVER PAYMENT - {ref}",
                f"COVER FOR BANK-TO-BANK SETTLEMENT - {ref}"
            ])
        elif purpose_code == 'XBCT':
            narrations.extend([
                f"CROSS BORDER PAYMENT COVER - {ref}",
                f"COVER FOR INTERNATIONAL BANK TRANSFER - {ref}",
                f"OVERSEAS FINANCIAL INSTITUTION COVER - {ref}"
            ])
        elif purpose_code == 'TREA':
            narrations.extend([
                f"COVER FOR TREASURY OPERATION - {ref}",
                f"TREASURY MANAGEMENT COVER PAYMENT - {ref}",
                f"INTERBANK TREASURY COVER - {ref}"
            ])
        elif purpose_code == 'FREX':
            narrations.extend([
                f"COVER FOR FINANCIAL INSTITUTION FOREX - {ref}",
                f"FX SETTLEMENT COVER BETWEEN BANKS - {ref}",
                f"INTERBANK CURRENCY EXCHANGE COVER - {ref}"
            ])
        elif purpose_code == 'CORT':
            narrations.extend([
                f"COVER FOR COURT ORDERED BANK PAYMENT - {ref}",
                f"LEGAL SETTLEMENT COVER TRANSFER - {ref}",
                f"JUDICIAL PAYMENT COVER - {ref}"
            ])

    # If no specific narrations were added, return an empty list
    return narrations

def test_comprehensive_purpose_codes():
    """Test the classifier with a comprehensive set of purpose codes."""
    # Initialize the classifier with thread limit to avoid CPU count issues
    import os
    os.environ['OMP_NUM_THREADS'] = '1'  # Limit OpenMP threads
    os.environ['OPENBLAS_NUM_THREADS'] = '1'  # Limit OpenBLAS threads
    os.environ['MKL_NUM_THREADS'] = '1'  # Limit MKL threads
    os.environ['VECLIB_MAXIMUM_THREADS'] = '1'  # Limit Accelerate threads
    os.environ['NUMEXPR_NUM_THREADS'] = '1'  # Limit NumExpr threads

    # Initialize with explicit thread limit
    classifier = LightGBMPurposeClassifier(thread_limit=1)

    # Load purpose codes and category purpose codes
    purpose_codes = load_purpose_codes()
    category_purpose_codes = load_category_purpose_codes()

    # Define the most common purpose codes that the model is trained on
    # These are the codes that appear most frequently in the training data
    common_purpose_codes = [
        'SALA', 'TAXS', 'INTC', 'TRAD', 'GDDS', 'SCVE', 'DIVD', 'LOAN',
        'INSU', 'WHLD', 'EDUC', 'FREX', 'TREA', 'CORT', 'XBCT', 'VATX',
        'CCRD', 'DCRD', 'INTE', 'ICCP', 'IDCP', 'BONU', 'COMM', 'SUPP'
    ]

    # Generate test cases
    test_cases = []

    # For each purpose code, generate test narrations for each message type
    for purpose_code in common_purpose_codes:
        # Skip if purpose code is not in the purpose_codes dictionary
        if purpose_code not in purpose_codes:
            continue

        # Get description from purpose_codes
        description = purpose_codes.get(purpose_code, purpose_code)

        # Generate generic narrations for this purpose code
        generic_narrations = generate_test_narrations(purpose_code, description)

        # For each message type, add generic and specific narrations
        for message_type in MESSAGE_TYPES:
            # Add generic narrations
            for narration in generic_narrations:
                test_cases.append({
                    'purpose_code': purpose_code,
                    'description': description,
                    'narration': narration,
                    'message_type': message_type,
                    'type': 'generic'
                })

            # Add message type specific narrations
            specific_narrations = generate_message_type_specific_narrations(purpose_code, message_type)
            for narration in specific_narrations:
                test_cases.append({
                    'purpose_code': purpose_code,
                    'description': description,
                    'narration': narration,
                    'message_type': message_type,
                    'type': 'specific'
                })

    # Process each test case
    results = []
    correct_purpose = 0
    total_count = len(test_cases)

    logger.info(f"Testing {total_count} narrations across all purpose codes and message types...")

    for i, case in enumerate(test_cases):
        if i % 100 == 0:
            logger.info(f"Processing test case {i+1}/{total_count}...")

        narration = case['narration']
        message_type = case['message_type']
        expected_purpose = case['purpose_code']

        # Skip if narration is empty
        if not narration:
            continue

        # Predict purpose code
        result = classifier.predict(narration, message_type)

        # Check if prediction matches expected purpose code
        purpose_correct = result.get('purpose_code') == expected_purpose

        if purpose_correct:
            correct_purpose += 1

        # Check if enhancement was applied
        enhanced = (result.get('enhancement_applied') is not None or
                   result.get('enhanced', False) or
                   result.get('category_enhancement_applied') is not None)

        # Add to results
        results.append({
            'Purpose Code': expected_purpose,
            'Description': case['description'],
            'Narration': narration,
            'Message Type': message_type,
            'Type': case['type'],
            'Predicted Purpose': result.get('purpose_code', 'UNKNOWN'),
            'Correct': 'Yes' if purpose_correct else 'No',
            'Confidence': f"{result.get('confidence', 0.0):.2f}",
            'Category Purpose': result.get('category_purpose_code', 'UNKNOWN'),
            'Category Confidence': f"{result.get('category_confidence', 0.0):.2f}",
            'Enhanced': 'Yes' if enhanced else 'No',
            'Enhancement': result.get('enhancement_applied',
                          result.get('enhancement_type',
                          result.get('category_enhancement_applied', 'N/A')))
        })

    # Calculate accuracy
    purpose_accuracy = (correct_purpose / total_count) * 100 if total_count > 0 else 0

    # Print overall results
    print("\nComprehensive Purpose Code Test Results:")
    print(f"Total test cases: {total_count}")
    print(f"Purpose Code Accuracy: {purpose_accuracy:.2f}% ({correct_purpose}/{total_count})")

    # Calculate accuracy by purpose code
    purpose_stats = {}
    for result in results:
        purpose_code = result['Purpose Code']
        correct = result['Correct'] == 'Yes'

        if purpose_code not in purpose_stats:
            purpose_stats[purpose_code] = {
                'total': 0,
                'correct': 0
            }

        purpose_stats[purpose_code]['total'] += 1
        if correct:
            purpose_stats[purpose_code]['correct'] += 1

    # Print accuracy by purpose code
    print("\nAccuracy by Purpose Code:")
    purpose_table = []
    for purpose_code, stats in purpose_stats.items():
        accuracy = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
        if isinstance(purpose_codes, dict):
            description = purpose_codes.get(purpose_code, 'Unknown')
        else:
            description = 'Unknown'

        purpose_table.append([
            purpose_code,
            description,
            stats['total'],
            stats['correct'],
            f"{accuracy:.2f}%"
        ])

    # Sort by accuracy (ascending)
    purpose_table.sort(key=lambda x: float(x[4].replace('%', '')))

    print(tabulate(purpose_table, headers=["Purpose Code", "Description", "Total", "Correct", "Accuracy"], tablefmt="grid"))

    # Calculate accuracy by message type
    message_type_stats = {}
    for result in results:
        message_type = result['Message Type']
        correct = result['Correct'] == 'Yes'

        if message_type not in message_type_stats:
            message_type_stats[message_type] = {
                'total': 0,
                'correct': 0
            }

        message_type_stats[message_type]['total'] += 1
        if correct:
            message_type_stats[message_type]['correct'] += 1

    # Print accuracy by message type
    print("\nAccuracy by Message Type:")
    message_type_table = []
    for message_type, stats in message_type_stats.items():
        accuracy = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0

        message_type_table.append([
            message_type,
            stats['total'],
            stats['correct'],
            f"{accuracy:.2f}%"
        ])

    print(tabulate(message_type_table, headers=["Message Type", "Total", "Correct", "Accuracy"], tablefmt="grid"))

    # Calculate enhancement rate
    enhancement_count = sum(1 for result in results if result['Enhanced'] == 'Yes')
    enhancement_rate = (enhancement_count / total_count) * 100 if total_count > 0 else 0

    print(f"\nEnhancement Rate: {enhancement_rate:.2f}% ({enhancement_count}/{total_count})")

    # Find the worst performing purpose codes (accuracy < 50%)
    print("\nWorst Performing Purpose Codes (Accuracy < 50%):")
    worst_performers = [row for row in purpose_table if float(row[4].replace('%', '')) < 50]
    if worst_performers:
        print(tabulate(worst_performers, headers=["Purpose Code", "Description", "Total", "Correct", "Accuracy"], tablefmt="grid"))
    else:
        print("No purpose codes with accuracy below 50%")

    # Save results to CSV
    df = pd.DataFrame(results)
    df.to_csv('comprehensive_purpose_code_results.csv', index=False)
    print("\nResults saved to comprehensive_purpose_code_results.csv")

    return results

if __name__ == "__main__":
    test_comprehensive_purpose_codes()
