#!/usr/bin/env python3
"""
Script to download large model files that are not included in the package.
"""

import os
import sys
import argparse
import requests
from pathlib import Path
import hashlib
import logging
from tqdm import tqdm

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Model information
MODEL_INFO = {
    'combined_model.pkl': {
        'url': 'https://github.com/solchos/purpose-classifier-models/releases/download/v1.2.0/combined_model.pkl',
        'size': 256000000,  # Approximate size in bytes
        'md5': 'placeholder_md5_hash',  # Replace with actual MD5 hash
        'local_path': 'models/combined_model.pkl',
        'description': 'Main purpose classifier model (BERT-based)',
        'required': True,
    },
    'combined_model.pkl.pt': {
        'url': 'https://github.com/solchos/purpose-classifier-models/releases/download/v1.2.0/combined_model.pkl.pt',
        'size': 512000000,  # Approximate size in bytes
        'md5': 'placeholder_md5_hash',  # Replace with actual MD5 hash
        'local_path': 'models/combined_model.pkl.pt',
        'description': 'PyTorch version of the main purpose classifier model',
        'required': True,
    },
    'word_embeddings.pkl': {
        'url': 'https://github.com/solchos/purpose-classifier-models/releases/download/v1.2.0/word_embeddings.pkl',
        'size': 128000000,  # Approximate size in bytes
        'md5': 'placeholder_md5_hash',  # Replace with actual MD5 hash
        'local_path': 'models/word_embeddings.pkl',
        'description': 'Word embeddings for semantic pattern matching',
        'required': True,
    }
}

def get_models_dir():
    """Get the models directory path"""
    # Try to find the models directory relative to the package
    package_dir = Path(__file__).parent.parent
    models_dir = package_dir / 'models'

    # If not found, try to find it relative to the current working directory
    if not models_dir.exists():
        models_dir = Path.cwd() / 'models'

    # If still not found, create it in the current working directory
    if not models_dir.exists():
        logger.info(f"Creating models directory at {models_dir}")
        models_dir.mkdir(parents=True, exist_ok=True)

    return models_dir

def calculate_md5(file_path):
    """Calculate MD5 hash of a file"""
    md5_hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        # Read in chunks to handle large files
        for chunk in iter(lambda: f.read(4096), b''):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

def download_file(url, file_path, expected_size=None):
    """
    Download a file with progress bar

    Args:
        url: URL to download from
        file_path: Path to save the file
        expected_size: Expected file size in bytes

    Returns:
        True if download was successful, False otherwise
    """
    try:
        # Make sure the directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Start the download
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Get the file size from the response headers or use the expected size
        total_size = int(response.headers.get('content-length', 0)) or expected_size or 0

        # Create a progress bar
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=file_path.name)

        # Download the file in chunks
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))

        progress_bar.close()

        # Check if the download was complete
        if total_size > 0 and os.path.getsize(file_path) != total_size:
            logger.error(f"Downloaded file size does not match expected size: {file_path}")
            return False

        return True

    except Exception as e:
        logger.error(f"Error downloading {url}: {str(e)}")
        return False

def download_model(model_name, force=False):
    """
    Download or copy a model file

    Args:
        model_name: Name of the model file
        force: Whether to force download even if the file exists

    Returns:
        True if successful, False otherwise
    """
    if model_name not in MODEL_INFO:
        logger.error(f"Unknown model: {model_name}")
        return False

    models_dir = get_models_dir()
    model_path = models_dir / model_name
    model_info = MODEL_INFO[model_name]

    # Check if the file already exists
    if model_path.exists() and not force:
        logger.info(f"Model file already exists: {model_path}")
        print(f"Model file already exists: {model_path}")
        return True

    # Define possible local paths to check
    local_paths = [
        # Project models directory
        os.path.join("models", model_name),
        # Absolute path in project
        os.path.join("C:\\Projects\\purpose-classifier-package\\models", model_name),
        # Local path from model info
        model_info.get('local_path', '')
    ]

    # Try to find the model in local paths
    for local_path in local_paths:
        if os.path.exists(local_path):
            print(f"Found model at local path: {local_path}")
            logger.info(f"Found model at local path: {local_path}")

            # Create models directory if it doesn't exist
            os.makedirs(models_dir, exist_ok=True)

            # Copy the file to the models directory
            try:
                import shutil
                shutil.copy2(local_path, model_path)
                print(f"Copied model from {local_path} to {model_path}")
                logger.info(f"Copied model from {local_path} to {model_path}")
                return True
            except Exception as copy_error:
                logger.error(f"Error copying model: {str(copy_error)}")
                print(f"Error copying model: {str(copy_error)}")

    # If we get here, we couldn't find the model locally
    # Try to download from URL as a fallback
    try:
        print(f"Trying to download {model_name} from {model_info['url']}...")
        logger.info(f"Trying to download {model_name} from {model_info['url']}...")
        success = download_file(model_info['url'], model_path, model_info.get('size'))

        if success:
            print(f"Successfully downloaded {model_name}")
            logger.info(f"Successfully downloaded {model_name}")
            return True
    except Exception as e:
        logger.error(f"Error downloading {model_name}: {str(e)}")
        print(f"Error downloading {model_name}: {str(e)}")

    # If we get here, we couldn't find or download the model
    print("\nModel setup failed. Please follow these steps to manually set up the model:")
    print(f"1. Ensure the model file '{model_name}' is in the 'models' directory")
    print(f"2. The model should be located at: {model_path}")
    print("3. If you have the model file in another location, copy it to the path above")
    logger.info("\nModel setup failed. Please follow these steps to manually set up the model:")
    logger.info(f"1. Ensure the model file '{model_name}' is in the 'models' directory")
    logger.info(f"2. The model should be located at: {model_path}")
    logger.info("3. If you have the model file in another location, copy it to the path above")

    return False

def download_all_models(force=False):
    """
    Download all model files

    Args:
        force: Whether to force download even if the files exist

    Returns:
        True if all downloads were successful, False otherwise
    """
    success = True
    for model_name in MODEL_INFO:
        if not download_model(model_name, force):
            success = False

    return success

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Download large model files for the purpose classifier')

    parser.add_argument('--model', type=str, choices=list(MODEL_INFO.keys()), default=None,
                        help='Name of the model file to download')

    parser.add_argument('--force', action='store_true',
                        help='Force download even if the file exists')

    return parser.parse_args()

def main():
    """Main function"""
    args = parse_args()

    # Print welcome message
    print("\n=== Purpose Classifier Model Downloader ===\n")
    print("This tool will download or locate the model files needed by the purpose-classifier package.")
    print("The following models are required:")
    for model_name, info in MODEL_INFO.items():
        print(f"- {model_name} ({info.get('size', 'Unknown size') // 1000000} MB): {info.get('description', 'No description')}")
    print("\nChecking for models...\n")

    if args.model:
        # Download a specific model
        success = download_model(args.model, args.force)
    else:
        # Download all models
        success = download_all_models(args.force)

    if success:
        print("\n=== Success ===")
        print("All model files are available and ready to use.")
        print("You can now use the purpose-classifier package.")
        logger.info("All downloads completed successfully")
        return 0
    else:
        print("\n=== Warning ===")
        print("Some model files could not be downloaded or located.")
        print("The purpose-classifier package may not work correctly without these files.")
        print("Please see the instructions above for manually setting up the models.")
        logger.error("Some downloads failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
