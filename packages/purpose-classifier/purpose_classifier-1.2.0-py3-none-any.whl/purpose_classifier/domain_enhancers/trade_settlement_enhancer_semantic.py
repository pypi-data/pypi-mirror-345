"""
Semantic Trade Settlement Enhancer for Purpose Code Classification.

This module provides a specialized enhancer for trade settlement-related transactions,
using semantic pattern matching to identify trade settlements with high accuracy.
"""

import logging
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer

logger = logging.getLogger(__name__)

class TradeSettlementEnhancerSemantic(SemanticEnhancer):
    """
    Specialized enhancer for trade settlement-related transactions.

    Uses semantic pattern matching to identify trade settlements
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

        # Initialize trade settlement-specific patterns and contexts
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize trade settlement-specific patterns and contexts."""
        # Direct trade settlement keywords
        self.direct_keywords = {
            'CORT': [
                'trade settlement', 'trade settlement payment', 'trade settlement transaction',
                'settlement of trade', 'settlement for trade', 'settlement of transaction',
                'settlement for transaction', 'trade settlement for export', 'trade settlement for import',
                'settlement of trade for export', 'settlement of trade for import',
                'settlement for trade for export', 'settlement for trade for import',
                'settlement of transaction for goods', 'settlement of transaction for services',
                'settlement for transaction for goods', 'settlement for transaction for services',
                'trade settlement for securities', 'trade settlement for commodities',
                'trade settlement for foreign exchange', 'trade settlement for forex',
                'trade settlement for fx', 'trade settlement for derivatives',
                'trade settlement for options', 'trade settlement for futures',
                'trade settlement for swaps', 'trade settlement for forwards',
                'trade settlement for spot', 'trade settlement for otc',
                'trade settlement for over-the-counter', 'trade settlement for exchange-traded',
                'trade settlement for etd', 'trade settlement for listed',
                'trade settlement for unlisted', 'trade settlement for otc derivatives',
                'trade settlement for exchange-traded derivatives', 'trade settlement for etd derivatives'
            ]
        }

        # Semantic context patterns for trade settlements
        self.context_patterns = [
            # CORT patterns
            {
                'purpose_code': 'CORT',
                'keywords': ['trade', 'settlement'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'CORT',
                'keywords': ['trade', 'settlement', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CORT',
                'keywords': ['settlement', 'of', 'trade'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CORT',
                'keywords': ['settlement', 'for', 'trade'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CORT',
                'keywords': ['settlement', 'of', 'transaction'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CORT',
                'keywords': ['settlement', 'for', 'transaction'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CORT',
                'keywords': ['trade', 'settlement', 'export'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CORT',
                'keywords': ['trade', 'settlement', 'import'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CORT',
                'keywords': ['settlement', 'transaction', 'goods'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CORT',
                'keywords': ['settlement', 'transaction', 'services'],
                'proximity': 5,
                'weight': 0.9
            }
        ]

        # Trade settlement-related terms for semantic similarity
        self.semantic_terms = [
            {'purpose_code': 'CORT', 'term': 'trade', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'CORT', 'term': 'settlement', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'CORT', 'term': 'transaction', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'CORT', 'term': 'export', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CORT', 'term': 'import', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CORT', 'term': 'goods', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CORT', 'term': 'services', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CORT', 'term': 'securities', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CORT', 'term': 'commodities', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CORT', 'term': 'forex', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CORT', 'term': 'derivatives', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CORT', 'term': 'options', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CORT', 'term': 'futures', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CORT', 'term': 'swaps', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CORT', 'term': 'forwards', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CORT', 'term': 'spot', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CORT', 'term': 'otc', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CORT', 'term': 'exchange', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CORT', 'term': 'listed', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CORT', 'term': 'unlisted', 'threshold': 0.7, 'weight': 0.8}
        ]

    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification for trade settlement-related transactions.

        Args:
            result: Initial classification result
            narration: Transaction narration
            message_type: Optional message type

        Returns:
            dict: Enhanced classification result
        """
        logger.debug(f"Trade settlement enhancer called with narration: {narration}")

        # First, check for high confidence classifications that should not be overridden
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)

        # Don't override high confidence classifications
        if confidence >= 0.95:
            logger.debug(f"Not overriding high confidence classification: {purpose_code} ({confidence})")
            return result

        narration_lower = narration.lower()

        # Special case for trade settlement
        if 'trade settlement' in narration_lower or 'settlement of trade' in narration_lower or 'settlement for trade' in narration_lower:
            logger.info(f"Trade settlement detected, overriding {purpose_code} with CORT")
            enhanced_result = self._create_enhanced_result(result, 'CORT', 0.99, "Trade settlement detected")

            # Ensure category purpose code is set to CORT for trade settlement
            enhanced_result['category_purpose_code'] = "CORT"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "trade_settlement_category_mapping"

            # Set high priority and final override to ensure this takes precedence
            enhanced_result['priority'] = 1000
            enhanced_result['final_override'] = True
            enhanced_result['force_purpose_code'] = True
            enhanced_result['force_category_purpose_code'] = True

            return enhanced_result

        # Special case for transaction settlement
        if ('settlement of transaction' in narration_lower or 'settlement for transaction' in narration_lower) and ('goods' in narration_lower or 'services' in narration_lower):
            logger.info(f"Transaction settlement detected, overriding {purpose_code} with CORT")
            enhanced_result = self._create_enhanced_result(result, 'CORT', 0.99, "Transaction settlement detected")

            # Ensure category purpose code is set to CORT for transaction settlement
            enhanced_result['category_purpose_code'] = "CORT"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "trade_settlement_category_mapping"

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
            # Ensure category purpose code is set appropriately for trade settlement codes
            if enhanced_result.get('purpose_code') == "CORT":
                enhanced_result['category_purpose_code'] = "CORT"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "trade_settlement_category_mapping"
            return enhanced_result

        # Check if we should override the current classification
        if self.should_override_classification(result, narration):
            logger.info(f"Overriding {purpose_code} with CORT based on context analysis")
            enhanced_result = self._create_enhanced_result(result, 'CORT', 0.95, "Context analysis override")

            # Ensure category purpose code is set to CORT for trade settlement
            enhanced_result['category_purpose_code'] = "CORT"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "trade_settlement_category_mapping"

            return enhanced_result

        # No trade settlement pattern detected
        logger.debug("No trade settlement pattern detected")
        return result

    def should_override_classification(self, result, narration):
        """
        Determine if trade settlement classification should override existing classification.

        Args:
            result: Current classification result
            narration: Transaction narration

        Returns:
            bool: True if should override
        """
        narration_lower = narration.lower()
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)

        # Check for strong trade settlement context
        trade_terms = ['trade', 'settlement', 'transaction', 'export', 'import', 'goods', 'services']
        trade_count = sum(1 for term in trade_terms if term in narration_lower)

        # If multiple trade terms are present, likely trade settlement-related
        if trade_count >= 3:
            # Don't override if confidence is very high
            if confidence >= 0.9:
                return False

            # Override OTHR or low confidence classifications
            if purpose_code == 'OTHR' or confidence < 0.7:
                return True

            # Override trade-related codes with medium confidence
            if purpose_code in ['TRAD', 'GDDS', 'SERV'] and confidence < 0.8:
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
        enhanced_result['enhancement_applied'] = f"trade_settlement_enhancer:{reason}"
        result['enhanced'] = True
        return enhanced_result
