#!/usr/bin/env python
"""
Test script for Phase 6 implementation of the purpose classifier.

This script tests the enhanced manager, optimized embeddings, and adaptive
confidence calibration components of Phase 6.
"""

import os
import sys
import time
import logging
import argparse
import pandas as pd
import numpy as np
from tqdm import tqdm

# Add the parent directory to the path so we can import the purpose_classifier package
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier
from purpose_classifier.domain_enhancers.enhancer_manager import EnhancerManager
from purpose_classifier.domain_enhancers.enhanced_manager import EnhancedManager
from purpose_classifier.optimized_embeddings import word_embeddings
from purpose_classifier.domain_enhancers.adaptive_confidence import AdaptiveConfidenceCalibrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_enhanced_manager():
    """Test the enhanced manager implementation."""
    logger.info("Testing Enhanced Manager...")

    # Initialize regular and enhanced managers
    regular_manager = EnhancerManager()
    enhanced_manager = EnhancedManager()

    # Test narrations
    test_narrations = [
        "Tuition fee payment for university",
        "Salary payment for employee",
        "Purchase of software licenses",
        "Dividend payment to shareholders",
        "Loan repayment for mortgage",
        "Tax payment for VAT",
        "Insurance premium payment",
        "Consulting services fee",
        "Payment for office supplies",
        "Withholding tax payment"
    ]

    # Test both managers
    regular_results = []
    enhanced_results = []

    logger.info("Processing test narrations with regular manager...")
    for narration in test_narrations:
        # Create a base result
        base_result = {
            'purpose_code': 'OTHR',
            'confidence': 0.5,
            'category_purpose_code': 'OTHR',
            'category_confidence': 0.5
        }

        # Apply regular manager
        regular_result = regular_manager.enhance(base_result.copy(), narration)
        regular_results.append(regular_result)

    logger.info("Processing test narrations with enhanced manager...")
    for narration in test_narrations:
        # Create a base result
        base_result = {
            'purpose_code': 'OTHR',
            'confidence': 0.5,
            'category_purpose_code': 'OTHR',
            'category_confidence': 0.5
        }

        # Apply enhanced manager
        enhanced_result = enhanced_manager.enhance(base_result.copy(), narration)
        enhanced_results.append(enhanced_result)

    # Compare results
    logger.info("Comparing results...")
    for i, narration in enumerate(test_narrations):
        regular_code = regular_results[i]['purpose_code']
        enhanced_code = enhanced_results[i]['purpose_code']
        regular_conf = regular_results[i].get('confidence', 0.0)
        enhanced_conf = enhanced_results[i].get('confidence', 0.0)

        logger.info(f"Narration: {narration}")
        logger.info(f"  Regular: {regular_code} ({regular_conf:.2f})")
        logger.info(f"  Enhanced: {enhanced_code} ({enhanced_conf:.2f})")

        if 'enhancer_decisions' in enhanced_results[i]:
            logger.info(f"  Enhanced manager decisions:")
            for decision in enhanced_results[i]['enhancer_decisions']:
                applied = "APPLIED" if decision.get('applied', False) else "NOT APPLIED"
                logger.info(f"    {decision.get('enhancer', 'unknown')}: {decision.get('old_code', 'OTHR')} -> {decision.get('new_code', 'OTHR')} ({decision.get('confidence', 0.0):.2f}) {applied}")

    return True

def test_optimized_embeddings():
    """Test the optimized embeddings implementation."""
    logger.info("Testing Optimized Embeddings...")

    # Ensure embeddings are loaded
    if not word_embeddings.is_loaded:
        word_embeddings.load()

    # Test word pairs
    test_pairs = [
        ("payment", "transfer"),
        ("salary", "wage"),
        ("dividend", "profit"),
        ("loan", "mortgage"),
        ("tax", "levy"),
        ("insurance", "policy"),
        ("consulting", "advisory"),
        ("software", "program"),
        ("office", "workplace"),
        ("withholding", "retention")
    ]

    # Test similarity calculation
    logger.info("Testing similarity calculation...")
    for word1, word2 in test_pairs:
        # Measure time for similarity calculation
        start_time = time.time()
        similarity = word_embeddings.get_similarity(word1, word2)
        elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

        logger.info(f"Similarity between '{word1}' and '{word2}': {similarity:.4f} (took {elapsed_time:.2f} ms)")

    # Test caching
    logger.info("Testing caching...")

    # First call (should be cached from previous test)
    start_time = time.time()
    similarity1 = word_embeddings.get_similarity("payment", "transfer")
    elapsed_time1 = (time.time() - start_time) * 1000  # Convert to ms

    # Second call (should use cache)
    start_time = time.time()
    similarity2 = word_embeddings.get_similarity("payment", "transfer")
    elapsed_time2 = (time.time() - start_time) * 1000  # Convert to ms

    logger.info(f"First call: {similarity1:.4f} (took {elapsed_time1:.2f} ms)")
    logger.info(f"Second call: {similarity2:.4f} (took {elapsed_time2:.2f} ms)")

    # Avoid division by zero
    if elapsed_time2 > 0:
        logger.info(f"Cache speedup: {elapsed_time1 / elapsed_time2:.2f}x")
    else:
        logger.info("Cache speedup: infinite (second call took 0ms)")

    # Get cache stats
    cache_stats = word_embeddings.get_cache_stats()
    logger.info(f"Cache stats: {cache_stats}")

    return True

def test_adaptive_confidence():
    """Test the adaptive confidence calibration implementation."""
    logger.info("Testing Adaptive Confidence Calibration...")

    # Initialize calibrator
    calibrator = AdaptiveConfidenceCalibrator()

    # Test results
    test_results = [
        {'purpose_code': 'EDUC', 'confidence': 0.9, 'enhancer': 'education_enhancer'},
        {'purpose_code': 'SALA', 'confidence': 0.8, 'enhancer': 'salary_enhancer'},
        {'purpose_code': 'SCVE', 'confidence': 0.7, 'enhancer': 'services_enhancer'},
        {'purpose_code': 'DIVD', 'confidence': 0.6, 'enhancer': 'dividend_enhancer'},
        {'purpose_code': 'LOAN', 'confidence': 0.5, 'enhancer': 'loan_enhancer'},
        {'purpose_code': 'TAXS', 'confidence': 0.4, 'enhancer': 'tax_enhancer'},
        {'purpose_code': 'INSU', 'confidence': 0.3, 'enhancer': 'insurance_enhancer'},
        {'purpose_code': 'TRAD', 'confidence': 0.2, 'enhancer': 'trade_enhancer'},
        {'purpose_code': 'GDDS', 'confidence': 0.1, 'enhancer': 'goods_enhancer'},
        {'purpose_code': 'OTHR', 'confidence': 0.05, 'enhancer': 'unknown_enhancer'}
    ]

    # Test calibration
    logger.info("Testing confidence calibration...")
    for result in test_results:
        # Calibrate confidence
        calibrated_result = calibrator.calibrate_confidence(result.copy())

        # Log results
        logger.info(f"Purpose code: {result['purpose_code']}")
        logger.info(f"  Original confidence: {result['confidence']:.2f}")
        logger.info(f"  Calibrated confidence: {calibrated_result['confidence']:.2f}")
        logger.info(f"  Scaling factor: {calibrated_result.get('scaling_factor', 1.0):.2f}")

    # Test performance tracking
    logger.info("Testing performance tracking...")

    # Update performance with some correct and incorrect predictions
    for i, result in enumerate(test_results):
        # Mark even indices as correct, odd indices as incorrect
        was_correct = (i % 2 == 0)
        calibrator.update_performance(result, was_correct)

    # Recalibrate
    logger.info("Testing recalibration...")
    recalibrated = calibrator.recalibrate(min_samples=5)  # Lower threshold for testing

    if recalibrated:
        logger.info("Recalibration successful")

        # Get calibration stats
        stats = calibrator.get_calibration_stats()
        logger.info(f"Calibration stats: {stats}")

        # Test calibration again after recalibration
        logger.info("Testing calibration after recalibration...")
        for result in test_results:
            # Calibrate confidence
            calibrated_result = calibrator.calibrate_confidence(result.copy())

            # Log results
            logger.info(f"Purpose code: {result['purpose_code']}")
            logger.info(f"  Original confidence: {result['confidence']:.2f}")
            logger.info(f"  Calibrated confidence: {calibrated_result['confidence']:.2f}")
            logger.info(f"  Scaling factor: {calibrated_result.get('scaling_factor', 1.0):.2f}")
    else:
        logger.info("Recalibration not performed (not enough samples)")

    return True

def test_full_classifier():
    """Test the full classifier with all Phase 6 components."""
    logger.info("Testing Full Classifier with Phase 6 Components...")

    # Initialize classifier
    classifier = LightGBMPurposeClassifier()

    # Test narrations
    test_narrations = [
        "Tuition fee payment for university",
        "Salary payment for employee",
        "Purchase of software licenses",
        "Dividend payment to shareholders",
        "Loan repayment for mortgage",
        "Tax payment for VAT",
        "Insurance premium payment",
        "Consulting services fee",
        "Payment for office supplies",
        "Withholding tax payment"
    ]

    # Test prediction
    logger.info("Testing prediction...")
    results = []

    for narration in test_narrations:
        # Measure prediction time
        start_time = time.time()
        result = classifier.predict(narration)
        elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

        # Add to results
        result['narration'] = narration
        result['prediction_time_ms'] = elapsed_time
        results.append(result)

    # Log results
    for result in results:
        logger.info(f"Narration: {result['narration']}")
        logger.info(f"  Purpose code: {result['purpose_code']}")
        logger.info(f"  Confidence: {result.get('confidence', 0.0):.2f}")
        logger.info(f"  Category purpose code: {result.get('category_purpose_code', 'OTHR')}")
        logger.info(f"  Prediction time: {result['prediction_time_ms']:.2f} ms")

        # Log enhancer decisions if available
        if 'enhancer_decisions' in result:
            logger.info(f"  Enhancer decisions:")
            for decision in result['enhancer_decisions']:
                applied = "APPLIED" if decision.get('applied', False) else "NOT APPLIED"
                logger.info(f"    {decision.get('enhancer', 'unknown')}: {decision.get('old_code', 'OTHR')} -> {decision.get('new_code', 'OTHR')} ({decision.get('confidence', 0.0):.2f}) {applied}")

    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Test Phase 6 implementation')

    parser.add_argument('--test', type=str, choices=['all', 'enhanced_manager', 'optimized_embeddings', 'adaptive_confidence', 'full_classifier'],
                       default='all', help='Test to run')

    args = parser.parse_args()

    try:
        if args.test == 'all' or args.test == 'enhanced_manager':
            test_enhanced_manager()

        if args.test == 'all' or args.test == 'optimized_embeddings':
            test_optimized_embeddings()

        if args.test == 'all' or args.test == 'adaptive_confidence':
            test_adaptive_confidence()

        if args.test == 'all' or args.test == 'full_classifier':
            test_full_classifier()

        logger.info("All tests completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Error in testing: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
