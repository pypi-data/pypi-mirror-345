#!/usr/bin/env python
"""
Script for evaluating purpose code enhancers.

This script evaluates enhancers using cross-validation and generates
performance metrics and visualizations.
"""

import os
import sys
import argparse
import logging
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Add the parent directory to the path so we can import the purpose_classifier package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
from tests.test_semantic_enhancers import create_test_cases_for_problematic_codes

# Import enhancers
from purpose_classifier.domain_enhancers.education_enhancer import EducationDomainEnhancer
from purpose_classifier.domain_enhancers.tech_enhancer import TechDomainEnhancer
from purpose_classifier.domain_enhancers.services_enhancer import ServicesDomainEnhancer
from purpose_classifier.domain_enhancers.trade_enhancer import TradeDomainEnhancer
from purpose_classifier.domain_enhancers.transportation_enhancer import TransportationDomainEnhancer
from purpose_classifier.domain_enhancers.financial_services_enhancer import FinancialServicesDomainEnhancer
from purpose_classifier.domain_enhancers.category_purpose_enhancer import CategoryPurposeDomainEnhancer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhancer_evaluation.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Evaluate purpose code enhancers')
    
    parser.add_argument('--enhancer', type=str, choices=[
        'education', 'tech', 'services', 'trade', 'transportation',
        'financial_services', 'category_purpose', 'all'
    ], default='all', help='Enhancer to evaluate')
    
    parser.add_argument('--cross-validate', action='store_true',
                        help='Perform cross-validation')
    
    parser.add_argument('--folds', type=int, default=5,
                        help='Number of folds for cross-validation')
    
    parser.add_argument('--output-dir', type=str, default='enhancer_evaluation',
                        help='Directory to save evaluation results')
    
    return parser.parse_args()

def get_enhancer_class(enhancer_name):
    """Get enhancer class by name."""
    enhancer_classes = {
        'education': EducationDomainEnhancer,
        'tech': TechDomainEnhancer,
        'services': ServicesDomainEnhancer,
        'trade': TradeDomainEnhancer,
        'transportation': TransportationDomainEnhancer,
        'financial_services': FinancialServicesDomainEnhancer,
        'category_purpose': CategoryPurposeDomainEnhancer
    }
    
    return enhancer_classes.get(enhancer_name)

def get_enhancer_instance(enhancer_name):
    """Get enhancer instance by name."""
    enhancer_class = get_enhancer_class(enhancer_name)
    if enhancer_class:
        return enhancer_class()
    return None

def evaluate_single_enhancer(enhancer_name, test_cases, cross_validate=False, folds=5, output_dir=None):
    """Evaluate a single enhancer."""
    logger.info(f"Evaluating enhancer: {enhancer_name}")
    
    # Get enhancer class and instance
    enhancer_class = get_enhancer_class(enhancer_name)
    enhancer = get_enhancer_instance(enhancer_name)
    
    if not enhancer:
        logger.error(f"Enhancer not found: {enhancer_name}")
        return None
    
    # Create output directory
    if output_dir:
        enhancer_dir = os.path.join(output_dir, enhancer_name)
        os.makedirs(enhancer_dir, exist_ok=True)
    
    # Evaluate with cross-validation if requested
    if cross_validate:
        logger.info(f"Performing {folds}-fold cross-validation")
        metrics = evaluate_enhancer_with_cross_validation(enhancer_class, test_cases, k=folds)
        
        # Print cross-validation metrics
        logger.info(f"Cross-validation metrics for {enhancer_name}:")
        logger.info(f"Accuracy: {metrics['accuracy']:.4f} ± {metrics['accuracy_std']:.4f}")
        logger.info(f"Precision: {metrics['precision']:.4f} ± {metrics['precision_std']:.4f}")
        logger.info(f"Recall: {metrics['recall']:.4f} ± {metrics['recall_std']:.4f}")
        logger.info(f"F1 Score: {metrics['f1']:.4f} ± {metrics['f1_std']:.4f}")
        
        # Save cross-validation metrics
        if output_dir:
            metrics_df = pd.DataFrame({
                'Metric': ['Accuracy', 'Precision', 'Recall', 'F1 Score'],
                'Value': [metrics['accuracy'], metrics['precision'], metrics['recall'], metrics['f1']],
                'Std Dev': [metrics['accuracy_std'], metrics['precision_std'], metrics['recall_std'], metrics['f1_std']]
            })
            metrics_df.to_csv(os.path.join(enhancer_dir, 'cross_validation_metrics.csv'), index=False)
    
    # Evaluate on all test cases
    logger.info(f"Evaluating on all test cases")
    metrics = evaluate_enhancer(enhancer, test_cases)
    
    # Print metrics
    logger.info(f"Evaluation metrics for {enhancer_name}:")
    logger.info(f"Accuracy: {metrics['accuracy']:.4f}")
    logger.info(f"Precision: {metrics['precision']:.4f}")
    logger.info(f"Recall: {metrics['recall']:.4f}")
    logger.info(f"F1 Score: {metrics['f1']:.4f}")
    
    # Analyze errors
    error_analysis = analyze_errors(metrics['detailed_results'])
    
    # Print error analysis
    logger.info(f"Error analysis for {enhancer_name}:")
    logger.info(f"Error count: {error_analysis['error_count']}")
    logger.info(f"Error rate: {error_analysis['error_rate']:.4f}")
    logger.info("Top error patterns:")
    for (expected, predicted), count in error_analysis['top_error_patterns']:
        logger.info(f"  {expected} -> {predicted}: {count}")
    
    # Generate visualizations if output directory is provided
    if output_dir:
        logger.info(f"Generating visualizations for {enhancer_name}")
        
        # Get unique classes
        classes = sorted(list(set([r['expected'] for r in metrics['detailed_results']])))
        
        # Plot confusion matrix
        plot_confusion_matrix(
            metrics['confusion_matrix'],
            classes,
            title=f'Confusion Matrix - {enhancer_name}',
            output_path=os.path.join(enhancer_dir, 'confusion_matrix.png')
        )
        
        # Plot error distribution
        plot_error_distribution(
            metrics['detailed_results'],
            output_path=os.path.join(enhancer_dir, 'error_distribution.png')
        )
        
        # Plot confidence distribution
        plot_confidence_distribution(
            metrics['detailed_results'],
            output_path=os.path.join(enhancer_dir, 'confidence_distribution.png')
        )
        
        # Plot top errors
        plot_top_errors(
            metrics['detailed_results'],
            output_path=os.path.join(enhancer_dir, 'top_errors.png')
        )
        
        # Save detailed results
        results_df = pd.DataFrame(metrics['detailed_results'])
        results_df.to_csv(os.path.join(enhancer_dir, 'detailed_results.csv'), index=False)
        
        # Save metrics
        metrics_df = pd.DataFrame({
            'Metric': ['Accuracy', 'Precision', 'Recall', 'F1 Score'],
            'Value': [metrics['accuracy'], metrics['precision'], metrics['recall'], metrics['f1']]
        })
        metrics_df.to_csv(os.path.join(enhancer_dir, 'metrics.csv'), index=False)
        
        # Save error analysis
        error_df = pd.DataFrame({
            'Metric': ['Error Count', 'Error Rate'],
            'Value': [error_analysis['error_count'], error_analysis['error_rate']]
        })
        error_df.to_csv(os.path.join(enhancer_dir, 'error_analysis.csv'), index=False)
        
        # Save top error patterns
        pattern_df = pd.DataFrame(error_analysis['top_error_patterns'], columns=['Pattern', 'Count'])
        pattern_df['Expected'] = pattern_df['Pattern'].apply(lambda x: x[0])
        pattern_df['Predicted'] = pattern_df['Pattern'].apply(lambda x: x[1])
        pattern_df = pattern_df[['Expected', 'Predicted', 'Count']]
        pattern_df.to_csv(os.path.join(enhancer_dir, 'error_patterns.csv'), index=False)
    
    return metrics

def compare_all_enhancers(test_cases, cross_validate=False, folds=5, output_dir=None):
    """Compare all enhancers."""
    logger.info("Comparing all enhancers")
    
    # Get all enhancer names
    enhancer_names = [
        'education', 'tech', 'services', 'trade', 'transportation',
        'financial_services', 'category_purpose'
    ]
    
    # Create enhancer instances
    enhancers = {name: get_enhancer_instance(name) for name in enhancer_names}
    
    # Filter out None values
    enhancers = {name: enhancer for name, enhancer in enhancers.items() if enhancer}
    
    # Compare enhancers
    comparison = compare_enhancers(enhancers, test_cases)
    
    # Print comparison
    logger.info("Enhancer comparison:")
    logger.info("Accuracy:")
    for name, accuracy in comparison['accuracy'].items():
        logger.info(f"  {name}: {accuracy:.4f}")
    
    logger.info("Precision:")
    for name, precision in comparison['precision'].items():
        logger.info(f"  {name}: {precision:.4f}")
    
    logger.info("Recall:")
    for name, recall in comparison['recall'].items():
        logger.info(f"  {name}: {recall:.4f}")
    
    logger.info("F1 Score:")
    for name, f1 in comparison['f1'].items():
        logger.info(f"  {name}: {f1:.4f}")
    
    # Generate comparison visualizations if output directory is provided
    if output_dir:
        logger.info("Generating comparison visualizations")
        
        # Create comparison directory
        comparison_dir = os.path.join(output_dir, 'comparison')
        os.makedirs(comparison_dir, exist_ok=True)
        
        # Create comparison dataframe
        comparison_df = pd.DataFrame({
            'Enhancer': list(comparison['accuracy'].keys()),
            'Accuracy': list(comparison['accuracy'].values()),
            'Precision': list(comparison['precision'].values()),
            'Recall': list(comparison['recall'].values()),
            'F1 Score': list(comparison['f1'].values())
        })
        
        # Save comparison dataframe
        comparison_df.to_csv(os.path.join(comparison_dir, 'comparison.csv'), index=False)
        
        # Plot comparison bar charts
        plt.figure(figsize=(12, 8))
        comparison_df.plot(x='Enhancer', y=['Accuracy', 'Precision', 'Recall', 'F1 Score'], kind='bar')
        plt.title('Enhancer Comparison')
        plt.ylabel('Score')
        plt.ylim(0, 1)
        plt.tight_layout()
        plt.savefig(os.path.join(comparison_dir, 'comparison.png'))
        plt.close()
        
        # Plot individual metric comparisons
        for metric in ['Accuracy', 'Precision', 'Recall', 'F1 Score']:
            plt.figure(figsize=(10, 6))
            comparison_df.plot(x='Enhancer', y=metric, kind='bar', color='skyblue')
            plt.title(f'{metric} Comparison')
            plt.ylabel(metric)
            plt.ylim(0, 1)
            plt.tight_layout()
            plt.savefig(os.path.join(comparison_dir, f'{metric.lower()}_comparison.png'))
            plt.close()
    
    return comparison

def main():
    """Main function."""
    # Parse command line arguments
    args = parse_args()
    
    # Create output directory
    if args.output_dir:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = f"{args.output_dir}_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = None
    
    # Create test cases
    logger.info("Creating test cases for problematic purpose codes")
    test_cases = create_test_cases_for_problematic_codes()
    logger.info(f"Created {len(test_cases)} test cases")
    
    # Evaluate enhancers
    if args.enhancer == 'all':
        # Compare all enhancers
        compare_all_enhancers(test_cases, args.cross_validate, args.folds, output_dir)
    else:
        # Evaluate single enhancer
        evaluate_single_enhancer(args.enhancer, test_cases, args.cross_validate, args.folds, output_dir)
    
    logger.info("Evaluation completed")
    if output_dir:
        logger.info(f"Results saved to {output_dir}")

if __name__ == '__main__':
    main()
