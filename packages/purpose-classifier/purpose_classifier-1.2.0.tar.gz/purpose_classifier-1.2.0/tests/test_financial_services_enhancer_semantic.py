import unittest
import logging
from purpose_classifier.domain_enhancers.financial_services_enhancer_semantic import FinancialServicesDomainEnhancer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestFinancialServicesEnhancerSemantic(unittest.TestCase):
    """Test cases for the FinancialServicesDomainEnhancer class."""

    def setUp(self):
        """Set up the test environment."""
        self.enhancer = FinancialServicesDomainEnhancer()
        
        # Check if word embeddings are loaded
        if hasattr(self.enhancer, 'matcher') and hasattr(self.enhancer.matcher, 'embeddings') and self.enhancer.matcher.embeddings:
            logger.info("Word embeddings are loaded in the financial services enhancer semantic")
            # Try to calculate semantic similarity
            similarity = self.enhancer.matcher.semantic_similarity("investment", "portfolio")
            logger.info(f"Semantic similarity between 'investment' and 'portfolio': {similarity}")
            
            # Try to find similar words
            similar_words = self.enhancer.matcher.find_similar_words("investment", threshold=0.7)
            if similar_words:
                logger.info(f"Similar words to 'investment': {similar_words[:5]}")
        else:
            logger.error("Word embeddings are NOT loaded in the financial services enhancer semantic")

    def test_investment_management_detection(self):
        """Test investment management detection."""
        # Test direct investment management detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Investment management services fee"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'SCVE')
        self.assertGreater(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'INVS')

    def test_securities_trading_detection(self):
        """Test securities trading detection."""
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Securities trading commission"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'SCVE')
        self.assertGreater(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'SECU')

    def test_financial_advisory_detection(self):
        """Test financial advisory detection."""
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Financial advisory services fee"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'SCVE')
        self.assertGreater(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'SUPP')

    def test_custody_service_detection(self):
        """Test custody service detection."""
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Custody service fee for securities"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'SCVE')
        self.assertGreater(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'SECU')

    def test_negative_indicators(self):
        """Test negative indicators."""
        # Test that non-financial services payments are not enhanced
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for groceries"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'OTHR')
        self.assertEqual(enhanced['confidence'], 0.5)

    def test_high_confidence_override(self):
        """Test that high confidence results are not overridden."""
        # Test that high confidence results are not overridden
        result = {'purpose_code': 'SALA', 'confidence': 0.9}
        narration = "Investment management services fee"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'SALA')
        self.assertEqual(enhanced['confidence'], 0.9)


if __name__ == '__main__':
    unittest.main()
