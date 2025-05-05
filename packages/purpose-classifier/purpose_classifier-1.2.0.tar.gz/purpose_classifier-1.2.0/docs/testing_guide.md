# Purpose Code Classifier Testing Guide

This guide provides instructions on how to test the purpose code classifier using various methods, including command-line tests and other testing approaches.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Command-Line Testing](#command-line-testing)
   - [Single Narration Testing](#single-narration-testing)
   - [Interactive Testing](#interactive-testing)
   - [Message Type Testing](#message-type-testing)
   - [Example Narrations](#example-narrations)
3. [Comprehensive Testing](#comprehensive-testing)
   - [Education Classification Testing](#education-classification-testing)
   - [Top Predictions Diversity Testing](#top-predictions-diversity-testing)
   - [Processing Time Testing](#processing-time-testing)
4. [Batch Testing](#batch-testing)
5. [MT Message Testing](#mt-message-testing)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

Before running any tests, ensure you have:

1. Activated your Python virtual environment:
   ```
   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

2. Installed all required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Verified that the model files are present in the `models` directory:
   ```
   dir models
   ```
   You should see `combined_model.pkl` in the output.

## Command-Line Testing

### Single Narration Testing

The simplest way to test the purpose code classifier is to use the `test_narration.py` script, which takes a narration as input and outputs the purpose code and category purpose code.

```bash
python test_narration.py "YOUR NARRATION TEXT HERE"
```

For example:
```bash
python test_narration.py "TUITION FEE PAYMENT FOR UNIVERSITY OF TECHNOLOGY"
```

Output:
```
Classifying narration: "TUITION FEE PAYMENT FOR UNIVERSITY OF TECHNOLOGY"

Results:
Purpose Code: EDUC (Confidence: 0.9900)
Category Purpose Code: FCOL (Confidence: 0.9900)

Top Predictions:
  EDUC: 0.9900
  SCVE: 0.0500
  SERV: 0.0300

Processing Time: 0.0000 seconds
```

### Interactive Testing

For testing multiple narrations in a single session, use the `interactive_test.py` script:

```bash
python interactive_test.py
```

This will start an interactive session where you can enter narrations one by one and see the results:

```
Purpose Code Classifier Interactive Test
================================================================================
Enter a narration to classify, or type 'exit' to quit.
You can specify a message type by prefixing with 'MT103:', 'MT202:', etc.
Example: MT103:PAYMENT FOR CONSULTING SERVICES
================================================================================

Enter narration (or 'exit'): TUITION FEE PAYMENT FOR UNIVERSITY OF TECHNOLOGY

Classifying: "TUITION FEE PAYMENT FOR UNIVERSITY OF TECHNOLOGY"

Results:
Purpose Code: EDUC (Confidence: 0.9900)
Category Purpose Code: FCOL (Confidence: 0.9900)

Top Predictions:
  EDUC: 0.9900
  SCVE: 0.0500
  SERV: 0.0300

Processing Time: 0.0000 seconds
--------------------------------------------------------------------------------
Enter narration (or 'exit'): exit
Exiting...
```

### Message Type Testing

To test with a specific SWIFT message type, use the `--message-type` parameter:

```bash
python test_narration.py "INTERBANK TRANSFER FOR LIQUIDITY MANAGEMENT" --message-type MT202
```

Output:
```
Classifying narration: "INTERBANK TRANSFER FOR LIQUIDITY MANAGEMENT"
Using message type: MT202

Results:
Purpose Code: INTC (Confidence: 0.9500)
Category Purpose Code: INTC (Confidence: 0.9000)

Top Predictions:
  INTC: 0.4167
  CASH: 0.0658
  TRAD: 0.0341
  GDDS: 0.0325
  SERV: 0.0300

Processing Time: 2.5581 seconds
```

In the interactive mode, you can specify the message type by prefixing the narration with the message type followed by a colon:

```
Enter narration (or 'exit'): MT202:INTERBANK TRANSFER FOR LIQUIDITY MANAGEMENT
```

### Example Narrations

Here are some example narrations you can use for testing different purpose codes:

#### Education
```bash
python test_narration.py "TUITION FEE PAYMENT FOR UNIVERSITY OF TECHNOLOGY"
python test_narration.py "SCHOOL FEES FOR JOHN SMITH - INTERNATIONAL SCHOOL - ACADEMIC YEAR 2025"
python test_narration.py "EDUCATION EXPENSES FOR TECHNICAL COLLEGE"
python test_narration.py "COURSE FEE PAYMENT - INTRODUCTION TO PROGRAMMING - ONLINE UNIVERSITY"
```

#### Salary and Compensation
```bash
python test_narration.py "SALARY PAYMENT FOR APRIL 2025"
python test_narration.py "PERFORMANCE BONUS PAYMENT FOR Q1 2025"
python test_narration.py "MONTHLY PAYROLL - EMPLOYEE ID 12345"
```

#### Financial Services
```bash
python test_narration.py "INTERBANK TRANSFER FOR LIQUIDITY MANAGEMENT" --message-type MT202
python test_narration.py "LOAN REPAYMENT - ACCOUNT 12345"
python test_narration.py "DIVIDEND PAYMENT FOR Q1 2025"
```

#### Other Services
```bash
python test_narration.py "PAYMENT FOR CONSULTING SERVICES INVOICE 12345"
python test_narration.py "INSURANCE PREMIUM PAYMENT FOR POLICY 67890"
python test_narration.py "TAX PAYMENT - INCOME TAX - Q1 2025"
```

#### Ambiguous Narrations
```bash
python test_narration.py "PAYMENT FOR INVOICE 12345"
python test_narration.py "PAYMENT FOR CONSULTING SERVICES AND EDUCATIONAL MATERIALS"
```

## Comprehensive Testing

For more comprehensive testing, use the `test_improvements.py` script, which tests various aspects of the classifier:

```bash
python scripts/test_improvements.py --test all
```

You can also test specific aspects:

### Education Classification Testing

```bash
python scripts/test_improvements.py --test education
```

This tests education-related narrations and measures:
- EDUC purpose code accuracy
- FCOL category purpose code accuracy
- Average confidence
- Average processing time

### Top Predictions Diversity Testing

```bash
python scripts/test_improvements.py --test diversity
```

This tests ambiguous narrations and measures:
- Number of top predictions
- Confidence gap between top predictions

### Processing Time Testing

```bash
python scripts/test_improvements.py --test performance
```

This tests various types of narrations and measures:
- Average processing time
- Processing time for different enhancement types

## Batch Testing

To test multiple narrations in batch mode, you can create a CSV file with narrations and use the following script:

```bash
python scripts/batch_test.py --input narrations.csv --output results.csv
```

The input CSV should have a column named 'narration' containing the narrations to test.

Example `narrations.csv`:
```
narration
"TUITION FEE PAYMENT FOR UNIVERSITY OF TECHNOLOGY"
"SALARY PAYMENT FOR APRIL 2025"
"PAYMENT FOR CONSULTING SERVICES INVOICE 12345"
```

## MT Message Testing

To test with actual SWIFT MT messages, use the MT message processing script:

```bash
python MT_messages/process_mt_messages.py --input mt_messages.txt --output mt_results.csv
```

Example MT message format:
```
:20:REFERENCE123
:32A:230425USD1000,00
:50K:/12345678
SENDER NAME
SENDER ADDRESS
:59:/87654321
BENEFICIARY NAME
BENEFICIARY ADDRESS
:70:TUITION FEE PAYMENT
FOR UNIVERSITY OF TECHNOLOGY
:71A:SHA
```

## Troubleshooting

### Model Loading Issues

If you encounter issues loading the model, check:

1. The model file exists in the expected location:
   ```bash
   dir models
   ```

2. The model file is not corrupted:
   ```bash
   python -c "import joblib; model = joblib.load('models/combined_model.pkl'); print('Model loaded successfully')"
   ```

### Slow Processing Time

If processing time is slow:

1. Check if you're using the latest version of the classifier with optimizations:
   ```bash
   python scripts/optimize_processing_time.py
   ```

2. Ensure you have enough memory available for the model.

### Incorrect Classifications

If you're getting unexpected classifications:

1. Check if the narration contains specific keywords that might trigger certain purpose codes.

2. Try with different variations of the narration to see if small changes affect the classification.

3. Use the interactive mode to see the top predictions and confidence scores, which can provide insights into why a particular classification was made.

### Other Issues

For other issues, check the logs for error messages:

```bash
python test_narration.py "YOUR NARRATION" 2> error.log
```

Then examine the error.log file for detailed error information.

## Related Documentation

For more information about testing, see:

- [Test Execution Guide](test_execution_guide.md): Detailed instructions for running tests
- [Purpose Code Testing Guide](purpose_code_testing.md): Guide for testing purpose codes
- [Test README](test_readme.md): Overview of all tests
- [Improvements](improvements.md): Information about recent improvements that may affect testing
