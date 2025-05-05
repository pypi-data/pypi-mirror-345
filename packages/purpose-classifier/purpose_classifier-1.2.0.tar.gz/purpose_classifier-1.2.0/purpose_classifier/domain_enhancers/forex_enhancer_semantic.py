"""
Forex domain enhancer for purpose code classification.

This enhancer specializes in forex-related narrations and improves the classification
of forex-related purpose codes such as FREX.
"""

import re
import logging
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer

logger = logging.getLogger(__name__)

class ForexEnhancerSemantic(SemanticEnhancer):
    """
    Enhancer for forex-related narrations.

    This enhancer improves the classification of forex-related purpose codes by
    analyzing the narration for specific forex-related keywords and patterns.
    """

    def __init__(self, matcher=None):
        """
        Initialize with optional matcher.

        Args:
            matcher: Optional SemanticPatternMatcher instance to use
        """
        super().__init__(matcher=matcher)

        # Define forex-related keywords
        self.forex_keywords = [
            'forex', 'fx', 'foreign exchange', 'currency', 'exchange rate',
            'swap', 'forward', 'spot', 'settlement', 'currency pair',
            'usd', 'eur', 'gbp', 'jpy', 'chf', 'aud', 'cad', 'nzd'
        ]

        # Define forex-related patterns
        self.forex_patterns = [
            r'\b(forex|foreign exchange|fx)\b.*?\b(settlement|payment|transfer|transaction|cover)\b',
            r'\b(payment|transfer|transaction|cover)\b.*?\b(forex|foreign exchange|fx)\b',
            r'\b(cover|covering)\b.*?\b(for|of)\b.*?\b(forex|foreign exchange|fx)\b',
            r'\b(USD|EUR|GBP|JPY|CHF|AUD|CAD|NZD)/(USD|EUR|GBP|JPY|CHF|AUD|CAD|NZD)\b',
            r'\b(settlement|payment)\b.*?\b(of|for)\b.*?\b(fx|forex|foreign exchange)\b',
            r'\bfx\s+(forward|swap|spot)\b',
            r'\b(forward|swap|spot)\s+fx\b',
            r'\b(currency|exchange)\s+(settlement|transaction|trading)\b'
        ]

        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.forex_patterns]

    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification for forex-related transactions.

        Args:
            result: Initial classification result
            narration: Transaction narration
            message_type: Optional message type

        Returns:
            dict: Enhanced classification result
        """
        logger.debug(f"Forex enhancer called with narration: {narration}")

        # Get current purpose code and confidence
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)

        # Don't override if already classified as FREX with high confidence
        if purpose_code == 'FREX' and confidence >= 0.8:
            logger.debug(f"Already classified as FREX with high confidence: {confidence}")
            return result

        # Skip if this is an interbank transaction
        narration_lower = narration.lower()
        if 'interbank' in narration_lower or 'nostro' in narration_lower or 'vostro' in narration_lower:
            logger.info(f"Skipping forex enhancer for interbank transaction: {narration}")
            return result

        # Check for forex patterns
        for pattern in self.compiled_patterns:
            if pattern.search(narration):
                logger.info(f"Forex pattern matched: {pattern.pattern}")
                return self._create_enhanced_result(result, 'FREX', 0.95, "forex_pattern_match")

        # Check for currency pairs
        if re.search(r'\b(USD|EUR|GBP|JPY|CHF|AUD|CAD|NZD)/(USD|EUR|GBP|JPY|CHF|AUD|CAD|NZD)\b', narration):
            logger.info(f"Currency pair detected in narration")
            return self._create_enhanced_result(result, 'FREX', 0.95, "currency_pair_match")

        # Check for forex keywords
        for keyword in self.forex_keywords:
            if keyword in narration_lower:
                logger.info(f"Forex keyword match: {keyword} with confidence 0.90")
                return self._create_enhanced_result(result, 'FREX', 0.90, f"forex_keyword_{keyword}")

        # Semantic matching for forex-related terms
        forex_terms = ['forex', 'foreign exchange', 'currency', 'fx']
        settlement_terms = ['settlement', 'payment', 'transaction', 'trade']

        # Check semantic similarity for forex terms
        for forex_term in forex_terms:
            forex_similarity = self.semantic_matcher.get_similarity(forex_term, narration_lower)
            if forex_similarity > 0.8:
                logger.info(f"Semantic match for forex term: {forex_term} with similarity {forex_similarity}")

                # Check if there's also a settlement term nearby
                for settlement_term in settlement_terms:
                    settlement_similarity = self.semantic_matcher.get_similarity(settlement_term, narration_lower)
                    if settlement_similarity > 0.7:
                        logger.info(f"Semantic match for settlement term: {settlement_term} with similarity {settlement_similarity}")
                        combined_confidence = (forex_similarity + settlement_similarity) / 2
                        return self._create_enhanced_result(result, 'FREX', combined_confidence, "semantic_forex_match")

        # Special handling for MT202 and MT202COV message types
        if message_type in ['MT202', 'MT202COV']:
            # These message types are often used for forex settlements
            if any(term in narration_lower for term in ['settlement', 'forward', 'swap', 'spot']):
                logger.info(f"MT202 forex settlement detected")
                return self._create_enhanced_result(result, 'FREX', 0.85, "mt202_forex_settlement")

        # Return original result if no enhancement applied
        return result

    def _create_enhanced_result(self, result, purpose_code, confidence, enhancement_type):
        """
        Create an enhanced result with the new purpose code and confidence.

        Args:
            result: Original result dictionary
            purpose_code: New purpose code
            confidence: New confidence score
            enhancement_type: Type of enhancement applied

        Returns:
            dict: Enhanced result
        """
        # Create a copy of the original result
        enhanced_result = result.copy()

        # Update with new purpose code and confidence
        enhanced_result['purpose_code'] = purpose_code
        enhanced_result['confidence'] = confidence
        enhanced_result['enhanced'] = True
        enhanced_result['enhancer'] = 'forex'
        enhanced_result['enhancement_applied'] = f"forex_enhancer_{enhancement_type}"

        # Add reason based on enhancement type
        if enhancement_type == "forex_pattern_match":
            enhanced_result['reason'] = "Forex pattern match in narration"
        elif enhancement_type == "currency_pair_match":
            enhanced_result['reason'] = "Currency pair detected in narration"
        elif enhancement_type.startswith("forex_keyword_"):
            keyword = enhancement_type.replace("forex_keyword_", "")
            enhanced_result['reason'] = f"Forex keyword match: {keyword}"
        elif enhancement_type == "semantic_forex_match":
            enhanced_result['reason'] = "Semantic match for forex-related terms"
        elif enhancement_type == "mt202_forex_settlement":
            enhanced_result['reason'] = "MT202 forex settlement detected"
        else:
            enhanced_result['reason'] = "Forex-related transaction"

        result['enhanced'] = True

        # Also update category purpose code to match
        enhanced_result['category_purpose_code'] = purpose_code
        enhanced_result['category_confidence'] = confidence

        logger.info(f"Enhanced purpose code: {purpose_code}, confidence: {confidence}, enhancement applied: forex_enhancer_{enhancement_type}, reason: {enhanced_result['reason']}")

        return enhanced_result
