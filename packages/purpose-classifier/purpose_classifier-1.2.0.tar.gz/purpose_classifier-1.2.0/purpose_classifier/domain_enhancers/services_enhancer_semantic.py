"""
Semantic Services Enhancer for Purpose Code Classification.

This module provides a specialized enhancer for service-related transactions,
using semantic pattern matching to identify service payments with high accuracy.
"""

import logging
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer

logger = logging.getLogger(__name__)

class ServicesEnhancerSemantic(SemanticEnhancer):
    """
    Specialized enhancer for service-related transactions.

    Uses semantic pattern matching to identify service payments
    with high accuracy and confidence.
    """

    def __init__(self, matcher=None):
        """
        Initialize with optional matcher.

        Args:
            matcher: Optional SemanticPatternMatcher instance to use
        """
        super().__init__(matcher=matcher)

        # Initialize services-specific patterns and contexts
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize services-specific patterns and contexts."""
        # Direct services keywords
        self.direct_keywords = {
            'SCVE': [
                'service fee', 'professional services', 'consulting services',
                'service payment', 'payment for services', 'consulting fee',
                'professional fee', 'service charge', 'maintenance service',
                'repair service', 'installation service', 'support service',
                'subscription service', 'service contract', 'service agreement',
                'service provider', 'service vendor', 'service supplier',
                'service invoice', 'service bill', 'service receipt'
            ]
        }

        # Semantic context patterns for services
        self.context_patterns = [
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'fee'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['professional', 'services'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['consulting', 'services'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['payment', 'services'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['payment', 'consulting'],
                'proximity': 5,
                'weight': 0.95
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['consulting', 'fee'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['professional', 'fee'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'charge'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['maintenance', 'service'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['repair', 'service'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['installation', 'service'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['support', 'service'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['subscription', 'service'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'contract'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'agreement'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'provider'],
                'proximity': 3,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'vendor'],
                'proximity': 3,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'supplier'],
                'proximity': 3,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'invoice'],
                'proximity': 3,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'bill'],
                'proximity': 3,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'receipt'],
                'proximity': 3,
                'weight': 0.8
            }
        ]

        # Services-related terms for semantic similarity
        self.semantic_terms = [
            {'purpose_code': 'SCVE', 'term': 'service', 'threshold': 0.7, 'weight': 1.0},
            {'purpose_code': 'SCVE', 'term': 'professional', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'SCVE', 'term': 'consulting', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'SCVE', 'term': 'maintenance', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'SCVE', 'term': 'repair', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'SCVE', 'term': 'installation', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'SCVE', 'term': 'support', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'SCVE', 'term': 'subscription', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'SCVE', 'term': 'contract', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'SCVE', 'term': 'agreement', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'SCVE', 'term': 'provider', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'SCVE', 'term': 'vendor', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'SCVE', 'term': 'supplier', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'SCVE', 'term': 'invoice', 'threshold': 0.7, 'weight': 0.7},
            {'purpose_code': 'SCVE', 'term': 'bill', 'threshold': 0.7, 'weight': 0.7},
            {'purpose_code': 'SCVE', 'term': 'receipt', 'threshold': 0.7, 'weight': 0.7},
            {'purpose_code': 'SCVE', 'term': 'fee', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'SCVE', 'term': 'charge', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'SCVE', 'term': 'payment', 'threshold': 0.7, 'weight': 0.7},
            {'purpose_code': 'SCVE', 'term': 'consultant', 'threshold': 0.7, 'weight': 0.9}
        ]

        # Negative indicators (not services)
        self.negative_indicators = [
            'goods', 'merchandise', 'product', 'equipment', 'hardware',
            'supplies', 'inventory', 'stock', 'purchase', 'loan', 'mortgage',
            'interest', 'dividend', 'investment', 'securities', 'trading',
            'forex', 'fx', 'foreign exchange', 'treasury', 'interbank',
            'nostro', 'vostro', 'correspondent', 'utility', 'electricity',
            'gas', 'water', 'phone', 'telephone', 'mobile', 'internet',
            'broadband', 'cable', 'tv', 'television', 'tax', 'vat', 'gst',
            'sales tax', 'income tax', 'property tax', 'withholding tax',
            'customs', 'duty', 'tariff', 'salary', 'wage', 'payroll',
            'compensation', 'bonus', 'commission', 'pension', 'retirement',
            'benefit'
        ]

    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification for service-related transactions.

        Args:
            result: Initial classification result
            narration: Transaction narration
            message_type: Optional message type

        Returns:
            dict: Enhanced classification result
        """
        logger.info(f"Services enhancer called with narration: {narration}")

        # First, check for high confidence classifications that should not be overridden
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)
        narration_lower = narration.lower()

        # Don't override high confidence classifications unless they're clearly wrong
        # Lower the threshold from 0.95 to 0.90 to allow more corrections
        if confidence >= 0.90 and purpose_code not in ['CCRD', 'INTE']:
            logger.debug(f"Not overriding high confidence classification: {purpose_code} ({confidence})")
            return result

        # Check for negative indicators
        for indicator in self.negative_indicators:
            if indicator.lower() in narration_lower:
                logger.debug(f"Negative indicator found: {indicator}")
                # This is clearly not service-related
                return result

        # Call the base implementation first
        enhanced_result = super().enhance_classification(result, narration, message_type)

        # If the base implementation changed something, return it
        if enhanced_result != result:
            # Ensure category purpose code is set to SUPP for services (correct mapping for SCVE)
            if enhanced_result.get('purpose_code') == "SCVE":
                enhanced_result['category_purpose_code'] = "SUPP"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "services_category_mapping_to_SUPP"
            return enhanced_result

        # Check if we should override the current classification
        if self.should_override_classification(result, narration):
            logger.info(f"Overriding {purpose_code} with SCVE based on context analysis")
            enhanced_result = self._create_enhanced_result(result, 'SCVE', 0.85, "Context analysis override")

            # Ensure category purpose code is set to SUPP for services (correct mapping for SCVE)
            enhanced_result['category_purpose_code'] = "SUPP"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "services_category_mapping_to_SUPP"

            return enhanced_result

        # Message type specific considerations
        if message_type == "MT103":
            # MT103 is commonly used for service payments
            # Enhanced pattern matching for MT103 service payments
            mt103_service_patterns = [
                'service', 'consulting', 'professional', 'maintenance', 'repair',
                'legal service', 'legal fee', 'attorney', 'lawyer',
                'professional service', 'professional fee',
                'consulting service', 'consulting fee',
                'maintenance service', 'repair service',
                'installation service', 'support service',
                'it support', 'technical support',
                'service payment', 'payment for service',
                'service fee', 'service charge',
                'marketing service', 'marketing fee',
                'advertising service', 'advertising fee',
                'accounting service', 'accounting fee',
                'audit service', 'audit fee',
                'management service', 'management fee',
                'advisory service', 'advisory fee',
                'consultancy', 'consultancy service',
                'professional advice', 'professional consultation'
            ]

            # Check for service patterns in MT103 messages
            if any(pattern in narration_lower for pattern in mt103_service_patterns):
                logger.info(f"MT103 services context detected: {narration}")

                # Check if the current classification is INTE (common misclassification)
                if purpose_code == 'INTE':
                    logger.info(f"Correcting INTE misclassification to SCVE for service-related MT103")
                    enhanced_result = self._create_enhanced_result(result, 'SCVE', 0.99, "MT103 services correction (INTE->SCVE)")
                else:
                    enhanced_result = self._create_enhanced_result(result, 'SCVE', 0.95, "MT103 services context")

                # Ensure category purpose code is set to SUPP for services (not SCVE)
                enhanced_result['category_purpose_code'] = "SUPP"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "services_category_mapping_to_SUPP"

                return enhanced_result

            # Special case for "PAYMENT FOR MAINTENANCE SERVICES" which is incorrectly classified as INTE
            if "maintenance service" in narration_lower or "maintenance services" in narration_lower:
                logger.info(f"Maintenance services detected in MT103: {narration}")
                enhanced_result = self._create_enhanced_result(result, 'SCVE', 0.99, "MT103 maintenance services correction")
                enhanced_result['category_purpose_code'] = "SUPP"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "maintenance_services_mapping_to_SUPP"
                return enhanced_result

            # Special case for "LEGAL SERVICES PAYMENT" which is incorrectly classified as INTE
            if "legal service" in narration_lower or "legal services" in narration_lower:
                logger.info(f"Legal services detected in MT103: {narration}")
                enhanced_result = self._create_enhanced_result(result, 'SCVE', 0.99, "MT103 legal services correction")
                enhanced_result['category_purpose_code'] = "SUPP"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "legal_services_mapping_to_SUPP"
                return enhanced_result

            # Special case for "MARKETING SERVICES" which is incorrectly classified as INTE
            if "marketing service" in narration_lower or "marketing services" in narration_lower:
                logger.info(f"Marketing services detected in MT103: {narration}")
                enhanced_result = self._create_enhanced_result(result, 'SCVE', 0.99, "MT103 marketing services correction")
                enhanced_result['category_purpose_code'] = "SUPP"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "marketing_services_mapping_to_SUPP"
                return enhanced_result

            # Special case for "CONSULTING SERVICES" which is incorrectly classified as INTE or CCRD
            logger.info(f"Checking for consulting services in: '{narration_lower}'")
            has_consulting_service = "consulting service" in narration_lower
            has_consulting_services = "consulting services" in narration_lower
            has_consultancy = "consultancy" in narration_lower
            has_payment_for_consulting = "payment for consulting" in narration_lower
            has_payment = "payment" in narration_lower
            has_fee = "fee" in narration_lower
            has_consulting = "consulting" in narration_lower

            logger.info(f"Consulting checks: service={has_consulting_service}, services={has_consulting_services}, "
                        f"consultancy={has_consultancy}, payment_for={has_payment_for_consulting}, "
                        f"payment={has_payment}, fee={has_fee}, consulting={has_consulting}")

            if (has_consulting_service or
                has_consulting_services or
                has_consultancy or
                has_payment_for_consulting or
                ((has_payment or has_fee) and has_consulting)):
                logger.info(f"Consulting services detected in MT103: {narration}")
                enhanced_result = self._create_enhanced_result(result, 'SCVE', 0.99, "MT103 consulting services correction")
                enhanced_result['category_purpose_code'] = "SUPP"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "consulting_services_mapping_to_SUPP"
                return enhanced_result

        # No services pattern detected
        logger.debug("No services pattern detected")
        return result

    def should_override_classification(self, result, narration):
        """
        Determine if services classification should override existing classification.

        Args:
            result: Current classification result
            narration: Transaction narration

        Returns:
            bool: True if should override
        """
        narration_lower = narration.lower()
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)

        # Check for strong services context
        services_terms = ['service', 'consulting', 'professional', 'maintenance', 'repair', 'installation', 'support', 'subscription']
        services_count = sum(1 for term in services_terms if term in narration_lower)

        # If multiple services terms are present, likely services-related
        if services_count >= 2:
            # Don't override if confidence is very high
            if confidence >= 0.9:
                return False

            # Override OTHR or low confidence classifications
            if purpose_code == 'OTHR' or confidence < 0.7:
                return True

            # Override goods-related codes with medium confidence
            if purpose_code in ['GDDS', 'GSCB', 'POPE'] and confidence < 0.8:
                return True

        # Don't override other classifications unless very strong evidence
        return False
