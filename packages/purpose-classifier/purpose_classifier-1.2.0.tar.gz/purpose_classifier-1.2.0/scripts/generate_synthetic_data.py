"""
Generate synthetic training data for purpose code classification.

This script generates synthetic training data for the worst-performing purpose codes
to improve the model's performance on these codes.
"""

import os
import json
import random
import pandas as pd
import numpy as np
from datetime import datetime

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

# Define the worst-performing purpose codes
WORST_PERFORMING_CODES = [
    "GDDS",  # Purchase Sale of Goods
    "SCVE",  # Purchase of Services
    "SERV",  # Service
    "EDUC",  # Education
    "INSU",  # Insurance Premium
    "SUPP",  # Supplier Payment
    "TAXS",  # Tax Payment
    "SALA",  # Salary Payment
    "VATX",  # Value Added Tax Payment
    "TREA",  # Treasury Payment
    "CORT",  # Court Payment
    "CCRD",  # Credit Card Payment
    "DCRD",  # Debit Card Payment
    "WHLD",  # Withholding
    "INTE",  # Interest
    "ICCP",  # Irrevocable Credit Card Payment
    "IDCP"   # Irrevocable Debit Card Payment
]

# Message types are no longer used in this version

def load_purpose_codes():
    """Load purpose codes from the JSON file."""
    with open('data/purpose_codes.json', 'r') as f:
        purpose_codes = json.load(f)
    return purpose_codes

def load_category_purpose_codes():
    """Load category purpose codes from the JSON file."""
    with open('data/category_purpose_codes.json', 'r') as f:
        category_purpose_codes = json.load(f)
    return category_purpose_codes

def get_category_for_purpose(purpose_code, category_purpose_codes):
    """Get the category purpose code for a given purpose code based on the documented mappings."""
    # Comprehensive mapping based on the purpose_code_mappings.md documentation
    purpose_to_category_mappings = {
        # Direct mappings
        "GDDS": "GDDS",  # Purchase Sale of Goods
        "SUPP": "SUPP",  # Supplier Payment
        "TAXS": "TAXS",  # Tax Payment
        "SALA": "SALA",  # Salary Payment
        "VATX": "VATX",  # Value Added Tax Payment
        "TREA": "TREA",  # Treasury Payment
        "CORT": "CORT",  # Trade Settlement Payment
        "CCRD": "CCRD",  # Credit Card Payment
        "DCRD": "DCRD",  # Debit Card Payment
        "WHLD": "WHLD",  # With Holding
        "INTE": "INTE",  # Interest
        "ICCP": "ICCP",  # Irrevocable Credit Card Payment
        "IDCP": "IDCP",  # Irrevocable Debit Card Payment
        "CASH": "CASH",  # Cash Management Transfer
        "HEDG": "HEDG",  # Hedging
        "INTC": "INTC",  # Intra-Company Payment
        "PENS": "PENS",  # Pension Payment
        "BONU": "BONU",  # Bonus Payment
        "SSBE": "SSBE",  # Social Security Benefit
        "EPAY": "EPAY",  # ePayment
        "TRAD": "TRAD",  # Trade Services
        "LOAN": "LOAN",  # Loan
        "SECU": "SECU",  # Securities
        "GOVT": "GOVT",  # Government Payment
        "DIVI": "DIVI",  # Dividend Payment

        # Services related
        "SCVE": "TRAD",  # Purchase of Services maps to Trade Services
        "SERV": "FCOL",  # Service Charge maps to Fee Collection
        "BBSC": "FCOL",  # Business Service Charge maps to Fee Collection
        "MSVC": "TRAD",  # Multiple Service Types maps to Trade Services

        # Education related
        "EDUC": "FCOL",  # Education maps to Fee Collection
        "STDY": "FCOL",  # Study maps to Fee Collection

        # Insurance related
        "INSU": "SECU",  # Insurance Premium maps to Securities
        "GOVI": "SECU",  # Government Insurance maps to Securities
        "LIFI": "SECU",  # Life Insurance maps to Securities
        "PPTI": "SECU",  # Property Insurance maps to Securities
        "LBRI": "SECU",  # Labor Insurance maps to Securities

        # Loan related
        "LOAR": "LOAN",  # Loan Repayment maps to Loan
        "HLRP": "LOAN",  # Housing Loan Repayment maps to Loan
        "STLR": "LOAN",  # Student Loan Repayment maps to Loan
        "CLPR": "LOAN",  # Car Loan Principal maps to Loan
        "CSLP": "LOAN",  # Car Loan Principal maps to Loan
        "RINP": "LOAN",  # Recurring Installment Payment maps to Loan

        # Investment related
        "INVS": "SECU",  # Investment and Securities maps to Securities
        "IVPT": "SECU",  # Investment Payment maps to Securities
        "IADD": "SECU",  # Investment Additional Deposit maps to Securities
        "CBFF": "SECU",  # Capital Building maps to Securities

        # Government related
        "GVEA": "GOVT",  # Austrian Government Payment maps to Government Payment
        "GVEB": "GOVT",  # Belgian Government Payment maps to Government Payment
        "GVEF": "GOVT",  # French Government Payment maps to Government Payment
        "GVEG": "GOVT",  # German Government Payment maps to Government Payment
        "GVEH": "GOVT",  # Greek Government Payment maps to Government Payment
        "GVEI": "GOVT",  # Irish Government Payment maps to Government Payment
        "GVEL": "GOVT",  # Luxembourg Government Payment maps to Government Payment
        "GVEN": "GOVT",  # Dutch Government Payment maps to Government Payment
        "GVEP": "GOVT",  # Portuguese Government Payment maps to Government Payment
        "GVES": "GOVT",  # Spanish Government Payment maps to Government Payment
        "EMIGR": "GOVT", # Emigration Payment maps to Government Payment

        # Social security related
        "BENE": "SSBE",  # Unemployment/Benefit maps to Social Security Benefit
        "GBEN": "SSBE",  # Government Benefit maps to Social Security Benefit
        "BECH": "SSBE",  # Child Benefit maps to Social Security Benefit

        # Salary related
        "PAYR": "SALA",  # Payroll maps to Salary Payment
        "WTER": "SALA",  # Worker Compensation maps to Salary Payment

        # Dividend related
        "DIVD": "DIVI",  # Dividend Payment maps to Dividend Payment

        # Tax related
        "REFU": "TAXS",  # Tax Refund maps to Tax Payment
        "RDTX": "TAXS",  # Road Tax maps to Tax Payment
        "NITX": "TAXS",  # Net Income Tax maps to Tax Payment
        "ESTX": "TAXS",  # Estate Tax maps to Tax Payment
        "HLTX": "TAXS",  # Health Tax maps to Tax Payment

        # Utility bills
        "ELEC": "SUPP",  # Electricity Bill maps to Supplier Payment
        "GASB": "SUPP",  # Gas Bill maps to Supplier Payment
        "UBIL": "SUPP",  # Utility Bill maps to Supplier Payment
        "CABLE": "SUPP", # Cable TV Bill maps to Supplier Payment
        "PHON": "SUPP",  # Telephone Bill maps to Supplier Payment
        "TBIL": "SUPP",  # Telecommunications Bill maps to Supplier Payment
        "NWCH": "SUPP",  # Network Charge maps to Supplier Payment
        "NWCM": "SUPP",  # Network Communication maps to Supplier Payment
        "OTLC": "SUPP",  # Other Telecom Related Bill maps to Supplier Payment

        # Fee collection
        "BKDF": "FCOL",  # Bank Fees maps to Fee Collection
        "LICF": "FCOL",  # License Fee maps to Fee Collection
        "COMM": "FCOL",  # Commission maps to Fee Collection
        "CHAR": "FCOL",  # Charges maps to Fee Collection
        "COST": "FCOL",  # Costs maps to Fee Collection
        "CPYR": "FCOL",  # Copyright maps to Fee Collection
        "ROYA": "FCOL",  # Royalties maps to Fee Collection
        "SUBS": "FCOL",  # Subscription maps to Fee Collection

        # ePayment
        "WEBI": "EPAY",  # Internet-Initiated Payment maps to ePayment
        "IPAY": "EPAY",  # Bill Payment maps to ePayment
        "TELI": "EPAY",  # Telephone Initiated Transaction maps to ePayment

        # Cash management
        "CSDB": "CASH",  # Cash Disbursement maps to Cash Management Transfer
        "ACCB": "CASH",  # Advance Against Cash Balance maps to Cash Management Transfer
        "BNET": "CASH",  # Clearing House Automated Payment maps to Cash Management Transfer
        "CAJT": "CASH",  # Cash Adjustment maps to Cash Management Transfer

        # Hedging
        "FREX": "HEDG",  # Foreign Exchange maps to Hedging
        "BKFX": "HEDG",  # Bank Foreign Exchange maps to Hedging

        # Cross-border
        "XBCT": "TRAD",  # Cross-Border Credit Transfer maps to Trade Services
        "XBDD": "TRAD",  # Cross-Border Direct Debit maps to Trade Services

        # Domestic transfers
        "DMCT": "SUPP",  # Domestic Credit Transfer maps to Supplier Payment
        "DMDD": "SUPP",  # Domestic Direct Debit maps to Supplier Payment

        # Other supplier payments
        "ADVA": "SUPP",  # Advance Payment maps to Supplier Payment
        "BEXP": "SUPP",  # Business Expenses maps to Supplier Payment
        "HSPC": "SUPP",  # Hospital Care maps to Supplier Payment
        "ALMY": "SUPP",  # Alimony Payment maps to Supplier Payment
        "PRCP": "SUPP",  # Price Payment maps to Supplier Payment
        "COLL": "SUPP",  # Collection Payment maps to Supplier Payment
        "PRME": "SUPP",  # Property Maintenance maps to Supplier Payment
        "RENT": "SUPP",  # Rent maps to Supplier Payment
        "DONR": "SUPP",  # Donor Payment maps to Supplier Payment
        "FRST": "SUPP",  # Fundraising maps to Supplier Payment
        "RLGN": "SUPP",  # Religious Payment maps to Supplier Payment
        "DBTC": "SUPP",  # Debit Collection Payment maps to Supplier Payment
        "PTSP": "SUPP",  # Payment Terms Specification maps to Supplier Payment
        "REBT": "SUPP",  # Rebate Payment maps to Supplier Payment
        "RIMB": "SUPP",  # Reimbursement maps to Supplier Payment
        "TCSC": "SUPP",  # Town Council Service Charges maps to Supplier Payment

        # Credit/debit card related
        "CDBL": "CCRD",  # Credit Card Bill maps to Credit Card Payment

        # Interest related
        "CDTI": "INTE",  # Credit Transfer with Interest maps to Interest
        "DBTI": "INTE",  # Debit Transfer with Interest maps to Interest

        # Court related
        "COMT": "CORT",  # Court Payment maps to Trade Settlement Payment
        "CVCF": "CORT",  # Conviction Payment maps to Trade Settlement Payment

        # Trade related
        "AIRB": "TRAD",  # Air Charter maps to Trade Services
        "COMC": "TRAD",  # Commercial Credit maps to Trade Services
        "GDSV": "GDDS",  # Goods and Services maps to Purchase Sale of Goods
        "GSCB": "GDDS",  # Purchase Sale of Goods and Services with Cash Back maps to Purchase Sale of Goods
        "POPE": "GDDS",  # Point of Purchase Entry maps to Purchase Sale of Goods

        # Other (mapped to appropriate categories, never OTHR)
        "OTHR": "SUPP"   # Other Payment maps to Supplier Payment
    }

    # Check if the purpose code has a mapping
    if purpose_code in purpose_to_category_mappings:
        return purpose_to_category_mappings[purpose_code]

    # If no mapping is found, use a more appropriate category based on purpose code semantics
    # This is a fallback mechanism to avoid using OTHR
    fallback_mappings = {
        # Default mappings by purpose code prefix
        "B": "SUPP",    # Business related -> Supplier Payment
        "C": "TRAD",    # Commercial related -> Trade Services
        "G": "GDDS",    # Goods related -> Purchase Sale of Goods
        "S": "TRAD",    # Service related -> Trade Services
        "T": "TAXS",    # Tax related -> Tax Payment
        "I": "SECU",    # Investment related -> Securities
        "L": "LOAN",    # Loan related -> Loan
        "P": "SUPP",    # Payment related -> Supplier Payment
        "R": "SUPP",    # Rent/Real estate -> Supplier Payment
        "E": "EPAY",    # Electronic -> ePayment
        "D": "DIVI",    # Dividend related -> Dividend Payment
        "F": "FCOL",    # Fee related -> Fee Collection
        "H": "SUPP",    # Housing related -> Supplier Payment
        "M": "SUPP",    # Miscellaneous -> Supplier Payment
        "N": "SUPP",    # Network related -> Supplier Payment
        "O": "SUPP",    # Other -> Supplier Payment
        "U": "SUPP",    # Utility related -> Supplier Payment
        "W": "WHLD",    # Withholding related -> With Holding
        "X": "TRAD",    # Cross-border -> Trade Services
        "A": "SUPP",    # Any other -> Supplier Payment
    }

    # Try to find a fallback based on the first letter of the purpose code
    first_letter = purpose_code[0] if purpose_code else ""
    if first_letter in fallback_mappings:
        return fallback_mappings[first_letter]

    # If all else fails, use SUPP as a last resort (never use OTHR)
    return "SUPP"

def generate_narrations_for_purpose_code(purpose_code, count=100):
    """Generate synthetic narrations for a specific purpose code."""
    narrations = []

    # Load templates based on purpose code
    templates = get_templates_for_purpose_code(purpose_code)

    # Generate narrations using templates
    for _ in range(count):
        template = random.choice(templates)
        narration = fill_template(template, purpose_code)
        narrations.append(narration)

    return narrations

def get_templates_for_purpose_code(purpose_code):
    """Get templates for a specific purpose code."""
    templates = {
        "GDDS": [
            "Purchase of {goods} from {company}",
            "Payment for {goods} to {company}",
            "Invoice {invoice_num} for {goods}",
            "{goods} purchase from {company}",
            "Goods payment: {goods} from {company}",
            "Purchase order {po_num} for {goods}",
            "Retail purchase of {goods}",
            "Wholesale purchase of {goods} from {company}",
            "Payment for merchandise: {goods}",
            "Product purchase: {goods} from {company}"
        ],
        "SCVE": [
            "Payment for {service} services",
            "Service fee for {service} from {company}",
            "Professional services: {service}",
            "Consulting services from {company} for {service}",
            "{service} service payment to {company}",
            "Service invoice {invoice_num} for {service}",
            "Payment for {service} consultation",
            "Professional fee for {service} services",
            "{service} service charge from {company}",
            "Service payment: {service} to {company}"
        ],
        "SERV": [
            "Service payment to {company}",
            "Payment for services rendered by {company}",
            "Service fee to {company}",
            "Services invoice {invoice_num}",
            "Payment for {service} services",
            "Service charge from {company}",
            "Professional services payment",
            "Service contract payment to {company}",
            "Payment for service agreement with {company}",
            "Service maintenance fee to {company}"
        ],
        "EDUC": [
            "Tuition payment for {semester}",
            "School fees for {student_name}",
            "Education payment to {institution}",
            "Tuition and fees for {semester}",
            "Payment for {course} course at {institution}",
            "Educational services at {institution}",
            "School tuition for {student_name} at {institution}",
            "University fees for {semester}",
            "Education expenses for {student_name}",
            "Tuition payment for {course} at {institution}"
        ],
        "INSU": [
            "Insurance premium for {insurance_type}",
            "Payment for {insurance_type} insurance policy {policy_num}",
            "Insurance payment to {company}",
            "Premium for {insurance_type} policy {policy_num}",
            "{insurance_type} insurance renewal",
            "Insurance policy {policy_num} payment",
            "Annual premium for {insurance_type} insurance",
            "Insurance coverage payment for {insurance_type}",
            "Policy renewal for {insurance_type} insurance",
            "Insurance premium payment to {company} for policy {policy_num}"
        ],
        "SUPP": [
            "Supplier payment to {company}",
            "Payment to supplier {company}",
            "Vendor payment for invoice {invoice_num}",
            "Payment to vendor {company}",
            "Supplier invoice {invoice_num} payment",
            "Payment for supplies from {company}",
            "Vendor payment for {goods}",
            "Supplier payment for {goods}",
            "Payment to {company} for supplies",
            "Vendor invoice {invoice_num} payment for {goods}"
        ],
        "TAXS": [
            "Tax payment for {tax_period}",
            "Payment of taxes for {tax_period}",
            "Tax remittance for {tax_period}",
            "Tax payment to {tax_authority}",
            "Income tax payment for {tax_period}",
            "Corporate tax payment for {tax_period}",
            "Tax payment reference {reference}",
            "Payment of {tax_type} taxes for {tax_period}",
            "Tax payment for account {account_num}",
            "Tax remittance to {tax_authority} for {tax_period}"
        ],
        "SALA": [
            "Salary payment for {month}",
            "Payroll for {month}",
            "Wages for {month}",
            "Employee compensation for {month}",
            "Monthly salary for {month}",
            "Payroll transfer for {month}",
            "Salary disbursement for {month}",
            "Employee payroll for {month}",
            "Wages payment for {month}",
            "Staff salary for {month}"
        ],
        "VATX": [
            "VAT payment for {tax_period}",
            "Value Added Tax for {tax_period}",
            "VAT remittance to {tax_authority}",
            "VAT payment reference {reference}",
            "Value Added Tax payment for {tax_period}",
            "VAT for invoice {invoice_num}",
            "VAT payment to {tax_authority} for {tax_period}",
            "Value Added Tax remittance for {tax_period}",
            "VAT payment for account {account_num}",
            "VAT tax payment for {tax_period}"
        ],
        "TREA": [
            "Treasury payment to {company}",
            "Treasury transfer to {company}",
            "Treasury operation with {company}",
            "Treasury payment reference {reference}",
            "Treasury transaction with {company}",
            "Treasury services payment",
            "Treasury management fee",
            "Treasury operation reference {reference}",
            "Treasury payment for {service}",
            "Treasury transaction reference {reference}"
        ],
        "CORT": [
            "Court payment for case {case_num}",
            "Legal fees for case {case_num}",
            "Court order payment {reference}",
            "Payment to court for case {case_num}",
            "Court settlement payment",
            "Legal settlement for case {case_num}",
            "Court fees for {legal_matter}",
            "Payment for legal proceedings {case_num}",
            "Court-ordered payment reference {reference}",
            "Legal payment for case {case_num}"
        ],
        "CCRD": [
            "Credit card payment to {company}",
            "Credit card bill payment",
            "Payment for credit card ending {last_digits}",
            "Credit card statement payment",
            "Credit card payment reference {reference}",
            "Payment for {company} credit card",
            "Credit card balance payment",
            "Credit card payment for account {account_num}",
            "Credit card bill for {month}",
            "Payment towards credit card ending {last_digits}"
        ],
        "DCRD": [
            "Debit card payment to {company}",
            "Debit card transaction with {company}",
            "Debit card purchase from {company}",
            "Debit card payment for {goods}",
            "Debit card transaction reference {reference}",
            "Payment using debit card ending {last_digits}",
            "Debit card payment for {service}",
            "Debit card purchase of {goods}",
            "Debit card payment reference {reference}",
            "Debit card transaction for {goods}"
        ],
        "WHLD": [
            "Withholding tax payment for {tax_period}",
            "Tax withholding for {tax_period}",
            "Withholding tax remittance to {tax_authority}",
            "Withholding tax payment reference {reference}",
            "Withholding tax for {tax_period}",
            "Tax withholding payment to {tax_authority}",
            "Withholding tax for invoice {invoice_num}",
            "Withholding tax payment for account {account_num}",
            "Tax withholding remittance for {tax_period}",
            "Withholding tax payment for {tax_type}"
        ],
        "INTE": [
            "Interest payment for {month}",
            "Interest on loan {loan_num}",
            "Interest payment to {company}",
            "Loan interest for {month}",
            "Interest payment reference {reference}",
            "Interest on deposit for {month}",
            "Interest payment for account {account_num}",
            "Interest on investment for {month}",
            "Interest payment for {investment_type}",
            "Interest on {investment_type} for {month}"
        ],
        "ICCP": [
            "Irrevocable credit card payment to {company}",
            "Irrevocable payment for credit card ending {last_digits}",
            "Irrevocable credit card settlement",
            "Irrevocable credit card payment reference {reference}",
            "Irrevocable payment for {company} credit card",
            "Irrevocable credit card payment for account {account_num}",
            "Irrevocable credit card bill payment",
            "Irrevocable payment towards credit card ending {last_digits}",
            "Irrevocable credit card payment for {month}",
            "Irrevocable credit card settlement reference {reference}"
        ],
        "IDCP": [
            "Irrevocable debit card payment to {company}",
            "Irrevocable debit card transaction with {company}",
            "Irrevocable debit card purchase from {company}",
            "Irrevocable debit card payment for {goods}",
            "Irrevocable debit card transaction reference {reference}",
            "Irrevocable payment using debit card ending {last_digits}",
            "Irrevocable debit card payment for {service}",
            "Irrevocable debit card purchase of {goods}",
            "Irrevocable debit card payment reference {reference}",
            "Irrevocable debit card transaction for {goods}"
        ]
    }

    return templates.get(purpose_code, ["Payment for {purpose_code}"])

def fill_template(template, purpose_code):
    """Fill a template with random values based on the purpose code."""
    # Common placeholders
    placeholders = {
        "company": random.choice([
            "ABC Corp", "XYZ Inc", "Acme Ltd", "Global Services", "Tech Solutions",
            "Smith & Co", "Johnson LLC", "Enterprise Systems", "Quality Products",
            "Worldwide Logistics", "Premier Supplies", "Elite Services", "First Choice",
            "Best Value", "Superior Products", "Innovative Solutions", "Strategic Partners",
            "Dynamic Systems", "Reliable Services", "Professional Solutions"
        ]),
        "invoice_num": f"INV-{random.randint(10000, 99999)}",
        "reference": f"REF-{random.randint(10000, 99999)}",
        "account_num": f"ACCT-{random.randint(10000, 99999)}",
        "po_num": f"PO-{random.randint(10000, 99999)}"
    }

    # Purpose code specific placeholders
    if purpose_code == "GDDS":
        placeholders.update({
            "goods": random.choice([
                "office supplies", "computer equipment", "furniture", "electronics",
                "machinery", "tools", "raw materials", "inventory", "retail products",
                "hardware", "appliances", "equipment", "components", "parts",
                "merchandise", "wholesale goods", "manufacturing supplies", "industrial equipment",
                "consumer goods", "packaging materials"
            ])
        })
    elif purpose_code in ["SCVE", "SERV"]:
        placeholders.update({
            "service": random.choice([
                "consulting", "maintenance", "repair", "installation", "support",
                "professional", "technical", "administrative", "management", "marketing",
                "advertising", "legal", "accounting", "IT", "HR", "training",
                "design", "development", "research", "analysis"
            ])
        })
    elif purpose_code == "EDUC":
        placeholders.update({
            "institution": random.choice([
                "University of Oxford", "Harvard University", "Stanford University",
                "MIT", "Cambridge University", "Yale University", "Princeton University",
                "Columbia University", "UC Berkeley", "Chicago University", "Local College",
                "Community College", "Technical Institute", "Business School", "Law School",
                "Medical School", "Engineering School", "Art Institute", "Language School",
                "Online University"
            ]),
            "semester": random.choice([
                "Fall 2023", "Spring 2024", "Summer 2023", "Winter 2023",
                "Fall 2022", "Spring 2023", "Summer 2022", "Winter 2022",
                "First semester", "Second semester", "Third semester", "Fourth semester",
                "First quarter", "Second quarter", "Third quarter", "Fourth quarter",
                "Academic year 2023-2024", "Academic year 2022-2023"
            ]),
            "student_name": random.choice([
                "John Smith", "Jane Doe", "Michael Johnson", "Emily Williams",
                "David Brown", "Sarah Miller", "Robert Davis", "Jennifer Wilson",
                "William Taylor", "Elizabeth Anderson", "Richard Thomas", "Susan Jackson",
                "Joseph White", "Margaret Harris", "Charles Martin", "Karen Thompson",
                "Thomas Garcia", "Nancy Martinez", "Daniel Robinson", "Lisa Clark"
            ]),
            "course": random.choice([
                "Business Administration", "Computer Science", "Engineering", "Medicine",
                "Law", "Economics", "Finance", "Marketing", "Psychology", "Sociology",
                "History", "English", "Mathematics", "Physics", "Chemistry", "Biology",
                "Art", "Music", "Philosophy", "Political Science"
            ])
        })
    elif purpose_code == "INSU":
        placeholders.update({
            "insurance_type": random.choice([
                "life", "health", "auto", "home", "property", "liability",
                "business", "travel", "disability", "dental", "vision",
                "pet", "umbrella", "flood", "earthquake", "renters",
                "motorcycle", "boat", "RV", "commercial"
            ]),
            "policy_num": f"POL-{random.randint(10000, 99999)}"
        })
    elif purpose_code in ["TAXS", "VATX", "WHLD"]:
        placeholders.update({
            "tax_period": random.choice([
                "Q1 2023", "Q2 2023", "Q3 2023", "Q4 2023",
                "Q1 2022", "Q2 2022", "Q3 2022", "Q4 2022",
                "January 2023", "February 2023", "March 2023", "April 2023",
                "May 2023", "June 2023", "July 2023", "August 2023",
                "September 2023", "October 2023", "November 2023", "December 2023",
                "FY 2022-2023", "FY 2021-2022"
            ]),
            "tax_authority": random.choice([
                "IRS", "HMRC", "CRA", "ATO", "IRD", "SARS", "Federal Tax Authority",
                "State Tax Department", "Local Tax Office", "Revenue Agency",
                "Tax Commission", "Treasury Department", "Finance Ministry",
                "Tax Administration", "Revenue Service", "Customs and Revenue",
                "Internal Revenue", "Tax Bureau", "Revenue Board", "Tax Department"
            ]),
            "tax_type": random.choice([
                "income", "corporate", "sales", "property", "payroll", "capital gains",
                "dividend", "interest", "royalty", "excise", "customs", "import",
                "export", "stamp", "gift", "estate", "wealth", "luxury", "carbon", "digital"
            ])
        })
    elif purpose_code == "SALA":
        placeholders.update({
            "month": random.choice([
                "January 2023", "February 2023", "March 2023", "April 2023",
                "May 2023", "June 2023", "July 2023", "August 2023",
                "September 2023", "October 2023", "November 2023", "December 2023",
                "January 2022", "February 2022", "March 2022", "April 2022",
                "May 2022", "June 2022", "July 2022", "August 2022",
                "September 2022", "October 2022", "November 2022", "December 2022"
            ])
        })
    elif purpose_code in ["CCRD", "DCRD", "ICCP", "IDCP"]:
        placeholders.update({
            "last_digits": f"{random.randint(1000, 9999)}",
            "month": random.choice([
                "January 2023", "February 2023", "March 2023", "April 2023",
                "May 2023", "June 2023", "July 2023", "August 2023",
                "September 2023", "October 2023", "November 2023", "December 2023"
            ])
        })
    elif purpose_code == "INTE":
        placeholders.update({
            "month": random.choice([
                "January 2023", "February 2023", "March 2023", "April 2023",
                "May 2023", "June 2023", "July 2023", "August 2023",
                "September 2023", "October 2023", "November 2023", "December 2023"
            ]),
            "loan_num": f"LOAN-{random.randint(10000, 99999)}",
            "investment_type": random.choice([
                "savings account", "certificate of deposit", "money market account",
                "bond", "treasury bill", "fixed deposit", "term deposit",
                "mutual fund", "stock", "ETF", "REIT", "index fund",
                "retirement account", "pension fund", "annuity", "life insurance",
                "real estate", "private equity", "venture capital", "hedge fund"
            ])
        })
    elif purpose_code == "CORT":
        placeholders.update({
            "case_num": f"CASE-{random.randint(10000, 99999)}",
            "legal_matter": random.choice([
                "civil case", "criminal case", "family law", "divorce", "custody",
                "probate", "estate", "bankruptcy", "foreclosure", "eviction",
                "personal injury", "medical malpractice", "product liability", "class action",
                "intellectual property", "patent", "trademark", "copyright", "contract dispute",
                "employment law"
            ])
        })

    # Fill the template with the placeholders
    filled_template = template
    for key, value in placeholders.items():
        filled_template = filled_template.replace(f"{{{key}}}", value)

    return filled_template

def generate_synthetic_data(output_file, samples_per_code=100):
    """Generate synthetic data for the worst-performing purpose codes."""
    # Load purpose codes and category purpose codes
    purpose_codes = load_purpose_codes()
    category_purpose_codes = load_category_purpose_codes()

    # Create a dataframe to store the synthetic data
    data = []

    # Generate synthetic data for each purpose code
    for purpose_code in WORST_PERFORMING_CODES:
        print(f"Generating synthetic data for purpose code: {purpose_code}")

        # Get the category purpose code for this purpose code
        category_purpose_code = get_category_for_purpose(purpose_code, category_purpose_codes)
        print(f"  Mapped to category purpose code: {category_purpose_code}")

        # Generate narrations for this purpose code
        narrations = generate_narrations_for_purpose_code(purpose_code, samples_per_code)

        # Add the narrations to the dataframe
        for narration in narrations:
            # Add the data point
            data.append({
                "narration": narration,
                "purpose_code": purpose_code,
                "category_purpose_code": category_purpose_code
            })

    # Convert to dataframe
    df = pd.DataFrame(data)

    # Save to CSV
    df.to_csv(output_file, index=False)

    print(f"Generated {len(df)} synthetic data points for {len(WORST_PERFORMING_CODES)} purpose codes")
    print(f"Saved to {output_file}")

    return df

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    os.makedirs("data", exist_ok=True)

    # Generate synthetic data
    output_file = f"data/synthetic_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df = generate_synthetic_data(output_file, samples_per_code=200)
