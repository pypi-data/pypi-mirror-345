#!/usr/bin/env python3
"""
Script to analyze MT messages from test_messages folder.
Extracts narrations and predicts purpose codes and category purpose codes.
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
from collections import defaultdict
import time
import logging
from tabulate import tabulate

# Import classifier and utilities
from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier
from purpose_classifier.utils.message_parser import (
    detect_message_type,
    extract_narration,
    extract_all_fields
)
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

def read_mt_message(file_path):
    """Read an MT message from a file"""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        return None

def process_mt_message(file_path, classifier):
    """Process an MT message file and return prediction results"""
    # Read the message
    message = read_mt_message(file_path)
    if not message:
        return {
            'file': file_path,
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
    result = classifier.predict(narration, message_type=detected_type or message_type)
    prediction_time = time.time() - start_time

    # Add additional information to result
    result['file'] = os.path.basename(file_path)
    result['message_type'] = detected_type or message_type
    result['extracted_narration'] = narration
    result['processing_time'] = prediction_time
    result['all_fields'] = all_fields

    return result

def analyze_results_by_message_type(results, purpose_codes, category_purpose_codes):
    """Analyze results grouped by message type"""
    # Group results by message type
    results_by_type = defaultdict(list)
    for result in results:
        message_type = result.get('message_type', 'Unknown')
        results_by_type[message_type].append(result)

    # Analyze each group
    analysis = {}
    for message_type, type_results in results_by_type.items():
        # Count purpose codes
        purpose_code_counts = defaultdict(int)
        category_purpose_code_counts = defaultdict(int)
        confidence_sum = 0
        category_confidence_sum = 0
        enhanced_count = 0

        for result in type_results:
            purpose_code = result.get('purpose_code', 'UNKNOWN')
            category_purpose_code = result.get('category_purpose_code', 'UNKNOWN')

            purpose_code_counts[purpose_code] += 1
            category_purpose_code_counts[category_purpose_code] += 1

            confidence_sum += result.get('confidence', 0)
            category_confidence_sum += result.get('category_confidence', 0)

            if result.get('enhanced', False) or result.get('enhancement_applied'):
                enhanced_count += 1

        # Calculate statistics
        avg_confidence = confidence_sum / len(type_results) if type_results else 0
        avg_category_confidence = category_confidence_sum / len(type_results) if type_results else 0
        enhanced_percentage = (enhanced_count / len(type_results) * 100) if type_results else 0

        # Store analysis
        analysis[message_type] = {
            'count': len(type_results),
            'purpose_code_counts': dict(purpose_code_counts),
            'category_purpose_code_counts': dict(category_purpose_code_counts),
            'avg_confidence': avg_confidence,
            'avg_category_confidence': avg_category_confidence,
            'enhanced_percentage': enhanced_percentage
        }

    return analysis

def print_analysis(analysis, purpose_codes, category_purpose_codes):
    """Print analysis results in a readable format"""
    print("\n=== ANALYSIS BY MESSAGE TYPE ===\n")

    for message_type, stats in analysis.items():
        print(f"\n{message_type} Messages ({stats['count']} files):")
        print("-" * 50)

        # Print purpose code distribution
        purpose_table = []
        for code, count in stats['purpose_code_counts'].items():
            description = purpose_codes.get(code, "Unknown")
            percentage = (count / stats['count']) * 100 if stats['count'] else 0
            purpose_table.append([code, description, count, f"{percentage:.1f}%"])

        print("\nPurpose Code Distribution:")
        print(tabulate(purpose_table, headers=["Code", "Description", "Count", "Percentage"], tablefmt="grid"))

        # Print category purpose code distribution
        category_table = []
        for code, count in stats['category_purpose_code_counts'].items():
            description = category_purpose_codes.get(code, "Unknown")
            percentage = (count / stats['count']) * 100 if stats['count'] else 0
            category_table.append([code, description, count, f"{percentage:.1f}%"])

        print("\nCategory Purpose Code Distribution:")
        print(tabulate(category_table, headers=["Code", "Description", "Count", "Percentage"], tablefmt="grid"))

        # Print statistics
        print("\nStatistics:")
        print(f"Average Confidence: {stats['avg_confidence']:.4f}")
        print(f"Average Category Confidence: {stats['avg_category_confidence']:.4f}")
        print(f"Enhanced Percentage: {stats['enhanced_percentage']:.1f}%")

    print("\n=== OVERALL STATISTICS ===\n")
    total_count = sum(stats['count'] for stats in analysis.values())
    total_confidence = sum(stats['avg_confidence'] * stats['count'] for stats in analysis.values())
    total_category_confidence = sum(stats['avg_category_confidence'] * stats['count'] for stats in analysis.values())
    total_enhanced = sum((stats['enhanced_percentage'] / 100) * stats['count'] for stats in analysis.values())

    print(f"Total Files Processed: {total_count}")
    print(f"Overall Average Confidence: {total_confidence / total_count if total_count else 0:.4f}")
    print(f"Overall Average Category Confidence: {total_category_confidence / total_count if total_count else 0:.4f}")
    print(f"Overall Enhanced Percentage: {(total_enhanced / total_count * 100) if total_count else 0:.1f}%")

def save_results_to_csv(results, output_path):
    """Save detailed results to a CSV file"""
    # Extract relevant fields for CSV
    csv_data = []
    for result in results:
        row = {
            'file': result.get('file', ''),
            'message_type': result.get('message_type', ''),
            'narration': result.get('extracted_narration', ''),
            'purpose_code': result.get('purpose_code', ''),
            'confidence': result.get('confidence', 0),
            'category_purpose_code': result.get('category_purpose_code', ''),
            'category_confidence': result.get('category_confidence', 0),
            'enhanced': result.get('enhanced', False) or bool(result.get('enhancement_applied', '')),
            'enhancer': result.get('enhancement_applied', ''),
            'processing_time': result.get('processing_time', 0)
        }
        csv_data.append(row)

    # Create DataFrame and save to CSV
    df = pd.DataFrame(csv_data)
    df.to_csv(output_path, index=False)
    print(f"\nDetailed results saved to {output_path}")

def main():
    """Main function to process MT messages and analyze results"""
    print("=== MT Message Analysis Tool ===")

    # Load purpose codes
    purpose_codes, category_purpose_codes = load_purpose_codes()

    # Initialize classifier
    print("\nLoading classifier model...")
    classifier = LightGBMPurposeClassifier(model_path=MODEL_PATH)
    classifier.load()
    print("Model loaded successfully")

    # Get test message files
    base_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    test_messages_dir = base_dir / "MT_messages" / "test_messages"
    if not test_messages_dir.exists():
        print(f"Error: Directory {test_messages_dir} not found")
        sys.exit(1)

    message_files = list(test_messages_dir.glob("*.txt"))
    print(f"\nFound {len(message_files)} message files in {test_messages_dir}")

    # Process each file
    print("\nProcessing message files...")
    results = []
    for i, file_path in enumerate(message_files):
        print(f"Processing {i+1}/{len(message_files)}: {file_path.name}")
        result = process_mt_message(file_path, classifier)
        results.append(result)

    # Analyze results
    print("\nAnalyzing results...")
    analysis = analyze_results_by_message_type(results, purpose_codes, category_purpose_codes)

    # Print analysis
    print_analysis(analysis, purpose_codes, category_purpose_codes)

    # Save detailed results to CSV
    base_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    output_path = base_dir / "MT_messages" / "analysis_results.csv"
    save_results_to_csv(results, output_path)

    print("\nAnalysis completed successfully")

if __name__ == "__main__":
    main()
