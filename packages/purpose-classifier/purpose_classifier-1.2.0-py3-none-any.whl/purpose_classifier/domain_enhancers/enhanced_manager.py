"""
Enhanced Manager for Purpose Code Classification.

This module provides an enhanced version of the EnhancerManager with improved
collaboration between enhancers, conflict resolution, and adaptive confidence scoring.
"""

import logging
import numpy as np
from collections import Counter
from purpose_classifier.domain_enhancers.enhancer_manager import EnhancerManager

logger = logging.getLogger(__name__)

class EnhancedManager(EnhancerManager):
    """
    Enhanced manager for purpose code enhancers.

    This class extends the EnhancerManager with improved collaboration between enhancers,
    conflict resolution, and adaptive confidence scoring.
    """

    def __init__(self, matcher=None):
        """
        Initialize the enhanced manager with all available enhancers.

        Args:
            matcher: Optional SemanticPatternMatcher instance to use
        """
        # Initialize the base EnhancerManager with the matcher
        super().__init__(matcher=matcher)

        # Initialize collaboration context
        self.collaboration_context = {}

        # Initialize conflict resolution settings
        self.conflict_resolution = {
            'use_semantic_similarity': True,
            'use_voting': True,
            'use_confidence_weighting': True,
            'min_confidence_threshold': 0.3,
            'semantic_similarity_threshold': 0.7
        }

        # Initialize adaptive confidence settings
        self.adaptive_confidence = {
            'use_adaptive_confidence': True,
            'confidence_history': {},
            'learning_rate': 0.1,
            'max_history_size': 100
        }

        # Initialize performance tracking
        self.performance_tracking = {
            'enhancer_timing': {},
            'enhancer_accuracy': {},
            'total_calls': 0,
            'successful_calls': 0
        }

        logger.info("Enhanced manager initialized with collaboration, conflict resolution, and adaptive confidence")

    def enhance(self, result, narration, message_type=None):
        """
        Apply all enhancers to the classification result with enhanced collaboration and conflict resolution.

        Args:
            result: The classification result dictionary
            narration: The narration text
            message_type: Optional message type (MT103, MT202, MT202COV, MT205, MT205COV)

        Returns:
            dict: The enhanced classification result
        """
        # Reset collaboration context for this enhancement
        self.collaboration_context = {
            'narration': narration,
            'message_type': message_type,
            'initial_result': result.copy(),
            'enhancer_suggestions': [],
            'purpose_code_votes': Counter(),
            'confidence_sum': {},
            'enhancer_count': {}
        }

        # Track performance
        self.performance_tracking['total_calls'] += 1

        # Special case handling from base class
        if narration.upper() in ["WITHHOLDING TAX PAYMENT", "TAX WITHHOLDING REMITTANCE"]:
            logger.info(f"Special case for withholding tax: {narration}")
            enhanced_result = result.copy()
            enhanced_result['purpose_code'] = 'WHLD'
            enhanced_result['confidence'] = 0.99
            enhanced_result['enhancer'] = "special_case_handler"
            enhanced_result['enhanced'] = True
            enhanced_result['category_purpose_code'] = "WHLD"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "special_case_withholding_tax"
            enhanced_result['force_purpose_code'] = True
            enhanced_result['force_category_purpose_code'] = True
            enhanced_result['final_override'] = True
            return enhanced_result

        # Create a copy of the result to work with
        current_result = result.copy()

        # Add narration to result for logging
        current_result['narration'] = narration
        if message_type:
            current_result['message_type'] = message_type

        # Track enhancer decisions for logging
        enhancer_decisions = []

        # Select relevant enhancers based on context
        relevant_enhancers = self.select_enhancers_by_context(narration, message_type)
        logger.debug(f"Selected relevant enhancers: {relevant_enhancers}")

        # Calculate relevance scores for each enhancer based on narration
        enhancer_relevance = self._calculate_enhancer_relevance(narration, relevant_enhancers)

        # Sort enhancers by relevance score (descending)
        sorted_enhancers = sorted(
            [(name, score) for name, score in enhancer_relevance.items()],
            key=lambda x: x[1],
            reverse=True
        )

        logger.info(f"Enhancers sorted by relevance: {sorted_enhancers}")

        # Apply enhancers in relevance order with collaboration
        level_suggestions = []
        for enhancer_name, relevance_score in sorted_enhancers:
            if enhancer_name not in self.enhancers:
                logger.warning(f"Enhancer {enhancer_name} not found in available enhancers")
                continue

            enhancer = self.enhancers[enhancer_name]
            logger.debug(f"Applying {enhancer_name} enhancer (relevance: {relevance_score:.2f})")

            try:
                # Apply enhancer with collaboration context
                enhanced = self._apply_enhancer_with_collaboration(
                    enhancer, enhancer_name, current_result, narration, message_type
                )

                # Check if enhancer changed the result
                if enhanced['purpose_code'] != current_result['purpose_code']:
                    # Add to suggestions
                    suggestion = {
                        'enhancer': enhancer_name,
                        'purpose_code': enhanced['purpose_code'],
                        'confidence': enhanced.get('confidence', 0.0),
                        'reason': enhanced.get('reason', 'No reason provided'),
                        'priority_weight': self.priorities.get(enhancer_name, {}).get('weight', 0.5),
                        'relevance_score': relevance_score  # Add relevance score to suggestion
                    }
                    level_suggestions.append(suggestion)
                    self.collaboration_context['enhancer_suggestions'].append(suggestion)

                    # Update votes
                    self.collaboration_context['purpose_code_votes'][enhanced['purpose_code']] += 1

                    # Update confidence sum and count
                    if enhanced['purpose_code'] not in self.collaboration_context['confidence_sum']:
                        self.collaboration_context['confidence_sum'][enhanced['purpose_code']] = 0.0
                        self.collaboration_context['enhancer_count'][enhanced['purpose_code']] = 0

                    self.collaboration_context['confidence_sum'][enhanced['purpose_code']] += enhanced.get('confidence', 0.0)
                    self.collaboration_context['enhancer_count'][enhanced['purpose_code']] += 1

                    # Record decision for logging
                    enhancer_decisions.append({
                        'enhancer': enhancer_name,
                        'old_code': current_result['purpose_code'],
                        'new_code': enhanced['purpose_code'],
                        'confidence': enhanced.get('confidence', 0.0),
                        'threshold': 0.0,  # No fixed threshold in dynamic system
                        'applied': False,  # Will be determined after conflict resolution
                        'reason': enhanced.get('reason', 'No reason provided'),
                        'relevance_score': relevance_score
                    })
            except Exception as e:
                logger.error(f"Error applying enhancer {enhancer_name}: {str(e)}")
                continue

        # Resolve conflicts among all suggestions
        if level_suggestions:
            resolved_result = self._resolve_conflicts(level_suggestions, current_result)

            # Update current result if conflict resolution produced a result
            if resolved_result:
                # Update which enhancer decision was applied
                for decision in enhancer_decisions:
                    if decision['new_code'] == resolved_result['purpose_code']:
                        decision['applied'] = True

                # Set the enhanced flag to True
                resolved_result['enhanced'] = True

                current_result = resolved_result

        # Ensure category purpose code is set
        if not current_result.get('category_purpose_code'):
            # Apply category purpose enhancer as a last resort
            logger.debug(f"Category purpose code not set, applying category purpose enhancer")
            current_result = self.enhancers['category_purpose'].enhance_classification(
                current_result, narration, message_type
            )

        # Add enhancer decisions to result for logging
        current_result['enhancer_decisions'] = enhancer_decisions

        # Log enhancer decisions
        self.log_enhancer_decisions(current_result)

        # Track successful call
        self.performance_tracking['successful_calls'] += 1

        return current_result

    def _apply_enhancer_with_collaboration(self, enhancer, enhancer_name, current_result, narration, message_type=None):
        """
        Apply an enhancer with collaboration context.

        Args:
            enhancer: The enhancer to apply
            enhancer_name: The name of the enhancer
            current_result: The current classification result
            narration: The narration text
            message_type: Optional message type

        Returns:
            dict: The enhanced classification result
        """
        # Special handling for message_type enhancer
        if enhancer_name == 'message_type' and message_type:
            return enhancer.enhance_classification(current_result.copy(), narration, message_type)

        # Add collaboration context to the result
        result_with_context = current_result.copy()
        result_with_context['collaboration_context'] = self.collaboration_context

        # Apply enhancer
        enhanced = enhancer.enhance_classification(result_with_context, narration, message_type)

        # Apply adaptive confidence if enabled
        if self.adaptive_confidence['use_adaptive_confidence']:
            enhanced = self._apply_adaptive_confidence(enhanced, enhancer_name)

        return enhanced

    def _resolve_conflicts(self, suggestions, current_result):
        """
        Resolve conflicts among enhancer suggestions.

        Args:
            suggestions: List of enhancer suggestions
            current_result: The current classification result

        Returns:
            dict: The resolved classification result
        """
        if not suggestions:
            return current_result

        # If only one suggestion, use it
        if len(suggestions) == 1:
            suggestion = suggestions[0]
            result = current_result.copy()
            result['purpose_code'] = suggestion['purpose_code']
            result['confidence'] = suggestion['confidence']
            result['enhancer'] = suggestion['enhancer']
            result['reason'] = suggestion['reason']
            return result

        # Get the most voted purpose code
        most_voted = self.collaboration_context['purpose_code_votes'].most_common(1)[0]
        most_voted_code = most_voted[0]
        most_voted_count = most_voted[1]

        # If there's a clear winner by votes, use it
        if most_voted_count > 1 and self.conflict_resolution['use_voting']:
            # Calculate average confidence for this purpose code
            avg_confidence = (
                self.collaboration_context['confidence_sum'][most_voted_code] /
                self.collaboration_context['enhancer_count'][most_voted_code]
            )

            # Find the suggestion with this purpose code and highest combined score (confidence * relevance)
            matching_suggestions = [s for s in suggestions if s['purpose_code'] == most_voted_code]
            best_suggestion = max(
                matching_suggestions,
                key=lambda s: s['confidence'] * s.get('relevance_score', 0.5)
            )

            # Calculate average relevance score for this purpose code
            avg_relevance = sum(s.get('relevance_score', 0.5) for s in matching_suggestions) / len(matching_suggestions)

            # Log voting decision
            logger.info(f"Voting consensus: {most_voted_code} with {most_voted_count} votes")
            logger.info(f"Average confidence: {avg_confidence:.2f}, Average relevance: {avg_relevance:.2f}")

            # Create result with boosted confidence (weighted by relevance)
            result = current_result.copy()
            result['purpose_code'] = most_voted_code
            result['confidence'] = min(0.99, avg_confidence * (1.0 + 0.2 * avg_relevance))  # Boost confidence by up to 20% based on relevance
            result['enhancer'] = f"consensus_{best_suggestion['enhancer']}"
            result['reason'] = f"Consensus from {most_voted_count} enhancers: {best_suggestion['reason']}"
            result['avg_relevance'] = avg_relevance
            result['votes'] = most_voted_count
            result['enhanced'] = True  # Set the enhanced flag
            return result

        # If no clear winner by votes, use relevance and confidence weighting
        if self.conflict_resolution['use_confidence_weighting']:
            # Find suggestion with highest weighted score (confidence * relevance * priority_weight)
            best_suggestion = max(
                suggestions,
                key=lambda s: s['confidence'] * s.get('relevance_score', 0.5) * s['priority_weight']
            )

            # Calculate combined score
            combined_score = best_suggestion['confidence'] * best_suggestion.get('relevance_score', 0.5) * best_suggestion['priority_weight']

            # Log the decision process
            logger.info(f"Best suggestion: {best_suggestion['enhancer']} with purpose code {best_suggestion['purpose_code']}")
            logger.info(f"Confidence: {best_suggestion['confidence']:.2f}, Relevance: {best_suggestion.get('relevance_score', 0.5):.2f}, Priority: {best_suggestion['priority_weight']:.2f}")
            logger.info(f"Combined score: {combined_score:.2f}")

            # Check if combined score is above threshold
            if combined_score >= self.conflict_resolution['min_confidence_threshold']:
                result = current_result.copy()
                result['purpose_code'] = best_suggestion['purpose_code']
                result['confidence'] = best_suggestion['confidence']
                result['enhancer'] = best_suggestion['enhancer']
                result['reason'] = best_suggestion['reason']
                result['relevance_score'] = best_suggestion.get('relevance_score', 0.5)
                result['combined_score'] = combined_score
                result['enhanced'] = True  # Set the enhanced flag
                return result

        # If no resolution, keep current result
        return current_result

    def _apply_adaptive_confidence(self, result, enhancer_name):
        """
        Apply adaptive confidence adjustment based on enhancer history.

        Args:
            result: The classification result
            enhancer_name: The name of the enhancer

        Returns:
            dict: The result with adjusted confidence
        """
        # If enhancer has no history, return as is
        if enhancer_name not in self.adaptive_confidence['confidence_history']:
            return result

        # Get confidence history for this enhancer
        history = self.adaptive_confidence['confidence_history'][enhancer_name]

        # Calculate average historical accuracy
        if history['total'] > 0:
            accuracy = history['correct'] / history['total']

            # Adjust confidence based on historical accuracy
            current_confidence = result.get('confidence', 0.5)
            adjusted_confidence = current_confidence * (0.5 + 0.5 * accuracy)

            # Cap confidence at 0.99
            result['confidence'] = min(0.99, adjusted_confidence)

            # Add adaptive confidence info
            result['adaptive_confidence_applied'] = True
            result['original_confidence'] = current_confidence
            result['historical_accuracy'] = accuracy

        return result

    def _calculate_enhancer_relevance(self, narration, enhancer_names):
        """
        Calculate relevance scores for enhancers based on narration content.
        Uses both exact keyword matching and semantic similarity with word embeddings.

        Args:
            narration: The narration text
            enhancer_names: List of enhancer names to calculate relevance for

        Returns:
            dict: Dictionary mapping enhancer names to relevance scores (0.0-1.0)
        """
        narration_lower = narration.lower()
        relevance_scores = {}

        # Define keyword relevance for each enhancer
        enhancer_keywords = {
            'pattern': ['payment', 'transfer', 'transaction', 'remittance', 'money', 'funds'],
            'interbank': ['interbank', 'nostro', 'vostro', 'correspondent', 'bank to bank', 'between banks', 'financial institution', 'rtgs', 'real time gross settlement'],
            'securities': ['securities', 'security', 'bond', 'custody', 'settlement', 'portfolio', 'stocks', 'shares', 'equities', 'investment', 'trading'],
            'dividend': ['dividend', 'shareholder', 'distribution', 'payout', 'profit sharing', 'corporate action', 'stock dividend', 'cash dividend'],
            'loan': ['loan', 'credit', 'facility', 'repayment', 'installment', 'mortgage', 'financing', 'borrowing', 'lending', 'principal', 'debt'],
            'mt103': ['customer', 'payment', 'transfer', 'remittance', 'single customer', 'credit transfer'],
            'property_purchase': ['property', 'real estate', 'house', 'apartment', 'land', 'purchase', 'building', 'residential', 'commercial property'],
            'card_payment': ['card', 'credit card', 'debit card', 'payment card', 'card payment', 'visa', 'mastercard', 'amex', 'card transaction'],
            'cover_payment': ['cover', 'cover payment', 'mt202cov', 'cover transfer', 'intermediary', 'correspondent'],
            'cross_border': ['cross border', 'international', 'foreign', 'overseas', 'global', 'transnational', 'cross-country', 'abroad'],
            'court_payment': ['court', 'legal', 'judgment', 'judicial', 'lawsuit', 'settlement', 'litigation', 'attorney', 'lawyer', 'legal fees'],
            'targeted': ['specific', 'targeted', 'designated', 'earmarked', 'allocated', 'assigned', 'dedicated'],
            'rare_codes': ['rare', 'unusual', 'special', 'specific', 'exceptional', 'uncommon', 'infrequent'],
            'investment': ['investment', 'invest', 'portfolio', 'fund', 'asset management', 'wealth management', 'capital', 'financial investment'],
            'forex': ['forex', 'fx', 'foreign exchange', 'currency', 'exchange rate', 'currency conversion', 'currency exchange'],
            'trade_settlement': ['trade', 'settlement', 'commercial', 'business', 'transaction', 'trade finance', 'trade settlement'],
            'government_payment': ['government', 'public', 'official', 'state', 'federal', 'municipal', 'authority', 'administration', 'agency'],
            'trade': ['trade', 'commercial', 'business', 'goods', 'merchandise', 'commerce', 'trading', 'import', 'export'],
            'treasury': ['treasury', 'liquidity', 'cash pooling', 'cash management', 'cash flow', 'treasury management'],
            'education': ['education', 'tuition', 'school', 'university', 'college', 'student', 'academic', 'educational', 'scholarship', 'course'],
            'services': ['service', 'consulting', 'consultancy', 'professional', 'maintenance', 'repair', 'advisory', 'advice', 'consultation', 'support',
                        'assistance', 'expertise', 'specialist', 'professional service', 'consulting service', 'consultancy service', 'service provider',
                        'professional advice', 'professional consultation', 'professional assistance', 'expert service', 'specialized service',
                        'technical service', 'business service', 'service fee', 'service charge', 'service payment'],
            'software_services': ['software', 'license', 'subscription', 'application', 'program', 'IT service', 'software development', 'tech support'],
            'tech': ['technology', 'it', 'computer', 'hardware', 'tech', 'digital', 'electronic', 'information technology', 'technical'],
            'transportation': ['transport', 'shipping', 'freight', 'logistics', 'delivery', 'cargo', 'shipment', 'transportation', 'courier'],
            'travel': ['travel', 'trip', 'journey', 'vacation', 'holiday', 'tour', 'tourism', 'flight', 'hotel', 'accommodation'],
            'goods': ['goods', 'product', 'merchandise', 'item', 'commodity', 'retail', 'wholesale', 'purchase', 'supply', 'inventory'],
            'insurance': ['insurance', 'policy', 'premium', 'coverage', 'claim', 'insurer', 'policyholder', 'underwriting', 'risk'],
            'message_type': ['mt103', 'mt202', 'mt202cov', 'mt205', 'mt205cov', 'swift', 'message', 'instruction'],
            'category_purpose': ['category', 'purpose', 'code', 'classification', 'reason', 'type', 'nature']
        }

        # Check if we have word embeddings available for semantic matching
        has_embeddings = hasattr(self, 'matcher') and self.matcher and hasattr(self.matcher, 'embeddings') and self.matcher.embeddings

        # Calculate relevance scores based on keyword matches and semantic similarity
        for enhancer_name in enhancer_names:
            # Default base score
            base_score = 0.5

            # Get keywords for this enhancer
            keywords = enhancer_keywords.get(enhancer_name, [])

            # 1. Exact keyword matching
            exact_matches = sum(1 for keyword in keywords if keyword in narration_lower)
            if keywords:
                exact_score = min(1.0, exact_matches / len(keywords) * 2)  # Scale up to 1.0
            else:
                exact_score = 0.0

            # 2. Semantic similarity matching (if word embeddings are available)
            semantic_score = 0.0
            if has_embeddings and keywords:
                # Tokenize the narration
                narration_tokens = self.matcher.tokenize(narration_lower)

                # Calculate semantic similarity for each keyword
                semantic_matches = []
                for keyword in keywords:
                    # For multi-word keywords, split and check each word
                    keyword_tokens = keyword.split()

                    # For each token in the narration, find the maximum similarity with any keyword token
                    for narr_token in narration_tokens:
                        # Skip very short tokens
                        if len(narr_token) < 3:
                            continue

                        # Find maximum similarity with any keyword token
                        max_similarity = 0.0
                        for kw_token in keyword_tokens:
                            # Skip very short tokens
                            if len(kw_token) < 3:
                                continue

                            try:
                                similarity = self.matcher.semantic_similarity(narr_token, kw_token)
                                max_similarity = max(max_similarity, similarity)
                            except Exception as e:
                                # If semantic similarity fails, just continue
                                logger.debug(f"Error calculating semantic similarity: {str(e)}")
                                continue

                        # If similarity is above threshold, count as a match
                        if max_similarity >= 0.7:  # Threshold for semantic similarity
                            semantic_matches.append((narr_token, keyword, max_similarity))

                # Calculate semantic score based on unique matches
                if semantic_matches:
                    # Get unique narration tokens that matched
                    unique_matches = set(match[0] for match in semantic_matches)
                    semantic_score = min(1.0, len(unique_matches) / len(narration_tokens) * 3)  # Scale up to 1.0

                    # Log semantic matches for debugging
                    if semantic_score > 0.3:
                        logger.debug(f"Semantic matches for {enhancer_name}: {semantic_matches}")

            # 3. Get priority weight from existing priorities
            priority_weight = self.priorities.get(enhancer_name, {}).get('weight', 0.5)

            # 4. Calculate combined relevance score
            # Give more weight to exact matches than semantic matches
            combined_score = (exact_score * 0.6) + (semantic_score * 0.4)

            # 5. Calculate final relevance score with base score and priority weight
            relevance_score = (base_score + combined_score) * priority_weight

            # Ensure score is between 0 and 1
            relevance_scores[enhancer_name] = min(1.0, relevance_score)

            # Log high relevance scores for debugging
            if relevance_score > 0.7:
                logger.info(f"High relevance for {enhancer_name}: {relevance_score:.2f} (exact: {exact_score:.2f}, semantic: {semantic_score:.2f})")

        # Ensure all enhancers have a score
        for enhancer_name in enhancer_names:
            if enhancer_name not in relevance_scores:
                # Default score based on priority weight
                priority_weight = self.priorities.get(enhancer_name, {}).get('weight', 0.5)
                relevance_scores[enhancer_name] = 0.5 * priority_weight

        return relevance_scores

    def update_confidence_history(self, enhancer_name, was_correct):
        """
        Update confidence history for an enhancer.

        Args:
            enhancer_name: The name of the enhancer
            was_correct: Whether the enhancer's prediction was correct
        """
        if enhancer_name not in self.adaptive_confidence['confidence_history']:
            self.adaptive_confidence['confidence_history'][enhancer_name] = {
                'correct': 0,
                'total': 0,
                'recent_results': []
            }

        history = self.adaptive_confidence['confidence_history'][enhancer_name]

        # Update counts
        history['total'] += 1
        if was_correct:
            history['correct'] += 1

        # Update recent results
        history['recent_results'].append(was_correct)

        # Trim recent results if needed
        if len(history['recent_results']) > self.adaptive_confidence['max_history_size']:
            history['recent_results'].pop(0)

    def log_enhancer_decisions(self, result):
        """
        Log enhancer decisions for debugging and analysis.

        Args:
            result: Enhanced classification result with enhancer_decisions
        """
        if 'enhancer_decisions' not in result:
            logger.debug("No enhancer decisions recorded")
            return

        decisions = result['enhancer_decisions']
        logger.debug(f"Enhancer decisions for narration: {result.get('narration', 'N/A')}")
        logger.debug(f"Initial purpose code: {result.get('initial_purpose_code', 'OTHR')}")
        logger.debug(f"Final purpose code: {result['purpose_code']}")

        for decision in decisions:
            applied_str = "APPLIED" if decision['applied'] else "NOT APPLIED"
            logger.debug(
                f"Enhancer: {decision['enhancer']} | "
                f"{decision['old_code']} -> {decision['new_code']} | "
                f"Confidence: {decision['confidence']:.2f} | "
                f"Threshold: {decision['threshold']:.2f} | "
                f"{applied_str} | "
                f"Reason: {decision.get('reason', 'No reason provided')}"
            )
