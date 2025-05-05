"""
Path helper module for the purpose-classifier package.

This module provides functions to locate data files and models,
with fallbacks to handle both package installation and development environments.
"""

import os
import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def get_package_root():
    """
    Get the root directory of the purpose_classifier package.
    
    Returns:
        Path to the package root directory
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_project_root():
    """
    Get the root directory of the project (one level up from the package).
    
    Returns:
        Path to the project root directory
    """
    return os.path.dirname(get_package_root())

def find_file(filename, search_paths):
    """
    Find a file in a list of search paths.
    
    Args:
        filename: Name of the file to find
        search_paths: List of paths to search
        
    Returns:
        Full path to the file if found, None otherwise
    """
    for path in search_paths:
        file_path = os.path.join(path, filename)
        if os.path.exists(file_path):
            return file_path
    return None

def get_data_file_path(filename):
    """
    Get the path to a data file, searching in package and project data directories.
    
    Args:
        filename: Name of the data file
        
    Returns:
        Full path to the data file
    """
    # Search paths in order of preference
    search_paths = [
        os.path.join(get_package_root(), 'data'),  # Package data directory
        os.path.join(get_project_root(), 'data'),  # Project data directory
    ]
    
    file_path = find_file(filename, search_paths)
    if file_path:
        return file_path
    
    # If not found, log a warning and return the package data path anyway
    logger.warning(f"Data file {filename} not found in search paths: {search_paths}")
    return os.path.join(get_package_root(), 'data', filename)

def get_model_file_path(filename):
    """
    Get the path to a model file, searching in package and project model directories.
    
    Args:
        filename: Name of the model file
        
    Returns:
        Full path to the model file
    """
    # Search paths in order of preference
    search_paths = [
        os.path.join(get_package_root(), 'models'),  # Package models directory
        os.path.join(get_project_root(), 'models'),  # Project models directory
    ]
    
    file_path = find_file(filename, search_paths)
    if file_path:
        return file_path
    
    # If not found, log a warning and return the package models path anyway
    logger.warning(f"Model file {filename} not found in search paths: {search_paths}")
    return os.path.join(get_project_root(), 'models', filename)
