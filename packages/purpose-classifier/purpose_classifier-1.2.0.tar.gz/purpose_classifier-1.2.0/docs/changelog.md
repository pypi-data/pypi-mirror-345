# Changelog

All notable changes to the Purpose Classifier package will be documented in this file.

## [1.2.0] - 2025-04-23

### Added
- Combined model implementation using LightGBM
- Improved domain enhancers for better accuracy
- Project cleanup and organization

### Improved
- Overall accuracy on SWIFT messages increased to 97.6% (244/250 correct predictions)
- MT103 accuracy increased to 98.0% (from 96.0%)
- MT202 accuracy increased to 100.0% (from 98.0%)
- SCVE (services) accuracy increased to 98.0% (from 96.0%)

### Changed
- Switched to LightGBMPurposeClassifier as the main classifier implementation
- Simplified project structure by moving unused files to archive
- Updated documentation to reflect current project stack

## [1.1.0] - 2023-04-23

### Added
- Support for all ISO20022 purpose codes and category purpose codes
- Synthetic data generation script for training data augmentation
- Enhanced rules for handling edge cases:
  - Software as GDDS when it's part of a purchase order
  - Better distinction between vehicle insurance and vehicle purchase
  - Improved detection of tax payments related to payroll
- Combined model that leverages both rule-based enhancers and machine learning

### Improved
- Overall accuracy increased to 97.2% (from 94.0%)
- GDDS (goods) accuracy increased to 100.0% (from 88.0%)
- TAXS (tax) accuracy increased to 100.0% (from 92.0%)
- SCVE (services) accuracy increased to 96.0% (from 92.0%)
- MT202COV accuracy increased to 96.0% (from 90.0%)
- MT205COV accuracy increased to 98.0% (from 90.0%)

### Fixed
- Fixed misclassification of software-related goods as services
- Fixed misclassification of vehicle insurance as goods
- Fixed misclassification of payroll tax as salary

## [1.0.0] - 2023-03-15

### Added
- Initial release of the Purpose Classifier package
- Support for basic ISO20022 purpose codes
- LightGBM-based classification model
- Rule-based enhancers for improved accuracy
- Batch processing capability
