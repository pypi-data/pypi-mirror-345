#!/usr/bin/env python3
"""
Generate focused training data for the remaining incorrectly classified examples.

This script creates synthetic training examples for the specific cases
where the model still makes incorrect classifications:
1. LOAN vs LOAR (Loan vs Loan Repayment)
2. VATX vs TAXS (Value Added Tax Payment vs Tax Payment)
3. SSBE vs GBEN (Social Security Benefit vs Government Benefit)
4. SCVE vs SERV (Purchase of Services vs Service Charge)
"""

import os
import pandas as pd
import random
import argparse
from datetime import datetime

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Generate focused training data for remaining issues')
    
    parser.add_argument('--output', type=str, default='data/focused_training_data.csv',
                        help='Path to save the generated training data')
    
    parser.add_argument('--existing-data', type=str, default='data/final_strict_data.csv',
                        help='Path to existing training data to avoid duplicates')
    
    parser.add_argument('--samples-per-case', type=int, default=200,
                        help='Number of samples to generate per case')
    
    return parser.parse_args()

def load_existing_data(file_path):
    """Load existing data to avoid duplicates"""
    if not os.path.exists(file_path):
        print(f"Warning: Existing data file not found: {file_path}")
        return set()
    
    try:
        df = pd.read_csv(file_path)
        if 'narration' not in df.columns:
            print(f"Warning: Existing data file does not have a 'narration' column")
            return set()
        
        return set(narration.lower() for narration in df['narration'] if isinstance(narration, str))
    except Exception as e:
        print(f"Error loading existing data: {str(e)}")
        return set()

def generate_loan_examples(n_samples):
    """Generate examples for LOAN (Loan) vs LOAR (Loan Repayment)"""
    # Templates for LOAN (Loan) with specific focus on "LOAN REPAYMENT"
    loan_templates = [
        "LOAN REPAYMENT - ACCOUNT {account_num}",
        "LOAN REPAYMENT - {account}",
        "LOAN REPAYMENT",
        "REPAYMENT OF LOAN",
        "LOAN REPAYMENT TRANSACTION",
        "LOAN REPAYMENT SETTLEMENT",
        "LOAN ACCOUNT REPAYMENT",
        "REPAYMENT FOR LOAN",
        "REPAYMENT TOWARDS LOAN",
        "LOAN REPAYMENT - PRINCIPAL AND INTEREST"
    ]
    
    # Templates for LOAR (Loan Repayment) with clear distinction
    loar_templates = [
        "LOAN REPAYMENT INSTALLMENT - {account}",
        "SCHEDULED LOAN REPAYMENT - {account}",
        "LOAN REPAYMENT PLAN - PAYMENT {number}",
        "LOAN REPAYMENT SCHEDULE - PAYMENT {number}",
        "LOAN REPAYMENT PROGRAM - {account}",
        "LOAN REPAYMENT ARRANGEMENT - PAYMENT {number}",
        "STRUCTURED LOAN REPAYMENT - {account}",
        "LOAN REPAYMENT AGREEMENT - PAYMENT {number}",
        "FORMAL LOAN REPAYMENT - {account}",
        "LOAN REPAYMENT CONTRACT - PAYMENT {number}"
    ]
    
    accounts = [
        "ACCOUNT 12345", "MORTGAGE 67890", "PERSONAL LOAN 54321", 
        "AUTO LOAN 98765", "HOME LOAN 13579", "BUSINESS LOAN 24680",
        "CREDIT LINE 11223", "LOAN FACILITY 44556", "TERM LOAN 77889",
        "LOAN ACCOUNT 10293"
    ]
    
    account_nums = [
        "12345", "67890", "54321", "98765", "13579", 
        "24680", "11223", "44556", "77889", "10293"
    ]
    
    numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
    
    examples = []
    # Generate LOAN examples
    for _ in range(n_samples):
        template = random.choice(loan_templates)
        
        # Some templates need formatting
        if "{account}" in template:
            account = random.choice(accounts)
            narration = template.format(account=account)
        elif "{account_num}" in template:
            account_num = random.choice(account_nums)
            narration = template.format(account_num=account_num)
        else:
            narration = template
            
        examples.append({
            'narration': narration,
            'purpose_code': 'LOAN',
            'category_purpose_code': 'LOAN'
        })
    
    # Generate LOAR examples
    for _ in range(n_samples // 2):
        template = random.choice(loar_templates)
        account = random.choice(accounts)
        number = random.choice(numbers)
        
        narration = template.format(account=account, number=number)
        examples.append({
            'narration': narration,
            'purpose_code': 'LOAR',
            'category_purpose_code': 'LOAN'
        })
    
    return examples

def generate_tax_examples(n_samples):
    """Generate examples for VATX (Value Added Tax Payment) vs TAXS (Tax Payment)"""
    # Templates for VATX (Value Added Tax Payment)
    vatx_templates = [
        "VALUE ADDED TAX PAYMENT",
        "VAT PAYMENT",
        "VALUE ADDED TAX",
        "VAT PAYMENT FOR {period}",
        "VALUE ADDED TAX FOR {period}",
        "VAT SETTLEMENT",
        "VALUE ADDED TAX SETTLEMENT",
        "VAT REMITTANCE",
        "VALUE ADDED TAX REMITTANCE",
        "PAYMENT OF VALUE ADDED TAX"
    ]
    
    # Additional specific templates for VATX
    specific_vatx_templates = [
        "VALUE ADDED TAX PAYMENT - {period}",
        "VAT PAYMENT - {business}",
        "VALUE ADDED TAX - {business}",
        "VAT - {period}",
        "VALUE ADDED TAX RETURN - {period}",
        "VAT RETURN - {business}",
        "VALUE ADDED TAX FILING - {period}",
        "VAT FILING - {business}",
        "VALUE ADDED TAX SUBMISSION - {period}",
        "VAT SUBMISSION - {business}"
    ]
    
    # Templates for TAXS (Tax Payment) that are clearly different from VAT
    taxs_templates = [
        "INCOME TAX PAYMENT",
        "CORPORATE TAX PAYMENT",
        "PROPERTY TAX PAYMENT",
        "CAPITAL GAINS TAX PAYMENT",
        "PAYROLL TAX PAYMENT",
        "SALES TAX PAYMENT",
        "EXCISE TAX PAYMENT",
        "CUSTOMS TAX PAYMENT",
        "STAMP DUTY PAYMENT",
        "INHERITANCE TAX PAYMENT"
    ]
    
    periods = [
        "Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025", 
        "JANUARY 2025", "FEBRUARY 2025", "MARCH 2025", 
        "APRIL 2025", "MAY 2025", "JUNE 2025"
    ]
    
    businesses = [
        "RETAIL BUSINESS", "MANUFACTURING", "SERVICES", "CONSTRUCTION", 
        "HOSPITALITY", "HEALTHCARE", "TECHNOLOGY", "AGRICULTURE", 
        "TRANSPORTATION", "EDUCATION"
    ]
    
    examples = []
    # Generate VATX examples
    for _ in range(n_samples // 2):
        template = random.choice(vatx_templates)
        
        # Some templates need formatting
        if "{period}" in template:
            period = random.choice(periods)
            narration = template.format(period=period)
        elif "{business}" in template:
            business = random.choice(businesses)
            narration = template.format(business=business)
        else:
            narration = template
            
        examples.append({
            'narration': narration,
            'purpose_code': 'VATX',
            'category_purpose_code': 'TAXS'
        })
    
    # Generate additional specific VATX examples
    for _ in range(n_samples // 2):
        template = random.choice(specific_vatx_templates)
        period = random.choice(periods)
        business = random.choice(businesses)
        
        # Format the template
        if "{period}" in template:
            narration = template.format(period=period)
        else:
            narration = template.format(business=business)
            
        examples.append({
            'narration': narration,
            'purpose_code': 'VATX',
            'category_purpose_code': 'TAXS'
        })
    
    # Generate TAXS examples
    for _ in range(n_samples):
        template = random.choice(taxs_templates)
        narration = template
        examples.append({
            'narration': narration,
            'purpose_code': 'TAXS',
            'category_purpose_code': 'TAXS'
        })
    
    return examples

def generate_benefit_examples(n_samples):
    """Generate examples for SSBE (Social Security Benefit) vs GBEN (Government Benefit)"""
    # Templates for SSBE (Social Security Benefit)
    ssbe_templates = [
        "SOCIAL SECURITY BENEFIT PAYMENT",
        "SOCIAL SECURITY PAYMENT",
        "SOCIAL SECURITY BENEFIT",
        "SOCIAL SECURITY BENEFIT FOR {period}",
        "SOCIAL SECURITY PAYMENT FOR {period}",
        "SOCIAL SECURITY DISBURSEMENT",
        "SOCIAL SECURITY BENEFIT DISBURSEMENT",
        "SOCIAL SECURITY ENTITLEMENT",
        "SOCIAL SECURITY BENEFIT ENTITLEMENT",
        "PAYMENT OF SOCIAL SECURITY BENEFIT"
    ]
    
    # Additional specific templates for SSBE
    specific_ssbe_templates = [
        "SOCIAL SECURITY BENEFIT PAYMENT - {recipient}",
        "SOCIAL SECURITY PAYMENT - {recipient}",
        "SOCIAL SECURITY BENEFIT - {period}",
        "SOCIAL SECURITY - {recipient}",
        "SOCIAL SECURITY BENEFIT TRANSFER - {period}",
        "SOCIAL SECURITY TRANSFER - {recipient}",
        "SOCIAL SECURITY BENEFIT DEPOSIT - {period}",
        "SOCIAL SECURITY DEPOSIT - {recipient}",
        "SOCIAL SECURITY BENEFIT CREDIT - {period}",
        "SOCIAL SECURITY CREDIT - {recipient}"
    ]
    
    # Templates for GBEN (Government Benefit) that are clearly different from SSBE
    gben_templates = [
        "GOVERNMENT BENEFIT PAYMENT",
        "GOVERNMENT ASSISTANCE PAYMENT",
        "GOVERNMENT SUPPORT PAYMENT",
        "GOVERNMENT AID PAYMENT",
        "GOVERNMENT WELFARE PAYMENT",
        "GOVERNMENT SUBSIDY PAYMENT",
        "GOVERNMENT GRANT PAYMENT",
        "GOVERNMENT ALLOWANCE PAYMENT",
        "GOVERNMENT RELIEF PAYMENT",
        "GOVERNMENT STIMULUS PAYMENT"
    ]
    
    periods = [
        "JANUARY 2025", "FEBRUARY 2025", "MARCH 2025", 
        "APRIL 2025", "MAY 2025", "JUNE 2025",
        "JULY 2025", "AUGUST 2025", "SEPTEMBER 2025",
        "OCTOBER 2025", "NOVEMBER 2025", "DECEMBER 2025"
    ]
    
    recipients = [
        "RETIREE", "PENSIONER", "SENIOR CITIZEN", "DISABLED", 
        "SURVIVOR", "DEPENDENT", "BENEFICIARY", "CLAIMANT", 
        "RECIPIENT", "ELIGIBLE INDIVIDUAL"
    ]
    
    examples = []
    # Generate SSBE examples
    for _ in range(n_samples // 2):
        template = random.choice(ssbe_templates)
        
        # Some templates need formatting
        if "{period}" in template:
            period = random.choice(periods)
            narration = template.format(period=period)
        else:
            narration = template
            
        examples.append({
            'narration': narration,
            'purpose_code': 'SSBE',
            'category_purpose_code': 'SSBE'
        })
    
    # Generate additional specific SSBE examples
    for _ in range(n_samples // 2):
        template = random.choice(specific_ssbe_templates)
        period = random.choice(periods)
        recipient = random.choice(recipients)
        
        # Format the template
        if "{period}" in template:
            narration = template.format(period=period)
        else:
            narration = template.format(recipient=recipient)
            
        examples.append({
            'narration': narration,
            'purpose_code': 'SSBE',
            'category_purpose_code': 'SSBE'
        })
    
    # Generate GBEN examples
    for _ in range(n_samples):
        template = random.choice(gben_templates)
        narration = template
        examples.append({
            'narration': narration,
            'purpose_code': 'GBEN',
            'category_purpose_code': 'GOVT'
        })
    
    return examples

def generate_service_examples(n_samples):
    """Generate examples for SCVE (Purchase of Services) vs SERV (Service Charge)"""
    # Templates for SCVE (Purchase of Services) with focus on "FEE COLLECTION FOR SERVICES"
    scve_templates = [
        "FEE COLLECTION FOR SERVICES",
        "FEE COLLECTION FOR {service} SERVICES",
        "SERVICE FEE COLLECTION",
        "COLLECTION OF FEES FOR SERVICES",
        "COLLECTION OF SERVICE FEES",
        "FEE COLLECTION - SERVICES",
        "SERVICE CHARGE COLLECTION",
        "COLLECTION OF SERVICE CHARGES",
        "PROFESSIONAL SERVICE FEE COLLECTION",
        "COLLECTION OF PROFESSIONAL SERVICE FEES"
    ]
    
    # Additional specific templates for SCVE
    specific_scve_templates = [
        "FEE COLLECTION FOR {service} SERVICES - {ref}",
        "SERVICE FEE COLLECTION - {service}",
        "COLLECTION OF FEES FOR {service} SERVICES - {ref}",
        "COLLECTION OF {service} SERVICE FEES",
        "FEE COLLECTION - {service} SERVICES - {ref}",
        "SERVICE CHARGE COLLECTION - {service}",
        "COLLECTION OF {service} SERVICE CHARGES - {ref}",
        "PROFESSIONAL {service} SERVICE FEE COLLECTION",
        "COLLECTION OF PROFESSIONAL {service} FEES - {ref}",
        "FEE COLLECTION FOR PROFESSIONAL {service} SERVICES"
    ]
    
    # Templates for SERV (Service Charge) that are clearly different from SCVE
    serv_templates = [
        "BANK SERVICE CHARGE",
        "ACCOUNT SERVICE FEE",
        "MONTHLY SERVICE CHARGE",
        "TRANSACTION SERVICE FEE",
        "MAINTENANCE SERVICE CHARGE",
        "PROCESSING SERVICE FEE",
        "ADMINISTRATIVE SERVICE CHARGE",
        "HANDLING SERVICE FEE",
        "OPERATIONAL SERVICE CHARGE",
        "MANAGEMENT SERVICE FEE"
    ]
    
    services = [
        "CONSULTING", "LEGAL", "ACCOUNTING", "MARKETING", 
        "ENGINEERING", "IT", "DESIGN", "ADVISORY", 
        "TRAINING", "MAINTENANCE"
    ]
    
    refs = [f"INV{random.randint(10000, 99999)}" for _ in range(20)]
    
    examples = []
    # Generate SCVE examples
    for _ in range(n_samples // 2):
        template = random.choice(scve_templates)
        
        # Some templates need formatting
        if "{service}" in template:
            service = random.choice(services)
            narration = template.format(service=service)
        else:
            narration = template
            
        examples.append({
            'narration': narration,
            'purpose_code': 'SCVE',
            'category_purpose_code': 'SUPP'
        })
    
    # Generate additional specific SCVE examples
    for _ in range(n_samples // 2):
        template = random.choice(specific_scve_templates)
        service = random.choice(services)
        ref = random.choice(refs)
        
        # Format the template
        if "{ref}" in template:
            narration = template.format(service=service, ref=ref)
        else:
            narration = template.format(service=service)
            
        examples.append({
            'narration': narration,
            'purpose_code': 'SCVE',
            'category_purpose_code': 'SUPP'
        })
    
    # Generate SERV examples
    for _ in range(n_samples):
        template = random.choice(serv_templates)
        narration = template
        examples.append({
            'narration': narration,
            'purpose_code': 'SERV',
            'category_purpose_code': 'SUPP'
        })
    
    return examples

def main():
    """Main function to generate focused training data"""
    args = parse_args()
    
    # Load existing data to avoid duplicates
    existing_narrations = load_existing_data(args.existing_data)
    print(f"Loaded {len(existing_narrations)} existing narrations")
    
    # Generate examples for each problematic case
    loan_examples = generate_loan_examples(args.samples_per_case)
    tax_examples = generate_tax_examples(args.samples_per_case)
    benefit_examples = generate_benefit_examples(args.samples_per_case)
    service_examples = generate_service_examples(args.samples_per_case)
    
    # Combine all examples
    all_examples = []
    all_examples.extend(loan_examples)
    all_examples.extend(tax_examples)
    all_examples.extend(benefit_examples)
    all_examples.extend(service_examples)
    
    # Remove duplicates with existing data
    filtered_examples = []
    for example in all_examples:
        if example['narration'].lower() not in existing_narrations:
            filtered_examples.append(example)
            existing_narrations.add(example['narration'].lower())
    
    print(f"Generated {len(all_examples)} examples")
    print(f"After removing duplicates: {len(filtered_examples)} examples")
    
    # Create DataFrame
    df = pd.DataFrame(filtered_examples)
    
    # Save to CSV
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"Saved {len(df)} examples to {args.output}")
    
    # Print sample of generated data
    print("\nSample of generated data:")
    print(df.sample(min(10, len(df))).to_string())
    
    return 0

if __name__ == "__main__":
    main()
