"""
Semantic Government Payment Enhancer for Purpose Code Classification.

This module provides a specialized enhancer for government-related transactions,
using semantic pattern matching to identify government payments with high accuracy.
"""

import logging
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer

logger = logging.getLogger(__name__)

class GovernmentPaymentEnhancerSemantic(SemanticEnhancer):
    """
    Specialized enhancer for government-related transactions.

    Uses semantic pattern matching to identify government payments
    with high accuracy and confidence.
    """

    def __init__(self, matcher=None):
        """
        Initialize with optional matcher.
        
        Args:
            matcher: Optional SemanticPatternMatcher instance to use
        """
        super().__init__(matcher=matcher)

        # Set high priority to ensure it's called before general enhancers
        self.priority = 150

        # Initialize government payment-specific patterns and contexts
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize government payment-specific patterns and contexts."""
        # Direct government payment keywords
        self.direct_keywords = {
            'GOVT': [
                'government payment', 'government transaction', 'payment to government',
                'transaction to government', 'payment from government', 'transaction from government',
                'government fee', 'government charge', 'government tax', 'government levy',
                'government duty', 'government fine', 'government penalty', 'government service',
                'government program', 'government initiative', 'government project',
                'government contract', 'government procurement', 'government purchase',
                'government acquisition', 'government expenditure', 'government expense',
                'government disbursement', 'government outlay', 'government spending',
                'government budget', 'government allocation', 'government appropriation',
                'government grant', 'government subsidy', 'government subvention',
                'government aid', 'government assistance', 'government support',
                'government funding', 'government financing', 'government investment',
                'government loan', 'government credit', 'government advance',
                'government payment for services', 'government payment for goods'
            ],
            'GOVI': [
                'government insurance', 'government insurance payment', 'government insurance premium',
                'government insurance contribution', 'government insurance fee', 'government insurance charge',
                'government insurance tax', 'government insurance levy', 'government insurance duty',
                'government insurance fine', 'government insurance penalty', 'government insurance service',
                'government insurance program', 'government insurance initiative', 'government insurance project',
                'government insurance contract', 'government insurance procurement', 'government insurance purchase',
                'government insurance acquisition', 'government insurance expenditure', 'government insurance expense',
                'government insurance disbursement', 'government insurance outlay', 'government insurance spending',
                'government insurance budget', 'government insurance allocation', 'government insurance appropriation',
                'government insurance grant', 'government insurance subsidy', 'government insurance subvention',
                'government insurance aid', 'government insurance assistance', 'government insurance support',
                'government insurance funding', 'government insurance financing', 'government insurance investment',
                'government insurance loan', 'government insurance credit', 'government insurance advance',
                'government health insurance', 'government life insurance', 'government property insurance',
                'government casualty insurance', 'government liability insurance', 'government auto insurance',
                'government home insurance', 'government business insurance', 'government commercial insurance'
            ]
        }

        # Semantic context patterns for government payments
        self.context_patterns = [
            # GOVT patterns
            {
                'purpose_code': 'GOVT',
                'keywords': ['government', 'payment'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'GOVT',
                'keywords': ['government', 'transaction'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'GOVT',
                'keywords': ['payment', 'to', 'government'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'GOVT',
                'keywords': ['transaction', 'to', 'government'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'GOVT',
                'keywords': ['payment', 'from', 'government'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'GOVT',
                'keywords': ['transaction', 'from', 'government'],
                'proximity': 5,
                'weight': 0.9
            },

            # GOVI patterns
            {
                'purpose_code': 'GOVI',
                'keywords': ['government', 'insurance'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'GOVI',
                'keywords': ['government', 'insurance', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'GOVI',
                'keywords': ['government', 'insurance', 'premium'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'GOVI',
                'keywords': ['government', 'health', 'insurance'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'GOVI',
                'keywords': ['government', 'life', 'insurance'],
                'proximity': 5,
                'weight': 0.9
            }
        ]

        # Government payment-related terms for semantic similarity
        self.semantic_terms = [
            {'purpose_code': 'GOVT', 'term': 'government', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'GOVT', 'term': 'payment', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'GOVT', 'term': 'transaction', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'GOVT', 'term': 'fee', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVT', 'term': 'charge', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVT', 'term': 'tax', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVT', 'term': 'levy', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVT', 'term': 'duty', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVT', 'term': 'fine', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVT', 'term': 'penalty', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVT', 'term': 'service', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVT', 'term': 'program', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVT', 'term': 'initiative', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVT', 'term': 'project', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVT', 'term': 'contract', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVT', 'term': 'procurement', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVT', 'term': 'purchase', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVT', 'term': 'acquisition', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVT', 'term': 'expenditure', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVT', 'term': 'expense', 'threshold': 0.7, 'weight': 0.8},

            {'purpose_code': 'GOVI', 'term': 'government', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'GOVI', 'term': 'insurance', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'GOVI', 'term': 'payment', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'GOVI', 'term': 'premium', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'GOVI', 'term': 'contribution', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVI', 'term': 'fee', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVI', 'term': 'charge', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVI', 'term': 'health', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVI', 'term': 'life', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVI', 'term': 'property', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVI', 'term': 'casualty', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVI', 'term': 'liability', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVI', 'term': 'auto', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVI', 'term': 'home', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVI', 'term': 'business', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GOVI', 'term': 'commercial', 'threshold': 0.7, 'weight': 0.8}
        ]

    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification for government-related transactions.

        Args:
            result: Initial classification result
            narration: Transaction narration
            message_type: Optional message type

        Returns:
            dict: Enhanced classification result
        """
        logger.debug(f"Government payment enhancer called with narration: {narration}")

        # First, check for high confidence classifications that should not be overridden
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)

        # Don't override high confidence classifications
        if confidence >= 0.95:
            logger.debug(f"Not overriding high confidence classification: {purpose_code} ({confidence})")
            return result

        narration_lower = narration.lower()

        # Special case for government insurance
        if 'government insurance' in narration_lower:
            logger.info(f"Government insurance detected, overriding {purpose_code} with GOVI")
            enhanced_result = self._create_enhanced_result(result, 'GOVI', 0.99, "Government insurance detected")

            # Ensure category purpose code is set to GOVI for government insurance
            enhanced_result['category_purpose_code'] = "GOVI"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "government_payment_category_mapping"

            return enhanced_result

        # Special case for government payment
        if 'government payment' in narration_lower or 'payment from government' in narration_lower or 'payment to government' in narration_lower or ('government' in narration_lower and 'payment' in narration_lower):
            logger.info(f"Government payment detected, overriding {purpose_code} with GOVT")
            enhanced_result = self._create_enhanced_result(result, 'GOVT', 0.99, "Government payment detected")

            # Ensure category purpose code is set to GOVT for government payment
            enhanced_result['category_purpose_code'] = "GOVT"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "government_payment_category_mapping"

            # Set high priority and final override to ensure this takes precedence
            enhanced_result['priority'] = 1000
            enhanced_result['final_override'] = True
            enhanced_result['force_purpose_code'] = True
            enhanced_result['force_category_purpose_code'] = True

            return enhanced_result

        # Call the base implementation
        enhanced_result = super().enhance_classification(result, narration, message_type)

        # If the base implementation changed something, return it
        if enhanced_result != result:
            # Ensure category purpose code is set appropriately for government payment codes
            if enhanced_result.get('purpose_code') == "GOVT":
                enhanced_result['category_purpose_code'] = "GOVT"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "government_payment_category_mapping"
            elif enhanced_result.get('purpose_code') == "GOVI":
                enhanced_result['category_purpose_code'] = "GOVI"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "government_payment_category_mapping"
            return enhanced_result

        # Check if we should override the current classification
        if self.should_override_classification(result, narration):
            # Determine if government insurance or general government payment
            if 'insurance' in narration_lower:
                logger.info(f"Overriding {purpose_code} with GOVI based on context analysis")
                enhanced_result = self._create_enhanced_result(result, 'GOVI', 0.95, "Context analysis override")

                # Ensure category purpose code is set to GOVI for government insurance
                enhanced_result['category_purpose_code'] = "GOVI"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "government_payment_category_mapping"
            else:
                logger.info(f"Overriding {purpose_code} with GOVT based on context analysis")
                enhanced_result = self._create_enhanced_result(result, 'GOVT', 0.95, "Context analysis override")

                # Ensure category purpose code is set to GOVT for government payment
                enhanced_result['category_purpose_code'] = "GOVT"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "government_payment_category_mapping"

            return enhanced_result

        # No government payment pattern detected
        logger.debug("No government payment pattern detected")
        return result

    def should_override_classification(self, result, narration):
        """
        Determine if government payment classification should override existing classification.

        Args:
            result: Current classification result
            narration: Transaction narration

        Returns:
            bool: True if should override
        """
        narration_lower = narration.lower()
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)

        # Check for strong government payment context
        govt_terms = ['government', 'payment', 'transaction', 'fee', 'charge', 'tax', 'levy', 'duty', 'fine', 'penalty']
        govt_count = sum(1 for term in govt_terms if term in narration_lower)

        # Check for strong government insurance context
        govi_terms = ['government', 'insurance', 'premium', 'contribution', 'health', 'life', 'property', 'casualty', 'liability']
        govi_count = sum(1 for term in govi_terms if term in narration_lower)

        # If multiple government terms are present, likely government payment-related
        if govt_count >= 2 or govi_count >= 2:
            # Don't override if confidence is very high
            if confidence >= 0.9:
                return False

            # Override OTHR or low confidence classifications
            if purpose_code == 'OTHR' or confidence < 0.7:
                return True

            # Override related codes with medium confidence
            if purpose_code in ['GBEN', 'TAXS', 'INSU'] and confidence < 0.8:
                return True

        # Don't override other classifications unless very strong evidence
        return False

    def _create_enhanced_result(self, result, purpose_code, confidence, reason):
        """
        Create an enhanced result with the new purpose code and confidence.

        Args:
            result: Original result dictionary
            purpose_code: New purpose code
            confidence: New confidence value
            reason: Reason for enhancement

        Returns:
            dict: Enhanced result
        """
        enhanced_result = result.copy()
        enhanced_result['purpose_code'] = purpose_code
        enhanced_result['confidence'] = confidence
        enhanced_result['enhancement_applied'] = f"government_payment_enhancer:{reason}"
        result['enhanced'] = True
        return enhanced_result
