"""
Semantic Insurance Enhancer for Purpose Code Classification.

This module provides a specialized enhancer for insurance-related transactions,
using semantic pattern matching to identify insurance payments with high accuracy.
"""

import logging
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer

logger = logging.getLogger(__name__)

class InsuranceEnhancerSemantic(SemanticEnhancer):
    """
    Specialized enhancer for insurance-related transactions.
    
    Uses semantic pattern matching to identify insurance payments
    with high accuracy and confidence.
    """
    
    def __init__(self, matcher=None):
        """
        Initialize with optional matcher.
        
        Args:
            matcher: Optional SemanticPatternMatcher instance to use
        """
        super().__init__(matcher=matcher)
        
        # Initialize insurance-specific patterns and contexts
        self._initialize_patterns()
    
    def _initialize_patterns(self):
        """Initialize insurance-specific patterns and contexts."""
        # Direct insurance keywords
        self.direct_keywords = {
            'INSU': [
                'insurance premium', 'insurance payment', 'policy premium',
                'insurance policy', 'insurance coverage', 'insurance renewal',
                'insurance claim', 'insurance settlement', 'insurance payout',
                'insurance reimbursement', 'insurance refund', 'insurance fee',
                'insurance contribution', 'insurance installment', 'insurance deposit',
                'insurance subscription', 'insurance dues', 'insurance charge',
                'insurance bill', 'insurance invoice', 'insurance receipt',
                'life insurance', 'health insurance', 'car insurance',
                'auto insurance', 'vehicle insurance', 'home insurance',
                'property insurance', 'liability insurance', 'travel insurance',
                'business insurance', 'commercial insurance', 'professional insurance'
            ]
        }
        
        # Semantic context patterns for insurance
        self.context_patterns = [
            {
                'purpose_code': 'INSU',
                'keywords': ['insurance', 'premium'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['insurance', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['policy', 'premium'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['insurance', 'policy'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['insurance', 'coverage'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['insurance', 'renewal'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['insurance', 'claim'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['insurance', 'settlement'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['insurance', 'payout'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['insurance', 'reimbursement'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['insurance', 'refund'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['insurance', 'fee'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['insurance', 'contribution'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['insurance', 'installment'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['insurance', 'deposit'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['insurance', 'subscription'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['insurance', 'dues'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['insurance', 'charge'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['insurance', 'bill'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['insurance', 'invoice'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['insurance', 'receipt'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['life', 'insurance'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['health', 'insurance'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['car', 'insurance'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['auto', 'insurance'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['vehicle', 'insurance'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['home', 'insurance'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['property', 'insurance'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['liability', 'insurance'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['travel', 'insurance'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['business', 'insurance'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['commercial', 'insurance'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'INSU',
                'keywords': ['professional', 'insurance'],
                'proximity': 3,
                'weight': 0.9
            }
        ]
        
        # Insurance-related terms for semantic similarity
        self.semantic_terms = [
            {'purpose_code': 'INSU', 'term': 'insurance', 'threshold': 0.7, 'weight': 1.0},
            {'purpose_code': 'INSU', 'term': 'premium', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'INSU', 'term': 'policy', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'INSU', 'term': 'coverage', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'INSU', 'term': 'renewal', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'INSU', 'term': 'claim', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'INSU', 'term': 'settlement', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'INSU', 'term': 'payout', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'INSU', 'term': 'reimbursement', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'INSU', 'term': 'refund', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'INSU', 'term': 'contribution', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'INSU', 'term': 'installment', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'INSU', 'term': 'deposit', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'INSU', 'term': 'subscription', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'INSU', 'term': 'dues', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'INSU', 'term': 'charge', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'INSU', 'term': 'bill', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'INSU', 'term': 'invoice', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'INSU', 'term': 'receipt', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'INSU', 'term': 'insurer', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'INSU', 'term': 'insured', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'INSU', 'term': 'underwriter', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'INSU', 'term': 'policyholder', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'INSU', 'term': 'beneficiary', 'threshold': 0.7, 'weight': 0.8}
        ]
        
        # Negative indicators (not insurance)
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
        Enhance classification for insurance-related transactions.
        
        Args:
            result: Initial classification result
            narration: Transaction narration
            message_type: Optional message type
            
        Returns:
            dict: Enhanced classification result
        """
        logger.debug(f"Insurance enhancer called with narration: {narration}")
        
        # First, check for high confidence classifications that should not be overridden
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)
        
        # Don't override high confidence classifications
        if confidence >= 0.95:
            logger.debug(f"Not overriding high confidence classification: {purpose_code} ({confidence})")
            return result
        
        narration_lower = narration.lower()
        
        # Check for negative indicators
        for indicator in self.negative_indicators:
            if indicator.lower() in narration_lower:
                logger.debug(f"Negative indicator found: {indicator}")
                # This is clearly not insurance-related
                return result
        
        # Call the base implementation first
        enhanced_result = super().enhance_classification(result, narration, message_type)
        
        # If the base implementation changed something, return it
        if enhanced_result != result:
            # Ensure category purpose code is set to INSU for insurance
            if enhanced_result.get('purpose_code') == "INSU":
                enhanced_result['category_purpose_code'] = "INSU"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "insurance_category_mapping"
            return enhanced_result
        
        # Check if we should override the current classification
        if self.should_override_classification(result, narration):
            logger.info(f"Overriding {purpose_code} with INSU based on context analysis")
            enhanced_result = self._create_enhanced_result(result, 'INSU', 0.85, "Context analysis override")
            
            # Ensure category purpose code is set to INSU for insurance
            enhanced_result['category_purpose_code'] = "INSU"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "insurance_category_mapping"
            
            return enhanced_result
        
        # Message type specific considerations
        if message_type == "MT103":
            # MT103 is commonly used for insurance payments
            if any(term in narration_lower for term in ['insurance', 'premium', 'policy', 'coverage']):
                logger.info(f"MT103 insurance context detected")
                enhanced_result = self._create_enhanced_result(result, 'INSU', 0.85, "MT103 insurance context")
                
                # Ensure category purpose code is set to INSU for insurance
                enhanced_result['category_purpose_code'] = "INSU"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "insurance_category_mapping"
                
                return enhanced_result
        
        # No insurance pattern detected
        logger.debug("No insurance pattern detected")
        return result
    
    def should_override_classification(self, result, narration):
        """
        Determine if insurance classification should override existing classification.
        
        Args:
            result: Current classification result
            narration: Transaction narration
            
        Returns:
            bool: True if should override
        """
        narration_lower = narration.lower()
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)
        
        # Check for strong insurance context
        insurance_terms = ['insurance', 'premium', 'policy', 'coverage', 'renewal', 'claim', 'settlement', 'payout', 'reimbursement', 'refund']
        insurance_count = sum(1 for term in insurance_terms if term in narration_lower)
        
        # If multiple insurance terms are present, likely insurance-related
        if insurance_count >= 2:
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
