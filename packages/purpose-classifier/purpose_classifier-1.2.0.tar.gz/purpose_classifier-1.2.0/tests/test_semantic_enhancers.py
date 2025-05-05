"""
Test suite for semantic enhancers.

This module provides test cases and evaluation functions for semantic enhancers,
focusing on problematic purpose codes.
"""

import os
import sys
import unittest
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Add the parent directory to the path so we can import the purpose_classifier package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from purpose_classifier.semantic_pattern_matcher import SemanticPatternMatcher
from purpose_classifier.utils.evaluation import (
    evaluate_enhancer_with_cross_validation,
    evaluate_enhancer,
    compare_enhancers,
    analyze_errors
)
from purpose_classifier.utils.metrics import (
    calculate_metrics,
    plot_confusion_matrix,
    plot_error_distribution,
    plot_confidence_distribution,
    plot_top_errors
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_test_cases_for_problematic_codes():
    """Generate comprehensive test cases for problematic purpose codes."""
    test_cases = []
    
    # Dividend test cases
    dividend_test_cases = [
        {"narration": "Dividend payment Q2 2023", "expected": "DIVD", "message_type": "MT103"},
        {"narration": "Shareholder dividend final 2023", "expected": "DIVD", "message_type": "MT103"},
        {"narration": "Quarterly dividend distribution", "expected": "DIVD", "message_type": "MT202"},
        {"narration": "Interim dividend payout", "expected": "DIVD", "message_type": "MT202COV"},
        {"narration": "Corporate dividend Q1 2023", "expected": "DIVD", "message_type": "MT205"},
        {"narration": "Distribution of profits to shareholders", "expected": "DIVD", "message_type": "MT103"},
        {"narration": "Annual dividend payment for fiscal year 2023", "expected": "DIVD", "message_type": "MT103"},
        {"narration": "Special dividend distribution", "expected": "DIVD", "message_type": "MT202"},
        {"narration": "Dividend income from investment portfolio", "expected": "DIVD", "message_type": "MT103"},
        {"narration": "Stock dividend payment", "expected": "DIVD", "message_type": "MT103"}
    ]
    test_cases.extend(dividend_test_cases)
    
    # Loan/Loan Repayment test cases
    loan_test_cases = [
        {"narration": "Loan disbursement - Account ID123456", "expected": "LOAN", "message_type": "MT103"},
        {"narration": "New loan facility - REF123456", "expected": "LOAN", "message_type": "MT103"},
        {"narration": "Loan repayment - Account ID123456", "expected": "LOAR", "message_type": "MT103"},
        {"narration": "Monthly loan installment", "expected": "LOAR", "message_type": "MT202"},
        {"narration": "Credit facility drawdown", "expected": "LOAN", "message_type": "MT103"},
        {"narration": "Loan advance for business expansion", "expected": "LOAN", "message_type": "MT103"},
        {"narration": "Mortgage loan disbursement", "expected": "LOAN", "message_type": "MT103"},
        {"narration": "Principal repayment on loan", "expected": "LOAR", "message_type": "MT103"},
        {"narration": "Loan installment payment", "expected": "LOAR", "message_type": "MT103"},
        {"narration": "Final loan repayment", "expected": "LOAR", "message_type": "MT202"}
    ]
    test_cases.extend(loan_test_cases)
    
    # Trade-related test cases
    trade_test_cases = [
        {"narration": "Payment for trade goods - Invoice #12345", "expected": "TRAD", "message_type": "MT103"},
        {"narration": "International trade settlement", "expected": "TRAD", "message_type": "MT103"},
        {"narration": "Trade finance payment", "expected": "TRAD", "message_type": "MT202"},
        {"narration": "Export trade settlement", "expected": "TRAD", "message_type": "MT103"},
        {"narration": "Import payment for goods", "expected": "TRAD", "message_type": "MT103"},
        {"narration": "Trade credit settlement", "expected": "TRAD", "message_type": "MT202"},
        {"narration": "Payment for goods under LC", "expected": "TRAD", "message_type": "MT103"},
        {"narration": "Settlement of trade invoice", "expected": "TRAD", "message_type": "MT103"},
        {"narration": "Trade payment for commodities", "expected": "TRAD", "message_type": "MT103"},
        {"narration": "Cross-border trade settlement", "expected": "TRAD", "message_type": "MT202COV"}
    ]
    test_cases.extend(trade_test_cases)
    
    # Tax-related test cases
    tax_test_cases = [
        {"narration": "VAT payment for Q2 2023", "expected": "VATX", "message_type": "MT103"},
        {"narration": "Corporate tax payment", "expected": "TAXS", "message_type": "MT103"},
        {"narration": "Income tax withholding", "expected": "WHLD", "message_type": "MT103"},
        {"narration": "Quarterly tax payment", "expected": "TAXS", "message_type": "MT103"},
        {"narration": "Value added tax settlement", "expected": "VATX", "message_type": "MT103"},
        {"narration": "Tax withholding on dividend", "expected": "WHLD", "message_type": "MT103"},
        {"narration": "Annual tax payment", "expected": "TAXS", "message_type": "MT103"},
        {"narration": "VAT refund", "expected": "VATX", "message_type": "MT103"},
        {"narration": "Withholding tax on interest", "expected": "WHLD", "message_type": "MT103"},
        {"narration": "Property tax payment", "expected": "TAXS", "message_type": "MT103"}
    ]
    test_cases.extend(tax_test_cases)
    
    # Interest-related test cases
    interest_test_cases = [
        {"narration": "Interest payment on loan", "expected": "INTE", "message_type": "MT103"},
        {"narration": "Monthly interest on deposit", "expected": "INTE", "message_type": "MT103"},
        {"narration": "Bond interest payment", "expected": "INTE", "message_type": "MT202"},
        {"narration": "Interest on credit balance", "expected": "INTE", "message_type": "MT103"},
        {"narration": "Quarterly interest payment", "expected": "INTE", "message_type": "MT103"},
        {"narration": "Interest on savings account", "expected": "INTE", "message_type": "MT103"},
        {"narration": "Interest income from securities", "expected": "INTE", "message_type": "MT202"},
        {"narration": "Accrued interest payment", "expected": "INTE", "message_type": "MT103"},
        {"narration": "Interest on fixed deposit", "expected": "INTE", "message_type": "MT103"},
        {"narration": "Interest on treasury bills", "expected": "INTE", "message_type": "MT202"}
    ]
    test_cases.extend(interest_test_cases)
    
    # Investment-related test cases
    investment_test_cases = [
        {"narration": "Investment in equity shares", "expected": "INVS", "message_type": "MT103"},
        {"narration": "Purchase of bonds", "expected": "INVS", "message_type": "MT202"},
        {"narration": "Mutual fund investment", "expected": "INVS", "message_type": "MT103"},
        {"narration": "Stock purchase", "expected": "INVS", "message_type": "MT103"},
        {"narration": "Investment in securities", "expected": "INVS", "message_type": "MT202"},
        {"narration": "Portfolio investment", "expected": "INVS", "message_type": "MT103"},
        {"narration": "Investment in government bonds", "expected": "INVS", "message_type": "MT202"},
        {"narration": "Equity investment in company", "expected": "INVS", "message_type": "MT103"},
        {"narration": "Investment fund subscription", "expected": "INVS", "message_type": "MT103"},
        {"narration": "Treasury investment", "expected": "INVS", "message_type": "MT202"}
    ]
    test_cases.extend(investment_test_cases)
    
    # Treasury-related test cases
    treasury_test_cases = [
        {"narration": "Treasury operations", "expected": "TREA", "message_type": "MT202"},
        {"narration": "Treasury transfer between accounts", "expected": "TREA", "message_type": "MT202"},
        {"narration": "Treasury management operation", "expected": "TREA", "message_type": "MT202"},
        {"narration": "Intra-company treasury transfer", "expected": "TREA", "message_type": "MT202"},
        {"narration": "Treasury funding operation", "expected": "TREA", "message_type": "MT202"},
        {"narration": "Treasury liquidity management", "expected": "TREA", "message_type": "MT202"},
        {"narration": "Treasury cash pooling", "expected": "TREA", "message_type": "MT202"},
        {"narration": "Treasury position adjustment", "expected": "TREA", "message_type": "MT202"},
        {"narration": "Treasury balance transfer", "expected": "TREA", "message_type": "MT202"},
        {"narration": "Treasury settlement", "expected": "TREA", "message_type": "MT202"}
    ]
    test_cases.extend(treasury_test_cases)
    
    # Card payment test cases
    card_test_cases = [
        {"narration": "Credit card payment", "expected": "CCRD", "message_type": "MT103"},
        {"narration": "Debit card transaction", "expected": "DCRD", "message_type": "MT103"},
        {"narration": "Card payment settlement", "expected": "CCRD", "message_type": "MT103"},
        {"narration": "Credit card bill payment", "expected": "CCRD", "message_type": "MT103"},
        {"narration": "Debit card purchase", "expected": "DCRD", "message_type": "MT103"},
        {"narration": "Card transaction settlement", "expected": "CCRD", "message_type": "MT103"},
        {"narration": "Payment for credit card statement", "expected": "CCRD", "message_type": "MT103"},
        {"narration": "Debit card withdrawal", "expected": "DCRD", "message_type": "MT103"},
        {"narration": "Credit card annual fee", "expected": "CCRD", "message_type": "MT103"},
        {"narration": "Card payment processing", "expected": "CCRD", "message_type": "MT103"}
    ]
    test_cases.extend(card_test_cases)
    
    # Intra-company payment test cases
    intra_company_test_cases = [
        {"narration": "Intra-company payment", "expected": "INTC", "message_type": "MT103"},
        {"narration": "Internal company transfer", "expected": "INTC", "message_type": "MT202"},
        {"narration": "Transfer between subsidiaries", "expected": "INTC", "message_type": "MT103"},
        {"narration": "Intra-group settlement", "expected": "INTC", "message_type": "MT202"},
        {"narration": "Payment to parent company", "expected": "INTC", "message_type": "MT103"},
        {"narration": "Subsidiary funding", "expected": "INTC", "message_type": "MT103"},
        {"narration": "Intra-company loan", "expected": "INTC", "message_type": "MT202"},
        {"narration": "Transfer to affiliated company", "expected": "INTC", "message_type": "MT103"},
        {"narration": "Intra-company service payment", "expected": "INTC", "message_type": "MT103"},
        {"narration": "Group company settlement", "expected": "INTC", "message_type": "MT202"}
    ]
    test_cases.extend(intra_company_test_cases)
    
    return test_cases

class TestSemanticEnhancers(unittest.TestCase):
    """Test cases for semantic enhancers."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test cases
        self.test_cases = create_test_cases_for_problematic_codes()
        
        # Create a mock enhancer for testing
        class MockEnhancer:
            def enhance_classification(self, result, narration, message_type=None):
                # Simple keyword-based enhancement for testing
                narration_lower = narration.lower()
                
                if 'dividend' in narration_lower:
                    return {'purpose_code': 'DIVD', 'confidence': 0.9}
                elif 'loan repayment' in narration_lower or 'installment' in narration_lower:
                    return {'purpose_code': 'LOAR', 'confidence': 0.85}
                elif 'loan' in narration_lower:
                    return {'purpose_code': 'LOAN', 'confidence': 0.8}
                elif 'trade' in narration_lower:
                    return {'purpose_code': 'TRAD', 'confidence': 0.75}
                elif 'vat' in narration_lower:
                    return {'purpose_code': 'VATX', 'confidence': 0.8}
                elif 'tax' in narration_lower:
                    return {'purpose_code': 'TAXS', 'confidence': 0.7}
                elif 'withholding' in narration_lower:
                    return {'purpose_code': 'WHLD', 'confidence': 0.75}
                elif 'interest' in narration_lower:
                    return {'purpose_code': 'INTE', 'confidence': 0.8}
                elif 'investment' in narration_lower or 'stock' in narration_lower:
                    return {'purpose_code': 'INVS', 'confidence': 0.85}
                elif 'treasury' in narration_lower:
                    return {'purpose_code': 'TREA', 'confidence': 0.9}
                elif 'credit card' in narration_lower:
                    return {'purpose_code': 'CCRD', 'confidence': 0.8}
                elif 'debit card' in narration_lower:
                    return {'purpose_code': 'DCRD', 'confidence': 0.8}
                elif 'intra-company' in narration_lower or 'internal' in narration_lower:
                    return {'purpose_code': 'INTC', 'confidence': 0.85}
                else:
                    return result
        
        self.mock_enhancer = MockEnhancer()
    
    def test_evaluate_enhancer(self):
        """Test enhancer evaluation."""
        # Evaluate the mock enhancer
        metrics = evaluate_enhancer(self.mock_enhancer, self.test_cases)
        
        # Check that metrics were calculated
        self.assertIn('accuracy', metrics)
        self.assertIn('precision', metrics)
        self.assertIn('recall', metrics)
        self.assertIn('f1', metrics)
        self.assertIn('detailed_results', metrics)
        
        # Print metrics
        print(f"Accuracy: {metrics['accuracy']:.2f}")
        print(f"Precision: {metrics['precision']:.2f}")
        print(f"Recall: {metrics['recall']:.2f}")
        print(f"F1 Score: {metrics['f1']:.2f}")
    
    def test_analyze_errors(self):
        """Test error analysis."""
        # Evaluate the mock enhancer
        metrics = evaluate_enhancer(self.mock_enhancer, self.test_cases)
        
        # Analyze errors
        error_analysis = analyze_errors(metrics['detailed_results'])
        
        # Check that error analysis was performed
        self.assertIn('error_count', error_analysis)
        self.assertIn('error_rate', error_analysis)
        self.assertIn('errors_by_expected', error_analysis)
        self.assertIn('errors_by_predicted', error_analysis)
        self.assertIn('top_error_patterns', error_analysis)
        
        # Print error analysis
        print(f"Error count: {error_analysis['error_count']}")
        print(f"Error rate: {error_analysis['error_rate']:.2f}")
        print("Top error patterns:")
        for (expected, predicted), count in error_analysis['top_error_patterns']:
            print(f"  {expected} -> {predicted}: {count}")

def main():
    """Run the tests and generate visualizations."""
    # Create test cases
    test_cases = create_test_cases_for_problematic_codes()
    
    # Create a mock enhancer for testing
    class MockEnhancer:
        def enhance_classification(self, result, narration, message_type=None):
            # Simple keyword-based enhancement for testing
            narration_lower = narration.lower()
            
            if 'dividend' in narration_lower:
                return {'purpose_code': 'DIVD', 'confidence': 0.9}
            elif 'loan repayment' in narration_lower or 'installment' in narration_lower:
                return {'purpose_code': 'LOAR', 'confidence': 0.85}
            elif 'loan' in narration_lower:
                return {'purpose_code': 'LOAN', 'confidence': 0.8}
            elif 'trade' in narration_lower:
                return {'purpose_code': 'TRAD', 'confidence': 0.75}
            elif 'vat' in narration_lower:
                return {'purpose_code': 'VATX', 'confidence': 0.8}
            elif 'tax' in narration_lower:
                return {'purpose_code': 'TAXS', 'confidence': 0.7}
            elif 'withholding' in narration_lower:
                return {'purpose_code': 'WHLD', 'confidence': 0.75}
            elif 'interest' in narration_lower:
                return {'purpose_code': 'INTE', 'confidence': 0.8}
            elif 'investment' in narration_lower or 'stock' in narration_lower:
                return {'purpose_code': 'INVS', 'confidence': 0.85}
            elif 'treasury' in narration_lower:
                return {'purpose_code': 'TREA', 'confidence': 0.9}
            elif 'credit card' in narration_lower:
                return {'purpose_code': 'CCRD', 'confidence': 0.8}
            elif 'debit card' in narration_lower:
                return {'purpose_code': 'DCRD', 'confidence': 0.8}
            elif 'intra-company' in narration_lower or 'internal' in narration_lower:
                return {'purpose_code': 'INTC', 'confidence': 0.85}
            else:
                return result
    
    # Create the enhancer
    enhancer = MockEnhancer()
    
    # Evaluate the enhancer
    metrics = evaluate_enhancer(enhancer, test_cases)
    
    # Print metrics
    print("Enhancer Evaluation Metrics:")
    print(f"Accuracy: {metrics['accuracy']:.2f}")
    print(f"Precision: {metrics['precision']:.2f}")
    print(f"Recall: {metrics['recall']:.2f}")
    print(f"F1 Score: {metrics['f1']:.2f}")
    
    # Analyze errors
    error_analysis = analyze_errors(metrics['detailed_results'])
    
    # Print error analysis
    print("\nError Analysis:")
    print(f"Error count: {error_analysis['error_count']}")
    print(f"Error rate: {error_analysis['error_rate']:.2f}")
    print("Top error patterns:")
    for (expected, predicted), count in error_analysis['top_error_patterns']:
        print(f"  {expected} -> {predicted}: {count}")
    
    # Create output directory for visualizations
    os.makedirs('test_results', exist_ok=True)
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    
    # Get unique classes
    classes = sorted(list(set([r['expected'] for r in metrics['detailed_results']])))
    
    # Plot confusion matrix
    plot_confusion_matrix(
        metrics['confusion_matrix'],
        classes,
        title='Confusion Matrix',
        output_path='test_results/confusion_matrix.png'
    )
    
    # Plot error distribution
    plot_error_distribution(
        metrics['detailed_results'],
        output_path='test_results/error_distribution.png'
    )
    
    # Plot confidence distribution
    plot_confidence_distribution(
        metrics['detailed_results'],
        output_path='test_results/confidence_distribution.png'
    )
    
    # Plot top errors
    plot_top_errors(
        metrics['detailed_results'],
        output_path='test_results/top_errors.png'
    )
    
    print("Visualizations saved to 'test_results' directory.")

if __name__ == '__main__':
    main()
