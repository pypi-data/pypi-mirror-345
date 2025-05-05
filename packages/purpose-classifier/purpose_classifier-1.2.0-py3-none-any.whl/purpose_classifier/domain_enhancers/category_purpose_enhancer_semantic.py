"""
CategoryPurposeEnhancerSemantic for Purpose Code Classifier.

This module provides a semantic-aware enhancer for category purpose codes,
using the CategoryPurposeMapper for improved mapping accuracy.
"""

import logging
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer
from purpose_classifier.utils.category_purpose_mapper import CategoryPurposeMapper

logger = logging.getLogger(__name__)

class CategoryPurposeEnhancerSemantic(SemanticEnhancer):
    """
    Enhances classification for category purpose codes using semantic understanding.

    This class extends the SemanticEnhancer to provide semantic-aware enhancement
    for category purpose codes, reducing OTHR usage and improving accuracy.
    """

    def __init__(self, matcher=None):
        """
        Initialize with optional matcher.

        Args:
            matcher: Optional SemanticPatternMatcher instance to use
        """
        super().__init__(matcher=matcher)

        # Initialize the category purpose mapper with the same matcher instance
        self.mapper = CategoryPurposeMapper(matcher=self.matcher)

        # Initialize semantic patterns for category purpose codes
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize semantic patterns for category purpose codes."""
        # Direct keywords for category purpose codes
        self.direct_keywords = {
            # Supplier Payment (SUPP)
            'SUPP': [
                'supplier payment', 'vendor payment', 'invoice payment',
                'bill payment', 'purchase order', 'payment to supplier',
                'payment to vendor', 'supplier invoice', 'vendor invoice'
            ],

            # Goods (GDDS)
            'GDDS': [
                'purchase of goods', 'goods payment', 'merchandise payment',
                'payment for goods', 'goods purchase', 'purchase payment',
                'merchandise settlement', 'product payment', 'goods acquisition',
                'retail purchase', 'wholesale purchase'
            ],

            # Salary Payment (SALA)
            'SALA': [
                'salary payment', 'wage payment', 'payroll',
                'compensation payment', 'employee payment', 'staff payment',
                'salary transfer', 'wage transfer', 'payroll transfer'
            ],

            # Fee Collection (FCOL)
            'FCOL': [
                'fee collection', 'payment of fees', 'service fee',
                'fee payment', 'collection of fees', 'fee settlement',
                'service charge collection', 'administrative fee', 'processing fee',
                'membership fee', 'tuition fee', 'school fees', 'education expenses'
            ],

            # Securities (SECU)
            'SECU': [
                'securities investment', 'stock purchase', 'bond purchase',
                'mutual fund', 'portfolio investment', 'securities settlement',
                'investment in securities', 'equity investment', 'fixed income investment'
            ],

            # Loan (LOAN)
            'LOAN': [
                'loan disbursement', 'loan repayment', 'mortgage payment',
                'credit facility', 'debt repayment', 'loan payment',
                'loan installment', 'principal payment', 'interest payment'
            ],

            # Tax Payment (TAXS)
            'TAXS': [
                'tax payment', 'income tax', 'property tax',
                'sales tax', 'corporate tax', 'tax return',
                'tax refund', 'tax collection', 'tax settlement'
            ],

            # VAT Payment (VATX)
            'VATX': [
                'vat payment', 'value added tax', 'vat return',
                'vat refund', 'vat collection', 'vat settlement',
                'vat invoice', 'vat receipt', 'vat claim'
            ],

            # Dividend Payment (DIVI)
            'DIVI': [
                'dividend payment', 'dividend distribution', 'shareholder dividend',
                'profit distribution', 'stock dividend', 'dividend income',
                'dividend yield', 'dividend payout', 'dividend reinvestment'
            ],

            # Trade Services (TRAD)
            'TRAD': [
                'trade services', 'trade payment', 'import export',
                'international trade', 'trade finance', 'trade settlement',
                'trade transaction', 'trade facilitation', 'trade credit'
            ],

            # Trade Settlement Payment (CORT)
            'CORT': [
                'trade settlement', 'correspondent banking', 'cover payment',
                'settlement instruction', 'clearing settlement', 'settlement payment',
                'correspondent payment', 'cover transfer', 'settlement transfer'
            ],

            # Treasury Payment (TREA)
            'TREA': [
                'treasury payment', 'treasury operation', 'treasury management',
                'treasury services', 'treasury transfer', 'treasury settlement',
                'treasury transaction', 'treasury activity', 'treasury function'
            ],

            # Cash Management Transfer (CASH)
            'CASH': [
                'cash management', 'liquidity management', 'cash pooling',
                'cash concentration', 'cash transfer', 'cash flow management',
                'cash optimization', 'cash forecasting', 'cash positioning'
            ],

            # Intra-Company Payment (INTC)
            'INTC': [
                'intra company', 'intercompany transfer', 'internal transfer',
                'subsidiary transfer', 'affiliate transfer', 'intra group payment',
                'intercompany settlement', 'internal settlement', 'group transfer'
            ],

            # Credit Card Payment (CCRD)
            'CCRD': [
                'credit card', 'credit card payment', 'credit card bill',
                'credit card settlement', 'credit card transaction', 'credit card account',
                'card bill payment', 'monthly credit card', 'visa payment',
                'mastercard payment', 'amex payment', 'discover payment'
            ],

            # Debit Card Payment (DCRD)
            'DCRD': [
                'debit card', 'debit card payment', 'debit card transaction',
                'debit card settlement', 'debit card purchase', 'debit card account',
                'atm card payment', 'bank card payment', 'maestro payment',
                'electron payment', 'debit card withdrawal'
            ],

            # Utility Bill (UBIL)
            'UBIL': [
                'utility bill', 'electricity bill', 'gas bill',
                'water bill', 'phone bill', 'internet bill',
                'cable bill', 'electric bill', 'electricity payment',
                'water payment', 'gas payment', 'phone payment',
                'internet payment', 'cable payment', 'utility service',
                'power bill', 'energy bill', 'telecom bill',
                'broadband bill', 'water service', 'electric service',
                'gas service'
            ],

            # ePayment (EPAY)
            'EPAY': [
                'epayment', 'electronic payment', 'online payment',
                'digital payment', 'e-payment', 'online transaction',
                'electronic funds transfer', 'digital transaction', 'payment gateway',
                'online purchase payment', 'mobile payment', 'app payment',
                'web payment', 'internet payment'
            ],

            # Foreign Exchange (FREX)
            'FREX': [
                'forex', 'foreign exchange', 'currency swap',
                'fx transaction', 'fx settlement', 'fx trade',
                'currency trade', 'currency transaction', 'currency exchange',
                'exchange rate', 'currency pair', 'spot exchange',
                'forward exchange'
            ],

            # Customs Payment (CUST)
            'CUST': [
                'customs duty', 'customs payment', 'import duty',
                'export duty', 'customs clearance', 'import tax',
                'customs fee', 'duty payment', 'customs declaration',
                'customs broker', 'customs agent'
            ]
        }

        # Context patterns for category purpose codes
        self.context_patterns = [
            # Supplier Payment (SUPP)
            {
                'purpose_code': 'SUPP',
                'keywords': ['supplier', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'SUPP',
                'keywords': ['vendor', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'SUPP',
                'keywords': ['invoice', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },

            # Goods (GDDS)
            {
                'purpose_code': 'GDDS',
                'keywords': ['goods', 'purchase'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['merchandise', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'GDDS',
                'keywords': ['product', 'purchase'],
                'proximity': 5,
                'weight': 0.9
            },

            # Salary Payment (SALA)
            {
                'purpose_code': 'SALA',
                'keywords': ['salary', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'SALA',
                'keywords': ['wage', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'SALA',
                'keywords': ['payroll', 'transfer'],
                'proximity': 5,
                'weight': 0.9
            },

            # Fee Collection (FCOL)
            {
                'purpose_code': 'FCOL',
                'keywords': ['fee', 'collection'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'FCOL',
                'keywords': ['tuition', 'fee'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'FCOL',
                'keywords': ['service', 'fee'],
                'proximity': 5,
                'weight': 0.9
            },

            # Credit Card Payment (CCRD)
            {
                'purpose_code': 'CCRD',
                'keywords': ['credit', 'card', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },

            # Debit Card Payment (DCRD)
            {
                'purpose_code': 'DCRD',
                'keywords': ['debit', 'card', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },

            # Utility Bill (UBIL)
            {
                'purpose_code': 'UBIL',
                'keywords': ['utility', 'bill'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'UBIL',
                'keywords': ['electricity', 'bill'],
                'proximity': 5,
                'weight': 0.9
            },

            # ePayment (EPAY)
            {
                'purpose_code': 'EPAY',
                'keywords': ['electronic', 'payment'],
                'proximity': 5,
                'weight': 0.9
            },
            {
                'purpose_code': 'EPAY',
                'keywords': ['online', 'payment'],
                'proximity': 5,
                'weight': 0.9
            }
        ]

        # Semantic terms for similarity matching
        self.semantic_terms = [
            # Supplier Payment (SUPP)
            {'purpose_code': 'SUPP', 'term': 'supplier', 'threshold': 0.7, 'weight': 1.0},
            {'purpose_code': 'SUPP', 'term': 'vendor', 'threshold': 0.7, 'weight': 1.0},
            {'purpose_code': 'SUPP', 'term': 'invoice', 'threshold': 0.7, 'weight': 1.0},

            # Goods (GDDS)
            {'purpose_code': 'GDDS', 'term': 'goods', 'threshold': 0.7, 'weight': 1.0},
            {'purpose_code': 'GDDS', 'term': 'merchandise', 'threshold': 0.7, 'weight': 1.0},
            {'purpose_code': 'GDDS', 'term': 'product', 'threshold': 0.7, 'weight': 1.0},

            # Salary Payment (SALA)
            {'purpose_code': 'SALA', 'term': 'salary', 'threshold': 0.7, 'weight': 1.0},
            {'purpose_code': 'SALA', 'term': 'wage', 'threshold': 0.7, 'weight': 1.0},
            {'purpose_code': 'SALA', 'term': 'payroll', 'threshold': 0.7, 'weight': 1.0},

            # Fee Collection (FCOL)
            {'purpose_code': 'FCOL', 'term': 'fee', 'threshold': 0.7, 'weight': 1.0},
            {'purpose_code': 'FCOL', 'term': 'tuition', 'threshold': 0.7, 'weight': 1.0},
            {'purpose_code': 'FCOL', 'term': 'service fee', 'threshold': 0.7, 'weight': 1.0},

            # Credit Card Payment (CCRD)
            {'purpose_code': 'CCRD', 'term': 'credit card', 'threshold': 0.7, 'weight': 1.0},

            # Debit Card Payment (DCRD)
            {'purpose_code': 'DCRD', 'term': 'debit card', 'threshold': 0.7, 'weight': 1.0},

            # Utility Bill (UBIL)
            {'purpose_code': 'UBIL', 'term': 'utility bill', 'threshold': 0.7, 'weight': 1.0},
            {'purpose_code': 'UBIL', 'term': 'electricity bill', 'threshold': 0.7, 'weight': 1.0},

            # ePayment (EPAY)
            {'purpose_code': 'EPAY', 'term': 'electronic payment', 'threshold': 0.7, 'weight': 1.0},
            {'purpose_code': 'EPAY', 'term': 'online payment', 'threshold': 0.7, 'weight': 1.0}
        ]

    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification for category purpose codes using semantic understanding.

        Args:
            result: Initial classification result
            narration: Transaction narration
            message_type: Optional message type

        Returns:
            dict: Enhanced classification result
        """
        # Get current purpose code and confidence
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)

        logger.info(f"Category purpose enhancer called with narration: {narration}, purpose_code: {purpose_code}")

        # Get current category purpose code and confidence (if any)
        category_purpose_code = result.get('category_purpose_code')
        category_confidence = result.get('category_confidence', 0.0)

        # Don't override if already classified with high confidence
        if category_purpose_code and category_confidence >= 0.9:
            logger.debug(f"Already classified as {category_purpose_code} with high confidence: {category_confidence}")
            return result

        # For simple "Payment" narration with OTHR purpose code, use message type context
        if purpose_code == 'OTHR' and narration.lower() == 'payment' and message_type:
            if message_type == 'MT103':
                logger.info(f"Using SUPP for MT103 with generic payment narration")
                return self._create_enhanced_result(result, 'SUPP', 0.7,
                                                  f"MT103 message type with payment context")
            elif message_type == 'MT202':
                logger.info(f"Using INTC for MT202 with generic payment narration")
                return self._create_enhanced_result(result, 'INTC', 0.7,
                                                  f"MT202 message type default")
            elif message_type == 'MT202COV':
                logger.info(f"Using CORT for MT202COV with generic payment narration")
                return self._create_enhanced_result(result, 'CORT', 0.7,
                                                  f"MT202COV message type default")

        # Special case for utility bill payments
        if 'electricity bill' in narration.lower() or 'utility bill' in narration.lower():
            logger.info(f"UBIL keyword match: electricity/utility bill with confidence 0.95")
            return self._create_enhanced_result(result, 'UBIL', 0.95,
                                              f"Direct keyword match: electricity/utility bill")

        # Special case for investment-related narrations
        if 'investment' in narration.lower() and 'equity' in narration.lower():
            logger.info(f"SECU keyword match: investment in equity with confidence 0.95")
            return self._create_enhanced_result(result, 'SECU', 0.95,
                                              f"Direct keyword match: investment in equity")

        # Special case for goods-related narrations
        if 'office supplies' in narration.lower() or 'merchandise' in narration.lower():
            logger.info(f"GDDS keyword match: office supplies/merchandise with confidence 0.95")
            return self._create_enhanced_result(result, 'GDDS', 0.95,
                                              f"Direct keyword match: office supplies/merchandise")

        # Use the mapper to get the category purpose code
        mapped_category, mapped_confidence, mapping_reason = self.mapper.map_purpose_to_category(
            purpose_code, narration, message_type, confidence
        )

        # Direct keyword matching (highest confidence)
        for category_code in self.direct_keywords:
            matched, keyword_confidence, keyword = self.direct_keyword_match(narration, category_code)
            if matched:
                logger.info(f"{category_code} keyword match: {keyword} with confidence {keyword_confidence}")
                return self._create_enhanced_result(result, category_code, keyword_confidence,
                                                  f"Direct keyword match: {keyword}")

        # Semantic context pattern matching
        context_score = self.context_match(narration, self.context_patterns)
        if context_score >= 0.7:
            # Find the purpose code with the highest score
            best_category_code = None
            best_score = 0.0

            for pattern in self.context_patterns:
                pattern_category_code = pattern.get('purpose_code')
                pattern_keywords = pattern.get('keywords', [])
                pattern_proximity = pattern.get('proximity', 5)

                # Check if keywords are in proximity
                words = self.matcher.tokenize(narration.lower())
                if self.matcher.keywords_in_proximity(words, pattern_keywords, pattern_proximity):
                    pattern_weight = pattern.get('weight', 0.9)
                    if pattern_weight > best_score:
                        best_score = pattern_weight
                        best_category_code = pattern_category_code

            if best_category_code:
                logger.info(f"Context match for {best_category_code} with score: {context_score:.2f}")
                return self._create_enhanced_result(result, best_category_code, min(0.95, context_score),
                                                  f"Context match with score: {context_score:.2f}")

        # Special case for SCVE - always map to SUPP
        if purpose_code == 'SCVE':
            logger.info(f"SPECIAL CASE: Using direct mapping for SCVE -> SUPP")
            enhanced_result = self._create_enhanced_result(result, 'SUPP', 0.99, f"Direct mapping from SCVE to SUPP")
            logger.info(f"Enhanced result: {enhanced_result}")
            return enhanced_result

        # If purpose code is not OTHR, use direct mapping as a reliable fallback
        if purpose_code != 'OTHR':
            # Check if the purpose code exists in the mapper's direct mappings
            if purpose_code in self.mapper.direct_mappings:
                fallback_category = self.mapper.direct_mappings[purpose_code]
                fallback_confidence = 0.9
                logger.info(f"Using direct mapping: {purpose_code} -> {fallback_category}")
                return self._create_enhanced_result(result, fallback_category, fallback_confidence,
                                                  f"Direct mapping from {purpose_code} to {fallback_category}")

        # Semantic similarity matching (only if we haven't found a better match)
        matched, sem_confidence, sem_category_code, sem_matches = self.semantic_similarity_match(narration, self.semantic_terms)
        if matched:
            # For OTHR purpose code with just "Payment", prefer SUPP over SALA
            if purpose_code == 'OTHR' and narration.lower() == 'payment' and sem_category_code == 'SALA':
                logger.info(f"Overriding SALA to SUPP for generic payment narration")
                return self._create_enhanced_result(result, 'SUPP', 0.6,
                                                  f"Default mapping for generic payment narration")

            logger.info(f"{sem_category_code} semantic match with confidence: {sem_confidence:.2f}")
            return self._create_enhanced_result(result, sem_category_code, sem_confidence,
                                              f"Semantic similarity matches: {len(sem_matches)}")

        # If we get here, use the mapped category from the mapper
        if mapped_category and mapped_category != 'OTHR':
            logger.info(f"Using mapped category {mapped_category} with confidence {mapped_confidence:.2f}")
            return self._create_enhanced_result(result, mapped_category, mapped_confidence, mapping_reason)

        # Final fallback: Use SUPP as a safe default (never use OTHR)
        if not category_purpose_code or category_purpose_code == 'OTHR':
            logger.info(f"Final fallback to SUPP for unknown purpose code: {purpose_code}")
            return self._create_enhanced_result(result, 'SUPP', 0.5,
                                              f"Final fallback for unknown purpose code: {purpose_code}")

        # No enhancement applied, return original result
        return result

    def _create_enhanced_result(self, original_result, category_purpose_code, confidence, reason):
        """
        Create an enhanced result dictionary.

        Args:
            original_result: Original classification result
            category_purpose_code: Enhanced category purpose code
            confidence: Enhanced confidence
            reason: Reason for enhancement

        Returns:
            dict: Enhanced classification result
        """
        # Create a copy of the original result
        result = original_result.copy()

        # Update with enhanced values
        result['category_purpose_code'] = category_purpose_code
        result['category_confidence'] = confidence

        # Add enhancement metadata
        result['category_enhanced'] = True
        result['category_enhancement_applied'] = 'category_purpose_enhancer_semantic'
        result['category_reason'] = reason
        result['original_category_purpose_code'] = original_result.get('category_purpose_code')
        result['original_category_confidence'] = original_result.get('category_confidence')

        # Log the enhancement
        logger.info(f"Category purpose enhanced: {original_result.get('category_purpose_code', 'None')} -> {category_purpose_code} (confidence: {confidence})")
        logger.info(f"Reason: {reason}")

        return result
