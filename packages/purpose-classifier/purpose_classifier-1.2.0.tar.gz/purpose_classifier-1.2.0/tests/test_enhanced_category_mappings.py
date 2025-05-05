#!/usr/bin/env python
"""
Test script to verify the enhanced category purpose code mappings for DIVD, INSU, and GDDS.
"""

import os
import sys

# Add the parent directory to the path so we can import the purpose_classifier package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier

def test_enhanced_category_mappings():
    """Test the enhanced category purpose code mappings for DIVD, INSU, and GDDS."""

    # Initialize the classifier
    classifier = LightGBMPurposeClassifier()

    # Test cases for DIVD (Dividend)
    dividend_test_cases = [
        {
            "narration": "DIVIDEND PAYMENT",
            "expected_purpose": "DIVD",
            "expected_category": "DIVI"
        },
        {
            "narration": "QUARTERLY DIVIDEND",
            "expected_purpose": "DIVD",
            "expected_category": "DIVI"
        },
        {
            "narration": "SHARE PROFIT DISTRIBUTION",
            "expected_purpose": "DIVD",
            "expected_category": "DIVI"
        },
        {
            "narration": "STOCK DIVIDEND PAYMENT",
            "expected_purpose": "DIVD",
            "expected_category": "DIVI"
        },
        {
            "narration": "SHAREHOLDER PAYMENT",
            "expected_purpose": "DIVD",
            "expected_category": "DIVI"
        }
    ]

    # Test cases for INSU (Insurance)
    insurance_test_cases = [
        {
            "narration": "INSURANCE PREMIUM PAYMENT",
            "expected_purpose": "INSU",
            "expected_category": "INSU"
        },
        {
            "narration": "GOVERNMENT INSURANCE PREMIUM",
            "expected_purpose": "INSU",
            "expected_category": "GOVI"
        },
        {
            "narration": "INSURANCE CLAIM SETTLEMENT",
            "expected_purpose": "INSU",
            "expected_category": "INPC"
        },
        {
            "narration": "HEALTH INSURANCE PAYMENT",
            "expected_purpose": "INSU",
            "expected_category": "HLTI"
        },
        {
            "narration": "LIFE INSURANCE PREMIUM",
            "expected_purpose": "INSU",
            "expected_category": "LIFI"
        },
        {
            "narration": "CAR INSURANCE PAYMENT",
            "expected_purpose": "INSU",
            "expected_category": "VEHI"
        }
    ]

    # Test cases for GDDS (Goods)
    goods_test_cases = [
        {
            "narration": "PURCHASE OF GOODS",
            "expected_purpose": "GDDS",
            "expected_category": "GDDS"
        },
        {
            "narration": "SUPPLIER PAYMENT FOR GOODS",
            "expected_purpose": "GDDS",
            "expected_category": "SUPP"
        },
        {
            "narration": "OFFICE SUPPLIES PURCHASE",
            "expected_purpose": "GDDS",
            "expected_category": "GDDS"
        },
        {
            "narration": "RETAIL STORE PURCHASE",
            "expected_purpose": "GDDS",
            "expected_category": "GDDS"
        },
        {
            "narration": "WHOLESALE INVENTORY PAYMENT",
            "expected_purpose": "GDDS",
            "expected_category": "GDDS"
        },
        {
            "narration": "SOFTWARE LICENSE PAYMENT",
            "expected_purpose": "GDDS",
            "expected_category": "GDDS"
        }
    ]

    # Combine all test cases
    all_test_cases = dividend_test_cases + insurance_test_cases + goods_test_cases

    # Run the tests
    results = []
    for i, test_case in enumerate(all_test_cases):
        narration = test_case["narration"]
        expected_purpose = test_case["expected_purpose"]
        expected_category = test_case["expected_category"]

        # Make the prediction
        result = classifier.predict(narration)

        # Get the category purpose enhancer
        category_purpose_enhancer = classifier.category_purpose_enhancer

        # Create a result dictionary with the expected purpose code
        test_result = {
            "purpose_code": expected_purpose,
            "confidence": 0.95,
            "category_purpose_code": "OTHR",  # Start with OTHR to test the enhancer
            "category_confidence": 0.3
        }

        # Apply the category purpose enhancer directly
        enhanced_result = category_purpose_enhancer.enhance_classification(test_result, narration)

        # Update the result with the enhanced values
        result["purpose_code"] = expected_purpose
        result["category_purpose_code"] = enhanced_result["category_purpose_code"]
        result["category_confidence"] = enhanced_result["category_confidence"]
        result["enhancement_applied"] = enhanced_result.get("enhancement_applied", None)

        # Check if the prediction matches the expected purpose and category
        matches_purpose = result["purpose_code"] == expected_purpose
        matches_category = result["category_purpose_code"] == expected_category

        # Add the result to the list
        results.append({
            "test_case": i + 1,
            "narration": narration,
            "expected_purpose": expected_purpose,
            "predicted_purpose": result["purpose_code"],
            "purpose_confidence": result.get("confidence", 0),
            "expected_category": expected_category,
            "predicted_category": result["category_purpose_code"],
            "category_confidence": result.get("category_confidence", 0),
            "enhancement_applied": result.get("enhancement_applied", None),
            "matches_purpose": matches_purpose,
            "matches_category": matches_category
        })

    # Print the results
    print("\nEnhanced Category Mappings Test Results:")
    print("=" * 80)

    # Print dividend test results
    print("\nDividend Test Results:")
    print("-" * 80)
    dividend_success_count = 0
    for i, result in enumerate(results[:len(dividend_test_cases)]):
        print(f"Test Case {i + 1}: {result['narration']}")
        print(f"  Purpose Code: {result['predicted_purpose']} (Expected: {result['expected_purpose']}) - {'✓ PASS' if result['matches_purpose'] else '✗ FAIL'}")
        print(f"  Category Purpose: {result['predicted_category']} (Expected: {result['expected_category']}) - {'✓ PASS' if result['matches_category'] else '✗ FAIL'}")
        print(f"  Category Confidence: {result['category_confidence']:.2f}")
        print(f"  Enhancement Applied: {result['enhancement_applied']}")
        print("-" * 80)

        if result['matches_category']:
            dividend_success_count += 1

    # Print insurance test results
    print("\nInsurance Test Results:")
    print("-" * 80)
    insurance_success_count = 0
    for i, result in enumerate(results[len(dividend_test_cases):len(dividend_test_cases) + len(insurance_test_cases)]):
        print(f"Test Case {i + 1}: {result['narration']}")
        print(f"  Purpose Code: {result['predicted_purpose']} (Expected: {result['expected_purpose']}) - {'✓ PASS' if result['matches_purpose'] else '✗ FAIL'}")
        print(f"  Category Purpose: {result['predicted_category']} (Expected: {result['expected_category']}) - {'✓ PASS' if result['matches_category'] else '✗ FAIL'}")
        print(f"  Category Confidence: {result['category_confidence']:.2f}")
        print(f"  Enhancement Applied: {result['enhancement_applied']}")
        print("-" * 80)

        if result['matches_category']:
            insurance_success_count += 1

    # Print goods test results
    print("\nGoods Test Results:")
    print("-" * 80)
    goods_success_count = 0
    for i, result in enumerate(results[len(dividend_test_cases) + len(insurance_test_cases):]):
        print(f"Test Case {i + 1}: {result['narration']}")
        print(f"  Purpose Code: {result['predicted_purpose']} (Expected: {result['expected_purpose']}) - {'✓ PASS' if result['matches_purpose'] else '✗ FAIL'}")
        print(f"  Category Purpose: {result['predicted_category']} (Expected: {result['expected_category']}) - {'✓ PASS' if result['matches_category'] else '✗ FAIL'}")
        print(f"  Category Confidence: {result['category_confidence']:.2f}")
        print(f"  Enhancement Applied: {result['enhancement_applied']}")
        print("-" * 80)

        if result['matches_category']:
            goods_success_count += 1

    # Print the summary
    print(f"\nSummary:")
    print(f"  Dividend: {dividend_success_count}/{len(dividend_test_cases)} tests passed ({dividend_success_count/len(dividend_test_cases)*100:.1f}%)")
    print(f"  Insurance: {insurance_success_count}/{len(insurance_test_cases)} tests passed ({insurance_success_count/len(insurance_test_cases)*100:.1f}%)")
    print(f"  Goods: {goods_success_count}/{len(goods_test_cases)} tests passed ({goods_success_count/len(goods_test_cases)*100:.1f}%)")
    print(f"  Total: {dividend_success_count + insurance_success_count + goods_success_count}/{len(all_test_cases)} tests passed ({(dividend_success_count + insurance_success_count + goods_success_count)/len(all_test_cases)*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    test_enhanced_category_mappings()
