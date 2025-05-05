# Purpose Classifier Models

This directory contains metadata about the models used by the purpose-classifier package.

## Model Files

The actual model files are too large to include in the package and must be downloaded separately:

- `combined_model.pkl` (~250MB): Main purpose classifier model
- `combined_model.pkl.pt` (~500MB): PyTorch version of the main model, used for BERT-based predictions
- `word_embeddings.pkl` (~120MB): Word embeddings for semantic pattern matching

## Downloading Models

You can download the models using the included `model_downloader.py` script:

```bash
# Download all models
python -m purpose_classifier.scripts.model_downloader

# Download a specific model
python -m purpose_classifier.scripts.model_downloader --model combined_model.pkl
```

## Model Locations

The package will look for models in the following locations, in order:

1. Inside the package models directory (if installed as a development package)
2. In the project root models directory
3. In the current working directory models subdirectory

## Model Versions

The current version of the models is 1.2.0, which corresponds to the package version.
