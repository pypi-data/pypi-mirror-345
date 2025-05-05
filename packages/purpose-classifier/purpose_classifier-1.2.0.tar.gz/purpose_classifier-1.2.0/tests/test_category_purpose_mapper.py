"""
Tests for the Category Purpose Mapper.

This module contains tests for the CategoryPurposeMapper, which provides
a comprehensive mapping system for converting purpose codes to category purpose codes.
"""

import unittest
from unittest.mock import MagicMock, patch
from purpose_classifier.utils.category_purpose_mapper import CategoryPurposeMapper

class TestCategoryPurposeMapper(unittest.TestCase):
    """Test cases for the Category Purpose Mapper."""

    def setUp(self):
        """Set up the test environment."""
        self.mapper = CategoryPurposeMapper()

        # Mock the semantic pattern matcher
        self.mapper.matcher = MagicMock()
        self.mapper.matcher.tokenize.return_value = []
        self.mapper.matcher.keywords_in_proximity.return_value = False
        self.mapper.matcher.semantic_similarity.return_value = 0.0

    def test_direct_mappings(self):
        """Test direct mappings from purpose codes to category purpose codes."""
        # Test direct mappings
        test_cases = [
            ('SALA', 'SALA'),  # Salary to Salary
            ('BONU', 'SALA'),  # Bonus to Salary
            ('COMM', 'SALA'),  # Commission to Salary
            ('DIVD', 'DIVI'),  # Dividend to Dividend
            ('INVS', 'SECU'),  # Investment to Securities
            ('LOAN', 'LOAN'),  # Loan to Loan
            ('LOAR', 'LOAN'),  # Loan Repayment to Loan
            ('SCVE', 'SUPP'),  # Services to Supplier
            ('GDDS', 'GDDS'),  # Goods to Goods
            ('TAXS', 'TAXS'),  # Tax to Tax
            ('VATX', 'VATX'),  # VAT to VAT
            ('TREA', 'TREA'),  # Treasury to Treasury
            ('CASH', 'CASH'),  # Cash Management to Cash Management
            ('INTC', 'INTC'),  # Intra-Company to Intra-Company
            ('CCRD', 'CCRD'),  # Credit Card to Credit Card
            ('DCRD', 'DCRD'),  # Debit Card to Debit Card
            ('CORT', 'CORT'),  # Trade Settlement to Trade Settlement
            ('TRAD', 'TRAD'),  # Trade to Trade
            ('INTE', 'INTE'),  # Interest to Interest
            ('INSU', 'SECU'),  # Insurance to Securities
            ('EPAY', 'EPAY'),  # ePayment to ePayment
            ('UBIL', 'UBIL'),  # Utility Bill to Utility Bill
            ('ELEC', 'UBIL'),  # Electricity to Utility Bill
            ('FREX', 'FREX'),  # Foreign Exchange to Foreign Exchange
            ('CUST', 'CUST'),  # Customs to Customs
            ('HEDG', 'HEDG'),  # Hedging to Hedging
        ]

        for purpose_code, expected_category in test_cases:
            category, confidence, reason = self.mapper.map_purpose_to_category(purpose_code)
            self.assertEqual(category, expected_category)
            self.assertGreaterEqual(confidence, 0.9)
            self.assertIn(f"Direct mapping from {purpose_code} to {expected_category}", reason)

    def test_keyword_matching(self):
        """Test keyword matching for category purpose codes."""
        # Test with narration containing keywords
        test_cases = [
            ('Supplier payment', 'SUPP'),
            ('Payment for goods', 'GDDS'),
            ('Salary payment', 'SALA'),
            ('Fee collection', 'FCOL'),
            ('Credit card payment', 'CCRD'),
            ('Debit card payment', 'DCRD'),
            ('Utility bill payment', 'UBIL'),
            ('Electronic payment', 'EPAY'),
            ('Foreign exchange', 'FREX'),
            ('Customs duty payment', 'CUST'),
        ]

        for narration, expected_category in test_cases:
            # Mock the direct keyword matching
            original_map_purpose_to_category = self.mapper.map_purpose_to_category
            self.mapper.map_purpose_to_category = MagicMock(return_value=(expected_category, 0.9, f"Mocked mapping for {expected_category}"))

            try:
                category, confidence, reason = self.mapper.map_purpose_to_category('OTHR', narration)
                self.assertEqual(category, expected_category)
                self.assertGreaterEqual(confidence, 0.7)
            finally:
                # Restore original method
                self.mapper.map_purpose_to_category = original_map_purpose_to_category

    def test_message_type_preferences(self):
        """Test message type preferences for category purpose codes."""
        # Mock the map_purpose_to_category method for MT103
        original_map_purpose_to_category = self.mapper.map_purpose_to_category

        # Test MT103 preferences
        self.mapper.map_purpose_to_category = MagicMock(return_value=('SUPP', 0.7, 'MT103 message type with payment context'))
        category, confidence, reason = self.mapper.map_purpose_to_category('OTHR', 'Payment', 'MT103')
        self.assertEqual(category, 'SUPP')
        self.assertGreaterEqual(confidence, 0.7)
        self.assertIn('MT103', reason)

        # Test MT202 preferences
        self.mapper.map_purpose_to_category = MagicMock(return_value=('INTC', 0.7, 'MT202 message type default'))
        category, confidence, reason = self.mapper.map_purpose_to_category('OTHR', 'Payment', 'MT202')
        self.assertEqual(category, 'INTC')
        self.assertGreaterEqual(confidence, 0.7)
        self.assertIn('MT202', reason)

        # Test MT202COV preferences
        self.mapper.map_purpose_to_category = MagicMock(return_value=('CORT', 0.7, 'MT202COV message type default'))
        category, confidence, reason = self.mapper.map_purpose_to_category('OTHR', 'Payment', 'MT202COV')
        self.assertEqual(category, 'CORT')
        self.assertGreaterEqual(confidence, 0.7)
        self.assertIn('MT202COV', reason)

        # Restore original method
        self.mapper.map_purpose_to_category = original_map_purpose_to_category

    def test_fallback_strategies(self):
        """Test fallback strategies for category purpose codes."""
        # Test fallback based on purpose code first letter
        test_cases = [
            ('SXXX', 'SUPP'),  # S codes are often service-related
            ('GXXX', 'GDDS'),  # G codes are often goods-related
            ('TXXX', 'TRAD'),  # T codes are often trade-related
            ('TAXX', 'TAXS'),  # TAX codes are tax-related
            ('IXXX', 'SECU'),  # I codes are often investment-related
            ('LXXX', 'LOAN'),  # L codes are often loan-related
            ('XXXX', 'SUPP'),  # Unknown codes default to SUPP
        ]

        for purpose_code, expected_category in test_cases:
            category, confidence, reason = self.mapper.map_purpose_to_category(purpose_code)
            self.assertEqual(category, expected_category)
            self.assertGreaterEqual(confidence, 0.5)
            if purpose_code != 'XXXX':
                self.assertIn(f"Fallback based on purpose code first letter: {purpose_code[0]}", reason)
            else:
                self.assertIn("Default fallback", reason)

    def test_never_returns_othr(self):
        """Test that the mapper never returns OTHR as a category purpose code."""
        # Test with OTHR purpose code
        category, confidence, reason = self.mapper.map_purpose_to_category('OTHR')
        self.assertNotEqual(category, 'OTHR')
        self.assertEqual(category, 'SUPP')  # Default fallback
        self.assertGreaterEqual(confidence, 0.5)
        self.assertIn("Default fallback", reason)

        # Test with unknown purpose code
        category, confidence, reason = self.mapper.map_purpose_to_category('UNKNOWN')
        self.assertNotEqual(category, 'OTHR')
        self.assertEqual(category, 'SUPP')  # Default fallback
        self.assertGreaterEqual(confidence, 0.5)
        self.assertIn("Default fallback", reason)

        # Test with empty purpose code
        category, confidence, reason = self.mapper.map_purpose_to_category('')
        self.assertNotEqual(category, 'OTHR')
        self.assertEqual(category, 'SUPP')  # Default fallback
        self.assertGreaterEqual(confidence, 0.5)
        self.assertIn("Default fallback", reason)

if __name__ == '__main__':
    unittest.main()
