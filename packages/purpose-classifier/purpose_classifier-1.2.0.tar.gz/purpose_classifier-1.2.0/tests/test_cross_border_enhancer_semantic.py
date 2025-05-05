"""
Test for the CrossBorderEnhancerSemantic class.

This module tests the CrossBorderEnhancerSemantic class to ensure it correctly
identifies cross-border payment-related transactions.
"""

import unittest
import logging
from purpose_classifier.domain_enhancers.cross_border_enhancer_semantic import CrossBorderEnhancerSemantic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestCrossBorderEnhancerSemantic(unittest.TestCase):
    """Test the CrossBorderEnhancerSemantic class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create the cross-border payment enhancer
        self.enhancer = CrossBorderEnhancerSemantic()

    def test_cross_border_detection(self):
        """Test cross-border payment detection."""
        # Test cases for cross-border payment
        narrations = [
            "Payment for cross border payment",
            "Payment for cross-border payment",
            "Payment for cross border transfer",
            "Payment for cross-border transfer",
            "Payment for international payment",
            "Payment for international transfer",
            "Payment for global payment",
            "Payment for global transfer",
            "Payment for foreign payment",
            "Payment for foreign transfer",
            "Payment for overseas payment",
            "Payment for overseas transfer",
            "Payment for transnational payment",
            "Payment for transnational transfer",
            "Payment for international wire",
            "Payment for international wire transfer",
            "Payment for international remittance",
            "Payment for foreign remittance",
            "Payment for overseas remittance",
            "Payment for global remittance",
            "Payment for transnational remittance"
        ]

        # Test each narration
        for narration in narrations:
            # Create a mock result
            result = {'purpose_code': 'OTHR', 'confidence': 0.3}

            # Apply the enhancer
            enhanced = self.enhancer.enhance_classification(result, narration)

            # Check the result
            self.assertEqual(enhanced['purpose_code'], 'XBCT')
            self.assertGreater(enhanced['confidence'], 0.8)
            self.assertEqual(enhanced['category_purpose_code'], 'XBCT')
            self.assertGreater(enhanced['category_confidence'], 0.9)
            self.assertTrue(enhanced['cross_border_detected'])
            self.assertIn(enhanced['cross_border_type'], ['general_payment', 'wire_transfer', 'remittance', 'settlement', 'cover_payment'])

    def test_cross_border_settlement_detection(self):
        """Test cross-border settlement detection."""
        # Test cases for cross-border settlement
        narrations = [
            "Payment for cross border settlement",
            "Payment for cross-border settlement",
            "Payment for international settlement",
            "Payment for global settlement",
            "Payment for foreign settlement",
            "Payment for overseas settlement",
            "Payment for transnational settlement"
        ]

        # Test each narration
        for narration in narrations:
            # Create a mock result
            result = {'purpose_code': 'OTHR', 'confidence': 0.3}

            # Apply the enhancer
            enhanced = self.enhancer.enhance_classification(result, narration)

            # Check the result
            self.assertEqual(enhanced['purpose_code'], 'XBCT')
            self.assertGreater(enhanced['confidence'], 0.8)
            self.assertEqual(enhanced['category_purpose_code'], 'XBCT')
            self.assertGreater(enhanced['category_confidence'], 0.9)
            self.assertTrue(enhanced['cross_border_detected'])
            self.assertEqual(enhanced['cross_border_type'], 'settlement')

    def test_cross_border_cover_detection(self):
        """Test cross-border cover detection."""
        # Test cases for cross-border cover
        narrations = [
            "Payment for cross border cover",
            "Payment for cross-border cover",
            "Payment for cover for cross border",
            "Payment for cover for cross-border",
            "Payment for international cover",
            "Payment for cover for international",
            "Payment for global cover",
            "Payment for cover for global",
            "Payment for foreign cover",
            "Payment for cover for foreign",
            "Payment for overseas cover",
            "Payment for cover for overseas",
            "Payment for transnational cover",
            "Payment for cover for transnational"
        ]

        # Test each narration
        for narration in narrations:
            # Create a mock result
            result = {'purpose_code': 'OTHR', 'confidence': 0.3}

            # Apply the enhancer
            enhanced = self.enhancer.enhance_classification(result, narration)

            # Check the result
            self.assertEqual(enhanced['purpose_code'], 'XBCT')
            self.assertGreater(enhanced['confidence'], 0.8)
            self.assertEqual(enhanced['category_purpose_code'], 'XBCT')
            self.assertGreater(enhanced['category_confidence'], 0.9)
            self.assertTrue(enhanced['cross_border_detected'])
            self.assertEqual(enhanced['cross_border_type'], 'cover_payment')

    def test_negative_indicators(self):
        """Test negative indicators."""
        # Test cases for negative indicators
        narrations = [
            "Payment for domestic payment",
            "Payment for domestic transfer",
            "Payment for domestic remittance",
            "Payment for local payment",
            "Payment for local transfer",
            "Payment for local remittance",
            "Payment for internal payment",
            "Payment for internal transfer",
            "Payment for internal remittance",
            "Payment for intra-company payment",
            "Payment for intracompany payment",
            "Payment for intra company payment",
            "Payment for intra-company transfer",
            "Payment for intracompany transfer",
            "Payment for intra company transfer",
            "Payment for intra-company remittance",
            "Payment for intracompany remittance",
            "Payment for intra company remittance"
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
            self.assertFalse(enhanced.get('cross_border_detected', False))

    def test_message_type_context(self):
        """Test message type context."""
        # Test cases for message type context
        test_cases = [
            {
                'narration': "Transfer for cover payment",
                'message_type': 'MT202COV',
                'expected_code': 'XBCT',
                'expected_category': 'XBCT'
            },
            {
                'narration': "Transfer for cover payment",
                'message_type': 'MT205COV',
                'expected_code': 'XBCT',
                'expected_category': 'XBCT'
            },
            {
                'narration': "Transfer for domestic payment",
                'message_type': 'MT103',
                'expected_code': 'OTHR',
                'expected_category': None
            }
        ]

        # Test each case
        for test_case in test_cases:
            # Create a mock result
            result = {'purpose_code': 'OTHR', 'confidence': 0.3}

            # Apply the enhancer
            enhanced = self.enhancer.enhance_classification(result, test_case['narration'], test_case['message_type'])

            # Check the result
            if test_case['message_type'] in ['MT202COV', 'MT205COV']:
                self.assertEqual(enhanced['purpose_code'], test_case['expected_code'])
                self.assertGreater(enhanced['confidence'], 0.8)
                self.assertEqual(enhanced['category_purpose_code'], test_case['expected_category'])
                self.assertGreater(enhanced['category_confidence'], 0.9)
                self.assertTrue(enhanced['cross_border_detected'])
                self.assertEqual(enhanced['cross_border_type'], 'cover_payment')
                if 'cross_border_message_type' in enhanced:
                    self.assertEqual(enhanced['cross_border_message_type'], test_case['message_type'])
            else:
                self.assertEqual(enhanced['purpose_code'], test_case['expected_code'])

    def test_high_confidence_override(self):
        """Test high confidence override."""
        # Create a mock result with high confidence
        result = {'purpose_code': 'OTHR', 'confidence': 0.96}

        # Apply the enhancer
        enhanced = self.enhancer.enhance_classification(result, "Payment for cross border payment")

        # Check the result - should not be enhanced because of high confidence
        self.assertEqual(enhanced['purpose_code'], 'OTHR')
        self.assertEqual(enhanced['confidence'], 0.96)


if __name__ == '__main__':
    unittest.main()
