#!/usr/bin/env python
"""
Script to fix confidence thresholds in the purpose classifier.

This script adjusts the confidence thresholds in the classifier and enhancers
to allow enhancers to correct high-confidence errors.
"""

import os
import sys
import logging

# Add the parent directory to the path so we can import the purpose_classifier package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purpose_classifier.domain_enhancers.enhancer_manager import EnhancerManager
from purpose_classifier.classifier import PurposeCodeClassifier
from purpose_classifier.config.settings import MODEL_SETTINGS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def fix_confidence_thresholds():
    """Fix confidence thresholds in the classifier and enhancers."""
    logger.info("Fixing confidence thresholds in the classifier and enhancers")
    
    # 1. Adjust confidence thresholds in the classifier
    classifier = PurposeCodeClassifier()
    
    # Lower the high confidence threshold to allow enhancers to correct more predictions
    original_high_threshold = classifier.confidence_thresholds["high"]
    classifier.confidence_thresholds["high"] = 0.85  # Increased from 0.65 to 0.85
    
    logger.info(f"Adjusted classifier high confidence threshold from {original_high_threshold} to {classifier.confidence_thresholds['high']}")
    
    # 2. Adjust confidence thresholds in the enhancer manager
    enhancer_manager = EnhancerManager()
    
    # Lower the confidence thresholds for all priority levels
    original_thresholds = enhancer_manager.confidence_thresholds.copy()
    enhancer_manager.confidence_thresholds = {
        'highest': 0.65,  # Reduced from 0.75 to 0.65
        'high': 0.70,     # Reduced from 0.80 to 0.70
        'medium': 0.75,   # Reduced from 0.85 to 0.75
        'low': 0.80       # Reduced from 0.90 to 0.80
    }
    
    logger.info(f"Adjusted enhancer manager confidence thresholds from {original_thresholds} to {enhancer_manager.confidence_thresholds}")
    
    # 3. Update MODEL_SETTINGS
    original_min_confidence = MODEL_SETTINGS['min_confidence']
    MODEL_SETTINGS['min_confidence'] = 0.40  # Reduced from 0.60 to 0.40
    
    logger.info(f"Adjusted MODEL_SETTINGS min_confidence from {original_min_confidence} to {MODEL_SETTINGS['min_confidence']}")
    
    # 4. Save the updated settings
    # Note: This is a temporary fix for testing. In production, these changes should be made in the actual code files.
    logger.info("Confidence thresholds have been adjusted for testing")
    logger.info("To make these changes permanent, update the following files:")
    logger.info("1. purpose_classifier/classifier.py")
    logger.info("2. purpose_classifier/domain_enhancers/enhancer_manager.py")
    logger.info("3. purpose_classifier/config/settings.py")

if __name__ == "__main__":
    fix_confidence_thresholds()
