"""
Command-line scripts for the purpose-classifier package.

This package contains scripts for:
- Predicting purpose codes from narrations (predict.py)
- Processing MT messages (process_mt_messages.py)
- Analyzing MT messages (analyze_mt_messages.py)
- Summarizing narrations (narration_summary.py)
- Downloading model files (model_downloader.py)
- Demonstrating the package (demo.py)
- Inspecting model properties (inspect_model.py)
"""

# We don't import the scripts directly to avoid circular imports
# when running with python -m purpose_classifier.scripts.X
#
# Instead, users should import specific modules as needed:
# from purpose_classifier.scripts import predict
#
# Or run them directly:
# python -m purpose_classifier.scripts.predict


