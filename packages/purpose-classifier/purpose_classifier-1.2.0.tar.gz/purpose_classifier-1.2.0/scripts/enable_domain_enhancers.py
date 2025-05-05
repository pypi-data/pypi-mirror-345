#!/usr/bin/env python3
"""
Script to enable the domain enhancers in the main configuration.
This script updates the model configuration to enable the services, trade, and interbank domain enhancers.
"""

import os
import sys
import pickle
import logging
from datetime import datetime

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the classifier
from models.classifier import MultiMTClassifier

def main():
    """
    Main function to enable domain enhancers
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('enable_domain_enhancers')
    
    # Path to the model file
    model_path = os.path.join(parent_dir, 'models', 'final_classifier.pkl')
    
    logger.info(f"Loading model from {model_path}")
    
    # Load the model
    classifier = MultiMTClassifier(
        environment='development',
        use_education_enhancer=True,
        auto_education_enhance=True,
        use_services_enhancer=True,
        auto_services_enhance=True,
        use_trade_enhancer=True,
        auto_trade_enhance=True,
        use_interbank_enhancer=True,
        auto_interbank_enhance=True
    )
    
    # Load the model
    classifier.load(custom_path=model_path)
    
    # Save the model with the domain enhancers enabled
    logger.info(f"Saving model with domain enhancers enabled to {model_path}")
    classifier.save(custom_path=model_path)
    
    logger.info("Domain enhancers enabled successfully")
    
    # Print model information
    logger.info(f"Model version: {classifier.model_version}")
    logger.info(f"Education enhancer: {classifier.use_education_enhancer}")
    logger.info(f"Auto education enhance: {classifier.auto_education_enhance}")
    logger.info(f"Services enhancer: {classifier.use_services_enhancer}")
    logger.info(f"Auto services enhance: {classifier.auto_services_enhance}")
    logger.info(f"Trade enhancer: {classifier.use_trade_enhancer}")
    logger.info(f"Auto trade enhance: {classifier.auto_trade_enhance}")
    logger.info(f"Interbank enhancer: {classifier.use_interbank_enhancer}")
    logger.info(f"Auto interbank enhance: {classifier.auto_interbank_enhance}")

if __name__ == "__main__":
    main()
