#!/usr/bin/env python
"""
Script to create word embeddings for the purpose code classifier.

This script downloads a pre-trained word embeddings model from gensim-data
and saves it in a format that can be loaded by the SemanticPatternMatcher.
"""

import os
import sys
import logging
import pickle
import gensim.downloader as api
from gensim.models import KeyedVectors

# Add the parent directory to the path so we can import the purpose_classifier package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purpose_classifier.config.config import BASE_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_word_embeddings(model_name='glove-wiki-gigaword-100', output_path=None):
    """
    Create word embeddings for the purpose code classifier.
    
    Args:
        model_name: Name of the pre-trained model to download
        output_path: Path to save the word embeddings
    """
    if output_path is None:
        output_path = os.path.join(BASE_DIR, 'models', 'word_embeddings.pkl')
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    logger.info(f"Downloading pre-trained word embeddings model: {model_name}")
    model = api.load(model_name)
    
    logger.info(f"Saving word embeddings to: {output_path}")
    with open(output_path, 'wb') as f:
        pickle.dump(model, f)
    
    logger.info(f"Word embeddings saved successfully with {len(model.key_to_index)} words")
    return output_path

def list_available_models():
    """List available pre-trained models."""
    logger.info("Available pre-trained models:")
    for model_name in api.info()['models'].keys():
        logger.info(f"- {model_name}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Create word embeddings for the purpose code classifier.')
    parser.add_argument('--model', type=str, default='glove-wiki-gigaword-100',
                        help='Name of the pre-trained model to download')
    parser.add_argument('--output', type=str, default=None,
                        help='Path to save the word embeddings')
    parser.add_argument('--list-models', action='store_true',
                        help='List available pre-trained models')
    
    args = parser.parse_args()
    
    if args.list_models:
        list_available_models()
    else:
        create_word_embeddings(args.model, args.output)
