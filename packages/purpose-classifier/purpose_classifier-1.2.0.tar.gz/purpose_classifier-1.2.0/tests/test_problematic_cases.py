#!/usr/bin/env python3
"""
Test the purpose code classifier with specific problematic cases.

This script:
1. Loads the purpose code classifier model
2. Tests it with specific problematic cases
3. Prints the results
"""

import os
import sys
import argparse
import pandas as pd

# Add parent directory to path to import from purpose_classifier
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Test purpose code classifier with problematic cases')
    
    parser.add_argument('--model', type=str, default='models/combined_model.pkl',
                        help='Path to the model to test')
    
    return parser.parse_args()

def main():
    """Main function to test problematic cases"""
    args = parse_args()
    
    # Load the model
    print(f"Loading model from {args.model}")
    classifier = LightGBMPurposeClassifier(model_path=args.model)
    
    # Define problematic cases
    problematic_cases = [
        # Office supplies cases
        "Invoice for office supplies",
        "Office stationery purchase",
        "Payment for office furniture",
        "Office equipment procurement",
        "Office supplies - staples, paper, pens",
        
        # Business expenses cases
        "Travel expenses for business trip",
        "Business trip reimbursement",
        "Expense claim for business travel",
        "Business expenses - conference fees",
        "Reimbursement for business expenses",
        
        # Account transfer cases
        "Withdrawal from savings account",
        "Transfer between accounts",
        "Account to account transfer",
        "Funds transfer to checking account",
        "Withdrawal of funds from savings",
        
        # Investment cases
        "Transfer to investment account",
        "Investment in mutual funds",
        "Purchase of stocks and bonds",
        "Investment portfolio funding",
        "Securities purchase transaction"
    ]
    
    # Test each case
    print("\nTesting problematic cases:")
    print("-" * 100)
    
    results = []
    
    for narration in problematic_cases:
        print(f"Narration: {narration}")
        
        # Make prediction
        result = classifier.predict(narration)
        
        # Get purpose code and confidence
        purpose_code = result['purpose_code']
        confidence = result['confidence']
        category_purpose_code = result.get('category_purpose_code', 'N/A')
        category_confidence = result.get('category_confidence', 0.0)
        
        # Print result
        print(f"Predicted Purpose Code: {purpose_code}")
        print(f"Confidence: {confidence:.4f}")
        print(f"Category Purpose Code: {category_purpose_code}")
        print(f"Category Confidence: {category_confidence:.4f}")
        
        # Add to results
        results.append({
            'narration': narration,
            'purpose_code': purpose_code,
            'confidence': confidence,
            'category_purpose_code': category_purpose_code,
            'category_confidence': category_confidence
        })
        
        print("-" * 100)
    
    # Group results by purpose code
    purpose_code_counts = {}
    for result in results:
        purpose_code = result['purpose_code']
        if purpose_code not in purpose_code_counts:
            purpose_code_counts[purpose_code] = 0
        purpose_code_counts[purpose_code] += 1
    
    # Print summary
    print("\nSummary of predictions:")
    for purpose_code, count in purpose_code_counts.items():
        print(f"{purpose_code}: {count} cases")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
