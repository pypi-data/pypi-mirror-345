"""
Semantic Goods Enhancer for Purpose Code Classification.

This module provides a specialized enhancer for goods-related transactions,
using semantic pattern matching to identify goods purchases with high accuracy.
"""

import logging
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer

logger = logging.getLogger(__name__)

class GoodsEnhancerSemantic(SemanticEnhancer):
    """
    Specialized enhancer for goods-related transactions.

    Uses semantic pattern matching to identify goods purchases
    with high accuracy and confidence.
    """

    def __init__(self, matcher=None):
        """
        Initialize with optional matcher.
        
        Args:
            matcher: Optional SemanticPatternMatcher instance to use
        """
        super().__init__(matcher=matcher)

        # Initialize goods-specific patterns and contexts
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize goods-specific patterns and contexts."""
        # Direct goods keywords
        self.direct_keywords = {
            'GDDS': [
                'purchase of goods', 'goods purchase', 'merchandise',
                'retail purchase', 'wholesale purchase', 'product purchase',
                'purchase of products', 'goods payment', 'payment for goods',
                'purchase of merchandise', 'inventory purchase', 'stock purchase',
                'equipment purchase', 'hardware purchase', 'purchase of equipment',
                'purchase of hardware', 'purchase of inventory', 'purchase of stock',
                'purchase of supplies', 'supplies purchase', 'office supplies',
                'office equipment'
            ]
        }

        # Semantic context patterns for goods
        self.context_patterns = [
            {
                'purpose_code': 'GDDS',
                'keywords': ['purchase', 'goods'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['payment', 'merchandise'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['retail', 'purchase'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['wholesale', 'purchase'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['product', 'purchase'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['inventory', 'purchase'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['stock', 'purchase'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['equipment', 'purchase'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['hardware', 'purchase'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['supplies', 'purchase'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['office', 'supplies'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['office', 'equipment'],
                'proximity': 3,
                'weight': 0.9
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['invoice', 'goods'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['invoice', 'products'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['invoice', 'merchandise'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['invoice', 'equipment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['invoice', 'hardware'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['invoice', 'supplies'],
                'proximity': 5,
                'weight': 0.8
            }
        ]

        # Goods-related terms for semantic similarity
        self.semantic_terms = [
            {'purpose_code': 'GDDS', 'term': 'goods', 'threshold': 0.7, 'weight': 1.0},
            {'purpose_code': 'GDDS', 'term': 'merchandise', 'threshold': 0.7, 'weight': 1.0},
            {'purpose_code': 'GDDS', 'term': 'product', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'GDDS', 'term': 'purchase', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'GDDS', 'term': 'retail', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'GDDS', 'term': 'wholesale', 'threshold': 0.7, 'weight': 0.9},
            {'purpose_code': 'GDDS', 'term': 'inventory', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GDDS', 'term': 'stock', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GDDS', 'term': 'equipment', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GDDS', 'term': 'hardware', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GDDS', 'term': 'supplies', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GDDS', 'term': 'office', 'threshold': 0.7, 'weight': 0.7},
            {'purpose_code': 'GDDS', 'term': 'invoice', 'threshold': 0.7, 'weight': 0.7},
            {'purpose_code': 'GDDS', 'term': 'order', 'threshold': 0.7, 'weight': 0.7},
            {'purpose_code': 'GDDS', 'term': 'shipment', 'threshold': 0.7, 'weight': 0.7},
            {'purpose_code': 'GDDS', 'term': 'delivery', 'threshold': 0.7, 'weight': 0.7},
            {'purpose_code': 'GDDS', 'term': 'electronics', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GDDS', 'term': 'furniture', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GDDS', 'term': 'clothing', 'threshold': 0.7, 'weight': 0.8},
            {'purpose_code': 'GDDS', 'term': 'food', 'threshold': 0.7, 'weight': 0.8}
        ]

        # Negative indicators (not goods)
        self.negative_indicators = [
            'service', 'consulting', 'professional service', 'maintenance',
            'repair', 'installation', 'support', 'subscription', 'license',
            'software', 'cloud', 'hosting', 'training', 'education', 'tuition',
            'loan', 'mortgage', 'interest', 'dividend', 'investment', 'securities',
            'trading', 'forex', 'fx', 'foreign exchange', 'treasury', 'interbank',
            'nostro', 'vostro', 'correspondent', 'utility', 'electricity', 'gas',
            'water', 'phone', 'telephone', 'mobile', 'internet', 'broadband',
            'cable', 'tv', 'television', 'tax', 'vat', 'gst', 'sales tax',
            'income tax', 'property tax', 'withholding tax', 'customs', 'duty',
            'tariff', 'salary', 'wage', 'payroll', 'compensation', 'bonus',
            'commission', 'pension', 'retirement', 'benefit'
        ]

    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification for goods-related transactions.

        Args:
            result: Initial classification result
            narration: Transaction narration
            message_type: Optional message type

        Returns:
            dict: Enhanced classification result
        """
        logger.debug(f"Goods enhancer called with narration: {narration}")

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
                # This is clearly not goods-related
                return result

        # Call the base implementation first
        enhanced_result = super().enhance_classification(result, narration, message_type)

        # If the base implementation changed something, return it
        if enhanced_result != result:
            # Ensure category purpose code is set to GDDS for goods
            if enhanced_result.get('purpose_code') == "GDDS":
                enhanced_result['category_purpose_code'] = "GDDS"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "goods_category_mapping"
            return enhanced_result

        # Check if we should override the current classification
        if self.should_override_classification(result, narration):
            logger.info(f"Overriding {purpose_code} with GDDS based on context analysis")
            enhanced_result = self._create_enhanced_result(result, 'GDDS', 0.85, "Context analysis override")

            # Ensure category purpose code is set to GDDS for goods
            enhanced_result['category_purpose_code'] = "GDDS"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "goods_category_mapping"

            return enhanced_result

        # Message type specific considerations
        if message_type == "MT103":
            # MT103 is commonly used for goods purchases
            # Enhanced pattern matching for MT103 goods payments
            mt103_goods_patterns = [
                'purchase', 'goods', 'merchandise', 'product', 'equipment',
                'office supplies', 'office equipment', 'computer hardware',
                'electronics', 'furniture', 'retail purchase',
                'wholesale purchase', 'product purchase',
                'equipment purchase', 'hardware purchase',
                'supplies purchase', 'inventory purchase',
                'goods payment', 'payment for goods',
                'procurement', 'order', 'retail', 'wholesale',
                'machinery', 'spare parts', 'raw materials',
                'components', 'devices', 'appliances',
                'tools', 'instruments', 'apparatus',
                'materials', 'commodities', 'items',
                'stock', 'inventory', 'supplies',
                'hardware', 'software purchase', 'equipment order'
            ]

            # Check for goods patterns in MT103 messages
            if any(pattern in narration_lower for pattern in mt103_goods_patterns):
                logger.info(f"MT103 goods context detected: {narration}")

                # Check if the current classification is INTE or SCVE (common misclassifications)
                if purpose_code == 'INTE':
                    logger.info(f"Correcting INTE misclassification to GDDS for goods-related MT103")
                    enhanced_result = self._create_enhanced_result(result, 'GDDS', 0.99, "MT103 goods correction (INTE->GDDS)")
                elif purpose_code == 'SCVE':
                    logger.info(f"Correcting SCVE misclassification to GDDS for goods-related MT103")
                    enhanced_result = self._create_enhanced_result(result, 'GDDS', 0.99, "MT103 goods correction (SCVE->GDDS)")
                else:
                    enhanced_result = self._create_enhanced_result(result, 'GDDS', 0.95, "MT103 goods context")

                # Ensure category purpose code is set to GDDS for goods
                enhanced_result['category_purpose_code'] = "GDDS"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "goods_category_mapping"

                return enhanced_result

            # Special case for "PAYMENT FOR OFFICE SUPPLIES" which is incorrectly classified as INTE
            if "office supplies" in narration_lower:
                logger.info(f"Office supplies detected in MT103: {narration}")
                enhanced_result = self._create_enhanced_result(result, 'GDDS', 0.99, "MT103 office supplies correction")
                enhanced_result['category_purpose_code'] = "GDDS"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "office_supplies_mapping_to_GDDS"
                return enhanced_result

            # Special case for "ELECTRONICS PROCUREMENT PAYMENT" which is incorrectly classified as SCVE
            if "electronics" in narration_lower and ("procurement" in narration_lower or "purchase" in narration_lower):
                logger.info(f"Electronics procurement detected in MT103: {narration}")
                enhanced_result = self._create_enhanced_result(result, 'GDDS', 0.99, "MT103 electronics procurement correction")
                enhanced_result['category_purpose_code'] = "GDDS"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "electronics_procurement_mapping_to_GDDS"
                return enhanced_result

            # Special case for "MACHINERY SUPPLY" which is incorrectly classified as SCVE
            if "machinery" in narration_lower and ("supply" in narration_lower or "purchase" in narration_lower):
                logger.info(f"Machinery supply detected in MT103: {narration}")
                enhanced_result = self._create_enhanced_result(result, 'GDDS', 0.99, "MT103 machinery supply correction")
                enhanced_result['category_purpose_code'] = "GDDS"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "machinery_supply_mapping_to_GDDS"
                return enhanced_result

            # Special case for "SPARE PARTS" which is incorrectly classified as SCVE
            if "spare parts" in narration_lower or "parts" in narration_lower:
                logger.info(f"Spare parts detected in MT103: {narration}")
                enhanced_result = self._create_enhanced_result(result, 'GDDS', 0.99, "MT103 spare parts correction")
                enhanced_result['category_purpose_code'] = "GDDS"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "spare_parts_mapping_to_GDDS"
                return enhanced_result

            # Special case for "FURNITURE" which is incorrectly classified as INTE
            if "furniture" in narration_lower:
                logger.info(f"Furniture detected in MT103: {narration}")
                enhanced_result = self._create_enhanced_result(result, 'GDDS', 0.99, "MT103 furniture correction")
                enhanced_result['category_purpose_code'] = "GDDS"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "furniture_mapping_to_GDDS"
                return enhanced_result

        # No goods pattern detected
        logger.debug("No goods pattern detected")
        return result

    def should_override_classification(self, result, narration):
        """
        Determine if goods classification should override existing classification.

        Args:
            result: Current classification result
            narration: Transaction narration

        Returns:
            bool: True if should override
        """
        narration_lower = narration.lower()
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)

        # Check for strong goods context
        goods_terms = ['purchase', 'goods', 'merchandise', 'product', 'equipment', 'hardware', 'supplies', 'inventory', 'stock']
        goods_count = sum(1 for term in goods_terms if term in narration_lower)

        # If multiple goods terms are present, likely goods-related
        if goods_count >= 2:
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
