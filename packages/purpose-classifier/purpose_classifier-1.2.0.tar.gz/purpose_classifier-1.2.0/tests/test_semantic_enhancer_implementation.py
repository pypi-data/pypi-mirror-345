#!/usr/bin/env python
"""
Test script for the semantic enhancer implementation (Phase 5).

This script tests the implementation of Phase 5 of the implementation plan,
which involves updating the SemanticEnhancer class and creating a migration
script to convert existing enhancers to use the semantic approach.
"""

import os
import sys
import logging
import unittest

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer
from purpose_classifier.domain_enhancers.education_enhancer_semantic import EducationEnhancerSemantic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestSemanticEnhancerImplementation(unittest.TestCase):
    """Test case for semantic enhancer implementation."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize enhancers
        self.base_enhancer = SemanticEnhancer()
        self.education_enhancer = EducationEnhancerSemantic()

        # Check if word embeddings are loaded in base enhancer
        if hasattr(self.base_enhancer, 'matcher') and hasattr(self.base_enhancer.matcher, 'embeddings') and self.base_enhancer.matcher.embeddings:
            logger.info("Word embeddings are loaded in the base semantic enhancer")
            # Try to calculate semantic similarity
            similarity = self.base_enhancer.matcher.semantic_similarity("payment", "transfer")
            logger.info(f"Semantic similarity between 'payment' and 'transfer': {similarity}")
        else:
            logger.error("Word embeddings are NOT loaded in the base semantic enhancer")

        # Check if word embeddings are loaded in education enhancer
        if hasattr(self.education_enhancer, 'matcher') and hasattr(self.education_enhancer.matcher, 'embeddings') and self.education_enhancer.matcher.embeddings:
            logger.info("Word embeddings are loaded in the education enhancer semantic")
            # Try to calculate semantic similarity
            similarity = self.education_enhancer.matcher.semantic_similarity("education", "university")
            logger.info(f"Semantic similarity between 'education' and 'university': {similarity}")
        else:
            logger.error("Word embeddings are NOT loaded in the education enhancer semantic")

    def test_base_semantic_enhancer(self):
        """Test the base semantic enhancer."""
        # Test direct keyword match
        result = {'purpose_code': 'OTHR', 'confidence': 0.3}
        narration = "This is a test narration"

        # Base enhancer should not modify the result
        enhanced = self.base_enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced, result)

    def test_education_enhancer_direct_match(self):
        """Test the education enhancer with direct keyword match."""
        # Test direct keyword match
        result = {'purpose_code': 'OTHR', 'confidence': 0.3}
        narration = "Payment for tuition fee for university"

        # Education enhancer should identify this as EDUC
        enhanced = self.education_enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'EDUC')
        self.assertGreater(enhanced['confidence'], 0.9)
        self.assertEqual(enhanced['category_purpose_code'], 'FCOL')

    def test_education_enhancer_context_match(self):
        """Test the education enhancer with context pattern match."""
        # Test context pattern match
        result = {'purpose_code': 'OTHR', 'confidence': 0.3}
        narration = "Payment to State University for semester registration"

        # Education enhancer should identify this as EDUC
        enhanced = self.education_enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'EDUC')
        self.assertGreater(enhanced['confidence'], 0.8)
        self.assertEqual(enhanced['category_purpose_code'], 'FCOL')

    def test_education_enhancer_negative_indicator(self):
        """Test the education enhancer with negative indicator."""
        # Test negative indicator
        result = {'purpose_code': 'OTHR', 'confidence': 0.3}
        narration = "Payment for office supplies and stationery"

        # Education enhancer should identify this as GDDS
        enhanced = self.education_enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'GDDS')
        self.assertGreater(enhanced['confidence'], 0.9)

    def test_education_enhancer_override(self):
        """Test the education enhancer override logic."""
        # Test override logic
        result = {'purpose_code': 'SCVE', 'confidence': 0.6}
        narration = "Payment to University of California for student tuition"

        # Education enhancer should override SCVE with EDUC
        enhanced = self.education_enhancer.enhance_classification(result, narration)
        self.assertEqual(enhanced['purpose_code'], 'EDUC')
        self.assertGreater(enhanced['confidence'], 0.8)
        self.assertEqual(enhanced['category_purpose_code'], 'FCOL')

    def test_education_enhancer_no_override(self):
        """Test the education enhancer no override case."""
        # Test no override case
        result = {'purpose_code': 'SCVE', 'confidence': 0.95}
        narration = "Payment for professional services"

        # Education enhancer should not override high confidence SCVE
        enhanced = self.education_enhancer.enhance_classification(result, narration)
        # Just check that the purpose code and confidence are preserved
        self.assertEqual(enhanced['purpose_code'], result['purpose_code'])
        self.assertEqual(enhanced['confidence'], result['confidence'])

    def test_education_enhancer_mt103(self):
        """Test the education enhancer with MT103 message type."""
        # Test MT103 message type
        result = {'purpose_code': 'OTHR', 'confidence': 0.3}
        narration = "Payment to State College"

        # Education enhancer should identify this as EDUC with MT103
        enhanced = self.education_enhancer.enhance_classification(result, narration, message_type="MT103")
        self.assertEqual(enhanced['purpose_code'], 'EDUC')
        self.assertGreater(enhanced['confidence'], 0.8)
        self.assertEqual(enhanced['category_purpose_code'], 'FCOL')

if __name__ == '__main__':
    unittest.main()
