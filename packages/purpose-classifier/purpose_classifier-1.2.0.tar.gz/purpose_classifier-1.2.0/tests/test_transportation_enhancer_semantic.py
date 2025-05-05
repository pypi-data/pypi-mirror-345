import unittest
import logging
from purpose_classifier.domain_enhancers.transportation_enhancer_semantic import TransportationDomainEnhancer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestTransportationEnhancerSemantic(unittest.TestCase):
    """Test cases for the TransportationDomainEnhancer class."""

    def setUp(self):
        """Set up the test environment."""
        self.enhancer = TransportationDomainEnhancer()
        
        # Check if word embeddings are loaded
        if hasattr(self.enhancer, 'matcher') and hasattr(self.enhancer.matcher, 'embeddings') and self.enhancer.matcher.embeddings:
            logger.info("Word embeddings are loaded in the transportation enhancer semantic")
            # Try to calculate semantic similarity
            similarity = self.enhancer.matcher.semantic_similarity("freight", "shipping")
            logger.info(f"Semantic similarity between 'freight' and 'shipping': {similarity}")
            
            # Try to find similar words
            similar_words = self.enhancer.matcher.find_similar_words("freight", threshold=0.7)
            if similar_words:
                logger.info(f"Similar words to 'freight': {similar_words[:5]}")
        else:
            logger.error("Word embeddings are NOT loaded in the transportation enhancer semantic")

    def test_freight_payment_detection(self):
        """Test freight payment detection."""
        # Test direct freight payment detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Freight payment for shipment"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'TRPT')
        self.assertGreaterEqual(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'TRPT')
        
        # Test shipping cost detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for shipping costs"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'TRPT')
        self.assertGreaterEqual(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'TRPT')
        
        # Test transportation fee detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Transportation fee payment"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'TRPT')
        self.assertGreaterEqual(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'TRPT')

    def test_air_freight_detection(self):
        """Test air freight detection."""
        # Test direct air freight detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Air freight payment"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'TRPT')
        self.assertGreaterEqual(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'TRPT')
        
        # Test air cargo detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for air cargo"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'TRPT')
        self.assertGreaterEqual(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'TRPT')
        
        # Test airway bill detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Airway bill payment"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'TRPT')
        self.assertGreaterEqual(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'TRPT')

    def test_sea_freight_detection(self):
        """Test sea freight detection."""
        # Test direct sea freight detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Sea freight payment"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'TRPT')
        self.assertGreaterEqual(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'TRPT')
        
        # Test ocean shipping detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for ocean shipping"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'TRPT')
        self.assertGreaterEqual(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'TRPT')
        
        # Test bill of lading detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Bill of lading payment"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'TRPT')
        self.assertGreaterEqual(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'TRPT')

    def test_rail_transport_detection(self):
        """Test rail transport detection."""
        # Test direct rail transport detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Rail transport payment"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'TRPT')
        self.assertGreaterEqual(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'TRPT')
        
        # Test railway freight detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for railway freight"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'TRPT')
        self.assertGreaterEqual(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'TRPT')
        
        # Test train shipping detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Train shipping payment"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'TRPT')
        self.assertGreaterEqual(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'TRPT')

    def test_road_transport_detection(self):
        """Test road transport detection."""
        # Test direct road transport detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Road transport payment"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'TRPT')
        self.assertGreaterEqual(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'TRPT')
        
        # Test truck freight detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for truck freight"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'TRPT')
        self.assertGreaterEqual(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'TRPT')
        
        # Test haulage detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Haulage payment"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'TRPT')
        self.assertGreaterEqual(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'TRPT')

    def test_courier_service_detection(self):
        """Test courier service detection."""
        # Test direct courier service detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Courier service payment"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'TRPT')
        self.assertGreaterEqual(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'TRPT')
        
        # Test express delivery detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Payment for express delivery"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'TRPT')
        self.assertGreaterEqual(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'TRPT')
        
        # Test parcel service detection
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Parcel service payment"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'TRPT')
        self.assertGreaterEqual(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'TRPT')

    def test_message_type_specific_detection(self):
        """Test message type specific detection."""
        # Test MT103 transportation boost
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Freight payment"
        enhanced = self.enhancer.enhance_classification(result, narration, message_type='MT103')
        self.assertEqual(enhanced['purpose_code'], 'TRPT')
        self.assertGreaterEqual(enhanced['confidence'], 0.7)
        self.assertEqual(enhanced['category_purpose_code'], 'TRPT')

    def test_high_confidence_override(self):
        """Test that high confidence results are not overridden."""
        # Test that high confidence results are not overridden
        result = {'purpose_code': 'SALA', 'confidence': 0.9}
        narration = "Freight payment for shipment"
        enhanced = self.enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'SALA')
        self.assertEqual(enhanced['confidence'], 0.9)


if __name__ == '__main__':
    unittest.main()
