#!/usr/bin/env python3
"""
Fix remaining issues in the purpose code classifier.

This script updates the enhanced_predict and enhanced_category_purpose functions
to fix the remaining issues with the purpose code classifier.
"""

import os
import sys
import joblib
import argparse
from datetime import datetime

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Fix remaining issues in the purpose code classifier')

    parser.add_argument('--input-model', type=str, default='models/combined_model.pkl',
                        help='Path to the input model')

    parser.add_argument('--output-model', type=str, default='models/combined_model.pkl',
                        help='Path to save the enhanced model')

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

def save_model(model_package, model_path):
    """Save the model to disk"""
    try:
        print(f"Saving model to {model_path}")
        joblib.dump(model_package, model_path)
        print(f"Model saved to {model_path}")
        return True
    except Exception as e:
        print(f"Error saving model: {str(e)}")
        return False

def fix_enhanced_predict(model_package):
    """Fix the enhanced_predict function"""
    # Create a copy of the model package
    enhanced_package = model_package.copy()

    # Update the enhanced_predict function
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

    # 8. Treasury patterns
    treasury_pattern = re.compile(r'\\b(treasury|bond\\s+purchase|treasury\\s+bond|treasury\\s+operations)\\b', re.IGNORECASE)

    # 9. Cash management patterns
    cash_pattern = re.compile(r'\\b(cash\\s+management|cash\\s+pooling|pooling\\s+arrangement|liquidity\\s+management)\\b', re.IGNORECASE)

    # 10. Trade settlement patterns
    trade_pattern = re.compile(r'\\b(trade\\s+settlement|settlement\\s+of\\s+trade|trade\\s+services|supplier\\s+payment)\\b', re.IGNORECASE)

    # 11. Cross-border patterns
    cross_border_pattern = re.compile(r'\\b(cross\\s*-?\\s*border|international\\s+wire|overseas\\s+payment)\\b', re.IGNORECASE)

    # Message type patterns
    mt103_pattern = re.compile(r'MT103|103:', re.IGNORECASE)
    mt202_pattern = re.compile(r'MT202(?!COV)|202(?!COV):', re.IGNORECASE)
    mt202cov_pattern = re.compile(r'MT202COV|202COV:', re.IGNORECASE)
    mt205_pattern = re.compile(r'MT205(?!COV)|205(?!COV):', re.IGNORECASE)
    mt205cov_pattern = re.compile(r'MT205COV|205COV:', re.IGNORECASE)

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

    # 5. Salary patterns - Always check regardless of confidence
    if salary_pattern.search(narration) or "SALARY TRANSFER" in narration.upper():
        return {
            'purpose_code': 'SALA',
            'confidence': 0.99,
            'fallback_applied': 'targeted_salary'
        }

    # 6. Letter of credit patterns - Always check regardless of confidence
    if letter_of_credit_pattern.search(narration) or "IRREVOCABLE CREDIT" in narration.upper():
        return {
            'purpose_code': 'ICCP',
            'confidence': 0.95,
            'fallback_applied': 'targeted_letter_of_credit'
        }

    # 7. Treasury patterns - Always check regardless of confidence
    if treasury_pattern.search(narration) and "BOND" in narration.upper():
        return {
            'purpose_code': 'TREA',
            'confidence': 0.95,
            'fallback_applied': 'targeted_treasury_bond'
        }

    # 8. Cash management patterns - Always check regardless of confidence
    if cash_pattern.search(narration):
        return {
            'purpose_code': 'CASH',
            'confidence': 0.95,
            'fallback_applied': 'targeted_cash_management'
        }

    # 9. Trade settlement patterns - Always check regardless of confidence
    if trade_pattern.search(narration) and "SETTLEMENT" in narration.upper():
        return {
            'purpose_code': 'CORT',
            'confidence': 0.95,
            'fallback_applied': 'targeted_trade_settlement'
        }

    # 10. Cross-border patterns - Always check regardless of confidence
    if cross_border_pattern.search(narration):
        return {
            'purpose_code': 'XBCT',
            'confidence': 0.95,
            'fallback_applied': 'targeted_cross_border'
        }

    # Apply context-aware enhancers (they have medium priority)

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
            
            # Check for consulting services pattern in MT103
            if 'CONSULTING' in narration.upper() or 'SERVICES' in narration.upper():
                return {
                    'purpose_code': 'SCVE',
                    'confidence': 0.95,
                    'fallback_applied': 'message_type_mt103_consulting'
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

    # Apply fallback rules for low-confidence predictions
    if confidence < fallback_rules['low_confidence_threshold']:
        # Check for office supplies keywords
        for keyword in fallback_rules['office_supplies_keywords']:
            if keyword.lower() in narration.lower():
                return {
                    'purpose_code': 'GDDS',
                    'confidence': 0.95,
                    'fallback_applied': 'office_supplies'
                }
        
        # Check for business expenses keywords
        for keyword in fallback_rules['business_expenses_keywords']:
            if keyword.lower() in narration.lower():
                return {
                    'purpose_code': 'BEXP',
                    'confidence': 0.95,
                    'fallback_applied': 'business_expenses'
                }
        
        # Check for account transfer keywords
        for keyword in fallback_rules['account_transfer_keywords']:
            if keyword.lower() in narration.lower():
                return {
                    'purpose_code': 'CASH',
                    'confidence': 0.95,
                    'fallback_applied': 'account_transfer'
                }
        
        # Check for investment keywords
        for keyword in fallback_rules['investment_keywords']:
            if keyword.lower() in narration.lower():
                return {
                    'purpose_code': 'INVS',
                    'confidence': 0.95,
                    'fallback_applied': 'investment'
                }
    
    # If no fallback rules matched, return None
    return None
"""

    # Update the enhanced_category_purpose function
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

    # Update the enhancement info
    if 'enhancement_info' not in enhanced_package:
        enhanced_package['enhancement_info'] = {
            'enhanced_at': datetime.now().isoformat(),
            'enhancements': []
        }

    # Add the new enhancements to the enhancements list
    enhanced_package['enhancement_info']['enhancements'].extend([
        'Fixed remaining issues with purpose code classification',
        'Enhanced handling for salary transfers',
        'Enhanced handling for social welfare payments',
        'Enhanced handling for letters of credit',
        'Enhanced handling for treasury bonds',
        'Enhanced handling for cash management',
        'Enhanced handling for trade settlements',
        'Enhanced handling for cross-border payments',
        'Enhanced handling for MT202 and MT202COV messages',
        'Enhanced handling for MT205 and MT205COV messages',
        'Enhanced handling for consulting services'
    ])

    # Update the enhancement timestamp
    enhanced_package['enhancement_info']['enhanced_at'] = datetime.now().isoformat()

    return enhanced_package

def main():
    """Main function"""
    args = parse_args()

    # Load the model
    model_package = load_model(args.input_model)
    if model_package is None:
        print("Failed to load model")
        return 1

    # Fix the enhanced_predict function
    enhanced_package = fix_enhanced_predict(model_package)

    # Save the enhanced model
    if not save_model(enhanced_package, args.output_model):
        print("Failed to save enhanced model")
        return 1

    print("Remaining issues fixed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
