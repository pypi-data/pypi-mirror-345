# Message Type Enhancer Improvements

## Overview

This document describes the improvements made to the message type enhancer to better handle MT202, MT202COV, MT205, and MT205COV message types using semantic pattern matching.

## Changes Made

1. **Semantic Pattern Matching**: We've updated the message type enhancer to use semantic pattern matching for MT202, MT202COV, MT205, and MT205COV message types. This approach focuses on understanding the semantic meaning of the narration rather than relying on exact string matches.

2. **Direct Category Purpose Code Mapping**: We've implemented a direct mapping from purpose codes to category purpose codes in the `_determine_category_purpose` method. This ensures that the category purpose code is always set correctly based on the purpose code, with high confidence.

3. **MT202 Message Type Handling**: We've improved the handling of MT202 messages by using semantic patterns to detect interbank, treasury, forex, settlement, and cash management patterns.

4. **MT202COV Message Type Handling**: We've improved the handling of MT202COV messages by using semantic patterns to detect treasury, settlement, forex, crossborder, and trade patterns.

5. **MT205 Message Type Handling**: We've improved the handling of MT205 messages by using semantic patterns to detect securities, investment, treasury, cash, and interbank patterns.

6. **MT205COV Message Type Handling**: We've improved the handling of MT205COV messages by using semantic patterns to detect securities, investment, treasury, crossborder, cash, and interbank patterns.

## Results

The changes have improved the consistency of the purpose code classifier, especially for category purpose code mapping. The semantic pattern matching approach ensures that the classifier can handle a wide variety of narrations without relying on exact matches.

However, the accuracy for MT202, MT202COV, MT205, and MT205COV message types is still lower than desired. This is because these message types are more complex and have less standardized narrations compared to MT103 messages.

## Future Improvements

1. **Enhance Semantic Pattern Matching**: Further improve the semantic pattern matching by adding more patterns and refining existing ones.

2. **Retrain the Model**: Retrain the model with more examples of MT202, MT202COV, MT205, and MT205COV messages to improve the base accuracy.

3. **Add More Enhancers**: Create specialized enhancers for specific domains that are common in these message types, such as securities, treasury, and forex.

4. **Improve Test Data**: Create more realistic test data for these message types to better evaluate the classifier's performance.
