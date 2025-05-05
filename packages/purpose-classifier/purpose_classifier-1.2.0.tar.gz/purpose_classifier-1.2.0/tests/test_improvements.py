#!/usr/bin/env python
"""
Test the improvements made to the purpose code classifier.

This script tests the improvements made to the purpose code classifier:
1. Education classification accuracy
2. Top predictions diversity
3. Processing time optimization
"""

import os
import sys
import time
import pandas as pd
import argparse
import logging
from datetime import datetime

# Add parent directory to path to import from purpose_classifier
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_education_classification(classifier):
    """
    Test education classification accuracy.
    
    Args:
        classifier: Initialized classifier
        
    Returns:
        dict: Test results
    """
    logger.info("Testing education classification accuracy...")
    
    # Test cases for education-related narrations
    education_test_cases = [
        "TUITION FEE PAYMENT FOR SPRING 2025 - UNIVERSITY OF TECHNOLOGY",
        "PAYMENT FOR UNIVERSITY TUITION - FALL SEMESTER",
        "SCHOOL FEES FOR JOHN SMITH - INTERNATIONAL SCHOOL - ACADEMIC YEAR 2025",
        "EDUCATION EXPENSES - TECHNICAL COLLEGE - SPRING 2025",
        "PAYMENT OF TUITION FOR SUMMER 2025 - BUSINESS SCHOOL",
        "UNIVERSITY PAYMENT - STUDENT ID 12345 - FALL 2025",
        "COLLEGE TUITION - SEMESTER 1 - 2025",
        "ACADEMIC FEE PAYMENT - GRADUATE SCHOOL - SPRING 2025",
        "COURSE FEE PAYMENT - INTRODUCTION TO PROGRAMMING - ONLINE UNIVERSITY",
        "STUDENT HOUSING PAYMENT - STATE UNIVERSITY - FALL 2025"
    ]
    
    # Process each test case
    results = []
    for narration in education_test_cases:
        start_time = time.time()
        prediction = classifier.predict(narration)
        processing_time = time.time() - start_time
        
        results.append({
            'narration': narration,
            'purpose_code': prediction['purpose_code'],
            'confidence': prediction['confidence'],
            'category_purpose_code': prediction.get('category_purpose_code', 'N/A'),
            'category_confidence': prediction.get('category_confidence', 0.0),
            'processing_time': processing_time,
            'education_score': prediction.get('education_score', 0.0),
            'top_predictions': prediction.get('top_predictions', [])
        })
    
    # Calculate statistics
    df = pd.DataFrame(results)
    educ_accuracy = (df['purpose_code'] == 'EDUC').mean()
    fcol_accuracy = (df['category_purpose_code'] == 'FCOL').mean()
    avg_confidence = df['confidence'].mean()
    avg_processing_time = df['processing_time'].mean()
    
    logger.info(f"Education classification accuracy: {educ_accuracy:.2f}")
    logger.info(f"FCOL category mapping accuracy: {fcol_accuracy:.2f}")
    logger.info(f"Average confidence: {avg_confidence:.2f}")
    logger.info(f"Average processing time: {avg_processing_time:.4f} seconds")
    
    return {
        'education_test_cases': len(education_test_cases),
        'educ_accuracy': educ_accuracy,
        'fcol_accuracy': fcol_accuracy,
        'avg_confidence': avg_confidence,
        'avg_processing_time': avg_processing_time,
        'results': results
    }

def test_top_predictions_diversity(classifier):
    """
    Test top predictions diversity.
    
    Args:
        classifier: Initialized classifier
        
    Returns:
        dict: Test results
    """
    logger.info("Testing top predictions diversity...")
    
    # Test cases with potentially ambiguous classifications
    ambiguous_test_cases = [
        "PAYMENT FOR CONSULTING SERVICES AND EDUCATIONAL MATERIALS",
        "INVOICE PAYMENT FOR SOFTWARE DEVELOPMENT AND TRAINING",
        "PAYMENT FOR OFFICE SUPPLIES AND TEXTBOOKS",
        "BUSINESS EXPENSES FOR CONFERENCE AND WORKSHOP",
        "PAYMENT FOR MARKETING SERVICES AND RESEARCH",
        "INVOICE FOR EQUIPMENT MAINTENANCE AND TECHNICAL SUPPORT",
        "PAYMENT FOR LEGAL SERVICES AND REGULATORY COMPLIANCE",
        "INVOICE FOR TRANSPORTATION AND LOGISTICS SERVICES",
        "PAYMENT FOR INSURANCE PREMIUM AND RISK ASSESSMENT",
        "INVOICE FOR CONSTRUCTION SERVICES AND MATERIALS"
    ]
    
    # Process each test case
    results = []
    for narration in ambiguous_test_cases:
        prediction = classifier.predict(narration)
        
        # Calculate diversity metrics
        top_predictions = prediction.get('top_predictions', [])
        if len(top_predictions) >= 2:
            top_confidence = top_predictions[0][1]
            second_confidence = top_predictions[1][1]
            confidence_gap = top_confidence - second_confidence
        else:
            confidence_gap = 1.0  # Maximum gap if only one prediction
        
        results.append({
            'narration': narration,
            'purpose_code': prediction['purpose_code'],
            'confidence': prediction['confidence'],
            'top_predictions': top_predictions,
            'num_predictions': len(top_predictions),
            'confidence_gap': confidence_gap
        })
    
    # Calculate statistics
    df = pd.DataFrame(results)
    avg_num_predictions = df['num_predictions'].mean()
    avg_confidence_gap = df['confidence_gap'].mean()
    
    logger.info(f"Average number of top predictions: {avg_num_predictions:.2f}")
    logger.info(f"Average confidence gap between top 2 predictions: {avg_confidence_gap:.4f}")
    
    return {
        'ambiguous_test_cases': len(ambiguous_test_cases),
        'avg_num_predictions': avg_num_predictions,
        'avg_confidence_gap': avg_confidence_gap,
        'results': results
    }

def test_processing_time(classifier):
    """
    Test processing time optimization.
    
    Args:
        classifier: Initialized classifier
        
    Returns:
        dict: Test results
    """
    logger.info("Testing processing time optimization...")
    
    # Generate a mix of test cases
    test_cases = [
        # High confidence cases (should use fast path)
        "SALARY PAYMENT FOR APRIL 2025",
        "DIVIDEND PAYMENT FOR Q1 2025",
        "LOAN REPAYMENT - ACCOUNT 12345",
        "INSURANCE PREMIUM - POLICY 67890",
        "TAX PAYMENT - INCOME TAX - Q1 2025",
        
        # Medium confidence cases
        "PAYMENT FOR CONSULTING SERVICES",
        "INVOICE FOR OFFICE SUPPLIES",
        "PAYMENT FOR SOFTWARE LICENSE",
        "RENT PAYMENT FOR OFFICE SPACE",
        "UTILITY BILL PAYMENT",
        
        # Low confidence cases (should apply fallback rules)
        "PAYMENT FOR MISCELLANEOUS EXPENSES",
        "GENERAL INVOICE PAYMENT",
        "BUSINESS TRANSACTION",
        "PAYMENT REFERENCE 12345",
        "TRANSFER OF FUNDS"
    ]
    
    # Process each test case multiple times to measure average performance
    num_iterations = 5
    results = []
    
    for narration in test_cases:
        processing_times = []
        
        # Warm-up run (not counted)
        _ = classifier.predict(narration)
        
        # Timed runs
        for _ in range(num_iterations):
            start_time = time.time()
            prediction = classifier.predict(narration)
            processing_time = time.time() - start_time
            processing_times.append(processing_time)
        
        # Calculate average processing time
        avg_processing_time = sum(processing_times) / num_iterations
        
        results.append({
            'narration': narration,
            'purpose_code': prediction['purpose_code'],
            'confidence': prediction['confidence'],
            'avg_processing_time': avg_processing_time,
            'enhancement_applied': prediction.get('enhancement_applied', 'N/A')
        })
    
    # Calculate statistics
    df = pd.DataFrame(results)
    overall_avg_time = df['avg_processing_time'].mean()
    
    # Group by enhancement type
    if 'enhancement_applied' in df.columns:
        enhancement_times = df.groupby('enhancement_applied')['avg_processing_time'].mean()
        for enhancement, avg_time in enhancement_times.items():
            logger.info(f"Average processing time for {enhancement}: {avg_time:.4f} seconds")
    
    logger.info(f"Overall average processing time: {overall_avg_time:.4f} seconds")
    
    return {
        'test_cases': len(test_cases),
        'num_iterations': num_iterations,
        'overall_avg_time': overall_avg_time,
        'results': results
    }

def main():
    """Main function to test improvements"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test improvements to the purpose code classifier')
    
    parser.add_argument('--model', type=str, default='models/combined_model.pkl',
                        help='Path to the model file')
    
    parser.add_argument('--output', type=str, default='improvement_test_results.csv',
                        help='Path to save the test results')
    
    parser.add_argument('--test', type=str, choices=['education', 'diversity', 'performance', 'all'],
                        default='all', help='Which test to run')
    
    args = parser.parse_args()
    
    # Initialize the classifier
    logger.info(f"Loading model from {args.model}")
    classifier = LightGBMPurposeClassifier(model_path=args.model)
    
    # Run the requested tests
    results = {}
    
    if args.test in ['education', 'all']:
        education_results = test_education_classification(classifier)
        results['education'] = education_results
    
    if args.test in ['diversity', 'all']:
        diversity_results = test_top_predictions_diversity(classifier)
        results['diversity'] = diversity_results
    
    if args.test in ['performance', 'all']:
        performance_results = test_processing_time(classifier)
        results['performance'] = performance_results
    
    # Save detailed results to CSV
    if 'education' in results:
        pd.DataFrame(results['education']['results']).to_csv(f"education_{args.output}", index=False)
        logger.info(f"Education test results saved to education_{args.output}")
    
    if 'diversity' in results:
        pd.DataFrame(results['diversity']['results']).to_csv(f"diversity_{args.output}", index=False)
        logger.info(f"Diversity test results saved to diversity_{args.output}")
    
    if 'performance' in results:
        pd.DataFrame(results['performance']['results']).to_csv(f"performance_{args.output}", index=False)
        logger.info(f"Performance test results saved to performance_{args.output}")
    
    # Print summary
    logger.info("\nTest Summary:")
    
    if 'education' in results:
        logger.info(f"Education Classification:")
        logger.info(f"  EDUC Accuracy: {results['education']['educ_accuracy']:.2f}")
        logger.info(f"  FCOL Mapping Accuracy: {results['education']['fcol_accuracy']:.2f}")
    
    if 'diversity' in results:
        logger.info(f"Top Predictions Diversity:")
        logger.info(f"  Avg. Number of Predictions: {results['diversity']['avg_num_predictions']:.2f}")
        logger.info(f"  Avg. Confidence Gap: {results['diversity']['avg_confidence_gap']:.4f}")
    
    if 'performance' in results:
        logger.info(f"Processing Time:")
        logger.info(f"  Avg. Processing Time: {results['performance']['overall_avg_time']:.4f} seconds")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
