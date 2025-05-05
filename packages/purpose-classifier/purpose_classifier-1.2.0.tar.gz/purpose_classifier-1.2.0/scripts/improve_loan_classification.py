#!/usr/bin/env python
"""
Script to improve LOAN vs LOAR classification.

This script enhances the classification of loan-related transactions,
distinguishing between loan disbursements (LOAN) and loan repayments (LOAR).
"""

import os
import sys
import logging
import re

# Add the parent directory to the path so we can import the purpose_classifier package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purpose_classifier.domain_enhancers.targeted_enhancer_semantic import TargetedEnhancer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def improve_loan_classification():
    """Improve LOAN vs LOAR classification."""
    logger.info("Improving LOAN vs LOAR classification")
    
    # 1. Enhance the targeted enhancer for loan-related transactions
    targeted_enhancer = TargetedEnhancer()
    
    # Define clearer patterns for loan disbursements
    loan_disbursement_patterns = [
        r'\b(loan|credit)\b.*\b(disbursement|disbursal|drawdown|advance|funding|proceeds|payout)\b',
        r'\b(disbursement|disbursal|drawdown|advance|funding|proceeds|payout)\b.*\b(loan|credit)\b',
        r'\b(new|initial)\b.*\b(loan|credit|mortgage|facility)\b',
        r'\b(loan|credit|mortgage|facility)\b.*\b(approval|approved|granted|issued)\b',
        r'\b(loan|credit)\b.*\b(amount|principal|fund|money)\b',
        r'\b(loan|credit)\b.*\b(transfer|deposit|payment)\b.*\b(to you|to your|to account|to the account)\b',
        r'\b(loan|credit)\b.*\b(release|released)\b'
    ]
    
    # Define clearer patterns for loan repayments
    loan_repayment_patterns = [
        r'\b(loan|credit|mortgage|facility)\b.*\b(repayment|payment|installment|instalment|settlement|payoff)\b',
        r'\b(repayment|payment|installment|instalment|settlement|payoff)\b.*\b(loan|credit|mortgage|facility)\b',
        r'\b(monthly|quarterly|annual|regular|scheduled)\b.*\b(loan|credit|mortgage)\b.*\b(payment|installment|instalment)\b',
        r'\b(loan|credit|mortgage)\b.*\b(payment|installment|instalment)\b.*\b(due|schedule|scheduled)\b',
        r'\b(principal|interest)\b.*\b(payment|repayment)\b',
        r'\b(payment|repayment)\b.*\b(principal|interest)\b',
        r'\b(loan|credit)\b.*\b(payment|transfer|withdrawal)\b.*\b(from you|from your|from account|from the account)\b'
    ]
    
    # Test the enhanced patterns with example narrations
    test_cases = [
        # Loan disbursement examples
        ("Loan disbursement for home purchase", "LOAN"),
        ("Credit facility drawdown", "LOAN"),
        ("New loan approved and transferred to your account", "LOAN"),
        ("Mortgage loan proceeds", "LOAN"),
        ("Loan amount transfer to account", "LOAN"),
        ("Initial loan funding", "LOAN"),
        ("Loan principal release", "LOAN"),
        
        # Loan repayment examples
        ("Loan repayment for May 2025", "LOAR"),
        ("Monthly mortgage payment", "LOAR"),
        ("Credit card payment", "LOAR"),
        ("Loan installment due", "LOAR"),
        ("Principal and interest payment", "LOAR"),
        ("Scheduled loan payment", "LOAR"),
        ("Loan settlement final payment", "LOAR")
    ]
    
    logger.info("Testing enhanced patterns with example narrations")
    
    for narration, expected_code in test_cases:
        # Check if narration matches any loan disbursement pattern
        is_disbursement = any(re.search(pattern, narration, re.IGNORECASE) for pattern in loan_disbursement_patterns)
        
        # Check if narration matches any loan repayment pattern
        is_repayment = any(re.search(pattern, narration, re.IGNORECASE) for pattern in loan_repayment_patterns)
        
        if is_disbursement and not is_repayment:
            predicted_code = "LOAN"
        elif is_repayment and not is_disbursement:
            predicted_code = "LOAR"
        elif is_disbursement and is_repayment:
            # If both match, use more specific logic
            # For example, check which pattern has more matches or higher confidence
            disbursement_count = sum(1 for pattern in loan_disbursement_patterns if re.search(pattern, narration, re.IGNORECASE))
            repayment_count = sum(1 for pattern in loan_repayment_patterns if re.search(pattern, narration, re.IGNORECASE))
            
            if disbursement_count > repayment_count:
                predicted_code = "LOAN"
            else:
                predicted_code = "LOAR"
        else:
            predicted_code = "Unknown"
        
        if predicted_code == expected_code:
            logger.info(f"✓ '{narration}' correctly classified as {predicted_code}")
        else:
            logger.info(f"✗ '{narration}' incorrectly classified as {predicted_code}, expected {expected_code}")
    
    logger.info("LOAN vs LOAR classification enhancement complete")
    logger.info("To implement these changes, update the following file:")
    logger.info("1. purpose_classifier/domain_enhancers/targeted_enhancer_semantic.py")

if __name__ == "__main__":
    improve_loan_classification()
