"""
Category Purpose Mapper for Purpose Code Classification.

This module provides a comprehensive mapping system for converting purpose codes
to category purpose codes with semantic context awareness.
"""

import os
import json
import logging
import re
from purpose_classifier.semantic_pattern_matcher import SemanticPatternMatcher

logger = logging.getLogger(__name__)

class CategoryPurposeMapper:
    """
    Maps purpose codes to category purpose codes with semantic context awareness.

    This class provides a comprehensive mapping system for converting purpose codes
    to category purpose codes, taking into account the semantic context of the narration.
    """

    def __init__(self, purpose_codes_path=None, category_purpose_codes_path=None, matcher=None):
        """
        Initialize the category purpose mapper.

        Args:
            purpose_codes_path: Path to the purpose codes JSON file
            category_purpose_codes_path: Path to the category purpose codes JSON file
            matcher: Optional existing SemanticPatternMatcher instance to use
        """
        # Initialize the semantic pattern matcher
        self.matcher = matcher if matcher is not None else SemanticPatternMatcher()

        # Load purpose codes and category purpose codes
        self.purpose_codes = self._load_purpose_codes(purpose_codes_path)
        self.category_purpose_codes = self._load_category_purpose_codes(category_purpose_codes_path)

        # Initialize the direct mapping dictionary
        self._initialize_direct_mappings()

        # Initialize semantic patterns for category purpose codes
        self._initialize_semantic_patterns()

    def _load_purpose_codes(self, purpose_codes_path):
        """
        Load purpose codes from the JSON file.

        Args:
            purpose_codes_path: Path to the purpose codes JSON file

        Returns:
            dict: Purpose codes dictionary
        """
        if purpose_codes_path is None:
            # Use default path
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            purpose_codes_path = os.path.join(base_dir, 'data', 'purpose_codes.json')

        try:
            with open(purpose_codes_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading purpose codes: {e}")
            return {}

    def _load_category_purpose_codes(self, category_purpose_codes_path):
        """
        Load category purpose codes from the JSON file.

        Args:
            category_purpose_codes_path: Path to the category purpose codes JSON file

        Returns:
            dict: Category purpose codes dictionary
        """
        if category_purpose_codes_path is None:
            # Use default path
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            category_purpose_codes_path = os.path.join(base_dir, 'data', 'category_purpose_codes.json')

        try:
            with open(category_purpose_codes_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading category purpose codes: {e}")
            return {}

    def _initialize_direct_mappings(self):
        """Initialize direct mappings from purpose codes to category purpose codes."""
        # Direct purpose code to category purpose code mappings
        self.direct_mappings = {
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
            'DIVD': 'DIVI',  # Dividend to Dividend
            'DIVI': 'DIVI',  # Dividend to Dividend

            # Investment and Securities
            'INVS': 'SECU',  # Investment to Securities
            'SECU': 'SECU',  # Securities to Securities

            # Loans
            'LOAN': 'LOAN',  # Loan to Loan
            'LOAR': 'LOAN',  # Loan Repayment to Loan

            # Services and Goods
            'SCVE': 'SUPP',  # Services to Supplier
            'GDDS': 'GDDS',  # Goods to Goods
            'SUPP': 'SUPP',  # Supplier to Supplier

            # Government and Tax
            'TAXS': 'TAXS',  # Tax to Tax
            'VATX': 'VATX',  # VAT to VAT
            'WHLD': 'WHLD',  # Withholding to Withholding (not TAXS)
            'GOVT': 'GOVT',  # Government to Government
            'SSBE': 'SSBE',  # Social Security Benefit to Social Security Benefit

            # Treasury and Cash Management
            'TREA': 'TREA',  # Treasury to Treasury
            'CASH': 'CASH',  # Cash Management to Cash Management
            'INTC': 'INTC',  # Intra-Company to Intra-Company

            # Card Payments
            'CCRD': 'CCRD',  # Credit Card to Credit Card
            'DCRD': 'DCRD',  # Debit Card to Debit Card
            'ICCP': 'ICCP',  # Irrevocable Credit Card to Irrevocable Credit Card
            'IDCP': 'IDCP',  # Irrevocable Debit Card to Irrevocable Debit Card
            'CBLK': 'CBLK',  # Card Bulk Clearing to Card Bulk Clearing

            # Trade and Settlement
            'CORT': 'CORT',  # Trade Settlement to Trade Settlement
            'TRAD': 'TRAD',  # Trade to Trade

            # Interest
            'INTE': 'INTE',  # Interest to Interest

            # Insurance
            'INSU': 'SECU',  # Insurance to Securities
            'GOVI': 'GOVI',  # Government Insurance to Government Insurance

            # Electronic Payments
            'EPAY': 'EPAY',  # ePayment to ePayment

            # Utility Bills
            'UBIL': 'UBIL',  # Utility Bill to Utility Bill
            'ELEC': 'UBIL',  # Electricity to Utility Bill
            'GASB': 'UBIL',  # Gas Bill to Utility Bill
            'PHON': 'UBIL',  # Phone Bill to Utility Bill
            'NWCH': 'UBIL',  # Network Charge to Utility Bill
            'NWCM': 'UBIL',  # Network Communication to Utility Bill
            'TBIL': 'UBIL',  # Telephone Bill to Utility Bill
            'OTLC': 'UBIL',  # Other Telecom to Utility Bill

            # Foreign Exchange
            'FREX': 'FREX',  # Foreign Exchange to Foreign Exchange

            # Customs
            'CUST': 'CUST',  # Customs to Customs

            # Hedging
            'HEDG': 'HEDG',  # Hedging to Hedging
        }

    def _initialize_semantic_patterns(self):
        """Initialize semantic patterns for category purpose codes."""
        # Semantic patterns for category purpose codes
        self.semantic_patterns = {
            # Supplier Payment (SUPP)
            'SUPP': [
                {'keywords': ['supplier', 'payment'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['vendor', 'payment'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['invoice', 'payment'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['bill', 'payment'], 'proximity': 5, 'weight': 0.8},
                {'keywords': ['purchase', 'order'], 'proximity': 5, 'weight': 0.8},
            ],

            # Goods (GDDS)
            'GDDS': [
                {'keywords': ['goods', 'purchase'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['merchandise', 'purchase'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['product', 'purchase'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['retail', 'purchase'], 'proximity': 5, 'weight': 0.8},
                {'keywords': ['wholesale', 'purchase'], 'proximity': 5, 'weight': 0.8},
            ],

            # Salary Payment (SALA)
            'SALA': [
                {'keywords': ['salary', 'payment'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['wage', 'payment'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['payroll', 'payment'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['compensation', 'payment'], 'proximity': 5, 'weight': 0.8},
                {'keywords': ['bonus', 'payment'], 'proximity': 5, 'weight': 0.8},
            ],

            # Fee Collection (FCOL)
            'FCOL': [
                {'keywords': ['fee', 'collection'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['tuition', 'fee'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['service', 'fee'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['subscription', 'fee'], 'proximity': 5, 'weight': 0.8},
                {'keywords': ['membership', 'fee'], 'proximity': 5, 'weight': 0.8},
            ],

            # Securities (SECU)
            'SECU': [
                {'keywords': ['securities', 'investment'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['stock', 'purchase'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['bond', 'purchase'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['mutual', 'fund'], 'proximity': 5, 'weight': 0.8},
                {'keywords': ['portfolio', 'investment'], 'proximity': 5, 'weight': 0.8},
            ],

            # Loan (LOAN)
            'LOAN': [
                {'keywords': ['loan', 'disbursement'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['loan', 'repayment'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['mortgage', 'payment'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['credit', 'facility'], 'proximity': 5, 'weight': 0.8},
                {'keywords': ['debt', 'repayment'], 'proximity': 5, 'weight': 0.8},
            ],

            # Tax Payment (TAXS)
            'TAXS': [
                {'keywords': ['tax', 'payment'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['income', 'tax'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['property', 'tax'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['sales', 'tax'], 'proximity': 5, 'weight': 0.8},
                {'keywords': ['corporate', 'tax'], 'proximity': 5, 'weight': 0.8},
            ],

            # VAT Payment (VATX)
            'VATX': [
                {'keywords': ['vat', 'payment'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['value', 'added', 'tax'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['vat', 'return'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['vat', 'refund'], 'proximity': 5, 'weight': 0.8},
                {'keywords': ['vat', 'collection'], 'proximity': 5, 'weight': 0.8},
            ],

            # Dividend Payment (DIVI)
            'DIVI': [
                {'keywords': ['dividend', 'payment'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['dividend', 'distribution'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['shareholder', 'dividend'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['profit', 'distribution'], 'proximity': 5, 'weight': 0.8},
                {'keywords': ['stock', 'dividend'], 'proximity': 5, 'weight': 0.8},
            ],

            # Trade Services (TRAD)
            'TRAD': [
                {'keywords': ['trade', 'services'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['trade', 'payment'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['import', 'export'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['international', 'trade'], 'proximity': 5, 'weight': 0.8},
                {'keywords': ['trade', 'finance'], 'proximity': 5, 'weight': 0.8},
            ],

            # Trade Settlement Payment (CORT)
            'CORT': [
                {'keywords': ['trade', 'settlement'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['correspondent', 'banking'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['cover', 'payment'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['settlement', 'instruction'], 'proximity': 5, 'weight': 0.8},
                {'keywords': ['clearing', 'settlement'], 'proximity': 5, 'weight': 0.8},
            ],

            # Treasury Payment (TREA)
            'TREA': [
                {'keywords': ['treasury', 'payment'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['treasury', 'operation'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['treasury', 'management'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['treasury', 'services'], 'proximity': 5, 'weight': 0.8},
                {'keywords': ['treasury', 'transfer'], 'proximity': 5, 'weight': 0.8},
            ],

            # Cash Management Transfer (CASH)
            'CASH': [
                {'keywords': ['cash', 'management'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['liquidity', 'management'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['cash', 'pooling'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['cash', 'concentration'], 'proximity': 5, 'weight': 0.8},
                {'keywords': ['cash', 'transfer'], 'proximity': 5, 'weight': 0.8},
            ],

            # Intra-Company Payment (INTC)
            'INTC': [
                {'keywords': ['intra', 'company'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['intercompany', 'transfer'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['internal', 'transfer'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['subsidiary', 'transfer'], 'proximity': 5, 'weight': 0.8},
                {'keywords': ['affiliate', 'transfer'], 'proximity': 5, 'weight': 0.8},
            ],

            # Credit Card Payment (CCRD)
            'CCRD': [
                {'keywords': ['credit', 'card'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['credit', 'card', 'payment'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['credit', 'card', 'bill'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['credit', 'card', 'settlement'], 'proximity': 5, 'weight': 0.8},
                {'keywords': ['credit', 'card', 'transaction'], 'proximity': 5, 'weight': 0.8},
            ],

            # Debit Card Payment (DCRD)
            'DCRD': [
                {'keywords': ['debit', 'card'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['debit', 'card', 'payment'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['debit', 'card', 'transaction'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['debit', 'card', 'settlement'], 'proximity': 5, 'weight': 0.8},
                {'keywords': ['debit', 'card', 'purchase'], 'proximity': 5, 'weight': 0.8},
            ],

            # Utility Bill (UBIL)
            'UBIL': [
                {'keywords': ['utility', 'bill'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['electricity', 'bill'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['gas', 'bill'], 'proximity': 5, 'weight': 0.9},
                {'keywords': ['water', 'bill'], 'proximity': 5, 'weight': 0.8},
                {'keywords': ['phone', 'bill'], 'proximity': 5, 'weight': 0.8},
            ],
        }

        # Semantic terms for similarity matching
        self.semantic_terms = {
            'SUPP': ['supplier', 'vendor', 'invoice', 'bill', 'purchase'],
            'GDDS': ['goods', 'merchandise', 'product', 'retail', 'wholesale'],
            'SALA': ['salary', 'wage', 'payroll', 'compensation', 'bonus'],
            'FCOL': ['fee', 'tuition', 'service fee', 'subscription', 'membership'],
            'SECU': ['securities', 'stock', 'bond', 'mutual fund', 'portfolio'],
            'LOAN': ['loan', 'mortgage', 'credit', 'debt', 'financing'],
            'TAXS': ['tax', 'income tax', 'property tax', 'sales tax', 'corporate tax'],
            'VATX': ['vat', 'value added tax', 'vat return', 'vat refund', 'vat collection'],
            'DIVI': ['dividend', 'shareholder', 'profit distribution', 'stock dividend'],
            'TRAD': ['trade', 'import', 'export', 'international trade', 'trade finance'],
            'CORT': ['trade settlement', 'correspondent banking', 'cover payment', 'clearing'],
            'TREA': ['treasury', 'treasury operation', 'treasury management'],
            'CASH': ['cash management', 'liquidity', 'cash pooling', 'cash concentration'],
            'INTC': ['intra company', 'intercompany', 'internal transfer', 'subsidiary'],
            'CCRD': ['credit card', 'credit card payment', 'credit card bill'],
            'DCRD': ['debit card', 'debit card payment', 'debit card transaction'],
            'UBIL': ['utility bill', 'electricity bill', 'gas bill', 'water bill', 'phone bill'],
        }

        # Message type preferences for category purpose codes
        self.message_type_preferences = {
            'MT103': {
                'SUPP': 1.2,  # Supplier payments are common in MT103
                'GDDS': 1.2,  # Goods payments are common in MT103
                'SALA': 1.2,  # Salary payments are common in MT103
                'FCOL': 1.2,  # Fee collection is common in MT103
                'TAXS': 1.2,  # Tax payments are common in MT103
                'VATX': 1.2,  # VAT payments are common in MT103
                'UBIL': 1.2,  # Utility bills are common in MT103
                'LOAN': 1.1,  # Loan payments are somewhat common in MT103
                'INTC': 0.8,  # Intra-company payments are less common in MT103
                'CASH': 0.8,  # Cash management transfers are less common in MT103
                'CORT': 0.7,  # Trade settlement payments are rare in MT103
            },
            'MT202': {
                'INTC': 1.3,  # Interbank transfers are very common in MT202
                'CASH': 1.3,  # Cash management is very common in MT202
                'TREA': 1.3,  # Treasury operations are very common in MT202
                'CORT': 1.2,  # Trade settlement is common in MT202
                'SECU': 1.2,  # Securities settlement is common in MT202
                'SUPP': 0.7,  # Supplier payments are less common in MT202
                'GDDS': 0.7,  # Goods payments are less common in MT202
                'SALA': 0.7,  # Salary payments are less common in MT202
            },
            'MT202COV': {
                'CORT': 1.3,  # Correspondent banking is very common in MT202COV
                'SECU': 1.2,  # Securities settlement is common in MT202COV
                'INTC': 1.2,  # Interbank transfers are common in MT202COV
                'SUPP': 0.6,  # Supplier payments are rare in MT202COV
                'GDDS': 0.6,  # Goods payments are rare in MT202COV
                'SALA': 0.6,  # Salary payments are rare in MT202COV
            }
        }

    def map_purpose_to_category(self, purpose_code, narration=None, message_type=None, confidence=None):
        """
        Map a purpose code to a category purpose code.

        Args:
            purpose_code: The purpose code to map
            narration: Optional narration text for context-aware mapping
            message_type: Optional message type for context-aware mapping
            confidence: Optional confidence score of the purpose code

        Returns:
            tuple: (category_purpose_code, confidence, reason)
        """
        # Check if purpose code has a direct mapping
        if purpose_code in self.direct_mappings:
            category_purpose_code = self.direct_mappings[purpose_code]
            category_confidence = 0.95 if confidence is None else min(confidence * 1.1, 0.95)
            reason = f"Direct mapping from {purpose_code} to {category_purpose_code}"
            return category_purpose_code, category_confidence, reason

        # If message type is provided, use message type preferences first
        if message_type:
            # MT103 is commonly used for customer payments
            if message_type == 'MT103':
                category_code = 'SUPP'  # Default to supplier payment for MT103
                category_confidence = 0.7
                reason = f"MT103 message type with payment context"
                return category_code, category_confidence, reason

            # MT202 is commonly used for interbank transfers
            elif message_type == 'MT202':
                category_code = 'INTC'  # Default to interbank transfer for MT202
                category_confidence = 0.7
                reason = f"MT202 message type default"
                return category_code, category_confidence, reason

            # MT202COV is commonly used for cover payments
            elif message_type == 'MT202COV':
                category_code = 'CORT'  # Default to trade settlement for MT202COV
                category_confidence = 0.7
                reason = f"MT202COV message type default"
                return category_code, category_confidence, reason

        # If narration is provided, try semantic mapping
        if narration:
            # Convert narration to lowercase for case-insensitive matching
            narration_lower = narration.lower()

            # Try direct keyword matching first (highest confidence)
            for category_code, terms in self.semantic_terms.items():
                for term in terms:
                    # Only match if the term is a complete phrase in the narration
                    if term.lower() in narration_lower and len(term) > 3:
                        # For single word terms, make sure it's a whole word match
                        if ' ' not in term:
                            words = self.matcher.tokenize(narration_lower)
                            if term.lower() in words:
                                category_confidence = 0.9
                                reason = f"Keyword match: {term} for {category_code}"
                                return category_code, category_confidence, reason
                        else:
                            category_confidence = 0.9
                            reason = f"Keyword match: {term} for {category_code}"
                            return category_code, category_confidence, reason

            # For simple "Payment" narration with OTHR purpose code, use SUPP as default
            if purpose_code == 'OTHR' and narration_lower == 'payment':
                category_code = 'SUPP'
                category_confidence = 0.6
                reason = f"Default mapping for generic payment narration"
                return category_code, category_confidence, reason

            # Try semantic pattern matching
            for category_code, patterns in self.semantic_patterns.items():
                for pattern in patterns:
                    keywords = pattern['keywords']
                    proximity = pattern['proximity']
                    weight = pattern['weight']

                    # Skip patterns with just 'payment' for OTHR purpose code
                    if purpose_code == 'OTHR' and len(keywords) == 1 and keywords[0] == 'payment':
                        continue

                    # For SALA pattern, require more specific match than just 'payment'
                    if category_code == 'SALA' and 'payment' in keywords and 'salary' not in narration_lower:
                        continue

                    # For FCOL pattern, require more specific match than just 'payment'
                    if category_code == 'FCOL' and 'fee' in keywords and 'fee' not in narration_lower:
                        continue

                    # Check if keywords are in proximity
                    words = self.matcher.tokenize(narration_lower)
                    if self.matcher.keywords_in_proximity(words, keywords, proximity):
                        category_confidence = min(0.85, weight)
                        reason = f"Pattern match: {keywords} for {category_code}"
                        return category_code, category_confidence, reason

            # Try semantic similarity matching
            for category_code, terms in self.semantic_terms.items():
                for term in terms:
                    words = self.matcher.tokenize(narration_lower)
                    for word in words:
                        similarity = self.matcher.semantic_similarity(word, term)
                        if similarity >= 0.7:
                            category_confidence = min(0.8, similarity)
                            reason = f"Semantic similarity: {word} ~ {term} for {category_code}"
                            return category_code, category_confidence, reason

        # Fallback strategies based on purpose code first letter
        # (This code is only reached if no other mapping was found)

        # Check if narration contains payment-related terms
        if narration and 'payment' in narration.lower():
            # Default to SUPP for payment-related narrations
            category_code = 'SUPP'
            category_confidence = 0.6
            reason = f"Fallback based on payment-related narration"
            return category_code, category_confidence, reason

        # Fallback: Use purpose code first letter to determine category
        first_letter = purpose_code[0] if purpose_code and len(purpose_code) > 0 else ''

        if first_letter == 'S':
            # S codes are often service-related
            category_code = 'SUPP'
            category_confidence = 0.6
            reason = f"Fallback based on purpose code first letter: {first_letter}"
            return category_code, category_confidence, reason

        elif first_letter == 'G':
            # G codes are often goods-related
            category_code = 'GDDS'
            category_confidence = 0.6
            reason = f"Fallback based on purpose code first letter: {first_letter}"
            return category_code, category_confidence, reason

        elif first_letter == 'T':
            # T codes are often tax or trade-related
            if 'TAX' in purpose_code:
                category_code = 'TAXS'
            else:
                category_code = 'TRAD'
            category_confidence = 0.6
            reason = f"Fallback based on purpose code first letter: {first_letter}"
            return category_code, category_confidence, reason

        elif first_letter == 'I':
            # I codes are often investment-related
            category_code = 'SECU'
            category_confidence = 0.6
            reason = f"Fallback based on purpose code first letter: {first_letter}"
            return category_code, category_confidence, reason

        elif first_letter == 'L':
            # L codes are often loan-related
            category_code = 'LOAN'
            category_confidence = 0.6
            reason = f"Fallback based on purpose code first letter: {first_letter}"
            return category_code, category_confidence, reason

        # Final fallback: Use SUPP as a safe default (never use OTHR)
        category_code = 'SUPP'
        category_confidence = 0.5
        reason = f"Default fallback for unknown purpose code: {purpose_code}"
        return category_code, category_confidence, reason
