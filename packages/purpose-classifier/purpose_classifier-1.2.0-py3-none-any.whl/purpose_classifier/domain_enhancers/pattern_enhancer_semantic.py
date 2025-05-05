"""
Pattern-based enhancer for purpose code classification.

This enhancer uses specific patterns to improve the classification of purpose codes
for cases where the base model might have low confidence or misclassifications.
"""

import re
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer
import logging

logger = logging.getLogger(__name__)

class PatternEnhancerSemantic(SemanticEnhancer):
    """
    Enhancer that uses specific patterns to improve purpose code classification.

    This enhancer focuses on fixing common misclassifications and improving
    confidence for specific transaction types based on pattern matching.
    """

    def __init__(self, matcher=None):
        super().__init__(matcher=matcher)

        # Initialize regex patterns
        self.mt103_pattern = re.compile(r'\b(MT103|103:|customer\s+credit\s+transfer)\b', re.IGNORECASE)
        self.mt202_pattern = re.compile(r'\b(MT202(?!COV)|202(?!COV)|financial\s+institution\s+transfer)\b', re.IGNORECASE)
        self.mt202cov_pattern = re.compile(r'\b(MT202COV|202COV|cover\s+payment)\b', re.IGNORECASE)
        self.mt205_pattern = re.compile(r'\b(MT205(?!COV)|205(?!COV)|financial\s+institution\s+transfer\s+execution)\b', re.IGNORECASE)
        self.mt205cov_pattern = re.compile(r'\b(MT205COV|205COV|financial\s+institution\s+transfer\s+cover)\b', re.IGNORECASE)

        # Initialize pattern lists
        self.court_patterns = []
        self.credit_card_patterns = []
        self.debit_card_patterns = []
        self.dividend_patterns = []
        self.cross_border_patterns = []
        self.letter_of_credit_patterns = []
        self.salary_patterns = []
        self.welfare_patterns = []
        self.mt202_patterns = []
        self.mt202cov_patterns = []
        self.investment_patterns = []
        self.fee_patterns = []
        self.bond_patterns = []

        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize semantic patterns and contexts."""
        # Direct keywords with purpose codes
        self.direct_keywords = {}

        # Initialize card payment patterns
        self.irrevocable_credit_card_patterns = [
            re.compile(r'\b(irrevocable\s+credit\s+card)\b', re.IGNORECASE),
            re.compile(r'\b(irrevocable\s+cc)\b', re.IGNORECASE),
            re.compile(r'\b(irrevocable\s+credit\s+card\s+payment)\b', re.IGNORECASE),
            re.compile(r'\b(irrevocable\s+credit\s+card\s+bill)\b', re.IGNORECASE),
            re.compile(r'\b(irrevocable\s+credit\s+card\s+transaction)\b', re.IGNORECASE)
        ]

        self.irrevocable_debit_card_patterns = [
            re.compile(r'\b(irrevocable\s+debit\s+card)\b', re.IGNORECASE),
            re.compile(r'\b(irrevocable\s+dc)\b', re.IGNORECASE),
            re.compile(r'\b(irrevocable\s+debit\s+card\s+payment)\b', re.IGNORECASE),
            re.compile(r'\b(irrevocable\s+debit\s+card\s+bill)\b', re.IGNORECASE),
            re.compile(r'\b(irrevocable\s+debit\s+card\s+transaction)\b', re.IGNORECASE)
        ]

        self.card_bulk_clearing_patterns = [
            re.compile(r'\b(card\s+bulk\s+clearing)\b', re.IGNORECASE),
            re.compile(r'\b(card\s+bulk\s+settlement)\b', re.IGNORECASE),
            re.compile(r'\b(card\s+bulk\s+processing)\b', re.IGNORECASE),
            re.compile(r'\b(card\s+bulk\s+reconciliation)\b', re.IGNORECASE),
            re.compile(r'\b(card\s+bulk\s+payment)\b', re.IGNORECASE),
            re.compile(r'\b(bulk\s+card\s+clearing)\b', re.IGNORECASE),
            re.compile(r'\b(bulk\s+card\s+settlement)\b', re.IGNORECASE),
            re.compile(r'\b(bulk\s+card\s+processing)\b', re.IGNORECASE)
        ]

        # Semantic context patterns
        self.context_patterns = [
            {
                'purpose_code': 'SALA',
                'keywords': ['salary', 'payroll', 'wage', 'compensation', 'remuneration'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'SALA',
                'keywords': ['salary', 'transfer', 'transfer', 'salary', 'employee', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'TAXS',
                'keywords': ['tax', 'income', 'tax', 'payment', 'tax', 'bill'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'TAXS',
                'keywords': ['tax', 'payment', 'payment', 'tax', 'tax', 'authority'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'UTIL',
                'keywords': ['utility', 'bill', 'electricity', 'bill', 'water', 'bill'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'UTIL',
                'keywords': ['gas', 'bill', 'phone', 'bill', 'internet', 'bill'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'BENE',
                'keywords': ['welfare', 'benefit', 'social', 'welfare', 'government', 'benefit'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'BENE',
                'keywords': ['disability', 'benefit', 'social', 'security', 'benefit'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DIVD',
                'keywords': ['dividend', 'shareholder', 'dividend', 'dividend', 'payment', 'dividend', 'distribution'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DIVD',
                'keywords': ['dividend', 'payout', 'corporate', 'dividend', 'quarterly', 'dividend', 'annual', 'dividend'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DIVD',
                'keywords': ['interim', 'dividend', 'final', 'dividend', 'special', 'dividend', 'extraordinary', 'dividend'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DIVD',
                'keywords': ['stock', 'dividend', 'cash', 'dividend', 'preferred', 'dividend', 'common', 'dividend'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DIVD',
                'keywords': ['dividend', 'income', 'dividend', 'yield', 'dividend', 'reinvestment'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'LCOL',
                'keywords': ['letter', 'credit', 'documentary', 'credit'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'LCOL',
                'keywords': ['irrevocable', 'credit', 'credit', 'irrevocable'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'LCOL',
                'keywords': ['standby', 'letter', 'credit', 'standby', 'standby'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'LCOL',
                'keywords': ['documentary', 'letter', 'credit', 'documentary', 'documentary'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'LCOL',
                'keywords': ['commercial', 'letter', 'credit', 'commercial', 'commercial'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'LCOL',
                'keywords': ['payment', 'under', 'letter', 'credit', 'payment', 'under', 'payment', 'under'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'LCOL',
                'keywords': ['settlement', 'under', 'letter', 'credit', 'settlement', 'under', 'settlement', 'under'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'LCOL',
                'keywords': ['payment', 'against', 'letter', 'credit', 'payment', 'against', 'payment', 'against'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'LCOL',
                'keywords': ['settlement', 'against', 'letter', 'credit', 'settlement', 'against', 'settlement', 'against'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'SECU',
                'keywords': ['bond', 'purchase', 'purchase', 'bond', 'treasury', 'bond'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'SECU',
                'keywords': ['bond', 'settlement', 'settlement', 'bond'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'INTC',
                'keywords': ['interbank', 'nostro', 'vostro', 'correspondent', 'liquidity', 'funding'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'INTC',
                'keywords': ['bank', 'bank', 'between', 'banks', 'interbank', 'transfer'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'INTC',
                'keywords': ['cover', 'payment', 'payment', 'cover', 'cover', 'for'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'INTC',
                'keywords': ['cross-border', 'international', 'wire', 'overseas'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'INVS',
                'keywords': ['investment', 'securities', 'equity', 'portfolio', 'fund', 'mutual', 'bond'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'INVS',
                'keywords': ['securities', 'trading', 'trading', 'securities'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'FEES',
                'keywords': ['fee', 'commission', 'charge', 'management', 'fee', 'advisory', 'fee'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'FEES',
                'keywords': ['portfolio', 'management', 'investment', 'advisory'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CORT',
                'keywords': ['court', 'order', 'court', 'ordered', 'court', 'mandated', 'court', 'payment', 'court', 'settlement'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CORT',
                'keywords': ['legal', 'settlement', 'court', 'judgment', 'court', 'judgement', 'judicial', 'order', 'judicial', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CORT',
                'keywords': ['legal', 'proceedings', 'legal', 'order', 'legal', 'mandate', 'court', 'proceedings', 'court', 'case'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CORT',
                'keywords': ['court', 'ruling', 'court', 'decision', 'judicial', 'ruling', 'judicial', 'decision'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CORT',
                'keywords': ['payment', 'per', 'court', 'payment', 'per', 'court', 'payment', 'pursuant', 'court'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CORT',
                'keywords': ['payment', 'accordance', 'with', 'court', 'payment', 'following', 'court'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CORT',
                'keywords': ['settlement', 'per', 'court', 'settlement', 'per', 'court', 'settlement', 'pursuant', 'court'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CORT',
                'keywords': ['settlement', 'accordance', 'with', 'court', 'settlement', 'following', 'court'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CORT',
                'keywords': ['litigation', 'lawsuit', 'legal', 'case', 'legal', 'dispute', 'dispute', 'resolution'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CORT',
                'keywords': ['arbitration', 'mediation', 'judgment', 'payment', 'judgement', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['credit', 'card', 'credit', 'card', 'payment', 'credit', 'card', 'bill', 'credit', 'card', 'invoice'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['credit', 'card', 'settlement', 'credit', 'card', 'transaction', 'credit', 'card', 'charge'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['visa', 'mastercard', 'amex', 'american', 'express', 'discover', 'diners', 'club', 'jcb', 'union', 'pay'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['payment', 'bill', 'invoice', 'settlement', 'transaction', 'charge'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['payment', 'credit', 'card', 'payment', 'for', 'credit', 'card', 'transfer', 'credit', 'card'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['transfer', 'for', 'credit', 'card', 'remittance', 'credit', 'card', 'remittance', 'for', 'credit', 'card'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['settlement', 'credit', 'card', 'settlement', 'for', 'credit', 'card'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['payment', 'credit', 'card', 'bill', 'payment', 'credit', 'card', 'statement'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['payment', 'credit', 'card', 'invoice', 'payment', 'credit', 'card', 'balance'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['payment', 'visa', 'payment', 'mastercard', 'payment', 'amex'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'CCRD',
                'keywords': ['payment', 'visa', 'payment', 'mastercard', 'payment', 'amex'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['debit', 'card', 'debit', 'card', 'payment', 'debit', 'card', 'bill', 'debit', 'card', 'invoice'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['debit', 'card', 'settlement', 'debit', 'card', 'transaction', 'debit', 'card', 'charge'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['atm', 'card', 'bank', 'card', 'check', 'card'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['payment', 'bill', 'invoice', 'settlement', 'transaction', 'charge'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['payment', 'debit', 'card', 'payment', 'for', 'debit', 'card', 'transfer', 'debit', 'card'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['transfer', 'for', 'debit', 'card', 'remittance', 'debit', 'card', 'remittance', 'for', 'debit', 'card'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['settlement', 'debit', 'card', 'settlement', 'for', 'debit', 'card'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['payment', 'debit', 'card', 'bill', 'payment', 'debit', 'card', 'statement'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['payment', 'debit', 'card', 'invoice', 'payment', 'debit', 'card', 'balance'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['payment', 'atm', 'card', 'payment', 'bank', 'card', 'payment', 'check', 'card'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'DCRD',
                'keywords': ['payment', 'atm', 'card', 'payment', 'bank', 'card', 'payment', 'check', 'card'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'XBCT',
                'keywords': ['cross', 'border', 'international', 'overseas', 'foreign', 'abroad'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['salary', 'payroll', 'wage', 'compensation', 'remuneration'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['salary', 'transfer', 'transfer', 'salary', 'employee', 'payment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['welfare', 'benefit', 'social', 'welfare', 'government', 'benefit'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['disability', 'benefit', 'social', 'security', 'benefit'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['dividend', 'shareholder', 'dividend', 'dividend', 'payment', 'dividend', 'distribution'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['dividend', 'payout', 'corporate', 'dividend', 'quarterly', 'dividend', 'annual', 'dividend'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['interim', 'dividend', 'final', 'dividend', 'special', 'dividend', 'extraordinary', 'dividend'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['stock', 'dividend', 'cash', 'dividend', 'preferred', 'dividend', 'common', 'dividend'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['dividend', 'income', 'dividend', 'yield', 'dividend', 'reinvestment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['letter', 'credit', 'documentary', 'credit'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['irrevocable', 'credit', 'credit', 'irrevocable'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['standby', 'letter', 'credit', 'standby', 'standby'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['documentary', 'letter', 'credit', 'documentary', 'documentary'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['commercial', 'letter', 'credit', 'commercial', 'commercial'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'under', 'letter', 'credit', 'payment', 'under', 'payment', 'under'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['settlement', 'under', 'letter', 'credit', 'settlement', 'under', 'settlement', 'under'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'against', 'letter', 'credit', 'payment', 'against', 'payment', 'against'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['settlement', 'against', 'letter', 'credit', 'settlement', 'against', 'settlement', 'against'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['bond', 'purchase', 'purchase', 'bond', 'treasury', 'bond'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['bond', 'settlement', 'settlement', 'bond'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['interbank', 'nostro', 'vostro', 'correspondent', 'liquidity', 'funding'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['bank', 'bank', 'between', 'banks', 'interbank', 'transfer'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['cover', 'payment', 'payment', 'cover', 'cover', 'for'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['cross-border', 'international', 'wire', 'overseas'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['investment', 'securities', 'equity', 'portfolio', 'fund', 'mutual', 'bond'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['securities', 'trading', 'trading', 'securities'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['fee', 'commission', 'charge', 'management', 'fee', 'advisory', 'fee'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['portfolio', 'management', 'investment', 'advisory'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['court', 'order', 'court', 'ordered', 'court', 'mandated', 'court', 'payment', 'court', 'settlement'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['legal', 'settlement', 'court', 'judgment', 'court', 'judgement', 'judicial', 'order', 'judicial', 'payment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['legal', 'proceedings', 'legal', 'order', 'legal', 'mandate', 'court', 'proceedings', 'court', 'case'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['court', 'ruling', 'court', 'decision', 'judicial', 'ruling', 'judicial', 'decision'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'per', 'court', 'payment', 'per', 'court', 'payment', 'pursuant', 'court'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'accordance', 'with', 'court', 'payment', 'following', 'court'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['settlement', 'per', 'court', 'settlement', 'per', 'court', 'settlement', 'pursuant', 'court'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['settlement', 'accordance', 'with', 'court', 'settlement', 'following', 'court'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['litigation', 'lawsuit', 'legal', 'case', 'legal', 'dispute', 'dispute', 'resolution'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['arbitration', 'mediation', 'judgment', 'payment', 'judgement', 'payment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['credit', 'card', 'credit', 'card', 'payment', 'credit', 'card', 'bill', 'credit', 'card', 'invoice'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['credit', 'card', 'settlement', 'credit', 'card', 'transaction', 'credit', 'card', 'charge'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['visa', 'mastercard', 'amex', 'american', 'express', 'discover', 'diners', 'club', 'jcb', 'union', 'pay'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'bill', 'invoice', 'settlement', 'transaction', 'charge'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'credit', 'card', 'payment', 'for', 'credit', 'card', 'transfer', 'credit', 'card'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['transfer', 'for', 'credit', 'card', 'remittance', 'credit', 'card', 'remittance', 'for', 'credit', 'card'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['settlement', 'credit', 'card', 'settlement', 'for', 'credit', 'card'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'credit', 'card', 'bill', 'payment', 'credit', 'card', 'statement'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'credit', 'card', 'invoice', 'payment', 'credit', 'card', 'balance'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'visa', 'payment', 'mastercard', 'payment', 'amex'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'visa', 'payment', 'mastercard', 'payment', 'amex'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['debit', 'card', 'debit', 'card', 'payment', 'debit', 'card', 'bill', 'debit', 'card', 'invoice'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['debit', 'card', 'settlement', 'debit', 'card', 'transaction', 'debit', 'card', 'charge'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['atm', 'card', 'bank', 'card', 'check', 'card'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'bill', 'invoice', 'settlement', 'transaction', 'charge'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'debit', 'card', 'payment', 'for', 'debit', 'card', 'transfer', 'debit', 'card'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['transfer', 'for', 'debit', 'card', 'remittance', 'debit', 'card', 'remittance', 'for', 'debit', 'card'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['settlement', 'debit', 'card', 'settlement', 'for', 'debit', 'card'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'debit', 'card', 'bill', 'payment', 'debit', 'card', 'statement'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'debit', 'card', 'invoice', 'payment', 'debit', 'card', 'balance'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'atm', 'card', 'payment', 'bank', 'card', 'payment', 'check', 'card'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'atm', 'card', 'payment', 'bank', 'card', 'payment', 'check', 'card'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['cross', 'border', 'international', 'overseas', 'foreign', 'global', 'transnational', 'payment', 'transfer', 'remittance', 'wire', 'settlement'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'transfer', 'remittance', 'wire', 'settlement', 'cross', 'border', 'international', 'overseas', 'foreign', 'global', 'transnational'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['cross', 'border', 'international', 'overseas', 'foreign', 'global', 'transnational'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['cover', 'covering', 'for', 'cross', 'border', 'international', 'overseas', 'foreign', 'payment', 'transfer', 'remittance', 'wire', 'settlement'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['cross', 'border', 'international', 'overseas', 'foreign', 'cover', 'covering', 'payment', 'transfer', 'remittance', 'wire', 'settlement'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['cross', 'border', 'international', 'overseas', 'foreign', 'payment', 'transfer', 'remittance', 'wire', 'settlement', 'cover', 'covering'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['cover', 'covering', 'payment', 'transfer', 'remittance', 'wire', 'settlement'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'transfer', 'remittance', 'wire', 'settlement', 'from', 'foreign', 'overseas', 'international', 'abroad', 'offshore', 'country', 'account', 'bank', 'institution'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'transfer', 'remittance', 'wire', 'settlement', 'with', 'using', 'foreign', 'multiple', 'multi', 'different', 'currenc', 'ies'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['foreign', 'multiple', 'multi', 'different', 'currenc', 'ies', 'payment', 'transfer', 'remittance', 'wire', 'settlement'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['multi', 'currency', 'foreign', 'currency'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['swift', 'sepa', 'chips', 'fedwire', 'correspondent', 'payment', 'transfer', 'remittance', 'wire', 'settlement'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'transfer', 'remittance', 'wire', 'settlement', 'via', 'through', 'using', 'swift', 'sepa', 'chips', 'fedwire', 'correspondent'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['swift', 'sepa', 'chips', 'fedwire'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['nostro', 'vostro', 'account', 'settlement', 'clearing'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['CROSS', 'BORDER', 'PAYMENT'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['CROSS-BORDER', 'TRANSFER'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['INTERNATIONAL', 'WIRE', 'TRANSFER'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['INTERNATIONAL', 'PAYMENT'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['OVERSEAS', 'REMITTANCE'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['FOREIGN', 'PAYMENT'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['GLOBAL', 'TRANSFER'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['TRANSNATIONAL', 'PAYMENT'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['MT103', '103:'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['MT202', '!COV', '202', '!COV'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['MT202COV', '202COV:'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['MT205', '!COV', '205', '!COV'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['MT205COV', '205COV:'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['narration_lower:'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['othr'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['othr'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['narration_lower'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['othr'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['othr'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['othr'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['othr'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['othr'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['othr'],
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

    def detect_message_type(self, narration):
        """
        Detect the message type from the narration.

        Args:
            narration: The narration text

        Returns:
            str: The detected message type ('MT103', 'MT202', 'MT202COV', 'MT205', 'MT205COV', or None)
        """
        if self.mt103_pattern.search(narration):
            return 'MT103'
        elif self.mt202cov_pattern.search(narration):
            return 'MT202COV'
        elif self.mt202_pattern.search(narration):
            return 'MT202'
        elif self.mt205cov_pattern.search(narration):
            return 'MT205COV'
        elif self.mt205_pattern.search(narration):
            return 'MT205'
        return None

    def enhance(self, purpose_code, confidence, narration):
        """
        Enhance the purpose code classification based on specific patterns.

        Args:
            purpose_code: The predicted purpose code
            confidence: The confidence score of the prediction
            narration: The narration text

        Returns:
            tuple: (enhanced_purpose_code, enhanced_confidence, enhancement_applied)
        """
        # Add debug logging
        logger.debug(f"Pattern enhancer enhance method called with purpose_code: {purpose_code}, confidence: {confidence}, narration: {narration}")

        # Detect message type
        message_type = self.detect_message_type(narration)
        narration_lower = narration.lower()

        logger.debug(f"Detected message type: {message_type}")

        # Special handling for low confidence predictions (below 0.5)
        if confidence < 0.5:
            logger.info(f"Low confidence prediction detected: {confidence}, applying special handling")

            # Check for goods-related keywords
            goods_keywords = ['goods', 'purchase', 'procurement', 'supply', 'equipment', 'materials',
                             'inventory', 'furniture', 'vehicles', 'parts', 'office supplies', 'raw materials']
            if any(keyword in narration_lower for keyword in goods_keywords):
                logger.info(f"Goods-related keywords found in low confidence prediction: {narration}")
                return 'GDDS', 0.85, 'low_confidence_goods_pattern'

            # Check for salary-related keywords
            salary_keywords = ['salary', 'wage', 'payroll', 'compensation', 'staff', 'employee',
                              'monthly pay', 'remuneration', 'earnings']
            if any(keyword in narration_lower for keyword in salary_keywords):
                logger.info(f"Salary-related keywords found in low confidence prediction: {narration}")
                return 'SALA', 0.85, 'low_confidence_salary_pattern'

            # Check for education-related keywords
            education_keywords = ['tuition', 'education', 'school', 'university', 'college', 'academic',
                                 'training', 'course', 'student', 'educational']
            if any(keyword in narration_lower for keyword in education_keywords):
                logger.info(f"Education-related keywords found in low confidence prediction: {narration}")
                return 'EDUC', 0.85, 'low_confidence_education_pattern'

            # Check for service-related keywords
            service_keywords = ['service', 'consulting', 'professional', 'maintenance', 'advisory',
                               'legal', 'accounting', 'marketing', 'engineering', 'research']
            if any(keyword in narration_lower for keyword in service_keywords):
                logger.info(f"Service-related keywords found in low confidence prediction: {narration}")
                return 'SCVE', 0.85, 'low_confidence_service_pattern'

            # Check for dividend-related keywords
            dividend_keywords = ['dividend', 'shareholder', 'distribution', 'payout', 'profit sharing']
            if any(keyword in narration_lower for keyword in dividend_keywords):
                logger.info(f"Dividend-related keywords found in low confidence prediction: {narration}")
                return 'DIVD', 0.85, 'low_confidence_dividend_pattern'

            # Check for loan-related keywords
            loan_keywords = ['loan', 'credit', 'mortgage', 'installment', 'repayment', 'facility', 'settlement']
            if any(keyword in narration_lower for keyword in loan_keywords):
                logger.info(f"Loan-related keywords found in low confidence prediction: {narration}")
                return 'LOAN', 0.85, 'low_confidence_loan_pattern'

            # Check for insurance-related keywords
            insurance_keywords = ['insurance', 'premium', 'policy', 'coverage']
            if any(keyword in narration_lower for keyword in insurance_keywords):
                logger.info(f"Insurance-related keywords found in low confidence prediction: {narration}")
                return 'INSU', 0.85, 'low_confidence_insurance_pattern'

            # Check for intercompany-related keywords
            intercompany_keywords = ['intercompany', 'intragroup', 'internal', 'affiliated', 'subsidiary', 'group company']
            if any(keyword in narration_lower for keyword in intercompany_keywords):
                logger.info(f"Intercompany-related keywords found in low confidence prediction: {narration}")
                return 'INTC', 0.85, 'low_confidence_intercompany_pattern'

            # Check for trade-related keywords
            trade_keywords = ['trade', 'export', 'import', 'shipment', 'international trade']
            if any(keyword in narration_lower for keyword in trade_keywords):
                logger.info(f"Trade-related keywords found in low confidence prediction: {narration}")
                return 'TRAD', 0.85, 'low_confidence_trade_pattern'

            # Check for withholding tax-related keywords first (higher priority than general tax)
            withholding_keywords = ['withholding tax', 'tax withholding', 'withholding', 'withheld']
            if any(keyword in narration_lower for keyword in withholding_keywords):
                logger.info(f"Withholding tax-related keywords found in low confidence prediction: {narration}")
                return 'WHLD', 0.85, 'low_confidence_withholding_tax_pattern'

            # Check for tax-related keywords
            tax_keywords = ['tax', 'taxation', 'vat', 'income tax', 'corporate tax', 'tax authority']
            if any(keyword in narration_lower for keyword in tax_keywords):
                logger.info(f"Tax-related keywords found in low confidence prediction: {narration}")
                return 'TAXS', 0.85, 'low_confidence_tax_pattern'

            logger.info(f"No specific pattern found for low confidence prediction: {narration}")


        # Check for card bulk clearing patterns (highest priority)
        for pattern in self.card_bulk_clearing_patterns:
            if pattern.search(narration_lower):
                logger.debug(f"Card bulk clearing pattern matched: {pattern.pattern}")
                return 'CBLK', 0.99, 'card_bulk_clearing_pattern'

        # Check for irrevocable credit card patterns (highest priority)
        if 'irrevocable credit card' in narration_lower or 'irrevocable cc' in narration_lower or 'irrevocable' in narration_lower and 'credit card' in narration_lower:
            logger.debug(f"Irrevocable credit card keyword matched in narration")
            return 'ICCP', 0.99, 'irrevocable_credit_card_keyword'

        # Check for irrevocable debit card patterns (highest priority)
        if 'irrevocable debit card' in narration_lower or 'irrevocable dc' in narration_lower:
            logger.debug(f"Irrevocable debit card keyword matched in narration")
            return 'IDCP', 0.99, 'irrevocable_debit_card_keyword'

        # Check for trade settlement patterns (highest priority)
        if 'trade settlement' in narration_lower or 'settlement of trade' in narration_lower or 'settlement for trade' in narration_lower:
            logger.debug(f"Trade settlement pattern matched in narration")
            return 'CORT', 0.99, 'trade_settlement_pattern'

        # Check for transaction settlement patterns (highest priority)
        if ('settlement of transaction' in narration_lower or 'settlement for transaction' in narration_lower) and ('goods' in narration_lower or 'services' in narration_lower):
            logger.debug(f"Transaction settlement pattern matched in narration")
            return 'CORT', 0.99, 'transaction_settlement_pattern'

        # Check for court payment patterns (highest priority)
        for pattern in self.court_patterns:
            if pattern.search(narration_lower):
                logger.debug(f"Court payment pattern matched: {pattern.pattern}")
                # Exclude sports courts
                if 'tennis court' in narration_lower or 'basketball court' in narration_lower or 'volleyball court' in narration_lower or 'squash court' in narration_lower:
                    logger.debug(f"Excluded sports court: {narration_lower}")
                    continue
                # Exclude court appearance scheduling
                if 'court appearance' in narration_lower or 'court hearing' in narration_lower or 'court date' in narration_lower or 'court time' in narration_lower or 'court schedule' in narration_lower:
                    logger.debug(f"Excluded court appearance scheduling: {narration_lower}")
                    continue
                logger.debug(f"Court payment pattern matched and returning CORT purpose code")
                return 'CORT', 0.99, 'court_payment_pattern'

        # Check for credit card patterns
        for pattern in self.credit_card_patterns:
            if pattern.search(narration_lower):
                # Check for irrevocable credit card
                if 'irrevocable' in narration_lower or 'guaranteed' in narration_lower or 'secured' in narration_lower or 'confirmed' in narration_lower:
                    return 'ICCP', 0.99, 'irrevocable_credit_card_pattern'
                # Check for letter of credit
                if 'letter of credit' in narration_lower or 'lc' in narration_lower or 'l/c' in narration_lower:
                    return 'ICCP', 0.99, 'letter_of_credit_pattern'
                return 'CCRD', 0.99, 'credit_card_pattern'

        # Check for debit card patterns
        for pattern in self.debit_card_patterns:
            if pattern.search(narration_lower):
                # Check for irrevocable debit card
                if 'irrevocable' in narration_lower or 'guaranteed' in narration_lower or 'secured' in narration_lower or 'confirmed' in narration_lower:
                    return 'IDCP', 0.99, 'irrevocable_debit_card_pattern'
                return 'DCRD', 0.99, 'debit_card_pattern'

        # Check for dividend patterns (highest priority)
        if 'dividend' in narration_lower or 'shareholder' in narration_lower:
            # Explicitly check for dividend-related keywords with highest priority
            if any(term in narration_lower for term in ['dividend', 'shareholder dividend', 'dividend payment',
                                                       'dividend distribution', 'dividend payout', 'corporate dividend',
                                                       'interim dividend', 'final dividend', 'quarterly dividend',
                                                       'annual dividend', 'semi-annual dividend', 'stock dividend']):
                logger.debug(f"Dividend keyword matched in narration")
                return 'DIVD', 0.99, 'dividend_keyword_match'

        # Check for dividend patterns (high priority)
        for pattern in self.dividend_patterns:
            if pattern.search(narration_lower):
                logger.debug(f"Dividend pattern matched: {pattern.pattern}")
                return 'DIVD', 0.99, 'dividend_pattern'

        # Check for cross-border payment patterns
        for pattern in self.cross_border_patterns:
            if pattern.search(narration_lower):
                # Exclude domestic payments
                if 'domestic' in narration_lower or 'local' in narration_lower or 'internal' in narration_lower or 'intra-country' in narration_lower:
                    continue
                logger.debug(f"Cross-border pattern matched: {pattern.pattern}")
                return 'XBCT', 0.99, 'cross_border_pattern'

        # Check for letter of credit patterns
        for pattern in self.letter_of_credit_patterns:
            if pattern.search(narration_lower):
                return 'ICCP', 0.99, 'letter_of_credit_pattern'

        # Check for salary patterns
        for pattern in self.salary_patterns:
            if pattern.search(narration_lower):
                return 'SALA', 0.99, 'salary_pattern'

        # Check for social welfare patterns
        for pattern in self.welfare_patterns:
            if pattern.search(narration_lower):
                return 'GBEN', 0.95, 'welfare_pattern'

        # Apply message type-specific patterns
        if message_type == 'MT103':
            # MT103 specific patterns
            if ('SALARY' in narration.upper() or 'PAYROLL' in narration.upper() or
                'WAGE' in narration.upper() or 'COMPENSATION' in narration.upper() or
                'EMPLOYEE' in narration.upper() and 'PAYMENT' in narration.upper() or
                'STAFF' in narration.upper() and 'PAYMENT' in narration.upper() or
                'MONTHLY' in narration.upper() and 'PAYMENT' in narration.upper() or
                'EMPLOYEE' in narration.upper() and 'TRANSFER' in narration.upper() or
                'STAFF' in narration.upper() and 'TRANSFER' in narration.upper() or
                'MONTHLY' in narration.upper() and 'TRANSFER' in narration.upper()):
                return 'SALA', 0.99, 'mt103_salary'

            # Check for withholding tax first (higher priority)
            if ('WITHHOLDING TAX' in narration.upper() or 'TAX WITHHOLDING' in narration.upper() or
                'WITHHOLDING' in narration.upper() and 'TAX' in narration.upper()):
                return 'WHLD', 0.95, 'mt103_withholding_tax'

            # General tax pattern
            if 'TAX' in narration.upper() and not 'VAT' in narration.upper():
                return 'TAXS', 0.95, 'mt103_tax'

            if 'VAT' in narration.upper() or 'VALUE ADDED TAX' in narration.upper():
                return 'VATX', 0.95, 'mt103_vat'

            # More precise loan vs loan repayment classification
            if ('LOAN REPAYMENT' in narration.upper() or
                'REPAYMENT OF LOAN' in narration.upper() or
                'LOAN INSTALLMENT' in narration.upper() or
                'MORTGAGE PAYMENT' in narration.upper() or
                'LOAN SETTLEMENT' in narration.upper()):
                return 'LOAR', 0.95, 'mt103_loan_repayment'
            elif 'LOAN' in narration.upper() or 'CREDIT FACILITY' in narration.upper() or 'MORTGAGE' in narration.upper():
                return 'LOAN', 0.95, 'mt103_loan'

            if 'DIVIDEND' in narration.upper():
                return 'DIVD', 0.99, 'mt103_dividend'

        elif message_type == 'MT202' or message_type == 'MT202COV':
            # MT202/MT202COV specific patterns
            for pattern in self.mt202_patterns:
                if pattern.search(narration):
                    return 'INTC', 0.95, 'mt202_interbank'

            if 'TREASURY' in narration.upper() or 'BOND' in narration.upper():
                return 'TREA', 0.95, 'mt202_treasury'

            if 'FOREIGN EXCHANGE' in narration.upper() or 'FX' in narration.upper():
                return 'FREX', 0.95, 'mt202_foreign_exchange'

            if 'CASH' in narration.upper() and ('MANAGEMENT' in narration.upper() or 'POOLING' in narration.upper()):
                return 'CASH', 0.95, 'mt202_cash_management'

            # MT202COV specific patterns
            if message_type == 'MT202COV':
                for pattern in self.mt202cov_patterns:
                    if pattern.search(narration):
                        if 'TRADE' in narration.upper() or 'SETTLEMENT' in narration.upper():
                            return 'CORT', 0.95, 'mt202cov_trade_settlement'
                        elif 'CROSS-BORDER' in narration.upper() or 'CROSS BORDER' in narration.upper():
                            return 'XBCT', 0.95, 'mt202cov_cross_border'
                        else:
                            return 'INTC', 0.95, 'mt202cov_cover_payment'

        elif message_type == 'MT205' or message_type == 'MT205COV':
            # MT205/MT205COV specific patterns
            for pattern in self.investment_patterns:
                if pattern.search(narration):
                    return 'INVS', 0.95, 'mt205_investment'

            if 'SECURITIES' in narration.upper() or 'SECURITY' in narration.upper():
                return 'SECU', 0.95, 'mt205_securities'

            if 'BOND' in narration.upper():
                return 'SECU', 0.95, 'mt205_bond'

            # Fee patterns for MT205
            for pattern in self.fee_patterns:
                if pattern.search(narration):
                    if 'COMMISSION' in narration.upper():
                        return 'COMM', 0.95, 'mt205_commission'
                    else:
                        return 'SERV', 0.95, 'mt205_fee'

        # Check for bond patterns (lower priority than message type-specific patterns)
        for pattern in self.bond_patterns:
            if pattern.search(narration) and confidence < 0.5:
                if 'TREASURY' in narration.upper():
                    return 'TREA', 0.95, 'bond_treasury_pattern'
                else:
                    return 'SECU', 0.95, 'bond_securities_pattern'

        # If confidence is already high, don't change the prediction
        if confidence >= 0.7:
            return purpose_code, confidence, None

        # If no patterns matched and confidence is low, apply general rules
        if confidence < 0.7:
            # General patterns for common purpose codes
            if 'DIVIDEND' in narration.upper():
                return 'DIVD', 0.95, 'general_dividend'

            if 'SALARY' in narration.upper() or 'PAYROLL' in narration.upper() or 'COMPENSATION' in narration.upper() or 'EMPLOYEE' in narration.upper():
                return 'SALA', 0.95, 'general_salary'

            # Check for withholding tax first (higher priority)
            if ('WITHHOLDING TAX' in narration.upper() or 'TAX WITHHOLDING' in narration.upper() or
                'WITHHOLDING' in narration.upper() and 'TAX' in narration.upper()):
                return 'WHLD', 0.95, 'general_withholding_tax'

            # General tax pattern
            if ('TAX' in narration.upper() or 'INCOME TAX' in narration.upper()) and not 'VAT' in narration.upper():
                return 'TAXS', 0.95, 'general_tax'

            if 'VAT' in narration.upper() or 'VALUE ADDED TAX' in narration.upper():
                return 'VATX', 0.95, 'general_vat'

            if 'ELECTRICITY' in narration.upper() or 'WATER' in narration.upper() or 'GAS' in narration.upper() or 'UTILITY' in narration.upper() or 'BILL' in narration.upper():
                return 'UTIL', 0.95, 'general_utility'

            # More precise loan vs loan repayment classification for general patterns
            if ('LOAN REPAYMENT' in narration.upper() or
                'REPAYMENT OF LOAN' in narration.upper() or
                'LOAN INSTALLMENT' in narration.upper() or
                'MORTGAGE PAYMENT' in narration.upper() or
                'LOAN SETTLEMENT' in narration.upper()):
                return 'LOAR', 0.95, 'general_loan_repayment'
            elif 'LOAN' in narration.upper() or 'CREDIT FACILITY' in narration.upper() or 'MORTGAGE' in narration.upper():
                return 'LOAN', 0.95, 'general_loan'

            if 'INVESTMENT' in narration.upper() or 'SECURITIES' in narration.upper():
                return 'INVS', 0.95, 'general_investment'

            if 'INSURANCE' in narration.upper() or 'PREMIUM' in narration.upper():
                return 'INSU', 0.95, 'general_insurance'

            if 'PENSION' in narration.upper():
                return 'PENS', 0.95, 'general_pension'

            if 'IRREVOCABLE CREDIT CARD' in narration.upper():
                return 'ICCP', 0.95, 'general_irrevocable_credit_card'

            if 'IRREVOCABLE DEBIT CARD' in narration.upper():
                return 'IDCP', 0.95, 'general_irrevocable_debit_card'

            if 'CARD BULK' in narration.upper() or 'BULK CARD' in narration.upper():
                return 'CBLK', 0.95, 'general_card_bulk'

            if 'CREDIT CARD' in narration.upper():
                return 'CCRD', 0.95, 'general_credit_card'

            if 'DEBIT CARD' in narration.upper():
                return 'DCRD', 0.95, 'general_debit_card'

            if 'CASH' in narration.upper() and ('MANAGEMENT' in narration.upper() or 'TRANSFER' in narration.upper()):
                return 'CASH', 0.95, 'general_cash_management'

            if 'SUPPLIER' in narration.upper() or 'VENDOR' in narration.upper():
                return 'SUPP', 0.95, 'general_supplier'

            if 'GOODS' in narration.upper() or 'PURCHASE' in narration.upper():
                return 'GDDS', 0.95, 'general_goods'

            # Only match specific service patterns, not generic "Payment for services"
            if ('SERVICE' in narration.upper() or 'CONSULTING' in narration.upper()) and not narration.upper() == "PAYMENT FOR SERVICES":
                return 'SCVE', 0.95, 'general_service'

        # If no patterns matched, return the original purpose code and confidence
        return purpose_code, confidence, None

    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification based on specific patterns.

        Args:
            result: The classification result dictionary
            narration: The narration text
            message_type: Optional message type (MT103, MT202, MT202COV, MT205, MT205COV)

        Returns:
            dict: The enhanced classification result
        """
        # Add debug logging
        logger.debug(f"Pattern enhancer called with narration: {narration}")
        if message_type:
            logger.debug(f"Message type: {message_type}")

        # Get the original purpose code and confidence
        original_purpose = result['purpose_code']
        original_conf = result['confidence']

        # Skip interbank-related payments
        narration_lower = narration.lower()
        interbank_terms = ['interbank', 'nostro', 'vostro', 'correspondent bank', 'bank to bank',
                          'rtgs', 'real time gross settlement', 'financial institution',
                          'liquidity management', 'reserve requirement']
        if any(term in narration_lower for term in interbank_terms):
            logger.debug(f"Skipping interbank-related payment: {narration}")
            return result

        # Skip if already classified as INTC
        if original_purpose == 'INTC':
            logger.debug(f"Skipping pattern enhancer because already classified as INTC")
            return result

        # Skip enhancement if confidence is already high, but always process low confidence predictions
        if original_conf > 0.85 and original_conf >= 0.5:
            logger.debug(f"Skipping pattern enhancer because confidence is already high: {original_conf}")
            return result

        logger.debug(f"Original purpose code: {original_purpose}, confidence: {original_conf}")

        # Apply the enhance method
        enhanced_purpose, enhanced_conf, enhancement_applied = self.enhance(original_purpose, original_conf, narration)

        logger.info(f"Enhanced purpose code: {enhanced_purpose}, confidence: {enhanced_conf}, enhancement applied: {enhancement_applied}")

        # If message_type is provided, use it for additional context
        if message_type:
            # For MT202COV and MT205COV messages, prioritize cross-border and cover payments
            if message_type in ['MT202COV', 'MT205COV']:
                narration_lower = narration.lower()
                if ('cross-border' in narration_lower or 'cross border' in narration_lower or
                    'international' in narration_lower or 'overseas' in narration_lower or
                    'foreign' in narration_lower):
                    enhanced_purpose = 'XBCT'
                    enhanced_conf = 0.99
                    enhancement_applied = 'message_type_cross_border'

        # If the purpose code was enhanced, update the result
        if enhanced_purpose != original_purpose or enhanced_conf != original_conf:
            result['purpose_code'] = enhanced_purpose
            result['confidence'] = enhanced_conf
            result['enhanced'] = True
            if enhancement_applied:
                result['enhancement_applied'] = "pattern"
                result['enhanced'] = True
                result['enhancement_type'] = enhancement_applied
                result['reason'] = f"Pattern match: {enhancement_applied}"
            result['original_purpose_code'] = original_purpose
            result['original_confidence'] = original_conf

            # Also update category purpose code based on the enhanced purpose code
            # Direct mapping of purpose codes to category purpose codes
            purpose_to_category_mapping = {
                'CORT': 'CORT',  # Court Payment
                'CCRD': 'CCRD',  # Credit Card Payment
                'DCRD': 'DCRD',  # Debit Card Payment
                'ICCP': 'ICCP',  # Irrevocable Credit Card Payment
                'IDCP': 'IDCP',  # Irrevocable Debit Card Payment
                'XBCT': 'XBCT',  # Cross-Border Payment
                'SALA': 'SALA',  # Salary Payment
                'GBEN': 'GOVT',  # Government Benefit
                'DIVD': 'DIVI',  # Dividend Payment
                'TAXS': 'TAXS',  # Tax Payment
                'VATX': 'TAXS',  # Value Added Tax Payment
                'LOAR': 'LOAN',  # Loan Repayment
                'INVS': 'SECU',  # Investment
                'SECU': 'SECU',  # Securities
                'INSU': 'INSU',  # Insurance
                'PENS': 'PENS',  # Pension Payment
                'CASH': 'CASH',  # Cash Management
                'SUPP': 'SUPP',  # Supplier Payment
                'GDDS': 'GDDS',  # Goods Purchase
                'SCVE': 'SCVE',  # Service Payment
                'INTC': 'INTC',  # Intra-Company Payment
                'TREA': 'TREA',  # Treasury Payment
                'FREX': 'FREX',  # Foreign Exchange
                'COMM': 'FCOL',  # Commission
                'SERV': 'SCVE',  # Service
                'BONU': 'SALA',  # Bonus Payment
                'CHAR': 'CHAR',  # Charity Payment
                'GOVT': 'GOVT',  # Government Payment
                'PENS': 'PENS',  # Pension Payment
                'SSBE': 'SSBE',  # Social Security Benefit
                'WHLD': 'WHLD',  # Withholding
                'EPAY': 'EPAY',  # Electronic Payment
                'HEDG': 'HEDG',  # Hedging
                'INTC': 'INTC',  # Intra-Company Payment
                'CBLK': 'CBLK',  # Card Bulk Clearing
                'UBIL': 'UBIL',  # Utility Bill
                'ELEC': 'UBIL',  # Electricity Bill
                'GASB': 'UBIL',  # Gas Bill
                'WTER': 'UBIL',  # Water Bill
                'PHON': 'UBIL',  # Phone Bill
                'NWCH': 'UBIL',  # Network Charge
                'NWCM': 'UBIL',  # Network Communication
                'EDUC': 'FCOL',  # Education
                'PRME': 'SUPP',  # Property Maintenance
                'RENT': 'SUPP',  # Rent
                'SUBS': 'SUPP',  # Subscription
                'ADMN': 'SUPP',  # Administrative
                'ADVA': 'CASH',  # Advance Payment
                'AREN': 'SUPP',  # Accounts Receivable Entry
                'BENE': 'SUPP',  # Benefit Payment
                'BLDG': 'SUPP',  # Building
                'BNET': 'SUPP',  # Business Network
                'COMC': 'SUPP',  # Commercial Credit
                'CPYR': 'SUPP',  # Copyright
                'CLPR': 'SUPP',  # Car Loan Principal
                'CDBT': 'SUPP',  # Credit Card Debt
                'DBTC': 'SUPP',  # Debit Collection
                'GOVI': 'GOVT',  # Government Insurance
                'HLRP': 'SUPP',  # Housing Loan Repayment
                'HLST': 'SUPP',  # Housing Loan Settlement
                'INPC': 'INSU',  # Insurance Premium Car
                'INPR': 'INSU',  # Insurance Premium
                'IVPT': 'SECU',  # Investment Payment
                'MSVC': 'SUPP',  # Multiple Service Types
                'NOWS': 'SUPP',  # Not Otherwise Specified
                'OFEE': 'SUPP',  # Opening Fee
                'OTHR': 'SUPP',  # Other
                'PADD': 'SUPP',  # Preauthorized Debit
                'PTSP': 'SUPP',  # Payment Terms Specification
                'RCKE': 'SUPP',  # Received
                'RCPT': 'SUPP',  # Receipt Payment
                'REFU': 'SUPP',  # Refund
                'RINP': 'INSU',  # Recurring Insurance Premium
                'TRPT': 'SUPP',  # Trip Payment
                'WEBI': 'SUPP',  # Internet Bill
                'ANNI': 'SUPP',  # Annuity
                'CAFI': 'SUPP',  # Cafeteria
                'CFEE': 'SUPP',  # Cancellation Fee
                'CSDB': 'SUPP',  # Cash Disbursement
                'DMEQ': 'SUPP',  # Durable Medical Equipment
                'IDCP': 'IDCP',  # Irrevocable Debit Card Payment
                'ICCP': 'ICCP',  # Irrevocable Credit Card Payment
                'IHRP': 'SUPP',  # Instalment Hire Purchase Agreement
                'INSM': 'SUPP',  # Instalment
                'MSVC': 'SUPP',  # Multiple Service Types
                'NITX': 'TAXS',  # Net Income Tax
                'PINV': 'SUPP',  # Payment Invoice
                'RINV': 'SUPP',  # Recurring Invoice
                'TRFD': 'SUPP',  # Trust Fund
                'FORW': 'SUPP',  # Forwarding
                'BKDF': 'SUPP',  # Bank Driven Fee
                'BKFE': 'SUPP',  # Bank Fee
                'BKFM': 'SUPP',  # Bank Fee Miscellaneous
                'CMDT': 'SUPP',  # Commodity Transfer
                'TREA': 'TREA',  # Treasury
                'ANTS': 'SUPP',  # Anesthesia Services
                'CVCF': 'SUPP',  # Convalescent Care Facility
                'DMEQ': 'SUPP',  # Durable Medical Equipment
                'DNTS': 'SUPP',  # Dental Services
                'HLTC': 'SUPP',  # Home Health Care
                'HSPC': 'SUPP',  # Hospital Care
                'ICRF': 'SUPP',  # Intermediate Care Facility
                'LTCF': 'SUPP',  # Long Term Care Facility
                'MDCS': 'SUPP',  # Medical Services
                'VIEW': 'SUPP',  # Vision Care
                'CDCD': 'SUPP',  # Credit Card Debit
                'CDCS': 'SUPP',  # Credit Card Settlement
                'CDQC': 'SUPP',  # Credit Card Settlement
                'DMDD': 'CASH',  # Domestic Payment
            }

            # Special handling for cross-border payments
            if enhanced_purpose == 'XBCT':
                result['category_purpose_code'] = 'XBCT'
                result['category_confidence'] = enhanced_conf
                result['category_enhancement_applied'] = 'pattern_match_enhancer'
                result['force_category_purpose_code'] = True
            # Special handling for court payments
            elif enhanced_purpose == 'CORT':
                result['category_purpose_code'] = 'CORT'
                result['category_confidence'] = enhanced_conf
                result['category_enhancement_applied'] = 'pattern_match_enhancer'
                result['force_category_purpose_code'] = True
            # Special handling for card payments
            elif enhanced_purpose in ['CCRD', 'DCRD']:
                result['category_purpose_code'] = enhanced_purpose
                result['category_confidence'] = enhanced_conf
                result['category_enhancement_applied'] = 'pattern_match_enhancer'
                result['force_category_purpose_code'] = True
            # Apply the mapping for other purpose codes
            elif enhanced_purpose in purpose_to_category_mapping:
                result['category_purpose_code'] = purpose_to_category_mapping[enhanced_purpose]
                result['category_confidence'] = enhanced_conf
                result['category_enhancement_applied'] = 'pattern_match_enhancer'
                result['force_category_purpose_code'] = True
            else:
                # Default to SUPP if no mapping exists
                result['category_purpose_code'] = 'SUPP'
                result['category_confidence'] = enhanced_conf
                result['category_enhancement_applied'] = 'pattern_match_enhancer'
                result['force_category_purpose_code'] = True

        return result
