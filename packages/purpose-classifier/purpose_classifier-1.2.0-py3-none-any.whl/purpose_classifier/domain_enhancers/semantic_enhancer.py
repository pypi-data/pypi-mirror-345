"""
Semantic Enhancer Base Class for Purpose Code Classification.

This module provides a base class for all semantic enhancers, combining
BaseEnhancer functionality with semantic pattern matching capabilities.
"""

import os
import logging
from purpose_classifier.semantic_pattern_matcher import SemanticPatternMatcher

logger = logging.getLogger(__name__)

class SemanticEnhancer:
    """
    Base class for all semantic enhancers.

    Combines enhancer functionality with semantic pattern matching capabilities
    for improved purpose code classification accuracy.
    """

    def __init__(self, matcher=None):
        """
        Initialize the semantic enhancer.

        Args:
            matcher: Optional SemanticPatternMatcher instance to use
        """
        if matcher:
            # Use the provided matcher
            self.matcher = matcher
            logger.info(f"Using provided matcher for {self.__class__.__name__}")
        else:
            # Get the absolute path to the word embeddings file
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            embeddings_path = os.path.join(base_dir, 'models', 'word_embeddings.pkl')

            # Initialize semantic pattern matcher with explicit embeddings path
            self.matcher = SemanticPatternMatcher(embeddings_path)

            # Log whether embeddings were loaded
            if self.matcher.embeddings:
                logger.info(f"Word embeddings loaded successfully for {self.__class__.__name__}")
            else:
                logger.warning(f"Word embeddings not loaded for {self.__class__.__name__}")

        # Initialize common patterns and contexts
        self.context_patterns = []
        self.direct_keywords = {}
        self.semantic_terms = []
        self.confidence_thresholds = {
            'direct_match': 0.95,
            'context_match': 0.80,  # Reduced from 0.85 to 0.80
            'semantic_match': 0.70  # Reduced from 0.75 to 0.70
        }

    def enhance_classification(self, result, narration, message_type=None):
        """
        Base implementation of semantic enhancement.

        Args:
            result: Initial classification result
            narration: Transaction narration
            message_type: Optional message type

        Returns:
            dict: Enhanced classification result
        """
        narration_lower = narration.lower()

        # Check for direct keyword matches first (highest confidence)
        for purpose_code in self.direct_keywords:
            matched, confidence, keyword = self.direct_keyword_match(
                narration_lower, purpose_code
            )
            if matched:
                return {
                    'purpose_code': purpose_code,
                    'confidence': confidence,
                    'enhancer': self.__class__.__name__.lower(),
                    'reason': f"Direct keyword match: {keyword}"
                }

        # Check for context pattern matches next
        for pattern in self.context_patterns:
            purpose_code = pattern.get('purpose_code')
            matched, confidence, pattern_info = self.context_match_for_purpose(
                narration_lower, purpose_code
            )
            if matched:
                return {
                    'purpose_code': purpose_code,
                    'confidence': confidence,
                    'enhancer': self.__class__.__name__.lower(),
                    'reason': f"Context pattern match: {pattern_info['keywords']}"
                }

        # Check for semantic similarity matches last
        for term in self.semantic_terms:
            purpose_code = term.get('purpose_code')
            matched, confidence, purpose_code, matches = self.semantic_similarity_match(
                narration_lower, self.semantic_terms
            )
            if matched and purpose_code:
                return {
                    'purpose_code': purpose_code,
                    'confidence': confidence,
                    'enhancer': self.__class__.__name__.lower(),
                    'reason': f"Semantic similarity match: {len(matches)} matches"
                }

        # No matches found, return original result
        return result

    def direct_keyword_match(self, narration, purpose_code):
        """
        Check for direct keyword matches.

        Args:
            narration: Transaction narration
            purpose_code: Purpose code to check keywords for

        Returns:
            tuple: (matched, confidence, keyword)
        """
        narration_lower = narration.lower()

        if purpose_code not in self.direct_keywords:
            return (False, 0.0, None)

        for keyword in self.direct_keywords[purpose_code]:
            if keyword.lower() in narration_lower:
                return (True, self.confidence_thresholds['direct_match'], keyword)

        return (False, 0.0, None)

    def context_match(self, narration, context_patterns):
        """
        Check for context pattern matches.

        Args:
            narration: Transaction narration
            context_patterns: List of context pattern dictionaries
                Each dict has keys: 'keywords', 'proximity', 'weight'

        Returns:
            float: Match score between 0 and 1
        """
        words = self.matcher.tokenize(narration.lower())
        total_score = 0.0
        max_weight = sum(pattern['weight'] for pattern in context_patterns)

        for pattern in context_patterns:
            keywords = pattern['keywords']
            proximity = pattern['proximity']
            weight = pattern['weight']

            # Check if all keywords are within proximity
            if self.matcher.keywords_in_proximity(words, keywords, proximity):
                total_score += weight

        return total_score / max_weight if max_weight > 0 else 0.0

    def context_match_for_purpose(self, narration, purpose_code):
        """
        Check for context pattern matches for a specific purpose code.

        Args:
            narration: Transaction narration
            purpose_code: Purpose code to check context for

        Returns:
            tuple: (matched, confidence, pattern)
        """
        # Filter context patterns for this purpose code
        relevant_patterns = [p for p in self.context_patterns
                           if p.get('purpose_code') == purpose_code]

        if not relevant_patterns:
            return (False, 0.0, None)

        # Check each pattern
        for pattern in relevant_patterns:
            # Check if pattern has required keys
            if 'keywords' not in pattern or 'proximity' not in pattern or 'weight' not in pattern:
                continue

            keywords = pattern['keywords']
            proximity = pattern['proximity']
            weight = pattern['weight']

            words = self.matcher.tokenize(narration)
            if self.matcher.keywords_in_proximity(words, keywords, proximity):
                confidence = min(self.confidence_thresholds['context_match'],
                               weight)
                return (True, confidence, pattern)

        return (False, 0.0, None)

    def semantic_similarity_match(self, narration, semantic_terms):
        """
        Check for semantic similarity matches.

        Args:
            narration: Transaction narration
            semantic_terms: List of semantic term dictionaries
                Each dict has keys: 'term', 'purpose_code', 'threshold', 'weight'

        Returns:
            tuple: (matched, confidence, purpose_code, matches)
        """
        narration_lower = narration.lower()
        words = self.matcher.tokenize(narration_lower)

        # Check semantic similarity
        matches = []
        for term_data in semantic_terms:
            term = term_data['term']
            purpose_code = term_data['purpose_code']
            threshold = term_data.get('threshold', 0.7)
            weight = term_data.get('weight', 1.0)

            for word in words:
                similarity = self.matcher.semantic_similarity(word, term)
                if similarity >= threshold:
                    matches.append((word, term, purpose_code, similarity, weight))

        if matches:
            # Group matches by purpose code
            purpose_matches = {}
            for match in matches:
                word, term, purpose_code, similarity, weight = match
                if purpose_code not in purpose_matches:
                    purpose_matches[purpose_code] = []
                purpose_matches[purpose_code].append((word, term, similarity, weight))

            # Find purpose code with highest weighted similarity
            best_purpose_code = None
            best_confidence = 0.0

            for purpose_code, code_matches in purpose_matches.items():
                total_weight = sum(m[3] for m in code_matches)
                weighted_similarity = sum(m[2] * m[3] for m in code_matches) / total_weight
                confidence = min(self.confidence_thresholds['semantic_match'], weighted_similarity)

                if confidence > best_confidence:
                    best_confidence = confidence
                    best_purpose_code = purpose_code

            return (True, best_confidence, best_purpose_code, matches)

        return (False, 0.0, None, [])

    def load_word_embeddings(self, embeddings_path):
        """
        Load word embeddings for semantic similarity matching.

        Args:
            embeddings_path: Path to word embeddings file

        Returns:
            bool: True if embeddings were loaded successfully
        """
        return self.matcher.load_word_embeddings(embeddings_path)

    def calculate_confidence(self, match_scores, weights=None):
        """
        Calculate overall confidence score from multiple match scores.

        Args:
            match_scores (dict): Dictionary of {pattern_name: score}
            weights (dict, optional): Dictionary of {pattern_name: weight}

        Returns:
            float: Confidence score between 0 and 1
        """
        if not match_scores:
            return 0.0

        if weights is None:
            weights = {name: 1.0 for name in match_scores}

        total_weight = sum(weights.values())
        weighted_score = sum(score * weights.get(name, 1.0)
                            for name, score in match_scores.items())

        return weighted_score / total_weight if total_weight > 0 else 0.0

    def should_override_classification(self, result, narration):
        """
        Determine if classification should override existing classification.

        Args:
            result: Current classification result
            narration: Transaction narration

        Returns:
            bool: True if should override
        """
        # Subclasses should override this method
        return False

    def _create_enhanced_result(self, original_result, purpose_code, confidence, reason):
        """
        Create an enhanced result dictionary.

        Args:
            original_result: Original classification result
            purpose_code: New purpose code
            confidence: New confidence score
            reason: Reason for enhancement

        Returns:
            dict: Enhanced classification result
        """
        # Create a copy of the original result
        result = original_result.copy()

        # Update with enhanced values
        result['purpose_code'] = purpose_code
        result['confidence'] = confidence

        # Add enhancement metadata
        result['enhanced'] = True
        result['enhancer'] = self.__class__.__name__.lower()
        result['reason'] = reason
        result['original_purpose_code'] = original_result.get('purpose_code')
        result['original_confidence'] = original_result.get('confidence')

        return result
