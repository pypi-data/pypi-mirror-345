import unittest
import logging
from purpose_classifier.domain_enhancers.pattern_enhancer_semantic import PatternEnhancerSemantic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestPatternEnhancerSemantic(unittest.TestCase):
    """Test cases for the PatternEnhancerSemantic class."""

    def setUp(self):
        """Set up the test environment."""
        self.enhancer = PatternEnhancerSemantic()

        # Check if word embeddings are loaded
        if hasattr(self.enhancer, 'matcher') and hasattr(self.enhancer.matcher, 'embeddings') and self.enhancer.matcher.embeddings:
            logger.info("Word embeddings are loaded in the pattern enhancer semantic")
            # Try to calculate semantic similarity
            similarity = self.enhancer.matcher.semantic_similarity("payment", "transfer")
            logger.info(f"Semantic similarity between 'payment' and 'transfer': {similarity}")
        else:
            logger.error("Word embeddings are NOT loaded in the pattern enhancer semantic")

    def test_salary_pattern_detection(self):
        """Test salary pattern detection."""
        # Test direct salary pattern detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Salary payment for May 2023"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'SALA')
        self.assertGreater(enhanced['confidence'], 0.8)

        # Test semantic salary pattern detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Monthly compensation for employee"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'SALA')
        self.assertGreater(enhanced['confidence'], 0.7)

    def test_tax_pattern_detection(self):
        """Test tax pattern detection."""
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for income tax"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'TAXS')
        self.assertGreater(enhanced['confidence'], 0.7)

    def test_utility_pattern_detection(self):
        """Test utility pattern detection."""
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for electricity bill"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'UTIL')
        self.assertGreater(enhanced['confidence'], 0.8)

    def test_negative_indicators(self):
        """Test negative indicators."""
        # Test that ambiguous narrations are not enhanced
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for services"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'OTHR')
        self.assertEqual(enhanced['confidence'], 0.5)

    def test_high_confidence_override(self):
        """Test that high confidence results are not overridden."""
        # Test that high confidence results are not overridden
        result = {'purpose_code': 'DIVD', 'confidence': 0.9}
        narration = "Salary payment for May 2023"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'DIVD')
        self.assertEqual(enhanced['confidence'], 0.9)


if __name__ == '__main__':
    unittest.main()
