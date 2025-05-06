#!/usr/bin/env python
"""
Test script for Swift Parser

This script demonstrates how to use the Swift Parser by parsing a sample SWIFT message.
"""

import json
import sys
from swift_parser import SwiftParser

# Sample MT103 message with Block 3 (User Header)
SAMPLE_SWIFT_MT103 = """
{1:F01BANKBEBBAXXX0000000000}{2:O1030103080313BANKDEFFAXXX00000000000803130803N}{3:{108:REFABC123456}{121:b6cb95d7-5576-48c9-a6e6-0123456789ab}}{4:
:20:REFERENCE123456
:23B:CRED
:32A:230803USD5000,00
:33B:USD5000,00
:50K:/123456789
CUSTOMER NAME
ADDRESS LINE 1
ADDRESS LINE 2
:57A:BANKAAAA
:59:/987654321
BENEFICIARY NAME
BENEFICIARY ADDRESS 1
BENEFICIARY ADDRESS 2
:70:PAYMENT FOR INVOICE 123
:71A:SHA
-}
"""

def main():
    """Main function to demonstrate the Swift Parser"""
    # Create a SwiftParser instance
    print("Creating Swift Parser...")
    parser = SwiftParser()
    
    # Parse the SWIFT message
    def parse_callback(err, ast):
        if err:
            print(f"Error parsing message: {err}")
            sys.exit(1)
        
        print("Successfully parsed SWIFT message!")
        
        # Print the parsed structure
        print(json.dumps(ast, indent=2))
        
        # Demonstrate accessing specific parts of the message
        print("\nMessage Details:")
        print(f"Message Type: {ast['block2']['msg_type']}")
        print(f"Reference: {next((f for f in ast['block4']['fields'] if f['type'] == '20'), {}).get('fieldValue', '')}")
        
        # Get amount field with proper null handling
        amount_field = next((f for f in ast['block4']['fields'] if f['type'] == '32' and f.get('option') == 'A'), None)
        if amount_field and 'ast' in amount_field:
            ast_data = amount_field['ast']
            if 'Amount' in ast_data:
                currency = ast_data.get('Currency', '')
                amount = ast_data.get('Amount', '')
                print(f"Amount: {currency} {amount}")
            else:
                print(f"Amount: {ast_data.get('value', '')}")
        else:
            print("Amount: Not found")
            
        print(f"Sender BIC: {ast['block1']['receiving_lt_id']}")
        print(f"Receiver BIC: {ast['block2']['bic']}")
        
        # Print Block 3 tags if present
        if "block3" in ast and "tags" in ast["block3"]:
            print("\nBlock 3 Tags:")
            for tag, value in ast["block3"]["tags"].items():
                print(f"Tag {tag}: {value}")
        else:
            print("\nBlock 3 not found or has no tags")
            if "block3" in ast:
                print("Block 3 structure:", ast["block3"])
        
        # Print all fields in Block 4
        print("\nBlock 4 Fields:")
        for field in ast['block4']['fields']:
            print(f"Field {field['type']}{field.get('option', '')}: {field['fieldValue']}")
            if 'ast' in field:
                print(f"  Parsed: {field['ast']}")
    
    # Parse the message
    print("Parsing SWIFT message...")
    parser.parse(SAMPLE_SWIFT_MT103, parse_callback)
    print("Test complete.")


if __name__ == "__main__":
    main() 