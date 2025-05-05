"""
Semantic Card Payment Enhancer for Purpose Code Classification.

This module provides a specialized enhancer for card payment-related transactions,
using semantic pattern matching to identify card payments with high accuracy.
"""

import logging
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer

logger = logging.getLogger(__name__)

class CardPaymentEnhancerSemantic(SemanticEnhancer):
    """
    Specialized enhancer for card payment-related transactions.

    Uses semantic pattern matching to identify card payments
    with high accuracy and confidence.
    """

    def __init__(self, matcher=None):
        """
        Initialize with optional matcher.

        Args:
            matcher: Optional SemanticPatternMatcher instance to use
        """
        super().__init__(matcher=matcher)

        # Initialize card payment-specific patterns and contexts
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize card payment-specific patterns and contexts."""
        # Direct card payment keywords
        self.direct_keywords = {
            'CCRD': [
                'credit card', 'credit card payment', 'credit card transaction',
                'credit card purchase', 'credit card charge', 'credit card fee',
                'credit card bill', 'credit card statement', 'credit card settlement',
                'credit card repayment', 'credit card balance', 'credit card debt',
                'credit card interest', 'credit card annual fee', 'credit card late fee',
                'credit card over limit fee', 'credit card cash advance fee',
                'credit card foreign transaction fee', 'credit card processing fee',
                'credit card merchant fee', 'credit card acquirer fee',
                'credit card issuer fee', 'credit card network fee',
                'credit card interchange fee', 'credit card assessment fee',
                'visa', 'mastercard', 'amex', 'american express', 'discover',
                'diners club', 'jcb', 'unionpay', 'credit card payment processor',
                'credit card payment gateway', 'credit card payment terminal',
                'credit card payment system', 'credit card payment platform',
                'credit card payment service', 'credit card payment provider',
                'credit card payment solution', 'credit card payment network',
                'credit card payment scheme', 'credit card payment brand',
                'credit card payment association', 'credit card payment company',
                'credit card payment vendor', 'credit card payment supplier'
            ],
            'DCRD': [
                'debit card', 'debit card payment', 'debit card transaction',
                'debit card purchase', 'debit card charge', 'debit card fee',
                'debit card bill', 'debit card statement', 'debit card settlement',
                'debit card repayment', 'debit card balance', 'debit card debt',
                'debit card interest', 'debit card annual fee', 'debit card late fee',
                'debit card over limit fee', 'debit card cash advance fee',
                'debit card foreign transaction fee', 'debit card processing fee',
                'debit card merchant fee', 'debit card acquirer fee',
                'debit card issuer fee', 'debit card network fee',
                'debit card interchange fee', 'debit card assessment fee',
                'visa debit', 'mastercard debit', 'maestro', 'visa electron',
                'debit card payment processor', 'debit card payment gateway',
                'debit card payment terminal', 'debit card payment system',
                'debit card payment platform', 'debit card payment service',
                'debit card payment provider', 'debit card payment solution',
                'debit card payment network', 'debit card payment scheme',
                'debit card payment brand', 'debit card payment association',
                'debit card payment company', 'debit card payment vendor',
                'debit card payment supplier'
            ],
            'ICCP': [
                'irrevocable credit card', 'irrevocable credit card payment',
                'irrevocable credit card transaction', 'irrevocable credit card purchase',
                'irrevocable credit card charge', 'irrevocable credit card fee',
                'irrevocable credit card bill', 'irrevocable credit card statement',
                'irrevocable credit card settlement', 'irrevocable credit card repayment'
            ],
            'IDCP': [
                'irrevocable debit card', 'irrevocable debit card payment',
                'irrevocable debit card transaction', 'irrevocable debit card purchase',
                'irrevocable debit card charge', 'irrevocable debit card fee',
                'irrevocable debit card bill', 'irrevocable debit card statement',
                'irrevocable debit card settlement', 'irrevocable debit card repayment'
            ],
            'CBLK': [
                'card bulk', 'card bulk clearing', 'card bulk settlement',
                'card bulk processing', 'card bulk reconciliation', 'card bulk payment',
                'bulk card', 'bulk card clearing', 'bulk card settlement',
                'bulk card processing', 'bulk card reconciliation', 'bulk card payment'
            ]
        }

        # Semantic context patterns for card payments
        self.context_patterns = [
            # CCRD patterns
            {
                'purpose_code': 'CCRD',
                'keywords': ['credit', 'card'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['credit', 'card', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['credit', 'card', 'transaction'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['credit', 'card', 'purchase'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['credit', 'card', 'charge'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['credit', 'card', 'fee'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['credit', 'card', 'bill'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['credit', 'card', 'statement'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['credit', 'card', 'settlement'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['credit', 'card', 'repayment'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['credit', 'card', 'balance'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['credit', 'card', 'debt'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['credit', 'card', 'interest'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['visa'],
                'proximity': 1,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['mastercard'],
                'proximity': 1,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['amex'],
                'proximity': 1,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['american', 'express'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['discover'],
                'proximity': 1,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['diners', 'club'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['jcb'],
                'proximity': 1,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['unionpay'],
                'proximity': 1,
                'weight': 0.9
            },

            # DCRD patterns
            {
                'purpose_code': 'DCRD',
                'keywords': ['debit', 'card'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['debit', 'card', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['debit', 'card', 'transaction'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['debit', 'card', 'purchase'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['debit', 'card', 'charge'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['debit', 'card', 'fee'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['debit', 'card', 'bill'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['debit', 'card', 'statement'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['debit', 'card', 'settlement'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['visa', 'debit'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['mastercard', 'debit'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['maestro'],
                'proximity': 1,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['visa', 'electron'],
                'proximity': 3,
                'weight': 0.9
            }
        ]

        # Card payment-related terms for semantic similarity
        self.semantic_terms = [
            # CCRD terms
            {'purpose_code': 'CCRD', 'term': 'credit', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'CCRD', 'term': 'card', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'CCRD', 'term': 'visa', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'CCRD', 'term': 'mastercard', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'CCRD', 'term': 'amex', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'CCRD', 'term': 'american', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'CCRD', 'term': 'express', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'CCRD', 'term': 'discover', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'CCRD', 'term': 'diners', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'CCRD', 'term': 'club', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'CCRD', 'term': 'jcb', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'CCRD', 'term': 'unionpay', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'CCRD', 'term': 'payment', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CCRD', 'term': 'transaction', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CCRD', 'term': 'purchase', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CCRD', 'term': 'charge', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CCRD', 'term': 'fee', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CCRD', 'term': 'bill', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CCRD', 'term': 'statement', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CCRD', 'term': 'settlement', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CCRD', 'term': 'repayment', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CCRD', 'term': 'balance', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CCRD', 'term': 'debt', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'CCRD', 'term': 'interest', 'threshold': 0.7, 'weight': 0.8},

            # DCRD terms
            {'purpose_code': 'DCRD', 'term': 'debit', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'DCRD', 'term': 'card', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'DCRD', 'term': 'maestro', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'DCRD', 'term': 'electron', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'DCRD', 'term': 'payment', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'DCRD', 'term': 'transaction', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'DCRD', 'term': 'purchase', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'DCRD', 'term': 'charge', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'DCRD', 'term': 'fee', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'DCRD', 'term': 'bill', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'DCRD', 'term': 'statement', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'DCRD', 'term': 'settlement', 'threshold': 0.7, 'weight': 0.8}
        ]

    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification for card payment-related transactions.

        Args:
            result: Initial classification result
            narration: Transaction narration
            message_type: Optional message type

        Returns:
            dict: Enhanced classification result
        """
        logger.debug(f"Card payment enhancer called with narration: {narration}")

        # First, check for high confidence classifications that should not be overridden
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)

        # Don't override high confidence classifications
        if confidence >= 0.95:
            logger.debug(f"Not overriding high confidence classification: {purpose_code} ({confidence})")
            return result

        # Skip withholding tax cases
        narration_upper = narration.upper()
        if narration_upper == "STATUTORY WITHHOLDING PAYMENT" or narration_upper == "WITHHOLDING ON CONTRACTOR PAYMENT":
            logger.debug(f"Skipping withholding tax case: {narration}")
            return result

        # Skip if narration contains withholding
        narration_lower = narration.lower()
        if 'withholding' in narration_lower:
            logger.debug(f"Skipping withholding tax case: {narration}")
            return result

        # Skip interbank-related payments
        interbank_terms = ['interbank', 'nostro', 'vostro', 'correspondent bank', 'bank to bank',
                          'rtgs', 'real time gross settlement', 'financial institution',
                          'liquidity management', 'reserve requirement']
        if any(term in narration_lower for term in interbank_terms):
            logger.debug(f"Skipping interbank-related payment: {narration}")
            return result

        # Call the base implementation first
        enhanced_result = super().enhance_classification(result, narration, message_type)

        # If the base implementation changed something, return it
        if enhanced_result != result:
            # Ensure category purpose code is set appropriately for card payment codes
            if enhanced_result.get('purpose_code') in ["CCRD", "DCRD"]:
                enhanced_result['category_purpose_code'] = enhanced_result.get('purpose_code')
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "card_payment_category_mapping"
            return enhanced_result

        # Special case for irrevocable credit card
        if 'irrevocable' in narration_lower and 'credit' in narration_lower and 'card' in narration_lower:
            logger.info(f"Irrevocable credit card detected, overriding {purpose_code} with ICCP")
            enhanced_result = self._create_enhanced_result(result, 'ICCP', 0.99, "Irrevocable credit card detected")

            # Ensure category purpose code is set to ICCP for irrevocable credit card
            enhanced_result['category_purpose_code'] = "ICCP"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "card_payment_category_mapping"

            # Set high priority and final override to ensure this takes precedence
            enhanced_result['priority'] = 1000
            enhanced_result['final_override'] = True
            enhanced_result['force_purpose_code'] = True
            enhanced_result['force_category_purpose_code'] = True

            return enhanced_result

        # Special case for irrevocable debit card
        if 'irrevocable' in narration_lower and 'debit' in narration_lower and 'card' in narration_lower:
            logger.info(f"Irrevocable debit card detected, overriding {purpose_code} with IDCP")
            enhanced_result = self._create_enhanced_result(result, 'IDCP', 0.99, "Irrevocable debit card detected")

            # Ensure category purpose code is set to IDCP for irrevocable debit card
            enhanced_result['category_purpose_code'] = "IDCP"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "card_payment_category_mapping"

            # Set high priority and final override to ensure this takes precedence
            enhanced_result['priority'] = 1000
            enhanced_result['final_override'] = True
            enhanced_result['force_purpose_code'] = True
            enhanced_result['force_category_purpose_code'] = True

            return enhanced_result

        # Special case for card bulk clearing
        if ('card bulk' in narration_lower or 'bulk card' in narration_lower) and any(term in narration_lower for term in ['clearing', 'settlement', 'processing', 'reconciliation', 'payment']):
            logger.info(f"Card bulk clearing detected, overriding {purpose_code} with CBLK")
            enhanced_result = self._create_enhanced_result(result, 'CBLK', 0.99, "Card bulk clearing detected")

            # Ensure category purpose code is set to CBLK for card bulk clearing
            enhanced_result['category_purpose_code'] = "CBLK"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "card_payment_category_mapping"

            return enhanced_result

        # Special case for credit card
        if 'credit' in narration_lower and 'card' in narration_lower:
            logger.info(f"Credit card detected, overriding {purpose_code} with CCRD")
            enhanced_result = self._create_enhanced_result(result, 'CCRD', 0.9, "Credit card detected")

            # Ensure category purpose code is set to CCRD for credit card
            enhanced_result['category_purpose_code'] = "CCRD"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "card_payment_category_mapping"

            return enhanced_result

        # Special case for debit card
        if 'debit' in narration_lower and 'card' in narration_lower:
            logger.info(f"Debit card detected, overriding {purpose_code} with DCRD")
            enhanced_result = self._create_enhanced_result(result, 'DCRD', 0.9, "Debit card detected")

            # Ensure category purpose code is set to DCRD for debit card
            enhanced_result['category_purpose_code'] = "DCRD"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "card_payment_category_mapping"

            return enhanced_result

        # Check for card brand names (assume credit card unless explicitly stated as debit)
        card_brands = ['visa', 'mastercard', 'amex', 'american express', 'discover', 'diners club', 'jcb', 'unionpay']
        for brand in card_brands:
            if brand in narration_lower:
                # Check if explicitly debit
                if 'debit' in narration_lower or 'maestro' in narration_lower or 'electron' in narration_lower:
                    logger.info(f"Debit card brand detected: {brand}, overriding {purpose_code} with DCRD")
                    enhanced_result = self._create_enhanced_result(result, 'DCRD', 0.9, f"Debit card brand detected: {brand}")

                    # Ensure category purpose code is set to DCRD for debit card
                    enhanced_result['category_purpose_code'] = "DCRD"
                    enhanced_result['category_confidence'] = 0.99
                    enhanced_result['category_enhancement_applied'] = "card_payment_category_mapping"
                else:
                    logger.info(f"Credit card brand detected: {brand}, overriding {purpose_code} with CCRD")
                    enhanced_result = self._create_enhanced_result(result, 'CCRD', 0.9, f"Credit card brand detected: {brand}")

                    # Ensure category purpose code is set to CCRD for credit card
                    enhanced_result['category_purpose_code'] = "CCRD"
                    enhanced_result['category_confidence'] = 0.99
                    enhanced_result['category_enhancement_applied'] = "card_payment_category_mapping"

                return enhanced_result

        # Check if we should override the current classification
        if self.should_override_classification(result, narration):
            # Determine if credit or debit card
            if 'debit' in narration_lower or 'maestro' in narration_lower or 'electron' in narration_lower:
                logger.info(f"Overriding {purpose_code} with DCRD based on context analysis")
                enhanced_result = self._create_enhanced_result(result, 'DCRD', 0.85, "Context analysis override")

                # Ensure category purpose code is set to DCRD for debit card
                enhanced_result['category_purpose_code'] = "DCRD"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "card_payment_category_mapping"
            else:
                logger.info(f"Overriding {purpose_code} with CCRD based on context analysis")
                enhanced_result = self._create_enhanced_result(result, 'CCRD', 0.85, "Context analysis override")

                # Ensure category purpose code is set to CCRD for credit card
                enhanced_result['category_purpose_code'] = "CCRD"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "card_payment_category_mapping"

            return enhanced_result

        # No card payment pattern detected
        logger.debug("No card payment pattern detected")
        return result

    def should_override_classification(self, result, narration):
        """
        Determine if card payment classification should override existing classification.

        Args:
            result: Current classification result
            narration: Transaction narration

        Returns:
            bool: True if should override
        """
        narration_lower = narration.lower()
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)

        # Skip interbank-related payments
        interbank_terms = ['interbank', 'nostro', 'vostro', 'correspondent bank', 'bank to bank',
                          'rtgs', 'real time gross settlement', 'financial institution',
                          'liquidity management', 'reserve requirement']
        if any(term in narration_lower for term in interbank_terms):
            return False

        # Check for explicit card payment terms
        explicit_card_terms = ['card', 'visa', 'mastercard', 'amex', 'american express',
                              'discover', 'diners club', 'jcb', 'unionpay', 'maestro', 'electron']

        # Only consider 'credit' and 'debit' if they appear with 'card' within 3 words
        has_credit_card = 'credit card' in narration_lower or 'card credit' in narration_lower
        has_debit_card = 'debit card' in narration_lower or 'card debit' in narration_lower

        # Count explicit card terms
        explicit_card_count = sum(1 for term in explicit_card_terms if term in narration_lower)
        if has_credit_card:
            explicit_card_count += 1
        if has_debit_card:
            explicit_card_count += 1

        # If multiple explicit card terms are present, likely card payment-related
        if explicit_card_count >= 2:
            # Don't override if confidence is very high
            if confidence >= 0.9:
                return False

            # Override OTHR or low confidence classifications
            if purpose_code == 'OTHR' or confidence < 0.7:
                return True

            # Override service-related codes with medium confidence
            if purpose_code in ['SCVE', 'SERV', 'SUPP'] and confidence < 0.8:
                return True

        # Don't override other classifications unless very strong evidence
        return False
