"""
Targeted domain enhancer for specific problematic purpose codes.

This enhancer focuses on the specific problematic cases identified in testing:
1. LOAN vs LOAR (Loan vs Loan Repayment)
2. VATX vs TAXS (Value Added Tax Payment vs Tax Payment)
3. SSBE vs GBEN (Social Security Benefit vs Government Benefit)
4. SCVE vs SERV (Purchase of Services vs Service Charge)
"""

import re
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer
import logging

logger = logging.getLogger(__name__)

class TargetedEnhancer(SemanticEnhancer):
    """
    Enhancer for specific problematic purpose codes.

    This enhancer improves the classification of specific purpose codes that
    have been identified as problematic in testing.
    """

    def __init__(self, matcher=None):
        super().__init__(matcher=matcher)
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize semantic patterns and contexts."""
        # Direct keywords with purpose codes
        self.direct_keywords = {}

        # Semantic context patterns
        self.context_patterns = [
            {
                'purpose_code': 'OTHR',
                'keywords': ['loan', 'credit', 'facility', 'mortgage', 'borrowing', 'lending'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['loan', 'repayment', 'repayment', 'loan', 'repay', 'loan', 'loan', 'payment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['vat', 'value', 'added', 'tax', 'sales', 'tax', 'gst'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['tax', 'added', 'income', 'tax', 'corporate', 'tax', 'property', 'tax'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['social', 'security', 'benefit', 'social', 'security', 'benefit'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['government', 'benefit', 'gov', 'benefit', 'state', 'benefit', 'public', 'benefit'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'purchase', 'purchase', 'service', 'professional', 'service', 'consulting', 'service', 'fee', 'collection', 'for', 'service'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'charge', 'service', 'fee', 'maintenance', 'fee', 'account', 'fee', 'processing', 'fee'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['loan', 'repayment', 'mortgage', 'repayment', 'credit', 'repayment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['repayment', 'loan', 'repayment', 'mortgage', 'repayment', 'credit'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['loan', 'credit', 'mortgage', 'repayment', 'payment', 'installment', 'settlement', 'amortization'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['repayment', 'payment', 'installment', 'settlement', 'amortization', 'for', 'loan', 'credit', 'mortgage'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['repay', 'pay', 'settle', 'paying', 'off', 'paying', 'back', 'loan', 'credit', 'mortgage', 'debt'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['loan', 'credit', 'mortgage', 'debt', 'repay', 'pay', 'settle', 'paying', 'off', 'paying', 'back'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['mortgage', 'payment', 'mortgage', 'installment', 'home', 'loan', 'payment', 'house', 'payment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'installment', 'for', 'mortgage', 'home', 'loan', 'house', 'loan', 'property', 'loan'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['emi', 'equated', 'monthly', 'installment', 'loan', 'mortgage', 'credit'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['loan', 'mortgage', 'credit', 'emi', 'equated', 'monthly', 'installment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['monthly', 'quarterly', 'regular', 'installment', 'payment', 'loan', 'mortgage', 'credit'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['principal', 'and', 'interest', 'payment', 'repayment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'repayment', 'principal', 'and', 'interest'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['loan', 'disbursement', 'loan', 'advance', 'loan', 'drawdown', 'loan', 'facility', 'loan', 'agreement', 'loan', 'origination'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['mortgage', 'disbursement', 'mortgage', 'advance', 'mortgage', 'drawdown', 'mortgage', 'facility', 'mortgage', 'agreement', 'mortgage', 'origination'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['loan', 'credit', 'mortgage', 'disbursement', 'advance', 'drawdown', 'facility', 'agreement', 'origination', 'approval', 'sanction'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['disbursement', 'advance', 'drawdown', 'issuance', 'provision', 'for', 'loan', 'credit', 'mortgage'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['new', 'approved', 'granted', 'sanctioned', 'issued', 'loan', 'credit', 'mortgage', 'facility'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['loan', 'credit', 'mortgage', 'facility', 'new', 'approved', 'granted', 'sanctioned', 'issued'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['loan', 'credit', 'mortgage', 'for', 'purchase', 'buy', 'acquire', 'fund', 'finance'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['personal', 'consumer', 'retail', 'individual', 'loan', 'credit', 'borrowing'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['loan', 'mortgage', 'not', 'interbank', 'customer', 'personal', 'individual', 'retail', 'consumer'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['loan', 'mortgage', 'not', 'purchase', 'payment', 'repayment', 'facility', 'agreement'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['credit', 'line', 'line', 'credit', 'credit', 'facility', 'drawdown', 'utilization', 'use'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['drawdown', 'utilization', 'use', 'from', 'credit', 'line', 'line', 'credit', 'credit', 'facility'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['interbank', 'inter-bank', 'bank', 'bank', 'between', 'banks', 'bank', 'transfer'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['interbank', 'inter-bank', 'transfer', 'payment', 'settlement', 'transaction', 'funding', 'liquidity'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['rtgs', 'real', 'time', 'gross', 'settlement', 'payment', 'transfer', 'transaction'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['transfer', 'payment', 'settlement', 'transaction', 'funding', 'liquidity', 'interbank', 'inter-bank'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['bank', 'financial', 'institution', 'with', 'between', 'bank', 'financial', 'institution'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['nostro', 'vostro', 'loro', 'account', 'settlement', 'funding', 'transfer'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['correspondent', 'banking', 'correspondent', 'bank', 'transfer', 'payment', 'settlement'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['property', 'real', 'estate', 'house', 'apartment', 'land', 'condo', 'condominium', 'flat', 'purchase', 'buy', 'acquisition', 'buying'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['purchase', 'buy', 'acquisition', 'buying', 'for', 'property', 'real', 'estate', 'house', 'apartment', 'land', 'condo', 'condominium', 'flat'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['down', 'payment', 'deposit', 'earnest', 'money', 'closing', 'costs', 'for', 'property', 'real', 'estate', 'house', 'apartment', 'land', 'condo', 'condominium', 'flat'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['real', 'estate', 'property', 'transaction', 'deal', 'closing', 'settlement'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['home', 'house', 'apartment', 'condo', 'condominium', 'flat', 'closing', 'settlement', 'purchase', 'completion'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['property', 'real', 'estate', 'house', 'apartment', 'purchase', 'buy', 'acquisition', 'not', 'loan', 'not', 'mortgage', 'without', 'financing'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['account', 'account', 'number', 'acct', 'account'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['account', 'acct', 'payment', 'transfer', 'deposit', 'credit', 'debit'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'transfer', 'deposit', 'credit', 'debit', 'into', 'for', 'from', 'account', 'acct'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['loan', 'mortgage', 'credit', 'account', 'acct', 'number'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['account', 'acct', 'number', 'loan', 'mortgage', 'credit'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['loan', 'mortgage', 'servicing', 'processing', 'account', 'payment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['loan', 'credit', 'syndication', 'participation', 'facility', 'arrangement'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['syndicated', 'club', 'loan', 'facility', 'credit'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['loan', 'credit', 'tranche', 'drawdown', 'utilization'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['bank', 'financial', 'institution', 'participation', 'share', 'loan', 'credit', 'facility'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['mortgage', 'home', 'loan', 'house', 'loan', 'repayment', 'payment', 'installment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['vat', 'value', 'added', 'tax', 'sales', 'tax', 'gst', 'goods', 'and', 'services', 'tax'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['vat', 'value', 'added', 'tax', 'sales', 'tax', 'gst', 'payment', 'remittance', 'return', 'bill', 'invoice'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'remittance', 'return', 'for', 'vat', 'value', 'added', 'tax', 'sales', 'tax', 'gst'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['quarterly', 'monthly', 'annual', 'vat', 'value', 'added', 'tax', 'sales', 'tax', 'gst'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['tax', 'added', 'income', 'tax', 'corporate', 'tax', 'property', 'tax', 'business', 'tax'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['tax', 'added', 'income', 'tax', 'corporate', 'tax', 'property', 'tax', 'payment', 'remittance', 'return', 'bill', 'invoice'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'remittance', 'return', 'for', 'tax', 'added', 'income', 'tax', 'corporate', 'tax', 'property', 'tax'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['quarterly', 'monthly', 'annual', 'tax', 'added', 'income', 'tax', 'corporate', 'tax', 'property', 'tax'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['social', 'security', 'benefit', 'social', 'security', 'benefit', 'payment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['social', 'security', 'benefit', 'payment', 'allowance', 'pension'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['benefit', 'payment', 'allowance', 'pension', 'from', 'social', 'security'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['retirement', 'disability', 'survivor', 'benefit', 'payment', 'allowance', 'social', 'security'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['government', 'gov', 'state', 'public', 'federal', 'benefit', 'payment', 'allowance', 'assistance', 'aid', 'grant'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['benefit', 'payment', 'allowance', 'assistance', 'aid', 'grant', 'from', 'government', 'gov', 'state', 'public', 'federal'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['unemployment', 'welfare', 'housing', 'child', 'benefit', 'payment', 'allowance', 'assistance', 'aid', 'grant'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['benefit', 'payment', 'allowance', 'assistance', 'aid', 'grant', 'unemployment', 'welfare', 'housing', 'child'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'purchase', 'purchase', 'service', 'professional', 'service', 'consulting', 'service'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['purchase', 'buy', 'acquire', 'procure', 'service', 'professional', 'service', 'consulting', 'service'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'professional', 'service', 'consulting', 'service', 'purchase', 'buy', 'acquire', 'procure'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['pay', 'ing', 'ment', 'transfer', 'ing', 'for', 'professional', 'consulting', 'business', 'service'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['fee', 'collection', 'for', 'service', 'service', 'fee', 'collection'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'charge', 'service', 'fee', 'maintenance', 'fee', 'account', 'fee', 'processing', 'fee'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['charge', 'fee', 'for', 'service', 'maintenance', 'account', 'processing'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'maintenance', 'account', 'processing', 'charge', 'fee'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['monthly', 'quarterly', 'annual', 'service', 'charge', 'service', 'fee', 'maintenance', 'fee'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['bank', 'financial', 'institution', 'service', 'charge', 'service', 'fee', 'maintenance', 'fee'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['fee', 'collection', 'for', 'service', 'service', 'fee', 'collection'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['fee', 'fees', 'collection', 'collecting', 'collected', 'for', 'service', 'services'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['collection', 'collecting', 'collected', 'for', 'fee', 'fees', 'for', 'service', 'services'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'services', 'fee', 'fees', 'collection', 'collecting', 'collected'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['loan', 'credit', 'mortgage', 'repayment', 'payment', 'installment', 'settlement'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['mortgage', 'home', 'loan', 'house', 'loan'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['loan', 'credit', 'mortgage', 'disbursement', 'advance', 'drawdown'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['tax', 'vat', 'duty', 'payment', 'remittance', 'return'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['vat', 'value', 'added', 'tax', 'sales', 'tax', 'gst'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['interbank', 'inter-bank', 'bank', 'bank'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['loan', 'credit', 'syndication', 'participation', 'facility'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['othr'],
                'proximity': 5,
                'weight': 0.8
            },
        ]

        # Semantic terms for similarity matching
        self.semantic_terms = []

    def enhance(self, purpose_code, confidence, narration, message_type=None):
        """
        Enhance the purpose code classification for specific problematic cases.
        Uses advanced pattern matching with regular expressions and semantic understanding.

        Args:
            purpose_code: The predicted purpose code
            confidence: The confidence score of the prediction
            narration: The narration text
            message_type: Optional SWIFT message type (MT103, MT202, etc.)

        Returns:
            tuple: (enhanced_purpose_code, enhanced_confidence, enhancement_type)
        """
        # Convert narration to lowercase for case-insensitive matching
        narration_lower = narration.lower()

        # 1. LOAN vs LOAR vs INTC vs PPTI - Enhanced pattern matching
        if purpose_code in ['LOAN', 'LOAR', 'INTC', 'PPTI', 'OTHR']:
            # Enhanced loan repayment patterns with semantic understanding
            loan_repayment_patterns = [
                # Specific loan repayment patterns with higher priority
                r'\b(loan\s+repayment|mortgage\s+repayment|credit\s+repayment)\b',
                r'\b(repayment\s+of\s+loan|repayment\s+of\s+mortgage|repayment\s+of\s+credit)\b',
                r'\b(loan|credit|mortgage)\b.*?\b(repayment|payment|installment|settlement|amortization)\b',
                r'\b(repayment|payment|installment|settlement|amortization)\b.*?\b(of|for|on)\b.*?\b(loan|credit|mortgage)\b',
                r'\b(repay|pay|settle|paying\s+off|paying\s+back)\b.*?\b(loan|credit|mortgage|debt)\b',
                r'\b(loan|credit|mortgage|debt)\b.*?\b(repay|pay|settle|paying\s+off|paying\s+back)\b',
                # Mortgage specific patterns
                r'\b(mortgage\s+payment|mortgage\s+installment|home\s+loan\s+payment|house\s+payment)\b',
                r'\b(payment|installment)\b.*?\b(for|of|on)\b.*?\b(mortgage|home\s+loan|house\s+loan|property\s+loan)\b',
                # EMI and installment patterns
                r'\b(emi|equated\s+monthly\s+installment)\b.*?\b(loan|mortgage|credit)\b',
                r'\b(loan|mortgage|credit)\b.*?\b(emi|equated\s+monthly\s+installment)\b',
                r'\b(monthly|quarterly|regular|scheduled)\b.*?\b(installment|payment)\b.*?\b(loan|mortgage|credit)\b',
                # Principal and interest patterns
                r'\b(principal\s+and\s+interest|p\s*&\s*i)\b.*?\b(payment|repayment)\b',
                r'\b(payment|repayment)\b.*?\b(principal\s+and\s+interest|p\s*&\s*i)\b',
                # Additional patterns for loan repayments
                r'\b(loan|credit|mortgage)\b.*?\b(due|schedule|scheduled)\b',
                r'\b(credit\s+card|card)\b.*?\b(payment|bill|statement)\b',
                r'\b(debt|balance)\b.*?\b(payment|reduction|paydown)\b',
                r'\b(final|last)\b.*?\b(payment|installment)\b.*?\b(loan|mortgage|credit)\b',
                r'\b(loan|mortgage|credit)\b.*?\b(payment|transfer|withdrawal)\b.*?\b(from\s+you|from\s+your|from\s+account|from\s+the\s+account)\b',
                # Additional patterns for loan installments
                r'\b(loan\s+installment|mortgage\s+installment|credit\s+installment)\b',
                r'\b(installment\s+for\s+loan|installment\s+for\s+mortgage|installment\s+for\s+credit)\b',
                r'\b(installment\s+payment|installment\s+due|installment\s+schedule)\b.*?\b(loan|mortgage|credit)\b',
                r'\b(loan|mortgage|credit)\b.*?\b(installment\s+payment|installment\s+due|installment\s+schedule)\b',
                # Additional patterns for loan settlements
                r'\b(loan\s+settlement|mortgage\s+settlement|credit\s+settlement)\b',
                r'\b(settlement\s+of\s+loan|settlement\s+of\s+mortgage|settlement\s+of\s+credit)\b',
                r'\b(settlement\s+payment|settlement\s+amount)\b.*?\b(loan|mortgage|credit)\b',
                r'\b(loan|mortgage|credit)\b.*?\b(settlement\s+payment|settlement\s+amount)\b',
                # Additional patterns for loan payments
                r'\b(loan\s+payment|mortgage\s+payment|credit\s+payment)\b',
                r'\b(payment\s+for\s+loan|payment\s+for\s+mortgage|payment\s+for\s+credit)\b',
                r'\b(payment\s+due|payment\s+schedule)\b.*?\b(loan|mortgage|credit)\b',
                r'\b(loan|mortgage|credit)\b.*?\b(payment\s+due|payment\s+schedule)\b'
            ]

            # Enhanced loan patterns with semantic understanding
            loan_patterns = [
                # Specific loan patterns with higher priority
                r'\b(loan\s+disbursement|loan\s+advance|loan\s+drawdown|loan\s+facility|loan\s+agreement|loan\s+origination)\b',
                r'\b(mortgage\s+disbursement|mortgage\s+advance|mortgage\s+drawdown|mortgage\s+facility|mortgage\s+agreement|mortgage\s+origination)\b',
                r'\b(loan|credit|mortgage)\b.*?\b(disbursement|advance|drawdown|facility|agreement|origination|approval|sanction)\b',
                r'\b(disbursement|advance|drawdown|issuance|provision)\b.*?\b(of|for)\b.*?\b(loan|credit|mortgage)\b',
                r'\b(new|approved|granted|sanctioned|issued)\b.*?\b(loan|credit|mortgage|facility)\b',
                r'\b(loan|credit|mortgage|facility)\b.*?\b(new|approved|granted|sanctioned|issued)\b',
                # Loan purpose patterns
                r'\b(loan|credit|mortgage)\b.*?\b(for|to)\b.*?\b(purchase|buy|acquire|fund|finance)\b',
                r'\b(personal|consumer|retail|individual)\b.*?\b(loan|credit|borrowing)\b',
                # Distinguish from interbank (INTC)
                r'\b(loan|mortgage)\b.*?\b(not.*?interbank|customer|personal|individual|retail|consumer)\b',
                # Distinguish from property purchase (PPTI)
                r'\b(loan|mortgage)\b.*?\b(not.*?purchase|payment|repayment|facility|agreement)\b',
                # Credit line patterns
                r'\b(credit\s+line|line\s+of\s+credit|credit\s+facility)\b.*?\b(drawdown|utilization|use)\b',
                r'\b(drawdown|utilization|use)\b.*?\b(of|from)\b.*?\b(credit\s+line|line\s+of\s+credit|credit\s+facility)\b',
                # Additional patterns for loan disbursements
                r'\b(loan|credit|mortgage)\b.*?\b(amount|principal|fund|money)\b',
                r'\b(loan|credit)\b.*?\b(transfer|deposit|payment)\b.*?\b(to\s+you|to\s+your|to\s+account|to\s+the\s+account)\b',
                r'\b(loan|credit)\b.*?\b(release|released)\b',
                r'\b(initial|first)\b.*?\b(loan|credit|mortgage)\b.*?\b(funding|disbursement|payment)\b',
                r'\b(loan|credit|mortgage)\b.*?\b(proceeds|payout)\b',
                # Additional patterns for loan origination
                r'\b(loan\s+origination|mortgage\s+origination|credit\s+origination)\b',
                r'\b(origination\s+of\s+loan|origination\s+of\s+mortgage|origination\s+of\s+credit)\b',
                r'\b(origination\s+fee|origination\s+charge)\b.*?\b(loan|mortgage|credit)\b',
                r'\b(loan|mortgage|credit)\b.*?\b(origination\s+fee|origination\s+charge)\b',
                # Additional patterns for loan approval
                r'\b(loan\s+approval|mortgage\s+approval|credit\s+approval)\b',
                r'\b(approval\s+of\s+loan|approval\s+of\s+mortgage|approval\s+of\s+credit)\b',
                r'\b(approval\s+for\s+loan|approval\s+for\s+mortgage|approval\s+for\s+credit)\b',
                r'\b(loan|mortgage|credit)\b.*?\b(approval\s+fee|approval\s+charge)\b',
                # Additional patterns for loan disbursement
                r'\b(loan\s+disbursement|mortgage\s+disbursement|credit\s+disbursement)\b',
                r'\b(disbursement\s+of\s+loan|disbursement\s+of\s+mortgage|disbursement\s+of\s+credit)\b',
                r'\b(disbursement\s+for\s+loan|disbursement\s+for\s+mortgage|disbursement\s+for\s+credit)\b',
                r'\b(loan|mortgage|credit)\b.*?\b(disbursement\s+fee|disbursement\s+charge)\b'
            ]

            # Enhanced interbank patterns to distinguish from LOAN
            interbank_patterns = [
                r'\b(interbank|inter-bank|bank\s+to\s+bank|between\s+banks|bank\s+transfer)\b',
                r'\b(interbank|inter-bank)\b.*?\b(transfer|payment|settlement|transaction|funding|liquidity)\b',
                r'\b(transfer|payment|settlement|transaction|funding|liquidity)\b.*?\b(interbank|inter-bank)\b',
                r'\b(bank|financial\s+institution|fi)\b.*?\b(to|with|between)\b.*?\b(bank|financial\s+institution|fi)\b',
                r'\b(nostro|vostro|loro)\b.*?\b(account|settlement|funding|transfer)\b',
                r'\b(correspondent\s+banking|correspondent\s+bank)\b.*?\b(transfer|payment|settlement)\b',
                r'\b(rtgs|real\s+time\s+gross\s+settlement)\b.*?\b(payment|transfer|settlement|transaction)\b',
                r'\b(payment|transfer|settlement|transaction)\b.*?\b(rtgs|real\s+time\s+gross\s+settlement)\b',
                r'\b(financial\s+institution)\b.*?\b(payment|transfer|settlement|transaction)\b',
                r'\b(payment|transfer|settlement|transaction)\b.*?\b(financial\s+institution)\b'
            ]

            # Enhanced property purchase patterns to distinguish from LOAN
            property_patterns = [
                r'\b(property|real\s+estate|house|apartment|land|condo|condominium|flat)\b.*?\b(purchase|buy|acquisition|buying)\b',
                r'\b(purchase|buy|acquisition|buying)\b.*?\b(of|for)\b.*?\b(property|real\s+estate|house|apartment|land|condo|condominium|flat)\b',
                r'\b(down\s+payment|deposit|earnest\s+money|closing\s+costs)\b.*?\b(for|on)\b.*?\b(property|real\s+estate|house|apartment|land|condo|condominium|flat)\b',
                r'\b(real\s+estate|property)\b.*?\b(transaction|deal|closing|settlement)\b',
                r'\b(home|house|apartment|condo|condominium|flat)\b.*?\b(closing|settlement|purchase\s+completion)\b',
                # Exclude mortgage loan patterns
                r'\b(property|real\s+estate|house|apartment)\b.*?\b(purchase|buy|acquisition)\b.*?\b(not.*?loan|not.*?mortgage|without\s+financing)\b'
            ]

            # Enhanced account-related patterns
            account_patterns = [
                r'\b(account|account\s+number|acct|a\/c|account\s+id)\b',
                r'\b(account|acct|a\/c)\b.*?\b(payment|transfer|deposit|credit|debit)\b',
                r'\b(payment|transfer|deposit|credit|debit)\b.*?\b(to|into|for|from)\b.*?\b(account|acct|a\/c)\b',
                r'\b(loan|mortgage|credit)\b.*?\b(account|acct|a\/c|number|id)\b',
                r'\b(account|acct|a\/c|number|id)\b.*?\b(loan|mortgage|credit)\b',
                r'\b(loan|mortgage)\b.*?\b(servicing|processing)\b.*?\b(account|payment)\b'
            ]

            # Message type specific patterns
            mt202_loan_patterns = []
            if message_type == "MT202" or message_type == "MT202COV":
                mt202_loan_patterns = [
                    r'\b(loan|credit)\b.*?\b(syndication|participation|facility|arrangement)\b',
                    r'\b(syndicated|club)\b.*?\b(loan|facility|credit)\b',
                    r'\b(loan|credit)\b.*?\b(tranche|drawdown|utilization)\b',
                    r'\b(bank|financial\s+institution)\b.*?\b(participation|share)\b.*?\b(loan|credit|facility)\b'
                ]

            # Check for various patterns
            is_loan_repayment = any(re.search(pattern, narration_lower) for pattern in loan_repayment_patterns)
            is_loan = any(re.search(pattern, narration_lower) for pattern in loan_patterns) and not is_loan_repayment
            is_interbank = any(re.search(pattern, narration_lower) for pattern in interbank_patterns)
            is_property = any(re.search(pattern, narration_lower) for pattern in property_patterns)
            is_account_related = any(re.search(pattern, narration_lower) for pattern in account_patterns)
            is_mt202_loan = message_type in ["MT202", "MT202COV"] and any(re.search(pattern, narration_lower) for pattern in mt202_loan_patterns)

            # Make the decision based on the patterns with clear precedence rules
            if is_mt202_loan:
                # MT202/MT202COV loan syndication has highest priority
                logger.debug(f"MT202/MT202COV loan syndication pattern matched in narration: {narration}")
                return 'LOAN', 0.99, "mt202_loan_syndication_pattern"
            elif is_interbank and not (is_loan_repayment or is_loan):
                # If it's interbank and not loan-related, it's likely an interbank transfer
                logger.debug(f"Interbank pattern matched in narration: {narration}")
                return 'INTC', 0.98, "interbank_pattern"
            elif is_property and not (is_loan_repayment or is_loan):
                # If it's property-related and not loan-related, it's likely a property purchase
                logger.debug(f"Property purchase pattern matched in narration: {narration}")
                return 'PPTI', 0.98, "property_purchase_pattern"
            elif is_loan_repayment:
                # Check for specific mortgage repayment patterns
                if re.search(r'\b(mortgage|home\s+loan|house\s+loan)\b.*?\b(repayment|payment|installment)\b', narration_lower):
                    logger.debug(f"Mortgage repayment pattern matched in narration: {narration}")
                    return 'LOAR', 0.99, "mortgage_repayment_pattern"
                elif is_account_related:
                    # If it's both loan repayment and account-related, it's likely a loan account payment
                    logger.debug(f"Loan account pattern matched in narration: {narration}")
                    return 'LOAN', 0.98, "loan_account_pattern"
                else:
                    # If it's loan repayment but not account-related, it's likely a loan repayment
                    logger.debug(f"Loan repayment pattern matched in narration: {narration}")
                    return 'LOAR', 0.98, "loan_repayment_pattern"
            elif is_loan:
                # If it's a loan but not a loan repayment, it's likely a loan
                logger.debug(f"Loan pattern matched in narration: {narration}")
                return 'LOAN', 0.98, "loan_pattern"

        # 2. VATX vs TAXS - Advanced pattern matching
        if purpose_code in ['VATX', 'TAXS', 'OTHR']:
            # Advanced VAT patterns with semantic understanding
            vat_patterns = [
                r'\b(vat|value\s+added\s+tax|sales\s+tax|gst|goods\s+and\s+services\s+tax)\b',
                r'\b(vat|value\s+added\s+tax|sales\s+tax|gst)\b.*?\b(payment|remittance|return|bill|invoice)\b',
                r'\b(payment|remittance|return)\b.*?\b(of|for)\b.*?\b(vat|value\s+added\s+tax|sales\s+tax|gst)\b',
                r'\b(quarterly|monthly|annual)\b.*?\b(vat|value\s+added\s+tax|sales\s+tax|gst)\b'
            ]

            # Advanced tax patterns with semantic understanding (excluding VAT)
            tax_patterns = [
                r'\b(tax(?!\s+added)|income\s+tax|corporate\s+tax|property\s+tax|business\s+tax)\b',
                r'\b(tax(?!\s+added)|income\s+tax|corporate\s+tax|property\s+tax)\b.*?\b(payment|remittance|return|bill|invoice)\b',
                r'\b(payment|remittance|return)\b.*?\b(of|for)\b.*?\b(tax(?!\s+added)|income\s+tax|corporate\s+tax|property\s+tax)\b',
                r'\b(quarterly|monthly|annual)\b.*?\b(tax(?!\s+added)|income\s+tax|corporate\s+tax|property\s+tax)\b'
            ]

            # Check for VAT patterns
            is_vat = any(re.search(pattern, narration_lower) for pattern in vat_patterns)

            # Check for tax patterns (excluding VAT)
            is_tax = any(re.search(pattern, narration_lower) for pattern in tax_patterns) and not is_vat

            # Make the decision based on the patterns
            if is_vat:
                logger.debug(f"VAT pattern matched in narration: {narration}")
                return 'VATX', 0.95, "vat_pattern"
            elif is_tax:
                logger.debug(f"Tax pattern matched in narration: {narration}")
                return 'TAXS', 0.95, "tax_pattern"

        # 3. SSBE vs GBEN - Advanced pattern matching
        if purpose_code in ['SSBE', 'GBEN', 'OTHR']:
            # Advanced social security patterns with semantic understanding
            ssbe_patterns = [
                r'\b(social\s+security|ss\s+benefit|social\s+security\s+benefit|ss\s+payment)\b',
                r'\b(social\s+security|ss)\b.*?\b(benefit|payment|allowance|pension)\b',
                r'\b(benefit|payment|allowance|pension)\b.*?\b(from|of)\b.*?\b(social\s+security|ss)\b',
                r'\b(retirement|disability|survivor)\b.*?\b(benefit|payment|allowance)\b.*?\b(social\s+security|ss)\b'
            ]

            # Advanced government benefit patterns with semantic understanding (excluding social security)
            gben_patterns = [
                r'\b(government|gov|state|public|federal)\b.*?\b(benefit|payment|allowance|assistance|aid|grant)\b',
                r'\b(benefit|payment|allowance|assistance|aid|grant)\b.*?\b(from|of)\b.*?\b(government|gov|state|public|federal)\b',
                r'\b(unemployment|welfare|housing|child)\b.*?\b(benefit|payment|allowance|assistance|aid|grant)\b',
                r'\b(benefit|payment|allowance|assistance|aid|grant)\b.*?\b(unemployment|welfare|housing|child)\b'
            ]

            # Check for social security patterns
            is_ssbe = any(re.search(pattern, narration_lower) for pattern in ssbe_patterns)

            # Check for government benefit patterns (excluding social security)
            is_gben = any(re.search(pattern, narration_lower) for pattern in gben_patterns) and not is_ssbe

            # Make the decision based on the patterns
            if is_ssbe:
                logger.debug(f"Social security pattern matched in narration: {narration}")
                return 'SSBE', 0.95, "ssbe_pattern"
            elif is_gben:
                logger.debug(f"Government benefit pattern matched in narration: {narration}")
                return 'GBEN', 0.95, "gben_pattern"

        # 4. SCVE vs SERV - Advanced pattern matching
        if purpose_code in ['SCVE', 'SERV', 'OTHR']:
            # Advanced service purchase patterns with semantic understanding
            scve_patterns = [
                r'\b(service\s+purchase|purchase\s+of\s+service|professional\s+service|consulting\s+service)\b',
                r'\b(purchase|buy|acquire|procure)\b.*?\b(service|professional\s+service|consulting\s+service)\b',
                r'\b(service|professional\s+service|consulting\s+service)\b.*?\b(purchase|buy|acquire|procure)\b',
                r'\b(pay(ing|ment)?|transfer(ing)?)\b.*?\b(for|to)\b.*?\b(professional|consulting|business)\b.*?\b(service)\b',
                r'\b(fee\s+collection\s+for\s+service|service\s+fee\s+collection)\b'
            ]

            # Advanced service charge patterns with semantic understanding (excluding service purchase)
            serv_patterns = [
                r'\b(service\s+charge|service\s+fee|maintenance\s+fee|account\s+fee|processing\s+fee)\b',
                r'\b(charge|fee)\b.*?\b(for|of)\b.*?\b(service|maintenance|account|processing)\b',
                r'\b(service|maintenance|account|processing)\b.*?\b(charge|fee)\b',
                r'\b(monthly|quarterly|annual)\b.*?\b(service\s+charge|service\s+fee|maintenance\s+fee)\b',
                r'\b(bank|financial|institution)\b.*?\b(service\s+charge|service\s+fee|maintenance\s+fee)\b'
            ]

            # Check for service purchase patterns
            is_scve = any(re.search(pattern, narration_lower) for pattern in scve_patterns)

            # Check for service charge patterns (excluding service purchase)
            is_serv = any(re.search(pattern, narration_lower) for pattern in serv_patterns) and not is_scve

            # Make the decision based on the patterns
            if is_scve:
                logger.debug(f"Service purchase pattern matched in narration: {narration}")
                return 'SCVE', 0.95, "scve_pattern"
            elif is_serv:
                logger.debug(f"Service charge pattern matched in narration: {narration}")
                return 'SERV', 0.95, "serv_pattern"

        # Special case for "FEE COLLECTION FOR SERVICES" with variations
        fee_collection_patterns = [
            r'\b(fee\s+collection\s+for\s+service|service\s+fee\s+collection)\b',
            r'\b(fee|fees)\b.*?\b(collection|collecting|collected)\b.*?\b(for|of)\b.*?\b(service|services)\b',
            r'\b(collection|collecting|collected)\b.*?\b(of|for)\b.*?\b(fee|fees)\b.*?\b(for|of)\b.*?\b(service|services)\b',
            r'\b(service|services)\b.*?\b(fee|fees)\b.*?\b(collection|collecting|collected)\b'
        ]

        if any(re.search(pattern, narration_lower) for pattern in fee_collection_patterns):
            logger.debug(f"Fee collection for services pattern matched in narration: {narration}")
            return 'SCVE', 0.99, "fee_collection_pattern"

        # Enhanced message type specific patterns
        if message_type == "MT103":
            # MT103 is commonly used for loan repayments - enhanced pattern
            if re.search(r'\b(loan|credit|mortgage)\b.*?\b(repayment|payment|installment|settlement)\b', narration_lower):
                # Check if it's a mortgage payment specifically
                if re.search(r'\b(mortgage|home\s+loan|house\s+loan)\b', narration_lower):
                    logger.debug(f"MT103 mortgage payment pattern matched in narration: {narration}")
                    return 'LOAR', 0.99, "mt103_mortgage_payment_pattern"
                else:
                    logger.debug(f"MT103 loan repayment pattern matched in narration: {narration}")
                    return 'LOAR', 0.99, "mt103_loan_repayment_pattern"

            # Additional patterns for loan repayments in MT103
            if re.search(r'\b(payment|installment)\b.*?\b(for|of|on)\b.*?\b(loan|credit|mortgage)\b', narration_lower):
                logger.debug(f"MT103 payment for loan pattern matched in narration: {narration}")
                return 'LOAR', 0.99, "mt103_payment_for_loan_pattern"

            if re.search(r'\b(monthly|quarterly|regular|scheduled)\b.*?\b(payment|installment)\b', narration_lower) and re.search(r'\b(loan|credit|mortgage)\b', narration_lower):
                logger.debug(f"MT103 scheduled loan payment pattern matched in narration: {narration}")
                return 'LOAR', 0.99, "mt103_scheduled_loan_payment_pattern"

            if re.search(r'\b(emi|equated\s+monthly\s+installment)\b', narration_lower):
                logger.debug(f"MT103 EMI payment pattern matched in narration: {narration}")
                return 'LOAR', 0.99, "mt103_emi_payment_pattern"

            # Special case for "LOAN INSTALLMENT" which is incorrectly classified as LOAN
            if re.search(r'\b(loan\s+installment|mortgage\s+installment|credit\s+installment)\b', narration_lower):
                logger.debug(f"MT103 loan installment pattern matched in narration: {narration}")
                return 'LOAR', 0.99, "mt103_loan_installment_pattern"

            # Special case for "LOAN SETTLEMENT" which is incorrectly classified as LOAN
            if re.search(r'\b(loan\s+settlement|mortgage\s+settlement|credit\s+settlement)\b', narration_lower):
                logger.debug(f"MT103 loan settlement pattern matched in narration: {narration}")
                return 'LOAR', 0.99, "mt103_loan_settlement_pattern"

            # Special case for "LOAN PAYMENT" which is incorrectly classified as LOAN
            if re.search(r'\b(loan\s+payment|mortgage\s+payment|credit\s+payment)\b', narration_lower):
                logger.debug(f"MT103 loan payment pattern matched in narration: {narration}")
                return 'LOAR', 0.99, "mt103_loan_payment_pattern"

            # MT103 is commonly used for loan disbursements
            if re.search(r'\b(loan|credit|mortgage)\b.*?\b(disbursement|advance|drawdown)\b', narration_lower):
                logger.debug(f"MT103 loan disbursement pattern matched in narration: {narration}")
                return 'LOAN', 0.99, "mt103_loan_disbursement_pattern"

            # Additional patterns for loan disbursements in MT103
            if re.search(r'\b(new|approved|granted|sanctioned|issued)\b.*?\b(loan|credit|mortgage)\b', narration_lower):
                logger.debug(f"MT103 new loan pattern matched in narration: {narration}")
                return 'LOAN', 0.99, "mt103_new_loan_pattern"

            if re.search(r'\b(loan|credit|mortgage)\b.*?\b(proceeds|payout|amount|principal|fund|money)\b', narration_lower):
                logger.debug(f"MT103 loan proceeds pattern matched in narration: {narration}")
                return 'LOAN', 0.99, "mt103_loan_proceeds_pattern"

            if re.search(r'\b(loan|credit)\b.*?\b(transfer|deposit|payment)\b.*?\b(to\s+you|to\s+your|to\s+account|to\s+the\s+account)\b', narration_lower):
                logger.debug(f"MT103 loan transfer to account pattern matched in narration: {narration}")
                return 'LOAN', 0.99, "mt103_loan_transfer_to_account_pattern"

            # Special case for "LOAN ORIGINATION" which is incorrectly classified as LOAR
            if re.search(r'\b(loan\s+origination|mortgage\s+origination|credit\s+origination)\b', narration_lower):
                logger.debug(f"MT103 loan origination pattern matched in narration: {narration}")
                return 'LOAN', 0.99, "mt103_loan_origination_pattern"

            # Special case for "LOAN APPROVAL" which is incorrectly classified as LOAR
            if re.search(r'\b(loan\s+approval|mortgage\s+approval|credit\s+approval)\b', narration_lower):
                logger.debug(f"MT103 loan approval pattern matched in narration: {narration}")
                return 'LOAN', 0.99, "mt103_loan_approval_pattern"

            # Special case for "LOAN DISBURSEMENT" which is incorrectly classified as LOAR
            if re.search(r'\b(loan\s+disbursement|mortgage\s+disbursement|credit\s+disbursement)\b', narration_lower):
                logger.debug(f"MT103 loan disbursement pattern matched in narration: {narration}")
                return 'LOAN', 0.99, "mt103_loan_disbursement_pattern"

            # MT103 is commonly used for tax payments - enhanced pattern
            if re.search(r'\b(tax|vat|duty)\b.*?\b(payment|remittance|return)\b', narration_lower):
                if re.search(r'\b(vat|value\s+added\s+tax|sales\s+tax|gst)\b', narration_lower):
                    logger.debug(f"MT103 VAT payment pattern matched in narration: {narration}")
                    return 'VATX', 0.95, "mt103_vat_payment_pattern"
                else:
                    logger.debug(f"MT103 tax payment pattern matched in narration: {narration}")
                    return 'TAXS', 0.95, "mt103_tax_payment_pattern"

        elif message_type == "MT202" or message_type == "MT202COV":
            # MT202/MT202COV is commonly used for interbank transfers
            if re.search(r'\b(interbank|inter-bank|bank\s+to\s+bank)\b', narration_lower):
                logger.debug(f"MT202/MT202COV interbank pattern matched in narration: {narration}")
                return 'INTC', 0.95, "mt202_interbank_pattern"

            # MT202/MT202COV can also be used for loan syndication
            if re.search(r'\b(loan|credit)\b.*?\b(syndication|participation|facility)\b', narration_lower):
                logger.debug(f"MT202/MT202COV loan syndication pattern matched in narration: {narration}")
                return 'LOAN', 0.95, "mt202_loan_syndication_pattern"

        # If no patterns matched, return the original purpose code and confidence
        return purpose_code, confidence, None

    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification based on domain-specific knowledge for specific problematic cases.
        Uses advanced pattern matching with regular expressions and semantic understanding.

        Args:
            result: The classification result dictionary
            narration: The narration text
            message_type: Optional SWIFT message type (MT103, MT202, etc.)

        Returns:
            dict: The enhanced classification result
        """
        # Get message type from result if not provided
        if message_type is None and 'message_type' in result:
            message_type = result.get('message_type')

        # Get the original purpose code and confidence
        original_purpose = result.get('purpose_code', 'OTHR')
        original_conf = result.get('confidence', 0.0)

        # Apply the enhance method
        enhanced_purpose, enhanced_conf, enhancement_type = self.enhance(original_purpose, original_conf, narration, message_type)

        # If the purpose code was enhanced, update the result
        if enhanced_purpose != original_purpose or enhanced_conf != original_conf:
            result['purpose_code'] = enhanced_purpose
            result['confidence'] = enhanced_conf
            result['enhancer'] = "targeted"
            result['enhanced'] = True
            result['reason'] = enhancement_type
            result['original_purpose_code'] = original_purpose
            result['original_confidence'] = original_conf

            # Enhanced category purpose code mapping with more specific logic for loan-related codes
            if enhanced_purpose == 'LOAN':
                result['category_purpose_code'] = 'LOAN'
                result['category_confidence'] = 0.99  # Increased confidence
                result['category_enhancement_applied'] = "loan_category_mapping"
                result['category_enhancement_reason'] = enhancement_type  # Add the specific reason
                logger.debug(f"Set category purpose code to LOAN for LOAN with reason: {enhancement_type}")
            elif enhanced_purpose == 'LOAR':
                result['category_purpose_code'] = 'LOAN'
                result['category_confidence'] = 0.99  # Increased confidence
                result['category_enhancement_applied'] = "loan_repayment_category_mapping"
                result['category_enhancement_reason'] = enhancement_type  # Add the specific reason
                logger.debug(f"Set category purpose code to LOAN for LOAR with reason: {enhancement_type}")
            elif enhanced_purpose == 'INTC':
                result['category_purpose_code'] = 'INTC'
                result['category_confidence'] = 0.99  # Increased confidence
                result['category_enhancement_applied'] = "interbank_category_mapping"
                result['category_enhancement_reason'] = enhancement_type  # Add the specific reason
                logger.debug(f"Set category purpose code to INTC for INTC with reason: {enhancement_type}")
            elif enhanced_purpose == 'PPTI':
                result['category_purpose_code'] = 'PPTI'
                result['category_confidence'] = 0.99  # Increased confidence
                result['category_enhancement_applied'] = "property_purchase_category_mapping"
                result['category_enhancement_reason'] = enhancement_type  # Add the specific reason
                logger.debug(f"Set category purpose code to PPTI for PPTI with reason: {enhancement_type}")
            elif enhanced_purpose == 'VATX':
                result['category_purpose_code'] = 'VATX'
                result['category_confidence'] = 0.95
                result['category_enhancement_applied'] = "vat_category_mapping"
                logger.debug(f"Set category purpose code to VATX for VATX")
            elif enhanced_purpose == 'TAXS':
                result['category_purpose_code'] = 'TAXS'
                result['category_confidence'] = 0.95
                result['category_enhancement_applied'] = "tax_category_mapping"
                logger.debug(f"Set category purpose code to TAXS for TAXS")
            elif enhanced_purpose == 'SSBE':
                result['category_purpose_code'] = 'SSBE'
                result['category_confidence'] = 0.95
                result['category_enhancement_applied'] = "social_security_category_mapping"
                logger.debug(f"Set category purpose code to SSBE for SSBE")
            elif enhanced_purpose == 'GBEN':
                result['category_purpose_code'] = 'GOVT'
                result['category_confidence'] = 0.95
                result['category_enhancement_applied'] = "government_benefit_category_mapping"
                logger.debug(f"Set category purpose code to GOVT for GBEN")
            elif enhanced_purpose == 'SCVE':
                result['category_purpose_code'] = 'SUPP'
                result['category_confidence'] = 0.95
                result['category_enhancement_applied'] = "service_purchase_category_mapping"
                logger.debug(f"Set category purpose code to SUPP for SCVE")
            elif enhanced_purpose == 'SERV':
                result['category_purpose_code'] = 'SUPP'
                result['category_confidence'] = 0.95
                result['category_enhancement_applied'] = "service_charge_category_mapping"
                logger.debug(f"Set category purpose code to SUPP for SERV")

        return result
