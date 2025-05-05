#!/usr/bin/env python
"""
Test script to verify the reduction of OTHR category purpose codes.
"""

import os
import sys

# Add the parent directory to the path so we can import the purpose_classifier package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier

def test_othr_reduction():
    """Test the reduction of OTHR category purpose codes."""
    
    # Initialize the classifier
    classifier = LightGBMPurposeClassifier()
    
    # Test cases with narrations that might previously have resulted in OTHR
    test_cases = [
        {
            "narration": "PAYMENT FOR SOFTWARE LICENSE",
            "expected_purpose": "GDDS",
            "expected_category": "SUPP"
        },
        {
            "narration": "CONSULTING SERVICES PAYMENT",
            "expected_purpose": "SCVE",
            "expected_category": "SCVE"
        },
        {
            "narration": "MAINTENANCE FEE FOR EQUIPMENT",
            "expected_purpose": "SERV",
            "expected_category": "SUPP"
        },
        {
            "narration": "PAYMENT FOR LEGAL SERVICES",
            "expected_purpose": "SCVE",
            "expected_category": "SCVE"
        },
        {
            "narration": "MARKETING EXPENSES",
            "expected_purpose": "SCVE",
            "expected_category": "SUPP"
        },
        {
            "narration": "PAYMENT FOR CLOUD SERVICES",
            "expected_purpose": "SCVE",
            "expected_category": "SUPP"
        },
        {
            "narration": "WEBSITE HOSTING FEE",
            "expected_purpose": "SCVE",
            "expected_category": "FCOL"
        },
        {
            "narration": "PAYMENT FOR ADVERTISING",
            "expected_purpose": "SCVE",
            "expected_category": "SUPP"
        },
        {
            "narration": "RESEARCH AND DEVELOPMENT COSTS",
            "expected_purpose": "SCVE",
            "expected_category": "SUPP"
        },
        {
            "narration": "PAYMENT FOR TRAINING SERVICES",
            "expected_purpose": "SCVE",
            "expected_category": "FCOL"
        }
    ]
    
    # Run the tests
    results = []
    for i, test_case in enumerate(test_cases):
        narration = test_case["narration"]
        expected_purpose = test_case["expected_purpose"]
        expected_category = test_case["expected_category"]
        
        # Make the prediction
        result = classifier.predict(narration)
        
        # Check if the prediction matches the expected purpose and category
        matches_purpose = result["purpose_code"] == expected_purpose
        matches_category = result.get("category_purpose_code", "OTHR") != "OTHR"  # We just want to avoid OTHR
        
        # Add the result to the list
        results.append({
            "test_case": i + 1,
            "narration": narration,
            "expected_purpose": expected_purpose,
            "predicted_purpose": result["purpose_code"],
            "purpose_confidence": result.get("confidence", 0),
            "expected_category": expected_category,
            "predicted_category": result.get("category_purpose_code", "OTHR"),
            "category_confidence": result.get("category_confidence", 0),
            "enhancement_applied": result.get("enhancement_applied", None),
            "matches_purpose": matches_purpose,
            "matches_category": matches_category
        })
    
    # Print the results
    print("\nOTHR Reduction Test Results:")
    print("=" * 80)
    
    purpose_success_count = 0
    category_success_count = 0
    for result in results:
        print(f"Test Case {result['test_case']}: {result['narration']}")
        print(f"  Purpose Code: {result['predicted_purpose']} (Expected: {result['expected_purpose']}) - {'✓ PASS' if result['matches_purpose'] else '✗ FAIL'}")
        print(f"  Category Purpose: {result['predicted_category']} (Expected: {result['expected_category']}) - {'✓ PASS' if result['matches_category'] else '✗ FAIL'}")
        print(f"  Purpose Confidence: {result['purpose_confidence']:.2f}")
        print(f"  Category Confidence: {result['category_confidence']:.2f}")
        print(f"  Enhancement Applied: {result['enhancement_applied']}")
        print("-" * 80)
        
        if result['matches_purpose']:
            purpose_success_count += 1
        if result['matches_category']:
            category_success_count += 1
    
    # Print the summary
    print(f"\nSummary:")
    print(f"  Purpose Code: {purpose_success_count}/{len(results)} tests passed ({purpose_success_count/len(results)*100:.1f}%)")
    print(f"  Category Purpose: {category_success_count}/{len(results)} tests passed ({category_success_count/len(results)*100:.1f}%)")
    print(f"  OTHR Reduction: {category_success_count}/{len(results)} ({category_success_count/len(results)*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    test_othr_reduction()
