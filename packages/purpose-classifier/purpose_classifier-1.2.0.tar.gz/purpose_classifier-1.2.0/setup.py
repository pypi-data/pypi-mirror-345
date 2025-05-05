from setuptools import setup, find_packages
import os
import re

# Read version from __init__.py
with open(os.path.join("purpose_classifier", "__init__.py"), encoding="utf-8") as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="purpose-classifier",
    version=version,
    author="Solchos",
    author_email="solchos@gmail.com",
    description="A high-accuracy machine learning system for classifying purpose codes and category purpose codes from SWIFT message narrations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/solchos/purpose-classifier-package",
    packages=find_packages(exclude=["tests*", "scripts*", "examples*", "MT_messages*", "*.egg-info", "data*", "models*", "logs*", "evaluation*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "scikit-learn>=1.0.2",
        "pandas>=1.4.2",
        "numpy>=1.22.3",
        "nltk>=3.7",
        "joblib>=1.1.0",
        "matplotlib>=3.5.2",
        "tqdm>=4.64.0",
        "regex>=2022.4.24",
        "lightgbm>=3.3.2",
        "tabulate>=0.8.9",
        "torch>=1.10.0",
        "transformers>=4.18.0"
    ],
    entry_points={
        "console_scripts": [
            # Main scripts
            "predict-purpose=purpose_classifier.scripts.predict:main",
            "process-mt-messages=purpose_classifier.scripts.process_mt_messages:main",
            "analyze-mt-messages=purpose_classifier.scripts.analyze_mt_messages:main",
            "narration-summary=purpose_classifier.scripts.narration_summary:main",

            # Additional scripts
            "download-purpose-models=purpose_classifier.scripts.model_downloader:main",
            "purpose-demo=purpose_classifier.scripts.demo:main",
            "inspect-purpose-model=purpose_classifier.scripts.inspect_model:main",
        ],
    },
    include_package_data=True,
)