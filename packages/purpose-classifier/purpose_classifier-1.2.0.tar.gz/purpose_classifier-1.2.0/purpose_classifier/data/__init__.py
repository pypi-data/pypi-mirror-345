"""
Data files for the purpose-classifier package.

This package contains JSON files with purpose codes, category purpose codes,
and sample messages for testing.
"""

import os
import json

# Get the path to the data directory
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

def get_data_path(filename):
    """
    Get the full path to a data file.
    
    Args:
        filename: Name of the data file
        
    Returns:
        Full path to the data file
    """
    return os.path.join(DATA_DIR, filename)

def load_json_data(filename):
    """
    Load JSON data from a file in the data directory.
    
    Args:
        filename: Name of the JSON file
        
    Returns:
        Parsed JSON data
    """
    file_path = get_data_path(filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise IOError(f"Error loading {filename}: {str(e)}")

# Convenience functions for loading specific data files
def load_purpose_codes():
    """Load purpose codes from purpose_codes.json"""
    return load_json_data('purpose_codes.json')

def load_category_purpose_codes():
    """Load category purpose codes from category_purpose_codes.json"""
    return load_json_data('category_purpose_codes.json')

def load_iso20022_purpose_codes():
    """Load ISO20022 purpose codes from iso20022_purpose_codes.json"""
    return load_json_data('iso20022_purpose_codes.json')

def load_sample_messages():
    """Load sample messages from sample_messages.json"""
    return load_json_data('sample_messages.json')
