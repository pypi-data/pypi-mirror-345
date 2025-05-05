"""
Message parser for SWIFT MT messages.
Provides extraction functions for different message types and validation utilities.
"""

import re
import logging
from typing import Dict, Tuple, Optional, List, Any

# Setup logging
logger = logging.getLogger(__name__)

# MT message field patterns
MT_FIELD_PATTERNS = {
    'MT103': {
        'narration': r':70:(.*?)(?=:\d{2}[A-Z]:|$)',
        'sender': r':50[AFK]?:(.*?)(?=:\d{2}[A-Z]:|$)',
        'receiver': r':59[AF]?:(.*?)(?=:\d{2}[A-Z]:|$)',
        'amount': r':32A:.*?([0-9,\.]+)',
        'currency': r':32A:.*?([A-Z]{3})',
        'reference': r':20:(.*?)(?=:\d{2}[A-Z]:|$)',
        'purpose': r':26T:(.*?)(?=:\d{2}[A-Z]:|$)',
        'category_purpose': r':77B:.*?CATT/(.*?)(?=/|$)',
    },
    'MT202': {
        'narration': r':72:(.*?)(?=:\d{2}[A-Z]:|$)',
        'sender': r':52[AD]?:(.*?)(?=:\d{2}[A-Z]:|$)',
        'receiver': r':58[AD]?:(.*?)(?=:\d{2}[A-Z]:|$)',
        'amount': r':32A:.*?([0-9,\.]+)',
        'currency': r':32A:.*?([A-Z]{3})',
        'reference': r':20:(.*?)(?=:\d{2}[A-Z]:|$)',
        'related_reference': r':21:(.*?)(?=:\d{2}[A-Z]:|$)',
    },
    'MT202COV': {
        'narration': [
            r':72:(.*?)(?=:\d{2}[A-Z]:|$)',
            r'B]:.*?:72:(.*?)(?=:\d{2}[A-Z]:|$)'
        ],
        'sender': r':52[AD]?:(.*?)(?=:\d{2}[A-Z]:|$)',
        'receiver': r':58[AD]?:(.*?)(?=:\d{2}[A-Z]:|$)',
        'amount': r':32A:.*?([0-9,\.]+)',
        'currency': r':32A:.*?([A-Z]{3})',
        'reference': r':20:(.*?)(?=:\d{2}[A-Z]:|$)',
        'related_reference': r':21:(.*?)(?=:\d{2}[A-Z]:|$)',
    },
    'MT205': {
        'narration': r':72:(.*?)(?=:\d{2}[A-Z]:|$)',
        'sender': r':52[AD]?:(.*?)(?=:\d{2}[A-Z]:|$)',
        'receiver': r':58[AD]?:(.*?)(?=:\d{2}[A-Z]:|$)',
        'amount': r':32A:.*?([0-9,\.]+)',
        'currency': r':32A:.*?([A-Z]{3})',
        'reference': r':20:(.*?)(?=:\d{2}[A-Z]:|$)',
    },
    'MT205COV': {
        'narration': [
            r':72:(.*?)(?=:\d{2}[A-Z]:|$)',
            r'B]:.*?:72:(.*?)(?=:\d{2}[A-Z]:|$)'
        ],
        'sender': r':52[AD]?:(.*?)(?=:\d{2}[A-Z]:|$)',
        'receiver': r':58[AD]?:(.*?)(?=:\d{2}[A-Z]:|$)',
        'amount': r':32A:.*?([0-9,\.]+)',
        'currency': r':32A:.*?([A-Z]{3})',
        'reference': r':20:(.*?)(?=:\d{2}[A-Z]:|$)',
    }
}

# Message format identifiers
MESSAGE_TYPE_IDENTIFIERS = {
    'MT103': [
        (r'\{2:I103', 'header'),
        (r'(:\d{2}:.*){5,}.*:70:', 'fields'),  # Contains multiple fields and narration
        (r':20:.*:32A:.*:50[AFK]?:.*:59[AF]?:', 'sequence'),  # Contains required fields in typical order
    ],
    'MT202': [
        (r'\{2:I202(?!COV)', 'header'),
        (r':20:.*:21:.*:32A:', 'sequence'),
    ],
    'MT202COV': [
        (r'\{2:I202COV', 'header'),
        (r'COV-', 'reference'),
        (r'B]:.*:50[AFK]?:.*:59[AF]?:', 'sequence B'),
    ],
    'MT205': [
        (r'\{2:I205(?!COV)', 'header'),
        (r':20:.*:32A:.*:57[AD]?:', 'sequence'),
    ],
    'MT205COV': [
        (r'\{2:I205COV', 'header'),
        (r'B]:.*:50[AFK]?:.*:59[AF]?:', 'sequence B'),
    ]
}

# Field validation rules
FIELD_VALIDATION = {
    'MT103': {
        'required': [':20:', ':32A:', ':50', ':59'],
        'conditional': [':70:'],
        'length_limits': {
            '20': 16,
            '70': 140,
        }
    },
    'MT202': {
        'required': [':20:', ':21:', ':32A:'],
        'conditional': [':72:'],
        'length_limits': {
            '20': 16,
            '21': 16,
            '72': 210,
        }
    },
    'MT202COV': {
        'required': [':20:', ':21:', ':32A:'],
        'conditional': [':72:'],
        'length_limits': {
            '20': 16,
            '21': 16,
            '72': 210,
        }
    },
    'MT205': {
        'required': [':20:', ':32A:'],
        'conditional': [':72:'],
        'length_limits': {
            '20': 16,
            '72': 210,
        }
    },
    'MT205COV': {
        'required': [':20:', ':32A:'],
        'conditional': [':72:'],
        'length_limits': {
            '20': 16,
            '72': 210,
        }
    }
}

# Common encoding errors and corrections
ENCODING_FIXES = {
    '\xa0': ' ',  # Non-breaking space
    '\u2019': "'",  # Right single quotation mark
    '\u2018': "'",  # Left single quotation mark
    '\u201c': '"',  # Left double quotation mark
    '\u201d': '"',  # Right double quotation mark
    '\u2013': '-',  # En dash
    '\u2014': '-',  # Em dash
    '\u00a9': '(c)',  # Copyright
    '\u00ae': '(R)',  # Registered trademark
}

def detect_message_type(message: str) -> Optional[str]:
    """
    Detect the message type from a SWIFT message.
    
    Args:
        message: The full SWIFT message
        
    Returns:
        The detected message type or None if not detected
    """
    if not message:
        return None
    
    # Check for header identifiers first - these are most reliable
    if "{2:I103" in message:
        return "MT103"
    elif "{2:I202COV" in message:
        return "MT202COV"
    elif "{2:I202" in message:
        return "MT202" 
    elif "{2:I205COV" in message:
        return "MT205COV"
    elif "{2:I205" in message:
        return "MT205"
        
    # For messages with modified or missing headers, check each message type against its identifiers
    for msg_type, identifiers in MESSAGE_TYPE_IDENTIFIERS.items():
        match_count = 0
        for pattern, _ in identifiers:
            if re.search(pattern, message, re.DOTALL):
                match_count += 1
        
        # If we have enough matches, we've found our message type
        if match_count >= 1:
            return msg_type
    
    # Fallback to basic field detection
    if ':20:' in message and ':32A:' in message:
        if ':50' in message and ':59' in message:
            return 'MT103'
        elif ':21:' in message:
            # Additional check for MT202COV
            if 'COV' in message or '{B]:' in message or ':{B]:' in message:
                return 'MT202COV'
            return 'MT202'
        elif ':53' in message or ':57' in message:
            if 'COV' in message or '{B]:' in message or ':{B]:' in message:
                return 'MT205COV'
            return 'MT205'
    
    return None

def validate_message_format(message: str, message_type: str) -> Tuple[bool, Optional[str]]:
    """
    Validate if the message format is correct for the given message type.
    
    Args:
        message: The full SWIFT message
        message_type: The expected message type
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if message_type not in FIELD_VALIDATION:
        return False, f"Unknown message type: {message_type}"
    
    validation = FIELD_VALIDATION[message_type]
    
    # Check required fields
    for field in validation['required']:
        if field not in message:
            return False, f"Missing required field {field} for {message_type}"
    
    # Check field length limits
    for field, max_length in validation['length_limits'].items():
        field_tag = f':{field}:'
        if field_tag in message:
            pattern = rf'{field_tag}(.*?)(?=:\d{{2}}[A-Z]?:|$)'
            matches = re.search(pattern, message, re.DOTALL)
            if matches and len(matches.group(1).strip()) > max_length:
                return False, f"Field {field} exceeds maximum length of {max_length}"
    
    return True, None

def fix_encoding_issues(text: str) -> str:
    """
    Fix common encoding issues in messages.
    
    Args:
        text: The text to fix
        
    Returns:
        Cleaned text with encoding issues fixed
    """
    if not text:
        return text
        
    for char, replacement in ENCODING_FIXES.items():
        text = text.replace(char, replacement)
    
    # Remove null bytes and other control characters
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    
    return text

def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in extracted text.
    
    Args:
        text: The text to normalize
        
    Returns:
        Text with normalized whitespace
    """
    if not text:
        return text
        
    # Replace newlines and tabs with spaces, then normalize multiple spaces
    text = text.replace('\n', ' ').replace('\t', ' ')
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()

def extract_field_value(message: str, field_pattern: str) -> Optional[str]:
    """
    Extract a field value using the provided pattern.
    
    Args:
        message: The message to extract from
        field_pattern: The regex pattern to use
        
    Returns:
        Extracted and cleaned field value or None
    """
    if not message or not field_pattern:
        return None
        
    matches = re.search(field_pattern, message, re.DOTALL)
    if matches:
        value = matches.group(1).strip()
        value = fix_encoding_issues(value)
        value = normalize_whitespace(value)
        return value
    
    return None

def try_multiple_patterns(message: str, patterns: List[str]) -> Optional[str]:
    """
    Try multiple patterns to extract a field value.
    
    Args:
        message: The message to extract from
        patterns: List of regex patterns to try
        
    Returns:
        First successful extraction or None
    """
    for pattern in patterns:
        value = extract_field_value(message, pattern)
        if value:
            return value
    
    return None

def extract_narration_from_mt103(message: str) -> Optional[str]:
    """
    Extract narration from MT103 message (field 70).
    
    Args:
        message: MT103 message text
        
    Returns:
        Extracted narration or None if not found
    """
    pattern = MT_FIELD_PATTERNS['MT103']['narration']
    narration_text = extract_field_value(message, pattern)
    
    if narration_text:
        # Ensure proper spacing in multiline narrations
        lines = narration_text.split('\n')
        formatted_narration = ' '.join(line.strip() for line in lines)
        # Fix any double spaces that might have been introduced
        formatted_narration = re.sub(r' {2,}', ' ', formatted_narration)
        return formatted_narration
    
    # If no narration found, try to get information from remitter (50) or beneficiary (59)
    if not narration_text:
        logger.debug("No narration found in field 70, trying alternative fields")
        alternative_fields = ['sender', 'receiver', 'purpose']
        for field in alternative_fields:
            if field in MT_FIELD_PATTERNS['MT103']:
                alt_narration = extract_field_value(message, MT_FIELD_PATTERNS['MT103'][field])
                if alt_narration:
                    logger.debug(f"Using {field} as alternative narration")
                    return f"[{field.upper()}] {alt_narration}"
    
    return narration_text

def extract_narration_from_mt202(message: str) -> Optional[str]:
    """
    Extract narration from MT202 message (field 72).
    
    Args:
        message: MT202 message text
        
    Returns:
        Extracted narration or None if not found
    """
    pattern = MT_FIELD_PATTERNS['MT202']['narration']
    narration_text = extract_field_value(message, pattern)
    
    if narration_text:
        # Ensure proper spacing in multiline narrations
        lines = narration_text.split('\n')
        formatted_narration = ' '.join(line.strip() for line in lines)
        # Fix any double spaces that might have been introduced
        formatted_narration = re.sub(r' {2,}', ' ', formatted_narration)
        return formatted_narration
    
    # If no narration found, try related reference
    if not narration_text:
        ref_pattern = MT_FIELD_PATTERNS['MT202']['related_reference']
        ref = extract_field_value(message, ref_pattern)
        if ref:
            return f"[REF] {ref}"
    
    return narration_text

def extract_narration_from_mt202cov(message: str) -> Optional[str]:
    """
    Extract narration from MT202COV message (field 72).
    
    Args:
        message: MT202COV message text
        
    Returns:
        Extracted narration or None if not found
    """
    patterns = MT_FIELD_PATTERNS['MT202COV']['narration']
    narration_text = try_multiple_patterns(message, patterns)
    
    if narration_text:
        # Ensure proper spacing in multiline narrations
        lines = narration_text.split('\n')
        formatted_narration = ' '.join(line.strip() for line in lines)
        # Fix any double spaces that might have been introduced
        formatted_narration = re.sub(r' {2,}', ' ', formatted_narration)
        return formatted_narration
    
    # If no narration found in field 72, use underlying payment details
    if not narration_text:
        # Try to get info from sequence B which contains underlying customer details
        sequence_b_match = re.search(r'B]:(.*?)(?=\{|$)', message, re.DOTALL)
        if sequence_b_match:
            seq_b = sequence_b_match.group(1)
            # Try to get sender or receiver from sequence B
            sender_pattern = r':50[AFK]?:(.*?)(?=:\d{2}[A-Z]?:|$)'
            receiver_pattern = r':59[AF]?:(.*?)(?=:\d{2}[A-Z]?:|$)'
            
            sender = extract_field_value(seq_b, sender_pattern)
            receiver = extract_field_value(seq_b, receiver_pattern)
            
            parts = []
            if sender:
                parts.append(f"FROM: {sender}")
            if receiver:
                parts.append(f"TO: {receiver}")
                
            if parts:
                return " | ".join(parts)
    
    return narration_text

def extract_narration_from_mt205(message: str) -> Optional[str]:
    """
    Extract narration from MT205 message (field 72).
    
    Args:
        message: MT205 message text
        
    Returns:
        Extracted narration or None if not found
    """
    pattern = MT_FIELD_PATTERNS['MT205']['narration']
    narration_text = extract_field_value(message, pattern)
    
    if narration_text:
        # Ensure proper spacing in multiline narrations
        lines = narration_text.split('\n')
        formatted_narration = ' '.join(line.strip() for line in lines)
        # Fix any double spaces that might have been introduced
        formatted_narration = re.sub(r' {2,}', ' ', formatted_narration)
        return formatted_narration
    
    return narration_text

def extract_narration_from_mt205cov(message: str) -> Optional[str]:
    """
    Extract narration from MT205COV message (field 72).
    
    Args:
        message: MT205COV message text
        
    Returns:
        Extracted narration or None if not found
    """
    patterns = MT_FIELD_PATTERNS['MT205COV']['narration']
    narration_text = try_multiple_patterns(message, patterns)
    
    if narration_text:
        # Ensure proper spacing in multiline narrations
        lines = narration_text.split('\n')
        formatted_narration = ' '.join(line.strip() for line in lines)
        # Fix any double spaces that might have been introduced
        formatted_narration = re.sub(r' {2,}', ' ', formatted_narration)
        return formatted_narration
    
    # Similar to MT202COV, try sequence B if narration not found
    if not narration_text:
        sequence_b_match = re.search(r'B]:(.*?)(?=\{|$)', message, re.DOTALL)
        if sequence_b_match:
            seq_b = sequence_b_match.group(1)
            sender_pattern = r':50[AFK]?:(.*?)(?=:\d{2}[A-Z]?:|$)'
            receiver_pattern = r':59[AF]?:(.*?)(?=:\d{2}[A-Z]?:|$)'
            
            sender = extract_field_value(seq_b, sender_pattern)
            receiver = extract_field_value(seq_b, receiver_pattern)
            
            parts = []
            if sender:
                parts.append(f"FROM: {sender}")
            if receiver:
                parts.append(f"TO: {receiver}")
                
            if parts:
                return " | ".join(parts)
    
    return narration_text

def extract_narration(message: str, message_type: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract narration from any message type.
    
    Args:
        message: The full message
        message_type: Known message type or None to auto-detect
        
    Returns:
        Tuple of (narration, message_type)
    """
    if not message:
        return None, None
        
    # Clean up message
    message = fix_encoding_issues(message)
    
    # Detect message type if not provided
    if not message_type:
        message_type = detect_message_type(message)
        if not message_type:
            logger.warning("Could not determine message type, trying MT103 extraction")
            message_type = 'MT103'  # Default to most common type
    
    # Extract based on message type
    extraction_functions = {
        'MT103': extract_narration_from_mt103,
        'MT202': extract_narration_from_mt202,
        'MT202COV': extract_narration_from_mt202cov,
        'MT205': extract_narration_from_mt205,
        'MT205COV': extract_narration_from_mt205cov,
    }
    
    extract_func = extraction_functions.get(message_type)
    if extract_func:
        narration = extract_func(message)
        if narration:
            return narration, message_type
    
    # Fallback to all extractors if specific one failed
    logger.debug(f"Extraction failed for {message_type}, trying all extractors")
    for mt_type, extractor in extraction_functions.items():
        if mt_type != message_type:  # Skip the one we already tried
            narration = extractor(message)
            if narration:
                logger.info(f"Found narration using {mt_type} extractor")
                return narration, mt_type
    
    return None, message_type

def extract_all_fields(message: str, message_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract all available fields from the message.
    
    Args:
        message: The full message
        message_type: Known message type or None to auto-detect
        
    Returns:
        Dictionary of extracted fields
    """
    if not message:
        return {}
        
    # Clean up message
    message = fix_encoding_issues(message)
    
    # Detect message type if not provided
    if not message_type:
        message_type = detect_message_type(message)
        if not message_type:
            logger.warning("Could not determine message type")
            return {}
    
    result = {'message_type': message_type}
    
    # Extract fields based on patterns for the message type
    patterns = MT_FIELD_PATTERNS.get(message_type, {})
    for field, pattern in patterns.items():
        if isinstance(pattern, list):
            value = try_multiple_patterns(message, pattern)
        else:
            value = extract_field_value(message, pattern)
        
        if value:
            result[field] = value
    
    return result

def handle_malformed_message(message: str) -> Dict[str, Any]:
    """
    Attempt to extract information from a malformed message.
    
    Args:
        message: The potentially malformed message
        
    Returns:
        Dictionary with best-effort extracted information
    """
    # Try to detect any recognizable patterns
    result = {'is_malformed': True}
    
    # Look for any field tags
    field_matches = re.findall(r':(\d{2}[A-Z]?):(.*?)(?=:\d{2}[A-Z]?:|$)', message, re.DOTALL)
    if field_matches:
        for field_tag, content in field_matches:
            clean_content = normalize_whitespace(fix_encoding_issues(content))
            result[f'field_{field_tag}'] = clean_content
    
    # Try to find anything that might be a narration (free text)
    narration_candidates = [
        r':70:(.*?)(?=:\d{2}[A-Z]?:|$)',
        r':72:(.*?)(?=:\d{2}[A-Z]?:|$)',
        r'INFO:(.*?)(?=\n|$)'
    ]
    
    for pattern in narration_candidates:
        narration = extract_field_value(message, pattern)
        if narration:
            result['possible_narration'] = narration
            break
    
    return result

def extract_purpose_from_message(message: str) -> Optional[str]:
    """
    Extract the purpose code from a message if present in field 26T or in 
    the narration as code pattern.
    
    Args:
        message: The full SWIFT message
        
    Returns:
        The extracted purpose code or None if not found
    """
    # First try to extract from field 26T if present (commonly used for purpose codes)
    purpose_pattern = r':26T:(.*?)(?=:\d{2}[A-Z]?:|$)'
    purpose_match = re.search(purpose_pattern, message, re.DOTALL)
    
    if purpose_match:
        purpose = purpose_match.group(1).strip()
        return purpose
    
    # Then look for category purpose in field 77B (used in some MT103 messages)
    category_pattern = r':77B:.*?CATT/(.*?)(?=/|$)'
    category_match = re.search(category_pattern, message, re.DOTALL)
    
    if category_match:
        category = category_match.group(1).strip()
        return category
    
    # Try to identify purpose codes in the narration
    narration, _ = extract_narration(message)
    if narration:
        # Look for common purpose code patterns in the narration
        code_patterns = [
            r'\b(INTC|TREA|CASH|CORT|DIVI|GOVT|PENS|SALA|SECU|SUPP|TAXS|TRAD|TREA|VATX|WHLD)\b',
            r'PURPOSE(?:\s+CODE)?[:\s]+([A-Z]{4})',
            r'CODE[:\s]+([A-Z]{4})'
        ]
        
        for pattern in code_patterns:
            match = re.search(pattern, narration, re.IGNORECASE)
            if match:
                return match.group(1).upper()
    
    return None 