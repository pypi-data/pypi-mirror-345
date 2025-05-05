"""
Central configuration file for the MT Message Purpose Code Classifier.
Contains settings for paths, environments, model parameters, and production configurations.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# Import path helper
from purpose_classifier.config.path_helper import (
    get_package_root, get_project_root,
    get_data_file_path, get_model_file_path
)

# Load environment variables
load_dotenv()

# Base directory - use project root
BASE_DIR = get_project_root()

# Package directory
PACKAGE_DIR = get_package_root()

# Data paths - with fallbacks to package data
DATA_DIR = os.path.join(PACKAGE_DIR, 'data')
PROJECT_DATA_DIR = os.path.join(BASE_DIR, 'data')
TRAINING_DATA_PATH = os.path.join(PROJECT_DATA_DIR, 'final_strict_data.csv')
PROCESSED_DATA_DIR = os.path.join(PROJECT_DATA_DIR, 'processed')

# Purpose code paths - use path helper to find files
PURPOSE_CODES_PATH = get_data_file_path('purpose_codes.json')
CATEGORY_PURPOSE_CODES_PATH = get_data_file_path('category_purpose_codes.json')
SAMPLE_MESSAGES_PATH = get_data_file_path('sample_messages.json')

# Model paths
MODEL_DIR = os.path.join(BASE_DIR, 'models')
MODEL_PATH = get_model_file_path('combined_model.pkl')
MODEL_VERSION_FILE = get_model_file_path('model_version.json')

# Logs path
LOG_DIR = os.path.join(BASE_DIR, 'logs')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')

# Ensure directories exist
for directory in [DATA_DIR, MODEL_DIR, LOG_DIR]:
    os.makedirs(directory, exist_ok=True)

# Create project directories if they exist in the project root
for directory in [PROJECT_DATA_DIR, PROCESSED_DATA_DIR, BACKUP_DIR]:
    if os.path.dirname(directory) == BASE_DIR:  # Only create if it's in the project root
        os.makedirs(directory, exist_ok=True)

# Model hyperparameters
MODEL_SETTINGS = {
    # Feature extraction settings
    'max_features': 1500,
    'ngram_range': (1, 2),
    'min_df': 2,
    'max_df': 0.95,

    # Classifier settings
    'classifier_type': 'random_forest',  # Options: 'random_forest', 'svm', 'logistic_regression'
    'n_estimators': 100,
    'max_depth': None,
    'min_samples_split': 2,
    'min_samples_leaf': 1,
    'random_state': 42,

    # Performance thresholds
    'min_confidence': 0.6,
    'fallback_threshold': 0.3,

    # Cross-validation settings
    'cv_folds': 5,

    # Training settings
    'test_size': 0.2,
    'validation_size': 0.2,
}

# Environment configurations
ENVIRONMENTS = {
    'development': {
        'log_level': logging.DEBUG,
        'model_version_file': None,
        'backup_enabled': False,
        'monitoring_enabled': False,
        'cache_enabled': True,
        'cache_size': 500,
    },
    'test': {
        'log_level': logging.INFO,
        'model_version_file': MODEL_VERSION_FILE,
        'backup_enabled': True,
        'monitoring_enabled': True,
        'cache_enabled': True,
        'cache_size': 1000,
    },
    'production': {
        'log_level': logging.INFO,
        'model_version_file': MODEL_VERSION_FILE,
        'backup_enabled': True,
        'monitoring_enabled': True,
        'cache_enabled': True,
        'cache_size': 10000,
    }
}

# Production settings
PROD_SETTINGS = {
    'batch_size': int(os.getenv('BATCH_SIZE', 1000)),
    'max_workers': int(os.getenv('MAX_WORKERS', 4)),
    'timeout': int(os.getenv('TIMEOUT', 30)),
    'retry_attempts': int(os.getenv('RETRY_ATTEMPTS', 3)),
    'cache_size': int(os.getenv('CACHE_SIZE', 10000)),
    'processing_queue_size': int(os.getenv('QUEUE_SIZE', 10000)),
    'max_request_size': int(os.getenv('MAX_REQUEST_SIZE', '10485760').split('#')[0].strip()),  # 10MB
}

# Message type configurations
MESSAGE_TYPES = {
    'MT103': {
        'narration_field': '70',
        'regex_pattern': r':70:(.*?)(?=:\d{2}[A-Z]:|$)',
    },
    'MT202': {
        'narration_field': '72',
        'regex_pattern': r':72:(.*?)(?=:\d{2}[A-Z]:|$)',
    },
    'MT202COV': {
        'narration_field': '72',
        'regex_pattern': r':72:(.*?)(?=:\d{2}[A-Z]:|$)',
    },
    'MT205': {
        'narration_field': '72',
        'regex_pattern': r':72:(.*?)(?=:\d{2}[A-Z]:|$)',
    },
    'MT205COV': {
        'narration_field': '72',
        'regex_pattern': r':72:(.*?)(?=:\d{2}[A-Z]:|$)',
    },
}

# Banking-specific preprocessing configs
BANKING_PREPROCESS_CONFIG = {
    # Terms to always keep (never remove as stopwords)
    'keep_terms': {
        # Payment-related terms
        'payment', 'invoice', 'salary', 'dividend', 'trade',
        'consulting', 'service', 'insurance', 'rent', 'transfer',
        'loan', 'interest', 'fee', 'tax', 'commission', 'bonus',
        'pension', 'refund', 'investment', 'treasury', 'settlement',
        'account', 'cover', 'management', 'bill', 'subscription',
        'intra', 'company', 'education', 'charity', 'customs',
        'license', 'royalty', 'advance', 'transportation',

        # Banking-specific terms
        'swift', 'wire', 'remittance', 'beneficiary', 'originator',
        'correspondent', 'intermediary', 'nostro', 'vostro', 'loro',
        'clearing', 'settlement', 'custody', 'escrow', 'collateral',
        'margin', 'principal', 'fiduciary', 'trustee', 'nominee',

        # Transaction types
        'purchase', 'sale', 'order', 'contract', 'agreement', 'lease',
        'credit', 'debit', 'installment', 'disbursement', 'reimbursement',

        # Financial terms
        'balance', 'liquidity', 'capital', 'equity', 'asset', 'liability',
        'revenue', 'income', 'expense', 'profit', 'loss', 'budget', 'fiscal',
        'accounting', 'reconciliation', 'finance', 'funding', 'appropriation',

        # Regulatory terms
        'compliance', 'regulation', 'sanctions', 'aml', 'kyc', 'fatca',
        'crs', 'mifid', 'gdpr', 'psd2', 'basel', 'solvency',

        # Corporate terms
        'corporation', 'enterprise', 'organization', 'corporate', 'subsidiary',
        'affiliate', 'holding', 'merger', 'acquisition', 'restructuring',

        # International terms
        'international', 'domestic', 'foreign', 'export', 'import', 'cross-border',
        'global', 'local', 'regional', 'jurisdiction', 'offshore', 'onshore'
    },

    # Common financial abbreviations and their expansions
    'abbreviations': {
        # Transaction-related
        'inv': 'invoice',
        'pmt': 'payment',
        'ref': 'reference',
        'sal': 'salary',
        'div': 'dividend',
        'int': 'interest',
        'acct': 'account',
        'mgmt': 'management',
        'trf': 'transfer',
        'tx': 'transaction',
        'pens': 'pension',
        'govt': 'government',

        # Banking-specific
        'ben': 'beneficiary',
        'orig': 'originator',
        'corr': 'correspondent',
        'int': 'intermediary',
        'stmt': 'statement',
        'bal': 'balance',
        'dep': 'deposit',
        'wd': 'withdrawal',
        'fx': 'foreign exchange',
        'rec': 'receivable',
        'pay': 'payable',
        'poc': 'purpose of currency',
        'pod': 'purpose of debit',
        'eft': 'electronic funds transfer',
        'rtgs': 'real time gross settlement',

        # Corporate-related
        'co': 'company',
        'corp': 'corporation',
        'inc': 'incorporated',
        'intl': 'international',
        'ltd': 'limited',
        'plc': 'public limited company',

        # Other
        'amt': 'amount',
        'apr': 'annual percentage rate',
        'atm': 'automated teller machine',
        'ccy': 'currency',
        'cus': 'customer',
        'dd': 'direct debit',
        'id': 'identification',
        'ira': 'individual retirement account',
        'kyc': 'know your customer',
        'lc': 'letter of credit',
        'mm': 'money market',
        'mtg': 'mortgage',
        'nda': 'non-disclosure agreement',
        'poc': 'proof of concept',
        'po': 'purchase order',
        'pp': 'payable party',
        'qtr': 'quarter',
        'rp': 'receiving party',
        'sc': 'service charge',
        'sm': 'statement of means',
        'so': 'standing order',
        'tbd': 'to be determined',
        'tpa': 'third party agreement',
        'yr': 'year'
    },

    # Currency codes to normalize
    'currency_codes': [
        'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'CNY',
        'INR', 'SGD', 'HKD', 'ZAR', 'RUB', 'BRL', 'MXN',
        'NZD', 'SEK', 'NOK', 'DKK', 'PLN', 'TRY', 'AED', 'SAR',
        'THB', 'MYR', 'IDR', 'PHP', 'TWD', 'KRW', 'ILS', 'CZK',
        'HUF', 'RON', 'BGN', 'HRK', 'ISK', 'UAH', 'RSD', 'KWD',
        'QAR', 'BHD', 'OMR', 'JOD', 'EGP', 'MAD', 'NGN', 'KES'
    ]
}

# Logging configuration
def setup_logging(environment='production'):
    """Set up logging configuration based on environment"""
    env_config = ENVIRONMENTS[environment]
    log_file = os.path.join(LOG_DIR, f'mt_classifier_{environment}.log')

    logging.basicConfig(
        level=env_config['log_level'],
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )

    # Reduce verbosity of third-party libraries
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('nltk').setLevel(logging.WARNING)
    logging.getLogger('sklearn').setLevel(logging.WARNING)
    logging.getLogger('tensorflow').setLevel(logging.WARNING)

    return logging.getLogger('purpose_classifier')

# API and service settings
API_SETTINGS = {
    'host': os.getenv('API_HOST', '0.0.0.0'),
    'port': int(os.getenv('API_PORT', 5000)),
    'debug': os.getenv('API_DEBUG', 'False').lower() == 'true',
    'workers': int(os.getenv('API_WORKERS', 4)),
    'timeout': int(os.getenv('API_TIMEOUT', 60)),
    'max_request_size': int(os.getenv('MAX_REQUEST_SIZE', '10485760').split('#')[0].strip()),  # 10MB
    'rate_limit': int(os.getenv('RATE_LIMIT', 100)),  # requests per minute
}

# Security settings
SECURITY_SETTINGS = {
    'api_key_required': os.getenv('API_KEY_REQUIRED', 'True').lower() == 'true',
    'api_key_header': os.getenv('API_KEY_HEADER', 'X-API-Key'),
    'default_api_key': os.getenv('DEFAULT_API_KEY', None),
    'ssl_enabled': os.getenv('SSL_ENABLED', 'True').lower() == 'true',
    'ssl_cert': os.getenv('SSL_CERT', None),
    'ssl_key': os.getenv('SSL_KEY', None),
}

# Function to get current environment
def get_environment():
    """Get the current environment from environment variable or default to production"""
    return os.getenv('ENVIRONMENT', 'production')

# Get environment-specific settings
def get_environment_settings(environment=None):
    """Get settings for the specified environment or current environment"""
    env = environment or get_environment()
    if env not in ENVIRONMENTS:
        raise ValueError(f"Invalid environment: {env}. Must be one of {list(ENVIRONMENTS.keys())}")
    return ENVIRONMENTS[env]
