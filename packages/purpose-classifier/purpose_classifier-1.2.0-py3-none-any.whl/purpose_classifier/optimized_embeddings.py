"""
Optimized Word Embeddings for Purpose Code Classification.

This module provides optimized word embeddings with lazy loading, caching,
and singleton pattern to improve performance.
"""

import os
import pickle
import logging
import numpy as np
from functools import lru_cache
from gensim.models import KeyedVectors

logger = logging.getLogger(__name__)

class WordEmbeddingsSingleton:
    """
    Singleton class for word embeddings.

    This class implements the singleton pattern to ensure that only one instance
    of the word embeddings is loaded in memory, regardless of how many enhancers
    use it.
    """

    _instance = None
    _embeddings = None
    _is_loaded = False

    def __new__(cls, embeddings_path=None):
        """
        Create a new instance if one doesn't exist.

        Args:
            embeddings_path: Path to the word embeddings file

        Returns:
            WordEmbeddingsSingleton: The singleton instance
        """
        if cls._instance is None:
            cls._instance = super(WordEmbeddingsSingleton, cls).__new__(cls)
            cls._instance._embeddings_path = embeddings_path or cls._get_default_path()
            cls._instance._cache_hits = 0
            cls._instance._cache_misses = 0
        return cls._instance

    @staticmethod
    def _get_default_path():
        """
        Get the default path for word embeddings.

        Returns:
            str: Default path for word embeddings
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, 'models', 'word_embeddings.pkl')

    def load(self, force=False):
        """
        Load word embeddings from file.

        Args:
            force: Force reload even if already loaded

        Returns:
            bool: True if embeddings were loaded successfully
        """
        if self._is_loaded and not force:
            logger.debug("Word embeddings already loaded")
            return True

        try:
            logger.info(f"Loading word embeddings from {self._embeddings_path}")

            if self._embeddings_path.endswith('.pkl'):
                with open(self._embeddings_path, 'rb') as f:
                    self._embeddings = pickle.load(f)
            elif self._embeddings_path.endswith('.bin'):
                self._embeddings = KeyedVectors.load_word2vec_format(self._embeddings_path, binary=True)
            else:
                self._embeddings = KeyedVectors.load_word2vec_format(self._embeddings_path)

            # Log success
            if hasattr(self._embeddings, 'key_to_index'):
                logger.info(f"Word embeddings loaded successfully with {len(self._embeddings.key_to_index)} words")
            else:
                logger.info("Word embeddings loaded successfully")

            self._is_loaded = True
            return True

        except Exception as e:
            logger.error(f"Error loading word embeddings: {str(e)}")
            self._is_loaded = False
            return False

    @property
    def embeddings(self):
        """
        Get the word embeddings.

        Returns:
            object: Word embeddings object
        """
        if not self._is_loaded:
            self.load()
        return self._embeddings

    @property
    def is_loaded(self):
        """
        Check if embeddings are loaded.

        Returns:
            bool: True if embeddings are loaded
        """
        return self._is_loaded

    @lru_cache(maxsize=10000)
    def get_similarity(self, word1, word2):
        """
        Get similarity between two words with caching.

        Args:
            word1: First word
            word2: Second word

        Returns:
            float: Similarity between words (0-1)
        """
        if not self._is_loaded:
            self.load()

        if not self._embeddings:
            return 0.0

        try:
            if word1 not in self._embeddings or word2 not in self._embeddings:
                self._cache_misses += 1
                return 0.0

            similarity = self._embeddings.similarity(word1, word2)
            self._cache_hits += 1

            # Normalize to [0,1]
            return max(0.0, min(1.0, (similarity + 1) / 2))

        except Exception as e:
            logger.debug(f"Error calculating similarity between {word1} and {word2}: {str(e)}")
            self._cache_misses += 1
            return 0.0

    @lru_cache(maxsize=1000)
    def find_similar_words(self, word, threshold=0.7, topn=20):
        """
        Find words similar to the input word with caching.

        Args:
            word: Input word
            threshold: Similarity threshold
            topn: Maximum number of similar words to return

        Returns:
            list: List of (word, similarity) tuples
        """
        if not self._is_loaded:
            self.load()

        if not self._embeddings or word not in self._embeddings:
            return []

        try:
            similar_words = self._embeddings.most_similar(word, topn=topn)
            return [(w, s) for w, s in similar_words if s >= threshold]

        except Exception as e:
            logger.debug(f"Error finding similar words for {word}: {str(e)}")
            return []

    def get_cache_stats(self):
        """
        Get cache statistics.

        Returns:
            dict: Cache statistics
        """
        total = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total if total > 0 else 0

        return {
            'hits': self._cache_hits,
            'misses': self._cache_misses,
            'total': total,
            'hit_rate': hit_rate
        }

    def clear_cache(self):
        """Clear the similarity cache."""
        self.get_similarity.cache_clear()
        self.find_similar_words.cache_clear()
        self._cache_hits = 0
        self._cache_misses = 0
        logger.info("Word embeddings cache cleared")

# Create a global instance for easy access
word_embeddings = WordEmbeddingsSingleton()
