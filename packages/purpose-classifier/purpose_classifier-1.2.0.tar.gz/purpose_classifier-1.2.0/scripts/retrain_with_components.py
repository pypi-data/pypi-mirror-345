"""
Retrain the model using the extracted components.

This script retrains the model using the extracted components and the synthetic data.
"""

import os
import sys
import joblib
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
import lightgbm as lgb

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_synthetic_data(data_path):
    """Load the synthetic data from the CSV file."""
    df = pd.read_csv(data_path)
    return df

def retrain_model(components_dir, synthetic_data, output_path):
    """Retrain the model with synthetic data."""
    print(f"Loading components from {components_dir}")

    # Load vectorizer
    vectorizer_path = os.path.join(components_dir, "vectorizer.pkl")
    if not os.path.exists(vectorizer_path):
        print(f"Vectorizer not found at {vectorizer_path}")
        return False

    vectorizer = joblib.load(vectorizer_path)
    print("Vectorizer loaded.")

    # Load label encoder
    label_encoder_path = os.path.join(components_dir, "label_encoder.pkl")
    if os.path.exists(label_encoder_path):
        label_encoder = joblib.load(label_encoder_path)
        print("Label encoder loaded.")
    else:
        label_encoder = None
        print("Label encoder not found.")

    # Prepare the synthetic data
    X = synthetic_data['narration'].values
    y = synthetic_data['purpose_code'].values

    print(f"Training data: {len(X)} samples, {len(np.unique(y))} classes")

    # Transform the narrations using the existing vectorizer
    X_transformed = vectorizer.transform(X)
    print(f"Transformed features shape: {X_transformed.shape}")

    # Convert sparse matrix to dense array for compatibility with some algorithms
    X_transformed = X_transformed.toarray()
    print(f"Converted to dense array. Shape: {X_transformed.shape}")

    # Split the data into training and validation sets
    X_train, X_val, y_train, y_val = train_test_split(
        X_transformed, y, test_size=0.2, random_state=42, stratify=y
    )

    # Create a new LightGBM classifier
    new_model = lgb.LGBMClassifier(
        objective='multiclass',
        num_class=len(np.unique(y)),
        n_estimators=100,
        learning_rate=0.1,
        max_depth=7,
        num_leaves=31,
        random_state=42
    )

    # Train the new model on the synthetic data
    print("Training model...")
    try:
        # Try with callbacks
        from lightgbm.callback import early_stopping
        callbacks = [early_stopping(stopping_rounds=10, verbose=True)]
        new_model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            eval_metric='multi_logloss',
            callbacks=callbacks
        )
    except Exception as e:
        print(f"Error with callbacks: {e}")
        # Simple fit without early stopping
        try:
            new_model.fit(X_train, y_train)
            print("Model trained with simple fit.")
        except Exception as e2:
            print(f"Error with simple fit: {e2}")
            raise RuntimeError(f"Failed to train model: {e2}")

    print("Model trained.")

    # Create a new model package
    model_package = {
        'vectorizer': vectorizer,
        'model': new_model,
        'label_encoder': label_encoder,
        'created_at': datetime.now().isoformat(),
        'params': new_model.get_params(),
        'feature_names': vectorizer.get_feature_names_out() if hasattr(vectorizer, 'get_feature_names_out') else None
    }

    # Load other components if available
    for component in ['fallback_rules', 'enhanced_predict', 'enhanced_category_purpose']:
        component_path = os.path.join(components_dir, f"{component}.pkl")
        if os.path.exists(component_path):
            model_package[component] = joblib.load(component_path)
            print(f"Added {component} to model package.")

    # Save the new model to a new file with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    new_model_path = output_path.replace('.pkl', f'_new_{timestamp}.pkl')
    print(f"Saving new model to {new_model_path}")
    joblib.dump(model_package, new_model_path)
    print("New model saved.")

    return True

if __name__ == "__main__":
    # Find the most recent synthetic data file
    data_dir = "data"
    synthetic_data_files = [f for f in os.listdir(data_dir) if f.startswith("synthetic_data_")]
    if not synthetic_data_files:
        print("No synthetic data files found. Please run generate_synthetic_data.py first.")
        sys.exit(1)

    # Sort by name (which includes timestamp)
    synthetic_data_files.sort(reverse=True)
    synthetic_data_path = os.path.join(data_dir, synthetic_data_files[0])
    print(f"Using synthetic data from {synthetic_data_path}")

    # Load the synthetic data
    synthetic_data = load_synthetic_data(synthetic_data_path)

    # We're not overwriting the existing model, so no backup needed
    existing_model_path = "models/combined_model.pkl"
    print(f"Using existing model at {existing_model_path} for components")

    # Retrain the model
    components_dir = "models/components"
    output_path = "models/combined_model.pkl"

    success = retrain_model(components_dir, synthetic_data, output_path)

    if success:
        print("Model retraining completed successfully.")
    else:
        print("Model retraining failed.")
