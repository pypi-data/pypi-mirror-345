#!/usr/bin/env python
"""
Generate additional education-specific training data for the purpose code classifier.

This script generates synthetic education-related narrations to improve the
classification accuracy for the EDUC purpose code.
"""

import os
import sys
import random
import pandas as pd
import argparse
from datetime import datetime

# Add parent directory to path to import from purpose_classifier
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Generate education-specific training data')
    
    parser.add_argument('--output', type=str, default='data/education_training_data.csv',
                        help='Path to save the generated data')
    
    parser.add_argument('--samples', type=int, default=500,
                        help='Number of samples to generate')
    
    parser.add_argument('--append', action='store_true',
                        help='Append to existing data file if it exists')
    
    return parser.parse_args()

def generate_education_examples(n_samples):
    """
    Generate education-specific examples with diverse narrations
    
    Args:
        n_samples: Number of samples to generate
        
    Returns:
        List of dictionaries with narration, purpose_code, and category_purpose_code
    """
    # Templates for education-related narrations
    templates = [
        # Tuition fee templates
        "TUITION FEE PAYMENT FOR {period} {year} - {institution}",
        "TUITION FEES FOR {student} - {institution} - {period} {year}",
        "PAYMENT OF TUITION FOR {period} {year} - {institution}",
        "{period} {year} TUITION PAYMENT - {institution}",
        "TUITION PAYMENT TO {institution} FOR {period} {year}",
        "{institution} TUITION FEE - {period} {year}",
        "TUITION FOR {program} PROGRAM - {institution}",
        "TUITION PAYMENT FOR {student} - {program} - {institution}",
        
        # School fee templates
        "SCHOOL FEES PAYMENT - {institution} - {period} {year}",
        "PAYMENT OF SCHOOL FEES FOR {student} - {institution}",
        "SCHOOL FEE FOR {period} {year} - {institution}",
        "{institution} SCHOOL FEES - {period} {year}",
        "SCHOOL PAYMENT FOR {student} - {period} {year}",
        
        # Course fee templates
        "COURSE FEE PAYMENT - {course} - {institution}",
        "PAYMENT FOR {course} COURSE - {institution}",
        "{course} COURSE FEES - {institution}",
        "COURSE PAYMENT FOR {student} - {course} - {institution}",
        "FEE FOR {course} COURSE AT {institution}",
        
        # Academic fee templates
        "ACADEMIC FEE PAYMENT - {institution} - {period} {year}",
        "PAYMENT OF ACADEMIC FEES - {institution}",
        "ACADEMIC PAYMENT FOR {student} - {institution}",
        "{institution} ACADEMIC FEES - {period} {year}",
        
        # Education expense templates
        "EDUCATION EXPENSES FOR {student} - {institution}",
        "PAYMENT FOR EDUCATION COSTS - {institution}",
        "EDUCATION PAYMENT - {institution} - {period} {year}",
        "{student} EDUCATION FEES - {institution}",
        
        # Exam fee templates
        "EXAMINATION FEE PAYMENT - {institution}",
        "EXAM FEES FOR {student} - {institution}",
        "PAYMENT FOR EXAM REGISTRATION - {institution}",
        "{institution} EXAM FEE - {period} {year}",
        
        # Registration fee templates
        "REGISTRATION FEE PAYMENT - {institution} - {program}",
        "PAYMENT FOR COURSE REGISTRATION - {institution}",
        "REGISTRATION PAYMENT FOR {student} - {institution}",
        "{institution} REGISTRATION FEE - {program}",
        
        # Dormitory/accommodation fee templates
        "DORMITORY FEE PAYMENT - {institution} - {period} {year}",
        "PAYMENT FOR STUDENT ACCOMMODATION - {institution}",
        "STUDENT HOUSING PAYMENT - {institution} - {period} {year}",
        "ACCOMMODATION FEES FOR {student} - {institution}",
        
        # Book and supplies templates
        "PAYMENT FOR TEXTBOOKS AND SUPPLIES - {institution}",
        "EDUCATIONAL MATERIALS PAYMENT - {institution}",
        "BOOKS AND SUPPLIES FOR {student} - {institution}",
        "ACADEMIC SUPPLIES PAYMENT - {institution} - {period} {year}",
        
        # Scholarship and financial aid templates
        "SCHOLARSHIP PAYMENT FOR {student} - {institution}",
        "FINANCIAL AID DISBURSEMENT - {institution} - {student}",
        "EDUCATIONAL GRANT PAYMENT - {student} - {institution}",
        "STUDENT FINANCIAL ASSISTANCE - {institution} - {period} {year}"
    ]
    
    # Variables to fill in templates
    variables = {
        'institution': [
            "UNIVERSITY OF TECHNOLOGY", "NATIONAL UNIVERSITY", "CITY COLLEGE", 
            "INTERNATIONAL SCHOOL OF BUSINESS", "TECHNICAL INSTITUTE", 
            "MEDICAL SCHOOL", "LAW SCHOOL", "BUSINESS ACADEMY", 
            "ENGINEERING COLLEGE", "ARTS INSTITUTE", "SCIENCE ACADEMY", 
            "LANGUAGE SCHOOL", "CULINARY INSTITUTE", "DESIGN COLLEGE", 
            "MUSIC CONSERVATORY", "FILM ACADEMY", "ONLINE UNIVERSITY", 
            "COMMUNITY COLLEGE", "STATE UNIVERSITY", "PRIVATE COLLEGE",
            "POLYTECHNIC UNIVERSITY", "LIBERAL ARTS COLLEGE", "VOCATIONAL SCHOOL",
            "GRADUATE SCHOOL", "RESEARCH INSTITUTE", "TECHNOLOGY ACADEMY"
        ],
        'period': [
            "SPRING", "SUMMER", "FALL", "WINTER", "FIRST SEMESTER", 
            "SECOND SEMESTER", "THIRD TRIMESTER", "ACADEMIC YEAR", 
            "FIRST QUARTER", "SECOND QUARTER", "THIRD QUARTER", "FOURTH QUARTER"
        ],
        'year': ["2023", "2024", "2025", "2026"],
        'student': [
            "JOHN SMITH", "JANE DOE", "STUDENT ID 12345", "STUDENT ID 67890", 
            "ACCOUNT 123456", "ACCOUNT 789012", "STUDENT ACCOUNT", "ID 123456789",
            "STUDENT", "DEPENDENT", "FAMILY MEMBER", "EMPLOYEE DEPENDENT"
        ],
        'program': [
            "BACHELOR", "MASTER", "PHD", "MBA", "CERTIFICATE", "DIPLOMA", 
            "UNDERGRADUATE", "GRADUATE", "DOCTORAL", "PROFESSIONAL", 
            "EXECUTIVE", "ONLINE", "DISTANCE LEARNING", "PART-TIME", "FULL-TIME",
            "COMPUTER SCIENCE", "BUSINESS ADMINISTRATION", "ENGINEERING", 
            "MEDICINE", "LAW", "ARTS", "HUMANITIES", "SCIENCE", "MATHEMATICS",
            "ECONOMICS", "FINANCE", "MARKETING", "PSYCHOLOGY", "SOCIOLOGY",
            "HISTORY", "ENGLISH", "FOREIGN LANGUAGE", "CHEMISTRY", "PHYSICS",
            "BIOLOGY", "ENVIRONMENTAL SCIENCE", "POLITICAL SCIENCE", "EDUCATION"
        ],
        'course': [
            "INTRODUCTION TO PROGRAMMING", "BUSINESS ETHICS", "CALCULUS", 
            "ORGANIC CHEMISTRY", "WORLD HISTORY", "MACROECONOMICS", 
            "FINANCIAL ACCOUNTING", "MARKETING PRINCIPLES", "STATISTICS", 
            "DATABASE MANAGEMENT", "ARTIFICIAL INTELLIGENCE", "CORPORATE FINANCE", 
            "INTERNATIONAL BUSINESS", "HUMAN RESOURCES", "STRATEGIC MANAGEMENT",
            "CREATIVE WRITING", "PUBLIC SPEAKING", "RESEARCH METHODS", 
            "PROJECT MANAGEMENT", "DIGITAL MARKETING", "DATA ANALYSIS", 
            "MACHINE LEARNING", "WEB DEVELOPMENT", "MOBILE APP DEVELOPMENT",
            "GRAPHIC DESIGN", "PHOTOGRAPHY", "FILM PRODUCTION", "MUSIC THEORY",
            "FOREIGN LANGUAGE", "LITERATURE", "PHILOSOPHY", "PSYCHOLOGY",
            "SOCIOLOGY", "ANTHROPOLOGY", "POLITICAL SCIENCE", "ENVIRONMENTAL STUDIES"
        ]
    }
    
    examples = []
    for _ in range(n_samples):
        template = random.choice(templates)
        
        # Fill in template with random variables
        narration = template
        for var_name, var_values in variables.items():
            if '{' + var_name + '}' in narration:
                narration = narration.replace('{' + var_name + '}', random.choice(var_values))
        
        # Add to examples
        examples.append({
            'narration': narration,
            'purpose_code': 'EDUC',
            'category_purpose_code': 'FCOL'  # Map to Fee Collection as per requirements
        })
    
    return examples

def main():
    """Main function to generate education training data"""
    args = parse_args()
    
    print(f"Generating {args.samples} education-specific training examples...")
    examples = generate_education_examples(args.samples)
    
    # Convert to DataFrame
    df = pd.DataFrame(examples)
    
    # Save to CSV
    if args.append and os.path.exists(args.output):
        print(f"Appending to existing file: {args.output}")
        existing_df = pd.read_csv(args.output)
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df.to_csv(args.output, index=False)
        print(f"Saved {len(df)} new examples (total: {len(combined_df)}) to {args.output}")
    else:
        print(f"Saving to new file: {args.output}")
        df.to_csv(args.output, index=False)
        print(f"Saved {len(df)} examples to {args.output}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
