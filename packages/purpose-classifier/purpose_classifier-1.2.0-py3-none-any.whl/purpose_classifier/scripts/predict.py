#!/usr/bin/env python3
"""
Prediction script for the MT Message Purpose Code Classifier.
Loads a trained model and makes predictions on new data.
"""

import os
import sys
import json
import argparse
import logging
import pandas as pd
import re
import numpy as np
from datetime import datetime
from pathlib import Path
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

# Import classifier and configuration
from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier
from purpose_classifier.utils.message_parser import detect_message_type, extract_narration, extract_all_fields, validate_message_format
from purpose_classifier.config.settings import (
    MODEL_PATH, SAMPLE_MESSAGES_PATH, setup_logging,
    get_environment, get_environment_settings, PROD_SETTINGS,
    PURPOSE_CODES_PATH, CATEGORY_PURPOSE_CODES_PATH
)

# Setup prediction cache
prediction_cache = {}

# Custom JSON encoder to handle numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

# Load purpose codes and category purpose codes
def load_purpose_codes():
    """Load purpose codes and category purpose codes from JSON files"""
    purpose_codes = {}
    category_purpose_codes = {}

    try:
        with open(PURPOSE_CODES_PATH, 'r') as f:
            purpose_codes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.getLogger(__name__).error(f"Failed to load purpose codes from {PURPOSE_CODES_PATH}: {str(e)}")

    try:
        with open(CATEGORY_PURPOSE_CODES_PATH, 'r') as f:
            category_purpose_codes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.getLogger(__name__).error(f"Failed to load category purpose codes from {CATEGORY_PURPOSE_CODES_PATH}: {str(e)}")

    return purpose_codes, category_purpose_codes

# Global variables for purpose codes
purpose_codes = {}
category_purpose_codes = {}

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Make predictions with the MT Message Purpose Code Classifier')

    parser.add_argument('--model', type=str, default=MODEL_PATH,
                        help=f'Path to trained model (default: {MODEL_PATH})')

    parser.add_argument('--input', type=str, default=None,
                        help='Path to input file (text, JSON, or CSV)')

    parser.add_argument('--text', type=str, default=None,
                        help='Direct text input for prediction')

    parser.add_argument('--output', type=str, default=None,
                        help='Path to output file for results (default: stdout)')

    parser.add_argument('--format', type=str, choices=['json', 'csv', 'text'], default='json',
                        help='Output format (default: json)')

    parser.add_argument('--env', type=str, default=None,
                        help='Environment (development, test, production)')

    parser.add_argument('--sample', action='store_true',
                        help=f'Use sample messages from {SAMPLE_MESSAGES_PATH}')

    parser.add_argument('--batch-size', type=int, default=PROD_SETTINGS['batch_size'],
                        help='Batch size for processing (default: %(default)s)')

    parser.add_argument('--workers', type=int, default=PROD_SETTINGS['max_workers'],
                        help='Number of worker threads (default: %(default)s)')

    parser.add_argument('--log-predictions', action='store_true',
                        help='Enable detailed logging of predictions')

    parser.add_argument('--cache', action='store_true',
                        help='Enable prediction caching')

    parser.add_argument('--show-enhancers', action='store_true',
                        help='Show detailed information about available enhancers')

    parser.add_argument('--verbose', action='store_true',
                        help='Show verbose output including model details and enhancer information')

    return parser.parse_args()

def read_input(input_path, sample=False):
    """
    Read input data from file.

    Args:
        input_path: Path to input file
        sample: Whether to use sample messages

    Returns:
        List of texts or messages for prediction
    """
    logger = logging.getLogger(__name__)

    if sample:
        # Use sample messages
        try:
            with open(SAMPLE_MESSAGES_PATH, 'r') as f:
                samples = json.load(f)
            logger.info(f"Loaded {len(samples)} sample messages")
            return [sample['message'] for sample in samples.values()]
        except Exception as e:
            logger.error(f"Error loading sample messages: {str(e)}")
            raise

    if not input_path:
        return []

    input_path = Path(input_path)

    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Determine file type from extension
    if input_path.suffix.lower() == '.json':
        try:
            with open(input_path, 'r') as f:
                data = json.load(f)

            # Handle different JSON formats
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                if 'messages' in data:
                    return data['messages']
                elif 'texts' in data:
                    return data['texts']
                else:
                    return list(data.values())
            else:
                logger.error("Unsupported JSON format")
                raise ValueError("Unsupported JSON format")
        except Exception as e:
            logger.error(f"Error reading JSON file: {str(e)}")
            raise

    elif input_path.suffix.lower() == '.csv':
        try:
            df = pd.read_csv(input_path)

            # Look for message or text column
            for col in ['message', 'text', 'narration', 'input']:
                if col in df.columns:
                    logger.info(f"Using column '{col}' from CSV")
                    return df[col].tolist()

            # Default to first column
            logger.warning(f"No obvious text column found, using first column: {df.columns[0]}")
            return df.iloc[:, 0].tolist()
        except Exception as e:
            logger.error(f"Error reading CSV file: {str(e)}")
            raise

    else:
        # Assume text file with one entry per line
        try:
            with open(input_path, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
            logger.info(f"Loaded {len(lines)} lines from text file")
            return lines
        except Exception as e:
            logger.error(f"Error reading text file: {str(e)}")
            raise

def write_output(results, output_path, output_format):
    """
    Write prediction results to output.

    Args:
        results: List of prediction result dictionaries
        output_path: Path to output file (None for stdout)
        output_format: Format to write (json, csv, text)
    """
    logger = logging.getLogger(__name__)

    # No special cases - rely on the enhancer system to handle all cases

    # Format the results
    if output_format == 'json':
        try:
            output = json.dumps(results, indent=2, cls=NumpyEncoder)
        except Exception as e:
            logger.error(f"Error formatting JSON output: {str(e)}")
            raise
    elif output_format == 'csv':
        try:
            df = pd.DataFrame(results)
            output = df.to_csv(index=False)
        except Exception as e:
            logger.error(f"Error formatting CSV output: {str(e)}")
            raise
    else:  # text
        try:
            lines = []
            for r in results:
                # Get purpose code and description
                purpose_code = r.get('purpose_code', 'UNKNOWN')
                purpose_desc = r.get('purpose_description', purpose_codes.get(purpose_code, 'No description available'))

                # Get category purpose code and description
                category_code = r.get('category_purpose_code', 'UNKNOWN')
                category_desc = r.get('category_purpose_description', category_purpose_codes.get(category_code, 'No description available'))

                lines.append(f"Purpose Code: {purpose_code} ({purpose_desc})")
                lines.append(f"Category Purpose Code: {category_code} ({category_desc})")
                lines.append(f"Confidence: {r.get('confidence', 0.0):.4f}")

                # Add enhancement information
                # Check for enhancer decisions to determine if enhancement was applied
                if r.get('enhanced', False) or r.get('enhancement_applied') or (r.get('enhancer_decisions') and any(d.get('applied', False) for d in r.get('enhancer_decisions', []))):
                    enhancer_name = r.get('enhancement_applied', 'Unknown enhancement')
                    enhancement_type = r.get('enhancement_type', 'Unknown')

                    # If we have enhancer decisions, use the applied one
                    if r.get('enhancer_decisions'):
                        applied_decisions = [d for d in r.get('enhancer_decisions', []) if d.get('applied', False)]
                        if applied_decisions:
                            enhancer_name = applied_decisions[0].get('enhancer', enhancer_name)
                            # Get enhancement type from the reason if available
                            if applied_decisions[0].get('reason'):
                                if 'Pattern match:' in applied_decisions[0].get('reason', ''):
                                    enhancement_type = applied_decisions[0].get('reason').replace('Pattern match: ', '')
                                elif 'Software/services match:' in applied_decisions[0].get('reason', ''):
                                    enhancement_type = applied_decisions[0].get('reason').replace('Software/services match: ', '')
                                elif 'Tech domain match:' in applied_decisions[0].get('reason', ''):
                                    enhancement_type = applied_decisions[0].get('reason').replace('Tech domain match: ', '')
                                elif 'Tech domain boost' in applied_decisions[0].get('reason', ''):
                                    enhancement_type = 'tech_domain_boost'
                                elif 'Minor tech domain boost' in applied_decisions[0].get('reason', ''):
                                    enhancement_type = 'tech_domain_minor_boost'
                                elif 'Direct dividend keyword match:' in applied_decisions[0].get('reason', ''):
                                    enhancement_type = 'dividend_keyword'
                                elif 'Dividend context match:' in applied_decisions[0].get('reason', ''):
                                    enhancement_type = 'dividend_context'
                                elif 'Dividend semantic match:' in applied_decisions[0].get('reason', ''):
                                    enhancement_type = 'dividend_semantic'
                                elif 'Dividend edge case:' in applied_decisions[0].get('reason', ''):
                                    enhancement_type = 'dividend_edge_case'

                    lines.append(f"Enhanced: YES - {enhancer_name}")
                    lines.append(f"Enhancement Type: {enhancement_type}")
                    if r.get('original_purpose_code'):
                        lines.append(f"Original Purpose Code: {r.get('original_purpose_code')}")
                else:
                    lines.append("Enhanced: NO")

                # Add enhancer decisions if available
                if 'enhancer_decisions' in r and r['enhancer_decisions']:
                    lines.append("Enhancer Decisions:")
                    for decision in r['enhancer_decisions']:
                        applied = "✓" if decision.get('applied', False) else "✗"
                        lines.append(f"  {applied} {decision.get('enhancer', 'Unknown')}: {decision.get('old_code', 'Unknown')} -> {decision.get('new_code', 'Unknown')} (conf: {decision.get('confidence', 0.0):.2f})")
                        if 'reason' in decision:
                            lines.append(f"     Reason: {decision.get('reason')}")

                if 'message_type' in r and r['message_type']:
                    lines.append(f"Message Type: {r['message_type']}")
                lines.append(f"Input: {r.get('extracted_narration', '')[:100]}..." if len(r.get('extracted_narration', '')) > 100 else f"Input: {r.get('extracted_narration', '')}")
                lines.append("-" * 60)
            output = "\n".join(lines)
        except Exception as e:
            logger.error(f"Error formatting text output: {str(e)}")
            raise

    # Write to file or stdout
    if output_path:
        try:
            with open(output_path, 'w') as f:
                f.write(output)
            logger.info(f"Results written to {output_path}")
        except Exception as e:
            logger.error(f"Error writing to output file: {str(e)}")
            raise
    else:
        print(output)

def log_prediction(prediction, input_text):
    """
    Log prediction details for auditing and monitoring

    Args:
        prediction: Dictionary with prediction results
        input_text: Original input text
    """
    logger = logging.getLogger('prediction_audit')

    # Create audit log entry
    audit_entry = {
        'timestamp': datetime.now().isoformat(),
        'input_hash': hashlib.md5(input_text.encode()).hexdigest()[:8],  # For reference without storing full text
        'message_type': prediction.get('message_type', 'unknown'),
        'purpose_code': prediction.get('purpose_code'),
        'category_purpose_code': prediction.get('category_purpose_code'),
        'confidence': prediction.get('confidence'),
        'status': 'success' if prediction.get('purpose_code') else 'failure'
    }

    # Log as JSON
    logger.info(json.dumps(audit_entry, cls=NumpyEncoder))

def cached_predict(classifier, text, cache_enabled=False, message_type=None):
    """
    Make a prediction with optional caching

    Args:
        classifier: Classifier instance
        text: Input text
        cache_enabled: Whether to use caching
        message_type: Optional message type (will be detected from narration if not provided)

    Returns:
        Prediction result dictionary
    """
    # Log the prediction request
    logger = logging.getLogger(__name__)
    logger.info(f"Making prediction for text: '{text}', message_type: '{message_type}'")

    if not cache_enabled:
        # Pass the text directly to the classifier
        # The classifier will prioritize narration content over message type
        return classifier.predict(text, message_type)

    # Use MD5 hash of text as cache key
    # Include message_type in the cache key if provided
    if message_type:
        cache_key = hashlib.md5((text + message_type).encode()).hexdigest()
    else:
        cache_key = hashlib.md5(text.encode()).hexdigest()

    # Check cache
    if cache_key in prediction_cache:
        return prediction_cache[cache_key]

    # Make prediction
    # Pass the text directly to the classifier
    # The classifier will prioritize narration content over message type
    logger = logging.getLogger(__name__)
    logger.info(f"Calling classifier.predict with text: '{text}', message_type: '{message_type}'")

    print(f"\n=== Making Prediction ===")
    print(f"Input text: '{text}'")
    if message_type:
        print(f"Message type: {message_type}")

    # Time the prediction
    start_time = time.time()
    result = classifier.predict(text, message_type)
    prediction_time = time.time() - start_time

    # Add prediction time to result
    result['processing_time'] = prediction_time

    # Log the purpose code and confidence
    logger.info(f"Prediction result: {result.get('purpose_code', 'UNKNOWN')} with confidence {result.get('confidence', 0.0)}")
    print(f"Predicted purpose code: {result.get('purpose_code', 'UNKNOWN')}")
    print(f"Confidence: {result.get('confidence', 0.0):.4f}")
    print(f"Category purpose code: {result.get('category_purpose_code', 'UNKNOWN')}")
    print(f"Processing time: {prediction_time:.4f} seconds")

    # Log enhancement information
    # Check for enhancer decisions to determine if enhancement was applied
    if result.get('enhanced', False) or result.get('enhancement_applied') or (result.get('enhancer_decisions') and any(d.get('applied', False) for d in result.get('enhancer_decisions', []))):
        enhancer_name = result.get('enhancement_applied', 'Unknown enhancement')
        enhancement_type = result.get('enhancement_type', 'Unknown')

        # If we have enhancer decisions, use the applied one
        if result.get('enhancer_decisions'):
            applied_decisions = [d for d in result.get('enhancer_decisions', []) if d.get('applied', False)]
            if applied_decisions:
                enhancer_name = applied_decisions[0].get('enhancer', enhancer_name)
                # Get enhancement type from the reason if available
                if applied_decisions[0].get('reason'):
                    if 'Pattern match:' in applied_decisions[0].get('reason', ''):
                        enhancement_type = applied_decisions[0].get('reason').replace('Pattern match: ', '')
                    elif 'Software/services match:' in applied_decisions[0].get('reason', ''):
                        enhancement_type = applied_decisions[0].get('reason').replace('Software/services match: ', '')
                    elif 'Tech domain match:' in applied_decisions[0].get('reason', ''):
                        enhancement_type = applied_decisions[0].get('reason').replace('Tech domain match: ', '')
                    elif 'Tech domain boost' in applied_decisions[0].get('reason', ''):
                        enhancement_type = 'tech_domain_boost'
                    elif 'Minor tech domain boost' in applied_decisions[0].get('reason', ''):
                        enhancement_type = 'tech_domain_minor_boost'
                    elif 'Direct dividend keyword match:' in applied_decisions[0].get('reason', ''):
                        enhancement_type = 'dividend_keyword'
                    elif 'Dividend context match:' in applied_decisions[0].get('reason', ''):
                        enhancement_type = 'dividend_context'
                    elif 'Dividend semantic match:' in applied_decisions[0].get('reason', ''):
                        enhancement_type = 'dividend_semantic'
                    elif 'Dividend edge case:' in applied_decisions[0].get('reason', ''):
                        enhancement_type = 'dividend_edge_case'

        print(f"Enhanced: YES - {enhancer_name}")
        print(f"Enhancement type: {enhancement_type}")
        if result.get('original_purpose_code'):
            print(f"Original purpose code: {result.get('original_purpose_code')}")
    else:
        print("Enhanced: NO")

    # Log the enhancer decisions if available
    if 'enhancer_decisions' in result and result['enhancer_decisions']:
        logger.info(f"Enhancer decisions: {result['enhancer_decisions']}")
        print("\nEnhancer decisions:")
        for decision in result['enhancer_decisions']:
            applied = "✓" if decision.get('applied', False) else "✗"
            print(f"  {applied} {decision.get('enhancer', 'Unknown')}: {decision.get('old_code', 'Unknown')} -> {decision.get('new_code', 'Unknown')} (conf: {decision.get('confidence', 0.0):.2f})")
            if 'reason' in decision:
                print(f"     Reason: {decision.get('reason')}")
    else:
        logger.info(f"No enhancer decisions found in result")
        print("\nNo enhancer decisions found")

    # Store in cache
    prediction_cache[cache_key] = result

    # Print a summary of the results with highlighted purpose codes
    print("\n=== PREDICTION SUMMARY ===")
    print(f"Input text: '{text}'")
    print(f"FINAL PURPOSE CODE: {result.get('purpose_code', 'UNKNOWN')}")
    print(f"FINAL CATEGORY PURPOSE CODE: {result.get('category_purpose_code', 'UNKNOWN')}")
    print(f"Confidence: {result.get('confidence', 0.0):.4f}")
    if result.get('enhanced', False):
        print(f"Enhanced by: {result.get('enhancer', 'Unknown enhancer')}")
        print(f"Enhancement reason: {result.get('reason', 'No reason provided')}")
    print("=" * 25)

    return result

def batch_process(inputs, classifier, batch_size, workers, cache_enabled, log_predictions):
    """
    Process inputs in batches with parallel workers

    Args:
        inputs: List of input texts
        classifier: Classifier instance
        batch_size: Size of each batch
        workers: Number of worker threads
        cache_enabled: Whether to use caching
        log_predictions: Whether to log prediction details

    Returns:
        List of prediction results
    """
    logger = logging.getLogger(__name__)

    start_time = time.time()
    results = []
    total_inputs = len(inputs)

    logger.info(f"Processing {total_inputs} inputs in batches of {batch_size} with {workers} workers")

    # Process in batches to avoid memory issues with large inputs
    for batch_start in range(0, total_inputs, batch_size):
        batch_end = min(batch_start + batch_size, total_inputs)
        batch = inputs[batch_start:batch_end]

        batch_results = []

        logger.info(f"Processing batch {batch_start//batch_size + 1} ({batch_start+1}-{batch_end} of {total_inputs})")
        batch_start_time = time.time()

        # Define worker function
        def process_item(item):
            try:
                # First, check if this is a simple narration (not a SWIFT message)
                # If it's a simple narration, we don't need to detect message type or extract narration
                # Check for common SWIFT message indicators
                is_swift_message = any(indicator in item for indicator in ['{1:', '{2:', ':20:', ':32A:'])

                if not is_swift_message:
                    # For simple narrations, use the text directly
                    narration = item
                    message_type = None

                    # Make prediction directly with the narration
                    # This ensures narration content is prioritized
                    # Pass None as message_type to let the classifier detect it from narration
                    result = cached_predict(classifier, narration, cache_enabled, message_type=None)

                    # Add narration to result
                    result['extracted_narration'] = narration

                    # Message type will be detected from narration content by the classifier
                    if 'message_type' not in result:
                        result['message_type'] = 'MT103'  # Default to MT103 if not detected
                else:
                    # For SWIFT messages, detect message type and extract narration
                    message_type = detect_message_type(item)

                    # Extract narration
                    narration, detected_type = extract_narration(item, message_type)

                    # If narration extraction failed, use the text as is
                    if not narration:
                        narration = item

                    # Make prediction
                    # Pass detected_type as message_type, but the classifier will still
                    # prioritize narration content over the provided message type
                    result = cached_predict(classifier, narration, cache_enabled, message_type=detected_type)

                    # Add additional information
                    # Use the message type from the result if available, otherwise use detected_type or message_type
                    if 'message_type' not in result:
                        result['message_type'] = detected_type or message_type
                    result['extracted_narration'] = narration

                # Log prediction if enabled
                if log_predictions:
                    log_prediction(result, item)

                return result

            except Exception as e:
                logger.error(f"Error processing item: {str(e)}")
                return {
                    'error': str(e),
                    'input': item[:100] + '...' if len(item) > 100 else item
                }

        # Process batch in parallel
        with ThreadPoolExecutor(max_workers=workers) as executor:
            batch_results = list(executor.map(process_item, batch))

        # Add batch results to overall results
        results.extend(batch_results)

        # Log batch timing
        batch_time = time.time() - batch_start_time
        if batch_time > 0:
            logger.info(f"Batch processed in {batch_time:.2f} seconds ({len(batch)/batch_time:.2f} items/sec)")
        else:
            logger.info(f"Batch processed in {batch_time:.2f} seconds")

    # Log total timing
    total_time = time.time() - start_time
    if total_time > 0:
        logger.info(f"All processing completed in {total_time:.2f} seconds ({total_inputs/total_time:.2f} items/sec)")
    else:
        logger.info(f"All processing completed in {total_time:.2f} seconds")

    return results

def setup_classifier(model_path=None):
    """
    Setup and initialize the classifier

    Args:
        model_path: Path to the model file (default: MODEL_PATH)

    Returns:
        Initialized classifier or None if initialization fails
    """
    logger = logging.getLogger(__name__)

    # Use default model path if not provided
    if model_path is None:
        model_path = MODEL_PATH

    # Check if model exists
    if not os.path.exists(model_path):
        logger.error(f"Model file not found: {model_path}")
        return None

    # Initialize classifier
    env = get_environment()
    logger.info(f"Loading model from {model_path}")

    classifier = LightGBMPurposeClassifier(
        environment=env,
        model_path=model_path
    )

    try:
        # Load the model
        classifier.load()
        return classifier
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return None

def predict_purpose_code(classifier, text, verbose=False):
    """
    Predict purpose code for a given text

    Args:
        classifier: Initialized classifier
        text: Input text
        verbose: Whether to show verbose output

    Returns:
        Prediction result dictionary
    """
    # Make prediction
    result = cached_predict(classifier, text, cache_enabled=False)

    # Format the result for display
    if verbose:
        format_prediction_result(result, text)

    return result

def format_prediction_result(result, text):
    """
    Format prediction result for display

    Args:
        result: Prediction result dictionary
        text: Input text
    """
    # This function doesn't need to do anything as cached_predict already formats the result
    pass

def main():
    """Main prediction function"""
    # Parse arguments
    args = parse_arguments()

    # Setup environment and logging
    env = args.env or get_environment()
    logger = setup_logging(env)

    # Load purpose codes
    global purpose_codes, category_purpose_codes
    purpose_codes, category_purpose_codes = load_purpose_codes()

    # Setup prediction audit logger if needed
    if args.log_predictions:
        prediction_logger = logging.getLogger('prediction_audit')
        handler = logging.FileHandler(os.path.join('logs', f'prediction_audit_{datetime.now().strftime("%Y%m%d")}.log'))
        handler.setFormatter(logging.Formatter('%(message)s'))
        prediction_logger.addHandler(handler)
        prediction_logger.setLevel(logging.INFO)
        prediction_logger.propagate = False

    logger.info(f"Starting prediction in {env} environment")

    try:
        # Check if model exists
        if not os.path.exists(args.model):
            logger.error(f"Model file not found: {args.model}")
            sys.exit(1)

        # Initialize and load classifier
        logger.info(f"Loading model from {args.model}")
        print(f"\n=== Loading Purpose Code Classifier Model ===")
        print(f"Model path: {args.model}")
        print(f"Environment: {env}")

        classifier = LightGBMPurposeClassifier(
            environment=env,
            model_path=args.model
        )
        try:
            classifier.load()

            # Display model information
            model_type = "LightGBM"
            if hasattr(classifier.model, 'bert_model'):
                model_type = f"BERT ({classifier.model.bert_model})"
            elif hasattr(classifier.model, 'get_params') and 'estimator' in classifier.model.get_params():
                model_type = f"Ensemble ({classifier.model.get_params()['estimator'].__class__.__name__})"

            print(f"Model type: {model_type}")
            print(f"Word embeddings loaded: {'Yes' if hasattr(classifier, 'matcher') and classifier.matcher.embeddings else 'No'}")
            print(f"Number of enhancers: {len(classifier.enhancer_manager.enhancers) if hasattr(classifier, 'enhancer_manager') else 'Unknown'}")
            print(f"Services enhancer available: {'Yes' if hasattr(classifier, 'enhancer_manager') and 'services' in classifier.enhancer_manager.enhancers else 'No'}")
            print(f"Model loaded successfully\n")

            # Show enhancer information if requested
            if args.show_enhancers or args.verbose:
                print("\n=== Available Enhancers ===")
                if hasattr(classifier, 'enhancer_manager') and classifier.enhancer_manager:
                    enhancers = classifier.enhancer_manager.enhancers
                    priorities = classifier.enhancer_manager.priorities

                    # Group enhancers by priority level
                    enhancers_by_level = {
                        'highest': [],
                        'high': [],
                        'medium': [],
                        'low': []
                    }

                    for name, enhancer in enhancers.items():
                        level = priorities.get(name, {}).get('level', 'unknown')
                        weight = priorities.get(name, {}).get('weight', 0.0)
                        enhancers_by_level.setdefault(level, []).append((name, enhancer, weight))

                    # Print enhancers by priority level
                    for level in ['highest', 'high', 'medium', 'low']:
                        print(f"\n{level.upper()} PRIORITY ENHANCERS:")
                        if level in enhancers_by_level and enhancers_by_level[level]:
                            # Sort by weight
                            sorted_enhancers = sorted(enhancers_by_level[level], key=lambda x: x[2], reverse=True)
                            for name, enhancer, weight in sorted_enhancers:
                                print(f"  - {name} (weight: {weight:.2f})")
                                # Show more details in verbose mode
                                if args.verbose:
                                    print(f"    Class: {enhancer.__class__.__name__}")
                                    if hasattr(enhancer, 'context_patterns') and enhancer.context_patterns:
                                        print(f"    Context patterns: {len(enhancer.context_patterns)}")
                                    if hasattr(enhancer, 'direct_keywords') and enhancer.direct_keywords:
                                        print(f"    Direct keywords: {len(enhancer.direct_keywords)}")
                        else:
                            print("  None")

                    # Show special information about services enhancer
                    if 'services_semantic' in enhancers:
                        print("\nSERVICES ENHANCER DETAILS:")
                        services_enhancer = enhancers['services_semantic']
                        if hasattr(services_enhancer, 'context_patterns'):
                            print(f"  Context patterns: {len(services_enhancer.context_patterns)}")
                            if args.verbose:
                                for i, pattern in enumerate(services_enhancer.context_patterns[:5]):
                                    print(f"    Pattern {i+1}: {pattern.get('keywords', [])} (proximity: {pattern.get('proximity', 0)}, weight: {pattern.get('weight', 0.0)})")
                                if len(services_enhancer.context_patterns) > 5:
                                    print(f"    ... and {len(services_enhancer.context_patterns) - 5} more patterns")
                else:
                    print("No enhancer manager found in the classifier")
                print()

        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            print(f"Error loading model: {str(e)}")
            sys.exit(1)

        # Get input data
        if args.text:
            # Direct text input
            logger.info("Using direct text input")
            inputs = [args.text]
        elif args.sample:
            # Use sample messages
            logger.info(f"Using sample messages from {SAMPLE_MESSAGES_PATH}")
            try:
                inputs = read_input(None, sample=True)
            except Exception as e:
                logger.error(f"Error reading sample messages: {str(e)}")
                sys.exit(1)
        elif args.input:
            # Read from file
            logger.info(f"Reading input from {args.input}")
            try:
                inputs = read_input(args.input)
            except Exception as e:
                logger.error(f"Error reading input: {str(e)}")
                sys.exit(1)
        else:
            logger.error("No input specified (use --text, --input, or --sample)")
            sys.exit(1)

        # Make predictions
        if not inputs:
            logger.warning("No input data to process")
            results = []
        else:
            logger.info(f"Making predictions on {len(inputs)} inputs")

            # Process inputs in batches
            results = batch_process(
                inputs=inputs,
                classifier=classifier,
                batch_size=args.batch_size,
                workers=args.workers,
                cache_enabled=args.cache,
                log_predictions=args.log_predictions
            )

        # Write output
        try:
            write_output(results, args.output, args.format)
        except Exception as e:
            logger.error(f"Error writing output: {str(e)}")
            sys.exit(1)

        logger.info("Prediction completed successfully")

        # Print message for test to capture from stdout
        print("Prediction completed")

        # Print a summary of the results with highlighted purpose codes
        if results and len(results) > 0:
            print("\n=== FINAL PREDICTION SUMMARY ===")
            for i, result in enumerate(results):
                print(f"Result {i+1}:")
                print(f"Input text: '{result.get('extracted_narration', 'Unknown')}'")
                print(f"FINAL PURPOSE CODE: {result.get('purpose_code', 'UNKNOWN')}")
                print(f"FINAL CATEGORY PURPOSE CODE: {result.get('category_purpose_code', 'UNKNOWN')}")
                print(f"Confidence: {result.get('confidence', 0.0):.4f}")
                if result.get('enhanced', False):
                    print(f"Enhanced by: {result.get('enhancer', 'Unknown enhancer')}")
                    print(f"Enhancement reason: {result.get('reason', 'No reason provided')}")
                print("=" * 50)

    except Exception as e:
        logger.error(f"Error in prediction script: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()