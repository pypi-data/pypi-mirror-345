Purpose Classifier
=================

A high-accuracy machine learning system for classifying purpose codes and category purpose codes from SWIFT message narrations.

Features
--------

- Predicts ISO20022 purpose codes and category purpose codes from payment narrations
- Supports multiple SWIFT message types (MT103, MT202, MT202COV, MT205, MT205COV)
- Uses a combination of machine learning and domain-specific enhancers
- Provides high confidence predictions with detailed explanations
- Includes utilities for parsing MT messages and extracting narrations
- Command-line tools for batch processing and analysis

Installation
-----------

Install from PyPI:

.. code-block:: bash

    pip install purpose-classifier

Or install from source:

.. code-block:: bash

    git clone https://github.com/solchos/purpose-classifier-package.git
    cd purpose-classifier-package
    pip install -e .

Usage
-----

Basic usage:

.. code-block:: python

    from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier

    # Initialize classifier
    classifier = LightGBMPurposeClassifier()
    classifier.load()

    # Make prediction
    result = classifier.predict("SALARY PAYMENT APRIL 2023")
    print(f"Purpose Code: {result['purpose_code']}")
    print(f"Category Purpose Code: {result['category_purpose_code']}")
    print(f"Confidence: {result['confidence']:.2f}")

Command-line usage:

.. code-block:: bash

    # Predict purpose code from text
    predict-purpose --text "SALARY PAYMENT APRIL 2023" --verbose

    # Process MT messages
    process-mt-messages --messages-dir path/to/messages --verbose

    # Analyze MT messages
    analyze-mt-messages

Documentation
------------

For full documentation, visit the GitHub repository: https://github.com/solchos/purpose-classifier-package

License
-------

MIT License
