# Purpose Code Testing Guide

This guide provides instructions on how to test purpose codes and category purpose codes using the new test scripts.

## Table of Contents

1. [Test Scripts](#test-scripts)
2. [Testing Purpose Codes](#testing-purpose-codes)
3. [Testing Category Purpose Codes](#testing-category-purpose-codes)
4. [Testing Custom Narrations](#testing-custom-narrations)
5. [Batch Testing](#batch-testing)
6. [Example Commands](#example-commands)

## Test Scripts

The following test scripts are available for testing purpose codes and category purpose codes:

- `test_purpose_codes.py`: Test specific purpose codes and category purpose codes with generated narrations
- `test_custom_narrations.py`: Test custom narrations with expected purpose codes and category purpose codes

## Testing Purpose Codes

To test a specific purpose code:

```bash
python tests/test_purpose_codes.py --purpose-code EDUC
```

This will generate a narration related to the purpose code and test if the classifier correctly identifies it.

To test all purpose codes:

```bash
python tests/test_purpose_codes.py --test-all-purpose-codes
```

## Testing Category Purpose Codes

To test a specific category purpose code:

```bash
python tests/test_purpose_codes.py --category-purpose-code FCOL
```

This will generate a narration related to the category purpose code and test if the classifier correctly maps it.

To test all category purpose codes:

```bash
python tests/test_purpose_codes.py --test-all-category-purpose-codes
```

## Testing Custom Narrations

To test a custom narration:

```bash
python tests/test_custom_narrations.py --narration "PAYMENT FOR UNIVERSITY TUITION AND DORMITORY FEES" --expected-purpose-code EDUC --expected-category-purpose-code FCOL
```

This will test if the classifier correctly identifies the purpose code and category purpose code for the given narration.

## Batch Testing

To test multiple narrations from a CSV file:

```bash
python tests/test_custom_narrations.py --file tests/sample_narrations.csv --output tests/results.csv
```

The CSV file should have the following columns:
- `narration`: The narration text to test
- `expected_purpose_code`: The expected purpose code (optional)
- `expected_category_purpose_code`: The expected category purpose code (optional)
- `message_type`: The SWIFT message type (optional)

## Example Commands

Here are some example commands for testing purpose codes and category purpose codes:

```bash
# Test a specific purpose code
python tests/test_purpose_codes.py --purpose-code EDUC

# Test a specific category purpose code
python tests/test_purpose_codes.py --category-purpose-code FCOL

# Test a custom narration
python tests/test_custom_narrations.py --narration "PAYMENT FOR UNIVERSITY TUITION AND DORMITORY FEES" --expected-purpose-code EDUC --expected-category-purpose-code FCOL

# Test with a specific message type
python tests/test_custom_narrations.py --narration "INTERBANK TRANSFER FOR LIQUIDITY MANAGEMENT" --expected-purpose-code INTC --expected-category-purpose-code INTC --message-type MT202

# Batch testing
python tests/test_custom_narrations.py --file tests/sample_narrations.csv --output tests/results.csv

# Test all purpose codes and save results
python tests/test_purpose_codes.py --test-all-purpose-codes --output tests/purpose_code_results.csv

# Test all category purpose codes and save results
python tests/test_purpose_codes.py --test-all-category-purpose-codes --output tests/category_purpose_code_results.csv
```

## Available Purpose Codes

The purpose codes are defined in `data/purpose_codes.json`. Here are some common purpose codes:

- `EDUC`: Education
- `SALA`: Salary Payment
- `SCVE`: Purchase of Services
- `INSU`: Insurance Premium
- `TAXS`: Tax Payment
- `LOAN`: Loan
- `DIVD`: Dividend Payment
- `INTC`: Intra Company Payment
- `BONU`: Bonus Payment
- `GDDS`: Purchase Sale of Goods

## Available Category Purpose Codes

The category purpose codes are defined in `data/category_purpose_codes.json`. Here are some common category purpose codes:

- `FCOL`: Fee Collection
- `SALA`: Salary Payment
- `SUPP`: Supplier Payment
- `INSU`: Insurance
- `TAXS`: Tax Payment
- `LOAN`: Loan
- `DIVI`: Dividend Payment
- `INTC`: Intra-Company Payment
- `BONU`: Bonus Payment
- `GDDS`: Purchase Sale of Goods

## Related Documentation

For more information about testing, see:

- [Testing Guide](testing_guide.md): Comprehensive testing guide
- [Test Execution Guide](test_execution_guide.md): Detailed instructions for running tests
- [Test README](test_readme.md): Overview of all tests
