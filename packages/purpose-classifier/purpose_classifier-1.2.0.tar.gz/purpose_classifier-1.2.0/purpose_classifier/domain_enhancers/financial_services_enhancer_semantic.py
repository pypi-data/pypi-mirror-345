"""
Financial Services Domain Enhancer for Purpose Code Classifier

This enhancer specializes in identifying financial services-related payments
and improving classification accuracy for these types of transactions.
Uses advanced pattern matching with regular expressions and semantic understanding.
"""

import re
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer
import logging

logger = logging.getLogger(__name__)

class FinancialServicesDomainEnhancer(SemanticEnhancer):
    """
    Domain-specific enhancer for financial services-related payments.
    Helps reduce OTHR usage by identifying financial services payments.
    Uses pattern matching with regular expressions and semantic understanding
    for different types of narrations.
    """

    def __init__(self, matcher=None):
        super().__init__(matcher=matcher)
        self._initialize_patterns()

        # Initialize confidence thresholds
        self.confidence_thresholds = {
            'high': 0.9,
            'medium': 0.7,
            'low': 0.5
        }

    def _initialize_patterns(self):
        """Initialize semantic patterns and contexts."""
        # Direct keywords with purpose codes
        self.direct_keywords = {
            'FINANCIAL': ["investment management", "asset management", "portfolio management", "wealth management", "fund management", "financial advisory", "investment advisory", "brokerage service", "securities trading", "trading commission", "custody fee", "management fee", "performance fee", "advisory fee", "transaction fee", "investment", "portfolio", "brokerage", "securities", "trading", "custody", "financial", "advisory", "wealth", "asset", "fund", "management", "commission", "fee", "account", "finance", "invest", "trade", "market", "stock", "bond", "equity", "debt", "derivative", "mutual fund", "etf", "hedge fund", "private equity", "venture capital", "capital"],
        }

        # Financial keywords with weights for scoring
        self.financial_keywords = {
            'investment management': 3.0,
            'asset management': 3.0,
            'portfolio management': 3.0,
            'wealth management': 3.0,
            'fund management': 3.0,
            'financial advisory': 3.0,
            'investment advisory': 3.0,
            'brokerage service': 3.0,
            'securities trading': 3.0,
            'trading commission': 3.0,
            'custody fee': 3.0,
            'management fee': 3.0,
            'performance fee': 3.0,
            'advisory fee': 3.0,
            'transaction fee': 3.0,
            'investment': 2.0,
            'portfolio': 2.0,
            'brokerage': 2.0,
            'securities': 2.0,
            'trading': 2.0,
            'custody': 2.0,
            'financial': 2.0,
            'advisory': 2.0,
            'wealth': 2.0,
            'asset': 2.0,
            'fund': 2.0,
            'management': 1.5,
            'commission': 1.5,
            'fee': 1.5,
            'account': 1.0,
            'finance': 1.0,
            'invest': 1.0,
            'trade': 1.0,
            'market': 1.0,
            'stock': 1.0,
            'bond': 1.0,
            'equity': 1.0,
            'debt': 1.0,
            'derivative': 1.0,
            'mutual fund': 2.0,
            'etf': 2.0,
            'hedge fund': 2.0,
            'private equity': 2.0,
            'venture capital': 2.0,
            'capital': 1.0,
        }

        # Financial purpose code mappings
        self.financial_purpose_mappings = {
            'investment management': 'SCVE',
            'asset management': 'SCVE',
            'portfolio management': 'SCVE',
            'wealth management': 'SCVE',
            'fund management': 'SCVE',
            'financial advisory': 'SCVE',
            'investment advisory': 'SCVE',
            'brokerage service': 'SCVE',
            'securities trading': 'SCVE',
            'trading commission': 'SCVE',
            'custody fee': 'SCVE',
            'management fee': 'SCVE',
            'performance fee': 'SCVE',
            'advisory fee': 'SCVE',
            'transaction fee': 'SCVE',
        }

        # Financial category mappings
        self.financial_category_mappings = {
            'investment management': 'INVS',
            'asset management': 'INVS',
            'portfolio management': 'INVS',
            'wealth management': 'INVS',
            'fund management': 'INVS',
            'investment': 'INVS',
            'portfolio': 'INVS',
            'fund': 'INVS',
            'securities trading': 'SECU',
            'brokerage service': 'SECU',
            'securities': 'SECU',
            'trading': 'SECU',
            'brokerage': 'SECU',
            'stock': 'SECU',
            'bond': 'SECU',
            'equity': 'SECU',
            'debt': 'SECU',
            'derivative': 'SECU',
            'mutual fund': 'SECU',
            'etf': 'SECU',
            'hedge fund': 'SECU',
            'financial advisory': 'SUPP',
            'investment advisory': 'SUPP',
            'advisory': 'SUPP',
            'custody': 'SECU',
            'custody fee': 'SECU',
        }

        # Semantic context patterns
        self.context_patterns = [
            {
                'purpose_code': 'OTHR',
                'keywords': ['othr'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['investment', 'asset', 'portfolio', 'wealth', 'fund', 'management', 'advisory', 'service', 'fee'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['management', 'advisory', 'service', 'fee', 'investment', 'asset', 'portfolio', 'wealth', 'fund'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['manage', 'managing', 'managed', 'investment', 'asset', 'portfolio', 'wealth', 'fund'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['investment', 'asset', 'portfolio', 'wealth', 'fund', 'manage', 'managing', 'managed'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['invest', 'investing', 'investment', 'into', 'fund', 'stock', 'bond', 'security', 'securities', 'mutual', 'fund', 'etf'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['fund', 'stock', 'bond', 'security', 'securities', 'mutual', 'fund', 'etf', 'invest', 'investing', 'investment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['purchase', 'buy', 'acquire', 'acquisition', 'fund', 'stock', 'bond', 'security', 'securities', 'mutual', 'fund', 'etf'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['fund', 'stock', 'bond', 'security', 'securities', 'mutual', 'fund', 'etf', 'purchase', 'buy', 'acquire', 'acquisition'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['transfer', 'deposit', 'allocation', 'into', 'investment', 'fund', 'portfolio', 'ira', '401k', 'retirement'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['investment', 'fund', 'portfolio', 'ira', '401k', 'retirement', 'transfer', 'deposit', 'allocation'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['investment', 'fund', 'portfolio', 'account', 'holding', 'position'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['account', 'holding', 'position', 'investment', 'fund', 'portfolio'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['stock', 'equity', 'share', 'bond', 'security', 'securities', 'trading', 'trade', 'transaction', 'purchase', 'sale', 'buy', 'sell'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['trading', 'trade', 'transaction', 'purchase', 'sale', 'buy', 'sell', 'stock', 'equity', 'share', 'bond', 'security', 'securities'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['portfolio', 'investment', 'funding', 'contribution', 'addition', 'deposit'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['funding', 'contribution', 'addition', 'deposit', 'portfolio', 'investment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['retirement', 'pension', 'ira', '401k', 'account', 'fund', 'investment', 'contribution', 'deposit'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['account', 'fund', 'investment', 'contribution', 'deposit', 'retirement', 'pension', 'ira', '401k'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['mutual', 'fund', 'etf', 'index', 'fund', 'exchange', 'traded', 'fund', 'investment', 'purchase', 'transaction', 'trade'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['investment', 'purchase', 'transaction', 'trade', 'mutual', 'fund', 'etf', 'index', 'fund', 'exchange', 'traded', 'fund'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['securities', 'purchase', 'transaction', 'investment', 'trading', 'trade'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['purchase', 'transaction', 'investment', 'trading', 'trade', 'securities'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['investment', 'portfolio', 'securities', 'portfolio'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['stock', 'market', 'securities', 'market', 'bond', 'market', 'investment', 'transaction', 'trade'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['investment', 'transaction', 'trade', 'stock', 'market', 'securities', 'market', 'bond', 'market'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['dividend', 'interest', 'yield', 'return', 'investment', 'stock', 'bond', 'fund', 'security', 'securities'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['investment', 'stock', 'bond', 'fund', 'security', 'securities', 'dividend', 'interest', 'yield', 'return'],
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
                'keywords': ['securities', 'stock', 'bond', 'equity', 'share', 'etf', 'mutual', 'fund', 'trading', 'brokerage', 'transaction', 'commission', 'fee'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['trading', 'brokerage', 'transaction', 'commission', 'fee', 'securities', 'stock', 'bond', 'equity', 'share', 'etf', 'mutual', 'fund'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['buy', 'sell', 'trade', 'trading', 'purchase', 'sale', 'securities', 'stock', 'bond', 'equity', 'share', 'etf', 'mutual', 'fund'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['securities', 'stock', 'bond', 'equity', 'share', 'etf', 'mutual', 'fund', 'buy', 'sell', 'trade', 'trading', 'purchase', 'sale'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['financial', 'investment', 'wealth', 'advisory', 'advice', 'consulting', 'consultancy', 'planning'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['advisory', 'advice', 'consulting', 'consultancy', 'planning', 'financial', 'investment', 'wealth'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['advise', 'advising', 'advised', 'financial', 'investment', 'wealth', 'portfolio', 'asset'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['financial', 'investment', 'wealth', 'portfolio', 'asset', 'advise', 'advising', 'advised'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['custody', 'custodial', 'safekeeping', 'depository', 'service', 'fee', 'charge', 'account'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'fee', 'charge', 'account', 'custody', 'custodial', 'safekeeping', 'depository'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['asset', 'securities', 'investment', 'administration', 'administrative', 'custody', 'safekeeping'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['administration', 'administrative', 'custody', 'safekeeping', 'asset', 'securities', 'investment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['settlement', 'clearing', 'exchange', 'trade'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['investment', 'fund', 'portfolio', 'asset'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['text_lower:'],
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
        self.semantic_terms = [
            {
                'purpose_code': 'SCVE',
                'term': 'service',
                'threshold': 0.7,
                'weight': 1.0
            },
            {
                'purpose_code': 'SCVE',
                'term': 'consulting',
                'threshold': 0.7,
                'weight': 1.0
            },
            {
                'purpose_code': 'SCVE',
                'term': 'professional',
                'threshold': 0.7,
                'weight': 0.9
            },
            {
                'purpose_code': 'SCVE',
                'term': 'maintenance',
                'threshold': 0.7,
                'weight': 0.9
            },
            {
                'purpose_code': 'SCVE',
                'term': 'repair',
                'threshold': 0.7,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'term': 'installation',
                'threshold': 0.7,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'term': 'support',
                'threshold': 0.7,
                'weight': 0.8
            },
        ]

    def score_financial_relevance(self, text, message_type=None):
        """
        Score the relevance of the text to the financial services domain.
        Uses advanced pattern matching with regular expressions and semantic understanding.

        Args:
            text: The narration text
            message_type: Optional SWIFT message type (MT103, MT202, etc.)

        Returns:
            tuple: (score, matched_keywords, most_likely_purpose_code)
        """
        if not text:
            return 0.0, [], None

        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()

        # Initialize variables
        score = 0.0
        matched_keywords = []
        keyword_scores = {}
        pattern_matches = []

        # Check for each keyword
        for keyword, weight in self.financial_keywords.items():
            # Use word boundary regex pattern for more accurate matching
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower, re.IGNORECASE):
                score += weight
                matched_keywords.append(keyword)
                keyword_scores[keyword] = weight
                logger.debug(f"Matched financial keyword: {keyword} with weight {weight}")

        # Advanced pattern matching with semantic understanding
        # These patterns look for semantic relationships between words

        # Investment management patterns - Enhanced for better investment handling
        investment_patterns = [
            # Original investment management patterns
            r'\b(investment|asset|portfolio|wealth|fund)\b.*?\b(management|advisory|service|fee)\b',
            r'\b(management|advisory|service|fee)\b.*?\b(investment|asset|portfolio|wealth|fund)\b',
            r'\b(manage|managing|managed)\b.*?\b(investment|asset|portfolio|wealth|fund)\b',
            r'\b(investment|asset|portfolio|wealth|fund)\b.*?\b(manage|managing|managed)\b',

            # Additional investment patterns
            r'\b(invest|investing|investment)\b.*?\b(in|into|to)\b.*?\b(fund|stock|bond|security|securities|mutual fund|etf)\b',
            r'\b(fund|stock|bond|security|securities|mutual fund|etf)\b.*?\b(invest|investing|investment)\b',
            r'\b(purchase|buy|acquire|acquisition)\b.*?\b(fund|stock|bond|security|securities|mutual fund|etf)\b',
            r'\b(fund|stock|bond|security|securities|mutual fund|etf)\b.*?\b(purchase|buy|acquire|acquisition)\b',
            r'\b(transfer|deposit|allocation)\b.*?\b(to|into)\b.*?\b(investment|fund|portfolio|ira|401k|retirement)\b',
            r'\b(investment|fund|portfolio|ira|401k|retirement)\b.*?\b(transfer|deposit|allocation)\b',
            r'\b(investment|fund|portfolio)\b.*?\b(account|holding|position)\b',
            r'\b(account|holding|position)\b.*?\b(investment|fund|portfolio)\b',

            # Further enhanced investment patterns for better coverage
            r'\b(stock|equity|share|bond|security|securities)\b.*?\b(trading|trade|transaction|purchase|sale|buy|sell)\b',
            r'\b(trading|trade|transaction|purchase|sale|buy|sell)\b.*?\b(stock|equity|share|bond|security|securities)\b',
            r'\b(portfolio|investment)\b.*?\b(funding|contribution|addition|deposit)\b',
            r'\b(funding|contribution|addition|deposit)\b.*?\b(portfolio|investment)\b',
            r'\b(retirement|pension|ira|401k)\b.*?\b(account|fund|investment|contribution|deposit)\b',
            r'\b(account|fund|investment|contribution|deposit)\b.*?\b(retirement|pension|ira|401k)\b',
            r'\b(mutual\s+fund|etf|index\s+fund|exchange\s+traded\s+fund)\b.*?\b(investment|purchase|transaction|trade)\b',
            r'\b(investment|purchase|transaction|trade)\b.*?\b(mutual\s+fund|etf|index\s+fund|exchange\s+traded\s+fund)\b',
            r'\b(securities)\b.*?\b(purchase|transaction|investment|trading|trade)\b',
            r'\b(purchase|transaction|investment|trading|trade)\b.*?\b(securities)\b',
            r'\b(investment\s+portfolio|securities\s+portfolio)\b',
            r'\b(stock\s+market|securities\s+market|bond\s+market)\b.*?\b(investment|transaction|trade)\b',
            r'\b(investment|transaction|trade)\b.*?\b(stock\s+market|securities\s+market|bond\s+market)\b',
            r'\b(dividend|interest|yield|return)\b.*?\b(investment|stock|bond|fund|security|securities)\b',
            r'\b(investment|stock|bond|fund|security|securities)\b.*?\b(dividend|interest|yield|return)\b'
        ]

        for pattern in investment_patterns:
            if re.search(pattern, text_lower):
                score += 3.0  # High weight for semantic patterns
                pattern_matches.append("investment_management")
                logger.debug(f"Matched investment management pattern: {pattern}")
                break  # Only count once

        # Additional investment-specific keywords - Enhanced for better investment handling
        investment_keywords = [
            # Original investment keywords
            'investment', 'invest', 'investing', 'investor', 'fund', 'mutual fund',
            'etf', 'exchange traded fund', 'stock', 'share', 'equity', 'bond',
            'security', 'securities', 'portfolio', 'asset allocation', 'asset management',
            'wealth management', 'financial advisor', 'broker', 'brokerage',
            'retirement', 'ira', '401k', 'pension', 'annuity', 'dividend',
            'capital gain', 'yield', 'return', 'market', 'trading', 'trade',

            # Additional investment keywords for better coverage
            'securities purchase', 'stock purchase', 'bond purchase', 'fund purchase',
            'investment portfolio', 'securities portfolio', 'stock portfolio', 'bond portfolio',
            'investment account', 'securities account', 'brokerage account', 'trading account',
            'retirement account', 'retirement fund', 'retirement investment', 'retirement portfolio',
            'pension fund', 'pension investment', 'pension portfolio', 'pension account',
            'ira account', 'ira investment', 'ira fund', 'ira portfolio',
            '401k account', '401k investment', '401k fund', '401k portfolio',
            'index fund', 'mutual fund investment', 'etf investment', 'exchange traded fund investment',
            'stock market', 'bond market', 'securities market', 'investment market',
            'dividend payment', 'interest payment', 'investment return', 'investment yield',
            'portfolio funding', 'portfolio contribution', 'investment contribution', 'investment deposit',
            'securities trading', 'stock trading', 'bond trading', 'fund trading',
            'investment transaction', 'securities transaction', 'stock transaction', 'bond transaction'
        ]

        # Check for investment keywords - Enhanced for better investment detection
        investment_keyword_count = 0
        matched_investment_keywords = []

        # First check for high-value multi-word investment keywords (more specific)
        high_value_keywords = [kw for kw in investment_keywords if ' ' in kw]
        for keyword in high_value_keywords:
            if keyword in text_lower:
                investment_keyword_count += 2  # Give higher weight to multi-word matches
                matched_investment_keywords.append(keyword)
                logger.debug(f"Found high-value investment keyword: {keyword}")

        # Then check for single-word investment keywords
        single_word_keywords = [kw for kw in investment_keywords if ' ' not in kw]
        for keyword in single_word_keywords:
            # Use word boundary to avoid partial matches
            if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                investment_keyword_count += 1
                matched_investment_keywords.append(keyword)
                logger.debug(f"Found investment keyword: {keyword}")

        # Adjust scoring based on keyword count
        if investment_keyword_count >= 4:  # Multiple strong matches
            score += 3.5
            pattern_matches.append("investment_keywords_strong")
            logger.debug(f"Multiple strong investment keywords found: {investment_keyword_count}")
        elif investment_keyword_count >= 2:  # At least 2 investment keywords
            score += 2.5
            pattern_matches.append("investment_keywords")
            logger.debug(f"Multiple investment keywords found: {investment_keyword_count}")
        elif investment_keyword_count == 1 and any(kw in matched_investment_keywords for kw in ['securities', 'stock', 'bond', 'fund', 'investment']):
            # Even a single strong keyword should count
            score += 1.5
            pattern_matches.append("investment_keyword_single")
            logger.debug(f"Single strong investment keyword found: {matched_investment_keywords[0]}")

        # Securities trading patterns
        securities_patterns = [
            r'\b(securities|stock|bond|equity|share|etf|mutual\s+fund)\b.*?\b(trading|brokerage|transaction|commission|fee)\b',
            r'\b(trading|brokerage|transaction|commission|fee)\b.*?\b(securities|stock|bond|equity|share|etf|mutual\s+fund)\b',
            r'\b(buy|sell|trade|trading|purchase|sale)\b.*?\b(securities|stock|bond|equity|share|etf|mutual\s+fund)\b',
            r'\b(securities|stock|bond|equity|share|etf|mutual\s+fund)\b.*?\b(buy|sell|trade|trading|purchase|sale)\b'
        ]

        for pattern in securities_patterns:
            if re.search(pattern, text_lower):
                score += 3.0  # High weight for semantic patterns
                pattern_matches.append("securities_trading")
                logger.debug(f"Matched securities trading pattern: {pattern}")
                break  # Only count once

        # Financial advisory patterns
        advisory_patterns = [
            r'\b(financial|investment|wealth)\b.*?\b(advisory|advice|consulting|consultancy|planning)\b',
            r'\b(advisory|advice|consulting|consultancy|planning)\b.*?\b(financial|investment|wealth)\b',
            r'\b(advise|advising|advised)\b.*?\b(financial|investment|wealth|portfolio|asset)\b',
            r'\b(financial|investment|wealth|portfolio|asset)\b.*?\b(advise|advising|advised)\b'
        ]

        for pattern in advisory_patterns:
            if re.search(pattern, text_lower):
                score += 2.5  # High weight for semantic patterns
                pattern_matches.append("financial_advisory")
                logger.debug(f"Matched financial advisory pattern: {pattern}")
                break  # Only count once

        # Custody and administration patterns
        custody_patterns = [
            r'\b(custody|custodial|safekeeping|depository)\b.*?\b(service|fee|charge|account)\b',
            r'\b(service|fee|charge|account)\b.*?\b(custody|custodial|safekeeping|depository)\b',
            r'\b(asset|securities|investment)\b.*?\b(administration|administrative|custody|safekeeping)\b',
            r'\b(administration|administrative|custody|safekeeping)\b.*?\b(asset|securities|investment)\b'
        ]

        for pattern in custody_patterns:
            if re.search(pattern, text_lower):
                score += 2.5  # High weight for semantic patterns
                pattern_matches.append("custody_service")
                logger.debug(f"Matched custody pattern: {pattern}")
                break  # Only count once

        # Message type specific patterns
        if message_type == "MT202" or message_type == "MT202COV":
            # MT202/MT202COV often used for securities settlement
            if re.search(r'\b(settlement|clearing|exchange|trade)\b', text_lower):
                score += 1.5  # Boost for securities terms in MT202
                pattern_matches.append("mt202_securities_boost")
                logger.debug(f"Applied MT202 securities boost")

        elif message_type == "MT205" or message_type == "MT205COV":
            # MT205/MT205COV often used for investment transfers
            if re.search(r'\b(investment|fund|portfolio|asset)\b', text_lower):
                score += 1.5  # Boost for investment terms in MT205
                pattern_matches.append("mt205_investment_boost")
                logger.debug(f"Applied MT205 investment boost")

        # Add pattern matches to matched keywords
        matched_keywords.extend(pattern_matches)

        # Normalize score to 0-1 range if we found matches
        if matched_keywords:
            # Lower denominator to make it easier to reach higher scores
            score = min(score / 4, 1.0)  # Cap at 1.0
            logger.debug(f"Financial services score: {score}")

        # Determine most likely purpose code based on matched keywords and patterns
        most_likely_purpose = None

        # First check for dividend keywords with highest priority
        if 'dividend' in text_lower or 'shareholder' in text_lower:
            # Explicitly check for dividend-related keywords with highest priority
            if any(term in text_lower for term in ['dividend', 'shareholder dividend', 'dividend payment',
                                                 'dividend distribution', 'dividend payout', 'corporate dividend',
                                                 'interim dividend', 'final dividend', 'quarterly dividend',
                                                 'annual dividend', 'semi-annual dividend', 'stock dividend']):
                logger.debug(f"Dividend keyword matched in narration")
                most_likely_purpose = "DIVD"
                return score, matched_keywords, most_likely_purpose

        # Then check pattern matches for purpose code mapping - Enhanced for better investment handling
        for pattern_match in pattern_matches:
            if pattern_match in ["investment_management", "investment_keywords", "investment_keywords_strong", "investment_keyword_single"]:
                most_likely_purpose = "SCVE"
                break
            elif pattern_match == "securities_trading":
                most_likely_purpose = "SCVE"
                break
            elif pattern_match == "financial_advisory":
                most_likely_purpose = "SCVE"  # Changed from CONS to SCVE
                break
            elif pattern_match == "custody_service":
                most_likely_purpose = "SCVE"
                break

        # If no purpose code found from patterns, check keyword matches
        if not most_likely_purpose and matched_keywords:
            # Sort matched keywords by their score (weight)
            sorted_keywords = sorted(
                [(k, keyword_scores.get(k, 0)) for k in matched_keywords if k in keyword_scores],
                key=lambda x: x[1],
                reverse=True
            )

            # Try to find a purpose code mapping for the highest-scored keywords
            for keyword, _ in sorted_keywords:
                if keyword in self.financial_purpose_mappings:
                    most_likely_purpose = self.financial_purpose_mappings[keyword]
                    logger.debug(f"Selected purpose code {most_likely_purpose} from keyword {keyword}")
                    break

            # If no mapping found, default to SCVE
            if not most_likely_purpose:
                most_likely_purpose = "SCVE"
                logger.debug(f"Defaulted to SCVE purpose code")

        return score, matched_keywords, most_likely_purpose

    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification based on domain-specific knowledge for financial services domain.
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

        # Get financial services relevance score, matched keywords, and most likely purpose code
        domain_score, matched_keywords, most_likely_purpose = self.score_financial_relevance(narration, message_type)

        # Always add domain score and keywords to the result for analysis
        result['financial_score'] = domain_score
        result['financial_keywords'] = matched_keywords
        result['most_likely_financial_purpose'] = most_likely_purpose

        # Skip enhancement if confidence is already high AND domain score isn't very high
        if result.get('confidence', 0.3) >= self.confidence_thresholds["high"]:
            # For test_high_confidence_override, we need to preserve the original purpose code
            return result

        # Lower threshold for applying enhancement - more aggressive to reduce OTHR usage
        if domain_score < 0.15 or not most_likely_purpose:
            return result

        # Original prediction and confidence
        original_purpose = result['purpose_code']
        original_conf = result.get('confidence', 0.3)  # Default if not present

        # Message type specific considerations
        if message_type == "MT202" or message_type == "MT202COV":
            # MT202/MT202COV often used for securities settlement
            if "securities_trading" in matched_keywords or "mt202_securities_boost" in matched_keywords:
                # Boost domain score for securities in MT202
                domain_score = min(domain_score * 1.2, 1.0)
                logger.debug(f"Boosted domain score for securities in MT202: {domain_score}")

        elif message_type == "MT205" or message_type == "MT205COV":
            # MT205/MT205COV often used for investment transfers
            if "investment_management" in matched_keywords or "mt205_investment_boost" in matched_keywords:
                # Boost domain score for investments in MT205
                domain_score = min(domain_score * 1.2, 1.0)
                logger.debug(f"Boosted domain score for investments in MT205: {domain_score}")

        # Determine if we need to override or enhance the classification
        if domain_score >= 0.25:
            # High domain relevance, override to the most likely purpose code with high confidence
            result['purpose_code'] = most_likely_purpose

            # Blend original confidence with domain score - give more weight to domain_score
            adjusted_conf = (original_conf * 0.2) + (domain_score * 0.8)
            result['confidence'] = min(adjusted_conf, 0.95)  # Cap at 0.95

            # Add enhancement info
            result['enhancement_applied'] = "financial_services"
            result['enhanced'] = True
            result['enhancement_type'] = "financial_domain_override"
            result['reason'] = "financial_services match: financial_domain_override"
            # Add detailed reason for the override
            if "investment_management" in matched_keywords:
                result['reason'] = "investment_management_pattern"
            elif "securities_trading" in matched_keywords:
                result['reason'] = "securities_trading_pattern"
            elif "financial_advisory" in matched_keywords:
                result['reason'] = "financial_advisory_pattern"
            elif "custody_service" in matched_keywords:
                result['reason'] = "custody_service_pattern"
            else:
                result['reason'] = "high_financial_score"

            # Also enhance category purpose code if it's OTHR or not set
            if result.get('category_purpose_code') in ['OTHR', None, '']:
                # First check pattern matches for category purpose code mapping
                category_purpose_code = None

                # Check narration for specific keywords to determine category purpose code
                if "custody" in narration.lower() or "securities" in narration.lower():
                    category_purpose_code = "SECU"
                elif "advisory" in narration.lower() or "financial advisory" in narration.lower():
                    category_purpose_code = "SUPP"
                elif "investment" in narration.lower() or "portfolio" in narration.lower():
                    category_purpose_code = "INVS"
                else:
                    # Check pattern matches as fallback
                    for pattern_match in matched_keywords:
                        if pattern_match in ["investment_management", "investment_keywords", "investment_keywords_strong", "investment_keyword_single"]:
                            category_purpose_code = "INVS"
                            break
                        elif pattern_match == "securities_trading":
                            category_purpose_code = "SECU"
                            break
                        elif pattern_match == "financial_advisory":
                            category_purpose_code = "SUPP"
                            break
                        elif pattern_match == "custody_service":
                            category_purpose_code = "SECU"
                            break

                # If no category purpose code found from patterns, check keyword mappings
                if not category_purpose_code:
                    for keyword in matched_keywords:
                        if keyword in self.financial_category_mappings:
                            category_purpose_code = self.financial_category_mappings[keyword]
                            break

                # If we found a category purpose code, set it
                if category_purpose_code:
                    result['category_purpose_code'] = category_purpose_code
                    result['category_confidence'] = result['confidence']
                    result['category_enhancement_applied'] = "financial_category_mapping"
                    logger.debug(f"Set category purpose code to {category_purpose_code}")

        # Medium domain relevance - enhance if original is OTHR or low confidence
        elif domain_score > 0.15:
            if original_purpose == 'OTHR' or original_conf < self.confidence_thresholds["medium"]:
                result['purpose_code'] = most_likely_purpose

                # Blend confidences but give less weight to domain score
                adjusted_conf = (original_conf * 0.4) + (domain_score * 0.6)
                result['confidence'] = min(adjusted_conf, 0.9)  # Cap at 0.9

                # Add enhancement info
                result['enhancement_applied'] = "financial_services"
                result['enhanced'] = True
                result['enhancement_type'] = "financial_domain_enhancement"
                result['reason'] = "financial_services match: financial_domain_enhancement"
                # Also enhance category purpose code if it's OTHR or not set
                if result.get('category_purpose_code') in ['OTHR', None, '']:
                    # First check pattern matches for category purpose code mapping
                    category_purpose_code = None

                    for pattern_match in matched_keywords:
                        if pattern_match in ["investment_management", "investment_keywords", "investment_keywords_strong", "investment_keyword_single"]:
                            category_purpose_code = "INVS"
                            break
                        elif pattern_match == "securities_trading":
                            category_purpose_code = "SECU"
                            break
                        elif pattern_match == "financial_advisory":
                            category_purpose_code = "SUPP"
                            break
                        elif pattern_match == "custody_service":
                            category_purpose_code = "SECU"
                            break

                    # If no category purpose code found from patterns, check keyword mappings
                    if not category_purpose_code:
                        for keyword in matched_keywords:
                            if keyword in self.financial_category_mappings:
                                category_purpose_code = self.financial_category_mappings[keyword]
                                break

                    # If we found a category purpose code, set it
                    if category_purpose_code:
                        result['category_purpose_code'] = category_purpose_code
                        result['category_confidence'] = result['confidence']
                        result['category_enhancement_applied'] = "financial_category_mapping"
                        logger.debug(f"Set category purpose code to {category_purpose_code}")

        return result
