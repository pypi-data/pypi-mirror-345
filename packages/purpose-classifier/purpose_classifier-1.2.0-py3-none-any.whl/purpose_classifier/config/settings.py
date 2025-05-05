"""
Configuration settings for the Purpose Code Classifier.
Defines environment-specific settings, model parameters, and paths.
"""

import os
import json
import logging
from pathlib import Path

# Import from config.py
from purpose_classifier.config.config import (
    BASE_DIR, MODEL_PATH, PURPOSE_CODES_PATH, CATEGORY_PURPOSE_CODES_PATH,
    MODEL_SETTINGS as CONFIG_MODEL_SETTINGS, PROD_SETTINGS as CONFIG_PROD_SETTINGS,
    MESSAGE_TYPES as CONFIG_MESSAGE_TYPES, BANKING_PREPROCESS_CONFIG as CONFIG_BANKING_PREPROCESS_CONFIG,
    setup_logging, get_environment, get_environment_settings
)

# Use the paths from config.py
# PURPOSE_CODES_PATH is already defined in config.py
# CATEGORY_PURPOSE_CODES_PATH is already defined in config.py

# Path for sample messages
SAMPLE_MESSAGES_PATH = os.path.join(BASE_DIR, 'data', 'sample_messages.json')

# Use message types from config.py but add descriptions
MESSAGE_TYPES = CONFIG_MESSAGE_TYPES.copy()
# Add descriptions to message types
MESSAGE_TYPES['MT103']['description'] = 'Customer Credit Transfer'
MESSAGE_TYPES['MT202']['description'] = 'General Financial Institution Transfer'
MESSAGE_TYPES['MT202COV']['description'] = 'Cover Payment'
MESSAGE_TYPES['MT205']['description'] = 'Financial Institution Transfer Execution'
MESSAGE_TYPES['MT205COV']['description'] = 'Financial Institution Transfer Cover'

# Model settings - optimized for better performance
# Start with config settings and override with optimized values
MODEL_SETTINGS = CONFIG_MODEL_SETTINGS.copy()

# Update with optimized settings
MODEL_SETTINGS.update({
    # Classifier settings
    'classifier_type': 'random_forest',
    'n_estimators': 200,  # Increased from default for better accuracy
    'max_depth': 20,      # Deeper trees for more complex patterns
    'min_samples_split': 5,
    'min_samples_leaf': 2,

    # Feature extraction settings
    'max_features': 3000,  # Reduced from 5000 to save memory
    'ngram_range': (1, 2), # Reduced from (1,3) to save memory - only unigrams and bigrams
    'min_df': 2,           # Minimum document frequency
    'max_df': 0.95,        # Maximum document frequency

    # Confidence thresholds
    'min_confidence': 0.20,  # Reduced from 0.25 to allow more enhancer interventions
    'fallback_threshold': 0.15,

    # Feature selection
    'feature_selection': True,
    'k_best_features': 2000, # Reduced from 3000 to save memory

    # Domain enhancement settings
    'tech_threshold': 0.4,
    'education_threshold': 0.4,
    'services_threshold': 0.4,
    'trade_threshold': 0.4,
    'interbank_threshold': 0.4,
    'category_purpose_threshold': 0.25,  # Lower threshold to reduce OTHR usage
    'transportation_threshold': 0.4,
    'financial_services_threshold': 0.4,

    # Training settings
    'test_size': 0.2,
    'validation_size': 0.1,
    'cv_folds': 5,

    # Default settings
    'use_education_enhancer': True,
    'use_tech_enhancer': True,
    'use_services_enhancer': True,
    'use_trade_enhancer': True,
    'use_transportation_enhancer': True,
    'use_financial_services_enhancer': True,
    'use_category_purpose_enhancer': True,
    'fallback_strategy': 'most_frequent',
    'fallback_default': 'OTHR'
})

# Environment-specific settings
ENV_SETTINGS = {
    'development': {
        'log_level': logging.WARNING,  # Changed from DEBUG to WARNING to reduce verbosity
        'log_file': os.path.join(BASE_DIR, 'logs', 'dev_classifier.log'),
        'cache_enabled': True,
        'cache_size': 1000,
        'model_path': os.path.join(BASE_DIR, 'models', 'dev_purpose_classifier.joblib'),
        'model_version_file': os.path.join(BASE_DIR, 'models', 'dev_version.json'),
    },
    'test': {
        'log_level': logging.WARNING,  # Changed from INFO to WARNING to reduce verbosity
        'log_file': os.path.join(BASE_DIR, 'logs', 'test_classifier.log'),
        'cache_enabled': True,
        'cache_size': 5000,
        'model_path': os.path.join(BASE_DIR, 'models', 'test_purpose_classifier.joblib'),
        'model_version_file': os.path.join(BASE_DIR, 'models', 'test_version.json'),
    },
    'production': {
        'log_level': logging.ERROR,  # Changed from WARNING to ERROR to further reduce verbosity
        'log_file': os.path.join(BASE_DIR, 'logs', 'prod_classifier.log'),
        'cache_enabled': True,
        'cache_size': 10000,
        'model_path': MODEL_PATH,
        'model_version_file': os.path.join(BASE_DIR, 'models', 'prod_version.json'),
    }
}

# Production-specific settings - use config settings
PROD_SETTINGS = CONFIG_PROD_SETTINGS.copy()

# Banking-specific preprocessing configuration - use config settings
BANKING_PREPROCESS_CONFIG = CONFIG_BANKING_PREPROCESS_CONFIG.copy()

# Add additional banking preprocessing configuration if needed
BANKING_PREPROCESS_CONFIG.update({
    # Terms to keep even if they are in stopwords
    'keep_terms': {
        'payment', 'transfer', 'transaction', 'account', 'bank', 'credit', 'debit',
        'deposit', 'withdrawal', 'balance', 'loan', 'interest', 'fee', 'charge',
        'invoice', 'statement', 'salary', 'payroll', 'tax', 'dividend', 'investment',
        'mortgage', 'insurance', 'pension', 'retirement', 'savings', 'checking',
        'wire', 'ach', 'swift', 'iban', 'bic', 'routing', 'branch', 'atm',
        'card', 'visa', 'mastercard', 'amex', 'discover', 'cash', 'check', 'cheque',
        'draft', 'order', 'remittance', 'advice', 'notice', 'receipt', 'confirmation',
        'authorization', 'approval', 'rejection', 'reversal', 'return', 'refund',
        'chargeback', 'dispute', 'claim', 'inquiry', 'request', 'application',
        'subscription', 'membership', 'dues', 'contribution', 'donation', 'grant',
        'scholarship', 'bursary', 'stipend', 'allowance', 'benefit', 'bonus',
        'commission', 'compensation', 'reimbursement', 'expense', 'travel', 'per diem',
        'mileage', 'accommodation', 'lodging', 'meal', 'entertainment', 'utility',
        'electricity', 'water', 'gas', 'phone', 'internet', 'cable', 'television',
        'rent', 'lease', 'purchase', 'sale', 'acquisition', 'disposal', 'settlement',
        'closing', 'escrow', 'title', 'deed', 'contract', 'agreement', 'terms',
        'conditions', 'policy', 'coverage', 'premium', 'claim', 'benefit', 'payout',
        'annuity', 'maturity', 'surrender', 'withdrawal', 'distribution', 'allocation',
        'rebalance', 'diversification', 'portfolio', 'asset', 'equity', 'stock',
        'bond', 'fund', 'etf', 'mutual', 'index', 'option', 'future', 'swap',
        'derivative', 'commodity', 'currency', 'forex', 'exchange', 'rate', 'quote',
        'bid', 'ask', 'spread', 'margin', 'leverage', 'collateral', 'security',
        'pledge', 'lien', 'encumbrance', 'guarantee', 'surety', 'endorsement',
        'signature', 'authorization', 'authentication', 'verification', 'validation',
        'compliance', 'regulation', 'law', 'rule', 'policy', 'procedure', 'guideline',
        'standard', 'requirement', 'obligation', 'duty', 'responsibility', 'liability',
        'risk', 'exposure', 'hedge', 'protection', 'insurance', 'assurance', 'warranty',
        'indemnity', 'compensation', 'damages', 'penalty', 'fine', 'sanction',
        'restriction', 'limitation', 'prohibition', 'ban', 'embargo', 'boycott',
        'blacklist', 'whitelist', 'watchlist', 'screening', 'monitoring', 'surveillance',
        'audit', 'examination', 'inspection', 'investigation', 'inquiry', 'probe',
        'review', 'assessment', 'evaluation', 'analysis', 'report', 'statement',
        'declaration', 'certification', 'attestation', 'affirmation', 'confirmation',
        'acknowledgment', 'receipt', 'acceptance', 'rejection', 'denial', 'refusal',
        'objection', 'protest', 'dispute', 'challenge', 'contest', 'appeal', 'petition',
        'application', 'submission', 'filing', 'registration', 'enrollment', 'subscription',
        'membership', 'affiliation', 'association', 'relationship', 'connection',
        'link', 'tie', 'bond', 'obligation', 'commitment', 'pledge', 'promise',
        'undertaking', 'assurance', 'guarantee', 'warranty', 'representation',
        'statement', 'disclosure', 'revelation', 'exposure', 'publication', 'announcement',
        'notification', 'alert', 'warning', 'caution', 'advice', 'recommendation',
        'suggestion', 'proposal', 'offer', 'bid', 'tender', 'quote', 'estimate',
        'projection', 'forecast', 'prediction', 'expectation', 'anticipation',
        'preparation', 'planning', 'scheduling', 'arrangement', 'organization',
        'coordination', 'management', 'administration', 'supervision', 'oversight',
        'governance', 'control', 'command', 'direction', 'guidance', 'leadership',
        'stewardship', 'custody', 'safekeeping', 'protection', 'preservation',
        'conservation', 'maintenance', 'upkeep', 'repair', 'renovation', 'restoration',
        'rehabilitation', 'reconstruction', 'rebuilding', 'redevelopment', 'renewal',
        'revitalization', 'regeneration', 'rejuvenation', 'revival', 'resurgence',
        'recovery', 'rebound', 'comeback', 'return', 'reversion', 'reversal',
        'rollback', 'withdrawal', 'retreat', 'recession', 'depression', 'downturn',
        'slump', 'decline', 'decrease', 'reduction', 'diminution', 'contraction',
        'shrinkage', 'compression', 'consolidation', 'concentration', 'centralization',
        'decentralization', 'distribution', 'allocation', 'apportionment', 'assignment',
        'designation', 'specification', 'identification', 'recognition', 'acknowledgment',
        'appreciation', 'gratitude', 'thanks', 'acknowledgment', 'recognition',
        'award', 'reward', 'prize', 'bonus', 'incentive', 'motivation', 'inspiration',
        'encouragement', 'support', 'assistance', 'aid', 'help', 'service', 'benefit',
        'advantage', 'gain', 'profit', 'return', 'yield', 'income', 'revenue',
        'proceeds', 'earnings', 'gains', 'profits', 'returns', 'yields', 'dividends',
        'interest', 'rent', 'royalty', 'license', 'permit', 'authorization', 'approval',
        'consent', 'agreement', 'acceptance', 'acquiescence', 'compliance', 'conformity',
        'adherence', 'observance', 'obedience', 'submission', 'surrender', 'capitulation',
        'concession', 'compromise', 'settlement', 'resolution', 'determination',
        'decision', 'judgment', 'ruling', 'verdict', 'finding', 'conclusion',
        'opinion', 'view', 'perspective', 'standpoint', 'position', 'stance',
        'attitude', 'approach', 'method', 'technique', 'procedure', 'process',
        'system', 'structure', 'framework', 'architecture', 'design', 'plan',
        'scheme', 'strategy', 'tactic', 'maneuver', 'move', 'action', 'activity',
        'operation', 'function', 'task', 'duty', 'job', 'work', 'labor', 'effort',
        'exertion', 'endeavor', 'attempt', 'try', 'essay', 'venture', 'undertaking',
        'enterprise', 'initiative', 'project', 'program', 'campaign', 'drive',
        'push', 'thrust', 'effort', 'move', 'movement', 'trend', 'tendency',
        'drift', 'shift', 'change', 'alteration', 'modification', 'adjustment',
        'adaptation', 'accommodation', 'reconciliation', 'harmonization', 'integration',
        'incorporation', 'inclusion', 'involvement', 'participation', 'engagement',
        'commitment', 'dedication', 'devotion', 'loyalty', 'allegiance', 'fidelity',
        'faithfulness', 'constancy', 'steadfastness', 'firmness', 'resolution',
        'determination', 'persistence', 'perseverance', 'tenacity', 'endurance',
        'stamina', 'fortitude', 'courage', 'bravery', 'valor', 'gallantry',
        'heroism', 'intrepidity', 'boldness', 'daring', 'audacity', 'temerity',
        'rashness', 'recklessness', 'carelessness', 'negligence', 'dereliction',
        'default', 'failure', 'omission', 'oversight', 'error', 'mistake', 'fault',
        'flaw', 'defect', 'deficiency', 'shortcoming', 'inadequacy', 'insufficiency',
        'lack', 'want', 'need', 'requirement', 'necessity', 'essential', 'requisite',
        'prerequisite', 'precondition', 'condition', 'stipulation', 'provision',
        'term', 'clause', 'article', 'section', 'paragraph', 'sentence', 'phrase',
        'word', 'expression', 'term', 'designation', 'appellation', 'title',
        'name', 'label', 'tag', 'mark', 'brand', 'logo', 'emblem', 'insignia',
        'badge', 'symbol', 'sign', 'token', 'indication', 'evidence', 'proof',
        'demonstration', 'manifestation', 'expression', 'display', 'exhibition',
        'presentation', 'performance', 'execution', 'implementation', 'realization',
        'actualization', 'materialization', 'embodiment', 'incarnation', 'personification',
        'exemplification', 'illustration', 'instance', 'example', 'case', 'specimen',
        'sample', 'model', 'prototype', 'archetype', 'paradigm', 'standard', 'benchmark',
        'criterion', 'measure', 'gauge', 'yardstick', 'touchstone', 'reference',
        'guide', 'manual', 'handbook', 'textbook', 'primer', 'introduction', 'overview',
        'summary', 'synopsis', 'abstract', 'precis', 'digest', 'compendium', 'anthology',
        'collection', 'compilation', 'selection', 'assortment', 'variety', 'range',
        'array', 'spectrum', 'gamut', 'scale', 'series', 'sequence', 'succession',
        'progression', 'procession', 'train', 'chain', 'string', 'line', 'row',
        'column', 'file', 'rank', 'tier', 'level', 'grade', 'class', 'category',
        'classification', 'division', 'section', 'segment', 'portion', 'part',
        'piece', 'fragment', 'fraction', 'component', 'constituent', 'element',
        'ingredient', 'factor', 'aspect', 'facet', 'feature', 'characteristic',
        'attribute', 'quality', 'property', 'trait', 'peculiarity', 'idiosyncrasy',
        'quirk', 'eccentricity', 'oddity', 'anomaly', 'aberration', 'deviation',
        'digression', 'departure', 'divergence', 'variation', 'variance', 'difference',
        'distinction', 'contrast', 'comparison', 'analogy', 'similarity', 'resemblance',
        'likeness', 'affinity', 'kinship', 'relationship', 'connection', 'association',
        'correlation', 'correspondence', 'parallel', 'equivalence', 'equality',
        'parity', 'uniformity', 'consistency', 'regularity', 'constancy', 'stability',
        'steadiness', 'equilibrium', 'balance', 'symmetry', 'proportion', 'ratio',
        'rate', 'percentage', 'fraction', 'quotient', 'dividend', 'divisor',
        'multiplier', 'multiplicand', 'product', 'factor', 'coefficient', 'constant',
        'variable', 'function', 'equation', 'formula', 'expression', 'term',
        'polynomial', 'monomial', 'binomial', 'trinomial', 'quadratic', 'cubic',
        'quartic', 'quintic', 'sextic', 'septic', 'octic', 'nonic', 'decic'
    },

    # Common banking abbreviations and their expansions
    'abbreviations': {
        'acct': 'account',
        'amt': 'amount',
        'atm': 'automated teller machine',
        'bal': 'balance',
        'bene': 'beneficiary',
        'bic': 'bank identifier code',
        'btc': 'bitcoin',
        'ccy': 'currency',
        'chq': 'cheque',
        'cr': 'credit',
        'cust': 'customer',
        'dd': 'direct debit',
        'dep': 'deposit',
        'dr': 'debit',
        'eft': 'electronic funds transfer',
        'fx': 'foreign exchange',
        'iban': 'international bank account number',
        'int': 'interest',
        'inv': 'invoice',
        'kyc': 'know your customer',
        'loc': 'letter of credit',
        'mtm': 'mark to market',
        'neft': 'national electronic funds transfer',
        'noc': 'notice of change',
        'nre': 'non resident external',
        'nro': 'non resident ordinary',
        'od': 'overdraft',
        'otc': 'over the counter',
        'po': 'purchase order',
        'pmt': 'payment',
        'pos': 'point of sale',
        'pp': 'payable',
        'rcpt': 'receipt',
        'ref': 'reference',
        'rtgs': 'real time gross settlement',
        'rv': 'receivable',
        'sav': 'savings',
        'sepa': 'single euro payments area',
        'stmt': 'statement',
        'swift': 'society for worldwide interbank financial telecommunication',
        'trf': 'transfer',
        'txn': 'transaction',
        'upi': 'unified payments interface',
        'vat': 'value added tax',
        'w/d': 'withdrawal',
        'wt': 'wire transfer',
        'yld': 'yield'
    },

    # Common currency codes
    'currency_codes': [
        'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'HKD', 'NZD',
        'SEK', 'KRW', 'SGD', 'NOK', 'MXN', 'INR', 'RUB', 'ZAR', 'TRY', 'BRL',
        'TWD', 'DKK', 'PLN', 'THB', 'IDR', 'HUF', 'CZK', 'ILS', 'CLP', 'PHP',
        'AED', 'COP', 'SAR', 'MYR', 'RON'
    ]
})

def get_environment():
    """Get the current environment from environment variable or default to development"""
    return os.environ.get('PURPOSE_CLASSIFIER_ENV', 'development')

def get_environment_settings(env=None):
    """Get settings for the specified environment"""
    env = env or get_environment()
    if env not in ENV_SETTINGS:
        logging.warning(f"Unknown environment: {env}. Using development settings.")
        env = 'development'
    return ENV_SETTINGS[env]

def setup_logging(env=None):
    """Set up logging based on environment settings"""
    env = env or get_environment()
    env_settings = get_environment_settings(env)

    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(env_settings['log_file'])
    os.makedirs(log_dir, exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=env_settings['log_level'],
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(env_settings['log_file']),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger('purpose_classifier')

def get_settings(env=None):
    """Get all settings for the specified environment"""
    env_settings = get_environment_settings(env)
    return {
        'env': env or get_environment(),
        'model_settings': MODEL_SETTINGS,
        'env_settings': env_settings,
        'prod_settings': PROD_SETTINGS,
        'purpose_codes_path': PURPOSE_CODES_PATH,
        'category_purpose_codes_path': CATEGORY_PURPOSE_CODES_PATH,
        'model_path': env_settings['model_path'],
    }
