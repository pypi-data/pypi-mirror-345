"""
Extract components from the existing model.

This script extracts the vectorizer and other components from the existing model
to be used in the retraining process.
"""

import os
import sys
import pickle
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def extract_model_components(model_path, output_dir):
    """Extract components from the model."""
    print(f"Extracting components from {model_path}")
    
    # Try loading with joblib first
    try:
        print("Trying to load with joblib...")
        model = joblib.load(model_path)
        print(f"Model loaded with joblib. Type: {type(model)}")
    except Exception as e:
        print(f"Error loading with joblib: {e}")
        try:
            print("Trying to load with pickle...")
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            print(f"Model loaded with pickle. Type: {type(model)}")
        except Exception as e2:
            print(f"Error loading with pickle: {e2}")
            print("Failed to load model.")
            return False
    
    # Extract components based on model type
    if isinstance(model, dict):
        print("Model is a dictionary.")
        components = model
    else:
        print("Model is an object.")
        # Try to extract components from object attributes
        components = {}
        for attr in ['vectorizer', 'model', 'label_encoder']:
            if hasattr(model, attr):
                components[attr] = getattr(model, attr)
                print(f"Extracted {attr} from model object.")
    
    # Check if we have the necessary components
    if 'vectorizer' not in components:
        print("Vectorizer not found in model.")
        return False
    
    # Save components
    os.makedirs(output_dir, exist_ok=True)
    
    for name, component in components.items():
        output_path = os.path.join(output_dir, f"{name}.pkl")
        try:
            joblib.dump(component, output_path)
            print(f"Saved {name} to {output_path}")
        except Exception as e:
            print(f"Error saving {name}: {e}")
    
    return True

if __name__ == "__main__":
    model_path = "models/combined_model.pkl"
    output_dir = "models/components"
    
    success = extract_model_components(model_path, output_dir)
    
    if success:
        print("Model components extracted successfully.")
    else:
        print("Failed to extract model components.")
