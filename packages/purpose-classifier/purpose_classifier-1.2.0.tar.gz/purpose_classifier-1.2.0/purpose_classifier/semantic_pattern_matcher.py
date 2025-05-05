"""
Semantic Pattern Matcher for Purpose Code Classification.

This module provides semantic pattern matching capabilities for enhancing
purpose code classification accuracy through word embeddings and context-aware
pattern matching.
"""

import os
import logging
import itertools
import numpy as np
from functools import lru_cache
from nltk.tokenize import word_tokenize

# Import optimized word embeddings
from purpose_classifier.optimized_embeddings import word_embeddings

logger = logging.getLogger(__name__)

class SemanticPatternMatcher:
    """
    Base class for semantic pattern matching.

    Provides functionality for calculating semantic similarity and performing
    context-aware pattern matching for purpose code classification using
    optimized word embeddings.
    """

    def __init__(self, embeddings_path=None):
        """
        Initialize the semantic pattern matcher.

        Args:
            embeddings_path: Optional path to word embeddings file
        """
        # Use the global word embeddings singleton
        if embeddings_path:
            # If a specific path is provided, update the singleton's path
            word_embeddings._embeddings_path = embeddings_path

        # Ensure embeddings are loaded (lazy loading)
        if not word_embeddings.is_loaded:
            word_embeddings.load()

        # Store a reference to the embeddings for backward compatibility
        self.embeddings = word_embeddings.embeddings

        logger.info(f"SemanticPatternMatcher initialized with optimized word embeddings")

    def load_word_embeddings(self, model_path='models/word_embeddings.pkl'):
        """
        Load pre-trained word embeddings from file.
        Supports Word2Vec, GloVe, or FastText formats.

        Args:
            model_path: Path to the word embeddings file

        Returns:
            bool: True if embeddings were loaded successfully
        """
        # Update the singleton's path and force reload
        word_embeddings._embeddings_path = model_path
        success = word_embeddings.load(force=True)

        # Update our reference
        if success:
            self.embeddings = word_embeddings.embeddings

        return success

    @lru_cache(maxsize=5000)
    def semantic_similarity(self, word1, word2):
        """
        Calculate semantic similarity between two words using word embeddings.
        Returns similarity score between 0 and 1.

        Args:
            word1: First word or text
            word2: Second word or list of words

        Returns:
            float: Similarity score between 0 and 1
        """
        # Handle the case where word2 is a list of terms
        if isinstance(word2, list):
            return self.semantic_similarity_with_terms(word1, word2)

        # Use the optimized word embeddings singleton
        return word_embeddings.get_similarity(word1, word2)

    def semantic_similarity_with_terms(self, text, terms):
        """
        Calculate semantic similarity between text and a list of terms.
        Returns the highest similarity score found.

        Args:
            text: Input text
            terms: List of terms to compare against

        Returns:
            float: Highest similarity score between 0 and 1
        """
        if not self.embeddings:
            logger.warning("Word embeddings not loaded, returning 0 similarity")
            return 0.0

        logger.debug(f"Calculating semantic similarity between text '{text}' and terms {terms}")

        # Tokenize the input text
        words = self.tokenize(text.lower())
        logger.debug(f"Tokenized words: {words}")

        # Calculate the maximum similarity for each word in the text against all terms
        max_similarities = []
        word_term_matches = []

        for word in words:
            word_max_similarity = 0.0
            best_term = None

            for term in terms:
                # Skip if word or term is not in embeddings
                if hasattr(self.embeddings, 'key_to_index'):
                    if word not in self.embeddings.key_to_index:
                        logger.debug(f"Word '{word}' not found in embeddings")
                        continue
                    if term not in self.embeddings.key_to_index:
                        logger.debug(f"Term '{term}' not found in embeddings")
                        continue
                elif hasattr(self.embeddings, '__contains__'):
                    if word not in self.embeddings:
                        logger.debug(f"Word '{word}' not found in embeddings")
                        continue
                    if term not in self.embeddings:
                        logger.debug(f"Term '{term}' not found in embeddings")
                        continue

                try:
                    similarity = self.embeddings.similarity(word, term)
                    normalized_similarity = max(0.0, min(1.0, (similarity + 1) / 2))  # Normalize to [0,1]
                    logger.debug(f"Similarity between '{word}' and '{term}': {normalized_similarity:.4f}")

                    if normalized_similarity > word_max_similarity:
                        word_max_similarity = normalized_similarity
                        best_term = term

                except Exception as e:
                    logger.warning(f"Error calculating similarity between '{word}' and '{term}': {str(e)}")
                    continue

            if word_max_similarity > 0:
                max_similarities.append(word_max_similarity)
                word_term_matches.append((word, best_term, word_max_similarity))

        # Log the best matches
        if word_term_matches:
            logger.debug("Best word-term matches:")
            for word, term, score in sorted(word_term_matches, key=lambda x: x[2], reverse=True):
                logger.debug(f"  '{word}' -> '{term}': {score:.4f}")

        # Return a weighted average of the top similarities
        if max_similarities:
            max_similarities.sort(reverse=True)

            # Use all similarities but with a weighted average that emphasizes higher scores
            # This gives more weight to strong matches while still considering all matches
            weights = []
            for i, score in enumerate(max_similarities):
                # Higher scores get higher weights, and earlier positions get higher weights
                weight = score * (1.0 / (i + 1))
                weights.append(weight)

            # Calculate weighted average
            weighted_sum = sum(s * w for s, w in zip(max_similarities, weights))
            total_weight = sum(weights)

            result = weighted_sum / total_weight if total_weight > 0 else 0.0

            # Apply a boost for multiple strong matches
            if len(max_similarities) >= 2 and max_similarities[0] > 0.7 and max_similarities[1] > 0.6:
                # Boost the score if we have multiple strong matches
                result = min(1.0, result * 1.1)  # 10% boost, capped at 1.0
                logger.debug(f"Applied multiple strong matches boost")

            logger.debug(f"Final similarity score: {result:.4f} (weighted average of {len(max_similarities)} matches)")
            return result

        logger.debug("No similarities found, returning 0.0")
        return 0.0

    def find_similar_words(self, word, threshold=0.7):
        """
        Find words semantically similar to the input word.
        Returns list of (word, similarity) tuples above threshold.

        Args:
            word: Input word to find similar words for
            threshold: Minimum similarity threshold

        Returns:
            list: List of (word, similarity) tuples above threshold
        """
        logger.debug(f"Finding words similar to '{word}' with threshold {threshold}")

        # Use the optimized word embeddings singleton
        return word_embeddings.find_similar_words(word, threshold)

    def context_match(self, text, context_patterns):
        """
        Match text against semantic context patterns.

        Args:
            text (str): The text to analyze
            context_patterns (list): List of context pattern dictionaries
                Each dict has keys: 'keywords', 'proximity', 'weight'

        Returns:
            float: Match score between 0 and 1
        """
        words = self.tokenize(text.lower())
        total_score = 0.0
        max_weight = sum(pattern['weight'] for pattern in context_patterns)

        for pattern in context_patterns:
            keywords = pattern['keywords']
            proximity = pattern['proximity']
            weight = pattern['weight']

            # Check if all keywords are within proximity
            if self.keywords_in_proximity(words, keywords, proximity):
                total_score += weight

        return total_score / max_weight if max_weight > 0 else 0.0

    def keywords_in_proximity(self, words, keywords, max_distance):
        """
        Check if all keywords appear within the specified proximity.

        Args:
            words (list): Tokenized words from text
            keywords (list): Keywords to check for
            max_distance (int): Maximum word distance between keywords

        Returns:
            bool: True if all keywords are within proximity
        """
        logger.debug(f"Checking if keywords {keywords} are within proximity {max_distance} in words: {words}")

        # Find positions of all keywords
        positions = {}
        for keyword in keywords:
            keyword_positions = []
            for i, word in enumerate(words):
                # Direct match
                if word == keyword:
                    logger.debug(f"Direct match: '{word}' == '{keyword}' at position {i}")
                    keyword_positions.append(i)
                # Semantic similarity match if embeddings are available
                elif self.embeddings and hasattr(self.embeddings, 'similarity'):
                    try:
                        similarity = self.semantic_similarity(word, keyword)
                        logger.debug(f"Semantic similarity between '{word}' and '{keyword}': {similarity:.4f}")
                        # Lower the threshold from 0.8 to 0.7 for better recall
                        if similarity > 0.7:
                            logger.debug(f"Semantic match: '{word}' ~ '{keyword}' at position {i} with similarity {similarity:.4f}")
                            keyword_positions.append(i)
                        # Add partial match for medium similarity (0.6-0.7)
                        elif similarity > 0.6:
                            logger.debug(f"Partial semantic match: '{word}' ~ '{keyword}' at position {i} with similarity {similarity:.4f}")
                            # For partial matches, we still add the position but with a note
                            keyword_positions.append(i)
                    except Exception as e:
                        # Skip if semantic similarity fails
                        logger.debug(f"Error calculating similarity between '{word}' and '{keyword}': {str(e)}")
                        pass

            # If no positions found for this keyword, return False
            if not keyword_positions:
                logger.debug(f"No positions found for keyword '{keyword}', returning False")
                return False

            positions[keyword] = keyword_positions
            logger.debug(f"Positions for keyword '{keyword}': {keyword_positions}")

        # Check if any combination of positions is within max_distance
        position_combinations = list(itertools.product(*positions.values()))
        logger.debug(f"Checking {len(position_combinations)} position combinations")

        for combo in position_combinations:
            distance = max(combo) - min(combo)
            logger.debug(f"Position combination {combo}, distance: {distance}")
            if distance <= max_distance:
                logger.debug(f"Found keywords within proximity {max_distance}, returning True")
                return True

        logger.debug(f"No keywords found within proximity {max_distance}, returning False")
        return False

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

    def tokenize(self, text):
        """
        Tokenize text into words.

        Args:
            text (str): Input text

        Returns:
            list: List of tokens
        """
        return word_tokenize(text)
