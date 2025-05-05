#!/usr/bin/env python
"""
Test script to check if word embeddings can be loaded correctly.
"""

import os
import sys
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purpose_classifier.semantic_pattern_matcher import SemanticPatternMatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Test loading word embeddings."""
    # Get the absolute path to the word embeddings file
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    embeddings_path = os.path.join(base_dir, 'models', 'word_embeddings.pkl')
    
    # Check if the file exists
    if not os.path.exists(embeddings_path):
        logger.error(f"Word embeddings file not found at {embeddings_path}")
        return
    
    # Try to load the word embeddings
    logger.info(f"Attempting to load word embeddings from {embeddings_path}")
    matcher = SemanticPatternMatcher(embeddings_path)
    
    # Check if embeddings were loaded successfully
    if matcher.embeddings:
        logger.info("Word embeddings loaded successfully")
        # Try to calculate semantic similarity
        similarity = matcher.semantic_similarity("payment", "transfer")
        logger.info(f"Semantic similarity between 'payment' and 'transfer': {similarity}")
    else:
        logger.error("Failed to load word embeddings")

if __name__ == "__main__":
    main()
