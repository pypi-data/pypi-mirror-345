#!/usr/bin/env python
"""
Test script for testing purpose codes and category purpose codes with custom narrations.

This script:
1. Loads the purpose code classifier model
2. Loads the purpose codes and category purpose codes from JSON files
3. Tests custom narrations for specific purpose codes and category purpose codes
4. Provides a batch testing capability from a CSV file
"""

import os
import sys
import json
import argparse
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

def test_narration(classifier, narration, purpose_codes, category_purpose_codes, expected_purpose_code=None, expected_category_purpose_code=None):
    """Test a narration and compare with expected codes if provided"""
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
    print(f"\nTesting narration: \"{narration}\"")
    
    if expected_purpose_code:
        expected_description = purpose_codes.get(expected_purpose_code, "Unknown")
        print(f"Expected Purpose Code: {expected_purpose_code} - {expected_description}")
    
    if expected_category_purpose_code:
        expected_category_description = category_purpose_codes.get(expected_category_purpose_code, "Unknown")
        print(f"Expected Category Purpose Code: {expected_category_purpose_code} - {expected_category_description}")
    
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
    if expected_purpose_code:
        if predicted_code == expected_purpose_code:
            print("\nPurpose Code Result: ✓ Matched expected purpose code")
        else:
            print("\nPurpose Code Result: ✗ Did not match expected purpose code")
    
    if expected_category_purpose_code:
        if category_code == expected_category_purpose_code:
            print("\nCategory Purpose Code Result: ✓ Matched expected category purpose code")
        else:
            print("\nCategory Purpose Code Result: ✗ Did not match expected category purpose code")
    
    print("-" * 80)
    
    return {
        'narration': narration,
        'expected_purpose_code': expected_purpose_code,
        'expected_purpose_description': purpose_codes.get(expected_purpose_code, "Unknown") if expected_purpose_code else None,
        'predicted_purpose_code': predicted_code,
        'predicted_purpose_description': predicted_description,
        'purpose_confidence': confidence,
        'expected_category_purpose_code': expected_category_purpose_code,
        'expected_category_purpose_description': category_purpose_codes.get(expected_category_purpose_code, "Unknown") if expected_category_purpose_code else None,
        'predicted_category_purpose_code': category_code,
        'predicted_category_purpose_description': category_description,
        'category_purpose_confidence': category_confidence,
        'purpose_code_matched': predicted_code == expected_purpose_code if expected_purpose_code else None,
        'category_purpose_code_matched': category_code == expected_category_purpose_code if expected_category_purpose_code else None,
        'processing_time': result.get('processing_time', 0.0)
    }

def main():
    """Main function to test custom narrations"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test custom narrations for purpose codes and category purpose codes')
    
    parser.add_argument('--model', type=str, default='models/combined_model.pkl',
                        help='Path to the model file')
    
    parser.add_argument('--purpose-codes', type=str, default='data/purpose_codes.json',
                        help='Path to the purpose codes JSON file')
    
    parser.add_argument('--category-purpose-codes', type=str, default='data/category_purpose_codes.json',
                        help='Path to the category purpose codes JSON file')
    
    parser.add_argument('--narration', type=str,
                        help='Custom narration to test')
    
    parser.add_argument('--expected-purpose-code', type=str,
                        help='Expected purpose code for the narration')
    
    parser.add_argument('--expected-category-purpose-code', type=str,
                        help='Expected category purpose code for the narration')
    
    parser.add_argument('--file', type=str,
                        help='CSV file with narrations to test (should have columns: narration, expected_purpose_code, expected_category_purpose_code)')
    
    parser.add_argument('--output', type=str,
                        help='Path to save the test results as CSV')
    
    parser.add_argument('--message-type', type=str, choices=['MT103', 'MT202', 'MT202COV', 'MT205', 'MT205COV'],
                        help='Optional SWIFT message type')
    
    args = parser.parse_args()
    
    # Load purpose codes and category purpose codes
    purpose_codes = load_json_file(args.purpose_codes)
    category_purpose_codes = load_json_file(args.category_purpose_codes)
    
    # Initialize the classifier
    print(f"Loading model from {args.model}")
    classifier = LightGBMPurposeClassifier(model_path=args.model)
    
    # Initialize results list
    results = []
    
    # Test single narration if provided
    if args.narration:
        # Make prediction
        if args.message_type:
            print(f"Using message type: {args.message_type}")
            result = test_narration(
                classifier, 
                args.narration, 
                purpose_codes, 
                category_purpose_codes, 
                args.expected_purpose_code, 
                args.expected_category_purpose_code
            )
        else:
            result = test_narration(
                classifier, 
                args.narration, 
                purpose_codes, 
                category_purpose_codes, 
                args.expected_purpose_code, 
                args.expected_category_purpose_code
            )
        
        results.append(result)
    
    # Test narrations from file if provided
    if args.file:
        if not os.path.exists(args.file):
            print(f"File not found: {args.file}")
            return 1
        
        print(f"\nLoading narrations from {args.file}")
        df = pd.read_csv(args.file)
        
        if 'narration' not in df.columns:
            print(f"File does not have a 'narration' column")
            return 1
        
        # Check for expected code columns
        has_expected_purpose_code = 'expected_purpose_code' in df.columns
        has_expected_category_purpose_code = 'expected_category_purpose_code' in df.columns
        
        # Check for message type column
        has_message_type = 'message_type' in df.columns
        
        # Process each narration
        for i, row in df.iterrows():
            narration = row['narration']
            expected_purpose_code = row['expected_purpose_code'] if has_expected_purpose_code else None
            expected_category_purpose_code = row['expected_category_purpose_code'] if has_expected_category_purpose_code else None
            message_type = row['message_type'] if has_message_type else args.message_type
            
            # Make prediction
            if message_type:
                print(f"Using message type: {message_type}")
                result = test_narration(
                    classifier, 
                    narration, 
                    purpose_codes, 
                    category_purpose_codes, 
                    expected_purpose_code, 
                    expected_category_purpose_code
                )
            else:
                result = test_narration(
                    classifier, 
                    narration, 
                    purpose_codes, 
                    category_purpose_codes, 
                    expected_purpose_code, 
                    expected_category_purpose_code
                )
            
            results.append(result)
    
    # Print summary
    if results:
        # Purpose code accuracy
        purpose_code_results = [r for r in results if r['expected_purpose_code'] is not None]
        if purpose_code_results:
            purpose_code_matched = sum(1 for r in purpose_code_results if r['purpose_code_matched'])
            purpose_code_total = len(purpose_code_results)
            purpose_code_accuracy = purpose_code_matched / purpose_code_total
            
            print("\nPurpose Code Accuracy:")
            print(f"Total: {purpose_code_total}")
            print(f"Matched: {purpose_code_matched}")
            print(f"Accuracy: {purpose_code_accuracy:.2%}")
        
        # Category purpose code accuracy
        category_purpose_code_results = [r for r in results if r['expected_category_purpose_code'] is not None]
        if category_purpose_code_results:
            category_purpose_code_matched = sum(1 for r in category_purpose_code_results if r['category_purpose_code_matched'])
            category_purpose_code_total = len(category_purpose_code_results)
            category_purpose_code_accuracy = category_purpose_code_matched / category_purpose_code_total
            
            print("\nCategory Purpose Code Accuracy:")
            print(f"Total: {category_purpose_code_total}")
            print(f"Matched: {category_purpose_code_matched}")
            print(f"Accuracy: {category_purpose_code_accuracy:.2%}")
        
        # Average processing time
        avg_processing_time = sum(r['processing_time'] for r in results) / len(results)
        print(f"\nAverage Processing Time: {avg_processing_time:.4f} seconds")
    
    # Save results if requested
    if args.output and results:
        df = pd.DataFrame(results)
        df.to_csv(args.output, index=False)
        print(f"\nResults saved to {args.output}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
