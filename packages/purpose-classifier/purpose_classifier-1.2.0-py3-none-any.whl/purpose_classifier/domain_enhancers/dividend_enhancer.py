#!/usr/bin/env python
"""
Dividend Enhancer for Purpose Code Classification.

This module provides a specialized enhancer for dividend-related transactions.
It uses semantic pattern matching to identify dividend payments and distributions.
"""

import re
import logging
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer

logger = logging.getLogger(__name__)

class DividendEnhancer(SemanticEnhancer):
    """
    Specialized enhancer for dividend payments.

    This enhancer uses semantic pattern matching to identify dividend-related
    transactions with high accuracy. It handles various types of dividends,
    profit distributions, and shareholder payments.
    """

    def __init__(self, matcher=None):
        """
        Initialize with optional matcher.

        Args:
            matcher: Optional SemanticPatternMatcher instance to use
        """
        super().__init__(matcher=matcher)

        # Initialize dividend-specific patterns and contexts
        self._initialize_patterns()

        # Set confidence thresholds
        self.confidence_thresholds = {
            'direct_match': 0.95,
            'context_match': 0.85,
            'semantic_match': 0.75,
            'edge_case': 0.90
        }

        # Purpose code to category purpose code mappings
        self.purpose_to_category_mappings = {
            'DIVD': 'DIVD'  # Dividend payment maps directly to DIVD category
        }

    def _initialize_patterns(self):
        """Initialize dividend-specific patterns and contexts."""
        # Direct dividend keywords (highest confidence)
        self.direct_keywords = {
            'DIVD': [
                'dividend', 'dividends', 'div', 'div.', 'dividend payment',
                'shareholder dividend', 'shareholder distribution',
                'dividend distribution', 'dividend payout',
                'quarterly dividend', 'annual dividend', 'interim dividend',
                'final dividend', 'special dividend', 'cash dividend',
                'stock dividend', 'share dividend', 'dividend income'
            ]
        }

        # Semantic context patterns for dividends
        self.context_patterns = [
            {
                'purpose_code': 'DIVD',
                'keywords': ['dividend', 'payment'],
                'proximity': 5,
                'weight': 1.0,
                'description': 'Dividend payment pattern'
            },
            {
                'purpose_code': 'DIVD',
                'keywords': ['shareholder', 'dividend'],
                'proximity': 3,
                'weight': 1.0,
                'description': 'Shareholder dividend pattern'
            },
            {
                'purpose_code': 'DIVD',
                'keywords': ['quarterly', 'dividend'],
                'proximity': 3,
                'weight': 0.9,
                'description': 'Quarterly dividend pattern'
            },
            {
                'purpose_code': 'DIVD',
                'keywords': ['interim', 'dividend'],
                'proximity': 3,
                'weight': 0.9,
                'description': 'Interim dividend pattern'
            },
            {
                'purpose_code': 'DIVD',
                'keywords': ['final', 'dividend'],
                'proximity': 3,
                'weight': 0.9,
                'description': 'Final dividend pattern'
            },
            {
                'purpose_code': 'DIVD',
                'keywords': ['annual', 'dividend'],
                'proximity': 3,
                'weight': 0.9,
                'description': 'Annual dividend pattern'
            },
            {
                'purpose_code': 'DIVD',
                'keywords': ['dividend', 'distribution'],
                'proximity': 5,
                'weight': 0.8,
                'description': 'Dividend distribution pattern'
            },
            {
                'purpose_code': 'DIVD',
                'keywords': ['dividend', 'payout'],
                'proximity': 5,
                'weight': 0.8,
                'description': 'Dividend payout pattern'
            },
            {
                'purpose_code': 'DIVD',
                'keywords': ['profit', 'sharing'],
                'proximity': 3,
                'weight': 0.7,
                'description': 'Profit sharing pattern'
            },
            {
                'purpose_code': 'DIVD',
                'keywords': ['profit', 'distribution'],
                'proximity': 3,
                'weight': 0.7,
                'description': 'Profit distribution pattern'
            },
            {
                'purpose_code': 'DIVD',
                'keywords': ['shareholder', 'payout'],
                'proximity': 3,
                'weight': 0.8,
                'description': 'Shareholder payout pattern'
            },
            {
                'purpose_code': 'DIVD',
                'keywords': ['shareholder', 'distribution'],
                'proximity': 3,
                'weight': 0.8,
                'description': 'Shareholder distribution pattern'
            }
        ]

        # Dividend-related terms for semantic similarity matching
        self.semantic_terms = [
            {
                'purpose_code': 'DIVD',
                'term': 'dividend',
                'threshold': 0.7,
                'weight': 1.0,
                'description': 'Dividend term'
            },
            {
                'purpose_code': 'DIVD',
                'term': 'shareholder',
                'threshold': 0.7,
                'weight': 0.9,
                'description': 'Shareholder term'
            },
            {
                'purpose_code': 'DIVD',
                'term': 'payout',
                'threshold': 0.7,
                'weight': 0.8,
                'description': 'Payout term'
            },
            {
                'purpose_code': 'DIVD',
                'term': 'distribution',
                'threshold': 0.7,
                'weight': 0.8,
                'description': 'Distribution term'
            },
            {
                'purpose_code': 'DIVD',
                'term': 'quarterly',
                'threshold': 0.7,
                'weight': 0.7,
                'description': 'Quarterly term'
            },
            {
                'purpose_code': 'DIVD',
                'term': 'annual',
                'threshold': 0.7,
                'weight': 0.7,
                'description': 'Annual term'
            },
            {
                'purpose_code': 'DIVD',
                'term': 'interim',
                'threshold': 0.7,
                'weight': 0.7,
                'description': 'Interim term'
            },
            {
                'purpose_code': 'DIVD',
                'term': 'final',
                'threshold': 0.7,
                'weight': 0.7,
                'description': 'Final term'
            },
            {
                'purpose_code': 'DIVD',
                'term': 'profit',
                'threshold': 0.7,
                'weight': 0.7,
                'description': 'Profit term'
            },
            {
                'purpose_code': 'DIVD',
                'term': 'sharing',
                'threshold': 0.7,
                'weight': 0.6,
                'description': 'Sharing term'
            },
            {
                'purpose_code': 'DIVD',
                'term': 'earnings',
                'threshold': 0.7,
                'weight': 0.7,
                'description': 'Earnings term'
            }
        ]

    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification for dividend payments.

        Args:
            result: Initial classification result
            narration: Transaction narration
            message_type: Optional message type

        Returns:
            dict: Enhanced classification result
        """
        # Don't override if already classified as DIVD with high confidence
        if result.get('purpose_code') == 'DIVD' and result.get('confidence', 0.0) >= 0.8:
            return result

        # Store original result for comparison
        original_result = result.copy()

        # Convert narration to lowercase for pattern matching
        narration_lower = narration.lower()

        # 1. Direct keyword matching (highest confidence)
        matched, confidence, keyword = self.direct_keyword_match(narration_lower, 'DIVD')
        if matched:
            logger.debug(f"Dividend direct keyword match: {keyword}")
            return self._create_enhanced_result(
                'DIVD',
                confidence,
                f"Direct dividend keyword match: {keyword}",
                original_result
            )

        # 2. Context pattern matching
        matched, confidence, pattern = self.context_match_for_purpose(narration_lower, 'DIVD')
        if matched:
            logger.debug(f"Dividend context match: {pattern.get('description')}")
            return self._create_enhanced_result(
                'DIVD',
                confidence,
                f"Dividend context match: {pattern.get('description')}",
                original_result
            )

        # 3. Semantic similarity matching
        # Filter semantic terms for DIVD
        divd_semantic_terms = [term for term in self.semantic_terms if term.get('purpose_code') == 'DIVD']
        if divd_semantic_terms:
            matched, confidence, purpose_code, matches = self.semantic_similarity_match(narration_lower, divd_semantic_terms)
            if matched and purpose_code == 'DIVD':
                match_terms = []
                for m in matches[:3]:
                    if len(m) >= 3:
                        word, term, purpose_code = m[0], m[1], m[2]
                        similarity = m[3] if len(m) > 3 else 0.7
                        match_terms.append(f"{word}~{term}({similarity:.2f})")
                match_str = ', '.join(match_terms) if match_terms else "semantic similarity"
                logger.debug(f"Dividend semantic match: {match_str}")
                return self._create_enhanced_result(
                    'DIVD',
                    confidence,
                    f"Dividend semantic match: {match_str}",
                    original_result
                )

        # 4. Handle edge cases
        is_edge_case, confidence, reason = self.handle_edge_cases(narration_lower)
        if is_edge_case:
            logger.debug(f"Dividend edge case: {reason}")
            return self._create_enhanced_result(
                'DIVD',
                confidence,
                f"Dividend edge case: {reason}",
                original_result
            )

        # 5. Check if we should override investment classification
        if self.should_override_investment(result, narration_lower):
            logger.debug("Overriding investment classification with dividend")
            return self._create_enhanced_result(
                'DIVD',
                0.85,
                "Overriding investment classification with dividend",
                original_result
            )

        # No dividend pattern detected
        return result

    def handle_edge_cases(self, narration):
        """
        Handle special edge cases for dividend classification.

        Args:
            narration: Transaction narration

        Returns:
            tuple: (is_dividend, confidence, reason)
        """
        # Handle profit sharing (semantically similar to dividends)
        if 'profit sharing' in narration or 'profit distribution' in narration:
            return (True, self.confidence_thresholds['edge_case'], "Profit sharing is semantically equivalent to dividends")

        # Handle stock dividends
        if ('stock' in narration and 'dividend' in narration) or 'stock dividend' in narration:
            return (True, self.confidence_thresholds['edge_case'], "Stock dividend explicitly mentioned")

        # Handle dividend reinvestment plans (DRIPs)
        if 'drip' in narration or 'dividend reinvestment' in narration:
            return (True, self.confidence_thresholds['edge_case'], "Dividend reinvestment plan (DRIP)")

        # Handle dividend income
        if 'dividend income' in narration:
            return (True, self.confidence_thresholds['edge_case'], "Dividend income explicitly mentioned")

        # Not a special case
        return (False, 0.0, "No special dividend case detected")

    def should_override_investment(self, result, narration):
        """
        Determine if dividend classification should override investment classification.

        Args:
            result: Current classification result
            narration: Transaction narration

        Returns:
            bool: True if should override
        """
        # Only consider overriding INVS classification
        if result.get('purpose_code') != 'INVS':
            return False

        # Check for dividend-related terms in investment context
        dividend_terms = ['dividend', 'payout', 'distribution', 'shareholder']
        investment_terms = ['investment', 'portfolio', 'securities', 'shares', 'stocks']

        # Count dividend and investment terms
        dividend_count = sum(1 for term in dividend_terms if term in narration)
        investment_count = sum(1 for term in investment_terms if term in narration)

        # If more dividend terms than investment terms, override
        if dividend_count > 0 and dividend_count >= investment_count:
            return True

        return False

    def _create_enhanced_result(self, purpose_code, confidence, reason, original_result):
        """
        Create enhanced result with dividend classification.

        Args:
            purpose_code: The purpose code to set
            confidence: The confidence score
            reason: The reason for enhancement
            original_result: The original result for comparison

        Returns:
            dict: Enhanced result
        """
        # Create enhanced result
        enhanced_result = original_result.copy()
        enhanced_result['purpose_code'] = purpose_code
        enhanced_result['confidence'] = confidence
        enhanced_result['enhancement_applied'] = 'dividend'
        enhanced_result['enhanced'] = True
        enhanced_result['enhancement_type'] = 'semantic_pattern'
        enhanced_result['reason'] = reason

        # Set category purpose code if appropriate
        if purpose_code in self.purpose_to_category_mappings:
            enhanced_result['category_purpose_code'] = self.purpose_to_category_mappings[purpose_code]
            enhanced_result['category_confidence'] = confidence
            enhanced_result['category_enhancement_applied'] = 'dividend_category_mapping'

        return enhanced_result
