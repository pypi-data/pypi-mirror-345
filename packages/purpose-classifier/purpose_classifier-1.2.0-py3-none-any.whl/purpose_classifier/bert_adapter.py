#!/usr/bin/env python
"""
BERT Adapter for Purpose Code Classification

This module provides adapter classes to make BERT models compatible with the
LightGBMPurposeClassifier interface.
"""

import os
import re
import torch
import logging
import numpy as np
from functools import lru_cache

# Configure logging
logger = logging.getLogger(__name__)

# Set a filter to suppress specific warnings
class SuppressSpecificWarning(logging.Filter):
    def filter(self, record):
        return not (record.levelname == 'WARNING' and
                   "Received dense array input, but BERT requires text input" in record.getMessage())

# Apply the filter to the logger
logger.addFilter(SuppressSpecificWarning())

class BertModelAdapter:
    """
    Adapter class for BERT models to make them compatible with the LightGBM interface.

    This class wraps a BERT model and provides a predict method that follows the
    same interface as LightGBM's predict method, making it a drop-in replacement
    in the LightGBMPurposeClassifier.
    """

    def __init__(self, bert_model, tokenizer, device=None):
        """
        Initialize the adapter with a BERT model and tokenizer.

        Args:
            bert_model: The BERT model (BertForSequenceClassification)
            tokenizer: The BERT tokenizer
            device: The device to run inference on ('cuda' or 'cpu')
        """
        self.bert_model = bert_model
        self.tokenizer = tokenizer

        # Determine device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = device

        # Make sure model is on the correct device
        self.bert_model.to(self.device)

        # Put model in evaluation mode
        self.bert_model.eval()

        logger.info(f"BertModelAdapter initialized with device: {self.device}")

    @lru_cache(maxsize=1000)
    def _tokenize(self, text):
        """Tokenize text for BERT input."""
        return self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=128,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

    def predict(self, X, raw_score=False):
        """
        Predict purpose codes from text using the BERT model.

        Args:
            X: Input features (array-like) or raw text
            raw_score: Whether to return raw scores or probabilities

        Returns:
            Numpy array of predictions
        """
        # Handle different input types
        if isinstance(X, np.ndarray) and X.ndim == 2:
            # Assuming this is a dense array from vectorizer.transform().toarray()
            # We need to convert it back to text for BERT
            logger.warning("Received dense array input, but BERT requires text input. "
                          "This might indicate incompatible usage. Using placeholder text.")
            # Use a placeholder since we can't reconstruct the original text
            text_batch = ["placeholder_text"] * X.shape[0]
        elif isinstance(X, list):
            # Assuming this is a list of processed texts
            text_batch = X
        else:
            # Single item
            text_batch = [X]

        # Tokenize inputs
        batch_encodings = [self._tokenize(text) for text in text_batch]

        # Merge encodings into batches
        input_ids = torch.cat([enc['input_ids'] for enc in batch_encodings], dim=0).to(self.device)
        attention_mask = torch.cat([enc['attention_mask'] for enc in batch_encodings], dim=0).to(self.device)

        # Get predictions
        with torch.no_grad():
            outputs = self.bert_model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits

            if raw_score:
                # Return raw logits
                return logits.cpu().numpy()
            else:
                # Apply softmax to get probabilities
                probs = torch.nn.functional.softmax(logits, dim=1)
                return probs.cpu().numpy()

class CustomNumpyArray(np.ndarray):
    """A wrapper around numpy.ndarray that provides a toarray method for compatibility."""

    def __new__(cls, input_array):
        obj = np.asarray(input_array).view(cls)
        return obj

    def toarray(self):
        """Return self to be compatible with sparse matrices."""
        return self

    def __array_finalize__(self, obj):
        if obj is None: return

class BertVectorizerAdapter:
    """
    Adapter class for BERT tokenizer to make it compatible with the TfidfVectorizer interface.

    This class wraps a BERT tokenizer and provides transform and fit_transform methods
    that follow the same interface as sklearn's TfidfVectorizer.
    """

    def __init__(self, tokenizer):
        """
        Initialize the adapter with a BERT tokenizer.

        Args:
            tokenizer: The BERT tokenizer
        """
        self.tokenizer = tokenizer
        # Replace lambda with a proper method for better pickling
        self._feature_names = ["placeholder_feature"]

    def get_feature_names_out(self):
        """Return feature names for compatibility with sklearn API."""
        return self._feature_names

    def transform(self, X):
        """
        Transform text to a format compatible with the existing pipeline.

        This method is a placeholder that returns a matrix-like object with
        the same shape as what would be expected from TfidfVectorizer.

        Args:
            X: Input text data

        Returns:
            A matrix-like object for compatibility
        """
        if isinstance(X, list):
            # For lists of strings, return a matrix of correct shape
            return CustomNumpyArray(np.ones((len(X), 1)))
        else:
            # For single strings
            return CustomNumpyArray(np.ones((1, 1)))

    def fit_transform(self, X, y=None):
        """
        Fit and transform in one step (placeholder for compatibility).

        Args:
            X: Input text data
            y: Target values (ignored)

        Returns:
            Same as transform
        """
        return self.transform(X)