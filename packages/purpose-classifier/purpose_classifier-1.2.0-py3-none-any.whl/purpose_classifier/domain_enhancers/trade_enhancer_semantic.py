"""
Semantic Trade Enhancer for Purpose Code Classification.

This module provides a specialized enhancer for trade-related transactions,
using semantic pattern matching to identify trade operations with high accuracy.
"""

import logging
import re
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer

logger = logging.getLogger(__name__)

class TradeEnhancerSemantic(SemanticEnhancer):
    """
    Specialized enhancer for trade-related transactions.
    
    Uses semantic pattern matching to identify trade operations
    with high accuracy and confidence.
    """
    
    def __init__(self, matcher=None):
        """
        Initialize with optional matcher.
        
        Args:
            matcher: Optional SemanticPatternMatcher instance to use
        """
        super().__init__(matcher=matcher)
        
        # Initialize trade-specific patterns and contexts
        self._initialize_patterns()
    
    def _initialize_patterns(self):
        """Initialize trade-specific patterns and contexts."""
        # Direct trade keywords (highest confidence)
        self.trade_keywords = [
            'trade', 'trading', 'import', 'export', 'goods trade', 'trade payment',
            'trade settlement', 'trade transaction', 'trade invoice', 'trade finance',
            'commercial invoice', 'commercial payment', 'commercial transaction',
            'import payment', 'export payment', 'import invoice', 'export invoice',
            'customs payment', 'customs duty', 'customs clearance', 'duty payment',
            'international trade', 'cross-border trade', 'trade agreement',
            'letter of credit', 'l/c', 'documentary credit', 'bill of lading',
            'shipping document', 'trade document', 'incoterm', 'fob', 'cif', 'exw'
        ]
        
        # Map keywords to purpose codes
        self.direct_keywords = {
            'TRAD': self.trade_keywords
        }
        
        # Semantic context patterns for trade operations
        self.trade_contexts = [
            {"keywords": ["trade", "payment"], "proximity": 5, "weight": 1.0},
            {"keywords": ["trade", "settlement"], "proximity": 5, "weight": 1.0},
            {"keywords": ["trade", "transaction"], "proximity": 5, "weight": 0.9},
            {"keywords": ["trade", "invoice"], "proximity": 5, "weight": 0.9},
            {"keywords": ["trade", "finance"], "proximity": 5, "weight": 0.9},
            {"keywords": ["commercial", "invoice"], "proximity": 5, "weight": 0.9},
            {"keywords": ["commercial", "payment"], "proximity": 5, "weight": 0.9},
            {"keywords": ["import", "payment"], "proximity": 5, "weight": 0.9},
            {"keywords": ["export", "payment"], "proximity": 5, "weight": 0.9},
            {"keywords": ["import", "invoice"], "proximity": 5, "weight": 0.9},
            {"keywords": ["export", "invoice"], "proximity": 5, "weight": 0.9},
            {"keywords": ["customs", "payment"], "proximity": 5, "weight": 0.9},
            {"keywords": ["customs", "duty"], "proximity": 5, "weight": 0.9},
            {"keywords": ["customs", "clearance"], "proximity": 5, "weight": 0.9},
            {"keywords": ["duty", "payment"], "proximity": 5, "weight": 0.9},
            {"keywords": ["international", "trade"], "proximity": 5, "weight": 0.9},
            {"keywords": ["cross-border", "trade"], "proximity": 5, "weight": 0.9},
            {"keywords": ["letter", "credit"], "proximity": 5, "weight": 0.9},
            {"keywords": ["documentary", "credit"], "proximity": 5, "weight": 0.9},
            {"keywords": ["bill", "lading"], "proximity": 5, "weight": 0.9},
            {"keywords": ["shipping", "document"], "proximity": 5, "weight": 0.9},
            {"keywords": ["trade", "document"], "proximity": 5, "weight": 0.9}
        ]
        
        # Trade-related terms for semantic similarity matching
        self.semantic_terms = [
            {"term": "trade", "purpose_code": "TRAD", "threshold": 0.7, "weight": 1.0},
            {"term": "trading", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.9},
            {"term": "import", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.9},
            {"term": "export", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.9},
            {"term": "goods", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.8},
            {"term": "commercial", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.8},
            {"term": "invoice", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.8},
            {"term": "settlement", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.7},
            {"term": "transaction", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.7},
            {"term": "finance", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.7},
            {"term": "customs", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.9},
            {"term": "duty", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.9},
            {"term": "clearance", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.8},
            {"term": "international", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.8},
            {"term": "cross-border", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.9},
            {"term": "letter", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.7},
            {"term": "credit", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.7},
            {"term": "documentary", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.8},
            {"term": "bill", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.7},
            {"term": "lading", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.9},
            {"term": "shipping", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.8},
            {"term": "document", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.7},
            {"term": "incoterm", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.9},
            {"term": "fob", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.9},
            {"term": "cif", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.9},
            {"term": "exw", "purpose_code": "TRAD", "threshold": 0.7, "weight": 0.9}
        ]
        
        # Negative indicators (patterns that suggest it's NOT a trade operation)
        self.negative_indicators = [
            'not trade', 'non-trade', 'excluding trade',
            'trade free', 'no trade', 'without trade',
            'trade tax', 'tax on trade'  # These are tax payments, not trade operations
        ]
        
        # Compile regex patterns for cross-border detection
        self.cross_border_patterns = [
            re.compile(r'\b(international|cross-border|overseas|foreign|global)\b', re.IGNORECASE),
            re.compile(r'\b(import|export|customs|duty|tariff)\b', re.IGNORECASE),
            re.compile(r'\b(shipping|freight|cargo|container)\b', re.IGNORECASE),
            re.compile(r'\b(incoterm|fob|cif|exw|fas|dap|ddp)\b', re.IGNORECASE)
        ]
        
        # Compile regex patterns for domestic trade detection
        self.domestic_trade_patterns = [
            re.compile(r'\b(domestic|local|national|internal)\s+(trade|commerce|business)\b', re.IGNORECASE),
            re.compile(r'\b(within\s+country|same\s+country)\b', re.IGNORECASE)
        ]
    
    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification for trade-related transactions.
        
        Args:
            result: Initial classification result
            narration: Transaction narration
            message_type: Optional message type
            
        Returns:
            dict: Enhanced classification result
        """
        logger.debug(f"Trade enhancer called with narration: {narration}")
        
        # Get current purpose code and confidence
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)
        
        # Don't override if already classified as TRAD with high confidence
        if purpose_code == 'TRAD' and confidence >= 0.8:
            logger.debug(f"Already classified as TRAD with high confidence: {confidence}")
            return result
        
        # Check for negative indicators
        narration_lower = narration.lower()
        for indicator in self.negative_indicators:
            if indicator.lower() in narration_lower:
                logger.debug(f"Negative indicator found: {indicator}")
                return result
        
        # Check for special trade cases
        is_special_case, special_confidence, special_reason = self.handle_special_cases(narration)
        if is_special_case:
            logger.info(f"Trade special case: {special_reason} with confidence {special_confidence}")
            return self._create_enhanced_result(result, 'TRAD', special_confidence, special_reason)
        
        # Direct keyword matching (highest confidence)
        matched, keyword_confidence, keyword = self.direct_keyword_match(narration, 'TRAD')
        if matched:
            logger.info(f"Trade keyword match: {keyword} with confidence {keyword_confidence}")
            return self._create_enhanced_result(result, 'TRAD', keyword_confidence, f"Direct trade keyword match: {keyword}")
        
        # Semantic context pattern matching
        context_score = self.context_match(narration, self.trade_contexts)
        if context_score >= 0.7:
            logger.info(f"Trade context match with score: {context_score:.2f}")
            return self._create_enhanced_result(result, 'TRAD', min(0.95, context_score), 
                                              f"Trade context match with score: {context_score:.2f}")
        
        # Semantic similarity matching
        matched, sem_confidence, sem_purpose_code, sem_matches = self.semantic_similarity_match(narration, self.semantic_terms)
        if matched and sem_purpose_code == 'TRAD':
            logger.info(f"Trade semantic match with confidence: {sem_confidence:.2f}")
            return self._create_enhanced_result(result, 'TRAD', sem_confidence, 
                                              f"Semantic similarity matches: {len(sem_matches)}")
        
        # Cross-border detection
        is_cross_border, cross_border_confidence, cross_border_reason = self.detect_cross_border_trade(narration)
        if is_cross_border:
            logger.info(f"Cross-border trade detected: {cross_border_reason} with confidence {cross_border_confidence}")
            return self._create_enhanced_result(result, 'TRAD', cross_border_confidence, cross_border_reason)
        
        # Message type specific analysis
        if message_type:
            enhanced_result = self.analyze_message_type(result, narration, message_type)
            if enhanced_result != result:
                return enhanced_result
        
        # Check if we should override the current classification
        if self.should_override_classification(result, narration):
            logger.info(f"Overriding {purpose_code} with TRAD based on context analysis")
            return self._create_enhanced_result(result, 'TRAD', 0.85, "Context analysis override")
        
        # No trade pattern detected
        logger.debug("No trade pattern detected")
        return result
    
    def handle_special_cases(self, narration):
        """
        Handle special edge cases for trade classification.
        
        Args:
            narration: Transaction narration
            
        Returns:
            tuple: (is_trade, confidence, reason)
        """
        narration_lower = narration.lower()
        
        # Check for negative indicators first
        for indicator in self.negative_indicators:
            if indicator in narration_lower:
                return (False, 0.0, f"Negative indicator found: {indicator}")
        
        # Handle letter of credit (highest confidence)
        if 'letter of credit' in narration_lower or 'l/c' in narration_lower or 'documentary credit' in narration_lower:
            return (True, 0.95, "Letter of credit explicitly mentioned")
        
        # Handle bill of lading
        if 'bill of lading' in narration_lower or 'b/l' in narration_lower:
            return (True, 0.95, "Bill of lading explicitly mentioned")
        
        # Handle incoterms
        incoterms = ['fob', 'cif', 'exw', 'fas', 'dap', 'ddp', 'cpt', 'cip', 'dat', 'dpu']
        for incoterm in incoterms:
            if f" {incoterm} " in f" {narration_lower} ":  # Add spaces to ensure it's a standalone term
                return (True, 0.95, f"Incoterm {incoterm.upper()} explicitly mentioned")
        
        # Handle customs and duty
        if ('customs' in narration_lower and ('duty' in narration_lower or 'payment' in narration_lower or 'clearance' in narration_lower)):
            return (True, 0.9, "Customs duty or clearance explicitly mentioned")
        
        # Not a special case
        return (False, 0.0, "No special trade case detected")
    
    def detect_cross_border_trade(self, narration):
        """
        Detect cross-border trade indicators in narration.
        
        Args:
            narration: Transaction narration
            
        Returns:
            tuple: (is_cross_border, confidence, reason)
        """
        narration_lower = narration.lower()
        
        # Check for explicit cross-border indicators
        cross_border_matches = []
        for pattern in self.cross_border_patterns:
            if matches := pattern.findall(narration_lower):
                cross_border_matches.extend(matches)
        
        # Check for domestic trade indicators (negative signal)
        domestic_matches = []
        for pattern in self.domestic_trade_patterns:
            if matches := pattern.findall(narration_lower):
                domestic_matches.extend(matches)
        
        # If we have domestic indicators, this is likely not cross-border
        if domestic_matches:
            return (False, 0.0, f"Domestic trade indicators found: {domestic_matches}")
        
        # If we have multiple cross-border indicators, this is likely cross-border trade
        if len(cross_border_matches) >= 2:
            confidence = min(0.9, 0.7 + (0.1 * len(cross_border_matches)))
            return (True, confidence, f"Cross-border trade indicators: {cross_border_matches}")
        
        # If we have one strong cross-border indicator, this might be cross-border trade
        if len(cross_border_matches) == 1:
            # Check if it's a strong indicator (import, export, customs, duty)
            strong_indicators = ['import', 'export', 'customs', 'duty', 'international', 'cross-border']
            if any(indicator in cross_border_matches[0].lower() for indicator in strong_indicators):
                return (True, 0.85, f"Strong cross-border trade indicator: {cross_border_matches[0]}")
        
        # No clear cross-border indicators
        return (False, 0.0, "No cross-border trade indicators detected")
    
    def analyze_message_type(self, result, narration, message_type):
        """
        Analyze message type for trade-related patterns.
        
        Args:
            result: Current classification result
            narration: Transaction narration
            message_type: Message type
            
        Returns:
            dict: Enhanced classification result
        """
        narration_lower = narration.lower()
        
        # MT103 specific patterns (customer transfers)
        if message_type == 'MT103':
            # Check for trade-related keywords in MT103
            if any(keyword in narration_lower for keyword in ['trade', 'import', 'export', 'commercial', 'invoice']):
                if 'payment' in narration_lower or 'settlement' in narration_lower:
                    logger.info(f"MT103 trade payment detected")
                    return self._create_enhanced_result(result, 'TRAD', 0.9, "MT103 trade payment")
        
        # MT202 specific patterns (financial institution transfers)
        elif message_type == 'MT202' or message_type == 'MT202COV':
            # Check for trade finance keywords in MT202
            if any(keyword in narration_lower for keyword in ['trade finance', 'letter of credit', 'l/c', 'documentary credit']):
                logger.info(f"MT202 trade finance detected")
                return self._create_enhanced_result(result, 'TRAD', 0.9, "MT202 trade finance")
        
        # No message type specific pattern detected
        return result
    
    def should_override_classification(self, result, narration):
        """
        Determine if trade classification should override existing classification.
        
        Args:
            result: Current classification result
            narration: Transaction narration
            
        Returns:
            bool: True if should override
        """
        narration_lower = narration.lower()
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)
        
        # Check for strong trade context
        context_score = self.context_match(narration, self.trade_contexts)
        
        # Check if current classification has low confidence
        if confidence < 0.7 and context_score >= 0.6:
            return True
        
        # Don't override other classifications unless very strong evidence
        return False
    
    def _create_enhanced_result(self, original_result, purpose_code, confidence, reason):
        """
        Create an enhanced result dictionary.
        
        Args:
            original_result: Original classification result
            purpose_code: Enhanced purpose code
            confidence: Enhanced confidence
            reason: Reason for enhancement
            
        Returns:
            dict: Enhanced classification result
        """
        # Create a copy of the original result
        result = original_result.copy()
        
        # Update with enhanced values
        result['purpose_code'] = purpose_code
        result['confidence'] = confidence
        result['category_purpose_code'] = purpose_code  # Direct mapping for TRAD
        result['category_confidence'] = confidence
        
        # Add enhancement metadata
        result['enhanced'] = True
        result['enhancement_applied'] = 'trade_enhancer'
        result['enhanced'] = True
        result['reason'] = reason
        result['original_purpose_code'] = original_result.get('purpose_code')
        result['original_confidence'] = original_result.get('confidence')
        
        # Set force flags to prevent other enhancers from overriding
        if confidence >= 0.9:
            result['force_purpose_code'] = True
            result['force_category_purpose_code'] = True
        
        return result
