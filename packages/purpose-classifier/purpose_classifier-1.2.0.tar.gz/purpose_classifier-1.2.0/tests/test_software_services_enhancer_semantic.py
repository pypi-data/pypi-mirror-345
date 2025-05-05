import unittest
import logging
from purpose_classifier.domain_enhancers.software_services_enhancer_semantic import SoftwareServicesEnhancer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestSoftwareServicesEnhancerSemantic(unittest.TestCase):
    """Test cases for the SoftwareServicesEnhancer class."""

    def setUp(self):
        """Set up the test environment."""
        self.enhancer = SoftwareServicesEnhancer()
        
        # Check if word embeddings are loaded
        if hasattr(self.enhancer, 'matcher') and hasattr(self.enhancer.matcher, 'embeddings') and self.enhancer.matcher.embeddings:
            logger.info("Word embeddings are loaded in the software services enhancer semantic")
            # Try to calculate semantic similarity
            similarity = self.enhancer.matcher.semantic_similarity("software", "application")
            logger.info(f"Semantic similarity between 'software' and 'application': {similarity}")
            
            # Try to find similar words
            similar_words = self.enhancer.matcher.find_similar_words("software", threshold=0.7)
            if similar_words:
                logger.info(f"Similar words to 'software': {similar_words[:5]}")
        else:
            logger.error("Word embeddings are NOT loaded in the software services enhancer semantic")

    def test_software_license_detection(self):
        """Test software license detection."""
        # Test direct software license detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Software license payment"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'GDDS')
        self.assertGreater(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'GDDS')
        
        # Test application subscription detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for application subscription"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'GDDS')
        self.assertGreater(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'GDDS')
        
        # Test SaaS subscription detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "SaaS subscription fee"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'GDDS')
        self.assertGreater(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'GDDS')

    def test_marketing_services_detection(self):
        """Test marketing services detection."""
        # Test direct marketing services detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Marketing services payment"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'SCVE')
        self.assertGreater(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'SCVE')
        
        # Test advertising campaign detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for advertising campaign"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'SCVE')
        self.assertGreater(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'SCVE')
        
        # Test marketing expenses detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Marketing expenses"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'SCVE')
        self.assertGreater(enhanced['confidence'], 0.9)
        self.assertEqual(enhanced['category_purpose_code'], 'SCVE')

    def test_website_services_detection(self):
        """Test website services detection."""
        # Test direct website services detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Website hosting payment"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'SCVE')
        self.assertGreater(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'FCOL')
        
        # Test domain registration detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for domain registration"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'SCVE')
        self.assertGreater(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'FCOL')
        
        # Test webmaster services detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Webmaster services fee"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'SCVE')
        self.assertGreater(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'FCOL')

    def test_rd_services_detection(self):
        """Test R&D services detection."""
        # Test direct R&D services detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Research and development services"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'SCVE')
        self.assertGreater(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'SUPP')
        
        # Test innovation services detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for innovation services"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'SCVE')
        self.assertGreater(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'SUPP')
        
        # Test testing services detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Testing services payment"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'SCVE')
        self.assertGreater(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'SUPP')

    def test_message_type_specific_detection(self):
        """Test message type specific detection."""
        # Test MT103 software boost
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Software payment"
        enhanced = self.enhancer.enhance_classification(result, narration, message_type='MT103')
        self.assertEqual(enhanced['purpose_code'], 'GDDS')
        self.assertGreater(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'GDDS')
        
        # Test MT103 service boost
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Service payment"
        enhanced = self.enhancer.enhance_classification(result, narration, message_type='MT103')
        self.assertEqual(enhanced['purpose_code'], 'SCVE')
        self.assertGreater(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'SUPP')

    def test_high_confidence_override(self):
        """Test that high confidence results are not overridden."""
        # Test that high confidence results are not overridden
        result = {'purpose_code': 'SALA', 'confidence': 0.9}
        narration = "Software license payment"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'SALA')
        self.assertEqual(enhanced['confidence'], 0.9)


if __name__ == '__main__':
    unittest.main()
