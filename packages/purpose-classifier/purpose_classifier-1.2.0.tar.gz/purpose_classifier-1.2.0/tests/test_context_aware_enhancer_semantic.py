import unittest
import logging
from purpose_classifier.domain_enhancers.context_aware_enhancer_semantic import ContextAwareEnhancer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestContextAwareEnhancerSemantic(unittest.TestCase):
    """Test cases for the ContextAwareEnhancer class."""

    def setUp(self):
        """Set up the test environment."""
        self.enhancer = ContextAwareEnhancer()
        
        # Check if word embeddings are loaded
        if hasattr(self.enhancer, 'matcher') and hasattr(self.enhancer.matcher, 'embeddings') and self.enhancer.matcher.embeddings:
            logger.info("Word embeddings are loaded in the context aware enhancer semantic")
            # Try to calculate semantic similarity
            similarity = self.enhancer.matcher.semantic_similarity("payment", "transfer")
            logger.info(f"Semantic similarity between 'payment' and 'transfer': {similarity}")
            
            # Try to find similar words
            similar_words = self.enhancer.matcher.find_similar_words("payment", threshold=0.7)
            if similar_words:
                logger.info(f"Similar words to 'payment': {similar_words[:5]}")
        else:
            logger.error("Word embeddings are NOT loaded in the context aware enhancer semantic")

    def test_mt103_detection(self):
        """Test MT103 message type detection."""
        # Test direct MT103 detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "MT103 payment for supplier invoice"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['message_type'], 'MT103')
        
        # Test with message_type parameter
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for supplier invoice"
        enhanced = self.enhancer.enhance_classification(result, narration, message_type='MT103')
        self.assertEqual(enhanced['message_type'], 'MT103')

    def test_mt202_detection(self):
        """Test MT202 message type detection."""
        # Test direct MT202 detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "MT202 interbank transfer"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['message_type'], 'MT202')
        
        # Test with message_type parameter
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Interbank transfer"
        enhanced = self.enhancer.enhance_classification(result, narration, message_type='MT202')
        self.assertEqual(enhanced['message_type'], 'MT202')

    def test_mt205_detection(self):
        """Test MT205 message type detection."""
        # Test direct MT205 detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "MT205 treasury operation"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['message_type'], 'MT205')
        
        # Test with message_type parameter
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Treasury operation"
        enhanced = self.enhancer.enhance_classification(result, narration, message_type='MT205')
        self.assertEqual(enhanced['message_type'], 'MT205')

    def test_confidence_adjustment(self):
        """Test confidence adjustment based on message type."""
        # Test confidence adjustment for MT103
        result = {'purpose_code': 'SALA', 'confidence': 0.7}
        narration = "Salary payment"
        enhanced = self.enhancer.enhance_classification(result, narration, message_type='MT103')
        self.assertGreater(enhanced['confidence'], 0.7)
        
        # Test confidence adjustment for MT202
        result = {'purpose_code': 'INTC', 'confidence': 0.7}
        narration = "Interbank transfer"
        enhanced = self.enhancer.enhance_classification(result, narration, message_type='MT202')
        self.assertGreater(enhanced['confidence'], 0.7)
        
        # Test confidence adjustment for MT205
        result = {'purpose_code': 'INVS', 'confidence': 0.7}
        narration = "Investment management"
        enhanced = self.enhancer.enhance_classification(result, narration, message_type='MT205')
        self.assertGreater(enhanced['confidence'], 0.7)

    def test_pattern_matching(self):
        """Test pattern matching for specific purpose codes."""
        # Test salary pattern matching for MT103
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Salary payment for employee"
        enhanced = self.enhancer.enhance_classification(result, narration, message_type='MT103')
        self.assertEqual(enhanced['purpose_code'], 'SALA')
        self.assertGreater(enhanced['confidence'], 0.9)
        
        # Test interbank pattern matching for MT202
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Interbank transfer settlement"
        enhanced = self.enhancer.enhance_classification(result, narration, message_type='MT202')
        self.assertEqual(enhanced['purpose_code'], 'INTC')
        self.assertGreater(enhanced['confidence'], 0.9)
        
        # Test investment pattern matching for MT205
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Investment portfolio management"
        enhanced = self.enhancer.enhance_classification(result, narration, message_type='MT205')
        self.assertEqual(enhanced['purpose_code'], 'INVS')
        self.assertGreater(enhanced['confidence'], 0.9)


if __name__ == '__main__':
    unittest.main()
