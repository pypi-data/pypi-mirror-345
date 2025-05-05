"""
Test script for running tests with debug logging.

This script runs the tests with debug logging enabled.
"""

import os
import sys
import logging
import unittest

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_logging(level=logging.DEBUG):
    """Set up logging configuration."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    # Set specific loggers to DEBUG level
    logging.getLogger('purpose_classifier.semantic_pattern_matcher').setLevel(level)
    logging.getLogger('purpose_classifier.domain_enhancers').setLevel(level)

if __name__ == '__main__':
    # Set up logging
    setup_logging()
    
    # Run the tests
    from tests.test_swift_messages import TestSwiftMessages
    
    # Create a test suite with just the MT202COV test
    suite = unittest.TestSuite()
    suite.addTest(TestSwiftMessages('test_mt202cov_messages'))
    
    # Run the test suite
    unittest.TextTestRunner().run(suite)
