"""
Models directory for the purpose-classifier package.

This directory contains model metadata and information about how to download
the actual model files, which are too large to include in the package.
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Get the path to the models directory
MODELS_DIR = os.path.dirname(os.path.abspath(__file__))

# Model information
MODEL_INFO = {
    'combined_model.pkl': {
        'description': 'Main purpose classifier model',
        'size': '~250MB',
        'url': 'https://github.com/solchos/purpose-classifier-models/releases/download/v1.2.0/combined_model.pkl',
        'required': True
    },
    'word_embeddings.pkl': {
        'description': 'Word embeddings for semantic pattern matching',
        'size': '~120MB',
        'url': 'https://github.com/solchos/purpose-classifier-models/releases/download/v1.2.0/word_embeddings.pkl',
        'required': True
    }
}

def get_model_path(model_name):
    """
    Get the path to a model file.
    
    Args:
        model_name: Name of the model file
        
    Returns:
        Path to the model file
    """
    # First check in the package models directory
    package_path = os.path.join(MODELS_DIR, model_name)
    if os.path.exists(package_path):
        return package_path
    
    # Then check in the project models directory
    project_path = os.path.join(os.path.dirname(os.path.dirname(MODELS_DIR)), 'models', model_name)
    if os.path.exists(project_path):
        return project_path
    
    # If not found, return the project path anyway
    return project_path

def get_model_info():
    """
    Get information about available models.
    
    Returns:
        Dictionary with model information
    """
    return MODEL_INFO

def check_models_exist():
    """
    Check if required model files exist.
    
    Returns:
        Dictionary with model names as keys and boolean values indicating existence
    """
    result = {}
    for model_name, info in MODEL_INFO.items():
        model_path = get_model_path(model_name)
        result[model_name] = os.path.exists(model_path)
    return result
