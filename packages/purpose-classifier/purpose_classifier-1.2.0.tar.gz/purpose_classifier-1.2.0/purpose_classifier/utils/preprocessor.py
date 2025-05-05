"""
Text preprocessing utilities for MT message narrations.
Provides functionality for cleaning, normalizing, and tokenizing text data.
"""

import re
import string
import logging
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from functools import lru_cache
import unicodedata

# Import configuration
import sys
import os
from purpose_classifier.config.settings import BANKING_PREPROCESS_CONFIG, PROD_SETTINGS, setup_logging, get_environment

# Ensure NLTK resources are available
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')


class TextPreprocessor:
    """
    Text preprocessing for financial message narrations.
    Handles cleaning, normalization, and tokenization with domain-specific adaptations.
    """

    def __init__(self):
        """Initialize the text preprocessor with banking-specific settings"""
        self.env = get_environment()
        self.logger = setup_logging(self.env)

        # Load stopwords but exclude financial terms
        self.stop_words = set(stopwords.words('english'))
        self.keep_terms = BANKING_PREPROCESS_CONFIG['keep_terms']

        # Add education-related terms to keep_terms
        self.education_terms = {
            'education', 'tuition', 'school', 'university', 'college',
            'semester', 'term', 'course', 'degree', 'academic', 'student',
            'scholarship', 'educational', 'learning', 'curriculum', 'program',
            'study', 'studies', 'faculty', 'campus', 'class', 'lecture',
            'professor', 'thesis', 'admission', 'enrollment', 'institute'
        }
        self.keep_terms.update(self.education_terms)

        self.financial_stopwords = self.stop_words - self.keep_terms

        # Set up lemmatizer
        self.lemmatizer = WordNetLemmatizer()

        # Load financial abbreviations
        self.abbreviations = BANKING_PREPROCESS_CONFIG['abbreviations']

        # Currency codes to normalize
        self.currency_codes = set(BANKING_PREPROCESS_CONFIG['currency_codes'])

        # Regex patterns for financial data
        self.account_pattern = re.compile(r'\b[A-Za-z]{1,4}\d{10,24}\b')  # IBAN-like pattern
        self.amount_pattern = re.compile(r'\b\d+[\.,]?\d*\s*[A-Za-z]{3}\b')  # Amount with currency code
        self.reference_pattern = re.compile(r'\b(?:ref|reference)[:\s]+([A-Za-z0-9\-_/]+)', re.IGNORECASE)
        self.invoice_pattern = re.compile(r'\b(?:inv|invoice)[:\s]+([A-Za-z0-9\-_/]+)', re.IGNORECASE)

        # Financial special characters to handle specially
        self.special_financial_chars = {
            '/': ' ',    # Slash used as line separator in MT messages
            '-': ' ',    # Often used in references
            '+': 'plus', # Used in amounts
            '#': 'num',  # Used in references
            '%': 'percent',
            '@': 'at',
            '&': 'and'
        }

        self.logger.info("Enhanced TextPreprocessor initialized")

    def _clean_text(self, text):
        """
        Clean text by handling special characters and normalizing.

        Args:
            text: Input text string

        Returns:
            Cleaned text
        """
        if not text or not isinstance(text, str):
            return ""

        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text)

        # Convert to lowercase
        text = text.lower()

        # Replace special financial characters
        for char, replacement in self.special_financial_chars.items():
            text = text.replace(char, f' {replacement} ')

        # Remove other special characters but preserve spaces
        text = re.sub(r'[^\w\s]', ' ', text)

        # Remove extra whitespace
        return re.sub(r'\s+', ' ', text).strip()

    def _normalize_account_numbers(self, text):
        """
        Replace account numbers with a standard token.

        Args:
            text: Input text

        Returns:
            Text with account numbers normalized
        """
        return self.account_pattern.sub('account_number', text)

    def _normalize_amount_with_currency(self, text):
        """
        Replace amounts with currency with standard tokens.

        Args:
            text: Input text

        Returns:
            Text with amounts normalized
        """
        return self.amount_pattern.sub('amount_currency', text)

    def _extract_and_normalize_references(self, text):
        """
        Extract references and standardize them.

        Args:
            text: Input text

        Returns:
            Text with references normalized
        """
        # Extract invoice references
        text = self.invoice_pattern.sub('invoice_reference', text)

        # Extract other references
        return self.reference_pattern.sub('reference_number', text)

    def _expand_abbreviations(self, text):
        """
        Expand common financial abbreviations.

        Args:
            text: Input text

        Returns:
            Text with abbreviations expanded
        """
        for abbr, expansion in self.abbreviations.items():
            # Match abbreviation as whole word
            text = re.sub(r'\b' + re.escape(abbr) + r'\b', expansion, text)

        return text

    def _normalize_currencies(self, text):
        """
        Normalize currency codes to a standard token.

        Args:
            text: Input text

        Returns:
            Text with currency codes normalized
        """
        for code in self.currency_codes:
            text = re.sub(r'\b' + code.lower() + r'\b', 'currency', text)

        return text

    @lru_cache(maxsize=PROD_SETTINGS['cache_size'])
    def preprocess(self, text):
        """
        Preprocess text through multiple cleaning and normalization steps.
        Uses caching for production performance.

        Args:
            text: Input text string

        Returns:
            Preprocessed text
        """
        if not text or not isinstance(text, str):
            return ""

        # Apply cleaning steps
        text = self._clean_text(text)

        # Expand abbreviations
        text = self._expand_abbreviations(text)

        # Apply financial-specific normalization
        text = self._normalize_account_numbers(text)
        text = self._normalize_amount_with_currency(text)
        text = self._extract_and_normalize_references(text)
        text = self._normalize_currencies(text)

        # Replace numbers with standard token but keep them
        text = re.sub(r'\b\d+\b', 'number', text)

        # Tokenize
        tokens = word_tokenize(text)

        # Remove stopwords but preserve financial terms
        tokens = [token for token in tokens if token not in self.financial_stopwords]

        # Lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens]

        # Rejoin into text
        processed_text = ' '.join(tokens)

        # Remove extra whitespace
        processed_text = re.sub(r'\s+', ' ', processed_text).strip()

        return processed_text

    def extract_keywords(self, text, top_n=5):
        """
        Extract key financial terms from text.

        Args:
            text: Input text
            top_n: Number of top keywords to extract

        Returns:
            List of keywords
        """
        processed = self.preprocess(text)
        tokens = word_tokenize(processed)

        # Count term frequency
        term_freq = {}
        for token in tokens:
            if token in self.keep_terms:
                term_freq[token] = term_freq.get(token, 0) + 1

        # Sort by frequency
        sorted_terms = sorted(term_freq.items(), key=lambda x: x[1], reverse=True)

        # Return top N terms
        return [term for term, freq in sorted_terms[:top_n]]

    def normalize_narration(self, narration):
        """
        Specifically normalize an MT message narration field.
        Handles special formatting in MT messages.

        Args:
            narration: MT message narration text

        Returns:
            Normalized narration
        """
        if not narration:
            return ""

        # Replace slash-prefixed lines with spaces (common in MT messages)
        narration = re.sub(r'/\s*', ' ', narration)

        # Remove line continuations in MT messages
        narration = re.sub(r'-\s*$', ' ', narration, flags=re.MULTILINE)

        # Replace newlines with spaces
        narration = narration.replace('\n', ' ')

        # Replace multiple spaces with single space
        narration = re.sub(r'\s+', ' ', narration)

        # Basic preprocessing
        return self.preprocess(narration)

    def detect_payment_type(self, text):
        """
        Attempt to detect the type of payment from narration text.

        Args:
            text: Narration text

        Returns:
            Detected payment type or None
        """
        text = text.lower()

        if re.search(r'\bsalary\b|\bpayroll\b|\bwage(s)?\b', text):
            return 'SALA'
        elif re.search(r'\bdividend\b|\bdistribution\b', text):
            return 'DIVD'
        elif re.search(r'\binvoice\b|\bpayment\s+for\s+goods\b|\bpurchase\b', text):
            return 'TRAD'
        elif re.search(r'\bconsulting\b|\bservice(s)?\b|\bfee(s)?\b', text):
            return 'CONS'
        elif re.search(r'\btax(es)?\b|\bvat\b|\bincome\s+tax\b', text):
            return 'TAXS'
        elif re.search(r'\bloan\b|\bcredit\b|\brepayment\b', text):
            return 'LOAN'
        elif re.search(r'\bintra[-\s]company\b|\bic\s+transfer\b', text):
            return 'INTC'
        elif re.search(r'\brent(al)?\b|\blease\b', text):
            return 'RENT'
        # Add education-specific pattern
        elif re.search(r'\beducation\b|\btuition\b|\bschool\s+fee(s)?\b|\buniversity\b|\bcollege\b|\bsemester\b|\bterm\b|\bcourse\b|\bdegree\b|\bacademic\b|\bstudent\b', text):
            return 'EDUC'

        return None