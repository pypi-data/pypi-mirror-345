import unittest
import logging
from purpose_classifier.domain_enhancers.court_payment_enhancer_semantic import CourtPaymentEnhancerSemantic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestCourtPaymentEnhancerSemantic(unittest.TestCase):
    """Test cases for the CourtPaymentEnhancerSemantic class."""

    def setUp(self):
        """Set up the test environment."""
        self.enhancer = CourtPaymentEnhancerSemantic()

        # Check if word embeddings are loaded
        if hasattr(self.enhancer, 'matcher') and hasattr(self.enhancer.matcher, 'embeddings') and self.enhancer.matcher.embeddings:
            logger.info("Word embeddings are loaded in the court payment enhancer semantic")
            # Try to calculate semantic similarity
            similarity = self.enhancer.matcher.semantic_similarity("court", "legal")
            logger.info(f"Semantic similarity between 'court' and 'legal': {similarity}")

            # Try to find similar words
            similar_words = self.enhancer.matcher.find_similar_words("court", threshold=0.7)
            if similar_words:
                logger.info(f"Similar words to 'court': {similar_words[:5]}")
        else:
            logger.error("Word embeddings are NOT loaded in the court payment enhancer semantic")

    def test_court_payment_detection(self):
        """Test court payment detection."""
        # Test direct court payment detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Court payment for legal fees"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'CORT')
        self.assertGreater(enhanced['confidence'], 0.8)

        # Test semantic court payment detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for judicial proceedings"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'CORT')
        self.assertGreater(enhanced['confidence'], 0.7)

    def test_legal_fees_detection(self):
        """Test legal fees detection."""
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for attorney fees"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'CORT')
        self.assertGreater(enhanced['confidence'], 0.7)

    def test_judgment_payment_detection(self):
        """Test judgment payment detection."""
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for court judgment"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'CORT')
        self.assertGreater(enhanced['confidence'], 0.8)

    def test_negative_indicators(self):
        """Test negative indicators."""
        # Test that non-court payments are not enhanced
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for groceries"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'OTHR')
        self.assertEqual(enhanced['confidence'], 0.5)

    def test_high_confidence_override(self):
        """Test that high confidence results are not overridden."""
        # Test that high confidence results are not overridden
        result = {'purpose_code': 'SALA', 'confidence': 0.9}
        narration = "Court payment for legal fees"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'SALA')
        self.assertEqual(enhanced['confidence'], 0.9)


if __name__ == '__main__':
    unittest.main()
