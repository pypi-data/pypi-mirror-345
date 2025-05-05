"""
Metrics utilities for evaluating purpose code classifier performance.

This module provides functions for calculating and visualizing performance metrics
for the purpose code classifier, including accuracy, precision, recall, and F1-score.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from collections import Counter

def calculate_metrics(results):
    """
    Calculate performance metrics for classification results.

    Args:
        results: List of dictionaries with 'expected' and 'predicted' keys

    Returns:
        dict: Performance metrics
    """
    # Extract expected and predicted labels
    y_true = [r['expected'] for r in results]
    y_pred = [r['predicted'] for r in results]

    # Calculate metrics
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)

    # Calculate per-class metrics
    class_report = classification_report(y_true, y_pred, output_dict=True)

    # Calculate confusion matrix
    cm = confusion_matrix(y_true, y_pred)

    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'class_report': class_report,
        'confusion_matrix': cm
    }

def plot_confusion_matrix(cm, classes, title='Confusion Matrix', output_path=None):
    """
    Plot confusion matrix as a heatmap.

    Args:
        cm: Confusion matrix
        classes: List of class names
        title: Plot title
        output_path: Optional path to save the plot
    """
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=classes, yticklabels=classes)
    plt.title(title)
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
        plt.close()
    else:
        plt.show()

def plot_error_distribution(results, output_path=None):
    """
    Plot distribution of errors by purpose code.

    Args:
        results: List of dictionaries with 'expected' and 'predicted' keys
        output_path: Optional path to save the plot
    """
    # Filter for errors
    errors = [r for r in results if r['expected'] != r['predicted']]

    # Count errors by expected class
    error_counts = Counter([e['expected'] for e in errors])

    # Sort by error count
    sorted_codes = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
    codes = [code for code, _ in sorted_codes]
    counts = [count for _, count in sorted_codes]

    # Plot
    plt.figure(figsize=(12, 6))
    sns.barplot(x=codes, y=counts)
    plt.title('Error Distribution by Purpose Code')
    plt.xlabel('Purpose Code')
    plt.ylabel('Error Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
        plt.close()
    else:
        plt.show()

def plot_confidence_distribution(results, bins=10, output_path=None):
    """
    Plot distribution of confidence scores for correct and incorrect predictions.

    Args:
        results: List of dictionaries with 'expected', 'predicted', and 'confidence' keys
        bins: Number of bins for histogram
        output_path: Optional path to save the plot
    """
    # Separate confidence scores for correct and incorrect predictions
    correct = [r['confidence'] for r in results if r['expected'] == r['predicted']]
    incorrect = [r['confidence'] for r in results if r['expected'] != r['predicted']]

    plt.figure(figsize=(10, 6))
    plt.hist(correct, bins=bins, alpha=0.5, label='Correct Predictions')
    plt.hist(incorrect, bins=bins, alpha=0.5, label='Incorrect Predictions')
    plt.title('Confidence Score Distribution')
    plt.xlabel('Confidence Score')
    plt.ylabel('Count')
    plt.legend()
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
        plt.close()
    else:
        plt.show()

def plot_top_errors(results, top_n=10, output_path=None):
    """
    Plot the most common error patterns.

    Args:
        results: List of dictionaries with 'expected' and 'predicted' keys
        top_n: Number of top error patterns to show
        output_path: Optional path to save the plot
    """
    # Filter for errors
    errors = [r for r in results if r['expected'] != r['predicted']]

    # Count error patterns
    error_patterns = Counter([(e['expected'], e['predicted']) for e in errors])

    # Get top N error patterns
    top_patterns = error_patterns.most_common(top_n)
    
    # Format labels
    labels = [f"{true} → {pred}" for (true, pred), _ in top_patterns]
    counts = [count for _, count in top_patterns]

    # Plot
    plt.figure(figsize=(12, 6))
    sns.barplot(x=counts, y=labels)
    plt.title(f'Top {top_n} Error Patterns')
    plt.xlabel('Count')
    plt.ylabel('Error Pattern (True → Predicted)')
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
        plt.close()
    else:
        plt.show()
