"""
Semantic Education Enhancer for Purpose Code Classification.

This module provides a specialized enhancer for education-related transactions,
using semantic pattern matching to identify education payments with high accuracy.
"""

import logging
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer

logger = logging.getLogger(__name__)

class EducationEnhancerSemantic(SemanticEnhancer):
    """
    Specialized enhancer for education-related transactions.

    Uses semantic pattern matching to identify education payments
    with high accuracy and confidence.
    """

    def __init__(self, matcher=None):
        """
        Initialize with optional matcher.
        
        Args:
            matcher: Optional SemanticPatternMatcher instance to use
        """
        super().__init__(matcher=matcher)

        # Initialize education-specific patterns and contexts
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize education-specific patterns and contexts."""
        # Direct education keywords
        self.direct_keywords = {
            'EDUC': [
                'tuition', 'school fee', 'college fee', 'university fee',
                'education payment', 'student loan', 'school payment',
                'course fee', 'education fee', 'academic fee',
                'scholarship', 'bursary', 'student grant',
                'tuition payment', 'tuition fee', 'semester fee',
                'academic payment', 'student payment', 'educational expenses',
                'educational costs', 'academic expenses', 'tuition and fees',
                'school tuition', 'university tuition', 'college tuition'
            ]
        }

        # Semantic context patterns for education
        self.context_patterns = [
            {
                'purpose_code': 'EDUC',
                'keywords': ['tuition', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'EDUC',
                'keywords': ['school', 'fee'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'EDUC',
                'keywords': ['college', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'EDUC',
                'keywords': ['university', 'fee'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'EDUC',
                'keywords': ['student', 'loan'],
                'proximity': 3,
                'weight': 0.8
            },
            {
                'purpose_code': 'EDUC',
                'keywords': ['course', 'registration'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'EDUC',
                'keywords': ['education', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'EDUC',
                'keywords': ['academic', 'fee'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'EDUC',
                'keywords': ['semester', 'payment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'EDUC',
                'keywords': ['scholarship', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'EDUC',
                'keywords': ['student', 'housing'],
                'proximity': 5,
                'weight': 0.7
            },
            {
                'purpose_code': 'EDUC',
                'keywords': ['dormitory', 'payment'],
                'proximity': 5,
                'weight': 0.7
            }
        ]

        # Education-related terms for semantic similarity
        self.semantic_terms = [
            {'purpose_code': 'EDUC', 'term': 'education', 'threshold': 0.7, 'weight': 1.0},
            {'purpose_code': 'EDUC', 'term': 'tuition', 'threshold': 0.7, 'weight': 1.0},
            {'purpose_code': 'EDUC', 'term': 'school', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'EDUC', 'term': 'college', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'EDUC', 'term': 'university', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'EDUC', 'term': 'student', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'EDUC', 'term': 'academic', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'EDUC', 'term': 'scholarship', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'EDUC', 'term': 'course', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'EDUC', 'term': 'semester', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'EDUC', 'term': 'degree', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'EDUC', 'term': 'diploma', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'EDUC', 'term': 'certificate', 'threshold': 0.7, 'weight': 0.7},
            {'purpose_code': 'EDUC', 'term': 'undergraduate', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'EDUC', 'term': 'graduate', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'EDUC', 'term': 'postgraduate', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'EDUC', 'term': 'faculty', 'threshold': 0.7, 'weight': 0.7},
            {'purpose_code': 'EDUC', 'term': 'professor', 'threshold': 0.7, 'weight': 0.7},
            {'purpose_code': 'EDUC', 'term': 'lecturer', 'threshold': 0.7, 'weight': 0.7},
            {'purpose_code': 'EDUC', 'term': 'teacher', 'threshold': 0.7, 'weight': 0.7}
        ]

        # Negative indicators (not education)
        self.negative_indicators = [
            'office supplies', 'office stationery', 'office equipment',
            'office furniture', 'office materials'
        ]

    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification for education-related transactions.

        Args:
            result: Initial classification result
            narration: Transaction narration
            message_type: Optional message type

        Returns:
            dict: Enhanced classification result
        """
        logger.debug(f"Education enhancer called with narration: {narration}")

        # First, check for high confidence classifications that should not be overridden
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)

        # Don't override high confidence classifications
        if confidence >= 0.95:
            logger.debug(f"Not overriding high confidence classification: {purpose_code} ({confidence})")
            return result

        # Don't override if narration contains "professional services"
        narration_lower = narration.lower()
        if "professional services" in narration_lower:
            logger.debug("Not overriding professional services")
            return result

        # Check for negative indicators
        for indicator in self.negative_indicators:
            if indicator.lower() in narration_lower:
                logger.debug(f"Negative indicator found: {indicator}")
                # This is clearly office supplies, not education
                return self._create_enhanced_result(result, "GDDS", 0.95, f"Negative indicator match: {indicator}")

        # Call the base implementation first
        enhanced_result = super().enhance_classification(result, narration, message_type)

        # If the base implementation changed something, return it
        if enhanced_result != result:
            # Ensure category purpose code is set to FCOL for education
            if enhanced_result.get('purpose_code') == "EDUC":
                enhanced_result['category_purpose_code'] = "FCOL"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "education_category_mapping"
            return enhanced_result

        # Check if we should override the current classification
        if self.should_override_classification(result, narration):
            logger.info(f"Overriding {purpose_code} with EDUC based on context analysis")
            enhanced_result = self._create_enhanced_result(result, 'EDUC', 0.85, "Context analysis override")

            # Ensure category purpose code is set to FCOL for education
            enhanced_result['category_purpose_code'] = "FCOL"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "education_category_mapping"

            return enhanced_result

        # Message type specific considerations
        if message_type == "MT103":
            # MT103 is commonly used for tuition payments
            if any(term in narration_lower for term in ['tuition', 'education', 'school', 'college', 'university']):
                logger.info(f"MT103 education context detected")
                enhanced_result = self._create_enhanced_result(result, 'EDUC', 0.85, "MT103 education context")

                # Ensure category purpose code is set to FCOL for education
                enhanced_result['category_purpose_code'] = "FCOL"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "education_category_mapping"

                return enhanced_result

        # No education pattern detected
        logger.debug("No education pattern detected")
        return result

    def should_override_classification(self, result, narration):
        """
        Determine if education classification should override existing classification.

        Args:
            result: Current classification result
            narration: Transaction narration

        Returns:
            bool: True if should override
        """
        narration_lower = narration.lower()
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)

        # Check for strong education context
        education_terms = ['tuition', 'school', 'college', 'university', 'education', 'academic', 'student']
        education_count = sum(1 for term in education_terms if term in narration_lower)

        # If multiple education terms are present, likely education-related
        if education_count >= 2:
            # Don't override if confidence is very high
            if confidence >= 0.9:
                return False

            # Override OTHR or low confidence classifications
            if purpose_code == 'OTHR' or confidence < 0.7:
                return True

            # Override service-related codes with medium confidence
            if purpose_code in ['SCVE', 'SERV', 'SUPP'] and confidence < 0.8:
                return True

        # Special case for "professional services" - never override
        if "professional services" in narration_lower:
            return False

        # Don't override other classifications unless very strong evidence
        return False
