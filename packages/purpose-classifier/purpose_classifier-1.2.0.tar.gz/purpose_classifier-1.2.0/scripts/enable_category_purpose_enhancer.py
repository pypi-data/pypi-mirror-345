#!/usr/bin/env python3
"""
Script to enable the category purpose domain enhancer in the model.
This script updates the model configuration to enable the category purpose domain enhancer.
"""

import os
import sys
import logging
from datetime import datetime

# Import the classifier
from purpose_classifier.classifier import PurposeClassifier
from purpose_classifier.config.settings import MODEL_PATH, setup_logging, get_environment

def main():
    """
    Main function to enable the category purpose domain enhancer
    """
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description='Enable the category purpose domain enhancer')

    parser.add_argument('--model', type=str, default=MODEL_PATH,
                        help=f'Path to the model file to update (default: {MODEL_PATH})')

    args = parser.parse_args()

    # Setup environment and logging
    env = get_environment()
    logger = setup_logging(env)
    logger.info(f"Starting category purpose domain enhancer enablement in {env} environment")

    # Load the model
    logger.info(f"Loading model from {args.model}")
    classifier = PurposeClassifier(
        environment=env,
        use_category_purpose_enhancer=True
    )

    # Load the model
    classifier.load(custom_path=args.model)

    # Save the model with the category purpose domain enhancer enabled
    logger.info(f"Saving model with category purpose domain enhancer enabled to {args.model}")
    classifier.save(custom_path=args.model)

    logger.info("Category purpose domain enhancer enabled successfully")

    # Print model information
    logger.info(f"Model version: {classifier.model_version}")
    logger.info(f"Category purpose enhancer: {classifier.use_category_purpose_enhancer}")
    logger.info(f"Auto category purpose enhance: {classifier.auto_category_purpose_enhance}")

    # Test the model with sample data
    logger.info("Testing model with sample data")
    test_examples = [
        "CREDIT CARD PAYMENT FOR JANUARY 2024 ACCT-12345",
        "DEBIT CARD PAYMENT VISA ENDING 1234",
        "EPAYMENT FOR ONLINE PURCHASE REF-EP-12345",
        "FEE COLLECTION FOR ADMINISTRATIVE MONTHLY",
        "PAYMENT FOR PURCHASE OF ELECTRONICS REF-PO-12345",
        "GOVERNMENT INSURANCE PAYMENT FOR QUARTERLY POL-12345",
        "IRREVOCABLE CREDIT CARD PAYMENT REF-ICC-12345",
        "IRREVOCABLE DEBIT CARD PAYMENT REF-IDC-12345",
        "CARD BULK CLEARING BATCH PROCESSING"
    ]

    expected_categories = [
        "CCRD",  # Credit Card Payment
        "DCRD",  # Debit Card Payment
        "EPAY",  # ePayment
        "FCOL",  # Fee Collection
        "GDDS",  # Purchase Sale of Goods
        "GOVI",  # Government Insurance
        "ICCP",  # Irrevocable Credit Card Payment
        "IDCP",  # Irrevocable Debit Card Payment
        "CBLK"   # Card Bulk Clearing
    ]

    for i, example in enumerate(test_examples):
        result = classifier.predict(example)
        logger.info(f"Test example: {example}")
        logger.info(f"Prediction: {result['category_purpose_code']} with confidence {result.get('category_confidence', 0):.4f}")
        logger.info(f"Expected: {expected_categories[i]}")
        logger.info(f"Category score: {result.get('category_score', 'N/A')}")
        logger.info(f"Category keywords: {result.get('category_keywords', 'N/A')}")
        logger.info(f"Enhancement applied: {result.get('enhancement_applied', 'N/A')}")
        logger.info("---")

    return 0

if __name__ == "__main__":
    sys.exit(main())
