"""
Context-aware enhancer for purpose code classification.

This enhancer takes into account the message type (MT103, MT202, MT205) and other
contextual information to improve the classification of purpose codes.
"""

import re
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer
import logging

logger = logging.getLogger(__name__)

class ContextAwareEnhancer(SemanticEnhancer):
    """
    Enhancer that considers message type and other contextual information.

    This enhancer improves the classification of purpose codes by taking into
    account the message type (MT103, MT202, MT205) and other contextual information.
    """

    def __init__(self, matcher=None):
        super().__init__(matcher=matcher)
        self._initialize_patterns()

        # Initialize message type patterns with expanded patterns to detect more variations
        self.mt103_pattern = re.compile(r'\b(MT103|103:|MT\s*103|103\s*message|customer\s*transfer|customer\s*credit\s*transfer)\b', re.IGNORECASE)
        self.mt202_pattern = re.compile(r'\b(MT202|202:|MT\s*202|202\s*message|financial\s*institution\s*transfer|bank\s*transfer)\b', re.IGNORECASE)
        self.mt205_pattern = re.compile(r'\b(MT205|205:|MT\s*205|205\s*message|financial\s*institution\s*transfer\s*to\s*customer)\b', re.IGNORECASE)

        # Add patterns for cover payments
        self.mt202cov_pattern = re.compile(r'\b(MT202COV|202COV:|MT\s*202\s*COV|202\s*COV\s*message|cover\s*payment)\b', re.IGNORECASE)
        self.mt205cov_pattern = re.compile(r'\b(MT205COV|205COV:|MT\s*205\s*COV|205\s*COV\s*message|cover\s*payment)\b', re.IGNORECASE)

        # Initialize message type preferences
        self.mt103_preferences = {
            'SALA': 1.2,
            'SUPP': 1.2,
            'SCVE': 1.2,
            'GDDS': 1.2,
            'OTHR': 1.0
        }

        self.mt202_preferences = {
            'INTC': 1.2,
            'CASH': 1.2,
            'TREA': 1.2,
            'FREX': 1.2,
            'OTHR': 1.0
        }

        self.mt205_preferences = {
            'INVS': 1.2,
            'SECU': 1.2,
            'DIVD': 1.2,
            'INTC': 1.2,
            'OTHR': 1.0
        }

    def _initialize_patterns(self):
        """Initialize semantic patterns and contexts."""
        # Direct keywords with purpose codes
        self.direct_keywords = {}

        # Semantic context patterns
        self.context_patterns = [
            {
                'purpose_code': 'OTHR',
                'keywords': ['MT103', '103:'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['MT202', '202:'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['MT205', '205:'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['salary', 'payroll', 'wage', 'compensation', 'remuneration', 'payment', 'transfer', 'deposit'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'transfer', 'salary', 'payroll', 'wage', 'compensation'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['supplier', 'vendor', 'payment', 'invoice', 'bill'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'invoice', 'supplier', 'vendor'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'consulting', 'professional', 'payment', 'invoice', 'fee'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['payment', 'invoice', 'fee', 'service', 'consulting', 'professional'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['goods', 'merchandise', 'product', 'equipment', 'payment', 'invoice', 'purchase'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['payment', 'invoice', 'purchase', 'goods', 'merchandise', 'product', 'equipment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['interbank', 'nostro', 'vostro', 'correspondent', 'transfer', 'payment', 'settlement'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['transfer', 'payment', 'settlement', 'interbank', 'nostro', 'vostro', 'correspondent'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['cash', 'liquidity', 'management', 'transfer', 'position', 'adjustment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['management', 'transfer', 'position', 'adjustment', 'cash', 'liquidity'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['treasury', 'treasuries', 'operation', 'management', 'position', 'settlement'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['operation', 'management', 'position', 'settlement', 'treasury', 'treasuries'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['forex', 'foreign', 'exchange', 'swap', 'settlement', 'trade', 'transaction'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['settlement', 'trade', 'transaction', 'forex', 'foreign', 'exchange', 'swap'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD', 'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['investment', 'portfolio', 'fund', 'asset', 'management', 'transfer', 'funding'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['management', 'transfer', 'funding', 'investment', 'portfolio', 'fund', 'asset'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['securities', 'security', 'bond', 'equity', 'stock', 'share', 'settlement', 'trading', 'purchase', 'sale'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['settlement', 'trading', 'purchase', 'sale', 'securities', 'security', 'bond', 'equity', 'stock', 'share'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['dividend', 'dividends', 'payment', 'distribution', 'payout'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'distribution', 'payout', 'dividend', 'dividends'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['intragroup', 'intercompany', 'group', 'internal', 'transfer', 'payment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['transfer', 'payment', 'intragroup', 'intercompany', 'group', 'internal'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['othr'],
                'proximity': 5,
                'weight': 0.8
            },
        ]

        # Semantic terms for similarity matching
        self.semantic_terms = []

    def detect_message_type(self, narration, message_type=None):
        """
        Detect the message type from the narration or use the provided message_type.

        IMPORTANT: This method prioritizes narration content analysis to detect
        message types, even when a message_type parameter is provided. This ensures
        that all relevant message type information is captured.

        Args:
            narration: The narration text
            message_type: The message type (if provided)

        Returns:
            str: The detected message type ('MT103', 'MT202', 'MT205', 'MT202COV', 'MT205COV', or None)
        """
        detected_type = None

        # First, try to detect from narration (prioritize narration content)
        if self.mt103_pattern.search(narration):
            detected_type = 'MT103'
        elif self.mt202cov_pattern.search(narration):
            detected_type = 'MT202COV'
        elif self.mt205cov_pattern.search(narration):
            detected_type = 'MT205COV'
        elif self.mt202_pattern.search(narration):
            detected_type = 'MT202'
        elif self.mt205_pattern.search(narration):
            detected_type = 'MT205'

        # Additional semantic detection from narration content
        narration_lower = narration.lower()

        # Look for customer transfer indicators (MT103)
        if not detected_type and any(term in narration_lower for term in
                                    ['customer transfer', 'customer credit', 'salary payment',
                                     'retail payment', 'personal transfer', 'individual payment']):
            detected_type = 'MT103'

        # Look for bank-to-bank transfer indicators (MT202)
        elif not detected_type and any(term in narration_lower for term in
                                      ['interbank', 'inter-bank', 'bank to bank', 'nostro', 'vostro',
                                       'correspondent', 'financial institution transfer']):
            detected_type = 'MT202'

        # Look for cover payment indicators
        elif not detected_type and any(term in narration_lower for term in
                                      ['cover payment', 'cover for payment', 'payment cover',
                                       'underlying payment', 'cover transfer']):
            detected_type = 'MT202COV'

        # If message_type is provided and we haven't detected from narration, use it
        if not detected_type and message_type:
            if 'MT103' in message_type.upper():
                detected_type = 'MT103'
            elif 'MT202COV' in message_type.upper():
                detected_type = 'MT202COV'
            elif 'MT205COV' in message_type.upper():
                detected_type = 'MT205COV'
            elif 'MT202' in message_type.upper():
                detected_type = 'MT202'
            elif 'MT205' in message_type.upper():
                detected_type = 'MT205'

        return detected_type

    def enhance(self, purpose_code, confidence, narration, message_type=None):
        """
        Enhance the purpose code classification based on message type and context.

        This method prioritizes narration content analysis for detecting patterns
        and determining the appropriate purpose code, using message type as
        additional context.

        Args:
            purpose_code: The predicted purpose code
            confidence: The confidence score of the prediction
            narration: The narration text
            message_type: The message type (if provided)

        Returns:
            tuple: (enhanced_purpose_code, enhanced_confidence)
        """
        # Convert narration to lowercase for case-insensitive matching
        narration_lower = narration.lower()

        # If no message type detected, we can still analyze the narration content
        # for semantic patterns, but we won't apply message type-specific preferences
        if not message_type:
            # Check for common patterns regardless of message type
            # Salary payments
            if re.search(r'\b(salary|payroll|wage|compensation|remuneration)\b.*?\b(payment|transfer|deposit)\b', narration_lower) or \
               re.search(r'\b(payment|transfer)\b.*?\b(salary|payroll|wage|compensation)\b', narration_lower):
                logger.debug(f"Salary pattern matched in narration: {narration}")
                return 'SALA', 0.95

            # Supplier payments
            if re.search(r'\b(supplier|vendor)\b.*?\b(payment|invoice|bill)\b', narration_lower) or \
               re.search(r'\b(payment|invoice)\b.*?\b(supplier|vendor)\b', narration_lower):
                logger.debug(f"Supplier pattern matched in narration: {narration}")
                return 'SUPP', 0.95

            # Service payments
            if re.search(r'\b(service|consulting|professional)\b.*?\b(payment|invoice|fee)\b', narration_lower) or \
               re.search(r'\b(payment|invoice|fee)\b.*?\b(service|consulting|professional)\b', narration_lower):
                logger.debug(f"Service pattern matched in narration: {narration}")
                return 'SCVE', 0.95

            # Goods payments
            if re.search(r'\b(goods|merchandise|product|equipment)\b.*?\b(payment|invoice|purchase)\b', narration_lower) or \
               re.search(r'\b(payment|invoice|purchase)\b.*?\b(goods|merchandise|product|equipment)\b', narration_lower):
                logger.debug(f"Goods pattern matched in narration: {narration}")
                return 'GDDS', 0.95

            # Return original if no patterns matched
            return purpose_code, confidence

        # Get the preferences for the detected message type
        if message_type == 'MT103':
            preferences = self.mt103_preferences

            # Advanced pattern matching for MT103 messages
            if re.search(r'\b(salary|payroll|wage|compensation|remuneration)\b.*?\b(payment|transfer|deposit)\b', narration_lower) or \
               re.search(r'\b(payment|transfer)\b.*?\b(salary|payroll|wage|compensation)\b', narration_lower):
                logger.debug(f"MT103 salary pattern matched in narration: {narration}")
                return 'SALA', 0.95

            if re.search(r'\b(supplier|vendor)\b.*?\b(payment|invoice|bill)\b', narration_lower) or \
               re.search(r'\b(payment|invoice)\b.*?\b(supplier|vendor)\b', narration_lower):
                logger.debug(f"MT103 supplier pattern matched in narration: {narration}")
                return 'SUPP', 0.95

            if re.search(r'\b(service|consulting|professional)\b.*?\b(payment|invoice|fee)\b', narration_lower) or \
               re.search(r'\b(payment|invoice|fee)\b.*?\b(service|consulting|professional)\b', narration_lower):
                logger.debug(f"MT103 service pattern matched in narration: {narration}")
                return 'SCVE', 0.95

            if re.search(r'\b(goods|merchandise|product|equipment)\b.*?\b(payment|invoice|purchase)\b', narration_lower) or \
               re.search(r'\b(payment|invoice|purchase)\b.*?\b(goods|merchandise|product|equipment)\b', narration_lower):
                logger.debug(f"MT103 goods pattern matched in narration: {narration}")
                return 'GDDS', 0.95

        elif message_type == 'MT202':
            preferences = self.mt202_preferences

            # Advanced pattern matching for MT202 messages
            if re.search(r'\b(interbank|nostro|vostro|correspondent)\b.*?\b(transfer|payment|settlement)\b', narration_lower) or \
               re.search(r'\b(transfer|payment|settlement)\b.*?\b(interbank|nostro|vostro|correspondent)\b', narration_lower):
                logger.debug(f"MT202 interbank pattern matched in narration: {narration}")
                return 'INTC', 0.95

            if re.search(r'\b(cash|liquidity)\b.*?\b(management|transfer|position|adjustment)\b', narration_lower) or \
               re.search(r'\b(management|transfer|position|adjustment)\b.*?\b(cash|liquidity)\b', narration_lower):
                logger.debug(f"MT202 cash management pattern matched in narration: {narration}")
                return 'CASH', 0.95

            if re.search(r'\b(treasury|treasuries)\b.*?\b(operation|management|position|settlement)\b', narration_lower) or \
               re.search(r'\b(operation|management|position|settlement)\b.*?\b(treasury|treasuries)\b', narration_lower):
                logger.debug(f"MT202 treasury pattern matched in narration: {narration}")
                return 'TREA', 0.95

            if re.search(r'\b(fx|forex|foreign exchange|swap)\b.*?\b(settlement|trade|transaction)\b', narration_lower) or \
               re.search(r'\b(settlement|trade|transaction)\b.*?\b(fx|forex|foreign exchange|swap)\b', narration_lower) or \
               re.search(r'(USD|EUR|GBP|JPY|CHF|AUD|CAD|NZD)/(USD|EUR|GBP|JPY|CHF|AUD|CAD|NZD)', narration):
                logger.debug(f"MT202 forex pattern matched in narration: {narration}")
                return 'FREX', 0.95

        elif message_type == 'MT202COV' or message_type == 'MT205COV':
            # For cover payments, we prioritize the COVR purpose code
            logger.debug(f"Cover payment message type detected: {message_type}")

            # Check if the narration contains cover payment indicators
            if re.search(r'\b(cover|underlying|related)\b.*?\b(payment|transfer|transaction)\b', narration_lower) or \
               re.search(r'\b(payment|transfer|transaction)\b.*?\b(cover|underlying|related)\b', narration_lower):
                logger.debug(f"Cover payment pattern matched in narration: {narration}")
                return 'COVR', 0.95

            # If it's a cover payment message type but no specific cover payment indicators in narration,
            # still return COVR but with slightly lower confidence
            return 'COVR', 0.90

        elif message_type == 'MT205':
            preferences = self.mt205_preferences

            # Advanced pattern matching for MT205 messages
            if re.search(r'\b(investment|portfolio|fund|asset)\b.*?\b(management|transfer|funding)\b', narration_lower) or \
               re.search(r'\b(management|transfer|funding)\b.*?\b(investment|portfolio|fund|asset)\b', narration_lower):
                logger.debug(f"MT205 investment pattern matched in narration: {narration}")
                return 'INVS', 0.95

            if re.search(r'\b(securities|security|bond|equity|stock|share)\b.*?\b(settlement|trading|purchase|sale)\b', narration_lower) or \
               re.search(r'\b(settlement|trading|purchase|sale)\b.*?\b(securities|security|bond|equity|stock|share)\b', narration_lower):
                logger.debug(f"MT205 securities pattern matched in narration: {narration}")
                return 'SECU', 0.95

            if re.search(r'\b(dividend|dividends)\b.*?\b(payment|distribution|payout)\b', narration_lower) or \
               re.search(r'\b(payment|distribution|payout)\b.*?\b(dividend|dividends)\b', narration_lower):
                logger.debug(f"MT205 dividend pattern matched in narration: {narration}")
                return 'DIVD', 0.95

            if re.search(r'\b(intragroup|intercompany|group|internal)\b.*?\b(transfer|payment)\b', narration_lower) or \
               re.search(r'\b(transfer|payment)\b.*?\b(intragroup|intercompany|group|internal)\b', narration_lower):
                logger.debug(f"MT205 intragroup pattern matched in narration: {narration}")
                return 'INTC', 0.95

        else:
            # If no preferences for the detected message type, return the original purpose code and confidence
            return purpose_code, confidence

        # Apply the preferences to the confidence
        if purpose_code in preferences:
            # Adjust confidence based on message type preference
            adjusted_confidence = confidence * preferences[purpose_code]
            # Cap the confidence at 0.95
            adjusted_confidence = min(adjusted_confidence, 0.95)
            logger.debug(f"Adjusted confidence for {purpose_code} from {confidence} to {adjusted_confidence} based on message type {message_type}")
            return purpose_code, adjusted_confidence

        # If no preferences for the purpose code, return the original purpose code and confidence
        return purpose_code, confidence

    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification based on message type and context.

        This method prioritizes narration content for message type detection,
        ensuring that all relevant contextual information is captured even when
        a message_type parameter is provided.

        Args:
            result: The classification result dictionary
            narration: The narration text
            message_type: The message type (if provided)

        Returns:
            dict: The enhanced classification result
        """
        # Get the original purpose code and confidence
        original_purpose = result['purpose_code']
        original_conf = result['confidence']

        # Detect message type from narration first, then fall back to provided message_type
        detected_message_type = self.detect_message_type(narration, message_type)

        # Log the detected message type
        if detected_message_type:
            logger.debug(f"Detected message type: {detected_message_type} from narration: {narration}")

        # Apply the enhance method with the detected message type
        enhanced_purpose, enhanced_conf = self.enhance(original_purpose, original_conf, narration, detected_message_type)

        # Always add the detected message_type to the result
        result['message_type'] = detected_message_type

        # Add narration-based detection flag to help with debugging and analysis
        if detected_message_type and (not message_type or detected_message_type != message_type):
            result['narration_detected_message_type'] = True

            # If we detected a message type from narration but it wasn't provided as parameter,
            # log this information for analysis
            if not message_type:
                logger.info(f"Message type '{detected_message_type}' detected from narration but not provided as parameter: {narration}")
            # If we detected a different message type than what was provided, log this discrepancy
            elif detected_message_type != message_type:
                logger.info(f"Message type mismatch: Provided '{message_type}' but detected '{detected_message_type}' from narration: {narration}")

        # If the purpose code was enhanced, update the result
        if enhanced_purpose != original_purpose or enhanced_conf != original_conf:
            result['purpose_code'] = enhanced_purpose
            result['confidence'] = enhanced_conf
            result['enhancement_applied'] = "context_aware_enhancer"
        result['enhanced'] = True
            result['original_purpose_code'] = original_purpose
            result['original_confidence'] = original_conf

            # Log the enhancement
            logger.debug(f"Enhanced purpose code from {original_purpose} to {enhanced_purpose} with confidence {enhanced_conf:.2f} based on message type {detected_message_type}")

        return result
