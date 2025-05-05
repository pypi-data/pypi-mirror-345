#!/usr/bin/env python3
"""
Script to inspect a model by loading it and using its methods.
This script loads a model and prints information about its properties and methods.
"""

import os
import sys
import argparse
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import classifier and configuration
from models.classifier import MultiMTClassifier
from config.config import setup_logging, get_environment

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Inspect a model by loading it and using its methods')
    
    parser.add_argument('--model', type=str, required=True,
                        help='Path to the model file to inspect')
    
    parser.add_argument('--env', type=str, default=None,
                        help='Environment (development, test, production)')
    
    return parser.parse_args()

def inspect_model(model_path):
    """
    Inspect a model by loading it and using its methods
    
    Args:
        model_path: Path to the model file to inspect
        
    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize classifier
        logger.info("Initializing classifier")
        classifier = MultiMTClassifier(
            environment='development',
            use_education_enhancer=True,
            auto_education_enhance=True
        )
        
        # Load the model
        logger.info(f"Loading model from {model_path}")
        classifier.load(model_path)
        
        # Print model information
        print("\nModel Information:")
        print(f"Model version: {classifier.model_version}")
        print(f"Use education enhancer: {classifier.use_education_enhancer}")
        print(f"Auto education enhance: {classifier.auto_education_enhance}")
        print(f"Use tech enhancer: {classifier.use_tech_enhancer}")
        print(f"Auto tech enhance: {classifier.auto_tech_enhance}")
        
        # Print purpose model information
        if classifier.purpose_model:
            print("\nPurpose Model Information:")
            print(f"Type: {type(classifier.purpose_model).__name__}")
            
            if hasattr(classifier.purpose_model, 'classes_'):
                print(f"Classes: {classifier.purpose_model.classes_}")
            
            if hasattr(classifier.purpose_model, 'estimators_'):
                print(f"Number of estimators: {len(classifier.purpose_model.estimators_)}")
                print("Estimator types:")
                for i, estimator in enumerate(classifier.purpose_model.estimators_):
                    print(f"{i+1}. {type(estimator).__name__}")
        
        # Print category purpose model information
        if classifier.category_purpose_model:
            print("\nCategory Purpose Model Information:")
            print(f"Type: {type(classifier.category_purpose_model).__name__}")
            
            if hasattr(classifier.category_purpose_model, 'classes_'):
                print(f"Classes: {classifier.category_purpose_model.classes_}")
        
        # Print feature extractor information
        if classifier.feature_extractor:
            print("\nFeature Extractor Information:")
            print(f"Type: {type(classifier.feature_extractor).__name__}")
            
            if hasattr(classifier.feature_extractor, 'max_features'):
                print(f"Max features: {classifier.feature_extractor.max_features}")
            
            if hasattr(classifier.feature_extractor, 'ngram_range'):
                print(f"N-gram range: {classifier.feature_extractor.ngram_range}")
        
        # Test the model with some examples
        print("\nTesting the model with examples:")
        
        test_examples = [
            "PAYMENT FOR PROFESSIONAL TRAINING SERVICES: LEADERSHIP DEVELOPMENT WORKSHOP FOR EXECUTIVES",
            "EDUCATION PAYMENT: TUITION FEES FOR ACADEMIC YEAR 2023-2024 STUDENT ID: 987654",
            "PAYMENT FOR STUDENT HOUSING AT STATE COLLEGE"
        ]
        
        for example in test_examples:
            result = classifier.predict(example)
            print(f"\nExample: {example}")
            print(f"Prediction: {result['purpose_code']} ({result['purpose_description']}) with confidence {result['confidence']:.4f}")
            
            if 'education_score' in result:
                print(f"Education score: {result['education_score']}")
                print(f"Education keywords: {result['education_keywords']}")
            
            if 'enhancement_applied' in result:
                print(f"Enhancement applied: {result['enhancement_applied']}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error inspecting model: {str(e)}")
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
