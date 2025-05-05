#!/usr/bin/env python3
"""
Enhanced MT message processor that extracts narrations and classifies purpose codes.

This script:
1. Reads MT message files from a specified directory
2. Uses purpose_classifier.utils.message_parser to extract narrations
3. Uses predict.py functionality to determine purpose codes and category purpose codes
4. Saves detailed results to a CSV file
5. Provides comprehensive analysis of results by message type
"""

import os
import sys
import json
import csv
import argparse
import pandas as pd
import time
import logging
from pathlib import Path
from datetime import datetime
from tabulate import tabulate
from collections import defaultdict

# Import classifier and utilities
from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier
from purpose_classifier.utils.message_parser import (
    detect_message_type,
    extract_narration,
    extract_all_fields,
    validate_message_format
)
from purpose_classifier.utils.preprocessor import TextPreprocessor
from purpose_classifier.config.settings import (
    MODEL_PATH,
    setup_logging,
    get_environment,
    PURPOSE_CODES_PATH,
    CATEGORY_PURPOSE_CODES_PATH
)

# Setup logging
logger = setup_logging(get_environment())

def load_purpose_codes():
    """Load purpose codes and category purpose codes from JSON files"""
    purpose_codes = {}
    category_purpose_codes = {}

    try:
        with open(PURPOSE_CODES_PATH, 'r') as f:
            purpose_codes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load purpose codes from {PURPOSE_CODES_PATH}: {str(e)}")

    try:
        with open(CATEGORY_PURPOSE_CODES_PATH, 'r') as f:
            category_purpose_codes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load category purpose codes from {CATEGORY_PURPOSE_CODES_PATH}: {str(e)}")

    return purpose_codes, category_purpose_codes

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Process MT messages and classify purpose codes')

    # Get default messages directory
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    default_messages_dir = os.path.join(base_dir, "MT_messages", "test_messages")

    parser.add_argument('--messages-dir', type=str, default=default_messages_dir,
                        help=f'Directory containing MT message files (default: {default_messages_dir})')

    parser.add_argument('--model', type=str, default=MODEL_PATH,
                        help=f'Path to the purpose classifier model (default: {MODEL_PATH})')

    parser.add_argument('--output', type=str, default='mt_message_results.csv',
                        help='Path to save the results (default: mt_message_results.csv)')

    parser.add_argument('--verbose', action='store_true',
                        help='Show detailed output including enhancer information')

    parser.add_argument('--cache', action='store_true',
                        help='Enable prediction caching for better performance')

    return parser.parse_args()

def read_mt_message(file_path):
    """Read an MT message from a file"""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        return None

def process_mt_message(file_path, classifier, cache_enabled=False, verbose=False):
    """
    Process an MT message file and return prediction results

    Args:
        file_path: Path to the MT message file
        classifier: LightGBMPurposeClassifier instance
        cache_enabled: Whether to use prediction caching
        verbose: Whether to show detailed output

    Returns:
        Dictionary with message information and prediction results
    """
    # Read the message
    message = read_mt_message(file_path)
    if not message:
        return {
            'file_name': os.path.basename(file_path),
            'message_type': 'Error',
            'narration': None,
            'purpose_code': 'N/A',
            'purpose_confidence': 0.0,
            'category_purpose_code': 'N/A',
            'category_confidence': 0.0,
            'error': 'Failed to read file'
        }

    # Detect message type
    message_type = detect_message_type(message)

    # Extract narration
    narration, detected_type = extract_narration(message, message_type)

    # If narration extraction failed, use the message as is
    if not narration:
        logger.warning(f"Failed to extract narration from {file_path}")
        narration = message

    # Extract all fields for additional context
    all_fields = extract_all_fields(message, message_type)

    # Make prediction
    start_time = time.time()

    # Use the message type detected from the message
    result = classifier.predict(narration, message_type=detected_type or message_type)

    prediction_time = time.time() - start_time

    # Create result dictionary
    message_info = {
        'file_name': os.path.basename(file_path),
        'message_type': detected_type or message_type,
        'narration': narration,
        'purpose_code': result.get('purpose_code', 'N/A'),
        'purpose_confidence': result.get('confidence', 0.0),
        'category_purpose_code': result.get('category_purpose_code', 'N/A'),
        'category_confidence': result.get('category_confidence', 0.0),
        'processing_time': prediction_time,
        'enhanced': result.get('enhanced', False) or bool(result.get('enhancement_applied', '')),
        'enhancer': result.get('enhancement_applied', ''),
        'enhancement_type': result.get('enhancement_type', ''),
        'all_fields': all_fields
    }

    # Add enhancer decisions if available
    if 'enhancer_decisions' in result and result['enhancer_decisions']:
        message_info['enhancer_decisions'] = result['enhancer_decisions']

    # Print detailed information if verbose
    if verbose:
        print(f"\n=== Processing {os.path.basename(file_path)} ===")
        print(f"Message Type: {message_info['message_type']}")
        print(f"Narration: \"{narration}\"")
        print(f"Purpose Code: {message_info['purpose_code']} (Confidence: {message_info['purpose_confidence']:.4f})")
        print(f"Category Purpose Code: {message_info['category_purpose_code']} (Confidence: {message_info['category_confidence']:.4f})")

        if message_info['enhanced']:
            print(f"Enhanced: YES - {message_info['enhancer']}")
            print(f"Enhancement Type: {message_info['enhancement_type']}")
        else:
            print("Enhanced: NO")

        if 'enhancer_decisions' in message_info and message_info['enhancer_decisions']:
            print("\nEnhancer Decisions:")
            for decision in message_info['enhancer_decisions']:
                applied = "✓" if decision.get('applied', False) else "✗"
                print(f"  {applied} {decision.get('enhancer', 'Unknown')}: {decision.get('old_code', 'Unknown')} -> {decision.get('new_code', 'Unknown')} (conf: {decision.get('confidence', 0.0):.2f})")
                if 'reason' in decision:
                    print(f"     Reason: {decision.get('reason')}")

        print(f"Processing Time: {prediction_time:.4f} seconds")
        print("-" * 60)
    else:
        print(f"Processed {os.path.basename(file_path)}: {message_info['purpose_code']} ({message_info['purpose_confidence']:.4f})")

    return message_info

def analyze_results(results, purpose_codes, category_purpose_codes):
    """
    Analyze results and print detailed statistics

    Args:
        results: List of message info dictionaries
        purpose_codes: Dictionary of purpose codes and descriptions
        category_purpose_codes: Dictionary of category purpose codes and descriptions
    """
    # Group results by message type
    results_by_type = defaultdict(list)
    for result in results:
        message_type = result.get('message_type', 'Unknown')
        results_by_type[message_type].append(result)

    # Print overall statistics
    print("\n=== ANALYSIS OF RESULTS ===\n")

    # Create a summary table
    summary_table = []
    total_count = len(results)
    total_enhanced = sum(1 for r in results if r.get('enhanced', False))
    total_confidence = sum(r.get('purpose_confidence', 0) for r in results) / total_count if total_count else 0
    total_category_confidence = sum(r.get('category_confidence', 0) for r in results) / total_count if total_count else 0

    # Add overall row
    summary_table.append([
        'OVERALL',
        total_count,
        f"{total_enhanced} ({total_enhanced/total_count*100:.1f}%)" if total_count else "0 (0.0%)",
        f"{total_confidence:.4f}",
        f"{total_category_confidence:.4f}"
    ])

    # Add rows for each message type
    for message_type, type_results in results_by_type.items():
        count = len(type_results)
        enhanced = sum(1 for r in type_results if r.get('enhanced', False))
        avg_confidence = sum(r.get('purpose_confidence', 0) for r in type_results) / count if count else 0
        avg_category_confidence = sum(r.get('category_confidence', 0) for r in type_results) / count if count else 0

        summary_table.append([
            message_type,
            count,
            f"{enhanced} ({enhanced/count*100:.1f}%)" if count else "0 (0.0%)",
            f"{avg_confidence:.4f}",
            f"{avg_category_confidence:.4f}"
        ])

    # Print summary table
    print("Summary by Message Type:")
    print(tabulate(
        summary_table,
        headers=['Message Type', 'Count', 'Enhanced', 'Avg Purpose Confidence', 'Avg Category Confidence'],
        tablefmt='grid'
    ))

    # Print purpose code distribution by message type
    print("\nPurpose Code Distribution by Message Type:")
    for message_type, type_results in results_by_type.items():
        print(f"\n{message_type} Messages ({len(type_results)} files):")

        # Count purpose codes
        purpose_code_counts = defaultdict(int)
        for result in type_results:
            purpose_code = result.get('purpose_code', 'N/A')
            purpose_code_counts[purpose_code] += 1

        # Create table
        purpose_table = []
        for code, count in purpose_code_counts.items():
            description = purpose_codes.get(code, "Unknown")
            percentage = (count / len(type_results)) * 100 if type_results else 0
            purpose_table.append([code, description, count, f"{percentage:.1f}%"])

        # Sort by count (descending)
        purpose_table.sort(key=lambda x: x[2], reverse=True)

        # Print table
        print(tabulate(
            purpose_table,
            headers=['Code', 'Description', 'Count', 'Percentage'],
            tablefmt='grid'
        ))

    # Print category purpose code distribution by message type
    print("\nCategory Purpose Code Distribution by Message Type:")
    for message_type, type_results in results_by_type.items():
        print(f"\n{message_type} Messages ({len(type_results)} files):")

        # Count category purpose codes
        category_code_counts = defaultdict(int)
        for result in type_results:
            category_code = result.get('category_purpose_code', 'N/A')
            category_code_counts[category_code] += 1

        # Create table
        category_table = []
        for code, count in category_code_counts.items():
            description = category_purpose_codes.get(code, "Unknown")
            percentage = (count / len(type_results)) * 100 if type_results else 0
            category_table.append([code, description, count, f"{percentage:.1f}%"])

        # Sort by count (descending)
        category_table.sort(key=lambda x: x[2], reverse=True)

        # Print table
        print(tabulate(
            category_table,
            headers=['Code', 'Description', 'Count', 'Percentage'],
            tablefmt='grid'
        ))

    # Print enhancement statistics
    if any(r.get('enhanced', False) for r in results):
        print("\nEnhancement Statistics:")

        # Count by enhancer
        enhancer_counts = defaultdict(int)
        for result in results:
            if result.get('enhanced', False):
                enhancer = result.get('enhancer', 'Unknown')
                enhancer_counts[enhancer] += 1

        # Create table
        enhancer_table = []
        for enhancer, count in enhancer_counts.items():
            percentage = (count / total_enhanced) * 100 if total_enhanced else 0
            enhancer_table.append([enhancer, count, f"{percentage:.1f}%"])

        # Sort by count (descending)
        enhancer_table.sort(key=lambda x: x[1], reverse=True)

        # Print table
        print(tabulate(
            enhancer_table,
            headers=['Enhancer', 'Count', 'Percentage'],
            tablefmt='grid'
        ))

        # Count by enhancement type
        enhancement_type_counts = defaultdict(int)
        for result in results:
            if result.get('enhanced', False):
                enhancement_type = result.get('enhancement_type', 'Unknown')
                enhancement_type_counts[enhancement_type] += 1

        # Create table
        enhancement_type_table = []
        for enhancement_type, count in enhancement_type_counts.items():
            percentage = (count / total_enhanced) * 100 if total_enhanced else 0
            enhancement_type_table.append([enhancement_type, count, f"{percentage:.1f}%"])

        # Sort by count (descending)
        enhancement_type_table.sort(key=lambda x: x[1], reverse=True)

        # Print table
        print("\nEnhancement Types:")
        print(tabulate(
            enhancement_type_table,
            headers=['Enhancement Type', 'Count', 'Percentage'],
            tablefmt='grid'
        ))

def save_results_to_csv(results, output_path):
    """
    Save results to a CSV file

    Args:
        results: List of message info dictionaries
        output_path: Path to save the CSV file
    """
    # Extract fields for CSV
    csv_data = []
    for result in results:
        # Create a copy without the 'all_fields' and 'enhancer_decisions' keys
        row = {k: v for k, v in result.items() if k not in ['all_fields', 'enhancer_decisions']}
        csv_data.append(row)

    # Write to CSV
    with open(output_path, 'w', newline='') as f:
        # Get all unique keys from all dictionaries
        fieldnames = set()
        for row in csv_data:
            fieldnames.update(row.keys())

        # Convert to list and sort
        fieldnames = sorted(list(fieldnames))

        # Create writer and write data
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)

    print(f"\nResults saved to {output_path}")

def main():
    """Main function to process MT messages and classify purpose codes"""
    args = parse_args()

    # Load purpose codes
    purpose_codes, category_purpose_codes = load_purpose_codes()

    # Check if messages directory exists
    messages_dir = Path(args.messages_dir)
    if not messages_dir.exists():
        print(f"Messages directory not found: {args.messages_dir}")
        return 1

    # Initialize purpose classifier
    print(f"Initializing purpose classifier with model: {args.model}")
    classifier = LightGBMPurposeClassifier(model_path=args.model)
    classifier.load()
    print("Model loaded successfully")

    # Initialize text preprocessor
    preprocessor = TextPreprocessor()

    # Process MT message files
    results = []

    print(f"\nProcessing MT messages from {args.messages_dir}")
    message_files = list(messages_dir.glob("*.txt"))

    if not message_files:
        print(f"No message files found in {args.messages_dir}")
        return 1

    print(f"Found {len(message_files)} message files")

    # Process each file
    for i, file_path in enumerate(message_files):
        print(f"Processing {i+1}/{len(message_files)}: {file_path.name}")
        result = process_mt_message(
            file_path,
            classifier,
            cache_enabled=args.cache,
            verbose=args.verbose
        )
        results.append(result)

    # Save results to CSV
    save_results_to_csv(results, args.output)

    # Analyze results
    analyze_results(results, purpose_codes, category_purpose_codes)

    print("\nProcessing completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
