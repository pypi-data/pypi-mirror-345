"""
Purpose Classifier Package

A high-accuracy machine learning system for classifying purpose codes and category purpose codes from SWIFT message narrations.
"""

from .classifier import InterbankDomainEnhancer
from .lightgbm_classifier import LightGBMPurposeClassifier
from .utils.message_parser import detect_message_type, extract_narration, extract_all_fields
from .utils.preprocessor import TextPreprocessor

__version__ = "1.2.0"
__author__ = "Solchos"
__email__ = "solchos@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/solchos/purpose-classifier-package"

__all__ = [
    "InterbankDomainEnhancer",
    "LightGBMPurposeClassifier",
    "detect_message_type",
    "extract_narration",
    "extract_all_fields",
    "TextPreprocessor"
]