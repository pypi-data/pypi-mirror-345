"""
Collaborative Enhancer Base Class for Purpose Code Classification.

This module provides a base class for collaborative enhancers that can share
information and build on each other's results.
"""

import logging
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer

logger = logging.getLogger(__name__)

class CollaborativeEnhancer(SemanticEnhancer):
    """
    Base class for collaborative enhancers.

    Extends the SemanticEnhancer with collaboration capabilities to share
    information and build on other enhancers' results.
    """

    def __init__(self, matcher=None):
        """
        Initialize with optional matcher.
        
        Args:
            matcher: Optional SemanticPatternMatcher instance to use
        """
        super().__init__(matcher=matcher)
        
        # Initialize collaboration settings
        self.collaboration_settings = {
            'use_collaboration': True,
            'confidence_boost_factor': 1.1,  # 10% boost when multiple enhancers agree
            'min_agreement_threshold': 2,    # Minimum number of enhancers that must agree
            'max_confidence': 0.99           # Maximum confidence after boosting
        }

    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification with collaboration capabilities.

        Args:
            result: Initial classification result
            narration: Transaction narration
            message_type: Optional message type

        Returns:
            dict: Enhanced classification result
        """
        # Extract collaboration context if available
        collaboration_context = result.pop('collaboration_context', None)
        
        # Apply base semantic enhancement
        enhanced_result = super().enhance_classification(result, narration, message_type)
        
        # Apply collaboration if context is available and enhancement was applied
        if collaboration_context and enhanced_result != result and self.collaboration_settings['use_collaboration']:
            enhanced_result = self._apply_collaboration(enhanced_result, collaboration_context)
            
        return enhanced_result

    def _apply_collaboration(self, result, context):
        """
        Apply collaboration to enhance the result.

        Args:
            result: Current enhanced result
            context: Collaboration context

        Returns:
            dict: Result with collaboration applied
        """
        purpose_code = result.get('purpose_code')
        
        # Check if other enhancers suggested the same purpose code
        if purpose_code in context['purpose_code_votes']:
            votes = context['purpose_code_votes'][purpose_code]
            
            # If enough enhancers agree, boost confidence
            if votes >= self.collaboration_settings['min_agreement_threshold']:
                original_confidence = result.get('confidence', 0.5)
                boosted_confidence = min(
                    self.collaboration_settings['max_confidence'],
                    original_confidence * self.collaboration_settings['confidence_boost_factor']
                )
                
                # Update result with boosted confidence
                result['confidence'] = boosted_confidence
                result['collaboration_applied'] = True
                result['original_confidence'] = original_confidence
                result['agreeing_enhancers'] = votes
                
                logger.debug(
                    f"Collaboration applied for {purpose_code}: "
                    f"{original_confidence:.2f} -> {boosted_confidence:.2f} "
                    f"with {votes} agreeing enhancers"
                )
        
        return result

    def get_other_enhancer_suggestions(self, context):
        """
        Get suggestions from other enhancers.

        Args:
            context: Collaboration context

        Returns:
            list: Suggestions from other enhancers
        """
        if not context:
            return []
            
        return context.get('enhancer_suggestions', [])

    def get_most_voted_purpose_code(self, context):
        """
        Get the most voted purpose code from the collaboration context.

        Args:
            context: Collaboration context

        Returns:
            tuple: (purpose_code, votes) or (None, 0) if no votes
        """
        if not context or not context.get('purpose_code_votes'):
            return (None, 0)
            
        votes = context['purpose_code_votes']
        if not votes:
            return (None, 0)
            
        most_common = votes.most_common(1)
        if not most_common:
            return (None, 0)
            
        return most_common[0]  # (purpose_code, votes)

    def should_consider_collaboration(self, result, context):
        """
        Determine if collaboration should be considered for this result.

        Args:
            result: Current result
            context: Collaboration context

        Returns:
            bool: True if collaboration should be considered
        """
        # Don't use collaboration for high confidence results
        if result.get('confidence', 0) > 0.9:
            return False
            
        # Don't use collaboration if no context or no suggestions
        if not context or not context.get('enhancer_suggestions'):
            return False
            
        return True
"""
