#!/usr/bin/env python
"""
Script to set the purpose classifier to production logging level.
This will reduce the verbosity of the logs by setting the log level to WARNING.
"""

import os
import sys
import logging

# Add the parent directory to the path so we can import the purpose_classifier package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from purpose_classifier.config.settings import ENV_SETTINGS

def set_production_logging():
    """Set the logging level to WARNING for all environments"""
    # Update the log level in the environment settings
    ENV_SETTINGS['development']['log_level'] = logging.WARNING
    ENV_SETTINGS['test']['log_level'] = logging.WARNING
    ENV_SETTINGS['production']['log_level'] = logging.WARNING
    
    # Configure logging with the new settings
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set the log level for specific loggers
    logging.getLogger('purpose_classifier').setLevel(logging.WARNING)
    logging.getLogger('purpose_classifier.lightgbm_classifier').setLevel(logging.WARNING)
    logging.getLogger('purpose_classifier.domain_enhancers').setLevel(logging.WARNING)
    
    # Reduce verbosity of third-party libraries
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('nltk').setLevel(logging.WARNING)
    logging.getLogger('sklearn').setLevel(logging.WARNING)
    logging.getLogger('tensorflow').setLevel(logging.WARNING)
    
    print("Logging level set to WARNING for all environments")

if __name__ == "__main__":
    set_production_logging()
