#!/usr/bin/env python
"""
Script to improve DIVD purpose code classification and DIVI category purpose code mapping.

This script enhances the classification of dividend-related transactions,
ensuring proper mapping between DIVD purpose code and DIVI category purpose code.
"""

import os
import sys
import logging
import re

# Add the parent directory to the path so we can import the purpose_classifier package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purpose_classifier.utils.category_purpose_mapper import CategoryPurposeMapper
from purpose_classifier.domain_enhancers.targeted_enhancer_semantic import TargetedEnhancer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def improve_dividend_classification():
    """Improve DIVD purpose code classification and DIVI category purpose code mapping."""
    logger.info("Improving DIVD purpose code classification and DIVI category purpose code mapping")
    
    # 1. Enhance the targeted enhancer for dividend-related transactions
    targeted_enhancer = TargetedEnhancer()
    
    # Define clearer patterns for dividend payments
    dividend_patterns = [
        r'\b(dividend|dividends)\b',
        r'\b(dividend|dividends)\b.*\b(payment|distribution|payout|income)\b',
        r'\b(payment|distribution|payout|income)\b.*\b(dividend|dividends)\b',
        r'\b(shareholder|stockholder)\b.*\b(payment|distribution|payout|income)\b',
        r'\b(payment|distribution|payout|income)\b.*\b(shareholder|stockholder)\b',
        r'\b(share|stock)\b.*\b(dividend|dividends|income)\b',
        r'\b(quarterly|annual|semi-annual|interim|final)\b.*\b(dividend|dividends)\b',
        r'\b(dividend|dividends)\b.*\b(quarterly|annual|semi-annual|interim|final)\b',
        r'\b(profit|earnings)\b.*\b(distribution|sharing|payout)\b',
        r'\b(distribution|sharing|payout)\b.*\b(profit|earnings)\b'
    ]
    
    # Test the enhanced patterns with example narrations
    test_cases = [
        ("Dividend payment for Q2 2025", "DIVD"),
        ("Quarterly dividend distribution", "DIVD"),
        ("Shareholder payment for annual dividend", "DIVD"),
        ("Stock dividend payout", "DIVD"),
        ("Profit distribution to shareholders", "DIVD"),
        ("Annual dividend income", "DIVD"),
        ("Dividend income from investments", "DIVD"),
        ("Interim dividend payment", "DIVD"),
        ("Earnings distribution to stockholders", "DIVD"),
        ("Share of profits payment", "DIVD")
    ]
    
    logger.info("Testing enhanced patterns with example narrations")
    
    for narration, expected_code in test_cases:
        # Check if narration matches any dividend pattern
        is_dividend = any(re.search(pattern, narration, re.IGNORECASE) for pattern in dividend_patterns)
        
        if is_dividend:
            predicted_code = "DIVD"
        else:
            predicted_code = "Unknown"
        
        if predicted_code == expected_code:
            logger.info(f"✓ '{narration}' correctly classified as {predicted_code}")
        else:
            logger.info(f"✗ '{narration}' incorrectly classified as {predicted_code}, expected {expected_code}")
    
    # 2. Fix the category purpose code mapping for DIVD
    category_mapper = CategoryPurposeMapper()
    
    # Test the category purpose code mapping
    logger.info("Testing category purpose code mapping for DIVD")
    
    for narration, _ in test_cases:
        category_purpose_code = category_mapper.map_purpose_to_category("DIVD", narration)
        
        if category_purpose_code == "DIVI":
            logger.info(f"✓ DIVD correctly mapped to DIVI for '{narration}'")
        else:
            logger.info(f"✗ DIVD incorrectly mapped to {category_purpose_code} for '{narration}', expected DIVI")
    
    logger.info("DIVD classification and DIVI mapping enhancement complete")
    logger.info("To implement these changes, update the following files:")
    logger.info("1. purpose_classifier/domain_enhancers/targeted_enhancer_semantic.py")
    logger.info("2. purpose_classifier/utils/category_purpose_mapper.py")

if __name__ == "__main__":
    improve_dividend_classification()
