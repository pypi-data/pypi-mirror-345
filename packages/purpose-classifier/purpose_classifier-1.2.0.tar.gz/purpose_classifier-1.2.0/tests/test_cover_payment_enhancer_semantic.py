"""
Test for the CoverPaymentEnhancerSemantic class.

This module tests the CoverPaymentEnhancerSemantic class to ensure it correctly
identifies cover payment-related transactions.
"""

import unittest
import logging
from purpose_classifier.domain_enhancers.cover_payment_enhancer_semantic import CoverPaymentEnhancerSemantic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestCoverPaymentEnhancerSemantic(unittest.TestCase):
    """Test the CoverPaymentEnhancerSemantic class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create the cover payment enhancer
        self.enhancer = CoverPaymentEnhancerSemantic()

    def test_cover_payment_detection(self):
        """Test cover payment detection."""
        # Test cases for cover payment
        narrations = [
            "Payment for cover payment",
            "Payment for cover transfer",
            "Payment for payment cover",
            "Payment for transfer cover",
            "Payment for covering payment",
            "Payment for covering transfer",
            "Payment for correspondent banking",
            "Payment for correspondent payment",
            "Payment for correspondent transfer",
            "Payment for interbank cover",
            "Payment for bank to bank cover",
            "Payment for financial institution cover",
            "Payment for nostro cover",
            "Payment for vostro cover",
            "Payment for loro cover"
        ]

        # Test each narration with MT202COV message type
        for narration in narrations:
            # Create a mock result
            result = {'purpose_code': 'OTHR', 'confidence': 0.3}

            # Apply the enhancer
            enhanced = self.enhancer.enhance_classification(result, narration, "MT202COV")

            # Check the result - should be XBCT for MT202COV message type
            self.assertEqual(enhanced['purpose_code'], 'XBCT')
            self.assertGreater(enhanced['confidence'], 0.8)
            self.assertEqual(enhanced['category_purpose_code'], 'XBCT')
            self.assertGreater(enhanced['category_confidence'], 0.9)
            self.assertTrue(enhanced['cover_payment_detected'])
            self.assertEqual(enhanced['cover_payment_type'], 'cross_border')
            self.assertEqual(enhanced['cover_payment_message_type'], 'MT202COV')

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
            "Payment for foreign transfer"
        ]

        # Test each narration with MT202COV message type
        for narration in narrations:
            # Create a mock result
            result = {'purpose_code': 'OTHR', 'confidence': 0.3}

            # Apply the enhancer
            enhanced = self.enhancer.enhance_classification(result, narration, "MT202COV")

            # Check the result
            self.assertEqual(enhanced['purpose_code'], 'XBCT')
            self.assertGreater(enhanced['confidence'], 0.8)
            self.assertEqual(enhanced['category_purpose_code'], 'XBCT')
            self.assertGreater(enhanced['category_confidence'], 0.9)
            self.assertTrue(enhanced['cover_payment_detected'])
            self.assertEqual(enhanced['cover_payment_type'], 'cross_border')
            self.assertEqual(enhanced['cover_payment_message_type'], 'MT202COV')

    def test_treasury_detection(self):
        """Test treasury operation detection."""
        # Test cases for treasury operation
        narrations = [
            "Payment for treasury payment",
            "Payment for treasury transfer",
            "Payment for treasury operation",
            "Payment for treasury transaction",
            "Payment for treasury settlement",
            "Payment for treasury cover"
        ]

        # Test each narration with MT202COV message type
        for narration in narrations:
            # Create a mock result
            result = {'purpose_code': 'OTHR', 'confidence': 0.3}

            # Apply the enhancer
            enhanced = self.enhancer.enhance_classification(result, narration, "MT202COV")

            # Check the result
            self.assertEqual(enhanced['purpose_code'], 'XBCT')
            self.assertGreater(enhanced['confidence'], 0.8)
            self.assertEqual(enhanced['category_purpose_code'], 'XBCT')
            self.assertGreater(enhanced['category_confidence'], 0.9)
            self.assertTrue(enhanced['cover_payment_detected'])
            self.assertEqual(enhanced['cover_payment_type'], 'cross_border')
            self.assertEqual(enhanced['cover_payment_message_type'], 'MT202COV')

    def test_forex_detection(self):
        """Test foreign exchange detection."""
        # Test cases for foreign exchange
        narrations = [
            "Payment for forex payment",
            "Payment for forex transfer",
            "Payment for forex settlement",
            "Payment for forex transaction",
            "Payment for foreign exchange payment",
            "Payment for foreign exchange transfer",
            "Payment for foreign exchange settlement",
            "Payment for foreign exchange transaction",
            "Payment for fx payment",
            "Payment for fx transfer",
            "Payment for fx settlement",
            "Payment for fx transaction"
        ]

        # Test each narration with MT202COV message type
        for narration in narrations:
            # Create a mock result
            result = {'purpose_code': 'OTHR', 'confidence': 0.3}

            # Apply the enhancer
            enhanced = self.enhancer.enhance_classification(result, narration, "MT202COV")

            # Check the result
            self.assertEqual(enhanced['purpose_code'], 'XBCT')
            self.assertGreater(enhanced['confidence'], 0.8)
            self.assertEqual(enhanced['category_purpose_code'], 'XBCT')
            self.assertGreater(enhanced['category_confidence'], 0.9)
            self.assertTrue(enhanced['cover_payment_detected'])
            self.assertEqual(enhanced['cover_payment_type'], 'cross_border')
            self.assertEqual(enhanced['cover_payment_message_type'], 'MT202COV')

    def test_intra_company_detection(self):
        """Test intra-company payment detection."""
        # Test cases for intra-company payment
        narrations = [
            "Payment for intra company payment",
            "Payment for intracompany payment",
            "Payment for intra-company payment",
            "Payment for intra company transfer",
            "Payment for intracompany transfer",
            "Payment for intra-company transfer",
            "Payment for internal company payment",
            "Payment for internal company transfer",
            "Payment for internal transfer",
            "Payment for internal payment",
            "Payment for company internal payment",
            "Payment for company internal transfer"
        ]

        # Test each narration with MT202COV message type
        for narration in narrations:
            # Create a mock result
            result = {'purpose_code': 'OTHR', 'confidence': 0.3}

            # Apply the enhancer
            enhanced = self.enhancer.enhance_classification(result, narration, "MT202COV")

            # Check the result
            self.assertEqual(enhanced['purpose_code'], 'XBCT')
            self.assertGreater(enhanced['confidence'], 0.8)
            self.assertEqual(enhanced['category_purpose_code'], 'XBCT')
            self.assertGreater(enhanced['category_confidence'], 0.9)
            self.assertTrue(enhanced['cover_payment_detected'])
            self.assertEqual(enhanced['cover_payment_type'], 'cross_border')
            self.assertEqual(enhanced['cover_payment_message_type'], 'MT202COV')

    def test_negative_indicators(self):
        """Test negative indicators."""
        # Test cases for negative indicators
        narrations = [
            "Payment for salary payment",
            "Payment for salary transfer",
            "Payment for wage payment",
            "Payment for wage transfer",
            "Payment for payroll payment",
            "Payment for payroll transfer",
            "Payment for pension payment",
            "Payment for pension transfer",
            "Payment for social security payment",
            "Payment for social security transfer",
            "Payment for tax payment",
            "Payment for tax transfer",
            "Payment for utility payment",
            "Payment for utility transfer",
            "Payment for rent payment",
            "Payment for rent transfer",
            "Payment for insurance payment",
            "Payment for insurance transfer",
            "Payment for loan payment",
            "Payment for loan transfer",
            "Payment for mortgage payment",
            "Payment for mortgage transfer",
            "Payment for credit card payment",
            "Payment for credit card transfer",
            "Payment for invoice payment",
            "Payment for invoice transfer",
            "Payment for bill payment",
            "Payment for bill transfer"
        ]

        # Test each narration with MT202COV message type
        for narration in narrations:
            # Create a mock result
            result = {'purpose_code': 'OTHR', 'confidence': 0.3}

            # Apply the enhancer
            enhanced = self.enhancer.enhance_classification(result, narration, "MT202COV")

            # Check the result - should not be enhanced
            self.assertEqual(enhanced['purpose_code'], 'OTHR')
            self.assertEqual(enhanced['confidence'], 0.3)
            self.assertFalse(enhanced.get('cover_payment_detected', False))

    def test_message_type_context(self):
        """Test message type context."""
        # Test cases for message type context
        test_cases = [
            {
                'narration': "Transfer for payment",
                'message_type': 'MT202COV',
                'expected_code': 'XBCT',
                'expected_category': 'XBCT'
            },
            {
                'narration': "Transfer for payment",
                'message_type': 'MT205COV',
                'expected_code': 'XBCT',
                'expected_category': 'XBCT'
            },
            {
                'narration': "Transfer for payment",
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
            self.assertEqual(enhanced['purpose_code'], test_case['expected_code'])
            if test_case['expected_code'] != 'OTHR':
                self.assertGreater(enhanced['confidence'], 0.8)
                self.assertEqual(enhanced['category_purpose_code'], test_case['expected_category'])
                self.assertGreater(enhanced['category_confidence'], 0.9)
                self.assertTrue(enhanced['cover_payment_detected'])
                self.assertEqual(enhanced['cover_payment_type'], 'cross_border')
                self.assertEqual(enhanced['cover_payment_message_type'], test_case['message_type'])

    def test_high_confidence_override(self):
        """Test high confidence override."""
        # Create a mock result with high confidence
        result = {'purpose_code': 'OTHR', 'confidence': 0.96}

        # Apply the enhancer
        enhanced = self.enhancer.enhance_classification(result, "Payment for cover payment", "MT202COV")

        # Check the result - should be enhanced because it's a cover payment message type
        self.assertEqual(enhanced['purpose_code'], 'XBCT')
        self.assertGreater(enhanced['confidence'], 0.8)
        self.assertEqual(enhanced['category_purpose_code'], 'XBCT')
        self.assertGreater(enhanced['category_confidence'], 0.9)
        self.assertTrue(enhanced['cover_payment_detected'])
        self.assertEqual(enhanced['cover_payment_type'], 'cross_border')
        self.assertEqual(enhanced['cover_payment_message_type'], 'MT202COV')

        # Create a mock result with high confidence and a valid cover payment purpose code
        result = {'purpose_code': 'INTC', 'confidence': 0.96}

        # Apply the enhancer
        enhanced = self.enhancer.enhance_classification(result, "Payment for cover payment", "MT202COV")

        # Check the result - should not be enhanced because it's already a valid cover payment purpose code
        self.assertEqual(enhanced['purpose_code'], 'INTC')
        self.assertEqual(enhanced['confidence'], 0.96)


if __name__ == '__main__':
    unittest.main()
