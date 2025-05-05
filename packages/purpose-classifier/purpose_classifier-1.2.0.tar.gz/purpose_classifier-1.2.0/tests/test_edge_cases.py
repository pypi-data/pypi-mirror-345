#!/usr/bin/env python
"""
Test script for edge cases in the purpose code classifier.

This script tests the classifier with specific edge cases to verify that
the enhancements are working correctly for challenging scenarios.
"""

import os
import sys
import logging
import pandas as pd
from tabulate import tabulate

# Add the parent directory to the path so we can import the purpose_classifier package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the classifier
from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define edge case test data
EDGE_CASES = {
    # Withholding tax edge cases
    'withholding_tax': [
        {"narration": "WITHHOLDING TAX PAYMENT", "message_type": "MT103", "expected_purpose": "WHLD", "expected_category": "WHLD"},
        {"narration": "TAX WITHHOLDING REMITTANCE", "message_type": "MT103", "expected_purpose": "WHLD", "expected_category": "WHLD"},
        {"narration": "PAYMENT FOR WITHHOLDING TAX", "message_type": "MT103", "expected_purpose": "WHLD", "expected_category": "WHLD"},
        {"narration": "STATUTORY WITHHOLDING PAYMENT", "message_type": "MT103", "expected_purpose": "WHLD", "expected_category": "WHLD"},
        {"narration": "WITHHOLDING ON CONTRACTOR PAYMENT", "message_type": "MT103", "expected_purpose": "WHLD", "expected_category": "WHLD"},
    ],
    
    # Travel and accommodation edge cases
    'travel': [
        {"narration": "BUSINESS TRAVEL EXPENSE REIMBURSEMENT", "message_type": "MT103", "expected_purpose": "TRAD", "expected_category": "TRAD"},
        {"narration": "HOTEL BOOKING PAYMENT FOR CONFERENCE", "message_type": "MT103", "expected_purpose": "TRAD", "expected_category": "TRAD"},
        {"narration": "AIRFARE PAYMENT FOR BUSINESS TRIP", "message_type": "MT103", "expected_purpose": "TRAD", "expected_category": "TRAD"},
        {"narration": "TRAVEL AGENCY PAYMENT FOR CORPORATE TRAVEL", "message_type": "MT103", "expected_purpose": "TRAD", "expected_category": "TRAD"},
        {"narration": "PAYMENT FOR FLIGHT TICKETS AND ACCOMMODATION", "message_type": "MT103", "expected_purpose": "TRAD", "expected_category": "TRAD"},
    ],
    
    # Cover payment edge cases
    'cover_payment': [
        {"narration": "COVER FOR CROSS-BORDER PAYMENT TO SUPPLIER", "message_type": "MT202COV", "expected_purpose": "XBCT", "expected_category": "XBCT"},
        {"narration": "COVERING PAYMENT FOR INTERNATIONAL TRADE", "message_type": "MT202COV", "expected_purpose": "TRAD", "expected_category": "TRAD"},
        {"narration": "CORRESPONDENT BANKING COVER FOR CLIENT PAYMENT", "message_type": "MT202COV", "expected_purpose": "INTC", "expected_category": "INTC"},
        {"narration": "COVER TRANSFER FOR FOREIGN EXCHANGE SETTLEMENT", "message_type": "MT202COV", "expected_purpose": "FREX", "expected_category": "FREX"},
        {"narration": "NOSTRO COVER FOR CUSTOMER PAYMENT", "message_type": "MT202COV", "expected_purpose": "INTC", "expected_category": "INTC"},
    ],
    
    # Forex settlement edge cases
    'forex': [
        {"narration": "FOREX SETTLEMENT USD/EUR", "message_type": "MT202", "expected_purpose": "FREX", "expected_category": "FREX"},
        {"narration": "FX SWAP SETTLEMENT", "message_type": "MT202", "expected_purpose": "FREX", "expected_category": "FREX"},
        {"narration": "FOREIGN EXCHANGE SETTLEMENT EUR/GBP", "message_type": "MT202COV", "expected_purpose": "FREX", "expected_category": "FREX"},
        {"narration": "CURRENCY PAIR TRADING USD/JPY", "message_type": "MT202", "expected_purpose": "FREX", "expected_category": "FREX"},
        {"narration": "SETTLEMENT OF FX FORWARD CONTRACT", "message_type": "MT202", "expected_purpose": "FREX", "expected_category": "FREX"},
    ],
    
    # Treasury operation edge cases
    'treasury': [
        {"narration": "TREASURY OPERATION", "message_type": "MT202", "expected_purpose": "TREA", "expected_category": "TREA"},
        {"narration": "TREASURY OPERATION COVER PAYMENT", "message_type": "MT202COV", "expected_purpose": "TREA", "expected_category": "TREA"},
        {"narration": "TREASURY OPERATION - LIQUIDITY MANAGEMENT", "message_type": "MT205", "expected_purpose": "TREA", "expected_category": "TREA"},
        {"narration": "TREASURY OPERATION FOR FINANCIAL INSTITUTION", "message_type": "MT205", "expected_purpose": "TREA", "expected_category": "TREA"},
        {"narration": "CORRESPONDENT COVER FOR TREASURY OPERATION", "message_type": "MT205COV", "expected_purpose": "TREA", "expected_category": "TREA"},
    ],
    
    # Cross-border payment edge cases
    'cross_border': [
        {"narration": "CROSS-BORDER TRANSFER COVER", "message_type": "MT202COV", "expected_purpose": "XBCT", "expected_category": "XBCT"},
        {"narration": "CROSS BORDER PAYMENT COVER", "message_type": "MT205COV", "expected_purpose": "XBCT", "expected_category": "XBCT"},
        {"narration": "CROSS BORDER COVER FOR TRADE SETTLEMENT", "message_type": "MT202COV", "expected_purpose": "XBCT", "expected_category": "XBCT"},
        {"narration": "CROSS BORDER COVER FOR INVESTMENT SETTLEMENT", "message_type": "MT205COV", "expected_purpose": "XBCT", "expected_category": "XBCT"},
        {"narration": "INTERNATIONAL WIRE TRANSFER", "message_type": "MT103", "expected_purpose": "XBCT", "expected_category": "XBCT"},
    ],
}

def test_edge_cases():
    """Test the classifier with edge cases."""
    # Initialize the classifier
    classifier = LightGBMPurposeClassifier()
    
    # Flatten the edge cases for testing
    all_test_cases = []
    for category, cases in EDGE_CASES.items():
        for case in cases:
            case['category'] = category
            all_test_cases.append(case)
    
    # Process each test case
    results = []
    correct_purpose = 0
    correct_category = 0
    total_count = len(all_test_cases)
    
    for case in all_test_cases:
        narration = case['narration']
        message_type = case['message_type']
        expected_purpose = case['expected_purpose']
        expected_category = case['expected_category']
        category = case['category']
        
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
            'Category': category,
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
    print("\nEdge Case Test Results:")
    print(tabulate(results, headers='keys', tablefmt='grid'))
    
    # Print accuracy
    print(f"\nPurpose Code Accuracy: {purpose_accuracy:.2f}% ({correct_purpose}/{total_count})")
    print(f"Category Purpose Code Accuracy: {category_accuracy:.2f}% ({correct_category}/{total_count})")
    
    # Calculate accuracy by category
    category_stats = {}
    for result in results:
        category = result['Category']
        purpose_correct = result['Purpose Correct'] == 'Yes'
        category_correct = result['Category Correct'] == 'Yes'
        
        if category not in category_stats:
            category_stats[category] = {
                'total': 0,
                'purpose_correct': 0,
                'category_correct': 0
            }
            
        category_stats[category]['total'] += 1
        if purpose_correct:
            category_stats[category]['purpose_correct'] += 1
        if category_correct:
            category_stats[category]['category_correct'] += 1
    
    # Print accuracy by category
    print("\nAccuracy by Category:")
    category_table = []
    for category, stats in category_stats.items():
        purpose_accuracy = (stats['purpose_correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
        category_accuracy = (stats['category_correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
        
        category_table.append([
            category,
            stats['total'],
            f"{purpose_accuracy:.2f}%",
            f"{category_accuracy:.2f}%"
        ])
    
    print(tabulate(category_table, headers=["Category", "Total", "Purpose Accuracy", "Category Accuracy"], tablefmt="grid"))
    
    # Save results to CSV
    df = pd.DataFrame(results)
    df.to_csv('edge_case_results.csv', index=False)
    print("\nResults saved to edge_case_results.csv")
    
    return results

if __name__ == "__main__":
    test_edge_cases()
