#!/usr/bin/env python
"""
Improve confidence calibration and top predictions diversity in the purpose code classifier.

This script modifies the combined model to:
1. Improve confidence calibration to avoid overconfidence
2. Enhance top predictions diversity to show more plausible alternatives
3. Adjust the prediction algorithm to consider multiple plausible classifications
"""

import os
import sys
import joblib
import logging
import numpy as np
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def improve_confidence_calibration(model_path='models/combined_model.pkl', output_path=None):
    """
    Improve confidence calibration in the combined model.
    
    Args:
        model_path: Path to the model file
        output_path: Path to save the updated model (defaults to overwriting the input)
        
    Returns:
        bool: True if successful, False otherwise
    """
    if output_path is None:
        output_path = model_path
    
    try:
        # Load the model
        logger.info(f"Loading model from {model_path}")
        model_package = joblib.load(model_path)
        
        # Check if the model package has the expected structure
        if not isinstance(model_package, dict):
            logger.error(f"Invalid model format: expected dictionary, got {type(model_package)}")
            return False
        
        # Debug print of model package keys
        logger.info(f"Model package keys: {list(model_package.keys())}")
        
        # Create backup
        backup_path = f"{model_path}.confidence_bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info(f"Creating backup at {backup_path}")
        joblib.dump(model_package, backup_path)
        
        # Update the enhanced_predict function to improve confidence calibration
        enhanced_predict_code = """
def enhanced_predict(self, narration, confidence, top_predictions, fallback_rules=None):
    \"\"\"
    Enhanced prediction with improved confidence calibration and top predictions diversity.
    
    This function applies domain-specific knowledge and fallback rules to improve
    prediction accuracy and confidence calibration. It also ensures that top predictions
    show more diverse alternatives.
    
    Args:
        narration: Original narration text
        confidence: Original prediction confidence
        top_predictions: List of top predictions with confidences
        fallback_rules: Optional fallback rules
        
    Returns:
        dict: Enhanced prediction with purpose code and confidence
    \"\"\"
    # Apply confidence calibration to avoid overconfidence
    # Use a sigmoid-like function to compress very high confidences
    if confidence > 0.8:
        # Apply a softer curve for high confidences to avoid overconfidence
        calibrated_confidence = 0.8 + (confidence - 0.8) * 0.5
    elif confidence > 0.6:
        # Slight reduction in mid-high range
        calibrated_confidence = 0.6 + (confidence - 0.6) * 0.8
    else:
        # Keep lower confidences as they are
        calibrated_confidence = confidence
    
    # Get the predicted purpose code and top alternatives
    purpose_code = top_predictions[0][0]
    
    # Ensure we have at least 3 predictions in top_predictions
    if len(top_predictions) < 3:
        # If we have fewer than 3, add some placeholder predictions
        while len(top_predictions) < 3:
            # Add a placeholder with very low confidence
            top_predictions.append(('OTHR', 0.01))
    
    # Ensure the confidence gap between top predictions isn't too large
    # This improves the diversity of top predictions
    if len(top_predictions) >= 2:
        top_confidence = top_predictions[0][1]
        second_confidence = top_predictions[1][1]
        
        # If the gap is too large, reduce it
        if top_confidence > 0.7 and second_confidence < 0.1:
            # Boost the second prediction's confidence
            adjusted_second_confidence = min(0.2, second_confidence * 3)
            top_predictions[1] = (top_predictions[1][0], adjusted_second_confidence)
            
            # Also boost the third prediction if it exists
            if len(top_predictions) >= 3:
                third_confidence = top_predictions[2][1]
                if third_confidence < 0.05:
                    adjusted_third_confidence = min(0.1, third_confidence * 3)
                    top_predictions[2] = (top_predictions[2][0], adjusted_third_confidence)
    
    # Apply fallback rules if confidence is low and rules are provided
    if calibrated_confidence < 0.5 and fallback_rules:
        narration_lower = narration.lower()
        
        # Check each fallback rule
        for rule in fallback_rules:
            if 'keywords' in rule and 'purpose_code' in rule:
                # Check if any of the keywords match
                if any(keyword.lower() in narration_lower for keyword in rule['keywords']):
                    # Apply the fallback rule
                    fallback_code = rule['purpose_code']
                    fallback_confidence = rule.get('confidence', 0.6)  # Default fallback confidence
                    
                    # Only apply if the fallback confidence is higher than the calibrated confidence
                    if fallback_confidence > calibrated_confidence:
                        return {
                            'purpose_code': fallback_code,
                            'confidence': fallback_confidence,
                            'enhancement_applied': 'fallback_rule',
                            'original_confidence': confidence,
                            'calibrated_confidence': calibrated_confidence,
                            'top_predictions': top_predictions
                        }
    
    # Return the result with calibrated confidence
    return {
        'purpose_code': purpose_code,
        'confidence': calibrated_confidence,
        'enhancement_applied': 'confidence_calibration',
        'original_confidence': confidence,
        'top_predictions': top_predictions
    }
"""
        
        # Update the model package
        model_package['enhanced_predict'] = enhanced_predict_code
        
        # Add enhancement info
        if 'enhancement_info' not in model_package:
            model_package['enhancement_info'] = {}
        
        model_package['enhancement_info']['last_updated'] = datetime.now().isoformat()
        model_package['enhancement_info']['updates'] = model_package['enhancement_info'].get('updates', []) + [
            "Improved confidence calibration and top predictions diversity"
        ]
        
        # Save the updated model
        logger.info(f"Saving updated model to {output_path}")
        joblib.dump(model_package, output_path)
        
        logger.info("Model updated successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error updating model: {str(e)}")
        return False

def main():
    """Main function to improve confidence calibration"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Improve confidence calibration in the purpose code classifier')
    
    parser.add_argument('--model', type=str, default='models/combined_model.pkl',
                        help='Path to the model file')
    
    parser.add_argument('--output', type=str, default=None,
                        help='Path to save the updated model (defaults to overwriting the input)')
    
    args = parser.parse_args()
    
    # Improve confidence calibration
    success = improve_confidence_calibration(args.model, args.output)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
