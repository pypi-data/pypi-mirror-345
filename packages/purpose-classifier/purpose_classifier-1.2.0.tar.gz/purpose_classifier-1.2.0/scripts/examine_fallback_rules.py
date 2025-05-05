#!/usr/bin/env python
"""
Script to examine the fallback_rules in model files.
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
    parser = argparse.ArgumentParser(description='Examine fallback_rules in model files')
    
    parser.add_argument('--model', type=str, required=True,
                        help='Path to the model file')
    
    parser.add_argument('--output', type=str,
                        help='Path to save the fallback_rules as JSON')
    
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

def examine_fallback_rules(model_data):
    """Examine the fallback_rules in a model"""
    if 'fallback_rules' not in model_data:
        print("No fallback_rules found in the model.")
        return None
    
    fallback_rules = model_data['fallback_rules']
    
    # Print basic info
    print("\nFallback Rules:")
    print("-" * 80)
    
    if isinstance(fallback_rules, dict):
        # Print each key-value pair
        rows = []
        for key, value in fallback_rules.items():
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
    elif isinstance(fallback_rules, list):
        print(f"fallback_rules is a list with {len(fallback_rules)} items.")
        if len(fallback_rules) > 0:
            print("\nSample items:")
            for i, item in enumerate(fallback_rules[:10]):
                if isinstance(item, dict):
                    print(f"\nRule {i}:")
                    sub_rows = []
                    for key, value in item.items():
                        sub_rows.append([key, str(value)])
                    print(tabulate(sub_rows, headers=["Key", "Value"], tablefmt="grid"))
                else:
                    print(f"  Rule {i}: {item}")
            if len(fallback_rules) > 10:
                print(f"  ... and {len(fallback_rules) - 10} more rules")
    else:
        print(f"fallback_rules is of type {type(fallback_rules).__name__}, not a dictionary or list.")
        print(fallback_rules)
    
    return fallback_rules

def main():
    """Main function to examine fallback_rules"""
    args = parse_args()
    
    # Load model
    model_data = load_model(args.model)
    
    if model_data is None:
        print("Error loading model. Exiting.")
        return 1
    
    # Examine fallback_rules
    fallback_rules = examine_fallback_rules(model_data)
    
    # Save fallback_rules if requested
    if args.output and fallback_rules is not None:
        with open(args.output, 'w') as f:
            json.dump(fallback_rules, f, indent=2)
        print(f"\nFallback rules saved to {args.output}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
