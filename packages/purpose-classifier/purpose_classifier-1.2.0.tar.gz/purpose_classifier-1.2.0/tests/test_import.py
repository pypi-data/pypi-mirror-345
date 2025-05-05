"""
Test that the package can be imported.
"""

def test_import():
    """Test that the package can be imported."""
    import purpose_classifier
    assert purpose_classifier.__version__ == "1.2.0"
    
    # Test importing main classes
    from purpose_classifier import LightGBMPurposeClassifier
    from purpose_classifier import InterbankDomainEnhancer
    from purpose_classifier.utils.message_parser import detect_message_type, extract_narration
    from purpose_classifier.utils.preprocessor import TextPreprocessor
    
    # Make sure they're the right type
    assert LightGBMPurposeClassifier.__name__ == "LightGBMPurposeClassifier"
    assert InterbankDomainEnhancer.__name__ == "InterbankDomainEnhancer"
    assert callable(detect_message_type)
    assert callable(extract_narration)
    assert TextPreprocessor.__name__ == "TextPreprocessor"
