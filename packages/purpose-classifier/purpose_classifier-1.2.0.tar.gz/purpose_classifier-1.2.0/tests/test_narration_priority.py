#!/usr/bin/env python
"""
Test script for verifying that narration content is prioritized over message type.

This script tests that the system correctly prioritizes narration content over
message type when selecting enhancers and detecting message types.
"""

import os
import sys
import logging
import unittest

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purpose_classifier.domain_enhancers.enhancer_manager import EnhancerManager
from purpose_classifier.domain_enhancers.context_aware_enhancer_semantic import ContextAwareEnhancer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestNarrationPriority(unittest.TestCase):
    """Test cases for verifying narration priority over message type."""

    def setUp(self):
        """Set up the test environment."""
        self.enhancer_manager = EnhancerManager()
        self.context_enhancer = ContextAwareEnhancer()
        
    def test_message_type_detection_from_narration(self):
        """Test that message types are correctly detected from narration."""
        # Test MT103 detection from narration
        narration = "MT103 payment for salary"
        detected_type = self.context_enhancer.detect_message_type(narration)
        self.assertEqual(detected_type, 'MT103')
        
        # Test MT202 detection from narration
        narration = "MT202 interbank transfer"
        detected_type = self.context_enhancer.detect_message_type(narration)
        self.assertEqual(detected_type, 'MT202')
        
        # Test MT202COV detection from narration
        narration = "MT202COV cover payment for underlying transaction"
        detected_type = self.context_enhancer.detect_message_type(narration)
        self.assertEqual(detected_type, 'MT202COV')
        
        # Test semantic detection of MT103 from narration
        narration = "Customer credit transfer for salary payment"
        detected_type = self.context_enhancer.detect_message_type(narration)
        self.assertEqual(detected_type, 'MT103')
        
        # Test semantic detection of MT202 from narration
        narration = "Financial institution transfer between banks"
        detected_type = self.context_enhancer.detect_message_type(narration)
        self.assertEqual(detected_type, 'MT202')
        
        # Test semantic detection of cover payment from narration
        narration = "Cover payment for underlying customer transaction"
        detected_type = self.context_enhancer.detect_message_type(narration)
        self.assertEqual(detected_type, 'MT202COV')
        
    def test_narration_priority_in_enhancer_selection(self):
        """Test that narration content is prioritized over message type in enhancer selection."""
        # Test that dividend enhancer is selected based on narration even with MT103 message type
        narration = "Dividend payment to shareholders"
        message_type = "MT103"
        enhancers = self.enhancer_manager.select_enhancers_by_context(narration, message_type)
        self.assertIn('dividend', enhancers)
        
        # Test that loan enhancer is selected based on narration even with MT202 message type
        narration = "Loan repayment installment"
        message_type = "MT202"
        enhancers = self.enhancer_manager.select_enhancers_by_context(narration, message_type)
        self.assertIn('loan', enhancers)
        
        # Test that securities enhancer is selected based on narration even with MT103 message type
        narration = "Securities settlement for bond purchase"
        message_type = "MT103"
        enhancers = self.enhancer_manager.select_enhancers_by_context(narration, message_type)
        self.assertIn('securities', enhancers)
        
        # Test that MT103 enhancer is selected based on narration even without message type
        narration = "MT103 payment for salary"
        enhancers = self.enhancer_manager.select_enhancers_by_context(narration)
        self.assertIn('mt103', enhancers)
        self.assertIn('message_type', enhancers)
        
        # Test that cover payment enhancer is selected based on narration even without message type
        narration = "MT202COV cover payment for underlying transaction"
        enhancers = self.enhancer_manager.select_enhancers_by_context(narration)
        self.assertIn('cover_payment', enhancers)
        self.assertIn('message_type', enhancers)
        
    def test_narration_priority_in_context_aware_enhancer(self):
        """Test that narration content is prioritized in the context-aware enhancer."""
        # Test that narration overrides message type for salary payments
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Salary payment to employee"
        message_type = "MT202"  # MT202 would normally not suggest SALA
        enhanced = self.context_enhancer.enhance_classification(result, narration, message_type)
        self.assertEqual(enhanced['purpose_code'], 'SALA')
        self.assertGreater(enhanced['confidence'], 0.9)
        
        # Test that narration overrides message type for interbank transfers
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "Interbank transfer between correspondent banks"
        message_type = "MT103"  # MT103 would normally not suggest INTC
        enhanced = self.context_enhancer.enhance_classification(result, narration, message_type)
        self.assertEqual(enhanced['purpose_code'], 'INTC')
        self.assertGreater(enhanced['confidence'], 0.9)
        
        # Test that narration-detected message type is used even when different message type is provided
        result = {'purpose_code': 'OTHR', 'confidence': 0.5}
        narration = "MT103 salary payment to employee"
        message_type = "MT202"  # Provided message type conflicts with narration
        enhanced = self.context_enhancer.enhance_classification(result, narration, message_type)
        self.assertEqual(enhanced['purpose_code'], 'SALA')
        self.assertGreater(enhanced['confidence'], 0.9)
        self.assertTrue(enhanced.get('narration_detected_message_type', False))

if __name__ == '__main__':
    unittest.main()
