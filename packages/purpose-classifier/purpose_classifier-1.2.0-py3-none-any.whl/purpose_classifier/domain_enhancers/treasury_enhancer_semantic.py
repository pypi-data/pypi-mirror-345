"""
Semantic Treasury Enhancer for Purpose Code Classification.

This module provides a specialized enhancer for treasury-related transactions,
using semantic pattern matching to identify treasury operations with high accuracy.
"""

import logging
import re
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer

logger = logging.getLogger(__name__)

class TreasuryEnhancerSemantic(SemanticEnhancer):
    """
    Specialized enhancer for treasury-related transactions.

    Uses semantic pattern matching to identify treasury operations
    with high accuracy and confidence.
    """

    def __init__(self, matcher=None):
        """
        Initialize with optional matcher.
        
        Args:
            matcher: Optional SemanticPatternMatcher instance to use
        """
        super().__init__(matcher=matcher)

        # Initialize treasury-specific patterns and contexts
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize treasury-specific patterns and contexts."""
        # Direct treasury keywords (highest confidence)
        self.treasury_keywords = [
            'treasury', 'treasury operation', 'treasury management', 'treasury transfer',
            'treasury settlement', 'treasury transaction', 'treasury payment',
            'cash management', 'liquidity management', 'cash pooling',
            'intercompany transfer', 'intercompany settlement', 'intercompany payment',
            'intracompany transfer', 'intracompany settlement', 'intracompany payment',
            'internal transfer', 'internal settlement', 'internal payment',
            'nostro', 'vostro', 'nostro account', 'vostro account',
            'correspondent banking', 'correspondent account', 'correspondent transfer'
        ]

        # Map keywords to purpose codes
        self.direct_keywords = {
            'TREA': self.treasury_keywords
        }

        # Semantic context patterns for treasury operations
        self.treasury_contexts = [
            {"keywords": ["treasury", "operation"], "proximity": 5, "weight": 1.0},
            {"keywords": ["treasury", "management"], "proximity": 5, "weight": 1.0},
            {"keywords": ["treasury", "transfer"], "proximity": 5, "weight": 0.9},
            {"keywords": ["treasury", "settlement"], "proximity": 5, "weight": 0.9},
            {"keywords": ["treasury", "transaction"], "proximity": 5, "weight": 0.9},
            {"keywords": ["treasury", "payment"], "proximity": 5, "weight": 0.9},
            {"keywords": ["cash", "management"], "proximity": 5, "weight": 0.9},
            {"keywords": ["liquidity", "management"], "proximity": 5, "weight": 0.9},
            {"keywords": ["cash", "pooling"], "proximity": 5, "weight": 0.9},
            {"keywords": ["intercompany", "transfer"], "proximity": 5, "weight": 0.9},
            {"keywords": ["intercompany", "settlement"], "proximity": 5, "weight": 0.9},
            {"keywords": ["intercompany", "payment"], "proximity": 5, "weight": 0.9},
            {"keywords": ["intracompany", "transfer"], "proximity": 5, "weight": 0.9},
            {"keywords": ["intracompany", "settlement"], "proximity": 5, "weight": 0.9},
            {"keywords": ["intracompany", "payment"], "proximity": 5, "weight": 0.9},
            {"keywords": ["internal", "transfer"], "proximity": 5, "weight": 0.8},
            {"keywords": ["internal", "settlement"], "proximity": 5, "weight": 0.8},
            {"keywords": ["internal", "payment"], "proximity": 5, "weight": 0.8},
            {"keywords": ["nostro", "account"], "proximity": 5, "weight": 0.9},
            {"keywords": ["vostro", "account"], "proximity": 5, "weight": 0.9},
            {"keywords": ["correspondent", "banking"], "proximity": 5, "weight": 0.9},
            {"keywords": ["correspondent", "account"], "proximity": 5, "weight": 0.9},
            {"keywords": ["correspondent", "transfer"], "proximity": 5, "weight": 0.9}
        ]

        # Treasury-related terms for semantic similarity matching
        self.semantic_terms = [
            {"term": "treasury", "purpose_code": "TREA", "threshold": 0.7, "weight": 1.0},
            {"term": "operation", "purpose_code": "TREA", "threshold": 0.7, "weight": 0.7},
            {"term": "management", "purpose_code": "TREA", "threshold": 0.7, "weight": 0.7},
            {"term": "transfer", "purpose_code": "TREA", "threshold": 0.7, "weight": 0.7},
            {"term": "settlement", "purpose_code": "TREA", "threshold": 0.7, "weight": 0.7},
            {"term": "transaction", "purpose_code": "TREA", "threshold": 0.7, "weight": 0.7},
            {"term": "payment", "purpose_code": "TREA", "threshold": 0.7, "weight": 0.6},
            {"term": "cash", "purpose_code": "TREA", "threshold": 0.7, "weight": 0.8},
            {"term": "liquidity", "purpose_code": "TREA", "threshold": 0.7, "weight": 0.9},
            {"term": "pooling", "purpose_code": "TREA", "threshold": 0.7, "weight": 0.9},
            {"term": "intercompany", "purpose_code": "TREA", "threshold": 0.7, "weight": 0.9},
            {"term": "intracompany", "purpose_code": "TREA", "threshold": 0.7, "weight": 0.9},
            {"term": "internal", "purpose_code": "TREA", "threshold": 0.7, "weight": 0.7},
            {"term": "nostro", "purpose_code": "TREA", "threshold": 0.7, "weight": 0.9},
            {"term": "vostro", "purpose_code": "TREA", "threshold": 0.7, "weight": 0.9},
            {"term": "correspondent", "purpose_code": "TREA", "threshold": 0.7, "weight": 0.8},
            {"term": "banking", "purpose_code": "TREA", "threshold": 0.7, "weight": 0.6}
        ]

        # Negative indicators (patterns that suggest it's NOT a treasury operation)
        self.negative_indicators = [
            'not treasury', 'non-treasury', 'excluding treasury',
            'treasury free', 'no treasury', 'without treasury',
            'treasury tax', 'tax on treasury'  # These are tax payments, not treasury operations
        ]

        # Compile regex patterns for message type analysis
        self.mt202_pattern = re.compile(r'\b(MT202|MT 202|MT-202|MT202COV|MT 202 COV|MT-202-COV)\b', re.IGNORECASE)

    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification for treasury-related transactions.

        Args:
            result: Initial classification result
            narration: Transaction narration
            message_type: Optional message type

        Returns:
            dict: Enhanced classification result
        """
        logger.debug(f"Treasury enhancer called with narration: {narration}")

        # Get current purpose code and confidence
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)

        # Special case for exact match "TREASURY OPERATION"
        if narration.upper() == "TREASURY OPERATION":
            logger.info(f"Exact match for TREASURY OPERATION")
            enhanced_result = self._create_enhanced_result(result, 'TREA', 0.99, "exact_match_treasury_operation")

            # Ensure category purpose code is set to TREA
            enhanced_result['category_purpose_code'] = "TREA"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "treasury_category_mapping"

            return enhanced_result

        # Don't override if already classified as TREA with high confidence
        if purpose_code == 'TREA' and confidence >= 0.8:
            logger.debug(f"Already classified as TREA with high confidence: {confidence}")
            return result

        # Check for negative indicators
        narration_lower = narration.lower()
        for indicator in self.negative_indicators:
            if indicator in narration_lower:
                logger.debug(f"Negative indicator found: {indicator}")
                return result

        # Direct keyword matching (highest confidence)
        matched, keyword_confidence, keyword = self.direct_keyword_match(narration, 'TREA')
        if matched:
            logger.info(f"Treasury keyword match: {keyword} with confidence {keyword_confidence}")
            return self._create_enhanced_result(result, 'TREA', keyword_confidence, f"Direct treasury keyword match: {keyword}")

        # Semantic context pattern matching
        context_score = self.context_match(narration, self.treasury_contexts)
        if context_score >= 0.7:
            logger.info(f"Treasury context match with score: {context_score:.2f}")
            return self._create_enhanced_result(result, 'TREA', min(0.95, context_score),
                                              f"Treasury context match with score: {context_score:.2f}")

        # Semantic similarity matching
        matched, sem_confidence, sem_purpose_code, sem_matches = self.semantic_similarity_match(narration, self.semantic_terms)
        if matched and sem_purpose_code == 'TREA':
            logger.info(f"Treasury semantic match with confidence: {sem_confidence:.2f}")
            return self._create_enhanced_result(result, 'TREA', sem_confidence,
                                              f"Semantic similarity matches: {len(sem_matches)}")

        # Message type specific analysis
        if message_type:
            enhanced_result = self.analyze_message_type(result, narration, message_type)
            if enhanced_result != result:
                return enhanced_result
        elif self.mt202_pattern.search(narration):
            # If message type is mentioned in narration, treat as MT202
            enhanced_result = self.analyze_message_type(result, narration, 'MT202')
            if enhanced_result != result:
                return enhanced_result

        # Check if we should override the current classification
        if self.should_override_classification(result, narration):
            logger.info(f"Overriding {purpose_code} with TREA based on context analysis")
            return self._create_enhanced_result(result, 'TREA', 0.85, "Context analysis override")

        # No treasury pattern detected
        logger.debug("No treasury pattern detected")
        return result

    def analyze_message_type(self, result, narration, message_type):
        """
        Analyze message type for treasury-related patterns.

        Args:
            result: Current classification result
            narration: Transaction narration
            message_type: Message type

        Returns:
            dict: Enhanced classification result
        """
        narration_lower = narration.lower()

        # MT202 specific patterns (financial institution transfers)
        if message_type in ['MT202', 'MT202COV']:
            # MT202 is often used for treasury operations
            if any(keyword in narration_lower for keyword in ['treasury', 'cash', 'liquidity', 'intercompany', 'intracompany', 'internal']):
                logger.info(f"MT202 treasury operation detected")
                return self._create_enhanced_result(result, 'TREA', 0.9, "MT202 treasury operation")

            # Check for nostro/vostro accounts
            if any(keyword in narration_lower for keyword in ['nostro', 'vostro', 'correspondent']):
                logger.info(f"MT202 nostro/vostro operation detected")
                return self._create_enhanced_result(result, 'TREA', 0.9, "MT202 nostro/vostro operation")

            # Check for general treasury terms in MT202
            if 'treasury' in narration_lower:
                logger.info(f"MT202 with treasury keyword detected")
                return self._create_enhanced_result(result, 'TREA', 0.95, "MT202 with treasury keyword")

        # No message type specific pattern detected
        return result

    def should_override_classification(self, result, narration):
        """
        Determine if treasury classification should override existing classification.

        Args:
            result: Current classification result
            narration: Transaction narration

        Returns:
            bool: True if should override
        """
        narration_lower = narration.lower()
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)

        # Check for strong treasury context
        context_score = self.context_match(narration, self.treasury_contexts)

        # Check if current classification has low confidence
        if confidence < 0.7 and context_score >= 0.6:
            return True

        # Don't override other classifications unless very strong evidence
        return False

    def _create_enhanced_result(self, original_result, purpose_code, confidence, reason):
        """
        Create an enhanced result dictionary.

        Args:
            original_result: Original classification result
            purpose_code: Enhanced purpose code
            confidence: Enhanced confidence
            reason: Reason for enhancement

        Returns:
            dict: Enhanced classification result
        """
        # Create a copy of the original result
        result = original_result.copy()

        # Update with enhanced values
        result['purpose_code'] = purpose_code
        result['confidence'] = confidence
        result['category_purpose_code'] = purpose_code  # Direct mapping for TREA
        result['category_confidence'] = confidence

        # Add enhancement metadata
        result['enhanced'] = True
        result['enhancement_applied'] = 'treasury_enhancer'
        result['enhanced'] = True
        result['reason'] = reason
        result['original_purpose_code'] = original_result.get('purpose_code')
        result['original_confidence'] = original_result.get('confidence')

        # Set force flags to prevent other enhancers from overriding
        if confidence >= 0.9:
            result['force_purpose_code'] = True
            result['force_category_purpose_code'] = True

        return result
