"""
Test for the PropertyPurchaseEnhancerSemantic class.

This module tests the PropertyPurchaseEnhancerSemantic class to ensure it correctly
identifies property purchase-related transactions.
"""

import unittest
import logging
from purpose_classifier.domain_enhancers.property_purchase_enhancer_semantic import PropertyPurchaseEnhancerSemantic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestPropertyPurchaseEnhancerSemantic(unittest.TestCase):
    """Test the PropertyPurchaseEnhancerSemantic class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create the property purchase enhancer
        self.enhancer = PropertyPurchaseEnhancerSemantic()

    def test_property_purchase_detection(self):
        """Test property purchase detection."""
        # Test cases for property purchase
        narrations = [
            "Payment for property purchase",
            "Payment for real estate purchase",
            "Payment for house purchase",
            "Payment for apartment purchase",
            "Payment for condo purchase",
            "Payment for home purchase",
            "Payment for buying property",
            "Payment for buying real estate",
            "Payment for buying house",
            "Payment for buying apartment",
            "Payment for buying condo",
            "Payment for buying home",
            "Payment for property acquisition",
            "Payment for real estate acquisition",
            "Payment for house acquisition",
            "Payment for apartment acquisition",
            "Payment for condo acquisition",
            "Payment for home acquisition",
            "Payment for purchase of property",
            "Payment for purchase of real estate",
            "Payment for purchase of house",
            "Payment for purchase of apartment",
            "Payment for purchase of condo",
            "Payment for purchase of home",
            "Payment for acquisition of property",
            "Payment for acquisition of real estate",
            "Payment for acquisition of house",
            "Payment for acquisition of apartment",
            "Payment for acquisition of condo",
            "Payment for acquisition of home",
            "Payment for down payment on property",
            "Payment for earnest money on house",
            "Payment for closing costs on apartment",
            "Payment for escrow payment on condo",
            "Payment for property settlement",
            "Payment for real estate closing",
            "Payment for house closing",
            "Payment for apartment closing",
            "Payment for condo closing",
            "Payment for home closing"
        ]

        # Test each narration
        for narration in narrations:
            # Create a mock result
            result = {'purpose_code': 'OTHR', 'confidence': 0.3}

            # Apply the enhancer
            enhanced = self.enhancer.enhance_classification(result, narration)

            # Check the result
            self.assertEqual(enhanced['purpose_code'], 'PPTI')
            self.assertGreater(enhanced['confidence'], 0.8)
            self.assertEqual(enhanced['category_purpose_code'], 'PPTI')
            self.assertGreater(enhanced['category_confidence'], 0.9)
            self.assertTrue(enhanced['property_purchase_detected'])

    def test_mortgage_loan_detection(self):
        """Test mortgage loan detection."""
        # Test cases for mortgage loan
        narrations = [
            "Payment for mortgage loan",
            "Payment for home loan",
            "Payment for property loan",
            "Payment for real estate loan",
            "Payment for house loan",
            "Payment for apartment loan",
            "Payment for condo loan",
            "Payment for mortgage payment",
            "Payment for home equity loan",
            "Payment for heloc",
            "Payment for second mortgage",
            "Payment for reverse mortgage",
            "Payment for mortgage refinance",
            "Payment for loan refinance",
            "Payment for mortgage application",
            "Payment for loan application",
            "Payment for mortgage approval",
            "Payment for loan approval",
            "Payment for mortgage processing",
            "Payment for loan processing",
            "Payment for mortgage origination",
            "Payment for loan origination",
            "Payment for mortgage closing",
            "Payment for loan closing"
        ]

        # Test each narration
        for narration in narrations:
            # Create a mock result
            result = {'purpose_code': 'OTHR', 'confidence': 0.3}

            # Apply the enhancer
            enhanced = self.enhancer.enhance_classification(result, narration)

            # Check the result
            self.assertEqual(enhanced['purpose_code'], 'LOAN')
            self.assertGreater(enhanced['confidence'], 0.8)
            self.assertEqual(enhanced['category_purpose_code'], 'LOAN')
            self.assertGreater(enhanced['category_confidence'], 0.9)
            self.assertTrue(enhanced['mortgage_loan_detected'])

    def test_negative_indicators(self):
        """Test negative indicators."""
        # Test cases for negative indicators
        narrations = [
            "Payment for rent payment",
            "Payment for rental payment",
            "Payment for lease payment",
            "Payment for property tax",
            "Payment for real estate tax",
            "Payment for property insurance",
            "Payment for homeowners insurance",
            "Payment for home insurance",
            "Payment for property management",
            "Payment for property maintenance",
            "Payment for property repair",
            "Payment for home repair",
            "Payment for home improvement",
            "Payment for renovation",
            "Payment for remodeling"
        ]

        # Test each narration
        for narration in narrations:
            # Create a mock result
            result = {'purpose_code': 'OTHR', 'confidence': 0.3}

            # Apply the enhancer
            enhanced = self.enhancer.enhance_classification(result, narration)

            # Check the result - should not be enhanced
            self.assertEqual(enhanced['purpose_code'], 'OTHR')
            self.assertEqual(enhanced['confidence'], 0.3)
            self.assertFalse(enhanced.get('property_purchase_detected', False))
            self.assertFalse(enhanced.get('mortgage_loan_detected', False))

    def test_message_type_context(self):
        """Test message type context."""
        # Test cases for message type context
        test_cases = [
            {
                'narration': "Transfer for property purchase",
                'message_type': 'MT103',
                'expected_code': 'PPTI',
                'expected_category': 'PPTI'
            },
            {
                'narration': "Transfer for mortgage loan",
                'message_type': 'MT103',
                'expected_code': 'LOAN',
                'expected_category': 'LOAN'
            }
        ]

        # Test each case
        for test_case in test_cases:
            # Create a mock result
            result = {'purpose_code': 'OTHR', 'confidence': 0.3}

            # Apply the enhancer
            enhanced = self.enhancer.enhance_classification(result, test_case['narration'], test_case['message_type'])

            # Check the result
            self.assertEqual(enhanced['purpose_code'], test_case['expected_code'])
            self.assertGreater(enhanced['confidence'], 0.8)
            self.assertEqual(enhanced['category_purpose_code'], test_case['expected_category'])
            self.assertGreater(enhanced['category_confidence'], 0.9)

    def test_high_confidence_override(self):
        """Test high confidence override."""
        # Create a mock result with high confidence
        result = {'purpose_code': 'OTHR', 'confidence': 0.96}

        # Apply the enhancer
        enhanced = self.enhancer.enhance_classification(result, "Payment for property purchase")

        # Check the result - should not be enhanced
        self.assertEqual(enhanced['purpose_code'], 'OTHR')
        self.assertEqual(enhanced['confidence'], 0.96)
        self.assertFalse(enhanced.get('property_purchase_detected', False))
        self.assertFalse(enhanced.get('mortgage_loan_detected', False))


if __name__ == '__main__':
    unittest.main()
