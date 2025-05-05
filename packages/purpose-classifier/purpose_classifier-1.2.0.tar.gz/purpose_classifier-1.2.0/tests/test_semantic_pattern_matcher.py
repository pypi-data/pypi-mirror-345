"""
Test suite for the SemanticPatternMatcher class.
"""

import os
import sys
import unittest
import logging

# Add the parent directory to the path so we can import the purpose_classifier package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from purpose_classifier.semantic_pattern_matcher import SemanticPatternMatcher

class TestSemanticPatternMatcher(unittest.TestCase):
    """Test cases for the SemanticPatternMatcher class."""

    def setUp(self):
        """Set up test fixtures."""
        # Try to load real embeddings first
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        embeddings_path = os.path.join(base_dir, 'models', 'word_embeddings.pkl')

        self.matcher = SemanticPatternMatcher(embeddings_path)

        # Check if real embeddings were loaded
        if self.matcher.embeddings:
            logger.info("Real word embeddings loaded successfully in test_semantic_pattern_matcher.py")
            # Try to calculate semantic similarity with real embeddings
            similarity = self.matcher.semantic_similarity("payment", "transfer")
            logger.info(f"Real semantic similarity between 'payment' and 'transfer': {similarity}")

            # Try to find similar words with real embeddings
            similar_words = self.matcher.find_similar_words("payment", threshold=0.7)
            if similar_words:
                logger.info(f"Real similar words to 'payment': {similar_words[:5]}")
        else:
            logger.warning("Real word embeddings not loaded in test_semantic_pattern_matcher.py, tests will be skipped")

            # Set the mock embeddings to the matcher
            self.matcher.embeddings = self.mock_embeddings

        # Skip the rest of the setup if we don't have real embeddings
        if not self.matcher.embeddings:
            self.skipTest("Word embeddings not loaded, skipping test")

    def test_semantic_similarity(self):
        """Test semantic similarity calculation."""
        # Test with words in embeddings
        similarity = self.matcher.semantic_similarity('payment', 'transfer')
        self.assertGreater(similarity, 0.5)  # Should have reasonable similarity

        # Test with words not in embeddings
        similarity = self.matcher.semantic_similarity('payment', 'nonexistentwordxyz')
        self.assertEqual(similarity, 0.0)

        # Test with both words not in embeddings
        similarity = self.matcher.semantic_similarity('nonexistentwordxyz1', 'nonexistentwordxyz2')
        self.assertEqual(similarity, 0.0)

    def test_find_similar_words(self):
        """Test finding similar words."""
        # Test with word in embeddings
        similar_words = self.matcher.find_similar_words('payment', threshold=0.7)
        self.assertGreater(len(similar_words), 0)

        # Test with word not in embeddings
        similar_words = self.matcher.find_similar_words('nonexistentwordxyz')
        self.assertEqual(similar_words, [])

        # Test with different threshold
        similar_words_high = self.matcher.find_similar_words('payment', threshold=0.9)
        similar_words_low = self.matcher.find_similar_words('payment', threshold=0.7)
        self.assertGreaterEqual(len(similar_words_low), len(similar_words_high))

    def test_context_match(self):
        """Test context matching."""
        # Create test context patterns
        context_patterns = [
            {'keywords': ['payment', 'transfer'], 'proximity': 3, 'weight': 1.0},
            {'keywords': ['loan', 'credit'], 'proximity': 2, 'weight': 0.8}
        ]

        # Test with matching text
        text = "This is a payment for the transfer of funds"
        score = self.matcher.context_match(text, context_patterns)
        self.assertGreater(score, 0.0)

        # Test with non-matching text
        text = "This is an unrelated message about something else"
        score = self.matcher.context_match(text, context_patterns)
        self.assertEqual(score, 0.0)

    def test_keywords_in_proximity(self):
        """Test keywords in proximity check."""
        # Test with keywords in proximity
        words = ['this', 'is', 'a', 'payment', 'for', 'transfer']
        keywords = ['payment', 'transfer']
        self.assertTrue(self.matcher.keywords_in_proximity(words, keywords, 3))

        # Test with missing keyword - use a different set of keywords to avoid false positives
        words = ['this', 'is', 'a', 'payment', 'only']
        missing_keywords = ['payment', 'nonexistentwordxyz']
        self.assertFalse(self.matcher.keywords_in_proximity(words, missing_keywords, 3))

    def test_calculate_confidence(self):
        """Test confidence calculation."""
        # Test with equal weights
        match_scores = {'pattern1': 0.8, 'pattern2': 0.6}
        confidence = self.matcher.calculate_confidence(match_scores)
        self.assertAlmostEqual(confidence, 0.7, places=2)

        # Test with custom weights
        weights = {'pattern1': 0.7, 'pattern2': 0.3}
        confidence = self.matcher.calculate_confidence(match_scores, weights)
        self.assertAlmostEqual(confidence, 0.74, places=2)  # (0.8*0.7 + 0.6*0.3) / 1.0

        # Test with empty scores
        confidence = self.matcher.calculate_confidence({})
        self.assertEqual(confidence, 0.0)

    def test_tokenize(self):
        """Test text tokenization."""
        text = "This is a test sentence."
        tokens = self.matcher.tokenize(text)
        self.assertEqual(tokens, ['This', 'is', 'a', 'test', 'sentence', '.'])

    def test_load_word_embeddings_error(self):
        """Test error handling when loading word embeddings."""
        # Test with non-existent file
        result = self.matcher.load_word_embeddings('nonexistent_file.pkl')
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
