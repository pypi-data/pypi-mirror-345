# Purpose Code Classifier Tests

This document describes the tests available for the purpose code classifier.

## Test Files

- `test_narration.py`: Test a single narration and output the purpose code and category purpose code
- `interactive_test.py`: Interactive test script for the purpose classifier
- `test_combined_model.py`: Test the combined LightGBM purpose code classifier model
- `test_problematic_cases.py`: Test the purpose code classifier with specific problematic cases
- `test_enhanced_model.py`: Test the enhanced LightGBM purpose code classifier model
- `test_improvements.py`: Test the improvements made to the purpose code classifier
- `test_swift_messages.py`: Test the classifier on various SWIFT message types
- `test_classifier.py`: Unit tests for the classifier
- `test_enhancers.py`: Unit tests for the enhancers
- `run_all_tests.py`: Run all tests for the purpose code classifier
- `test_purpose_codes.py`: Test specific purpose codes and category purpose codes with generated narrations
- `test_custom_narrations.py`: Test custom narrations with expected purpose codes and category purpose codes
- `sample_narrations.csv`: Sample narrations for batch testing

## Running Tests

### Single Narration Test

```bash
python tests/test_narration.py "YOUR NARRATION TEXT HERE"
```

For example:
```bash
python tests/test_narration.py "TUITION FEE PAYMENT FOR UNIVERSITY OF TECHNOLOGY"
```

With a specific SWIFT message type:
```bash
python tests/test_narration.py "INTERBANK TRANSFER FOR LIQUIDITY MANAGEMENT" --message-type MT202
```

### Interactive Testing

```bash
python tests/interactive_test.py
```

### Comprehensive Testing

```bash
python tests/test_improvements.py --test all
```

You can also test specific aspects:
```bash
python tests/test_improvements.py --test education
python tests/test_improvements.py --test diversity
python tests/test_improvements.py --test performance
```

### SWIFT Message Testing

```bash
python -m unittest tests.test_swift_messages
```

### Problematic Cases Testing

```bash
python tests/test_problematic_cases.py
```

### Purpose Code Testing

```bash
# Test a specific purpose code
python tests/test_purpose_codes.py --purpose-code EDUC

# Test a specific category purpose code
python tests/test_purpose_codes.py --category-purpose-code FCOL

# Test all purpose codes
python tests/test_purpose_codes.py --test-all-purpose-codes

# Test all category purpose codes
python tests/test_purpose_codes.py --test-all-category-purpose-codes
```

For more information about purpose code testing, see [Purpose Code Testing Guide](purpose_code_testing.md).

### Custom Narration Testing

```bash
# Test a custom narration
python tests/test_custom_narrations.py --narration "PAYMENT FOR UNIVERSITY TUITION" --expected-purpose-code EDUC --expected-category-purpose-code FCOL

# Batch testing with a CSV file
python tests/test_custom_narrations.py --file tests/sample_narrations.csv --output tests/results.csv
```

### Running All Tests

```bash
python tests/run_all_tests.py
```

You can also run specific test groups:
```bash
python tests/run_all_tests.py --tests unit
python tests/run_all_tests.py --tests improvements
python tests/run_all_tests.py --tests swift
python tests/run_all_tests.py --tests problematic
```

## Test Results

Test results are saved in the `test_results` directory by default. You can specify a different directory with the `--output-dir` parameter:

```bash
python tests/run_all_tests.py --output-dir my_test_results
```
