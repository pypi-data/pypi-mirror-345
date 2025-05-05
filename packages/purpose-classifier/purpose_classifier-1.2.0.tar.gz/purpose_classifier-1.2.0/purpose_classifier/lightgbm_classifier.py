#!/usr/bin/env python
"""
LightGBM-based Purpose Code Classifier

This module provides a specialized classifier for purpose codes that uses LightGBM models.
It's designed to work with the enhanced LightGBM model format and is optimized for SWIFT messages.
"""

import os
import re
import json
import time
import joblib
import logging
import numpy as np
import pandas as pd
import types
import textwrap
import warnings
from datetime import datetime
from collections import Counter
from functools import lru_cache
from sklearn.feature_extraction.text import TfidfVectorizer

# Suppress specific sklearn warnings about feature names
warnings.filterwarnings("ignore", message="X does not have valid feature names, but LGBMClassifier was fitted with feature names")

# Import from purpose_classifier package
from purpose_classifier.config.settings import (
    MODEL_PATH, PURPOSE_CODES_PATH, CATEGORY_PURPOSE_CODES_PATH
)
from purpose_classifier.utils.preprocessor import TextPreprocessor
from purpose_classifier.domain_enhancers import TechDomainEnhancer
from purpose_classifier.domain_enhancers import EducationDomainEnhancer
from purpose_classifier.domain_enhancers import ServicesDomainEnhancer
from purpose_classifier.domain_enhancers import TradeDomainEnhancer
from purpose_classifier.classifier import InterbankDomainEnhancer
from purpose_classifier.domain_enhancers import CategoryPurposeDomainEnhancer as CategoryPurposeEnhancer
from purpose_classifier.domain_enhancers import TransportationDomainEnhancer
from purpose_classifier.domain_enhancers import FinancialServicesDomainEnhancer
from purpose_classifier.domain_enhancers.software_services_enhancer_semantic import SoftwareServicesEnhancer
from purpose_classifier.domain_enhancers.message_type_enhancer_semantic import MessageTypeEnhancerSemantic as MessageTypeEnhancer

# Set up logging
logger = logging.getLogger(__name__)

class LightGBMPurposeClassifier:
    """
    LightGBM-based classifier for ISO20022 purpose codes from SWIFT message narrations.

    This classifier uses a LightGBM model to predict purpose codes for payment narrations.
    It includes domain-specific enhancers to improve prediction accuracy for various purpose codes:

    Supported Purpose Codes:
    - GDDS: Purchase Sale of Goods (e.g., equipment, furniture, merchandise)
    - SCVE: Purchase of Services (e.g., consulting, professional services, tech services)
    - EDUC: Education (e.g., tuition, school fees, academic payments)
    - TRAD: Trade Services (e.g., wholesale, retail, import/export)
    - INTC: Intra Company Payment (e.g., intercompany transfers, treasury operations)
    - INSU: Insurance Premium (e.g., policy payments, insurance coverage)
    - LOAN: Loan (e.g., mortgage payments, credit facilities)
    - DIVD: Dividend Payment (e.g., shareholder distributions)
    - SALA: Salary Payment (e.g., wages, payroll, compensation)
    - TAXS: Tax Payment (e.g., VAT, duties, levies)
    - BONU: Bonus Payment (e.g., performance bonuses, commissions)

    Supported Category Purpose Codes:
    - SUPP: Supplier Payment (for GDDS and SCVE)
    - SALA: Salary Payment
    - DIVD: Dividend Payment
    - LOAN: Loan
    - INSU: Insurance Premium
    - INTC: Intra-Company Payment
    - TRAD: Trade Services
    - TAXS: Tax Payment
    - BONU: Bonus Payment

    The classifier uses a combination of machine learning and rule-based enhancements
    to achieve high accuracy across different SWIFT message types (MT103, MT202, MT202COV, MT205, MT205COV).
    """

    def __init__(self, model_path=None, environment='development', thread_limit=None):
        """
        Initialize the LightGBM-based purpose code classifier.

        Args:
            model_path: Path to the LightGBM model file
            environment: Environment to use ('development', 'test', 'production')
            thread_limit: Limit the number of threads used by LightGBM
        """
        self.env = environment
        self.model_path = model_path or os.path.join('models', 'combined_model.pkl')
        self.thread_limit = thread_limit

        # Set thread limit if specified
        if thread_limit is not None:
            # os is already imported at the top of the file
            os.environ['OMP_NUM_THREADS'] = str(thread_limit)
            os.environ['OPENBLAS_NUM_THREADS'] = str(thread_limit)
            os.environ['MKL_NUM_THREADS'] = str(thread_limit)
            os.environ['VECLIB_MAXIMUM_THREADS'] = str(thread_limit)
            os.environ['NUMEXPR_NUM_THREADS'] = str(thread_limit)
            logger.info(f"Thread limit set to {thread_limit}")

        # Initialize components
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.feature_names = None
        self.preprocessor = TextPreprocessor()

        # Load purpose codes
        self.purpose_codes = self._load_purpose_codes(PURPOSE_CODES_PATH)
        self.category_purpose_codes = self._load_purpose_codes(CATEGORY_PURPOSE_CODES_PATH)

        # Initialize domain enhancers
        self.tech_enhancer = TechDomainEnhancer()
        self.education_enhancer = EducationDomainEnhancer()
        self.services_enhancer = ServicesDomainEnhancer()
        self.trade_enhancer = TradeDomainEnhancer()
        self.interbank_enhancer = InterbankDomainEnhancer()
        self.category_purpose_enhancer = CategoryPurposeEnhancer()
        self.transportation_enhancer = TransportationDomainEnhancer()
        self.financial_services_enhancer = FinancialServicesDomainEnhancer()
        self.software_services_enhancer = SoftwareServicesEnhancer()
        self.message_type_enhancer = MessageTypeEnhancer()

        # Initialize the Cover Payment Enhancer
        from purpose_classifier.domain_enhancers import CoverPaymentEnhancer
        self.cover_payment_enhancer = CoverPaymentEnhancer()

        # Initialize the Card Payment Enhancer
        from purpose_classifier.domain_enhancers import CardPaymentEnhancer
        self.card_payment_enhancer = CardPaymentEnhancer()

        # Initialize the Court Payment Enhancer
        from purpose_classifier.domain_enhancers import CourtPaymentEnhancer
        self.court_payment_enhancer = CourtPaymentEnhancer()

        # Initialize the Cross-Border Payment Enhancer
        from purpose_classifier.domain_enhancers import CrossBorderEnhancer
        self.cross_border_enhancer = CrossBorderEnhancer()

        # Initialize the Pattern Enhancer
        from purpose_classifier.domain_enhancers.pattern_enhancer_semantic import PatternEnhancerSemantic as PatternEnhancer
        self.pattern_enhancer = PatternEnhancer()

        # Initialize the Property Purchase Enhancer
        from purpose_classifier.domain_enhancers.property_purchase_enhancer_semantic import PropertyPurchaseEnhancerSemantic as PropertyPurchaseEnhancer
        self.property_purchase_enhancer = PropertyPurchaseEnhancer()

        # Initialize the Enhancer Manager
        from purpose_classifier.domain_enhancers.enhancer_manager import EnhancerManager
        from purpose_classifier.domain_enhancers.enhanced_manager import EnhancedManager

        # Initialize the SemanticPatternMatcher for word embeddings
        from purpose_classifier.semantic_pattern_matcher import SemanticPatternMatcher
        embeddings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models', 'word_embeddings.pkl')
        self.matcher = SemanticPatternMatcher(embeddings_path)

        # Log whether word embeddings were loaded
        if hasattr(self.matcher, 'embeddings') and self.matcher.embeddings:
            logger.info(f"Word embeddings loaded successfully with {len(self.matcher.embeddings.key_to_index) if hasattr(self.matcher.embeddings, 'key_to_index') else 'unknown'} words")
        else:
            logger.warning("Word embeddings not loaded")

        # Use the enhanced manager by default, but allow fallback to regular manager
        try:
            self.enhancer_manager = EnhancedManager(matcher=self.matcher)
            logger.info("Using Enhanced Manager for purpose code classification")
        except Exception as e:
            logger.warning(f"Failed to initialize Enhanced Manager: {str(e)}. Falling back to regular EnhancerManager.")
            self.enhancer_manager = EnhancerManager(matcher=self.matcher)

        # Initialize the Adaptive Confidence Calibrator
        from purpose_classifier.domain_enhancers.adaptive_confidence import AdaptiveConfidenceCalibrator
        self.confidence_calibrator = AdaptiveConfidenceCalibrator()

        # Message type handlers
        self.message_handlers = {
            'MT103': self._extract_mt103_narration,
            'MT202': self._extract_mt202_narration,
            'MT202COV': self._extract_mt202cov_narration,
            'MT205': self._extract_mt205_narration,
            'MT205COV': self._extract_mt205cov_narration
        }

        # Set up prediction cache with increased size for better performance
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
        Load the LightGBM model from disk.

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

            # Extract model components based on the enhanced LightGBM model format
            if 'model' in model_package:
                self.model = model_package['model']
                logger.info("Loaded LightGBM model")
            else:
                logger.error("Model package does not contain a 'model' key")
                return False

            if 'vectorizer' in model_package:
                self.vectorizer = model_package['vectorizer']
                logger.info("Loaded vectorizer")
            else:
                logger.error("Model package does not contain a 'vectorizer' key")
                return False

            if 'label_encoder' in model_package:
                self.label_encoder = model_package['label_encoder']
                logger.info("Loaded label encoder")
            else:
                logger.error("Model package does not contain a 'label_encoder' key")
                return False

            # Load optional components
            self.feature_names = model_package.get('feature_names', None)
            self.params = model_package.get('params', {})
            self.created_at = model_package.get('created_at', datetime.now().isoformat())

            # Load fallback rules if available
            self.fallback_rules = model_package.get('fallback_rules', None)

            # Load enhanced prediction function if available
            if 'enhanced_predict' in model_package:
                self.enhanced_predict_code = model_package['enhanced_predict']
                # Create a local namespace to execute the code
                local_namespace = {}
                # Execute the code in the local namespace
                exec(self.enhanced_predict_code, globals(), local_namespace)
                # Get the function from the local namespace
                if 'enhanced_predict' in local_namespace:
                    # Bind the method to this instance
                    self.enhanced_predict_impl = types.MethodType(local_namespace['enhanced_predict'], self)
                else:
                    self.enhanced_predict_impl = None
                    logger.warning("Failed to load enhanced_predict function")
            else:
                self.enhanced_predict_impl = None

            # Load enhanced category purpose function if available
            if 'enhanced_category_purpose' in model_package:
                self.enhanced_category_purpose_code = model_package['enhanced_category_purpose']
                # Create a local namespace to execute the code
                local_namespace = {}
                # Execute the code in the local namespace
                exec(self.enhanced_category_purpose_code, globals(), local_namespace)
                # Get the function from the local namespace
                if 'enhanced_category_purpose' in local_namespace:
                    # Bind the method to this instance
                    self.enhanced_category_purpose_impl = types.MethodType(local_namespace['enhanced_category_purpose'], self)
                else:
                    self.enhanced_category_purpose_impl = None
                    logger.warning("Failed to load enhanced_category_purpose function")
            else:
                self.enhanced_category_purpose_impl = None

            logger.info(f"Model loaded successfully from {load_path}")
            return True

        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False

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

            # Apply confidence calibration if available
            if hasattr(self, 'confidence_calibrator'):
                result = self.confidence_calibrator.calibrate_confidence(result)

            # No exact matches - rely solely on semantic pattern matching
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
        if not self.model or not self.vectorizer or not self.label_encoder:
            raise RuntimeError("Model not trained or loaded")

        # Fast path for common education-related narrations
        narration_lower = narration.lower()
        if ('tuition fee' in narration_lower or 'school fee' in narration_lower or
            'education expenses' in narration_lower or 'university payment' in narration_lower or
            'college payment' in narration_lower):
            # This is definitely an education payment
            return {
                'purpose_code': 'EDUC',
                'confidence': 0.99,
                'category_purpose_code': 'FCOL',
                'category_confidence': 0.99,
                'top_predictions': [('EDUC', 0.99), ('SCVE', 0.05), ('SERV', 0.03)],
                'processing_time': time.time() - start_time,
                'fast_path': 'education'
            }

        # Fast path for common salary-related narrations
        if ('salary payment' in narration_lower or 'monthly payroll' in narration_lower or
            'employee compensation' in narration_lower or 'staff salary' in narration_lower):
            # This is definitely a salary payment
            return {
                'purpose_code': 'SALA',
                'confidence': 0.99,
                'category_purpose_code': 'SALA',
                'category_confidence': 0.99,
                'top_predictions': [('SALA', 0.99), ('PAYR', 0.05), ('COMP', 0.03)],
                'processing_time': time.time() - start_time,
                'fast_path': 'salary'
            }

        # Preprocess text
        processed_text = self.preprocessor.preprocess(narration)

        # Transform using vectorizer
        features = self.vectorizer.transform([processed_text])

        # Suppress the feature names warning by converting to dense array
        # This removes the feature names information which causes the warning
        features_array = features.toarray()

        # For LightGBM models, we need to handle prediction differently
        # LightGBM Booster doesn't have predict_proba, so we use predict with raw_score=True
        try:
            # Get raw scores for each class - use the dense array to avoid feature names warning
            raw_scores = self.model.predict(features_array, raw_score=True)

            # Convert raw scores to probabilities using softmax
            exp_scores = np.exp(raw_scores - np.max(raw_scores, axis=1, keepdims=True))
            purpose_probs = exp_scores / np.sum(exp_scores, axis=1, keepdims=True)

            # If the model returns a 2D array (multiple samples), take the first one
            if purpose_probs.ndim > 1:
                purpose_probs = purpose_probs[0]

            # Get the predicted class index and confidence
            purpose_idx = np.argmax(purpose_probs)
            purpose_code = self.label_encoder.inverse_transform([purpose_idx])[0]
            confidence = purpose_probs[purpose_idx]

            # Get top-5 predictions for more robust decision making and better diversity
            top_indices = purpose_probs.argsort()[-5:][::-1]
            top_codes = [self.label_encoder.inverse_transform([i])[0] for i in top_indices]
            top_probs = [purpose_probs[i] for i in top_indices]

            # Apply confidence calibration to avoid overconfidence
            # Use a sigmoid-like function to compress very high confidences
            calibrated_probs = []
            for prob in top_probs:
                if prob > 0.8:
                    # Apply a softer curve for high confidences to avoid overconfidence
                    calibrated_prob = 0.8 + (prob - 0.8) * 0.5
                elif prob > 0.6:
                    # Slight reduction in mid-high range
                    calibrated_prob = 0.6 + (prob - 0.6) * 0.8
                else:
                    # Keep lower confidences as they are
                    calibrated_prob = prob
                calibrated_probs.append(calibrated_prob)

            # Ensure the confidence gap between top predictions isn't too large
            # This improves the diversity of top predictions
            if len(calibrated_probs) >= 2:
                top_confidence = calibrated_probs[0]
                second_confidence = calibrated_probs[1]

                # If the gap is too large, reduce it
                if top_confidence > 0.7 and second_confidence < 0.1:
                    # Boost the second prediction's confidence
                    adjusted_second_confidence = min(0.2, second_confidence * 3)
                    calibrated_probs[1] = adjusted_second_confidence

                    # Also boost the third prediction if it exists
                    if len(calibrated_probs) >= 3:
                        third_confidence = calibrated_probs[2]
                        if third_confidence < 0.05:
                            adjusted_third_confidence = min(0.1, third_confidence * 3)
                            calibrated_probs[2] = adjusted_third_confidence

            # Create the top predictions list with calibrated confidences
            top_predictions = list(zip(top_codes, calibrated_probs))

            # Update the confidence with the calibrated value
            confidence = calibrated_probs[0]
        except Exception as e:
            # If there's an error with the LightGBM prediction, try a simpler approach
            logger.warning(f"Error using LightGBM prediction with raw scores: {str(e)}")

            # Use simple predict to get class index
            try:
                # Get predicted class index - use the dense array to avoid feature names warning
                pred_class = self.model.predict(features_array)
                if isinstance(pred_class, np.ndarray) and pred_class.ndim > 0:
                    pred_class = pred_class[0]

                # Convert to integer if it's a float
                if isinstance(pred_class, (np.floating, float)):
                    pred_class = int(pred_class)

                # Get the purpose code
                purpose_code = self.label_encoder.inverse_transform([pred_class])[0]
                confidence = 0.8  # Default confidence

                # Set default top predictions
                top_predictions = [(purpose_code, confidence)]
            except Exception as e2:
                logger.error(f"Error in fallback prediction: {str(e2)}")
                purpose_code = 'OTHR'
                confidence = 0.0
                top_predictions = [('OTHR', 0.0)]

        # Apply domain-specific enhancements
        enhanced_result = self._enhance_prediction(purpose_code, confidence, narration, top_predictions, message_type)

        # Determine category purpose code
        category_purpose_code, category_confidence = self._determine_category_purpose(
            enhanced_result['purpose_code'], narration, message_type
        )

        # Create result dictionary
        result = {
            'purpose_code': enhanced_result['purpose_code'],
            'confidence': enhanced_result['confidence'],
            'category_purpose_code': category_purpose_code,
            'category_confidence': category_confidence,
            'top_predictions': top_predictions,
            'processing_time': time.time() - start_time
        }

        # Copy enhancement-related fields from enhanced_result
        enhancement_fields = [
            'enhanced', 'enhancement_applied', 'enhancement_type', 'enhancer',
            'reason', 'original_purpose_code', 'enhancer_decisions'
        ]

        for field in enhancement_fields:
            if field in enhanced_result:
                result[field] = enhanced_result[field]

        return result

    def _enhance_prediction(self, purpose_code, confidence, narration, top_predictions, message_type=None):
        """
        Enhance prediction using domain-specific knowledge and fallback rules.

        Args:
            purpose_code: The predicted purpose code
            confidence: The confidence score of the prediction
            narration: The narration text
            top_predictions: List of top predictions with confidence scores
            message_type: Optional SWIFT message type (MT103, MT202, etc.)
        """
        # Create initial result dictionary
        result = {
            'purpose_code': purpose_code,
            'confidence': confidence,
            'top_predictions': top_predictions
        }

        # Add message type to result if provided
        if message_type:
            result['message_type'] = message_type

        # Use the enhancer manager if available
        if hasattr(self, 'enhancer_manager'):
            logger.debug(f"Using enhancer manager with narration: {narration}")
            result = self.enhancer_manager.enhance(result, narration, message_type)
            logger.debug(f"Enhancer manager result: {result}")

            # If enhanced by the enhancer manager, return early
            if result.get('enhanced', False):
                logger.debug(f"Enhancer manager enhanced the result: {result}")
                return result

        # Fallback to individual enhancers if enhancer manager is not available or didn't enhance
        # Apply pattern enhancer first (highest priority)
        if hasattr(self, 'pattern_enhancer'):
            logger.debug(f"Calling pattern_enhancer with narration: {narration}")
            result = self.pattern_enhancer.enhance_classification(result, narration, message_type)
            logger.debug(f"Pattern enhancer result: {result}")

            # Log if we're forcing a category purpose code
            if result.get('force_category_purpose_code', False):
                logger.debug(f"Forced {result.get('category_purpose_code')} category purpose code for {result.get('purpose_code')} purpose code")

            # If enhanced, return early
            if result.get('enhanced', False):
                logger.debug(f"Pattern enhancer enhanced the result: {result}")
                return result

        # Apply message type enhancer next, but only if pattern_enhancer didn't force a category purpose code
        if hasattr(self, 'message_type_enhancer') and message_type and not result.get('force_category_purpose_code', False):
            # Log the message type for debugging
            logger.debug(f"Applying message type enhancer with message type: {message_type}")

            # Apply the message type enhancer
            result = self.message_type_enhancer.enhance_classification(result, narration, message_type)

            # No exact matches - rely solely on semantic pattern matching

            # Always return the enhanced result to ensure category purpose codes are applied
            logger.debug(f"Returning result from message type enhancer with purpose: {result.get('purpose_code')}, category: {result.get('category_purpose_code')}")
            return result

        # Apply cover payment enhancer for MT202COV and MT205COV messages
        if hasattr(self, 'cover_payment_enhancer') and message_type in ['MT202COV', 'MT205COV']:
            # Apply the cover payment enhancer
            result = self.cover_payment_enhancer.enhance_classification(result, narration, message_type)
            # If enhanced, return early
            if result.get('enhanced', False):
                logger.debug(f"Enhanced with cover payment enhancer: {result.get('purpose_code')}, confidence: {result.get('confidence')}")
                return result

        # Apply interbank enhancer with message type context
        if hasattr(self, 'interbank_enhancer'):
            # No exact matches - rely solely on semantic pattern matching

            # Special case for cash management in MT205
            if message_type in ['MT205', 'MT205COV'] and 'cash management' in narration.lower():
                result['purpose_code'] = 'CASH'
                result['confidence'] = 0.98
                result['enhancement_applied'] = 'cash_management_override'
                result['category_purpose_code'] = 'CASH'
                result['category_confidence'] = 0.98
                return result

            # Apply the interbank enhancer
            result = self.interbank_enhancer.enhance_classification(result, narration, message_type)
            # If enhanced with high confidence, return early
            if result.get('enhancement_applied') in [
                'interbank_domain_override', 'interbank_message_type_override', 'message_type_context_override',
                'forex_settlement_override', 'currency_pair_override', 'treasury_message_type_override'
            ]:
                return result



        # Apply new enhancers next (high priority)
        # Cross-border enhancer - always apply regardless of confidence
        if hasattr(self, 'cross_border_enhancer'):
            result = self.cross_border_enhancer.enhance_classification(result, narration, message_type)
            # If enhanced, return early
            if result.get('enhanced', False):
                return result

        # Court payment enhancer - always apply regardless of confidence
        if hasattr(self, 'court_payment_enhancer'):
            result = self.court_payment_enhancer.enhance_classification(result, narration, message_type)
            # If enhanced, return early
            if result.get('enhanced', False):
                return result

        # Card payment enhancer - always apply regardless of confidence
        if hasattr(self, 'card_payment_enhancer'):
            result = self.card_payment_enhancer.enhance_classification(result, narration, message_type)
            # If enhanced, return early
            if result.get('enhanced', False):
                return result

        # Tax enhancer - always apply regardless of confidence
        if hasattr(self, 'tax_enhancer'):
            result = self.tax_enhancer.enhance_classification(result, narration)
            # If enhanced, return early
            if result.get('enhanced', False) and result.get('enhancement_type') == 'tax':
                return result

        # Treasury enhancer - always apply regardless of confidence
        if hasattr(self, 'treasury_enhancer'):
            result = self.treasury_enhancer.enhance_classification(result, narration, message_type)
            # If enhanced, return early
            if result.get('enhanced', False) and result.get('enhancement_type') == 'treasury':
                return result

        # Software services enhancer - always apply regardless of confidence
        if hasattr(self, 'software_services_enhancer'):
            result = self.software_services_enhancer.enhance_classification(result, narration)
            # If enhanced, return early
            if result.get('enhanced', False) and result.get('enhancement_type') == 'software_services':
                return result

        # Special case for office supplies
        narration_lower = narration.lower()
        if 'office supplies' in narration_lower or 'office stationery' in narration_lower or 'office equipment' in narration_lower:
            result['purpose_code'] = 'GDDS'
            result['confidence'] = 0.99
            result['category_purpose_code'] = 'GDDS'
            result['category_confidence'] = 0.99
            result['enhanced'] = True
            result['enhancement_type'] = 'office_supplies'
            return result

        # Special case for marketing expenses
        if 'marketing expenses' in narration_lower or 'marketing costs' in narration_lower:
            result['purpose_code'] = 'SCVE'
            result['confidence'] = 0.99
            result['category_purpose_code'] = 'SUPP'
            result['category_confidence'] = 0.99
            result['enhanced'] = True
            result['enhancement_type'] = 'marketing_expenses'
            return result

        # Special case for dividend payments
        if 'dividend' in narration_lower and ('payment' in narration_lower or 'distribution' in narration_lower):
            result['purpose_code'] = 'DIVD'
            result['confidence'] = 0.99
            result['category_purpose_code'] = 'DIVI'
            result['category_confidence'] = 0.99
            result['enhanced'] = True
            result['enhancement_type'] = 'dividend'
            return result

        # Special case for government benefit
        if ('government benefit' in narration_lower or 'state benefit' in narration_lower) and 'payment' in narration_lower:
            result['purpose_code'] = 'GBEN'
            result['confidence'] = 0.99
            result['category_purpose_code'] = 'GOVT'
            result['category_confidence'] = 0.99
            result['enhanced'] = True
            result['enhancement_type'] = 'government_benefit'
            return result

        # Check if we have enhanced prediction implementation from the model
        if hasattr(self, 'enhanced_predict_impl') and self.enhanced_predict_impl and self.fallback_rules:
            # Apply the enhanced prediction function
            enhanced_result = self.enhanced_predict_impl(narration, confidence, top_predictions, self.fallback_rules)
            if enhanced_result:
                return enhanced_result

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
            'VATX': 'VATX',  # Value Added Tax Payment (direct mapping)
            'WHLD': 'WHLD',  # Withholding Tax Payment (direct mapping)

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
            'SCVE': 'SUPP',  # Purchase of Services (maps to Supplier Payment)
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
