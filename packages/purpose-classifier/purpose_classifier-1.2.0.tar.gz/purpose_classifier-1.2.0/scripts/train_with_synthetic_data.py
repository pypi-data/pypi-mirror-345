#!/usr/bin/env python
"""
Train the purpose code classifier with synthetic data.

This script trains the purpose code classifier with synthetic data for problematic purpose codes.
"""

import os
import sys
import json
import argparse
import pandas as pd
import joblib
from pathlib import Path

# Add the parent directory to the path so we can import the purpose_classifier package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier

def load_purpose_codes(filepath):
    """Load purpose codes from JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Failed to load purpose codes from {filepath}: {str(e)}")
        return {}

def load_synthetic_data(filepath):
    """Load synthetic data from CSV file"""
    try:
        df = pd.read_csv(filepath)
        return df
    except Exception as e:
        print(f"Failed to load synthetic data from {filepath}: {str(e)}")
        return None

def update_model_with_synthetic_data(model_path, synthetic_data_path, output_model_path=None):
    """Update the model with synthetic data"""
    # Load the model
    print(f"Loading model from {model_path}")
    model_package = joblib.load(model_path)

    # Load synthetic data
    print(f"Loading synthetic data from {synthetic_data_path}")
    synthetic_data = load_synthetic_data(synthetic_data_path)
    if synthetic_data is None:
        print("Failed to load synthetic data")
        return False

    # Extract narrations and purpose codes
    narrations = synthetic_data['narration'].tolist()
    purpose_codes = synthetic_data['purpose_code'].tolist()

    print(f"Loaded {len(narrations)} synthetic narrations")

    # Extract model components
    vectorizer = model_package['vectorizer']
    label_encoder = model_package['label_encoder']

    # Preprocess narrations
    from purpose_classifier.lightgbm_classifier import TextPreprocessor
    preprocessor = TextPreprocessor()
    processed_narrations = [preprocessor.preprocess(narration) for narration in narrations]

    # Transform narrations to features
    features = vectorizer.transform(processed_narrations)

    # Transform purpose codes to labels
    labels = label_encoder.transform(purpose_codes)

    # Update the model
    print("Updating the model with synthetic data")

    # LightGBM Booster objects don't have a fit method, we need to create a new model
    import lightgbm as lgb

    # Create a LightGBM dataset
    lgb_train = lgb.Dataset(features, labels)

    # Get the original parameters
    params = model_package.get('params', {})

    # Train a new model
    print("Training a new model with the synthetic data")

    # Set verbosity in params
    if 'verbose' not in params:
        params['verbose'] = 1

    # Train the model
    new_model = lgb.train(params, lgb_train)

    # Update the model package
    model_package['model'] = new_model

    # Save the updated model
    if output_model_path is None:
        output_model_path = model_path

    print(f"Saving updated model to {output_model_path}")
    joblib.dump(model_package, output_model_path)

    print("Model updated successfully")
    return True

def main():
    parser = argparse.ArgumentParser(description='Train the purpose code classifier with synthetic data')
    parser.add_argument('--model', type=str, default='models/combined_model.pkl', help='Path to the model file')
    parser.add_argument('--synthetic-data', type=str, default='data/synthetic_data.csv', help='Path to the synthetic data file')
    parser.add_argument('--output-model', type=str, help='Path to save the updated model')

    args = parser.parse_args()

    # Update the model with synthetic data
    update_model_with_synthetic_data(args.model, args.synthetic_data, args.output_model)

if __name__ == '__main__':
    main()
