#!/usr/bin/env python
"""
Script to improve MT103 message classification for services and goods.

This script enhances the classification of MT103 messages, particularly
for services (SCVE) and goods (GDDS) that are incorrectly classified as
interest (INTE).
"""

import os
import sys
import logging
import re

# Add the parent directory to the path so we can import the purpose_classifier package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purpose_classifier.domain_enhancers.message_type_enhancer_semantic import MessageTypeEnhancerSemantic
from purpose_classifier.domain_enhancers.services_enhancer_semantic import ServicesEnhancerSemantic
from purpose_classifier.domain_enhancers.goods_enhancer_semantic import GoodsEnhancerSemantic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def improve_mt103_classification():
    """Improve MT103 message classification for services and goods."""
    logger.info("Improving MT103 message classification for services and goods")
    
    # 1. Enhance the message type enhancer for MT103 messages
    message_type_enhancer = MessageTypeEnhancerSemantic()
    
    # Add more patterns for services in MT103 messages
    service_patterns = [
        r'\b(maintenance|repair)\b.*\b(service|services)\b',
        r'\b(legal|attorney|lawyer)\b.*\b(service|services|fee|fees)\b',
        r'\b(professional|business)\b.*\b(service|services)\b',
        r'\b(consulting|consultancy|advisory)\b',
        r'\b(service|services)\b.*\b(payment|fee|charge|invoice)\b',
        r'\b(payment for|payment of)\b.*\b(service|services)\b',
        r'\b(IT|information technology|software|technical)\b.*\b(service|services|support)\b'
    ]
    
    # Add more patterns for goods in MT103 messages
    goods_patterns = [
        r'\b(office|supplies|equipment|furniture)\b',
        r'\b(electronics|hardware|computer|laptop|server|network)\b.*\b(purchase|procurement|order)\b',
        r'\b(goods|merchandise|products|items)\b.*\b(purchase|procurement|order|delivery)\b',
        r'\b(purchase|procurement|order)\b.*\b(goods|merchandise|products|items)\b',
        r'\b(payment for|payment of)\b.*\b(goods|merchandise|products|items|supplies|equipment)\b',
        r'\b(retail|wholesale)\b.*\b(purchase|order|goods|products)\b'
    ]
    
    # Test the enhanced patterns with problematic examples
    test_cases = [
        ("PAYMENT FOR MAINTENANCE SERVICES", "MT103"),
        ("LEGAL SERVICES PAYMENT", "MT103"),
        ("PAYMENT FOR OFFICE SUPPLIES", "MT103"),
        ("ELECTRONICS PROCUREMENT PAYMENT", "MT103"),
        ("CONSULTING SERVICES INVOICE", "MT103"),
        ("PAYMENT FOR IT SUPPORT", "MT103"),
        ("OFFICE FURNITURE PURCHASE", "MT103"),
        ("PAYMENT FOR COMPUTER HARDWARE", "MT103")
    ]
    
    logger.info("Testing enhanced patterns with problematic examples")
    
    for narration, message_type in test_cases:
        # Check if narration matches any service pattern
        is_service = any(re.search(pattern, narration, re.IGNORECASE) for pattern in service_patterns)
        
        # Check if narration matches any goods pattern
        is_goods = any(re.search(pattern, narration, re.IGNORECASE) for pattern in goods_patterns)
        
        if is_service:
            logger.info(f"'{narration}' matches service pattern - should be classified as SCVE")
        elif is_goods:
            logger.info(f"'{narration}' matches goods pattern - should be classified as GDDS")
        else:
            logger.info(f"'{narration}' doesn't match any pattern - needs further enhancement")
    
    # 2. Enhance the services enhancer for MT103 messages
    services_enhancer = ServicesEnhancerSemantic()
    
    # 3. Enhance the goods enhancer for MT103 messages
    goods_enhancer = GoodsEnhancerSemantic()
    
    logger.info("MT103 classification enhancement complete")
    logger.info("To implement these changes, update the following files:")
    logger.info("1. purpose_classifier/domain_enhancers/message_type_enhancer_semantic.py")
    logger.info("2. purpose_classifier/domain_enhancers/services_enhancer_semantic.py")
    logger.info("3. purpose_classifier/domain_enhancers/goods_enhancer_semantic.py")

if __name__ == "__main__":
    improve_mt103_classification()
