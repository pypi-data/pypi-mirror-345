#!/usr/bin/env python
"""
Test script for testing specific purpose codes and category purpose codes.

This script:
1. Loads the purpose code classifier model
2. Loads the purpose codes and category purpose codes from JSON files
3. Allows testing specific purpose codes and category purpose codes
4. Provides examples for each purpose code and category purpose code
"""

import os
import sys
import json
import argparse
import random
import pandas as pd
from tabulate import tabulate

# Add parent directory to path to import from purpose_classifier
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier

def load_json_file(file_path):
    """Load a JSON file and return its contents"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        return {}

def generate_example_narration(code, description):
    """Generate an example narration for a purpose code or category purpose code"""
    templates = [
        f"Payment for {description.lower()}",
        f"{description} payment",
        f"{description} - reference 12345",
        f"Invoice for {description.lower()}",
        f"{description} - payment for services",
        f"{code} payment - {description}",
        f"Transfer for {description.lower()}",
        f"{description} - transaction ID 67890",
        f"Payment related to {description.lower()}",
        f"{description} - customer reference ABC123"
    ]
    return random.choice(templates)

def test_purpose_code(classifier, code, description, purpose_codes, category_purpose_codes):
    """Test a specific purpose code with an example narration"""
    # Generate an example narration
    narration = generate_example_narration(code, description)
    
    # Make prediction
    result = classifier.predict(narration)
    
    # Get purpose code and confidence
    predicted_code = result['purpose_code']
    confidence = result['confidence']
    category_code = result.get('category_purpose_code', 'N/A')
    category_confidence = result.get('category_confidence', 0.0)
    
    # Get descriptions
    predicted_description = purpose_codes.get(predicted_code, "Unknown")
    category_description = category_purpose_codes.get(category_code, "Unknown")
    
    # Print result
    print(f"\nTesting Purpose Code: {code} - {description}")
    print(f"Narration: \"{narration}\"")
    print(f"Predicted Purpose Code: {predicted_code} - {predicted_description}")
    print(f"Confidence: {confidence:.4f}")
    print(f"Category Purpose Code: {category_code} - {category_description}")
    print(f"Category Confidence: {category_confidence:.4f}")
    
    # Print top predictions
    print("\nTop Predictions:")
    for pred_code, pred_conf in result.get('top_predictions', []):
        pred_desc = purpose_codes.get(pred_code, "Unknown")
        print(f"  {pred_code} ({pred_conf:.4f}): {pred_desc}")
    
    # Print match status
    if predicted_code == code:
        print("\nResult: ✓ Matched expected purpose code")
    else:
        print("\nResult: ✗ Did not match expected purpose code")
    
    print("-" * 80)
    
    return {
        'code': code,
        'description': description,
        'narration': narration,
        'predicted_code': predicted_code,
        'predicted_description': predicted_description,
        'confidence': confidence,
        'category_code': category_code,
        'category_description': category_description,
        'category_confidence': category_confidence,
        'matched': predicted_code == code
    }

def test_category_purpose_code(classifier, code, description, purpose_codes, category_purpose_codes):
    """Test a specific category purpose code with an example narration"""
    # Generate an example narration
    narration = generate_example_narration(code, description)
    
    # Make prediction
    result = classifier.predict(narration)
    
    # Get purpose code and confidence
    predicted_code = result['purpose_code']
    confidence = result['confidence']
    category_code = result.get('category_purpose_code', 'N/A')
    category_confidence = result.get('category_confidence', 0.0)
    
    # Get descriptions
    predicted_description = purpose_codes.get(predicted_code, "Unknown")
    category_description = category_purpose_codes.get(category_code, "Unknown")
    
    # Print result
    print(f"\nTesting Category Purpose Code: {code} - {description}")
    print(f"Narration: \"{narration}\"")
    print(f"Predicted Purpose Code: {predicted_code} - {predicted_description}")
    print(f"Confidence: {confidence:.4f}")
    print(f"Category Purpose Code: {category_code} - {category_description}")
    print(f"Category Confidence: {category_confidence:.4f}")
    
    # Print top predictions
    print("\nTop Predictions:")
    for pred_code, pred_conf in result.get('top_predictions', []):
        pred_desc = purpose_codes.get(pred_code, "Unknown")
        print(f"  {pred_code} ({pred_conf:.4f}): {pred_desc}")
    
    # Print match status
    if category_code == code:
        print("\nResult: ✓ Matched expected category purpose code")
    else:
        print("\nResult: ✗ Did not match expected category purpose code")
    
    print("-" * 80)
    
    return {
        'code': code,
        'description': description,
        'narration': narration,
        'predicted_code': predicted_code,
        'predicted_description': predicted_description,
        'confidence': confidence,
        'category_code': category_code,
        'category_description': category_description,
        'category_confidence': category_confidence,
        'matched': category_code == code
    }

def main():
    """Main function to test purpose codes and category purpose codes"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test purpose codes and category purpose codes')
    
    parser.add_argument('--model', type=str, default='models/combined_model.pkl',
                        help='Path to the model file')
    
    parser.add_argument('--purpose-codes', type=str, default='data/purpose_codes.json',
                        help='Path to the purpose codes JSON file')
    
    parser.add_argument('--category-purpose-codes', type=str, default='data/category_purpose_codes.json',
                        help='Path to the category purpose codes JSON file')
    
    parser.add_argument('--purpose-code', type=str,
                        help='Specific purpose code to test')
    
    parser.add_argument('--category-purpose-code', type=str,
                        help='Specific category purpose code to test')
    
    parser.add_argument('--test-all-purpose-codes', action='store_true',
                        help='Test all purpose codes')
    
    parser.add_argument('--test-all-category-purpose-codes', action='store_true',
                        help='Test all category purpose codes')
    
    parser.add_argument('--output', type=str,
                        help='Path to save the test results as CSV')
    
    parser.add_argument('--narration', type=str,
                        help='Custom narration to test')
    
    args = parser.parse_args()
    
    # Load purpose codes and category purpose codes
    purpose_codes = load_json_file(args.purpose_codes)
    category_purpose_codes = load_json_file(args.category_purpose_codes)
    
    # Initialize the classifier
    print(f"Loading model from {args.model}")
    classifier = LightGBMPurposeClassifier(model_path=args.model)
    
    # Test with custom narration if provided
    if args.narration:
        print(f"\nTesting custom narration: \"{args.narration}\"")
        result = classifier.predict(args.narration)
        
        # Get purpose code and confidence
        predicted_code = result['purpose_code']
        confidence = result['confidence']
        category_code = result.get('category_purpose_code', 'N/A')
        category_confidence = result.get('category_confidence', 0.0)
        
        # Get descriptions
        predicted_description = purpose_codes.get(predicted_code, "Unknown")
        category_description = category_purpose_codes.get(category_code, "Unknown")
        
        # Print result
        print(f"Predicted Purpose Code: {predicted_code} - {predicted_description}")
        print(f"Confidence: {confidence:.4f}")
        print(f"Category Purpose Code: {category_code} - {category_description}")
        print(f"Category Confidence: {category_confidence:.4f}")
        
        # Print top predictions
        print("\nTop Predictions:")
        for pred_code, pred_conf in result.get('top_predictions', []):
            pred_desc = purpose_codes.get(pred_code, "Unknown")
            print(f"  {pred_code} ({pred_conf:.4f}): {pred_desc}")
        
        print("-" * 80)
        
        # Return early if only testing a custom narration
        if not (args.purpose_code or args.category_purpose_code or 
                args.test_all_purpose_codes or args.test_all_category_purpose_codes):
            return 0
    
    # Initialize results list
    results = []
    
    # Test specific purpose code if provided
    if args.purpose_code:
        if args.purpose_code in purpose_codes:
            description = purpose_codes[args.purpose_code]
            result = test_purpose_code(classifier, args.purpose_code, description, purpose_codes, category_purpose_codes)
            results.append(result)
        else:
            print(f"Purpose code {args.purpose_code} not found in {args.purpose_codes}")
    
    # Test specific category purpose code if provided
    if args.category_purpose_code:
        if args.category_purpose_code in category_purpose_codes:
            description = category_purpose_codes[args.category_purpose_code]
            result = test_category_purpose_code(classifier, args.category_purpose_code, description, purpose_codes, category_purpose_codes)
            results.append(result)
        else:
            print(f"Category purpose code {args.category_purpose_code} not found in {args.category_purpose_codes}")
    
    # Test all purpose codes if requested
    if args.test_all_purpose_codes:
        print("\nTesting all purpose codes...")
        for code, description in purpose_codes.items():
            result = test_purpose_code(classifier, code, description, purpose_codes, category_purpose_codes)
            results.append(result)
    
    # Test all category purpose codes if requested
    if args.test_all_category_purpose_codes:
        print("\nTesting all category purpose codes...")
        for code, description in category_purpose_codes.items():
            result = test_category_purpose_code(classifier, code, description, purpose_codes, category_purpose_codes)
            results.append(result)
    
    # Print summary
    if results:
        matched = sum(1 for result in results if result['matched'])
        total = len(results)
        accuracy = matched / total if total > 0 else 0
        
        print("\nSummary:")
        print(f"Total tests: {total}")
        print(f"Matched: {matched}")
        print(f"Accuracy: {accuracy:.2%}")
    
    # Save results if requested
    if args.output and results:
        df = pd.DataFrame(results)
        df.to_csv(args.output, index=False)
        print(f"\nResults saved to {args.output}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
