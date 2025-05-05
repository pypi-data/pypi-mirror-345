"""
Semantic Property Purchase Enhancer for Purpose Code Classification.

This module provides a specialized enhancer for property purchase-related transactions,
using semantic pattern matching to identify property purchases with high accuracy.
"""

import logging
import re
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer

logger = logging.getLogger(__name__)

class PropertyPurchaseEnhancerSemantic(SemanticEnhancer):
    """
    Specialized enhancer for property purchase-related transactions.
    
    Uses semantic pattern matching to identify property purchases
    with high accuracy and confidence.
    """
    
    def __init__(self, matcher=None):
        """
        Initialize with optional matcher.
        
        Args:
            matcher: Optional SemanticPatternMatcher instance to use
        """
        super().__init__(matcher=matcher)
        
        # Initialize property purchase-specific patterns and contexts
        self._initialize_patterns()
    
    def _initialize_patterns(self):
        """Initialize semantic patterns and contexts for property purchases."""
        # Direct keywords with purpose codes
        self.direct_keywords = {
            'PPTI': [
                'property purchase',
                'real estate purchase',
                'house purchase',
                'apartment purchase',
                'condo purchase',
                'home purchase',
                'buying property',
                'buying real estate',
                'buying house',
                'buying apartment',
                'buying condo',
                'buying home',
                'property acquisition',
                'real estate acquisition',
                'house acquisition',
                'apartment acquisition',
                'condo acquisition',
                'home acquisition',
                'purchase of property',
                'purchase of real estate',
                'purchase of house',
                'purchase of apartment',
                'purchase of condo',
                'purchase of home',
                'acquisition of property',
                'acquisition of real estate',
                'acquisition of house',
                'acquisition of apartment',
                'acquisition of condo',
                'acquisition of home',
                'down payment',
                'earnest money',
                'closing costs',
                'escrow payment',
                'property settlement',
                'real estate closing',
                'house closing',
                'apartment closing',
                'condo closing',
                'home closing'
            ],
            'LOAN': [
                'mortgage loan',
                'home loan',
                'property loan',
                'real estate loan',
                'house loan',
                'apartment loan',
                'condo loan',
                'mortgage payment',
                'home equity loan',
                'heloc',
                'second mortgage',
                'reverse mortgage',
                'mortgage refinance',
                'loan refinance',
                'mortgage application',
                'loan application',
                'mortgage approval',
                'loan approval',
                'mortgage processing',
                'loan processing',
                'mortgage origination',
                'loan origination',
                'mortgage closing',
                'loan closing'
            ]
        }
        
        # Semantic context patterns
        self.property_purchase_contexts = [
            # Property purchase contexts
            {'terms': ['property', 'purchase'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['real estate', 'purchase'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['house', 'purchase'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['apartment', 'purchase'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['condo', 'purchase'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['home', 'purchase'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['property', 'buy'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['real estate', 'buy'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['house', 'buy'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['apartment', 'buy'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['condo', 'buy'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['home', 'buy'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['property', 'acquisition'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['real estate', 'acquisition'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['house', 'acquisition'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['apartment', 'acquisition'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['condo', 'acquisition'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['home', 'acquisition'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['down', 'payment'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['earnest', 'money'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['closing', 'costs'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['escrow', 'payment'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['property', 'settlement'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['real estate', 'closing'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['house', 'closing'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['apartment', 'closing'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['condo', 'closing'], 'proximity': 5, 'weight': 1.0},
            {'terms': ['home', 'closing'], 'proximity': 5, 'weight': 1.0}
        ]
        
        self.mortgage_loan_contexts = [
            # Mortgage loan contexts
            {'terms': ['mortgage', 'loan'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['home', 'loan'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['property', 'loan'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['real estate', 'loan'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['house', 'loan'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['apartment', 'loan'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['condo', 'loan'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['mortgage', 'payment'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['home equity', 'loan'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['second', 'mortgage'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['reverse', 'mortgage'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['mortgage', 'refinance'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['loan', 'refinance'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['mortgage', 'application'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['loan', 'application'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['mortgage', 'approval'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['loan', 'approval'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['mortgage', 'processing'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['loan', 'processing'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['mortgage', 'origination'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['loan', 'origination'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['mortgage', 'closing'], 'proximity': 2, 'weight': 1.0},
            {'terms': ['loan', 'closing'], 'proximity': 2, 'weight': 1.0}
        ]
        
        # Combine all context patterns
        self.context_patterns = self.property_purchase_contexts + self.mortgage_loan_contexts
        
        # Semantic terms for similarity matching
        self.semantic_terms = [
            # Property purchase terms
            {"term": "property", "purpose_code": "PPTI", "threshold": 0.7, "weight": 1.0},
            {"term": "real estate", "purpose_code": "PPTI", "threshold": 0.7, "weight": 1.0},
            {"term": "house", "purpose_code": "PPTI", "threshold": 0.7, "weight": 0.9},
            {"term": "apartment", "purpose_code": "PPTI", "threshold": 0.7, "weight": 0.9},
            {"term": "condo", "purpose_code": "PPTI", "threshold": 0.7, "weight": 0.9},
            {"term": "condominium", "purpose_code": "PPTI", "threshold": 0.7, "weight": 0.9},
            {"term": "home", "purpose_code": "PPTI", "threshold": 0.7, "weight": 0.9},
            {"term": "purchase", "purpose_code": "PPTI", "threshold": 0.7, "weight": 0.8},
            {"term": "buy", "purpose_code": "PPTI", "threshold": 0.7, "weight": 0.8},
            {"term": "acquisition", "purpose_code": "PPTI", "threshold": 0.7, "weight": 0.8},
            {"term": "closing", "purpose_code": "PPTI", "threshold": 0.7, "weight": 0.8},
            {"term": "settlement", "purpose_code": "PPTI", "threshold": 0.7, "weight": 0.8},
            {"term": "escrow", "purpose_code": "PPTI", "threshold": 0.7, "weight": 0.8},
            {"term": "down payment", "purpose_code": "PPTI", "threshold": 0.7, "weight": 0.9},
            {"term": "earnest money", "purpose_code": "PPTI", "threshold": 0.7, "weight": 0.9},
            {"term": "deposit", "purpose_code": "PPTI", "threshold": 0.7, "weight": 0.7},
            
            # Mortgage loan terms
            {"term": "mortgage", "purpose_code": "LOAN", "threshold": 0.7, "weight": 1.0},
            {"term": "loan", "purpose_code": "LOAN", "threshold": 0.7, "weight": 0.8},
            {"term": "refinance", "purpose_code": "LOAN", "threshold": 0.7, "weight": 0.9},
            {"term": "home equity", "purpose_code": "LOAN", "threshold": 0.7, "weight": 0.9},
            {"term": "heloc", "purpose_code": "LOAN", "threshold": 0.7, "weight": 0.9},
            {"term": "second mortgage", "purpose_code": "LOAN", "threshold": 0.7, "weight": 0.9},
            {"term": "reverse mortgage", "purpose_code": "LOAN", "threshold": 0.7, "weight": 0.9}
        ]
        
        # Negative indicators (terms that suggest it's NOT a property purchase)
        self.negative_indicators = [
            'rent payment',
            'rental payment',
            'lease payment',
            'property tax',
            'real estate tax',
            'property insurance',
            'homeowners insurance',
            'home insurance',
            'property management',
            'property maintenance',
            'property repair',
            'home repair',
            'home improvement',
            'renovation',
            'remodeling'
        ]
    
    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification for property purchase-related transactions.
        
        Args:
            result: Initial classification result
            narration: Transaction narration
            message_type: Optional message type
            
        Returns:
            dict: Enhanced classification result
        """
        logger.debug(f"Property purchase enhancer called with narration: {narration}")
        
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
                # This is clearly not a property purchase
                return result
        
        # Call the base implementation first
        enhanced_result = super().enhance_classification(result, narration, message_type)
        
        # If the base implementation changed something, return it
        if enhanced_result != result:
            # Ensure category purpose code is set appropriately
            if enhanced_result.get('purpose_code') == "PPTI":
                enhanced_result['category_purpose_code'] = "PPTI"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "property_purchase_category_mapping"
                
                # Add additional information for better debugging
                enhanced_result['property_purchase_detected'] = True
                
                # Check for specific property purchase types
                if any(term in narration_lower for term in ['down payment', 'deposit', 'earnest money']):
                    enhanced_result['property_purchase_type'] = 'down_payment'
                elif any(term in narration_lower for term in ['closing', 'settlement', 'escrow']):
                    enhanced_result['property_purchase_type'] = 'closing'
                else:
                    enhanced_result['property_purchase_type'] = 'general_purchase'
            elif enhanced_result.get('purpose_code') == "LOAN":
                enhanced_result['category_purpose_code'] = "LOAN"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "mortgage_loan_category_mapping"
                
                # Add additional information for better debugging
                enhanced_result['mortgage_loan_detected'] = True
                
                # Check for specific mortgage loan types
                if 'refinance' in narration_lower or 'refinancing' in narration_lower:
                    enhanced_result['mortgage_loan_type'] = 'refinance'
                elif 'equity' in narration_lower or 'heloc' in narration_lower:
                    enhanced_result['mortgage_loan_type'] = 'home_equity'
                elif 'payment' in narration_lower or 'repayment' in narration_lower or 'installment' in narration_lower:
                    enhanced_result['mortgage_loan_type'] = 'payment'
                else:
                    enhanced_result['mortgage_loan_type'] = 'general_mortgage'
            
            return enhanced_result
        
        # Check for property purchase context
        context_score = self.context_match(narration, self.property_purchase_contexts)
        if context_score >= 0.7:
            logger.info(f"Property purchase context match with score: {context_score:.2f}")
            enhanced_result = self._create_enhanced_result(result, 'PPTI', min(0.95, context_score), 
                                                         f"Property purchase context match with score: {context_score:.2f}")
            
            # Ensure category purpose code is set to PPTI for property purchase
            enhanced_result['category_purpose_code'] = "PPTI"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "property_purchase_category_mapping"
            
            # Add additional information for better debugging
            enhanced_result['property_purchase_detected'] = True
            
            # Check for specific property purchase types
            if any(term in narration_lower for term in ['down payment', 'deposit', 'earnest money']):
                enhanced_result['property_purchase_type'] = 'down_payment'
            elif any(term in narration_lower for term in ['closing', 'settlement', 'escrow']):
                enhanced_result['property_purchase_type'] = 'closing'
            else:
                enhanced_result['property_purchase_type'] = 'general_purchase'
            
            return enhanced_result
        
        # Check for mortgage loan context
        context_score = self.context_match(narration, self.mortgage_loan_contexts)
        if context_score >= 0.7:
            logger.info(f"Mortgage loan context match with score: {context_score:.2f}")
            enhanced_result = self._create_enhanced_result(result, 'LOAN', min(0.95, context_score), 
                                                         f"Mortgage loan context match with score: {context_score:.2f}")
            
            # Ensure category purpose code is set to LOAN for mortgage loan
            enhanced_result['category_purpose_code'] = "LOAN"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "mortgage_loan_category_mapping"
            
            # Add additional information for better debugging
            enhanced_result['mortgage_loan_detected'] = True
            
            # Check for specific mortgage loan types
            if 'refinance' in narration_lower or 'refinancing' in narration_lower:
                enhanced_result['mortgage_loan_type'] = 'refinance'
            elif 'equity' in narration_lower or 'heloc' in narration_lower:
                enhanced_result['mortgage_loan_type'] = 'home_equity'
            elif 'payment' in narration_lower or 'repayment' in narration_lower or 'installment' in narration_lower:
                enhanced_result['mortgage_loan_type'] = 'payment'
            else:
                enhanced_result['mortgage_loan_type'] = 'general_mortgage'
            
            return enhanced_result
        
        # Message type specific considerations
        if message_type == "MT103":
            # MT103 is commonly used for property purchases
            if any(term in narration_lower for term in ['property', 'real estate', 'house', 'apartment', 'condo', 'home']):
                if any(term in narration_lower for term in ['purchase', 'buy', 'acquisition', 'closing', 'settlement', 'escrow', 'down payment', 'earnest money']):
                    logger.info(f"MT103 property purchase context detected")
                    enhanced_result = self._create_enhanced_result(result, 'PPTI', 0.85, "MT103 property purchase context")
                    
                    # Ensure category purpose code is set to PPTI for property purchase
                    enhanced_result['category_purpose_code'] = "PPTI"
                    enhanced_result['category_confidence'] = 0.99
                    enhanced_result['category_enhancement_applied'] = "property_purchase_category_mapping"
                    
                    # Add additional information for better debugging
                    enhanced_result['property_purchase_detected'] = True
                    
                    # Check for specific property purchase types
                    if any(term in narration_lower for term in ['down payment', 'deposit', 'earnest money']):
                        enhanced_result['property_purchase_type'] = 'down_payment'
                    elif any(term in narration_lower for term in ['closing', 'settlement', 'escrow']):
                        enhanced_result['property_purchase_type'] = 'closing'
                    else:
                        enhanced_result['property_purchase_type'] = 'general_purchase'
                    
                    return enhanced_result
                elif any(term in narration_lower for term in ['mortgage', 'loan', 'refinance', 'equity', 'heloc']):
                    logger.info(f"MT103 mortgage loan context detected")
                    enhanced_result = self._create_enhanced_result(result, 'LOAN', 0.85, "MT103 mortgage loan context")
                    
                    # Ensure category purpose code is set to LOAN for mortgage loan
                    enhanced_result['category_purpose_code'] = "LOAN"
                    enhanced_result['category_confidence'] = 0.99
                    enhanced_result['category_enhancement_applied'] = "mortgage_loan_category_mapping"
                    
                    # Add additional information for better debugging
                    enhanced_result['mortgage_loan_detected'] = True
                    
                    # Check for specific mortgage loan types
                    if 'refinance' in narration_lower or 'refinancing' in narration_lower:
                        enhanced_result['mortgage_loan_type'] = 'refinance'
                    elif 'equity' in narration_lower or 'heloc' in narration_lower:
                        enhanced_result['mortgage_loan_type'] = 'home_equity'
                    elif 'payment' in narration_lower or 'repayment' in narration_lower or 'installment' in narration_lower:
                        enhanced_result['mortgage_loan_type'] = 'payment'
                    else:
                        enhanced_result['mortgage_loan_type'] = 'general_mortgage'
                    
                    return enhanced_result
        
        # No property purchase or mortgage loan pattern detected
        logger.debug("No property purchase or mortgage loan pattern detected")
        return result
    
    def _create_enhanced_result(self, original_result, purpose_code, confidence, reason):
        """
        Create an enhanced result with the given purpose code and confidence.
        
        Args:
            original_result: The original classification result
            purpose_code: The enhanced purpose code
            confidence: The confidence score
            reason: The reason for enhancement
            
        Returns:
            dict: Enhanced classification result
        """
        # Create a copy of the original result
        result = original_result.copy()
        
        # Update with enhanced values
        result['purpose_code'] = purpose_code
        result['confidence'] = confidence
        
        # Add enhancement metadata
        result['enhanced'] = True
        result['enhancement_applied'] = 'property_purchase_enhancer_semantic'
        result['enhanced'] = True
        result['reason'] = reason
        result['original_purpose_code'] = original_result.get('purpose_code')
        result['original_confidence'] = original_result.get('confidence')
        
        return result
