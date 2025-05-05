#!/usr/bin/env python3
"""
Rename BERT Model Script

This script renames the BERT model to combined_model.pkl and renames the existing
combined_model.pkl to combined_model_old.pkl to maintain backward compatibility.
"""

import os
import sys
import shutil
import logging
import argparse
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rename_bert_model.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('model_renamer')

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Rename BERT model to combined_model.pkl')
    
    parser.add_argument('--bert-model', type=str, default='models/bert_model.pkl',
                        help='Path to the BERT model')
    
    parser.add_argument('--combined-model', type=str, default='models/combined_model.pkl',
                        help='Path to the existing combined model')
    
    parser.add_argument('--old-model', type=str, default='models/combined_model_old.pkl',
                        help='Path to save the old combined model')
    
    return parser.parse_args()

def rename_models(bert_model_path, combined_model_path, old_model_path):
    """
    Rename the models to maintain backward compatibility.
    
    Args:
        bert_model_path: Path to the BERT model
        combined_model_path: Path to the existing combined model
        old_model_path: Path to save the old combined model
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Renaming models:")
    logger.info(f"  BERT model: {bert_model_path}")
    logger.info(f"  Combined model: {combined_model_path}")
    logger.info(f"  Old model: {old_model_path}")
    
    try:
        # Check if the BERT model exists
        if not os.path.exists(bert_model_path):
            logger.error(f"BERT model not found at {bert_model_path}")
            return False
        
        # Check if the combined model exists
        if not os.path.exists(combined_model_path):
            logger.warning(f"Combined model not found at {combined_model_path}")
            logger.info(f"Renaming BERT model to combined model")
            shutil.copy2(bert_model_path, combined_model_path)
            return True
        
        # Rename the existing combined model to old model
        logger.info(f"Renaming existing combined model to old model")
        shutil.copy2(combined_model_path, old_model_path)
        
        # Rename the BERT model to combined model
        logger.info(f"Renaming BERT model to combined model")
        shutil.copy2(bert_model_path, combined_model_path)
        
        logger.info(f"Models renamed successfully")
        return True
    except Exception as e:
        logger.error(f"Error renaming models: {str(e)}")
        return False

def main():
    """Main function"""
    args = parse_args()
    
    # Log arguments
    logger.info(f"Renaming models with the following parameters:")
    for arg, value in vars(args).items():
        logger.info(f"  {arg}: {value}")
    
    # Rename models
    success = rename_models(args.bert_model, args.combined_model, args.old_model)
    
    if success:
        logger.info("Model renaming completed successfully")
        return 0
    else:
        logger.error("Model renaming failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
