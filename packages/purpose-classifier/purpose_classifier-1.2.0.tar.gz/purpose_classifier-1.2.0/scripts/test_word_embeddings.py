"""
Test script for word embeddings.

This script tests the word embeddings functionality in the purpose classifier.
"""

import os
import sys
import logging
import argparse

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purpose_classifier.semantic_pattern_matcher import SemanticPatternMatcher

def setup_logging(level=logging.INFO):
    """Set up logging configuration."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

def test_word_embeddings(embeddings_path=None, debug=False):
    """Test word embeddings functionality."""
    # Set up logging
    log_level = logging.DEBUG if debug else logging.INFO
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("Testing word embeddings...")
    
    # Initialize the semantic pattern matcher
    matcher = SemanticPatternMatcher(embeddings_path)
    
    # Check if embeddings were loaded
    if matcher.embeddings is None:
        logger.error("Word embeddings not loaded!")
        return False
    
    # Test semantic similarity
    test_pairs = [
        ('payment', 'transfer'),
        ('salary', 'wage'),
        ('dividend', 'payment'),
        ('education', 'tuition'),
        ('loan', 'credit'),
        ('tax', 'government'),
        ('service', 'consulting'),
        ('goods', 'merchandise')
    ]
    
    logger.info("Testing semantic similarity between word pairs:")
    for word1, word2 in test_pairs:
        similarity = matcher.semantic_similarity(word1, word2)
        logger.info(f"Similarity between '{word1}' and '{word2}': {similarity:.4f}")
    
    # Test semantic similarity with terms
    test_texts = [
        ('salary payment for employees', ['wage', 'payroll', 'compensation']),
        ('dividend distribution to shareholders', ['dividend', 'shareholder', 'payment']),
        ('educational expenses for university', ['education', 'tuition', 'school']),
        ('loan repayment installment', ['loan', 'credit', 'mortgage']),
        ('tax payment to government', ['tax', 'government', 'authority']),
        ('consulting services invoice', ['service', 'consulting', 'professional']),
        ('purchase of office supplies', ['goods', 'merchandise', 'product'])
    ]
    
    logger.info("\nTesting semantic similarity with terms:")
    for text, terms in test_texts:
        similarity = matcher.semantic_similarity_with_terms(text, terms)
        logger.info(f"Similarity between '{text}' and {terms}: {similarity:.4f}")
    
    # Test keywords in proximity
    test_proximity = [
        ('salary payment for employees in the company', ['salary', 'payment'], 3),
        ('dividend distribution to shareholders quarterly', ['dividend', 'shareholders'], 3),
        ('educational expenses for university students', ['educational', 'university'], 3),
        ('loan repayment installment for mortgage', ['loan', 'mortgage'], 3),
        ('tax payment to government authority', ['tax', 'government'], 3),
        ('consulting services invoice for professional work', ['consulting', 'professional'], 4),
        ('purchase of office supplies for the company', ['purchase', 'supplies'], 3)
    ]
    
    logger.info("\nTesting keywords in proximity:")
    for text, keywords, max_distance in test_proximity:
        words = matcher.tokenize(text.lower())
        result = matcher.keywords_in_proximity(words, keywords, max_distance)
        logger.info(f"Keywords {keywords} in proximity {max_distance} in '{text}': {result}")
    
    logger.info("\nWord embeddings test completed successfully!")
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test word embeddings functionality')
    parser.add_argument('--embeddings', help='Path to word embeddings file')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()
    
    test_word_embeddings(args.embeddings, args.debug)
