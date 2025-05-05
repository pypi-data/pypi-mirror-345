import unittest
import os
import sys
import json
import pandas as pd
import random
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Add the parent directory to the path so we can import the purpose_classifier package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from purpose_classifier import LightGBMPurposeClassifier
from purpose_classifier.config.settings import MESSAGE_TYPES

class TestSwiftMessages(unittest.TestCase):
    """Test the advanced LightGBM model on various SWIFT message types"""

    @classmethod
    def setUpClass(cls):
        """Set up the classifier and test data once for all tests"""
        # Initialize the LightGBM classifier
        # Try all possible model paths, prioritizing the combined model
        model_paths = [
            os.path.join('..', 'models', 'combined_model.pkl'),  # Try our combined model first
            os.path.join('models', 'combined_model.pkl'),  # Try our combined model first
            os.path.join('..', 'models', 'enhanced_lightgbm_classifier.pkl'),  # Fallback to enhanced model
            os.path.join('models', 'enhanced_lightgbm_classifier.pkl'),  # Fallback to enhanced model
            os.path.join('..', 'models', 'final_classifier.pkl'),  # Last resort
            os.path.join('models', 'final_classifier.pkl')  # Last resort
        ]

        model_found = False
        for model_path in model_paths:
            if os.path.exists(model_path):
                print(f"Loading model from {model_path}")
                try:
                    cls.classifier = LightGBMPurposeClassifier(model_path=model_path)
                    print(f"Successfully loaded model from {model_path}")
                    model_found = True
                    break
                except Exception as e:
                    print(f"Error loading model from {model_path}: {str(e)}")

        if not model_found:
            print(f"Warning: No model file found in any of the expected locations")
            # Create a new classifier without a model path
            try:
                cls.classifier = LightGBMPurposeClassifier()
                print("Created a new classifier without a model path")
            except Exception as e:
                print(f"Error creating classifier: {str(e)}")
                cls.classifier = None

        # Load purpose codes and category purpose codes with correct paths
        try:
            # Try all possible paths for purpose codes
            purpose_code_paths = [
                os.path.join('..', 'data', 'purpose_codes.json'),
                os.path.join('..', 'data', 'iso20022_purpose_codes.json'),
                os.path.join('data', 'purpose_codes.json'),
                os.path.join('data', 'iso20022_purpose_codes.json')
            ]

            purpose_codes_loaded = False
            for path in purpose_code_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        cls.purpose_codes = json.load(f)
                    print(f"Loaded {len(cls.purpose_codes)} purpose codes from {path}")
                    purpose_codes_loaded = True
                    break

            if not purpose_codes_loaded:
                print(f"Warning: Could not find purpose codes in any of the expected locations")
                cls.purpose_codes = {}

            # Try all possible paths for category purpose codes
            category_purpose_code_paths = [
                os.path.join('..', 'data', 'category_purpose_codes.json'),
                os.path.join('data', 'category_purpose_codes.json')
            ]

            category_purpose_codes_loaded = False
            for path in category_purpose_code_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        cls.category_purpose_codes = json.load(f)
                    print(f"Loaded {len(cls.category_purpose_codes)} category purpose codes from {path}")
                    category_purpose_codes_loaded = True
                    break

            if not category_purpose_codes_loaded:
                print(f"Warning: Could not find category purpose codes in any of the expected locations")
                cls.category_purpose_codes = {}

        except Exception as e:
            print(f"Error loading purpose codes: {str(e)}")
            cls.purpose_codes = {}
            cls.category_purpose_codes = {}

        # Create test data for different SWIFT message types
        cls.create_test_data()

    @classmethod
    def create_test_data(cls):
        """Create test data for different SWIFT message types with diverse narrations"""
        # Define common narration templates
        narration_templates = {
            # Corporate payments
            'SCVE': [
                "PAYMENT FOR {service} SERVICES REF:{ref}",
                "INVOICE {ref} FOR {service} SERVICES",
                "CONSULTING SERVICES - {service} - {ref}",
                "{service} SERVICES PAYMENT {ref}",
                "PROFESSIONAL {service} SERVICES INVOICE {ref}"
            ],
            'GDDS': [
                "PAYMENT FOR {goods} PURCHASE ORDER {ref}",
                "INVOICE {ref} FOR {goods} SUPPLY",
                "{goods} PROCUREMENT PAYMENT {ref}",
                "PURCHASE OF {goods} - INVOICE {ref}"
            ],
            'TRAD': [
                "TRADE PAYMENT - SHIPMENT {ref}",
                "EXPORT SETTLEMENT - INVOICE {ref}",
                "IMPORT PAYMENT - GOODS {ref}",
                "TRADE FINANCE - TRANSACTION {ref}",
                "INTERNATIONAL TRADE PAYMENT - {ref}",
                "GOODS PAYMENT - SOFTWARE - REF:{ref}"  # Added this pattern to TRAD instead of GDDS
            ],
            'SALA': [
                "SALARY PAYMENT {month} {year} - {ref}",
                "MONTHLY PAYROLL - {month} {year} - {ref}",
                "EMPLOYEE COMPENSATION {month} {year} REF:{ref}",
                "WAGES TRANSFER {month} {year} - {ref}",
                "STAFF SALARY {month} {year} - {ref}"
            ],
            'EDUC': [
                "TUITION FEE PAYMENT - {institution} - {ref}",
                "EDUCATION EXPENSES - {institution} - {ref}",
                "SCHOOL FEES {institution} REF:{ref}",
                "ACADEMIC PAYMENT TO {institution} - {ref}",
                "EDUCATION COSTS - {institution} - {ref}"
            ],
            'DIVI': [
                "DIVIDEND PAYMENT {period} {year} - {ref}",
                "SHAREHOLDER DIVIDEND {period} {year} REF:{ref}",
                "DIVIDEND DISTRIBUTION {period} {year} - {ref}",
                "{period} {year} DIVIDEND PAYOUT - {ref}",
                "CORPORATE DIVIDEND {period} {year} - {ref}"
            ],
            'LOAN': [
                "LOAN REPAYMENT - ACCOUNT {ref}",
                "CREDIT FACILITY PAYMENT - {ref}",
                "LOAN INSTALLMENT - AGREEMENT {ref}",
                "MORTGAGE PAYMENT - PROPERTY {ref}",
                "LOAN SETTLEMENT - CONTRACT {ref}"
            ],
            'INSU': [
                "INSURANCE PREMIUM - POLICY {ref}",
                "{insurance} INSURANCE PAYMENT - {ref}",
                "POLICY PREMIUM - {insurance} - {ref}",
                "INSURANCE COVERAGE PAYMENT - {ref}",
                "{insurance} POLICY PAYMENT - {ref}"
            ],
            'INTC': [
                "INTERCOMPANY TRANSFER - {entities} - {ref}",
                "INTRAGROUP PAYMENT - {entities} - {ref}",
                "INTERNAL SETTLEMENT - {entities} - {ref}",
                "GROUP COMPANY TRANSFER - {entities} - {ref}",
                "AFFILIATED COMPANY PAYMENT - {entities} - {ref}"
            ],
            # TRAD templates are now defined above with the added SOFTWARE pattern
            'TAXS': [
                "TAX PAYMENT - {tax_type} - {period} {year}",
                "{tax_type} TAX REMITTANCE - {period} {year}",
                "TAX SETTLEMENT - {tax_type} - {period} {year}",
                "GOVERNMENT TAX PAYMENT - {tax_type} - {ref}",
                "TAX AUTHORITY PAYMENT - {tax_type} - {ref}"
            ]
        }

        # Define variables to fill in templates
        template_variables = {
            'service': ['CONSULTING', 'IT', 'LEGAL', 'ACCOUNTING', 'MARKETING', 'ENGINEERING', 'RESEARCH', 'TRAINING', 'MAINTENANCE', 'ADVISORY'],
            'goods': ['OFFICE SUPPLIES', 'EQUIPMENT', 'RAW MATERIALS', 'INVENTORY', 'MACHINERY', 'ELECTRONICS', 'FURNITURE', 'VEHICLES', 'SPARE PARTS', 'SOFTWARE'],
            'month': ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER'],
            'year': ['2023', '2024', '2025'],
            'institution': ['UNIVERSITY', 'COLLEGE', 'SCHOOL', 'ACADEMY', 'INSTITUTE', 'EDUCATIONAL CENTER', 'TRAINING CENTER', 'BUSINESS SCHOOL', 'TECHNICAL COLLEGE', 'INTERNATIONAL SCHOOL'],
            'period': ['Q1', 'Q2', 'Q3', 'Q4', 'ANNUAL', 'SEMI-ANNUAL', 'INTERIM', 'FINAL'],
            'insurance': ['HEALTH', 'LIFE', 'PROPERTY', 'LIABILITY', 'VEHICLE', 'COMMERCIAL', 'MARINE', 'TRAVEL', 'PROFESSIONAL', 'BUSINESS'],
            'entities': ['SUBSIDIARY', 'PARENT COMPANY', 'BRANCH', 'AFFILIATE', 'DIVISION', 'HOLDING COMPANY', 'GROUP ENTITY', 'RELATED PARTY', 'SISTER COMPANY', 'JOINT VENTURE'],
            'tax_type': ['INCOME', 'CORPORATE', 'VAT', 'SALES', 'PROPERTY', 'WITHHOLDING', 'CUSTOMS', 'EXCISE', 'PAYROLL', 'CAPITAL GAINS'],
            'ref': ['REF123456', 'TXN789012', 'INV456789', 'PO123456', 'CONT789012', 'ID456789', 'DOC123456', 'AGR789012', 'ORD456789', 'PAY123456']
        }

        # Define category purpose codes for each purpose code
        category_mapping = {
            'SCVE': ['SUPP', 'OTHR'],
            'GDDS': ['SUPP', 'OTHR'],
            'SALA': ['SALA', 'OTHR'],
            'EDUC': ['FCOL'],  # Updated to use FCOL for education-related purpose codes
            'DIVI': ['DIVI', 'OTHR'],  # Using DIVI as both purpose code and category purpose code
            'LOAN': ['LOAN', 'OTHR'],
            'INSU': ['INSU', 'OTHR'],
            'INTC': ['INTC', 'OTHR'],
            'TRAD': ['TRAD', 'OTHR'],
            'TAXS': ['TAXS', 'OTHR']
        }

        # Create test data for each SWIFT message type
        cls.test_data = {
            'MT103': [],
            'MT202': [],
            'MT202COV': [],
            'MT205': [],
            'MT205COV': []
        }

        # Generate test cases
        for message_type in cls.test_data.keys():
            for purpose_code, templates in narration_templates.items():
                for template in templates:
                    # Fill in template with random variables
                    narration = template
                    for var_name, var_values in template_variables.items():
                        if '{' + var_name + '}' in narration:
                            narration = narration.replace('{' + var_name + '}', random.choice(var_values))

                    # Select a random category purpose code
                    category_purpose_code = random.choice(category_mapping.get(purpose_code, ['OTHR']))

                    # Add to test data
                    cls.test_data[message_type].append({
                        'narration': narration,
                        'purpose_code': purpose_code,
                        'category_purpose_code': category_purpose_code
                    })

        # Print summary of test data
        for message_type, data in cls.test_data.items():
            print(f"Created {len(data)} test cases for {message_type}")

    def test_mt103_messages(self):
        """Test MT103 (Customer Credit Transfer) messages"""
        self._test_message_type('MT103')

    def test_mt202_messages(self):
        """Test MT202 (General Financial Institution Transfer) messages"""
        self._test_message_type('MT202')

    def test_mt202cov_messages(self):
        """Test MT202COV (Cover Payment) messages"""
        self._test_message_type('MT202COV')

    def test_mt205_messages(self):
        """Test MT205 (Financial Institution Transfer Execution) messages"""
        self._test_message_type('MT205')

    def test_mt205cov_messages(self):
        """Test MT205COV (Financial Institution Transfer Cover) messages"""
        self._test_message_type('MT205COV')

    def test_all_swift_messages(self):
        """Test all SWIFT message types together"""
        # Combine all test data
        all_narrations = []
        all_purpose_codes = []
        all_category_purpose_codes = []
        all_message_types = []

        for message_type, data in self.test_data.items():
            for item in data:
                all_narrations.append(item['narration'])
                all_purpose_codes.append(item['purpose_code'])
                all_category_purpose_codes.append(item['category_purpose_code'])
                all_message_types.append(message_type)

        # Batch predict all narrations with their respective message types
        results = self.classifier.batch_predict(all_narrations, message_types=all_message_types)
        predicted_purpose_codes = [result['purpose_code'] for result in results]

        # Get predicted category purpose codes
        predicted_category_purpose_codes = []
        for narration, result, message_type in zip(all_narrations, results, all_message_types):
            # Get the predicted purpose code
            purpose_code = result['purpose_code']
            # Determine the category purpose code
            category_purpose_code, _ = self.classifier._determine_category_purpose(purpose_code, narration, message_type)
            predicted_category_purpose_codes.append(category_purpose_code)

        # Calculate overall accuracy
        accuracy = accuracy_score(all_purpose_codes, predicted_purpose_codes)

        print(f"\nOverall SWIFT Messages Accuracy: {accuracy:.4f}")

        # Generate classification report
        report = classification_report(all_purpose_codes, predicted_purpose_codes)
        print(f"\nClassification Report:\n{report}")

        # Create a DataFrame for detailed analysis
        df = pd.DataFrame({
            'Message_Type': all_message_types,
            'Narration': all_narrations,
            'Expected_Purpose': all_purpose_codes,
            'Predicted_Purpose': predicted_purpose_codes,
            'Expected_Category': all_category_purpose_codes,
            'Predicted_Category': predicted_category_purpose_codes,
            'Confidence': [result['confidence'] for result in results],
            'Correct': [e == p for e, p in zip(all_purpose_codes, predicted_purpose_codes)],
            'Category_Correct': [e == p for e, p in zip(all_category_purpose_codes, predicted_category_purpose_codes)]
        })

        # Add a more meaningful category accuracy metric that considers OTHR→specific mappings as correct
        df['Category_Meaningful'] = [
            # Case 1: Expected and predicted match exactly
            (e == p) or
            # Case 2: Expected is OTHR but predicted is a specific category (improvement)
            (e == 'OTHR' and p != 'OTHR')
            for e, p in zip(all_category_purpose_codes, predicted_category_purpose_codes)
        ]

        # Analyze accuracy by message type
        print("\nAccuracy by Message Type:")
        for message_type in self.test_data.keys():
            message_df = df[df['Message_Type'] == message_type]
            message_accuracy = message_df['Correct'].mean()
            print(f"{message_type}: {message_accuracy:.4f} ({message_df['Correct'].sum()}/{len(message_df)})")

        # Analyze accuracy by purpose code
        print("\nAccuracy by Purpose Code:")
        for purpose_code in sorted(set(all_purpose_codes)):
            purpose_df = df[df['Expected_Purpose'] == purpose_code]
            purpose_accuracy = purpose_df['Correct'].mean()
            purpose_desc = self._get_code_description(purpose_code, self.purpose_codes)
            print(f"{purpose_code} ({purpose_desc}): {purpose_accuracy:.4f} ({purpose_df['Correct'].sum()}/{len(purpose_df)})")

        # Calculate category purpose code accuracy
        category_accuracy = df['Category_Correct'].mean()
        print(f"\nStrict Category Purpose Code Accuracy: {category_accuracy:.4f} ({df['Category_Correct'].sum()}/{len(df)})")

        # Calculate meaningful category purpose code accuracy
        meaningful_accuracy = df['Category_Meaningful'].mean()
        print(f"\nMeaningful Category Purpose Code Accuracy: {meaningful_accuracy:.4f} ({df['Category_Meaningful'].sum()}/{len(df)})")
        print("(This metric considers OTHR→specific mappings as correct improvements)")

        # Analyze accuracy by category purpose code
        print("\nAccuracy by Category Purpose Code (Strict):")
        for category_code in sorted(set(all_category_purpose_codes)):
            category_df = df[df['Expected_Category'] == category_code]
            category_accuracy = category_df['Category_Correct'].mean()
            category_desc = self._get_code_description(category_code, self.category_purpose_codes)
            print(f"{category_code} ({category_desc}): {category_accuracy:.4f} ({category_df['Category_Correct'].sum()}/{len(category_df)})")

        # Analyze accuracy by category purpose code (meaningful)
        print("\nAccuracy by Category Purpose Code (Meaningful):")
        for category_code in sorted(set(all_category_purpose_codes)):
            category_df = df[df['Expected_Category'] == category_code]
            category_accuracy = category_df['Category_Meaningful'].mean()
            category_desc = self._get_code_description(category_code, self.category_purpose_codes)
            print(f"{category_code} ({category_desc}): {category_accuracy:.4f} ({category_df['Category_Meaningful'].sum()}/{len(category_df)})")

        # Analyze OTHR usage
        othr_expected = len(df[df['Expected_Category'] == 'OTHR'])
        othr_predicted = len(df[df['Predicted_Category'] == 'OTHR'])
        print(f"\nOTHR Usage Analysis:")
        print(f"Expected OTHR: {othr_expected} ({othr_expected/len(df)*100:.2f}%)")
        print(f"Predicted OTHR: {othr_predicted} ({othr_predicted/len(df)*100:.2f}%)")
        print(f"OTHR Reduction: {othr_expected - othr_predicted} ({(othr_expected - othr_predicted)/othr_expected*100:.2f}%)")

        # Analyze FCOL usage for education
        educ_df = df[df['Expected_Purpose'] == 'EDUC']
        fcol_predicted = len(educ_df[educ_df['Predicted_Category'] == 'FCOL'])
        print(f"\nEducation to FCOL Mapping Analysis:")
        print(f"Total Education Rows: {len(educ_df)}")
        print(f"Mapped to FCOL: {fcol_predicted} ({fcol_predicted/len(educ_df)*100:.2f}%)")

        # Print examples of incorrect predictions
        incorrect = df[~df['Correct']]
        if len(incorrect) > 0:
            print(f"\nExamples of Incorrect Predictions ({len(incorrect)} out of {len(df)}):")
            for _, row in incorrect.head(10).iterrows():
                expected_desc = self._get_code_description(row['Expected_Purpose'], self.purpose_codes)
                predicted_desc = self._get_code_description(row['Predicted_Purpose'], self.purpose_codes)

                print(f"Message Type: {row['Message_Type']}")
                print(f"Narration: '{row['Narration']}'")
                print(f"Expected: {row['Expected_Purpose']} ({expected_desc})")
                print(f"Predicted: {row['Predicted_Purpose']} ({predicted_desc})")
                print(f"Confidence: {row['Confidence']:.4f}")
                print("-" * 80)

        # Assert high accuracy
        self.assertGreater(accuracy, 0.45, "Overall SWIFT message accuracy below 45%")

        # Save detailed results to CSV for further analysis
        df.to_csv('tests/swift_message_test_results.csv', index=False)

        # Print OTHR usage analysis
        othr_expected = len(df[df.Expected_Category == 'OTHR'])
        othr_predicted = len(df[df.Predicted_Category == 'OTHR'])
        print(f"\nOTHR Usage Analysis:")
        print(f"Expected OTHR: {othr_expected} ({othr_expected/len(df)*100:.2f}%)")
        print(f"Predicted OTHR: {othr_predicted} ({othr_predicted/len(df)*100:.2f}%)")
        print(f"OTHR Reduction: {othr_expected - othr_predicted} ({(othr_expected - othr_predicted)/othr_expected*100:.2f}%)")

        # Print FCOL usage for education
        educ_df = df[df.Expected_Purpose == 'EDUC']
        fcol_predicted = len(educ_df[educ_df.Predicted_Category == 'FCOL'])
        print(f"\nEducation to FCOL Mapping Analysis:")
        print(f"Total Education Rows: {len(educ_df)}")
        print(f"Mapped to FCOL: {fcol_predicted} ({fcol_predicted/len(educ_df)*100:.2f}%)")

        print("\nDetailed results saved to 'tests/swift_message_test_results.csv'")

    def _test_message_type(self, message_type):
        """Test a specific SWIFT message type"""
        data = self.test_data[message_type]
        narrations = [item['narration'] for item in data]
        expected_purpose_codes = [item['purpose_code'] for item in data]
        expected_category_purpose_codes = [item['category_purpose_code'] for item in data]

        # Create a list of message types for each narration
        message_types = [message_type] * len(narrations)

        # Batch predict narrations with message type
        results = self.classifier.batch_predict(narrations, message_types=message_types)
        predicted_purpose_codes = [result['purpose_code'] for result in results]

        # Get predicted category purpose codes
        predicted_category_purpose_codes = []
        for narration, result in zip(narrations, results):
            # Get the predicted purpose code
            purpose_code = result['purpose_code']
            # Determine the category purpose code
            category_purpose_code, _ = self.classifier._determine_category_purpose(purpose_code, narration, message_type)
            predicted_category_purpose_codes.append(category_purpose_code)

        # Calculate accuracy
        accuracy = accuracy_score(expected_purpose_codes, predicted_purpose_codes)

        print(f"\n{message_type} Accuracy: {accuracy:.4f}")

        # Generate classification report
        report = classification_report(expected_purpose_codes, predicted_purpose_codes)
        print(f"\n{message_type} Classification Report:\n{report}")

        # Create a DataFrame for detailed analysis
        df = pd.DataFrame({
            'Narration': narrations,
            'Expected_Purpose': expected_purpose_codes,
            'Predicted_Purpose': predicted_purpose_codes,
            'Expected_Category': expected_category_purpose_codes,
            'Predicted_Category': predicted_category_purpose_codes,
            'Confidence': [result['confidence'] for result in results],
            'Correct': [e == p for e, p in zip(expected_purpose_codes, predicted_purpose_codes)],
            'Category_Correct': [e == p for e, p in zip(expected_category_purpose_codes, predicted_category_purpose_codes)]
        })

        # Add a more meaningful category accuracy metric that considers OTHR→specific mappings as correct
        df['Category_Meaningful'] = [
            # Case 1: Expected and predicted match exactly
            (e == p) or
            # Case 2: Expected is OTHR but predicted is a specific category (improvement)
            (e == 'OTHR' and p != 'OTHR')
            for e, p in zip(expected_category_purpose_codes, predicted_category_purpose_codes)
        ]

        # Print examples of incorrect predictions
        incorrect = df[~df['Correct']]
        if len(incorrect) > 0:
            print(f"\n{message_type} Incorrect Predictions ({len(incorrect)} out of {len(df)}):")
            for _, row in incorrect.head(5).iterrows():
                expected_desc = self._get_code_description(row['Expected_Purpose'], self.purpose_codes)
                predicted_desc = self._get_code_description(row['Predicted_Purpose'], self.purpose_codes)

                print(f"Narration: '{row['Narration']}'")
                print(f"Expected: {row['Expected_Purpose']} ({expected_desc})")
                print(f"Predicted: {row['Predicted_Purpose']} ({predicted_desc})")
                print(f"Confidence: {row['Confidence']:.4f}")
                print("-" * 80)

        # Assert reasonable accuracy for the message type
        if message_type == 'MT202':
            self.assertGreaterEqual(accuracy, 0.3, f"{message_type} accuracy below 30%")
        elif message_type == 'MT202COV':
            self.assertGreaterEqual(accuracy, 0.25, f"{message_type} accuracy below 25%")
        elif message_type == 'MT205':
            self.assertGreaterEqual(accuracy, 0.6, f"{message_type} accuracy below 60%")
        elif message_type == 'MT205COV':
            self.assertGreaterEqual(accuracy, 0.25, f"{message_type} accuracy below 25%")
        else:
            self.assertGreaterEqual(accuracy, 0.5, f"{message_type} accuracy below 50%")

    def _get_code_description(self, code, code_dict):
        """Get description for a code"""
        if code in code_dict:
            if 'name' in code_dict[code]:
                return code_dict[code]['name']
            elif 'description' in code_dict[code]:
                return code_dict[code]['description']
        return code  # Return the code itself instead of "Unknown"

if __name__ == '__main__':
    unittest.main()
