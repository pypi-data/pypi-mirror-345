#!/usr/bin/env python
"""
Script to improve category purpose code mapping.

This script enhances the mapping between purpose codes and category purpose codes,
particularly focusing on DIVD->DIVI and SCVE->SUPP mappings.
"""

import os
import sys
import logging
import json

# Add the parent directory to the path so we can import the purpose_classifier package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purpose_classifier.utils.category_purpose_mapper import CategoryPurposeMapper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def improve_category_purpose_mapping():
    """Improve category purpose code mapping."""
    logger.info("Improving category purpose code mapping")
    
    # 1. Load the current category purpose mapper
    category_mapper = CategoryPurposeMapper()
    
    # 2. Define the improved direct mappings
    improved_mappings = {
        # Education and Fee Collection
        'EDUC': 'FCOL',  # Education to Fee Collection
        'FCOL': 'FCOL',  # Fee Collection to Fee Collection
        'STDY': 'FCOL',  # Study to Fee Collection

        # Salary and Compensation
        'SALA': 'SALA',  # Salary to Salary
        'BONU': 'SALA',  # Bonus to Salary
        'COMM': 'SALA',  # Commission to Salary
        'PENS': 'PENS',  # Pension to Pension

        # Dividend
        'DIVD': 'DIVI',  # Dividend to Dividend Income
        'DIVI': 'DIVI',  # Dividend to Dividend Income

        # Investment and Securities
        'INVS': 'SECU',  # Investment to Securities
        'SECU': 'SECU',  # Securities to Securities

        # Loans
        'LOAN': 'LOAN',  # Loan to Loan
        'LOAR': 'LOAR',  # Loan Repayment to Loan Repayment

        # Services and Goods
        'SCVE': 'SUPP',  # Services to Supplier Payment
        'GDDS': 'GDDS',  # Goods to Goods
        'SUPP': 'SUPP',  # Supplier to Supplier Payment

        # Taxes
        'TAXS': 'TAXS',  # Tax to Tax Payment
        'VATX': 'VATX',  # VAT to VAT Payment
        'WHLD': 'WHLD',  # Withholding to Withholding

        # Utilities
        'UBIL': 'UBIL',  # Utility Bill to Utility Bill
        'ELEC': 'UBIL',  # Electricity to Utility Bill
        'GASB': 'UBIL',  # Gas Bill to Utility Bill
        'WTER': 'UBIL',  # Water to Utility Bill
        'OTLC': 'UBIL',  # Other Telecom to Utility Bill
        'PHON': 'UBIL',  # Telephone to Utility Bill
        'NWCH': 'UBIL',  # Network Charge to Utility Bill

        # Trade
        'TRAD': 'TRAD',  # Trade to Trade
        'CORT': 'CORT',  # Trade Settlement to Trade Settlement

        # Treasury
        'TREA': 'TREA',  # Treasury to Treasury
        'CASH': 'CASH',  # Cash Management to Cash Management
        'INTC': 'INTC',  # Intra Company to Intra Company

        # Cards
        'CCRD': 'CCRD',  # Credit Card to Credit Card
        'DCRD': 'DCRD',  # Debit Card to Debit Card
        'ICCP': 'ICCP',  # Irrevocable Credit Card to Irrevocable Credit Card
        'IDCP': 'IDCP',  # Irrevocable Debit Card to Irrevocable Debit Card

        # Interest
        'INTE': 'INTE',  # Interest to Interest
    }
    
    # 3. Test the improved mappings with problematic cases
    test_cases = [
        # Dividend cases
        ("DIVD", "Dividend payment for Q2 2025", "DIVI"),
        ("DIVD", "Quarterly dividend distribution", "DIVI"),
        ("DIVD", "Shareholder payment for annual dividend", "DIVI"),
        
        # Services cases
        ("SCVE", "Payment for maintenance services", "SUPP"),
        ("SCVE", "Legal services payment", "SUPP"),
        ("SCVE", "Consulting services invoice", "SUPP"),
        
        # Goods cases
        ("GDDS", "Payment for office supplies", "GDDS"),
        ("GDDS", "Electronics procurement payment", "GDDS"),
        ("GDDS", "Office furniture purchase", "GDDS"),
        
        # Loan cases
        ("LOAN", "Loan disbursement for home purchase", "LOAN"),
        ("LOAR", "Loan repayment for May 2025", "LOAR"),
        
        # Other cases
        ("SALA", "Salary payment for April 2025", "SALA"),
        ("TAXS", "Tax payment for Q1 2025", "TAXS"),
        ("INTC", "Intra-company transfer", "INTC")
    ]
    
    logger.info("Testing improved category purpose code mappings")
    
    for purpose_code, narration, expected_category in test_cases:
        # Use the current mapper to get the category
        current_category = category_mapper.map_purpose_to_category(purpose_code, narration)
        
        # Get the improved category from our new mappings
        improved_category = improved_mappings.get(purpose_code, "OTHR")
        
        logger.info(f"Purpose code: {purpose_code}, Narration: '{narration}'")
        logger.info(f"  Current mapping: {current_category}")
        logger.info(f"  Improved mapping: {improved_category}")
        logger.info(f"  Expected mapping: {expected_category}")
        
        if improved_category == expected_category:
            logger.info(f"  ✓ Improved mapping matches expected")
        else:
            logger.info(f"  ✗ Improved mapping does not match expected")
        
        logger.info("")
    
    # 4. Save the improved mappings to a file for reference
    with open('improved_category_mappings.json', 'w') as f:
        json.dump(improved_mappings, f, indent=4)
    
    logger.info("Improved category purpose mappings saved to improved_category_mappings.json")
    logger.info("To implement these changes, update the following file:")
    logger.info("1. purpose_classifier/utils/category_purpose_mapper.py")

if __name__ == "__main__":
    improve_category_purpose_mapping()
