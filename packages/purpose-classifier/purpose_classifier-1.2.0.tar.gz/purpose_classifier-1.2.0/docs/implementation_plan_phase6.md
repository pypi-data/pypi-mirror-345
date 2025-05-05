# Implementation Plan - Phase 6: Accuracy Improvement

## Overview

This document outlines the implementation plan for Phase 6 of the purpose classifier project, which focuses on improving the accuracy of the classifier, particularly for MT103 messages and specific purpose codes (LOAN, DIVD) that currently have low accuracy.

## Current Issues

Based on our analysis, we've identified several key issues that need to be addressed:

1. **MT103 Classification Issues**:
   - MT103 messages are incorrectly classified as INTE (Interest) when they should be SCVE (Services) or GDDS (Goods)
   - Overall accuracy for MT103 messages is only 52%

2. **LOAN vs LOAR Classification Issues**:
   - Only 36% accuracy for LOAN purpose code (9/25 correct)
   - Many LOAN transactions are incorrectly classified as LOAR

3. **DIVD vs DIVI Classification Issues**:
   - Only 60% accuracy for DIVD purpose code (15/25 correct)
   - Many DIVD transactions are incorrectly classified as DIVI

4. **Category Purpose Code Mapping Issues**:
   - DIVD category purpose code: 0% accuracy (0/17)
   - SUPP category purpose code: 0% accuracy (0/28)

5. **Confidence Threshold Issues**:
   - The base model is producing very high confidence scores (0.99) for incorrect predictions
   - Enhancers skip enhancement when confidence is high (typically >= 0.7 or 0.8)
   - This prevents enhancers from correcting these predictions

## Implementation Steps

### 1. Adjust Confidence Thresholds

**File**: `scripts/fix_confidence_thresholds.py`

This script adjusts the confidence thresholds in the classifier and enhancers to allow enhancers to correct high-confidence errors.

**Changes**:
- Increase the high confidence threshold in the classifier from 0.65 to 0.85
- Reduce the confidence thresholds in the enhancer manager:
  - Highest priority: 0.75 -> 0.65
  - High priority: 0.80 -> 0.70
  - Medium priority: 0.85 -> 0.75
  - Low priority: 0.90 -> 0.80
- Reduce the min_confidence in MODEL_SETTINGS from 0.60 to 0.40

**Files to Update**:
- `purpose_classifier/classifier.py`
- `purpose_classifier/domain_enhancers/enhancer_manager.py`
- `purpose_classifier/config/settings.py`

### 2. Improve MT103 Message Processing

**File**: `scripts/improve_mt103_classification.py`

This script enhances the classification of MT103 messages, particularly for services (SCVE) and goods (GDDS) that are incorrectly classified as interest (INTE).

**Changes**:
- Add more patterns for services in MT103 messages
- Add more patterns for goods in MT103 messages
- Enhance the message type enhancer for MT103 messages
- Enhance the services enhancer for MT103 messages
- Enhance the goods enhancer for MT103 messages

**Files to Update**:
- `purpose_classifier/domain_enhancers/message_type_enhancer_semantic.py`
- `purpose_classifier/domain_enhancers/services_enhancer_semantic.py`
- `purpose_classifier/domain_enhancers/goods_enhancer_semantic.py`

### 3. Improve LOAN vs LOAR Classification

**File**: `scripts/improve_loan_classification.py`

This script enhances the classification of loan-related transactions, distinguishing between loan disbursements (LOAN) and loan repayments (LOAR).

**Changes**:
- Define clearer patterns for loan disbursements
- Define clearer patterns for loan repayments
- Enhance the targeted enhancer for loan-related transactions

**Files to Update**:
- `purpose_classifier/domain_enhancers/targeted_enhancer_semantic.py`

### 4. Improve DIVD vs DIVI Classification

**File**: `scripts/improve_dividend_classification.py`

This script enhances the classification of dividend-related transactions, ensuring proper mapping between DIVD purpose code and DIVI category purpose code.

**Changes**:
- Define clearer patterns for dividend payments
- Enhance the targeted enhancer for dividend-related transactions
- Fix the category purpose code mapping for DIVD

**Files to Update**:
- `purpose_classifier/domain_enhancers/targeted_enhancer_semantic.py`
- `purpose_classifier/utils/category_purpose_mapper.py`

### 5. Improve Category Purpose Code Mapping

**File**: `scripts/improve_category_purpose_mapping.py`

This script enhances the mapping between purpose codes and category purpose codes, particularly focusing on DIVD->DIVI and SCVE->SUPP mappings.

**Changes**:
- Define improved direct mappings between purpose codes and category purpose codes
- Test the improved mappings with problematic cases
- Save the improved mappings to a file for reference

**Files to Update**:
- `purpose_classifier/utils/category_purpose_mapper.py`

### 6. Test the Improvements

**File**: `scripts/test_improvements.py`

This script tests the improvements to the purpose classifier by running a series of tests on problematic cases.

**Changes**:
- Define test cases for problematic areas
- Run the tests and collect results
- Calculate accuracy metrics
- Save results to CSV

## Expected Outcomes

After implementing these changes, we expect to see the following improvements:

1. **MT103 Classification**:
   - Increase accuracy from 52% to at least 75%
   - Correctly classify service-related (SCVE) and goods-related (GDDS) transactions

2. **LOAN vs LOAR Classification**:
   - Increase LOAN accuracy from 36% to at least 80%
   - Correctly distinguish between loan disbursements and repayments

3. **DIVD vs DIVI Classification**:
   - Increase DIVD accuracy from 60% to at least 85%
   - Correctly map DIVD purpose code to DIVI category purpose code

4. **Category Purpose Code Mapping**:
   - Increase DIVD category purpose code accuracy from 0% to at least 90%
   - Increase SUPP category purpose code accuracy from 0% to at least 80%

5. **Overall Accuracy**:
   - Increase overall accuracy from 78% to at least 85%
   - Reduce OTHR code usage to 0%

## Testing and Validation

To validate the improvements, we will:

1. Run the `test_improvements.py` script to test the changes on problematic cases
2. Run the existing test suite to ensure we haven't broken anything
3. Perform a comprehensive test on a larger dataset to measure overall accuracy

## Timeline

- Day 1: Implement confidence threshold adjustments and MT103 message processing improvements
- Day 2: Implement LOAN vs LOAR and DIVD vs DIVI classification improvements
- Day 3: Implement category purpose code mapping improvements and test all changes
- Day 4: Review results, make any necessary adjustments, and finalize documentation

## Conclusion

By implementing these changes, we aim to address the specific issues identified in our analysis and improve the overall accuracy of the purpose classifier. The focus on MT103 messages and specific purpose codes (LOAN, DIVD) will help us reach our target of 90% accuracy.
