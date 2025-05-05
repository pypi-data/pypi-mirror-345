"""
Evaluation utilities for purpose code classifier enhancers.

This module provides functions for evaluating enhancers using cross-validation
and other evaluation techniques.
"""

import numpy as np
import pandas as pd
import logging
from sklearn.model_selection import KFold
from purpose_classifier.utils.metrics import calculate_metrics

logger = logging.getLogger(__name__)

def evaluate_enhancer_with_cross_validation(enhancer_class, test_data, k=5):
    """
    Evaluate enhancer performance using k-fold cross-validation.

    Args:
        enhancer_class: The enhancer class to evaluate
        test_data: List of test cases
        k: Number of folds for cross-validation

    Returns:
        dict: Performance metrics
    """
    # Convert test data to numpy array for splitting
    test_data_array = np.array(test_data)
    
    # Initialize k-fold cross-validation
    kf = KFold(n_splits=k, shuffle=True, random_state=42)
    
    # Initialize metrics
    metrics = {
        'accuracy': [],
        'precision': [],
        'recall': [],
        'f1': []
    }
    
    # Perform k-fold cross-validation
    for fold, (train_idx, test_idx) in enumerate(kf.split(test_data_array)):
        logger.info(f"Processing fold {fold+1}/{k}")
        
        # Get train and test data for this fold
        train_data = test_data_array[train_idx].tolist()
        test_fold = test_data_array[test_idx].tolist()
        
        # Initialize enhancer
        enhancer = enhancer_class()
        
        # Train enhancer on training data (if applicable)
        if hasattr(enhancer, 'train'):
            logger.info(f"Training enhancer on {len(train_data)} examples")
            enhancer.train(train_data)
        
        # Test enhancer on test fold
        logger.info(f"Testing enhancer on {len(test_fold)} examples")
        results = []
        for case in test_fold:
            # Create a baseline result with low confidence
            result = {'purpose_code': 'OTHR', 'confidence': 0.3}
            
            # Apply the enhancer
            enhanced_result = enhancer.enhance_classification(
                result, case['narration'], case.get('message_type')
            )
            
            # Record the result
            results.append({
                'expected': case['expected'],
                'predicted': enhanced_result['purpose_code'],
                'confidence': enhanced_result.get('confidence', 0.0)
            })
        
        # Calculate metrics for this fold
        fold_metrics = calculate_metrics(results)
        
        # Store metrics for this fold
        for metric in ['accuracy', 'precision', 'recall', 'f1']:
            metrics[metric].append(fold_metrics[metric])
    
    # Calculate average metrics across folds
    avg_metrics = {metric: np.mean(values) for metric, values in metrics.items()}
    std_metrics = {f"{metric}_std": np.std(values) for metric, values in metrics.items()}
    
    # Combine average and standard deviation metrics
    final_metrics = {**avg_metrics, **std_metrics}
    
    return final_metrics

def evaluate_enhancer(enhancer, test_data):
    """
    Evaluate enhancer performance on test data.

    Args:
        enhancer: Initialized enhancer instance
        test_data: List of test cases

    Returns:
        dict: Performance metrics and detailed results
    """
    logger.info(f"Evaluating enhancer on {len(test_data)} examples")
    
    # Test enhancer on all test data
    results = []
    for case in test_data:
        # Create a baseline result with low confidence
        result = {'purpose_code': 'OTHR', 'confidence': 0.3}
        
        # Apply the enhancer
        enhanced_result = enhancer.enhance_classification(
            result, case['narration'], case.get('message_type')
        )
        
        # Record the result
        results.append({
            'expected': case['expected'],
            'predicted': enhanced_result['purpose_code'],
            'confidence': enhanced_result.get('confidence', 0.0),
            'narration': case['narration'],
            'message_type': case.get('message_type', 'Unknown'),
            'enhancement_applied': enhanced_result.get('enhancement_applied', False),
            'enhancement_reason': enhanced_result.get('reason', 'No enhancement')
        })
    
    # Calculate metrics
    metrics = calculate_metrics(results)
    
    # Add detailed results
    metrics['detailed_results'] = results
    
    return metrics

def compare_enhancers(enhancers, test_data):
    """
    Compare multiple enhancers on the same test data.

    Args:
        enhancers: Dictionary of {name: enhancer_instance}
        test_data: List of test cases

    Returns:
        dict: Comparison results
    """
    logger.info(f"Comparing {len(enhancers)} enhancers on {len(test_data)} examples")
    
    # Evaluate each enhancer
    results = {}
    for name, enhancer in enhancers.items():
        logger.info(f"Evaluating enhancer: {name}")
        results[name] = evaluate_enhancer(enhancer, test_data)
    
    # Create comparison summary
    comparison = {
        'accuracy': {name: results[name]['accuracy'] for name in enhancers},
        'precision': {name: results[name]['precision'] for name in enhancers},
        'recall': {name: results[name]['recall'] for name in enhancers},
        'f1': {name: results[name]['f1'] for name in enhancers}
    }
    
    # Add detailed results
    comparison['detailed_results'] = results
    
    return comparison

def analyze_errors(results):
    """
    Analyze error patterns in classification results.

    Args:
        results: List of dictionaries with 'expected' and 'predicted' keys

    Returns:
        dict: Error analysis results
    """
    # Filter for errors
    errors = [r for r in results if r['expected'] != r['predicted']]
    
    # Count errors by expected class
    errors_by_expected = pd.DataFrame(errors).groupby('expected').size().to_dict()
    
    # Count errors by predicted class
    errors_by_predicted = pd.DataFrame(errors).groupby('predicted').size().to_dict()
    
    # Count error patterns
    error_patterns = pd.DataFrame(errors).groupby(['expected', 'predicted']).size().to_dict()
    
    # Sort error patterns by frequency
    sorted_patterns = sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)
    
    # Calculate error rate
    error_rate = len(errors) / len(results)
    
    return {
        'error_count': len(errors),
        'error_rate': error_rate,
        'errors_by_expected': errors_by_expected,
        'errors_by_predicted': errors_by_predicted,
        'top_error_patterns': sorted_patterns[:10]  # Top 10 error patterns
    }
