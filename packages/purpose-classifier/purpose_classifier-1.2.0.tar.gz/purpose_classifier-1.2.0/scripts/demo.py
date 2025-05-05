"""
Demonstration script for the Purpose Classifier package.
Shows how to load and use the pre-trained model for classifying financial transactions.
"""

import os
import sys
from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier

def main():
    # Create classifier instance
    print("Initializing LightGBM Purpose Classifier...")
    classifier = LightGBMPurposeClassifier(
        environment='development'
    )

    # Load the pre-trained model
    model_path = os.path.join('models', 'combined_model.pkl')
    if not os.path.exists(model_path):
        print(f"Error: Model file not found at {model_path}")
        return 1

    print(f"Loading model from {model_path}...")
    classifier.load(model_path)
    print("Model loaded successfully!")

    # Check if purpose codes and category purpose codes are loaded correctly
    print("\nChecking purpose codes and category purpose codes...")
    print(f"Purpose codes loaded: {len(classifier.purpose_codes)} codes")
    print(f"Category purpose codes loaded: {len(classifier.category_purpose_codes)} codes")

    # Load purpose codes and category purpose codes from JSON files
    iso20022_purpose_codes_path = os.path.join('data', 'iso20022_purpose_codes.json')
    category_purpose_codes_path = os.path.join('data', 'category_purpose_codes.json')

    # Import json module
    import json

    # Load purpose codes
    purpose_codes = {}

    # Load ISO20022 purpose codes if available
    if os.path.exists(iso20022_purpose_codes_path):
        print("Loading purpose codes from iso20022_purpose_codes.json...")
        with open(iso20022_purpose_codes_path, 'r') as f:
            iso_purpose_codes = json.load(f)
        print(f"Purpose codes from iso20022_purpose_codes.json: {len(iso_purpose_codes)} codes")

        # Merge with existing purpose codes
        purpose_codes.update(iso_purpose_codes)
        print(f"Total purpose codes after merging: {len(purpose_codes)} codes")

    # Load category purpose codes
    category_purpose_codes = {}
    if os.path.exists(category_purpose_codes_path):
        print("Loading category purpose codes from category_purpose_codes.json...")
        with open(category_purpose_codes_path, 'r') as f:
            category_purpose_codes = json.load(f)
        print(f"Category purpose codes from file: {len(category_purpose_codes)} codes")

    # Add any missing purpose codes if needed
    missing_purpose_codes = {
        'INVS': 'Investment and Securities',
        'GOVI': 'Government Insurance',
        'FXTR': 'Foreign Exchange Transaction'
    }

    # Add any missing category purpose codes if needed
    missing_category_codes = {
        'FXTR': 'Foreign Exchange Transaction'
    }

    # Update purpose codes with missing codes
    purpose_codes.update(missing_purpose_codes)

    # Update category purpose codes with missing codes
    category_purpose_codes.update(missing_category_codes)

    # Update the classifier's purpose codes and category purpose codes
    if purpose_codes:
        classifier.purpose_codes = purpose_codes
        print("Updated purpose codes in classifier")

    if category_purpose_codes:
        classifier.category_purpose_codes = category_purpose_codes
        print("Updated category purpose codes in classifier")

    # Sample narrations to test
    samples = [
        "TUITION PAYMENT FOR UNIVERSITY OF CALIFORNIA",
        "MONTHLY RENT PAYMENT FOR APARTMENT 301",
        "PAYMENT FOR SOFTWARE LICENSE RENEWAL",
        "CREDIT CARD PAYMENT - VISA ENDING 1234",
        "INTERBANK TRANSFER TO NOSTRO ACCOUNT",
        "PAYMENT FOR GOODS - INVOICE #12345",
        "INSURANCE PREMIUM FOR AUTO POLICY",
        "SALARY PAYMENT FOR MARCH 2025",
        "UTILITY BILL PAYMENT - ELECTRICITY",
        "FOREIGN EXCHANGE TRANSACTION USD/EUR"
    ]

    # Test each sample
    print("\nTesting sample narrations:")
    print("-" * 80)

    for i, sample in enumerate(samples, 1):
        print(f"\nSample {i}: {sample}")

        # Get prediction
        result = classifier.predict(sample)

        # Display results
        print(f"Purpose Code: {result.get('purpose_code', 'N/A')}")
        print(f"Description: {result.get('purpose_description', 'N/A')}")
        print(f"Confidence: {result.get('confidence', 0):.4f}")

        if 'category_purpose_code' in result:
            print(f"Category Purpose Code: {result.get('category_purpose_code', 'N/A')}")
            print(f"Category Description: {result.get('category_purpose_description', 'N/A')}")
            print(f"Category Confidence: {result.get('category_confidence', 0):.4f}")

        # Show domain enhancement if applied
        if 'enhancement_applied' in result:
            print(f"Enhancement Applied: {result.get('enhancement_applied')}")

        # Show top alternative codes if available
        if 'top_codes' in result:
            print("\nTop Alternative Codes:")
            for code, prob in result.get('top_codes', {}).items():
                print(f"  {code}: {prob:.4f}")

        print("-" * 80)

    return 0

if __name__ == "__main__":
    sys.exit(main())
