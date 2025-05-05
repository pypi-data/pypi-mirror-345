#!/usr/bin/env python
"""
Verify the BERT-based purpose code classifier.

This script loads the trained BERT model and tests it on a few sample narrations.
"""

import os
import sys
import joblib
import argparse
import logging

# Add the parent directory to the path so we can import the purpose_classifier package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Verify the BERT model for purpose code classification')
    parser.add_argument('--model', type=str, default='models/combined_model.pkl',
                       help='Path to the trained model')
    parser.add_argument('--samples', type=int, default=5,
                       help='Number of sample narrations to test')
    
    return parser.parse_args()

def main():
    """Main function to verify the BERT model"""
    args = parse_args()
    
    # Check if model exists
    if not os.path.exists(args.model):
        print(f"Model not found: {args.model}")
        return 1
    
    print(f"Loading model from {args.model}")
    
    # Initialize the classifier with the trained BERT model
    try:
        classifier = LightGBMPurposeClassifier(model_path=args.model)
        print("Model loaded successfully")
        
        # Check model type
        model_type = getattr(classifier.model, 'bert_model', None)
        if model_type:
            print(f"Detected BERT model: {model_type}")
        else:
            print("This does not appear to be a BERT model")
            
        # Test sample narrations
        test_narrations = [
            "PAYMENT FOR CONSULTING SERVICES - INVOICE #12345",
            "SETTLEMENT OF LOAN #98765 - FINAL PAYMENT",
            "SALARY PAYMENT FOR APRIL 2025",
            "DIVIDEND PAYMENT TO SHAREHOLDERS Q2 2025",
            "PURCHASE OF IT EQUIPMENT - PO #54321",
            "PAYMENT FOR SOFTWARE LICENSE RENEWAL - ANNUAL SUBSCRIPTION",
            "TUITION FEE PAYMENT FOR FALL SEMESTER",
            "INSURANCE PREMIUM PAYMENT - POLICY #8765432",
            "TAX PAYMENT - Q1 2025",
            "INTERBANK TRANSFER - SETTLEMENT OF SECURITIES TRADE"
        ]
        
        # Limit to the requested number of samples
        test_narrations = test_narrations[:args.samples]
        
        # Test each narration
        for narration in test_narrations:
            print("\n" + "="*80)
            print(f"Narration: {narration}")
            try:
                result = classifier.predict(narration)
                print(f"Predicted purpose code: {result['purpose_code']}")
                print(f"Confidence: {result['confidence']:.4f}")
                print(f"Category purpose code: {result['category_purpose_code']}")
                print(f"Top predictions: {result['top_predictions']}")
                print(f"Processing time: {result['processing_time']:.4f} seconds")
            except Exception as e:
                print(f"Error during prediction: {str(e)}")
        
        return 0
    except Exception as e:
        print(f"Error loading or testing model: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 