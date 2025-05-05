"""
Tests for the Category Purpose Enhancer Semantic.

This module contains tests for the CategoryPurposeEnhancerSemantic, which provides
semantic-aware enhancement for category purpose codes.
"""

import unittest
from unittest.mock import MagicMock, patch
from purpose_classifier.domain_enhancers.category_purpose_enhancer_semantic import CategoryPurposeEnhancerSemantic

class TestCategoryPurposeEnhancerSemantic(unittest.TestCase):
    """Test cases for the Category Purpose Enhancer Semantic."""

    def setUp(self):
        """Set up the test environment."""
        self.enhancer = CategoryPurposeEnhancerSemantic()

        # Mock the semantic pattern matcher
        self.enhancer.matcher = MagicMock()
        self.enhancer.matcher.tokenize.return_value = []
        self.enhancer.matcher.keywords_in_proximity.return_value = False
        self.enhancer.matcher.semantic_similarity.return_value = 0.0

        # Mock the category purpose mapper
        self.enhancer.mapper = MagicMock()
        self.enhancer.mapper.map_purpose_to_category.return_value = ('SUPP', 0.9, 'Mocked mapping')

    def test_direct_keyword_matching(self):
        """Test direct keyword matching."""
        # Test supplier keywords
        test_cases = [
            ("Supplier payment", "SUPP"),
            ("Vendor payment", "SUPP"),
            ("Invoice payment", "SUPP"),
            ("Bill payment", "SUPP"),
            ("Purchase order", "SUPP"),
            ("Purchase of goods", "GDDS"),
            ("Goods payment", "GDDS"),
            ("Merchandise payment", "GDDS"),
            ("Payment for goods", "GDDS"),
            ("Goods purchase", "GDDS")
        ]

        for narration, expected_code in test_cases:
            # Mock the direct_keyword_match method
            original_direct_keyword_match = self.enhancer.direct_keyword_match

            # Create a mock that returns True for the expected code and False for others
            def mock_direct_keyword_match(text, code):
                if code == expected_code:
                    return (True, 0.95, narration)
                return (False, 0.0, None)

            self.enhancer.direct_keyword_match = mock_direct_keyword_match

            try:
                result = {'purpose_code': 'OTHR', 'confidence': 0.3}
                enhanced = self.enhancer.enhance_classification(result, narration)

                # Should enhance to the expected code
                self.assertEqual(enhanced['category_purpose_code'], expected_code)
                self.assertGreaterEqual(enhanced['category_confidence'], 0.9)
                self.assertTrue(enhanced['category_enhanced'])
                self.assertEqual(enhanced['category_enhancement_applied'], 'category_purpose_enhancer_semantic')
            finally:
                # Restore original method
                self.enhancer.direct_keyword_match = original_direct_keyword_match

    def test_context_pattern_matching(self):
        """Test context pattern matching."""
        # Mock the context_match method
        original_context_match = self.enhancer.context_match
        self.enhancer.context_match = MagicMock(return_value=0.8)

        # Mock the keywords_in_proximity method
        self.enhancer.matcher.keywords_in_proximity = MagicMock(return_value=True)

        try:
            # Test with supplier context
            result = {'purpose_code': 'OTHR', 'confidence': 0.3}
            enhanced = self.enhancer.enhance_classification(result, "Payment to supplier")

            # Should enhance to SUPP
            self.assertEqual(enhanced['category_purpose_code'], 'SUPP')
            self.assertGreaterEqual(enhanced['category_confidence'], 0.7)
            self.assertTrue(enhanced['category_enhanced'])
            self.assertEqual(enhanced['category_enhancement_applied'], 'category_purpose_enhancer_semantic')
        finally:
            # Restore original methods
            self.enhancer.context_match = original_context_match

    def test_semantic_similarity_matching(self):
        """Test semantic similarity matching."""
        # Mock the semantic_similarity_match method
        original_semantic_similarity_match = self.enhancer.semantic_similarity_match
        self.enhancer.semantic_similarity_match = MagicMock(return_value=(True, 0.8, 'SUPP', [('payment', 'supplier', 0.8, 1.0)]))

        try:
            # Test with supplier semantic similarity
            result = {'purpose_code': 'OTHR', 'confidence': 0.3}
            enhanced = self.enhancer.enhance_classification(result, "Payment to vendor")

            # Should enhance to SUPP
            self.assertEqual(enhanced['category_purpose_code'], 'SUPP')
            self.assertGreaterEqual(enhanced['category_confidence'], 0.7)
            self.assertTrue(enhanced['category_enhanced'])
            self.assertEqual(enhanced['category_enhancement_applied'], 'category_purpose_enhancer_semantic')
        finally:
            # Restore original method
            self.enhancer.semantic_similarity_match = original_semantic_similarity_match

    def test_mapper_integration(self):
        """Test integration with the category purpose mapper."""
        # Mock the mapper to return different values
        self.enhancer.mapper.map_purpose_to_category.return_value = ('SALA', 0.9, 'Mocked mapping')

        # Test with purpose code that doesn't have direct mapping
        result = {'purpose_code': 'CUSTOM', 'confidence': 0.3}
        enhanced = self.enhancer.enhance_classification(result, "Custom payment")

        # Should use the mapper result
        self.assertEqual(enhanced['category_purpose_code'], 'SALA')
        self.assertGreaterEqual(enhanced['category_confidence'], 0.9)
        self.assertTrue(enhanced['category_enhanced'])
        self.assertEqual(enhanced['category_enhancement_applied'], 'category_purpose_enhancer_semantic')

    def test_fallback_strategies(self):
        """Test fallback strategies."""
        # Mock the mapper to return None
        self.enhancer.mapper.map_purpose_to_category.return_value = (None, 0.0, 'No mapping')

        # Mock the direct mappings
        self.enhancer.mapper.direct_mappings = {'SALA': 'SALA'}

        # Test with purpose code that has direct mapping
        result = {'purpose_code': 'SALA', 'confidence': 0.3}
        enhanced = self.enhancer.enhance_classification(result, "Custom payment")

        # Should fallback to direct mapping
        self.assertEqual(enhanced['category_purpose_code'], 'SALA')
        self.assertGreaterEqual(enhanced['category_confidence'], 0.7)
        self.assertTrue(enhanced['category_enhanced'])
        self.assertEqual(enhanced['category_enhancement_applied'], 'category_purpose_enhancer_semantic')

        # Test with purpose code that doesn't have direct mapping
        result = {'purpose_code': 'CUSTOM', 'confidence': 0.3}
        enhanced = self.enhancer.enhance_classification(result, "Custom payment")

        # Should fallback to SUPP
        self.assertEqual(enhanced['category_purpose_code'], 'SUPP')
        self.assertGreaterEqual(enhanced['category_confidence'], 0.5)
        self.assertTrue(enhanced['category_enhanced'])
        self.assertEqual(enhanced['category_enhancement_applied'], 'category_purpose_enhancer_semantic')

    def test_no_override_high_confidence(self):
        """Test not overriding high confidence classifications."""
        # Test with high confidence
        result = {'purpose_code': 'SALA', 'confidence': 0.95, 'category_purpose_code': 'SALA', 'category_confidence': 0.95}
        enhanced = self.enhancer.enhance_classification(result, "Salary payment")

        # Should not override
        self.assertEqual(enhanced['category_purpose_code'], 'SALA')
        self.assertEqual(enhanced['category_confidence'], 0.95)
        self.assertFalse('category_enhanced' in enhanced)

    def test_never_returns_othr(self):
        """Test that the enhancer never returns OTHR as a category purpose code."""
        # Mock the mapper to return OTHR
        self.enhancer.mapper.map_purpose_to_category.return_value = ('OTHR', 0.5, 'OTHR mapping')

        # Test with OTHR purpose code
        result = {'purpose_code': 'OTHR', 'confidence': 0.3}
        enhanced = self.enhancer.enhance_classification(result, "Unknown payment")

        # Should never return OTHR
        self.assertNotEqual(enhanced['category_purpose_code'], 'OTHR')
        self.assertEqual(enhanced['category_purpose_code'], 'SUPP')  # Default fallback
        self.assertGreaterEqual(enhanced['category_confidence'], 0.5)
        self.assertTrue(enhanced['category_enhanced'])
        self.assertEqual(enhanced['category_enhancement_applied'], 'category_purpose_enhancer_semantic')

if __name__ == '__main__':
    unittest.main()
