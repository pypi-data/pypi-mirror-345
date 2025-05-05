"""
Feature extraction utilities for MT message purpose code classification.
Provides vectorization and feature transformation for text data.
"""

import logging
import numpy as np
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_selection import SelectKBest, chi2
from concurrent.futures import ThreadPoolExecutor

# Import configuration
import sys
import os
from purpose_classifier.config.settings import MODEL_SETTINGS, PROD_SETTINGS, MESSAGE_TYPES, setup_logging, get_environment


class FinancialNGramExtractor:
    """
    Custom n-gram extractor for financial text.
    Creates domain-specific n-grams for financial terms.
    """

    def __init__(self):
        """Initialize with financial n-gram patterns"""
        # Common financial bigram patterns
        self.financial_bigrams = [
            r'\b(payment)\s+(for)\b',
            r'\b(invoice)\s+(payment)\b',
            r'\b(invoice)\s+(number)\b',
            r'\b(account)\s+(transfer)\b',
            r'\b(salary)\s+(payment)\b',
            r'\b(interest)\s+(payment)\b',
            r'\b(loan)\s+(repayment)\b',
            r'\b(trade)\s+(settlement)\b',
            r'\b(dividend)\s+(payment)\b',
            r'\b(tax)\s+(payment)\b',
            r'\b(pension)\s+(contribution)\b',
            r'\b(investment)\s+(return)\b',
        ]
        # Compile patterns
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.financial_bigrams]

    def extract_financial_ngrams(self, text):
        """
        Extract financial n-grams from text.

        Args:
            text: Preprocessed text

        Returns:
            List of financial n-grams found in text
        """
        ngrams = []
        # Apply each pattern and collect matches
        for pattern in self.compiled_patterns:
            matches = pattern.findall(text)
            if matches:
                # Join tuples into phrases
                for match in matches:
                    if isinstance(match, tuple):
                        ngrams.append('_'.join(match))
                    else:
                        ngrams.append(match)

        return ngrams


class DomainFeatureExtractor:
    """
    Extracts domain-specific features from financial texts.
    """

    def __init__(self):
        """Initialize domain feature patterns"""
        # Patterns for domain-specific features
        self.patterns = {
            'has_account_number': r'\b[A-Za-z]{1,4}\d{10,24}\b',
            'has_amount': r'\b\d+[\.,]\d+\b',
            'has_currency': r'\b(?:USD|EUR|GBP|JPY|CHF|CAD|AUD)\b',
            'has_reference': r'\b(?:ref|reference)[:\s]+([A-Za-z0-9\-_/]+)',
            'has_invoice': r'\b(?:inv|invoice)[:\s]+([A-Za-z0-9\-_/]+)',
            'has_date': r'\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b'
        }
        # Compile patterns
        self.compiled_patterns = {name: re.compile(pattern, re.IGNORECASE)
                                 for name, pattern in self.patterns.items()}

    def extract_features(self, text):
        """
        Extract domain-specific binary features from text.

        Args:
            text: Input text

        Returns:
            Dictionary of boolean features
        """
        features = {}

        # Apply each pattern and set feature value
        for name, pattern in self.compiled_patterns.items():
            features[name] = bool(pattern.search(text))

        # Additional specialized features
        features['word_count'] = len(text.split())
        features['is_short_text'] = features['word_count'] < 5
        features['is_long_text'] = features['word_count'] > 15

        return features


class FeatureExtractor(BaseEstimator, TransformerMixin):
    """
    Feature extraction for MT message narrations.
    Provides TF-IDF vectorization with configurable parameters.
    Supports different message types and financial-specific features.
    """

    def __init__(self, max_features=1500, ngram_range=(1, 3), min_df=2, max_df=0.95,
                feature_selection=True, k_best_features=1000, use_domain_features=True):
        """
        Initialize feature extractor with vectorization parameters.

        Args:
            max_features: Maximum number of features to extract
            ngram_range: Range of n-grams to consider
            min_df: Minimum document frequency for terms
            max_df: Maximum document frequency for terms
            feature_selection: Whether to perform feature selection
            k_best_features: Number of best features to select
            use_domain_features: Whether to use domain-specific features
        """
        self.env = get_environment()
        self.logger = setup_logging(self.env)

        self.max_features = max_features
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.max_df = max_df
        self.feature_selection = feature_selection
        self.k_best_features = k_best_features
        self.use_domain_features = use_domain_features

        # Initialize the vectorizer with financial terms optimization
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            min_df=self.min_df,
            max_df=self.max_df,
            sublinear_tf=True,  # Apply sublinear tf scaling (1 + log(tf))
            use_idf=True,
            strip_accents='unicode',
            analyzer='word',
            token_pattern=r'\b\w+\b',  # Match words
            stop_words=None  # Stopwords already handled in preprocessor
        )

        # Initialize feature selection if enabled
        self.selector = SelectKBest(chi2, k=self.k_best_features) if self.feature_selection else None

        # Initialize financial n-gram extractor
        self.ngram_extractor = FinancialNGramExtractor()

        # Initialize domain feature extractor
        self.domain_extractor = DomainFeatureExtractor() if self.use_domain_features else None

        # Track feature names
        self.feature_names = None
        self.domain_feature_names = None

        # Message type-specific configurations
        self.message_type_configs = MESSAGE_TYPES

        self.logger.info(f"Enhanced FeatureExtractor initialized with max_features={max_features}, "
                         f"ngram_range={ngram_range}, feature_selection={feature_selection}")

    def fit(self, texts, y=None, message_types=None):
        """
        Fit the vectorizer on the training texts.

        Args:
            texts: List of preprocessed text strings
            y: Target values (used for feature selection)
            message_types: List of message types corresponding to texts

        Returns:
            self
        """
        if not texts:
            self.logger.error("Cannot fit on empty text data")
            raise ValueError("Cannot fit on empty text data")

        # Extract financial n-grams and add to texts
        enhanced_texts = self._enhance_texts_with_ngrams(texts)

        self.logger.info(f"Fitting vectorizer on {len(enhanced_texts)} texts")

        # Fit the vectorizer
        X = self.vectorizer.fit_transform(enhanced_texts)

        # Apply feature selection if enabled and target values are provided
        if self.feature_selection and y is not None:
            self.logger.info(f"Performing feature selection to get {self.k_best_features} best features")
            self.selector.fit(X, y)

            # Get selected feature indices
            selected_indices = self.selector.get_support(indices=True)

            # Update feature names
            all_features = self.vectorizer.get_feature_names_out()
            self.feature_names = [all_features[i] for i in selected_indices]
        else:
            # If feature selection is enabled but no y is provided, disable it for this fit
            if self.feature_selection and y is None:
                self.logger.warning("Feature selection enabled but no target values provided. Using all features.")

            self.feature_names = self.vectorizer.get_feature_names_out()

        # Set up domain feature names if using domain features
        if self.use_domain_features:
            self.domain_feature_names = list(self.domain_extractor.patterns.keys()) + \
                                       ['word_count', 'is_short_text', 'is_long_text']

        # Log vocabulary size and some sample features
        vocab_size = len(self.feature_names)
        self.logger.info(f"Vocabulary size after fitting: {vocab_size}")

        if vocab_size > 0 and self.logger.isEnabledFor(logging.DEBUG):
            sample_features = self.feature_names[:10]
            self.logger.debug(f"Sample features: {sample_features}")

        return self

    def _enhance_texts_with_ngrams(self, texts):
        """
        Enhance texts with financial n-grams.

        Args:
            texts: List of preprocessed text strings

        Returns:
            List of enhanced texts
        """
        enhanced_texts = []

        for text in texts:
            # Extract financial n-grams
            financial_ngrams = self.ngram_extractor.extract_financial_ngrams(text)

            # Add n-grams to text
            enhanced_text = text + ' ' + ' '.join(financial_ngrams)
            enhanced_texts.append(enhanced_text)

        return enhanced_texts

    def _extract_domain_features(self, texts):
        """
        Extract domain-specific features from texts.

        Args:
            texts: List of preprocessed text strings

        Returns:
            DataFrame with domain features
        """
        features_list = []

        for text in texts:
            features = self.domain_extractor.extract_features(text)
            features_list.append(features)

        # Convert to DataFrame
        return pd.DataFrame(features_list)

    def transform(self, texts, message_types=None):
        """
        Transform text data to feature vectors.

        Args:
            texts: List of preprocessed text strings
            message_types: List of message types corresponding to texts

        Returns:
            Feature matrix (sparse or ndarray depending on use_domain_features)
        """
        if not texts:
            self.logger.warning("Transforming empty text data")
            if self.use_domain_features:
                return np.zeros((0, len(self.feature_names) + len(self.domain_feature_names)
                               if hasattr(self, 'feature_names') and hasattr(self, 'domain_feature_names') else 0))
            else:
                return np.zeros((0, len(self.feature_names) if hasattr(self, 'feature_names') else 0))

        try:
            # Enhance texts with financial n-grams
            enhanced_texts = self._enhance_texts_with_ngrams(texts)

            # Transform texts with vectorizer
            X = self.vectorizer.transform(enhanced_texts)

            # Apply feature selection if enabled and selector is fit
            if self.feature_selection and hasattr(self, 'selector') and self.selector is not None:
                # Check if selector has been fit
                try:
                    # Check if the selector has been properly fit
                    if hasattr(self.selector, '_check_is_fitted'):
                        try:
                            self.selector._check_is_fitted()
                            X = self.selector.transform(X)
                        except Exception:
                            # If not fitted, just use all features without warning
                            pass
                    else:
                        # Try to transform and catch any errors
                        try:
                            X = self.selector.transform(X)
                        except Exception:
                            # If it fails, just use all features without warning
                            pass
                except Exception as selector_error:
                    # Continue with all features without warning
                    pass

            # Extract domain features if enabled
            if self.use_domain_features:
                domain_features_df = self._extract_domain_features(texts)

                # Convert sparse matrix to dense for concatenation
                X_dense = X.toarray()

                # Convert domain features to numpy array
                domain_features = domain_features_df.values

                # Concatenate
                X_combined = np.hstack((X_dense, domain_features))

                self.logger.info(f"Transformed {len(texts)} texts to feature matrix "
                                f"of shape {X_combined.shape} with domain features")

                return X_combined
            else:
                self.logger.info(f"Transformed {len(texts)} texts to feature matrix of shape {X.shape}")
                return X

        except Exception as e:
            self.logger.error(f"Error transforming texts: {str(e)}")
            raise

    def fit_transform(self, texts, y=None, message_types=None):
        """
        Fit the vectorizer and transform the texts in one step.

        Args:
            texts: List of preprocessed text strings
            y: Target values (used for feature selection)
            message_types: List of message types corresponding to texts

        Returns:
            Feature matrix
        """
        return self.fit(texts, y, message_types).transform(texts, message_types)

    def get_feature_names(self):
        """
        Get the feature names (vocabulary terms).

        Returns:
            List of feature names
        """
        if not hasattr(self, 'feature_names') or self.feature_names is None:
            self.logger.error("Vectorizer not fitted yet")
            raise RuntimeError("Vectorizer not fitted yet")

        if self.use_domain_features and hasattr(self, 'domain_feature_names'):
            return list(self.feature_names) + list(self.domain_feature_names)
        else:
            return list(self.feature_names)

    def get_message_type_features(self, message_type):
        """
        Get features specific to a message type.

        Args:
            message_type: Type of MT message (e.g., 'MT103')

        Returns:
            List of features specific to this message type
        """
        if message_type not in self.message_type_configs:
            self.logger.warning(f"Unknown message type: {message_type}")
            return []

        # Return message type-specific features
        config = self.message_type_configs[message_type]
        field = config['narration_field']

        # Features specific to this message type's field
        return [f"field_{field}", f"has_field_{field}"]

    def extract_top_features(self, feature_matrix, top_n=10):
        """
        Extract top N features with highest values from a feature matrix.

        Args:
            feature_matrix: Feature matrix from transform()
            top_n: Number of top features to extract

        Returns:
            List of (feature_name, weight) tuples
        """
        if not hasattr(self, 'feature_names') or self.feature_names is None:
            self.logger.error("Vectorizer not fitted yet")
            raise RuntimeError("Vectorizer not fitted yet")

        if feature_matrix.shape[0] != 1:
            self.logger.error("Can only extract top features from a single document (matrix row)")
            raise ValueError("Feature matrix must have exactly 1 row")

        # Get feature names
        feature_names = self.get_feature_names()

        # Get feature importance
        if isinstance(feature_matrix, np.ndarray):
            # For dense arrays (when domain features are used)
            dense_features = feature_matrix[0]
        else:
            # For sparse matrices
            dense_features = feature_matrix.toarray()[0]

        # Ensure we only look at the number of features we have
        num_features = min(len(feature_names), dense_features.shape[0])

        # Get indices of top features
        top_indices = dense_features[:num_features].argsort()[-top_n:][::-1]

        # Create list of (feature_name, weight) tuples
        top_features = [(feature_names[i], dense_features[i]) for i in top_indices]

        return top_features

    def batch_transform(self, texts, message_types=None, batch_size=PROD_SETTINGS['batch_size']):
        """
        Process texts in batches for production workloads.

        Args:
            texts: List of text strings
            message_types: List of message types corresponding to texts
            batch_size: Batch size for processing

        Returns:
            Combined feature matrix
        """
        # Create batches
        batches = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]

            # Create message types batch if provided
            batch_message_types = None
            if message_types is not None:
                batch_message_types = message_types[i:i + batch_size]

            batches.append((batch_texts, batch_message_types))

        # Process batches in parallel
        results = []
        with ThreadPoolExecutor(max_workers=PROD_SETTINGS['max_workers']) as executor:
            # Submit all batches for processing
            futures = [
                executor.submit(self.transform, batch_texts, batch_message_types)
                for batch_texts, batch_message_types in batches
            ]

            # Gather results
            for future in futures:
                result = future.result()
                results.append(result)

        # Combine results based on result type
        if results and isinstance(results[0], np.ndarray):
            # For dense arrays (with domain features)
            return np.vstack(results)
        else:
            # For sparse matrices
            from scipy.sparse import vstack
            return vstack(results)

    def get_feature_importance(self, model):
        """
        Get feature importance from a trained model.

        Args:
            model: Trained classifier with feature_importances_ attribute

        Returns:
            DataFrame with feature importance scores
        """
        if not hasattr(model, 'feature_importances_'):
            self.logger.error("Model does not have feature_importances_ attribute")
            raise ValueError("Model does not support feature importance")

        feature_names = self.get_feature_names()
        importances = model.feature_importances_

        # Create DataFrame
        importance_df = pd.DataFrame({
            'feature': feature_names[:len(importances)],
            'importance': importances
        }).sort_values('importance', ascending=False)

        return importance_df