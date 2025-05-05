import unittest
import logging
from purpose_classifier.domain_enhancers.targeted_enhancer_semantic import TargetedEnhancer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestTargetedEnhancerSemantic(unittest.TestCase):
    """Test cases for the TargetedEnhancer class."""

    def setUp(self):
        """Set up the test environment."""
        self.enhancer = TargetedEnhancer()
        
        # Check if word embeddings are loaded
        if hasattr(self.enhancer, 'matcher') and hasattr(self.enhancer.matcher, 'embeddings') and self.enhancer.matcher.embeddings:
            logger.info("Word embeddings are loaded in the targeted enhancer semantic")
            # Try to calculate semantic similarity
            similarity = self.enhancer.matcher.semantic_similarity("loan", "mortgage")
            logger.info(f"Semantic similarity between 'loan' and 'mortgage': {similarity}")
            
            # Try to find similar words
            similar_words = self.enhancer.matcher.find_similar_words("loan", threshold=0.7)
            if similar_words:
                logger.info(f"Similar words to 'loan': {similar_words[:5]}")
        else:
            logger.error("Word embeddings are NOT loaded in the targeted enhancer semantic")

    def test_loan_repayment_detection(self):
        """Test loan repayment detection."""
        # Test direct loan repayment detection
        purpose_code = 'OTHR'
        confidence = 0.5
        narration = "Loan repayment for personal loan"
        enhanced_purpose, enhanced_confidence, enhancement_type = self.enhancer.enhance(purpose_code, confidence, narration)
        self.assertEqual(enhanced_purpose, 'LOAR')
        self.assertGreaterEqual(enhanced_confidence, 0.7)
        
        # Test mortgage repayment detection
        purpose_code = 'OTHR'
        confidence = 0.5
        narration = "Mortgage payment for home loan"
        enhanced_purpose, enhanced_confidence, enhancement_type = self.enhancer.enhance(purpose_code, confidence, narration)
        self.assertEqual(enhanced_purpose, 'LOAR')
        self.assertGreaterEqual(enhanced_confidence, 0.7)
        
        # Test EMI payment detection
        purpose_code = 'OTHR'
        confidence = 0.5
        narration = "EMI payment for car loan"
        enhanced_purpose, enhanced_confidence, enhancement_type = self.enhancer.enhance(purpose_code, confidence, narration)
        self.assertEqual(enhanced_purpose, 'LOAR')
        self.assertGreaterEqual(enhanced_confidence, 0.7)

    def test_loan_disbursement_detection(self):
        """Test loan disbursement detection."""
        # Test direct loan disbursement detection
        purpose_code = 'OTHR'
        confidence = 0.5
        narration = "Loan disbursement for personal loan"
        enhanced_purpose, enhanced_confidence, enhancement_type = self.enhancer.enhance(purpose_code, confidence, narration)
        self.assertEqual(enhanced_purpose, 'LOAN')
        self.assertGreaterEqual(enhanced_confidence, 0.7)
        
        # Test mortgage disbursement detection
        purpose_code = 'OTHR'
        confidence = 0.5
        narration = "Mortgage disbursement for home purchase"
        enhanced_purpose, enhanced_confidence, enhancement_type = self.enhancer.enhance(purpose_code, confidence, narration)
        self.assertEqual(enhanced_purpose, 'LOAN')
        self.assertGreaterEqual(enhanced_confidence, 0.7)
        
        # Test credit facility detection
        purpose_code = 'OTHR'
        confidence = 0.5
        narration = "Credit facility drawdown for business expansion"
        enhanced_purpose, enhanced_confidence, enhancement_type = self.enhancer.enhance(purpose_code, confidence, narration)
        self.assertEqual(enhanced_purpose, 'LOAN')
        self.assertGreaterEqual(enhanced_confidence, 0.7)

    def test_interbank_transfer_detection(self):
        """Test interbank transfer detection."""
        # Test direct interbank transfer detection
        purpose_code = 'OTHR'
        confidence = 0.5
        narration = "Interbank transfer for liquidity management"
        enhanced_purpose, enhanced_confidence, enhancement_type = self.enhancer.enhance(purpose_code, confidence, narration)
        self.assertEqual(enhanced_purpose, 'INTC')
        self.assertGreaterEqual(enhanced_confidence, 0.7)
        
        # Test nostro account detection
        purpose_code = 'OTHR'
        confidence = 0.5
        narration = "Nostro account funding for settlement"
        enhanced_purpose, enhanced_confidence, enhancement_type = self.enhancer.enhance(purpose_code, confidence, narration)
        self.assertEqual(enhanced_purpose, 'INTC')
        self.assertGreaterEqual(enhanced_confidence, 0.7)
        
        # Test correspondent banking detection
        purpose_code = 'OTHR'
        confidence = 0.5
        narration = "Correspondent banking payment for settlement"
        enhanced_purpose, enhanced_confidence, enhancement_type = self.enhancer.enhance(purpose_code, confidence, narration)
        self.assertEqual(enhanced_purpose, 'INTC')
        self.assertGreaterEqual(enhanced_confidence, 0.7)

    def test_property_purchase_detection(self):
        """Test property purchase detection."""
        # Test direct property purchase detection
        purpose_code = 'OTHR'
        confidence = 0.5
        narration = "Property purchase payment for apartment"
        enhanced_purpose, enhanced_confidence, enhancement_type = self.enhancer.enhance(purpose_code, confidence, narration)
        self.assertEqual(enhanced_purpose, 'PPTI')
        self.assertGreaterEqual(enhanced_confidence, 0.7)
        
        # Test real estate closing detection
        purpose_code = 'OTHR'
        confidence = 0.5
        narration = "Real estate closing payment for house purchase"
        enhanced_purpose, enhanced_confidence, enhancement_type = self.enhancer.enhance(purpose_code, confidence, narration)
        self.assertEqual(enhanced_purpose, 'PPTI')
        self.assertGreaterEqual(enhanced_confidence, 0.7)
        
        # Test down payment detection
        purpose_code = 'OTHR'
        confidence = 0.5
        narration = "Down payment for property purchase"
        enhanced_purpose, enhanced_confidence, enhancement_type = self.enhancer.enhance(purpose_code, confidence, narration)
        self.assertEqual(enhanced_purpose, 'PPTI')
        self.assertGreaterEqual(enhanced_confidence, 0.7)

    def test_high_confidence_override(self):
        """Test that high confidence results are not overridden."""
        # Test that high confidence results are not overridden
        purpose_code = 'SALA'
        confidence = 0.9
        narration = "Loan repayment for personal loan"
        enhanced_purpose, enhanced_confidence, enhancement_type = self.enhancer.enhance(purpose_code, confidence, narration)
        self.assertEqual(enhanced_purpose, 'SALA')
        self.assertEqual(enhanced_confidence, 0.9)


if __name__ == '__main__':
    unittest.main()
