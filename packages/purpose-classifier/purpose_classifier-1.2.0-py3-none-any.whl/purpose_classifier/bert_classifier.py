#!/usr/bin/env python
"""
BERT-based Purpose Code Classifier

This module provides a specialized classifier for purpose codes that uses BERT models.
It's designed to work with the enhanced BERT model format and is optimized for SWIFT messages.
"""

import os
import re
import json
import time
import joblib
import logging
import numpy as np
import pandas as pd
import torch
from datetime import datetime
from collections import Counter
from functools import lru_cache
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Set up logging
logger = logging.getLogger(__name__)

class BERTPurposeClassifier:
    """
    BERT-based classifier for ISO20022 purpose codes from SWIFT message narrations.

    This classifier uses a BERT model to predict purpose codes for payment narrations.
    It includes domain-specific enhancers to improve prediction accuracy for various purpose codes.
    """

    def __init__(self, model_path=None, environment='development'):
        """
        Initialize the BERT-based purpose code classifier.

        Args:
            model_path: Path to the BERT model file
            environment: Environment to use ('development', 'test', 'production')
        """
        self.env = environment
        self.model_path = model_path or os.path.join('models', 'combined_model.pkl')

        # Initialize components
        self.model = None
        self.tokenizer = None
        self.label_encoder = None

        # Load purpose codes
        from purpose_classifier.config.settings import PURPOSE_CODES_PATH, CATEGORY_PURPOSE_CODES_PATH
        self.purpose_codes = self._load_purpose_codes(PURPOSE_CODES_PATH)
        self.category_purpose_codes = self._load_purpose_codes(CATEGORY_PURPOSE_CODES_PATH)

        # Message type handlers
        self.message_handlers = {
            'MT103': self._extract_mt103_narration,
            'MT202': self._extract_mt202_narration,
            'MT202COV': self._extract_mt202cov_narration,
            'MT205': self._extract_mt205_narration,
            'MT205COV': self._extract_mt205cov_narration
        }

        # Set up prediction cache
        self.predict_cached = lru_cache(maxsize=2000)(self._predict_impl)
        logger.info(f"Prediction cache enabled with size 2000")

        # Load model if path is provided
        if self.model_path:
            self.load(self.model_path)

    def _load_purpose_codes(self, filepath):
        """Load purpose codes from JSON file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load purpose codes from {filepath}: {str(e)}")
            return {}

    def load(self, model_path=None):
        """
        Load the BERT model from disk.

        Args:
            model_path: Path to the model file

        Returns:
            bool: True if successful, False otherwise
        """
        load_path = model_path or self.model_path

        try:
            logger.info(f"Loading model from {load_path}")
            model_package = joblib.load(load_path)

            # Check if the model package has the expected structure
            if not isinstance(model_package, dict):
                logger.error(f"Invalid model format: expected dictionary, got {type(model_package)}")
                return False

            # Debug print of model package keys
            logger.debug(f"Model package keys: {list(model_package.keys())}")

            # Extract model components
            if 'model' in model_package:
                self.model = model_package['model']
                logger.info("Loaded BERT model")
            else:
                logger.error("Model package does not contain a 'model' key")
                return False

            if 'tokenizer' in model_package:
                self.tokenizer = model_package['tokenizer']
                logger.info("Loaded tokenizer")
            else:
                logger.error("Model package does not contain a 'tokenizer' key")
                return False

            if 'label_encoder' in model_package:
                self.label_encoder = model_package['label_encoder']
                logger.info("Loaded label encoder")
            else:
                logger.error("Model package does not contain a 'label_encoder' key")
                return False

            # Load optional components
            self.created_at = model_package.get('created_at', datetime.now().isoformat())

            logger.info(f"Model loaded successfully from {load_path}")
            return True

        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False

    # SWIFT message narration extraction methods
    def _extract_mt103_narration(self, message):
        """Extract narration from MT103 message"""
        # Look for field 70 (remittance information)
        match = re.search(r':70:([^\n]+)', message, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return message

    def _extract_mt202_narration(self, message):
        """Extract narration from MT202 message"""
        # Look for field 72 (sender to receiver information)
        match = re.search(r':72:([^\n]+)', message, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return message

    def _extract_mt202cov_narration(self, message):
        """Extract narration from MT202COV message"""
        # Look for field 72 (sender to receiver information)
        match = re.search(r':72:([^\n]+)', message, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return message

    def _extract_mt205_narration(self, message):
        """Extract narration from MT205 message"""
        # Look for field 72 (sender to receiver information)
        match = re.search(r':72:([^\n]+)', message, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return message

    def _extract_mt205cov_narration(self, message):
        """Extract narration from MT205COV message"""
        # Look for field 72 (sender to receiver information)
        match = re.search(r':72:([^\n]+)', message, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return message

    def predict(self, narration, message_type=None):
        """
        Predict purpose code for a narration.

        Args:
            narration: Text narration to classify
            message_type: Optional SWIFT message type (MT103, MT202, etc.)

        Returns:
            dict: Prediction result with purpose code, confidence, etc.
        """
        # Store original narration and message type
        original_narration = narration
        original_message_type = message_type

        # Extract narration from SWIFT message if message_type is provided
        if message_type and message_type in self.message_handlers:
            narration = self.message_handlers[message_type](narration)

        # Use cached prediction for better performance
        try:
            # Get the base prediction
            result = self.predict_cached(narration, message_type)

            # Add message type to the result if provided
            if original_message_type:
                result['message_type'] = original_message_type

            return result
        except Exception as e:
            logger.error(f"Error in prediction: {str(e)}")
            # Return default result on error
            return {
                'purpose_code': 'OTHR',
                'confidence': 0.0,
                'category_purpose_code': 'OTHR',
                'category_confidence': 0.0,
                'top_predictions': [('OTHR', 0.0)],
                'processing_time': 0.0,
                'message_type': original_message_type,
                'error': str(e)
            }

    def batch_predict(self, narrations, message_type=None, message_types=None):
        """
        Predict purpose codes for multiple narrations.

        Args:
            narrations: List of text narrations to classify
            message_type: Optional SWIFT message type (MT103, MT202, etc.) for all narrations
            message_types: Optional list of SWIFT message types, one for each narration

        Returns:
            list: List of prediction results
        """
        logger.info(f"Processing batch of {len(narrations)} items")
        results = []

        for i, narration in enumerate(narrations):
            try:
                # Use message_types[i] if provided, otherwise use message_type
                current_message_type = message_types[i] if message_types and i < len(message_types) else message_type
                result = self.predict(narration, current_message_type)
                results.append(result)
            except Exception as e:
                logger.error(f"Error in batch prediction: {str(e)}")
                # Add default result on error
                results.append({
                    'purpose_code': 'OTHR',
                    'confidence': 0.0,
                    'category_purpose_code': 'OTHR',
                    'category_confidence': 0.0,
                    'top_predictions': [('OTHR', 0.0)],
                    'processing_time': 0.0,
                    'error': str(e)
                })

        return results

    def _predict_impl(self, narration, message_type=None):
        """
        Implementation of prediction logic.

        Args:
            narration: Text narration to classify
            message_type: Optional SWIFT message type (MT103, MT202, etc.)

        Returns:
            dict: Prediction result with purpose code, confidence, etc.
        """
        start_time = time.time()

        # Check if model is loaded
        if not self.model or not self.tokenizer or not self.label_encoder:
            raise RuntimeError("Model not trained or loaded")

        # Preprocess text for BERT
        # BERT requires special tokens and padding
        inputs = self.tokenizer(narration,
                               return_tensors="pt",
                               truncation=True,
                               padding=True,
                               max_length=128)

        # Get model predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits

        # Convert logits to probabilities
        probs = torch.nn.functional.softmax(logits, dim=-1).squeeze().numpy()

        # Get the predicted class index and confidence
        purpose_idx = np.argmax(probs)
        purpose_code = self.label_encoder.inverse_transform([purpose_idx])[0]
        confidence = probs[purpose_idx]

        # Get top-5 predictions for more robust decision making
        top_indices = probs.argsort()[-5:][::-1]
        top_codes = [self.label_encoder.inverse_transform([i])[0] for i in top_indices]
        top_probs = [probs[i] for i in top_indices]

        # Create top predictions list
        top_predictions = list(zip(top_codes, top_probs))

        # Determine category purpose code
        category_purpose_code, category_confidence = self._determine_category_purpose(
            purpose_code, narration, message_type
        )

        # Create result dictionary
        result = {
            'purpose_code': purpose_code,
            'confidence': confidence,
            'category_purpose_code': category_purpose_code,
            'category_confidence': category_confidence,
            'top_predictions': top_predictions,
            'processing_time': time.time() - start_time
        }

        return result

    def _determine_category_purpose(self, purpose_code, narration, message_type=None):
        """
        Determine category purpose code based on purpose code.

        This method uses a direct mapping from purpose codes to category purpose codes.

        Args:
            purpose_code: The purpose code
            narration: Not used for mapping
            message_type: Not used for mapping

        Returns:
            tuple: (category_purpose_code, confidence)
        """
        # Direct mapping from purpose codes to category purpose codes
        purpose_to_category_map = {
            # Property and real estate
            'PPTI': 'PPTI',  # Property Purchase

            # Card payments
            'CCRD': 'CCRD',  # Credit Card Payment
            'DCRD': 'DCRD',  # Debit Card Payment
            'ICCP': 'ICCP',  # Irrevocable Credit Card Payment
            'IDCP': 'IDCP',  # Irrevocable Debit Card Payment
            'CBLK': 'CBLK',  # Card Bulk Clearing

            # Salary and compensation
            'SALA': 'SALA',  # Salary Payment
            'BONU': 'SALA',  # Bonus Payment
            'COMM': 'SALA',  # Commission Payment
            'PENS': 'PENS',  # Pension Payment

            # Taxes
            'TAXS': 'TAXS',  # Tax Payment
            'VATX': 'TAXS',  # Value Added Tax Payment
            'WHLD': 'TAXS',  # Withholding Tax Payment

            # Utilities
            'ELEC': 'UBIL',  # Electricity Bill Payment
            'WTER': 'UBIL',  # Water Bill Payment
            'GASB': 'UBIL',  # Gas Bill Payment
            'CBTV': 'UBIL',  # Cable TV Bill Payment
            'TLCM': 'UBIL',  # Telecommunications Bill Payment
            'NWCH': 'UBIL',  # Network Charge
            'OTLC': 'UBIL',  # Other Telecom Related Bill Payment

            # Loans and investments
            'LOAN': 'LOAN',  # Loan
            'LOAR': 'LOAN',  # Loan Repayment
            'MDCR': 'LOAN',  # Medical Care
            'RENT': 'RENT',  # Rent
            'INSU': 'INSU',  # Insurance Premium
            'INPC': 'INSU',  # Insurance Policy Claim
            'INVS': 'INVS',  # Investment & Securities
            'SECU': 'SECU',  # Securities
            'DIVI': 'DIVI',  # Dividend
            'DIVD': 'DIVI',  # Dividend Payment
            'INTE': 'INTE',  # Interest

            # Trade and business
            'SUPP': 'SUPP',  # Supplier Payment
            'TRAD': 'TRAD',  # Trade
            'CORT': 'CORT',  # Trade Settlement
            'SCVE': 'SCVE',  # Purchase of Services
            'SERV': 'SERV',  # Service
            'FREX': 'FREX',  # Foreign Exchange
            'HEDG': 'HEDG',  # Hedging

            # Education
            'EDUC': 'FCOL',  # Education

            # Government
            'GOVT': 'GOVT',  # Government Payment
            'GOVI': 'GOVI',  # Government Insurance
            'GSCB': 'GSCB',  # Purchase/Sale Of Goods & Services With Government
            'GDDS': 'GDDS',  # Purchase/Sale Of Goods

            # Interbank and treasury
            'INTC': 'INTC',  # Intra Company Payment
            'TREA': 'TREA',  # Treasury Payment
            'CASH': 'CASH',  # Cash Management
            'XBCT': 'XBCT',  # Cross-Border Credit Transfer

            # Other
            'OTHR': 'OTHR',  # Other
        }

        # Get the category purpose code from the mapping
        category_purpose_code = purpose_to_category_map.get(purpose_code, purpose_code)

        # Return the category purpose code with high confidence
        return category_purpose_code, 0.99
