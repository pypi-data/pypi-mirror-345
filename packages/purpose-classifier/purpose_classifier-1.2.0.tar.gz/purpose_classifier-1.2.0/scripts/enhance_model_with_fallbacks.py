#!/usr/bin/env python3
"""
Enhance the combined model with fallback rules for low-confidence predictions.

This script adds rule-based fallbacks for cases where the model has low confidence:
1. Office supplies and business expenses (GDDS vs HLTX)
2. Account transfers and withdrawals (CASH vs HLTX)
3. Investment-related transactions (INVS vs SCVE)
4. Improved category purpose code mapping
5. Targeted enhancers for specific problematic cases (LOAN vs LOAR, VATX vs TAXS, SSBE vs GBEN, SCVE vs SERV)
6. Context-aware enhancers that consider message type (MT103, MT202, MT202COV, MT205, MT205COV)
7. Advanced message type enhancer with specific patterns for different message types
8. Special case handling for salary transfers, social welfare payments, and letters of credit
9. Pattern-based enhancers for specific transaction types
10. Enhanced handling for bond and treasury transactions
11. Improved confidence for MT202 and MT202COV messages
"""

import os
import sys
import joblib
import argparse
import json
import numpy as np
import pandas as pd
from datetime import datetime
import re

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Enhance the combined model with fallback rules')

    parser.add_argument('--input-model', type=str, default='models/combined_model.pkl',
                        help='Path to the input model')

    parser.add_argument('--output-model', type=str, default='models/enhanced_combined_model.pkl',
                        help='Path to save the enhanced model')

    parser.add_argument('--purpose-codes', type=str, default='data/purpose_codes.json',
                        help='Path to the purpose codes JSON file')

    parser.add_argument('--category-purpose-codes', type=str, default='data/category_purpose_codes.json',
                        help='Path to the category purpose codes JSON file')

    return parser.parse_args()

def load_model(model_path):
    """Load the model from disk"""
    try:
        print(f"Loading model from {model_path}")
        model_package = joblib.load(model_path)
        print(f"Model loaded successfully")
        return model_package
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return None

def load_purpose_codes(purpose_codes_path):
    """Load purpose codes from JSON file"""
    try:
        with open(purpose_codes_path, 'r') as f:
            purpose_codes = json.load(f)
        print(f"Loaded {len(purpose_codes)} purpose codes")
        return purpose_codes
    except Exception as e:
        print(f"Error loading purpose codes: {str(e)}")
        return {}

def enhance_model_with_fallbacks(model_package, purpose_codes, category_purpose_codes):
    """Enhance the model with fallback rules for low-confidence predictions"""
    # Create a copy of the model package
    enhanced_package = model_package.copy()

    # Add fallback rules
    enhanced_package['fallback_rules'] = {
        # Office supplies fallback rules
        'office_supplies_keywords': [
            'office supplies', 'stationery', 'paper', 'printer', 'ink', 'toner',
            'pens', 'notebooks', 'folders', 'binders', 'staplers', 'paper clips',
            'desk', 'chair', 'filing cabinet', 'whiteboard', 'markers'
        ],

        # Business expenses fallback rules
        'business_expenses_keywords': [
            'travel expenses', 'business trip', 'reimbursement', 'expense claim',
            'business travel', 'expenses for', 'expense report', 'travel claim',
            'business expenses'
        ],

        # Account transfer fallback rules
        'account_transfer_keywords': [
            'withdrawal from', 'transfer from', 'account withdrawal', 'transfer to',
            'funds transfer', 'account transfer', 'transfer of funds', 'moving funds',
            'withdrawal of funds', 'account to account'
        ],

        # Investment fallback rules
        'investment_keywords': [
            'investment account', 'investment in', 'purchase of stocks', 'purchase of bonds',
            'investment purchase', 'investment deposit', 'investment portfolio',
            'mutual fund', 'etf', 'index fund', 'brokerage', 'securities'
        ],

        # Confidence thresholds
        'low_confidence_threshold': 0.1,
        'medium_confidence_threshold': 0.5,
        'high_confidence_threshold': 0.8,

        # Category purpose code mappings
        'category_purpose_mappings': {
            'SALA': 'SALA',
            'DIVD': 'DIVI',
            'BONU': 'BONU',
            'COMM': 'BONU',
            'TAXS': 'TAXS',
            'INTC': 'INTC',
            'TRAD': 'TRAD',
            'LOAN': 'LOAN',
            'LOAR': 'LOAN',  # Loan Repayment maps to LOAN
            'SCVE': 'SUPP',
            'GDDS': 'SUPP',
            'INSU': 'GOVI',
            'PENS': 'PENS',
            'SSBE': 'SSBE',
            'GBEN': 'GOVT',  # Government Benefit maps to GOVT
            'SECU': 'SECU',
            'HEDG': 'HEDG',
            'VATX': 'VATX',
            'WHLD': 'WHLD',
            'EPAY': 'EPAY',
            'CCRD': 'CCRD',
            'DCRD': 'DCRD',
            'CASH': 'CASH',
            'INVS': 'SECU',
            'SERV': 'SUPP',  # Service Charge maps to SUPP
            'MSVC': 'SUPP',  # Multiple Service Types maps to SUPP
            'EDUC': 'FCOL',  # Education maps to FCOL
            'FREX': 'TRAD',  # Foreign Exchange maps to TRAD
            'ELEC': 'SUPP',  # Electricity Bill maps to SUPP
            'GASB': 'SUPP',  # Gas Bill maps to SUPP
            'PHON': 'SUPP',  # Telephone Bill maps to SUPP
            'TBIL': 'SUPP',  # Telecommunications Bill maps to SUPP
            'UBIL': 'SUPP',  # Utility Bill maps to SUPP
            'CABLE': 'SUPP', # Cable TV Bill maps to SUPP
            'NWCH': 'SUPP',  # Network Charge maps to SUPP
            'NWCM': 'SUPP',  # Network Communication maps to SUPP
            'OTLC': 'SUPP',  # Other Telecom Related Bill maps to SUPP
            'RENT': 'SUPP',  # Rent maps to SUPP
            'HLRP': 'LOAN',  # Housing Loan Repayment maps to LOAN
            'STLR': 'LOAN',  # Student Loan Repayment maps to LOAN
            'CSLP': 'LOAN',  # Car Loan Principal maps to LOAN
            'CLPR': 'LOAN',  # Car Loan Principal maps to LOAN
            'CDBL': 'CCRD',  # Credit Card Bill maps to CCRD
            'IPAY': 'SUPP',  # Bill Payment maps to SUPP
            'IVPT': 'SECU',  # Investment Payment maps to SECU
            'BKDF': 'SUPP',  # Bank Fees maps to SUPP
            'BKFX': 'TRAD',  # Bank Foreign Exchange maps to TRAD
            'RIMB': 'SUPP',  # Reimbursement maps to SUPP
            'REBT': 'SUPP',  # Rebate Payment maps to SUPP
            'TCSC': 'SUPP',  # Town Council Service Charges maps to SUPP
            'ADVA': 'SUPP',  # Advance Payment maps to SUPP
            'AIRB': 'SUPP',  # Air Charter maps to SUPP
            'BEXP': 'SUPP',  # Business Expenses maps to SUPP
            'BBSC': 'SUPP',  # Business Service Charge maps to SUPP
            'COMC': 'SUPP',  # Commercial Credit maps to SUPP
            'CPYR': 'SUPP',  # Copyright maps to SUPP
            'GDSV': 'SUPP',  # Goods and Services maps to SUPP
            'GSCB': 'SUPP',  # Purchase Sale of Goods and Services with Cash Back maps to SUPP
            'LICF': 'SUPP',  # License Fee maps to SUPP
            'POPE': 'SUPP',  # Point of Purchase Entry maps to SUPP
            'ROYA': 'SUPP',  # Royalties maps to SUPP
            'SUBS': 'SUPP',  # Subscription maps to SUPP
            'COMT': 'GOVT',  # Court Payment maps to GOVT
            'CSDB': 'CASH',  # Cash Disbursement maps to CASH
            'ACCB': 'CASH',  # Advance Against Cash Balance maps to CASH
            'BNET': 'CASH',  # Clearing House Automated Payment maps to CASH
            'CAJT': 'CASH',  # Cash Adjustment maps to CASH
            'CHAR': 'SUPP',  # Charges maps to SUPP
            'COST': 'SUPP',  # Costs maps to SUPP
            'IADD': 'SECU',  # Investment Additional Deposit maps to SECU
            'LBRI': 'GOVI',  # Labor Insurance maps to GOVI
            'LIFI': 'GOVI',  # Life Insurance maps to GOVI
            'PPTI': 'GOVI',  # Property Insurance maps to GOVI
            'RINP': 'SUPP',  # Recurring Installment Payment maps to SUPP
            'STDY': 'FCOL',  # Study maps to FCOL
            'GOVT': 'GOVT',  # Government Payment maps to GOVT
            'GVEA': 'GOVT',  # Austrian Government Payment maps to GOVT
            'GVEB': 'GOVT',  # Belgian Government Payment maps to GOVT
            'GVEF': 'GOVT',  # French Government Payment maps to GOVT
            'GVEG': 'GOVT',  # German Government Payment maps to GOVT
            'GVEH': 'GOVT',  # Greek Government Payment maps to GOVT
            'GVEI': 'GOVT',  # Irish Government Payment maps to GOVT
            'GVEL': 'GOVT',  # Luxembourg Government Payment maps to GOVT
            'GVEN': 'GOVT',  # Dutch Government Payment maps to GOVT
            'GVEP': 'GOVT',  # Portuguese Government Payment maps to GOVT
            'GVES': 'GOVT',  # Spanish Government Payment maps to GOVT
            'REFU': 'TAXS',  # Tax Refund maps to TAXS
            'RDTX': 'TAXS',  # Road Tax maps to TAXS
            'EMIGR': 'GOVT', # Emigration Payment maps to GOVT
            'NITX': 'TAXS',  # Net Income Tax maps to TAXS
            'ESTX': 'TAXS',  # Estate Tax maps to TAXS
            'HLTX': 'TAXS',  # Health Tax maps to TAXS
            'ALMY': 'SUPP',  # Alimony Payment maps to SUPP
            'ANNT': 'PENS',  # Annuity maps to PENS
            'BECH': 'GOVT',  # Child Benefit maps to GOVT
            'BENE': 'GOVT',  # Unemployment/Benefit maps to GOVT
            'PAYR': 'SALA',  # Payroll maps to SALA
            'PRCP': 'SUPP',  # Price Payment maps to SUPP
            'WTER': 'SALA',  # Worker Compensation maps to SALA
            'COLL': 'SUPP',  # Collection Payment maps to SUPP
            'XBCT': 'INTC',  # Cross-Border Credit Transfer maps to INTC
            'XBDD': 'INTC',  # Cross-Border Direct Debit maps to INTC
            'DMCT': 'INTC',  # Domestic Credit Transfer maps to INTC
            'DMDD': 'INTC',  # Domestic Direct Debit maps to INTC
            'PRME': 'SUPP',  # Property Maintenance maps to SUPP
            'DONR': 'SUPP',  # Donor Payment maps to SUPP
            'FRST': 'SUPP',  # Fundraising maps to SUPP
            'RLGN': 'SUPP',  # Religious Payment maps to SUPP
            'CDTI': 'INTE',  # Credit Transfer with Interest maps to INTE
            'DBTI': 'INTE',  # Debit Transfer with Interest maps to INTE
            'CBFF': 'SUPP',  # Capital Building maps to SUPP
            'CVCF': 'GOVT',  # Conviction Payment maps to GOVT
            'DBTC': 'SUPP',  # Debit Collection Payment maps to SUPP
            'PTSP': 'SUPP',  # Payment Terms Specification maps to SUPP
            'TELI': 'SUPP'   # Telephone Initiated Transaction maps to SUPP
        }
    }

    # Add enhanced prediction function
    enhanced_package['enhanced_predict'] = """
def enhanced_predict(self, narration, confidence, top_predictions, fallback_rules):
    \"\"\"
    Apply fallback rules for low-confidence predictions
    \"\"\"
    # Import necessary modules for targeted enhancers
    import re

    # Define patterns for targeted enhancers
    # 1. LOAN vs LOAR patterns
    loan_pattern = re.compile(r'\\b(loan|credit facility|mortgage|borrowing|lending)\\b', re.IGNORECASE)
    loan_repayment_pattern = re.compile(r'\\b(loan\\s+repayment|repayment\\s+of\\s+loan|repay.*loan|loan\\s+payment)\\b', re.IGNORECASE)

    # 2. VATX vs TAXS patterns
    vat_pattern = re.compile(r'\\b(vat|value\\s+added\\s+tax|sales\\s+tax|gst)\\b', re.IGNORECASE)
    tax_pattern = re.compile(r'\\b(tax(?!\\s+added)|income\\s+tax|corporate\\s+tax|property\\s+tax)\\b', re.IGNORECASE)

    # 3. SSBE vs GBEN patterns
    ssbe_pattern = re.compile(r'\\b(social\\s+security|ss\\s+benefit|social\\s+security\\s+benefit)\\b', re.IGNORECASE)
    gben_pattern = re.compile(r'\\b(government\\s+benefit|gov\\s+benefit|state\\s+benefit|public\\s+benefit|welfare|social\\s+welfare)\\b', re.IGNORECASE)

    # 4. SCVE vs SERV patterns
    scve_pattern = re.compile(r'\\b(service\\s+purchase|purchase\\s+of\\s+service|professional\\s+service|consulting\\s+service|fee\\s+collection\\s+for\\s+service)\\b', re.IGNORECASE)
    serv_pattern = re.compile(r'\\b(service\\s+charge|service\\s+fee|maintenance\\s+fee|account\\s+fee|processing\\s+fee)\\b', re.IGNORECASE)

    # 5. Salary patterns
    salary_pattern = re.compile(r'\\b(salary|payroll|wage|compensation|remuneration|employee\\s+payment)\\b', re.IGNORECASE)

    # 6. Investment patterns
    investment_pattern = re.compile(r'\\b(investment|securities|equity|portfolio|fund|mutual|bond)\\b', re.IGNORECASE)

    # 7. Letter of credit patterns
    letter_of_credit_pattern = re.compile(r'\\b(letter\\s+of\\s+credit|lc|l\\/c|documentary\\s+credit|irrevocable\\s+credit)\\b', re.IGNORECASE)

    # Message type patterns
    mt103_pattern = re.compile(r'MT103|103:', re.IGNORECASE)
    mt202_pattern = re.compile(r'MT202(?!COV)|202(?!COV):', re.IGNORECASE)
    mt202cov_pattern = re.compile(r'MT202COV|202COV:', re.IGNORECASE)
    mt205_pattern = re.compile(r'MT205(?!COV)|205(?!COV):', re.IGNORECASE)
    mt205cov_pattern = re.compile(r'MT205COV|205COV:', re.IGNORECASE)

    # Apply targeted enhancers first (they have highest priority)

    # 1. LOAN vs LOAR vs INTE - Always check regardless of confidence
    # Check for interest payment pattern first (highest priority)
    if re.search(r'\\b(interest\\s+payment|payment\\s+of\\s+interest|interest\\s+on)\\b', narration, re.IGNORECASE):
        return {
            'purpose_code': 'INTE',
            'confidence': 0.99,
            'fallback_applied': 'targeted_interest_payment'
        }
    # Check for loan repayment pattern
    elif loan_repayment_pattern.search(narration):
        # If narration contains "LOAN REPAYMENT" but also contains "ACCOUNT" or "ACCOUNT NUMBER",
        # it's likely a LOAN (account payment) rather than LOAR (loan repayment)
        if re.search(r'\\b(account|account\\s+number)\\b', narration, re.IGNORECASE):
            return {
                'purpose_code': 'LOAN',
                'confidence': 0.95,
                'fallback_applied': 'targeted_loan_account'
            }
        else:
            return {
                'purpose_code': 'LOAR',
                'confidence': 0.95,
                'fallback_applied': 'targeted_loan_repayment'
            }
    # Check for loan pattern (but not loan repayment or interest)
    elif loan_pattern.search(narration) and not loan_repayment_pattern.search(narration) and not re.search(r'\\b(interest)\\b', narration, re.IGNORECASE):
        return {
            'purpose_code': 'LOAN',
            'confidence': 0.95,
            'fallback_applied': 'targeted_loan'
        }

    # 2. VATX vs TAXS vs WHLD - Always check regardless of confidence
    # Check for withholding tax pattern first (highest priority)
    if re.search(r'\\b(withholding\\s+tax|with\\s+holding\\s+tax|withholding)\\b', narration, re.IGNORECASE):
        return {
            'purpose_code': 'WHLD',
            'confidence': 0.99,
            'fallback_applied': 'targeted_withholding_tax'
        }
    # Check for VAT pattern
    elif vat_pattern.search(narration):
        return {
            'purpose_code': 'VATX',
            'confidence': 0.95,
            'fallback_applied': 'targeted_vat'
        }
    # Check for tax pattern (but not VAT or withholding)
    elif tax_pattern.search(narration) and not vat_pattern.search(narration):
        return {
            'purpose_code': 'TAXS',
            'confidence': 0.95,
            'fallback_applied': 'targeted_tax'
        }

    # 3. SSBE vs GBEN - Always check regardless of confidence
    # Check for social security pattern
    if ssbe_pattern.search(narration):
        return {
            'purpose_code': 'SSBE',
            'confidence': 0.95,
            'fallback_applied': 'targeted_ssbe'
        }
    # Check for government benefit pattern (but not social security)
    elif gben_pattern.search(narration) and not ssbe_pattern.search(narration):
        return {
            'purpose_code': 'GBEN',
            'confidence': 0.95,
            'fallback_applied': 'targeted_gben'
        }

    # 4. SCVE vs SERV - Always check regardless of confidence
    # Check for service purchase pattern
    if scve_pattern.search(narration):
        return {
            'purpose_code': 'SCVE',
            'confidence': 0.95,
            'fallback_applied': 'targeted_scve'
        }
    # Check for service charge pattern (but not service purchase)
    elif serv_pattern.search(narration) and not scve_pattern.search(narration):
        return {
            'purpose_code': 'SERV',
            'confidence': 0.95,
            'fallback_applied': 'targeted_serv'
        }

    # Special case for "FEE COLLECTION FOR SERVICES"
    if "FEE COLLECTION FOR SERVICES" in narration.upper():
        return {
            'purpose_code': 'SCVE',
            'confidence': 0.99,
            'fallback_applied': 'targeted_fee_collection'
        }

    # Apply context-aware enhancers (they have medium priority)

    # Detect message type
    message_type = None
    if mt103_pattern.search(narration):
        message_type = 'MT103'
    elif mt202cov_pattern.search(narration):
        message_type = 'MT202COV'
    elif mt202_pattern.search(narration):
        message_type = 'MT202'
    elif mt205cov_pattern.search(narration):
        message_type = 'MT205COV'
    elif mt205_pattern.search(narration):
        message_type = 'MT205'

    # Check for salary pattern in narration (especially important for MT103)
    if salary_pattern.search(narration) and (message_type == 'MT103' or message_type is None):
        return {
            'purpose_code': 'SALA',
            'confidence': 0.99,
            'fallback_applied': 'message_type_salary'
        }

    # Check for social welfare pattern in narration
    if gben_pattern.search(narration) and 'WELFARE' in narration.upper():
        return {
            'purpose_code': 'GBEN',
            'confidence': 0.95,
            'fallback_applied': 'message_type_welfare'
        }

    # Check for letter of credit pattern in narration
    if letter_of_credit_pattern.search(narration):
        return {
            'purpose_code': 'ICCP',
            'confidence': 0.95,
            'fallback_applied': 'message_type_letter_of_credit'
        }

    # Get the predicted purpose code and confidence from the base model
    predicted_purpose_code = self.predict(narration)[0]

    # Apply message type-specific rules
    if message_type:
        # MT103 specific rules
        if message_type == 'MT103':
            # Check for salary pattern in MT103
            if 'SALARY' in narration.upper() or 'PAYROLL' in narration.upper():
                return {
                    'purpose_code': 'SALA',
                    'confidence': 0.99,
                    'fallback_applied': 'message_type_mt103_salary'
                }

        # MT202 specific rules
        elif message_type == 'MT202':
            # Check for interbank/liquidity pattern in MT202
            if 'INTERBANK' in narration.upper() or 'LIQUIDITY' in narration.upper() or 'NOSTRO' in narration.upper():
                return {
                    'purpose_code': 'INTC',
                    'confidence': 0.99,
                    'fallback_applied': 'message_type_mt202_interbank'
                }

            # Check for treasury pattern in MT202
            elif 'TREASURY' in narration.upper() or 'BOND' in narration.upper():
                return {
                    'purpose_code': 'TREA',
                    'confidence': 0.95,
                    'fallback_applied': 'message_type_mt202_treasury'
                }

        # MT202COV specific rules
        elif message_type == 'MT202COV':
            # Check for trade settlement pattern in MT202COV
            if 'TRADE SETTLEMENT' in narration.upper() or 'SETTLEMENT' in narration.upper():
                return {
                    'purpose_code': 'CORT',
                    'confidence': 0.99,
                    'fallback_applied': 'message_type_mt202cov_settlement'
                }

            # Check for cross-border pattern in MT202COV
            elif 'CROSS-BORDER' in narration.upper() or 'CROSS BORDER' in narration.upper():
                return {
                    'purpose_code': 'XBCT',
                    'confidence': 0.99,
                    'fallback_applied': 'message_type_mt202cov_crossborder'
                }

        # MT205 specific rules
        elif message_type == 'MT205' or message_type == 'MT205COV':
            # Check for investment pattern in MT205/MT205COV
            if investment_pattern.search(narration) or 'INVESTMENT' in narration.upper():
                return {
                    'purpose_code': 'INVS',
                    'confidence': 0.99,
                    'fallback_applied': f'message_type_{message_type.lower()}_investment'
                }

            # Check for securities pattern in MT205/MT205COV
            elif 'SECURITIES' in narration.upper() or 'SECURITY' in narration.upper():
                return {
                    'purpose_code': 'SECU',
                    'confidence': 0.99,
                    'fallback_applied': f'message_type_{message_type.lower()}_securities'
                }

            # Check for bond pattern in MT205/MT205COV
            elif 'BOND' in narration.upper():
                return {
                    'purpose_code': 'SECU',
                    'confidence': 0.95,
                    'fallback_applied': f'message_type_{message_type.lower()}_bond'
                }

        # Define preferences by message type
        mt103_preferences = {
            'SALA': 1.5,  # Salary payments are very common in MT103
            'SUPP': 1.3,  # Supplier payments are common in MT103
            'SCVE': 1.3,  # Service payments are common in MT103
            'GDDS': 1.3,  # Goods payments are common in MT103
            'TAXS': 1.3,  # Tax payments are common in MT103
            'VATX': 1.3,  # VAT payments are common in MT103
            'WHLD': 1.3,  # Withholding tax payments are common in MT103
            'LOAN': 1.3,  # Loan payments are common in MT103
            'LOAR': 1.3,  # Loan repayments are common in MT103
            'INTC': 0.7,  # Intra-company payments are less common in MT103
            'CASH': 0.7,  # Cash management transfers are less common in MT103
            'INVS': 0.7,  # Investment transfers are less common in MT103
            'SECU': 0.7   # Securities transfers are less common in MT103
        }

        mt202_preferences = {
            'INTC': 1.8,  # Intra-company payments are very common in MT202
            'CASH': 1.8,  # Cash management transfers are very common in MT202
            'TREA': 1.5,  # Treasury payments are common in MT202
            'FREX': 1.5,  # Foreign exchange is common in MT202
            'HEDG': 1.3,  # Hedging is common in MT202
            'SALA': 0.5,  # Salary payments are rare in MT202
            'SUPP': 0.5,  # Supplier payments are rare in MT202
            'SCVE': 0.5,  # Service payments are rare in MT202
            'GDDS': 0.5,  # Goods payments are rare in MT202
            'TAXS': 0.5,  # Tax payments are rare in MT202
            'VATX': 0.5,  # VAT payments are rare in MT202
            'WHLD': 0.5   # Withholding tax payments are rare in MT202
        }

        mt202cov_preferences = {
            'INTC': 1.5,  # Intra-company payments are common in MT202COV
            'CASH': 1.5,  # Cash management transfers are common in MT202COV
            'CORT': 1.8,  # Trade settlement payments are very common in MT202COV
            'TRAD': 1.5,  # Trade services are common in MT202COV
            'XBCT': 1.8,  # Cross-border credit transfers are very common in MT202COV
            'SUPP': 1.3,  # Supplier payments are common in MT202COV
            'SALA': 0.6,  # Salary payments are less common in MT202COV
            'TAXS': 0.6,  # Tax payments are less common in MT202COV
            'VATX': 0.6   # VAT payments are less common in MT202COV
        }

        mt205_preferences = {
            'INVS': 1.8,  # Investment transfers are very common in MT205
            'SECU': 1.8,  # Securities transfers are very common in MT205
            'DIVD': 1.5,  # Dividend payments are common in MT205
            'INTC': 1.3,  # Intra-company payments are common in MT205
            'HEDG': 1.3,  # Hedging is common in MT205
            'TREA': 1.5,  # Treasury payments are common in MT205
            'COMM': 1.3,  # Commission payments are common in MT205
            'SALA': 0.4,  # Salary payments are very rare in MT205
            'SUPP': 0.4,  # Supplier payments are very rare in MT205
            'SCVE': 0.4,  # Service payments are very rare in MT205
            'GDDS': 0.4,  # Goods payments are very rare in MT205
            'TAXS': 0.4,  # Tax payments are very rare in MT205
            'VATX': 0.4   # VAT payments are very rare in MT205
        }

        mt205cov_preferences = {
            'INVS': 1.8,  # Investment transfers are very common in MT205COV
            'SECU': 1.8,  # Securities transfers are very common in MT205COV
            'XBCT': 1.5,  # Cross-border credit transfers are common in MT205COV
            'INTC': 1.3,  # Intra-company payments are common in MT205COV
            'DIVD': 1.3,  # Dividend payments are common in MT205COV
            'SALA': 0.4,  # Salary payments are very rare in MT205COV
            'SUPP': 0.4,  # Supplier payments are very rare in MT205COV
            'SCVE': 0.4,  # Service payments are very rare in MT205COV
            'GDDS': 0.4   # Goods payments are very rare in MT205COV
        }

        # Get the preferences for the detected message type
        preferences = None
        if message_type == 'MT103':
            preferences = mt103_preferences
        elif message_type == 'MT202':
            preferences = mt202_preferences
        elif message_type == 'MT202COV':
            preferences = mt202cov_preferences
        elif message_type == 'MT205':
            preferences = mt205_preferences
        elif message_type == 'MT205COV':
            preferences = mt205cov_preferences

        # Apply the preferences to the confidence
        # We need to use the predicted purpose code from the model
        predicted_purpose_code = self.predict(narration)[0]

        if preferences and predicted_purpose_code in preferences:
            # Adjust confidence based on message type preference
            adjusted_confidence = confidence * preferences[predicted_purpose_code]
            # Cap the confidence at 0.99
            adjusted_confidence = min(adjusted_confidence, 0.99)

            # If the adjusted confidence is significantly higher or lower, return the enhanced result
            if abs(adjusted_confidence - confidence) > 0.1:
                return {
                    'purpose_code': predicted_purpose_code,
                    'confidence': adjusted_confidence,
                    'fallback_applied': f'message_type_{message_type.lower()}_preference'
                }

    # Apply standard fallback rules (they have lowest priority)

    # If confidence is high, return the original prediction
    if confidence >= fallback_rules['high_confidence_threshold']:
        return None

    # Convert narration to lowercase for matching
    narration_lower = narration.lower()

    # Check for office supplies keywords
    if confidence < fallback_rules['low_confidence_threshold']:
        for keyword in fallback_rules['office_supplies_keywords']:
            if keyword in narration_lower:
                return {
                    'purpose_code': 'GDDS',
                    'confidence': 0.85,
                    'fallback_applied': 'office_supplies'
                }

    # Check for business expenses keywords
    if confidence < fallback_rules['low_confidence_threshold']:
        for keyword in fallback_rules['business_expenses_keywords']:
            if keyword in narration_lower:
                return {
                    'purpose_code': 'BEXP',
                    'confidence': 0.85,
                    'fallback_applied': 'business_expenses'
                }

    # Check for account transfer keywords
    if confidence < fallback_rules['low_confidence_threshold']:
        for keyword in fallback_rules['account_transfer_keywords']:
            if keyword in narration_lower:
                return {
                    'purpose_code': 'CASH',
                    'confidence': 0.85,
                    'fallback_applied': 'account_transfer'
                }

    # Check for investment keywords
    if confidence < fallback_rules['medium_confidence_threshold']:
        for keyword in fallback_rules['investment_keywords']:
            if keyword in narration_lower:
                return {
                    'purpose_code': 'INVS',
                    'confidence': 0.85,
                    'fallback_applied': 'investment'
                }

    # If no fallback rules matched, return None
    return None
"""

    # Add enhanced category purpose code function
    enhanced_package['enhanced_category_purpose'] = """
def enhanced_category_purpose(self, purpose_code, narration, fallback_rules):
    \"\"\"
    Apply enhanced category purpose code mapping
    \"\"\"
    # Special case for education-related purpose codes - map to FCOL (Fee Collection)
    # This is a high-priority rule that should be applied before any other rules
    if purpose_code == 'EDUC':
        return 'FCOL', 0.99  # Map education to Fee Collection with very high confidence

    # Special case for "FEE COLLECTION FOR SERVICES" - map to SUPP (Supplier Payment)
    if "FEE COLLECTION FOR SERVICES" in narration.upper():
        return 'SUPP', 0.99  # Map fee collection for services to Supplier Payment with very high confidence

    # Special case for "LOAN REPAYMENT" - map to LOAN
    if "LOAN REPAYMENT" in narration.upper():
        return 'LOAN', 0.95  # Map loan repayment to Loan with high confidence

    # Special case for "VALUE ADDED TAX" - map to VATX
    if "VALUE ADDED TAX" in narration.upper() or "VAT" in narration.upper():
        return 'VATX', 0.95  # Map VAT to VATX with high confidence

    # Special case for "WITHHOLDING TAX" - map to WHLD
    if "WITHHOLDING TAX" in narration.upper() or "WITH HOLDING TAX" in narration.upper():
        return 'WHLD', 0.99  # Map withholding tax to WHLD with very high confidence

    # Special case for "INTEREST PAYMENT" - map to INTE
    if "INTEREST PAYMENT" in narration.upper() or "PAYMENT OF INTEREST" in narration.upper() or "INTEREST ON" in narration.upper():
        return 'INTE', 0.99  # Map interest payment to INTE with very high confidence

    # Special case for "FOREIGN EXCHANGE" - map to TRAD
    if "FOREIGN EXCHANGE" in narration.upper() or "FX TRANSACTION" in narration.upper() or "FOREX" in narration.upper() or "CURRENCY EXCHANGE" in narration.upper():
        return 'TRAD', 0.95  # Map foreign exchange to TRAD with high confidence

    # Special case for utility bills - map to SUPP
    if any(keyword in narration.upper() for keyword in ["ELECTRICITY", "ELECTRIC BILL", "UTILITY BILL", "GAS BILL", "WATER BILL", "PHONE BILL", "TELEPHONE BILL"]):
        return 'SUPP', 0.95  # Map utility bills to SUPP with high confidence

    # Special case for rent - map to SUPP
    if "RENT" in narration.upper() or "RENTAL" in narration.upper():
        return 'SUPP', 0.95  # Map rent to SUPP with high confidence

    # Special case for "SOCIAL SECURITY BENEFIT" - map to SSBE
    if "SOCIAL SECURITY BENEFIT" in narration.upper() or "SOCIAL SECURITY" in narration.upper():
        return 'SSBE', 0.95  # Map social security to SSBE with high confidence

    # Special case for "SALARY TRANSFER" - map to SALA
    if "SALARY TRANSFER" in narration.upper() or "TRANSFER" in narration.upper() and "SALARY" in narration.upper():
        return 'SALA', 0.99  # Map salary transfer to SALA with very high confidence

    # Special case for "SOCIAL WELFARE PAYMENT" - map to GOVT
    if "SOCIAL WELFARE" in narration.upper() or "WELFARE PAYMENT" in narration.upper():
        return 'GOVT', 0.95  # Map social welfare to GOVT with high confidence

    # Special case for "LETTER OF CREDIT" - map to ICCP
    if "LETTER OF CREDIT" in narration.upper() or "IRREVOCABLE CREDIT" in narration.upper():
        return 'ICCP', 0.95  # Map letter of credit to ICCP with high confidence

    # Special case for "TREASURY BOND" - map to SUPP
    if "TREASURY BOND" in narration.upper() or "BOND PURCHASE" in narration.upper():
        return 'SUPP', 0.95  # Map treasury bond to SUPP with high confidence

    # Special case for MT202 messages - map to appropriate category purpose codes
    if "MT202" in narration.upper() or "202:" in narration.upper():
        if "INTERBANK" in narration.upper() or "NOSTRO" in narration.upper() or "LIQUIDITY" in narration.upper():
            return 'INTC', 0.95  # Map interbank transfers to INTC with high confidence
        elif "CASH" in narration.upper() or "POOLING" in narration.upper():
            return 'CASH', 0.95  # Map cash management to CASH with high confidence

    # Special case for MT202COV messages - map to appropriate category purpose codes
    if "MT202COV" in narration.upper() or "202COV:" in narration.upper():
        if "TRADE SETTLEMENT" in narration.upper() or "SETTLEMENT" in narration.upper():
            return 'OTHR', 0.95  # Map trade settlement to OTHR with high confidence
        elif "CROSS-BORDER" in narration.upper() or "CROSS BORDER" in narration.upper():
            return 'INTC', 0.95  # Map cross-border to INTC with high confidence

    # Special case for MT205 messages - map to appropriate category purpose codes
    if "MT205" in narration.upper() or "205:" in narration.upper():
        if "INVESTMENT" in narration.upper() or "SECURITIES" in narration.upper() or "BOND" in narration.upper():
            return 'SECU', 0.95  # Map investment to SECU with high confidence
        elif "FEE" in narration.upper() or "COMMISSION" in narration.upper():
            return 'BONU', 0.95  # Map fee/commission to BONU with high confidence

    # Use the mapping from fallback rules
    if purpose_code in fallback_rules['category_purpose_mappings']:
        category_purpose_code = fallback_rules['category_purpose_mappings'][purpose_code]
        return category_purpose_code, 0.85

    # Check narration for specific keywords
    narration_lower = narration.lower()

    # Check for bonus/commission keywords
    if 'bonus' in narration_lower or 'commission' in narration_lower:
        return 'BONU', 0.85

    # Check for salary keywords
    if 'salary' in narration_lower or 'wage' in narration_lower or 'payroll' in narration_lower or 'employee' in narration_lower and 'payment' in narration_lower:
        return 'SALA', 0.95  # Increased confidence for salary keywords

    # Check for tax keywords
    if 'tax' in narration_lower:
        return 'TAXS', 0.85

    # Check for loan keywords
    if 'loan' in narration_lower or 'mortgage' in narration_lower:
        return 'LOAN', 0.85

    # Check for investment keywords
    if 'investment' in narration_lower or 'securities' in narration_lower or 'stocks' in narration_lower or 'bonds' in narration_lower:
        return 'SECU', 0.85

    # Check for insurance keywords
    if 'insurance' in narration_lower or 'premium' in narration_lower:
        return 'GOVI', 0.85

    # Check for supplier keywords
    if 'supplier' in narration_lower or 'vendor' in narration_lower or 'purchase' in narration_lower or 'invoice' in narration_lower:
        return 'SUPP', 0.85

    # Check for interbank keywords
    if 'interbank' in narration_lower or 'nostro' in narration_lower or 'vostro' in narration_lower or 'correspondent' in narration_lower:
        return 'INTC', 0.85

    # Check for cash management keywords
    if 'cash management' in narration_lower or 'pooling' in narration_lower or 'liquidity' in narration_lower:
        return 'CASH', 0.85

    # Check for trade settlement keywords
    if 'trade settlement' in narration_lower or 'settlement' in narration_lower:
        return 'OTHR', 0.85

    # Check for cross-border keywords
    if 'cross-border' in narration_lower or 'cross border' in narration_lower or 'international wire' in narration_lower:
        return 'INTC', 0.85

    # Default to OTHR with low confidence
    return 'OTHR', 0.3
"""

    # Add metadata
    enhanced_package['enhancement_info'] = {
        'enhanced_at': datetime.now().isoformat(),
        'enhancements': [
            'Added fallback rules for low-confidence predictions',
            'Improved office supplies and business expenses classification',
            'Enhanced account transfers and withdrawals classification',
            'Improved investment-related transactions classification',
            'Enhanced category purpose code mapping',
            'Added targeted enhancers for specific problematic cases (LOAN vs LOAR, VATX vs TAXS, SSBE vs GBEN, SCVE vs SERV)',
            'Added context-aware enhancers that consider message type (MT103, MT202, MT202COV, MT205, MT205COV)',
            'Improved special case handling for "FEE COLLECTION FOR SERVICES"',
            'Enhanced category purpose code mapping for education-related purpose codes (EDUC -> FCOL)',
            'Added special case handling for "LOAN REPAYMENT", "VALUE ADDED TAX", and "SOCIAL SECURITY BENEFIT"',
            'Added high-priority pattern matching for "WITHHOLDING TAX PAYMENT" to ensure WHLD classification',
            'Added high-priority pattern matching for "INTEREST PAYMENT ON LOAN" to ensure INTE classification',
            'Enhanced category purpose code mapping for withholding tax and interest payments',
            'Added comprehensive category purpose code mappings for all ISO20022 purpose codes',
            'Added special case handling for utility bills and rent payments',
            'Added special case handling for foreign exchange transactions',
            'Added advanced message type enhancer with specific patterns for different message types',
            'Added special case handling for salary transfers to ensure SALA classification',
            'Added special case handling for social welfare payments to ensure GBEN classification',
            'Added special case handling for letters of credit to ensure ICCP classification',
            'Enhanced MT202 and MT202COV handling for interbank transfers and trade settlements',
            'Enhanced MT205 and MT205COV handling for investment and securities transactions',
            'Adjusted confidence levels based on message type appropriateness',
            'Added pattern-based enhancers for specific transaction types',
            'Enhanced handling for bond and treasury transactions',
            'Improved confidence for MT202 and MT202COV messages',
            'Added special case handling for "SALARY TRANSFER" to ensure SALA classification',
            'Added special case handling for "SOCIAL WELFARE PAYMENT" to ensure GOVT classification',
            'Added special case handling for "LETTER OF CREDIT" to ensure ICCP classification',
            'Added special case handling for "TREASURY BOND" to ensure SUPP classification',
            'Enhanced message type-specific category purpose code mappings'
        ]
    }

    return enhanced_package

def save_model(model_package, output_path):
    """Save the enhanced model to disk"""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        joblib.dump(model_package, output_path)
        print(f"Enhanced model saved to {output_path}")
        return True
    except Exception as e:
        print(f"Error saving model: {str(e)}")
        return False

def main():
    """Main function to enhance the model with fallback rules"""
    args = parse_args()

    # Load the model
    model_package = load_model(args.input_model)
    if model_package is None:
        return 1

    # Load purpose codes
    purpose_codes = load_purpose_codes(args.purpose_codes)
    category_purpose_codes = load_purpose_codes(args.category_purpose_codes)

    # Enhance the model with fallback rules
    enhanced_package = enhance_model_with_fallbacks(model_package, purpose_codes, category_purpose_codes)

    # Save the enhanced model
    if not save_model(enhanced_package, args.output_model):
        return 1

    print("\nModel enhancement completed successfully!")
    print(f"Original model: {args.input_model}")
    print(f"Enhanced model: {args.output_model}")
    print("\nEnhancements applied:")
    for enhancement in enhanced_package['enhancement_info']['enhancements']:
        print(f"- {enhancement}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
