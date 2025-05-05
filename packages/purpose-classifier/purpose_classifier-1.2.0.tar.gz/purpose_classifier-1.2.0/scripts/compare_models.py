#!/usr/bin/env python
"""
Script to compare two model files and analyze their differences.
"""

import os
import sys
import joblib
import argparse
import numpy as np
import pandas as pd
from tabulate import tabulate

# Add parent directory to path to import from purpose_classifier
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Compare two model files')
    
    parser.add_argument('--model1', type=str, required=True,
                        help='Path to the first model file')
    
    parser.add_argument('--model2', type=str, required=True,
                        help='Path to the second model file')
    
    parser.add_argument('--output', type=str,
                        help='Path to save the comparison results as CSV')
    
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

def analyze_model(model_data, model_name):
    """Analyze a model and return its properties"""
    analysis = {
        'model_name': model_name,
        'file_size': os.path.getsize(model_name),
        'keys': list(model_data.keys()),
    }
    
    # Check for specific components
    if 'model' in model_data:
        analysis['model_type'] = type(model_data['model']).__name__
        if hasattr(model_data['model'], 'n_estimators'):
            analysis['n_estimators'] = model_data['model'].n_estimators
        if hasattr(model_data['model'], 'feature_importances_'):
            analysis['feature_importances'] = model_data['model'].feature_importances_
    
    if 'vectorizer' in model_data:
        analysis['vectorizer_type'] = type(model_data['vectorizer']).__name__
        if hasattr(model_data['vectorizer'], 'vocabulary_'):
            analysis['vocabulary_size'] = len(model_data['vectorizer'].vocabulary_)
    
    if 'label_encoder' in model_data:
        analysis['label_encoder_type'] = type(model_data['label_encoder']).__name__
        if hasattr(model_data['label_encoder'], 'classes_'):
            analysis['num_classes'] = len(model_data['label_encoder'].classes_)
            analysis['classes'] = model_data['label_encoder'].classes_
    
    if 'params' in model_data:
        analysis['params'] = model_data['params']
    
    if 'training_args' in model_data:
        analysis['training_args'] = model_data['training_args']
    
    if 'created_at' in model_data:
        analysis['created_at'] = model_data['created_at']
    
    if 'fallback_rules' in model_data:
        analysis['has_fallback_rules'] = True
        analysis['num_fallback_rules'] = len(model_data['fallback_rules']) if isinstance(model_data['fallback_rules'], list) else 'N/A'
    else:
        analysis['has_fallback_rules'] = False
    
    if 'enhanced_predict' in model_data:
        analysis['has_enhanced_predict'] = True
    else:
        analysis['has_enhanced_predict'] = False
    
    if 'enhanced_category_purpose' in model_data:
        analysis['has_enhanced_category_purpose'] = True
    else:
        analysis['has_enhanced_category_purpose'] = False
    
    if 'enhancement_info' in model_data:
        analysis['has_enhancement_info'] = True
        analysis['enhancement_info'] = model_data['enhancement_info']
    else:
        analysis['has_enhancement_info'] = False
    
    return analysis

def compare_models(model1_analysis, model2_analysis):
    """Compare two model analyses and return the differences"""
    comparison = {}
    
    # Compare basic properties
    for key in set(model1_analysis.keys()).union(set(model2_analysis.keys())):
        if key in model1_analysis and key in model2_analysis:
            if isinstance(model1_analysis[key], (list, dict, np.ndarray)) or isinstance(model2_analysis[key], (list, dict, np.ndarray)):
                # For complex types, just check if they're equal
                if key == 'feature_importances' and 'feature_importances' in model1_analysis and 'feature_importances' in model2_analysis:
                    # Special handling for feature importances
                    if len(model1_analysis[key]) == len(model2_analysis[key]):
                        # Calculate correlation
                        correlation = np.corrcoef(model1_analysis[key], model2_analysis[key])[0, 1]
                        comparison[f"{key}_correlation"] = correlation
                        
                        # Calculate differences
                        diff = model1_analysis[key] - model2_analysis[key]
                        comparison[f"{key}_max_diff"] = np.max(np.abs(diff))
                        comparison[f"{key}_mean_diff"] = np.mean(np.abs(diff))
                    else:
                        comparison[f"{key}_different_length"] = True
                elif key == 'classes' and 'classes' in model1_analysis and 'classes' in model2_analysis:
                    # Special handling for classes
                    model1_classes = set(model1_analysis[key])
                    model2_classes = set(model2_analysis[key])
                    
                    comparison[f"{key}_only_in_model1"] = list(model1_classes - model2_classes)
                    comparison[f"{key}_only_in_model2"] = list(model2_classes - model1_classes)
                    comparison[f"{key}_common"] = len(model1_classes.intersection(model2_classes))
                else:
                    comparison[key] = "Complex type, equality check: " + str(model1_analysis[key] == model2_analysis[key])
            else:
                # For simple types, store both values
                if model1_analysis[key] == model2_analysis[key]:
                    comparison[key] = f"Same: {model1_analysis[key]}"
                else:
                    comparison[key] = f"Different: {model1_analysis[key]} vs {model2_analysis[key]}"
        elif key in model1_analysis:
            comparison[key] = f"Only in model1: {model1_analysis[key]}"
        else:
            comparison[key] = f"Only in model2: {model2_analysis[key]}"
    
    return comparison

def main():
    """Main function to compare models"""
    args = parse_args()
    
    # Load models
    model1_data = load_model(args.model1)
    model2_data = load_model(args.model2)
    
    if model1_data is None or model2_data is None:
        print("Error loading models. Exiting.")
        return 1
    
    # Analyze models
    model1_analysis = analyze_model(model1_data, args.model1)
    model2_analysis = analyze_model(model2_data, args.model2)
    
    # Compare models
    comparison = compare_models(model1_analysis, model2_analysis)
    
    # Print comparison
    print("\nModel Comparison:")
    print("-" * 80)
    
    # Print in a more readable format
    rows = []
    for key, value in comparison.items():
        rows.append([key, str(value)])
    
    print(tabulate(rows, headers=["Property", "Comparison"], tablefmt="grid"))
    
    # Save comparison if requested
    if args.output:
        df = pd.DataFrame(rows, columns=["Property", "Comparison"])
        df.to_csv(args.output, index=False)
        print(f"\nComparison saved to {args.output}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
