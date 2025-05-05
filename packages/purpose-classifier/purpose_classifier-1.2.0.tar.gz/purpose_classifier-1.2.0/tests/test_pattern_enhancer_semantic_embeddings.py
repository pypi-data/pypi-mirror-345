#!/usr/bin/env python
"""
Test script to check if word embeddings are being used in the pattern enhancer semantic.
"""

import os
import sys
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purpose_classifier.domain_enhancers.pattern_enhancer_semantic import PatternEnhancerSemantic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Test if word embeddings are being used in the pattern enhancer semantic."""
    # Create a pattern enhancer semantic
    enhancer = PatternEnhancerSemantic()
    
    # Check if the matcher has embeddings
    if hasattr(enhancer, 'matcher') and hasattr(enhancer.matcher, 'embeddings') and enhancer.matcher.embeddings:
        logger.info("Word embeddings are loaded in the pattern enhancer semantic")
        
        # Try to calculate semantic similarity
        similarity = enhancer.matcher.semantic_similarity("payment", "transfer")
        logger.info(f"Semantic similarity between 'payment' and 'transfer': {similarity}")
        
        # Try to find similar words
        similar_words = enhancer.matcher.find_similar_words("payment", threshold=0.7)
        logger.info(f"Similar words to 'payment': {similar_words[:5] if similar_words else 'None'}")
        
        # Try to use the context match
        context_patterns = [
            {
                'keywords': ['payment', 'transfer'],
                'proximity': 3,
                'weight': 1.0
            }
        ]
        narration = "This is a payment for the transfer of funds"
        score = enhancer.matcher.context_match(narration, context_patterns)
        logger.info(f"Context match score for '{narration}': {score}")
        
        # Try to use the keywords_in_proximity
        words = enhancer.matcher.tokenize(narration.lower())
        keywords = ['payment', 'transfer']
        in_proximity = enhancer.matcher.keywords_in_proximity(words, keywords, 5)
        logger.info(f"Keywords in proximity for '{narration}': {in_proximity}")
    else:
        logger.error("Word embeddings are NOT loaded in the pattern enhancer semantic")
        if hasattr(enhancer, 'matcher'):
            logger.error(f"Matcher exists: {enhancer.matcher}")
            if hasattr(enhancer.matcher, 'embeddings'):
                logger.error(f"Embeddings attribute exists but is: {enhancer.matcher.embeddings}")
            else:
                logger.error("Embeddings attribute does not exist")
        else:
            logger.error("Matcher does not exist")

if __name__ == "__main__":
    main()
