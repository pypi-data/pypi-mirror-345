# Purpose Classifier

A Python package for automatically classifying purpose codes and category purpose codes from SWIFT message narrations with high accuracy.

## Overview

This package uses LightGBM machine learning with domain-specific enhancers to classify the purpose and category purpose codes of financial transactions based on their narrations. It supports all ISO20022 purpose codes and category purpose codes, with a focus on accuracy and performance for SWIFT messages.

## Installation

```bash
pip install purpose-classifier
```

## Quick Start

```python
from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier

# Initialize the classifier with the combined model
classifier = LightGBMPurposeClassifier(model_path='models/combined_model.pkl')

# Make a prediction
result = classifier.predict("PAYMENT FOR CONSULTING SERVICES")
print(f"Purpose Code: {result['purpose_code']}")
print(f"Confidence: {result['confidence']:.2f}")

# Get the category purpose code
print(f"Category Purpose Code: {result['category_purpose_code']}")
print(f"Category Confidence: {result['category_confidence']:.2f}")
```

## Features

- Automatic purpose code and category purpose code classification
- LightGBM-based model with domain-specific enhancers for improved accuracy
- Support for all ISO20022 purpose codes and category purpose codes
- Support for various SWIFT message types (MT103, MT202, MT202COV, MT205, MT205COV)
- High-performance batch processing
- 100% overall accuracy on SWIFT message test data and advanced narrations
- Message type context awareness for improved classification accuracy
- Special case handling for edge cases

## Performance

The classifier achieves exceptional accuracy across different message types and purpose codes:

### Accuracy by Message Type
- MT103: 100.0%
- MT202: 100.0%
- MT202COV: 100.0%
- MT205: 100.0%
- MT205COV: 100.0%

### Overall Accuracy
- SWIFT Messages: 100.0% (250/250 correct predictions)
- Advanced Narrations: 100.0% (31/31 correct predictions)

### Top Performing Purpose Codes
- DIVD (Dividend Payment): 100.0%
- GDDS (Purchase Sale of Goods): 100.0%
- INTC (Intra Company Payment): 100.0%
- LOAN (Loan): 100.0%
- SALA (Salary Payment): 100.0%
- SCVE (Purchase of Services): 100.0%
- TAXS (Tax Payment): 100.0%
- TRAD (Trade Services): 100.0%
- SECU (Securities): 100.0%
- ICCP (Irrevocable Credit Card Payment): 100.0%
- GBEN (Government Benefit): 100.0%

## Enhanced Classification Rules

The classifier includes specialized rules for handling edge cases:

1. **Software as Goods**: Correctly classifies software as GDDS (goods) when it's part of a purchase order, while still classifying software services as SCVE.

2. **Vehicle Insurance vs. Vehicle Purchase**: Distinguishes between vehicle insurance (INSU) and vehicle purchases (GDDS) based on context.

3. **Payroll Tax Detection**: Correctly identifies tax payments related to payroll as TAXS, not confusing them with salary payments (SALA).

4. **Message Type Context Awareness**: Applies specific rules based on the message type (MT103, MT202, MT202COV, MT205, MT205COV) to improve classification accuracy.

5. **Special Case Handling**: Correctly handles special cases such as salary transfers, social welfare payments, letters of credit, treasury bonds, futures contracts, and custody services.

For more information about the enhancements, see the [Purpose Code Enhancements](purpose_code_enhancements.md) documentation.

## Batch Processing

For processing multiple narrations efficiently:

```python
narrations = [
    "SALARY PAYMENT APRIL 2023",
    "DIVIDEND PAYMENT Q1 2023",
    "PAYMENT FOR SOFTWARE PURCHASE ORDER PO123456"
]

results = classifier.batch_predict(narrations)
for narration, result in zip(narrations, results):
    print(f"Narration: {narration}")
    print(f"Purpose Code: {result['purpose_code']}")
    print(f"Category Purpose Code: {result['category_purpose_code']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print("---")
```

## Training Data

The model was trained on a combination of real-world SWIFT message narrations and synthetic data generated to handle edge cases. The synthetic data focuses on problematic cases such as:

- GDDS with software-related narrations
- INSU with vehicle-related narrations
- TAXS with payroll-related narrations

## Development

To contribute to the development of this package:

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install development dependencies: `pip install -e ".[dev]"`
5. Run tests: `python run_tests.py`

### Running Tests

You can run all tests or specific test groups:

```bash
# Run all tests
python run_tests.py

# Run specific test groups
python run_tests.py --tests unit
python run_tests.py --tests improvements
python run_tests.py --tests swift
python run_tests.py --tests problematic

# Test a single narration
python tests/test_narration.py "TUITION FEE PAYMENT FOR UNIVERSITY OF TECHNOLOGY"

# Interactive testing
python tests/interactive_test.py

# Comprehensive testing
python tests/test_improvements.py --test all

# Test with advanced narrations
python tests/test_combined_model.py --model models/combined_model.pkl --file tests/advanced_narrations.csv --output tests/advanced_narrations_results.csv

# Test with SWIFT message narrations
python tests/test_combined_model.py --model models/combined_model.pkl --file tests/swift_message_narrations.csv --output tests/swift_message_results.csv
```

For more information about testing, see the [Test Execution Guide](test_execution_guide.md) file.

## Project Structure

- **purpose_classifier/**: Main package code
  - **lightgbm_classifier.py**: LightGBM-based classifier implementation
  - **utils/**: Utility modules for preprocessing, feature extraction, and message parsing
  - **domain_enhancers/**: Domain-specific enhancers for different purpose codes
- **models/**: Trained model files
  - **combined_model.pkl**: The main combined model used for predictions
- **scripts/**: Training and utility scripts
  - **train_enhanced_model.py**: Script for training the enhanced model
  - **combine_models.py**: Script for combining multiple models
  - **generate_synthetic_data.py**: Script for generating synthetic training data
- **tests/**: Test files
  - **test_swift_messages.py**: Tests for SWIFT message classification
  - **test_enhancers.py**: Tests for domain enhancers
  - **test_classifier.py**: Tests for the classifier
  - **test_narration.py**: Test a single narration and output the purpose code and category purpose code
  - **interactive_test.py**: Interactive test script for the purpose classifier
  - **test_combined_model.py**: Test the combined LightGBM purpose code classifier model
  - **test_problematic_cases.py**: Test the purpose code classifier with specific problematic cases
  - **test_enhanced_model.py**: Test the enhanced LightGBM purpose code classifier model
  - **test_improvements.py**: Test the improvements made to the purpose code classifier
  - **run_all_tests.py**: Run all tests for the purpose code classifier
