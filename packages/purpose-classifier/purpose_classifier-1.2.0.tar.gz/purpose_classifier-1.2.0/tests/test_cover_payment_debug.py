"""
Debug test for cover payment narrations.

This module tests the cover payment narrations to see what purpose code is being returned.
"""

import unittest
import logging
from purpose_classifier.domain_enhancers.enhancer_manager import EnhancerManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestCoverPaymentDebug(unittest.TestCase):
    """Debug test for cover payment narrations."""

    def setUp(self):
        """Set up test fixtures."""
        # Create the enhancer manager
        self.manager = EnhancerManager()

    def test_cover_payment_debug(self):
        """Debug test for cover payment narrations."""
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

            # Apply the enhancer manager
            enhanced = self.manager.enhance(result, narration, "MT202COV")

            # Print the result
            print(f"Narration: {narration}")
            print(f"Purpose code: {enhanced.get('purpose_code')}")
            print(f"Category purpose code: {enhanced.get('category_purpose_code')}")
            print(f"Confidence: {enhanced.get('confidence')}")
            print(f"Category confidence: {enhanced.get('category_confidence')}")
            print(f"Enhancer decisions:")
            for decision in enhanced.get('enhancer_decisions', []):
                print(f"  {decision.get('enhancer')}: {decision.get('old_code')} -> {decision.get('new_code')} ({decision.get('confidence')}) - {decision.get('applied')}")
            print()


if __name__ == '__main__':
    unittest.main()
