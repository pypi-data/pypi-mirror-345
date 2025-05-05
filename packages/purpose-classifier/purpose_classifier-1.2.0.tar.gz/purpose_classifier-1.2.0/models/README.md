# Purpose Code Classifier Models

This directory contains the trained models for the purpose code classifier.

## Main Model Files

The following model files are required but are not included in the GitHub repository or PyPI package due to their large size:

- **combined_model.pkl**: The main combined model used for predictions. This model includes all enhancements and is the one referenced in the code.
- **combined_model.pkl.pt**: The PyTorch version of the main model, used for BERT-based predictions.
- **word_embeddings.pkl**: Word embeddings used for semantic pattern matching.

## Obtaining the Model Files

You can obtain the model files in one of the following ways:

1. **Using the model_downloader script**:
   ```
   python -m purpose_classifier.scripts.model_downloader
   ```
   This script will attempt to download the model files from the repository or locate them in your local environment.

2. **Manual download**:
   The model files can be downloaded from the project's release page or requested from the package maintainer.

3. **Local copy**:
   If you have the model files locally, place them in this directory (`models/`).

## Backup Models

The `backup` directory contains older versions of the models and intermediate models used during development:

- **combined_model_enhanced.pkl**: Enhanced version of the combined model
- **enhanced_combined_model.pkl**: Another enhanced version of the combined model
- **enhanced_lightgbm_classifier.pkl**: The enhanced LightGBM classifier model
- **enhanced_retrained_model.pkl**: Enhanced model retrained with additional data
- **enhanced_synthetic_model.pkl**: Enhanced model trained with synthetic data
- **mt_enhanced_model.pkl**: Model enhanced with message type context
- **retrained_model.pkl**: Model retrained with additional data

## Model Structure

The models are stored as Python dictionaries with the following keys:

- **vectorizer**: The TF-IDF vectorizer used for text preprocessing
- **label_encoder**: The label encoder used for purpose code encoding
- **model**: The LightGBM model
- **params**: The parameters used for training
- **feature_names**: The names of the features used for training
- **training_args**: The arguments used for training
- **created_at**: The timestamp when the model was created
- **fallback_rules**: The fallback rules used for enhancing predictions
- **enhanced_predict**: Flag indicating whether enhanced prediction is enabled
- **enhanced_category_purpose**: Flag indicating whether enhanced category purpose mapping is enabled
- **enhancement_info**: Information about the enhancements applied to the model

## Usage

To use the main model:

```python
from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier

# Initialize the classifier with the combined model
classifier = LightGBMPurposeClassifier(model_path='models/combined_model.pkl')

# Make a prediction
result = classifier.predict("PAYMENT FOR CONSULTING SERVICES")
print(f"Purpose Code: {result['purpose_code']}")
print(f"Confidence: {result['confidence']:.2f}")
```
