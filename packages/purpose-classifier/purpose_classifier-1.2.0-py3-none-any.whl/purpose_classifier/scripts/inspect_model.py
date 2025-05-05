#!/usr/bin/env python3
"""
Script to inspect a model by loading it and using its methods.
This script loads a model and prints information about its properties and methods.
"""

import os
import sys
import argparse
import logging
import time
from pathlib import Path

from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier
from purpose_classifier.config.settings import setup_logging, get_environment
from purpose_classifier.config.path_helper import get_model_file_path

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Inspect a model by loading it and using its methods')
    
    parser.add_argument('--model', type=str, default=None,
                        help='Path to the model file to inspect (default: models/combined_model.pkl)')
    
    parser.add_argument('--env', type=str, default=None,
                        help='Environment (development, test, production)')
    
    return parser.parse_args()

def inspect_model(model_path=None):
    """
    Inspect a model by loading it and using its methods
    
    Args:
        model_path: Path to the model file to inspect
        
    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Determine model path
        if model_path is None:
            model_path = get_model_file_path('combined_model.pkl')
        
        # Initialize classifier
        logger.info("Initializing classifier")
        classifier = LightGBMPurposeClassifier()
        
        # Load the model
        logger.info(f"Loading model from {model_path}")
        start_time = time.time()
        success = classifier.load(model_path)
        load_time = time.time() - start_time
        
        if not success:
            logger.error("Failed to load model")
            print(f"Error: Failed to load model from {model_path}")
            return False
        
        # Print model information
        print("\nModel Information:")
        print(f"Model path: {model_path}")
        print(f"Load time: {load_time:.2f} seconds")
        
        # Print model attributes
        print("\nModel Attributes:")
        for attr_name in dir(classifier):
            if not attr_name.startswith('_') and not callable(getattr(classifier, attr_name)):
                attr_value = getattr(classifier, attr_name)
                if isinstance(attr_value, (str, int, float, bool)):
                    print(f"{attr_name}: {attr_value}")
        
        # Print model components
        print("\nModel Components:")
        if hasattr(classifier, 'model'):
            print(f"Model type: {type(classifier.model).__name__}")
            
            if hasattr(classifier.model, 'feature_importances_'):
                print(f"Number of features: {len(classifier.model.feature_importances_)}")
        
        if hasattr(classifier, 'vectorizer'):
            print(f"Vectorizer type: {type(classifier.vectorizer).__name__}")
            
            if hasattr(classifier.vectorizer, 'get_feature_names_out'):
                try:
                    feature_names = classifier.vectorizer.get_feature_names_out()
                    print(f"Number of features: {len(feature_names)}")
                    print(f"Sample features: {feature_names[:5]}...")
                except Exception as e:
                    print(f"Could not get feature names: {str(e)}")
        
        if hasattr(classifier, 'label_encoder'):
            print(f"Label encoder type: {type(classifier.label_encoder).__name__}")
            
            if hasattr(classifier.label_encoder, 'classes_'):
                print(f"Number of classes: {len(classifier.label_encoder.classes_)}")
                print(f"Classes: {classifier.label_encoder.classes_}")
        
        # Print enhancer information
        print("\nEnhancer Information:")
        if hasattr(classifier, 'enhancer_manager'):
            print(f"Enhancer manager type: {type(classifier.enhancer_manager).__name__}")
            
            if hasattr(classifier.enhancer_manager, 'enhancers'):
                print(f"Number of enhancers: {len(classifier.enhancer_manager.enhancers)}")
                print("Enhancers:")
                for name in classifier.enhancer_manager.enhancers:
                    print(f"  - {name}")
        
        # Test the model with some examples
        print("\nTesting the model with examples:")
        
        test_examples = [
            "PAYMENT FOR PROFESSIONAL TRAINING SERVICES: LEADERSHIP DEVELOPMENT WORKSHOP FOR EXECUTIVES",
            "EDUCATION PAYMENT: TUITION FEES FOR ACADEMIC YEAR 2023-2024 STUDENT ID: 987654",
            "PAYMENT FOR STUDENT HOUSING AT STATE COLLEGE",
            "DIVIDEND PAYMENT FOR SHAREHOLDER ACCOUNT 12345",
            "LOAN REPAYMENT FOR MORTGAGE ACCOUNT 67890",
            "INTERBANK TRANSFER TO NOSTRO ACCOUNT",
            "PAYMENT FOR SOFTWARE LICENSE RENEWAL"
        ]
        
        for example in test_examples:
            start_time = time.time()
            result = classifier.predict(example)
            prediction_time = time.time() - start_time
            
            print(f"\nExample: {example}")
            print(f"Prediction: {result['purpose_code']} with confidence {result['confidence']:.4f}")
            print(f"Category Purpose Code: {result['category_purpose_code']} with confidence {result.get('category_confidence', 0):.4f}")
            print(f"Prediction time: {prediction_time:.4f} seconds")
            
            if 'enhanced' in result and result['enhanced']:
                print(f"Enhanced: YES - {result.get('enhancement_applied', 'Unknown')}")
                print(f"Enhancement type: {result.get('enhancement_type', 'Unknown')}")
                if 'original_purpose_code' in result:
                    print(f"Original purpose code: {result['original_purpose_code']}")
            else:
                print("Enhanced: NO")
            
            if 'enhancer_decisions' in result and result['enhancer_decisions']:
                print("Enhancer decisions:")
                for decision in result['enhancer_decisions']:
                    applied = "✓" if decision.get('applied', False) else "✗"
                    print(f"  {applied} {decision.get('enhancer', 'Unknown')}: {decision.get('old_code', 'Unknown')} -> {decision.get('new_code', 'Unknown')} (conf: {decision.get('confidence', 0.0):.2f})")
                    if 'reason' in decision:
                        print(f"     Reason: {decision.get('reason')}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error inspecting model: {str(e)}")
        print(f"Error inspecting model: {str(e)}")
        return False

def main():
    """Main function"""
    # Parse arguments
    args = parse_arguments()
    
    # Setup environment and logging
    env = args.env or get_environment()
    logger = setup_logging(env)
    logger.info(f"Starting model inspection in {env} environment")
    
    # Inspect the model
    success = inspect_model(args.model)
    
    if success:
        logger.info("Model inspection completed successfully")
        print("\nModel inspection completed successfully")
        return 0
    else:
        logger.error("Model inspection failed")
        print("\nModel inspection failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
