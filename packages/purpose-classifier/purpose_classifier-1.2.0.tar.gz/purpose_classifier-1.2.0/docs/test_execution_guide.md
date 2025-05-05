# Purpose Code Classifier Test Execution Guide

This guide explains how to run tests for the purpose code classifier model to validate its performance.

## Prerequisites

- Python 3.8 or higher
- Virtual environment (venv) activated
- Required packages installed (see requirements.txt)

## Test Types

The purpose code classifier can be tested using several methods:

1. **Demo Test**: Tests the model with standard test cases
2. **Advanced Narrations Test**: Tests the model with complex narrations
3. **SWIFT Message Test**: Tests the model with different SWIFT message types (MT103, MT202, MT202COV, MT205, MT205COV)

## Running the Demo Test

The demo test runs the model against a set of standard test cases to validate basic functionality.

```bash
cd C:\Projects\purpose-classifier-package
python demo.py
```

This will output the results for each test case, showing the predicted purpose code, confidence, category purpose code, and category confidence.

## Running the Advanced Narrations Test

The advanced narrations test runs the model against a set of complex narrations to validate its performance on edge cases.

```bash
cd C:\Projects\purpose-classifier-package
python tests\test_combined_model.py --model models\combined_model.pkl --file tests\advanced_narrations.csv --output tests\advanced_narrations_results.csv
```

This will output the results for each narration and save them to the specified output file.

## Running the SWIFT Message Test

The SWIFT message test runs the model against a set of narrations with different SWIFT message types to validate its message type context awareness.

```bash
cd C:\Projects\purpose-classifier-package
python tests\test_combined_model.py --model models\combined_model.pkl --file tests\swift_message_narrations.csv --output tests\swift_message_results.csv
```

This will output the results for each narration and save them to the specified output file.

## Analyzing Test Results

The test results can be analyzed to evaluate the model's performance:

1. **Classification Accuracy**: Check if the predicted purpose codes match the expected purpose codes
2. **Confidence Levels**: Check if the confidence levels are high (> 0.90) for most predictions
3. **Category Purpose Code Mappings**: Check if the category purpose codes are correctly mapped
4. **Message Type Context Awareness**: Check if the model correctly handles different message types
5. **Special Case Handling**: Check if the model correctly handles special cases

## Expected Results

The enhanced purpose code classifier model should achieve:

- 100% accuracy on advanced narrations test set
- 100% accuracy on SWIFT message narrations test set
- High confidence levels (> 0.90) for most predictions
- Correct category purpose code mappings for all purpose codes
- Correct handling of all special cases

## Troubleshooting

If the tests fail or show unexpected results:

1. Check if the model file exists and is correctly specified
2. Check if the test file exists and is correctly specified
3. Check if the virtual environment is activated
4. Check if all required packages are installed
5. Check if the model has been enhanced with the latest enhancements

## Backup and Recovery

Before running tests or applying enhancements, it's recommended to back up the model:

```bash
cd C:\Projects\purpose-classifier-package
copy models\combined_model.pkl models\backup\combined_model_backup_<date>.pkl
```

To restore from a backup:

```bash
cd C:\Projects\purpose-classifier-package
copy models\backup\combined_model_backup_<date>.pkl models\combined_model.pkl
```

## Conclusion

By following this guide, you can run tests to validate the performance of the purpose code classifier model and ensure it meets the expected standards.
