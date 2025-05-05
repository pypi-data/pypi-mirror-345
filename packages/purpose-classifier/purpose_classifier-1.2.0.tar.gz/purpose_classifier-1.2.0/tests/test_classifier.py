import unittest
import os
import sys

# Add the parent directory to the path so we can import the purpose_classifier package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from purpose_classifier.lightgbm_classifier import LightGBMPurposeClassifier

class TestPurposeClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = LightGBMPurposeClassifier(model_path='models/combined_model.pkl')

    def test_predict(self):
        result = self.classifier.predict("PAYMENT FOR CONSULTING SERVICES")
        self.assertIsNotNone(result)
        self.assertIn('purpose_code', result)
        self.assertIn('confidence', result)

    def test_batch_predict(self):
        narrations = [
            "PAYMENT FOR CONSULTING SERVICES",
            "TUITION PAYMENT FOR UNIVERSITY"
        ]
        results = self.classifier.batch_predict(narrations)
        self.assertEqual(len(results), 2)

if __name__ == '__main__':
    unittest.main()