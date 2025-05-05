"""
Merge the newly trained model with the existing model.

This script merges the newly trained model with the existing model to create a more robust model.
"""

import os
import sys
import joblib
import argparse
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def list_available_models():
    """List all available models in the models directory."""
    models_dir = "models"
    model_files = [f for f in os.listdir(models_dir) if f.endswith('.pkl')]
    
    print("Available models:")
    for i, model_file in enumerate(model_files):
        model_path = os.path.join(models_dir, model_file)
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        modified_time = datetime.fromtimestamp(os.path.getmtime(model_path)).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i+1}. {model_file} ({size_mb:.2f} MB, modified: {modified_time})")
    
    return model_files

def merge_models(existing_model_path, new_model_path, output_path):
    """Merge the existing model with the new model."""
    print(f"Loading existing model from {existing_model_path}")
    existing_model = joblib.load(existing_model_path)
    
    print(f"Loading new model from {new_model_path}")
    new_model = joblib.load(new_model_path)
    
    # Create a merged model
    print("Merging models...")
    
    # Start with the existing model as the base
    merged_model = existing_model.copy() if isinstance(existing_model, dict) else existing_model
    
    # Update with components from the new model
    if isinstance(new_model, dict) and isinstance(merged_model, dict):
        # Both are dictionaries, merge them
        for key, value in new_model.items():
            if key == 'model':
                # Use the new model
                merged_model[key] = value
                print(f"Using new '{key}' component")
            elif key not in merged_model:
                # Add new components
                merged_model[key] = value
                print(f"Added new '{key}' component")
    elif isinstance(new_model, dict):
        # New model is a dictionary, existing model is an object
        # Convert existing model to dictionary
        merged_model = {
            'vectorizer': getattr(existing_model, 'vectorizer', None),
            'model': getattr(existing_model, 'model', None),
            'label_encoder': getattr(existing_model, 'label_encoder', None)
        }
        
        # Update with components from the new model
        for key, value in new_model.items():
            if key == 'model':
                # Use the new model
                merged_model[key] = value
                print(f"Using new '{key}' component")
            elif key not in merged_model or merged_model[key] is None:
                # Add new components
                merged_model[key] = value
                print(f"Added new '{key}' component")
    elif hasattr(new_model, 'model') and hasattr(merged_model, 'model'):
        # Both are objects, update the model component
        merged_model.model = new_model.model
        print("Using new 'model' component")
    else:
        print("Warning: Could not merge models due to incompatible types")
        return False
    
    # Add metadata
    if isinstance(merged_model, dict):
        merged_model['merged_at'] = datetime.now().isoformat()
        merged_model['merged_from'] = {
            'existing_model': os.path.basename(existing_model_path),
            'new_model': os.path.basename(new_model_path)
        }
    
    # Backup the existing model
    backup_dir = "models/backup"
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, f"combined_model_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl")
    
    print(f"Backing up existing model to {backup_path}")
    import shutil
    shutil.copy2(existing_model_path, backup_path)
    
    # Save the merged model
    print(f"Saving merged model to {output_path}")
    joblib.dump(merged_model, output_path)
    print("Merged model saved.")
    
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Merge models')
    parser.add_argument('--list', action='store_true', help='List available models')
    parser.add_argument('--existing', type=str, help='Path to the existing model')
    parser.add_argument('--new', type=str, help='Path to the new model')
    parser.add_argument('--output', type=str, default='models/combined_model.pkl', help='Path to save the merged model')
    
    args = parser.parse_args()
    
    if args.list:
        list_available_models()
        return
    
    if not args.existing or not args.new:
        # List available models and prompt for selection
        model_files = list_available_models()
        
        if not args.existing:
            existing_idx = int(input("Enter the number of the existing model: ")) - 1
            args.existing = os.path.join("models", model_files[existing_idx])
        
        if not args.new:
            new_idx = int(input("Enter the number of the new model: ")) - 1
            args.new = os.path.join("models", model_files[new_idx])
    
    print(f"Existing model: {args.existing}")
    print(f"New model: {args.new}")
    print(f"Output path: {args.output}")
    
    # Confirm
    confirm = input("Proceed with merging? (y/n): ")
    if confirm.lower() != 'y':
        print("Merge cancelled.")
        return
    
    # Merge models
    success = merge_models(args.existing, args.new, args.output)
    
    if success:
        print("Models merged successfully.")
    else:
        print("Failed to merge models.")

if __name__ == "__main__":
    main()
