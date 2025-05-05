#!/usr/bin/env python3
"""
Script to display a clean summary of narrations, message types, purpose codes, and category purpose codes
from the analysis results CSV file.
"""

import os
import sys
import pandas as pd

def main():
    """Main function to read and display the narration summary"""
    # Path to the analysis results CSV
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "MT_messages", "analysis_results.csv")

    # Check if the file exists
    if not os.path.exists(csv_path):
        print(f"Error: Analysis results file not found at {csv_path}")
        print("Please run the analyze_mt_messages.py script first.")
        sys.exit(1)

    # Read the CSV file
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        sys.exit(1)

    # Print header
    print("\n=== NARRATION AND PURPOSE CODE SUMMARY ===\n")

    # Print each row in a clean format
    for i, row in df.iterrows():
        print(f"File: {row['file']}")
        print(f"Message Type: {row['message_type']}")
        print(f"Narration: \"{row['narration']}\"")
        print(f"Purpose Code: {row['purpose_code']}")
        print(f"Category Purpose Code: {row['category_purpose_code']}")
        print("-" * 60)

    # Print summary statistics
    print("\n=== SUMMARY STATISTICS ===\n")

    # Count by message type
    print("Count by Message Type:")
    message_type_counts = df['message_type'].value_counts()
    for msg_type, count in message_type_counts.items():
        print(f"  {msg_type}: {count}")

    # Count by purpose code
    print("\nCount by Purpose Code:")
    purpose_code_counts = df['purpose_code'].value_counts()
    for code, count in purpose_code_counts.items():
        print(f"  {code}: {count}")

    # Count by category purpose code
    print("\nCount by Category Purpose Code:")
    category_code_counts = df['category_purpose_code'].value_counts()
    for code, count in category_code_counts.items():
        print(f"  {code}: {count}")

    # Print purpose code distribution by message type
    print("\nPurpose Code Distribution by Message Type:")
    for msg_type in df['message_type'].unique():
        print(f"\n  {msg_type} Messages:")
        type_df = df[df['message_type'] == msg_type]
        type_counts = type_df['purpose_code'].value_counts()
        for code, count in type_counts.items():
            percentage = (count / len(type_df)) * 100
            print(f"    {code}: {count} ({percentage:.1f}%)")

if __name__ == "__main__":
    main()
