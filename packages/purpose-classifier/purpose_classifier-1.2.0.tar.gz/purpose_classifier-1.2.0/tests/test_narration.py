#!/usr/bin/env python
"""
Test script to classify a narration and output the purpose code and category purpose code.
"""

import sys
import os
import argparse

# Add parent directory to path to import from purpose_classifier
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Classify a narration and output purpose codes')
    parser.add_argument('narration', type=str, help='The narration text to classify')
    parser.add_argument('--model', type=str, default='models/combined_model.pkl',
                        help='Path to the model file (default: models/combined_model.pkl)')
    parser.add_argument('--message-type', type=str, choices=['MT103', 'MT202', 'MT202COV', 'MT205', 'MT205COV'],
                        help='Optional SWIFT message type')
    args = parser.parse_args()

    # Initialize the classifier
    print(f"Loading model from {args.model}...")
    classifier = LightGBMPurposeClassifier(model_path=args.model)
    
    # Classify the narration
    print(f"\nClassifying narration: \"{args.narration}\"")
    if args.message_type:
        print(f"Using message type: {args.message_type}")
        result = classifier.predict(args.narration, message_type=args.message_type)
    else:
        result = classifier.predict(args.narration)
    
    # Print the results
    print("\nResults:")
    print(f"Purpose Code: {result['purpose_code']} (Confidence: {result['confidence']:.4f})")
    print(f"Category Purpose Code: {result['category_purpose_code']} (Confidence: {result.get('category_confidence', 0):.4f})")
    
    # Print top predictions
    print("\nTop Predictions:")
    for code, confidence in result.get('top_predictions', []):
        print(f"  {code}: {confidence:.4f}")
    
    # Print processing time
    print(f"\nProcessing Time: {result.get('processing_time', 0):.4f} seconds")

if __name__ == "__main__":
    main()
