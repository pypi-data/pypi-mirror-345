#!/usr/bin/env python
"""
Script to examine the enhancement_info in model files.
"""

import os
import sys
import joblib
import argparse
import json
from tabulate import tabulate

# Add parent directory to path to import from purpose_classifier
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Examine enhancement_info in model files')
    
    parser.add_argument('--model', type=str, required=True,
                        help='Path to the model file')
    
    parser.add_argument('--output', type=str,
                        help='Path to save the enhancement_info as JSON')
    
    return parser.parse_args()

def load_model(model_path):
    """Load a model from a file"""
    try:
        print(f"Loading model from {model_path}")
        model_data = joblib.load(model_path)
        print(f"Successfully loaded model from {model_path}")
        return model_data
    except Exception as e:
        print(f"Error loading model from {model_path}: {str(e)}")
        return None

def examine_enhancement_info(model_data):
    """Examine the enhancement_info in a model"""
    if 'enhancement_info' not in model_data:
        print("No enhancement_info found in the model.")
        return None
    
    enhancement_info = model_data['enhancement_info']
    
    # Print basic info
    print("\nEnhancement Info:")
    print("-" * 80)
    
    if isinstance(enhancement_info, dict):
        # Print each key-value pair
        rows = []
        for key, value in enhancement_info.items():
            if isinstance(value, (dict, list)):
                rows.append([key, f"Complex type: {type(value).__name__}"])
                
                # Print details for complex types
                if isinstance(value, dict):
                    print(f"\nDetails for {key}:")
                    sub_rows = []
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, (dict, list)):
                            sub_rows.append([sub_key, f"Complex type: {type(sub_value).__name__}"])
                        else:
                            sub_rows.append([sub_key, str(sub_value)])
                    print(tabulate(sub_rows, headers=["Key", "Value"], tablefmt="grid"))
                elif isinstance(value, list) and len(value) > 0:
                    print(f"\nSample items from {key} (total: {len(value)}):")
                    for i, item in enumerate(value[:5]):
                        print(f"  Item {i}: {item}")
                    if len(value) > 5:
                        print(f"  ... and {len(value) - 5} more items")
            else:
                rows.append([key, str(value)])
        
        print(tabulate(rows, headers=["Key", "Value"], tablefmt="grid"))
    else:
        print(f"enhancement_info is of type {type(enhancement_info).__name__}, not a dictionary.")
        print(enhancement_info)
    
    return enhancement_info

def main():
    """Main function to examine enhancement_info"""
    args = parse_args()
    
    # Load model
    model_data = load_model(args.model)
    
    if model_data is None:
        print("Error loading model. Exiting.")
        return 1
    
    # Examine enhancement_info
    enhancement_info = examine_enhancement_info(model_data)
    
    # Save enhancement_info if requested
    if args.output and enhancement_info is not None:
        with open(args.output, 'w') as f:
            json.dump(enhancement_info, f, indent=2)
        print(f"\nEnhancement info saved to {args.output}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
