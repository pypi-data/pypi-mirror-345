import unittest
import logging
from purpose_classifier.domain_enhancers.message_type_enhancer_semantic import MessageTypeEnhancerSemantic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestMessageTypeEnhancerSemantic(unittest.TestCase):
    """Test cases for the MessageTypeEnhancerSemantic class."""

    def setUp(self):
        """Set up the test environment."""
        self.enhancer = MessageTypeEnhancerSemantic()

        # Check if word embeddings are loaded
        if hasattr(self.enhancer, 'matcher') and hasattr(self.enhancer.matcher, 'embeddings') and self.enhancer.matcher.embeddings:
            logger.info("Word embeddings are loaded in the message type enhancer semantic")
            # Try to calculate semantic similarity
            similarity = self.enhancer.matcher.semantic_similarity("payment", "transfer")
            logger.info(f"Semantic similarity between 'payment' and 'transfer': {similarity}")
        else:
            logger.error("Word embeddings are NOT loaded in the message type enhancer semantic")

    def test_mt103_detection(self):
        """Test MT103 message type detection."""
        # Test MT103 message type detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for services"
        enhanced = self.enhancer.enhance_classification(result, narration, message_type="MT103")
        self.assertNotEqual(enhanced['purpose_code'], 'OTHR')
        self.assertGreater(enhanced['confidence'], 0.6)

    def test_mt202_detection(self):
        """Test MT202 message type detection."""
        # Test MT202 message type detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for services"
        enhanced = self.enhancer.enhance_classification(result, narration, message_type="MT202")
        self.assertNotEqual(enhanced['purpose_code'], 'OTHR')
        self.assertGreater(enhanced['confidence'], 0.6)

    def test_mt202cov_detection(self):
        """Test MT202COV message type detection."""
        # Test MT202COV message type detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for services"
        enhanced = self.enhancer.enhance_classification(result, narration, message_type="MT202COV")
        self.assertEqual(enhanced['purpose_code'], 'INTC')
        self.assertGreater(enhanced['confidence'], 0.7)

    def test_mt205_detection(self):
        """Test MT205 message type detection."""
        # Test MT205 message type detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for services"
        enhanced = self.enhancer.enhance_classification(result, narration, message_type="MT205")
        self.assertNotEqual(enhanced['purpose_code'], 'OTHR')
        self.assertGreater(enhanced['confidence'], 0.6)

    def test_mt205cov_detection(self):
        """Test MT205COV message type detection."""
        # Test MT205COV message type detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for services"
        enhanced = self.enhancer.enhance_classification(result, narration, message_type="MT205COV")
        self.assertEqual(enhanced['purpose_code'], 'INTC')
        self.assertGreater(enhanced['confidence'], 0.7)

    def test_no_message_type(self):
        """Test no message type."""
        # Test no message type
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for services"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'OTHR')
        self.assertEqual(enhanced['confidence'], 0.5)

    def test_high_confidence_override(self):
        """Test that high confidence results are not overridden."""
        # Test that high confidence results are not overridden
        result = {'purpose_code': 'SALA', 'confidence': 0.9}
        narration = "Payment for services"
        enhanced = self.enhancer.enhance_classification(result, narration, message_type="MT202COV")
        self.assertEqual(enhanced['purpose_code'], 'SALA')
        self.assertEqual(enhanced['confidence'], 0.9)


if __name__ == '__main__':
    unittest.main()
