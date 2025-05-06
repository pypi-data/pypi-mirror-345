# SWIFT Parser (Python)

A Python parser for [ISO 15022](http://www.iso15022.org/) messages used for messaging in securities trading by the [SWIFT network](http://www.swift.com/). This parser is designed to handle the standard format of SWIFT financial messages.

[![PyPI version](https://badge.fury.io/py/swift-parser-py.svg)](https://badge.fury.io/py/swift-parser-py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

* Parses any FIN MT message defined by the [ISO 15022](http://www.iso15022.org/) standard
* Supports Block 1, Block 2, Block 3 (User Header), and Block 4 (Message Content)
* Extensive field pattern support with over 100 different field formats
* Parses structured fields (including complex fields like 50K, 59, etc.)
* Non-validating - generously parses messages not 100% compliant with the ISO standard
* One-way parsing only - doesn't generate MT messages
* Metadata-driven approach using field pattern definitions
* Handles complex nested blocks and multi-line fields
* Produces a structured Abstract Syntax Tree (AST) representation of messages
* Robust error handling for malformed fields

## Installation

### From PyPI

```Shell
$ pip install swift-parser-py
```

### From Source

```Shell
$ git clone https://github.com/solchos/swift-parser.git
$ cd swift-parser
$ pip install -e .
```

## Usage

```python
from swift_parser_py.swift_parser import SwiftParser

# Initialize the parser
parser = SwiftParser()

# Parse a SWIFT message
with open('message.txt', 'r') as file:
    swift_message = file.read()

# Method 1: Using process() for direct result
result = parser.process(swift_message)
print(result)

# Method 2: Using parse() with a callback
def callback(err, result):
    if err:
        print(f"Error: {err}")
    else:
        print(result)

parser.parse(swift_message, callback)
```

It is also possible to run the parser from the command line:

```Shell
$ python -m swift_parser_py.swift_parser path/to/message.txt
```

## Architecture

The parser is composed of several specialized components:

### Core Components

* **SwiftParser**: Main entry point that orchestrates the parsing process
* **FinParser**: Parses the high-level block structure of SWIFT messages
* **MtParser**: Parses the fields within Block 4 (Message Text)
* **Block-specific parsers**:
  * `block1_parser.py`: Parses Block 1 (Basic Header)
  * `block2_parser.py`: Parses Block 2 (Application Header)
  * `block3_parser.py`: Parses Block 3 (User Header, optional)

### Field Parsing

* **FieldParser**: Parses individual field content based on field patterns
* **FieldRegexpFactory**: Generates regular expressions for field validation
* **Field pattern definitions**: Stored in `metadata/patterns.json`

### Parsing Process

1. The message is first parsed into blocks using `FinParser`
2. Each block is then parsed by its specific parser
3. For Block 4, fields are extracted using `MtParser`
4. Each field's content is parsed using pattern definitions
5. The result is a structured AST (Abstract Syntax Tree)

## Field Patterns Support

The parser supports an extensive set of field patterns as defined in the ISO 15022 standard:

* Basic field types (16x, 35x, etc.)
* Currency and amount fields (3!a15d)
* Date and time fields (6!n, 8!n, etc.)
* Complex structured fields (addresses, multi-line fields)
* Special field formats for different message types

For more details about field patterns, see [FIELD_PATTERNS.md](swift_parser_py/docs/FIELD_PATTERNS.md)

## Message Types Support

The parser supports all standard SWIFT MT message types, including but not limited to:

* MT101: Request for Transfer
* MT103: Single Customer Credit Transfer
* MT202: General Financial Institution Transfer
* MT202COV: Cover Payment
* MT205: Financial Institution Transfer Execution
* MT900: Confirmation of Debit
* MT910: Confirmation of Credit
* MT940: Customer Statement
* MT942: Interim Statement
* MT950: Statement Message

## Example

Parsing this SWIFT message:

```
{1:F01EXAMPLEBANK0001000001}{2:I103RECEIVERBANK0000N}{3:{108:MSGREF2023}{121:REF-XYZ-789}}{4:
:20:CUSTREF2023-001
:23B:CRED
:32A:230803USD5000,00
:33B:USD5000,00
:50K:/87654321
SENDER COMPANY LTD
123 SENDER STREET, CITY
:52A:ORDERBANK
:53A:SENDERBANK
:57A:RECEIVERBANK
:59:/12345678
BENEFICIARY NAME
15 BENEFICIARY ROAD
:70:PAYMENT FOR SERVICES
INVOICE 2023-001
:71A:SHA
:72:/ACC/INTERNAL TRANSFER
-}
```

Results in a structured dictionary with blocks and parsed fields:

```json
{
  "block1": {
    "block_id": 1,
    "content": "F01EXAMPLEBANK0001000001",
    "application_id": "F",
    "service_id": "01",
    "receiving_lt_id": "EXAMPLEBANK0",
    "session_number": "0010",
    "sequence_number": "00001"
  },
  "block2": {
    "content": "I103RECEIVERBANK0000N",
    "block_id": 2,
    "direction": "I",
    "msg_type": "103",
    "bic": "RECEIVERBA",
    "prio": "N"
  },
  "block3": {
    "block_id": 3,
    "tags": {
      "108": "MSGREF2023",
      "121": "REF-XYZ-789"
    },
    "content": [
      {
        "name": "108",
        "content": [
          "MSGREF2023"
        ]
      },
      {
        "name": "121",
        "content": [
          "REF-XYZ-789"
        ]
      }
    ]
  },
  "block4": {
    "fields": [
      {
        "type": "20",
        "option": "",
        "fieldValue": "CUSTREF2023-001",
        "content": ":20:CUSTREF2023-001",
        "ast": {
          "Reference Number": "CUSTREF2023-001"
        }
      },
      {
        "type": "23",
        "option": "B",
        "fieldValue": "CRED",
        "content": ":23B:CRED",
        "ast": {
          "Bank Operation Code": "CRED"
        }
      },
      {
        "type": "32",
        "option": "A",
        "fieldValue": "230803USD5000,00",
        "content": ":32A:230803USD5000,00",
        "ast": {
          "Date": "230803",
          "Currency": "USD",
          "Amount": "5000,00"
        }
      },
      {
        "type": "33",
        "option": "B",
        "fieldValue": "USD5000,00",
        "content": ":33B:USD5000,00",
        "ast": {
          "Currency": "USD",
          "Instructed Amount": "5000,00"
        }
      },
      {
        "type": "50",
        "option": "K",
        "fieldValue": "/87654321\nSENDER COMPANY LTD\n123 SENDER STREET, CITY",
        "content": ":50K:/87654321\nSENDER COMPANY LTD\n123 SENDER STREET, CITY",
        "ast": {
          "Account": "/87654321",
          "Name": "SENDER COMPANY LTD",
          "Address": ["123 SENDER STREET, CITY"],
          "Name and Address": ["SENDER COMPANY LTD", "123 SENDER STREET, CITY"]
        }
      },
      {
        "type": "52",
        "option": "A",
        "fieldValue": "ORDERBANK",
        "content": ":52A:ORDERBANK",
        "ast": {
          "BIC": "ORDERBANK"
        }
      },
      {
        "type": "53",
        "option": "A",
        "fieldValue": "SENDERBANK",
        "content": ":53A:SENDERBANK",
        "ast": {
          "BIC": "SENDERBANK"
        }
      },
      {
        "type": "57",
        "option": "A",
        "fieldValue": "RECEIVERBANK",
        "content": ":57A:RECEIVERBANK",
        "ast": {
          "BIC": "RECEIVERBANK"
        }
      }
      // Additional fields omitted for brevity
    ]
  }
}

## Usage Examples

### Basic Parsing

```python
from swift_parser_py.swift_parser import SwiftParser

# Initialize the parser
parser = SwiftParser()

# Parse a SWIFT message
swift_message = "{1:F01EXAMPLEBANK0001000001}{2:I103RECEIVERBANK0000N}..."
result = parser.process(swift_message)

# Access basic message information
msg_type = result['block2']['msg_type']  # "103"
sender_bic = result['block2']['bic']     # "RECEIVERBA"

# Access specific fields
reference = result['block4']['fields'][0]['fieldValue']  # "CUSTREF2023-001"
amount = result['block4']['fields'][2]['ast']['Amount']  # "5000,00"
currency = result['block4']['fields'][2]['ast']['Currency']  # "USD"
sender_name = result['block4']['fields'][4]['ast']['Name']  # "SENDER COMPANY LTD"
beneficiary_account = result['block4']['fields'][8]['ast']['Account']  # "/12345678"
```

### Processing Multiple Messages

```python
import os
from swift_parser_py.swift_parser import SwiftParser

parser = SwiftParser()
results = []

# Process all message files in a directory
message_dir = 'messages/'
for filename in os.listdir(message_dir):
    if filename.endswith('.txt'):
        with open(os.path.join(message_dir, filename), 'r') as file:
            swift_message = file.read()
            try:
                result = parser.process(swift_message)
                results.append({
                    'filename': filename,
                    'parsed': result
                })
            except Exception as e:
                print(f"Error processing {filename}: {e}")
```

### Error Handling

```python
from swift_parser_py.swift_parser import SwiftParser

parser = SwiftParser()

# Method 1: Using try/except
try:
    result = parser.process(swift_message)

    # Check for field parsing errors
    for field in result['block4']['fields']:
        if 'ast' in field and 'error' in field['ast']:
            print(f"Warning: Field {field['type']}{field.get('option', '')} parsing error: {field['ast']['error']}")

except Exception as e:
    print(f"Error parsing message: {e}")

# Method 2: Using callback
def callback(err, result):
    if err:
        print(f"Error: {err}")
    else:
        # Process the result
        print(f"Message type: MT{result['block2']['msg_type']}")
        print(f"Reference: {result['block4']['fields'][0]['fieldValue']}")

# Parse with callback
parser.parse(swift_message, callback)
```

## Testing

The project includes comprehensive tests in the `tests` directory:

```python
# Run all tests
python -m unittest discover -s swift_parser_py/tests

# Run specific test files
python -m unittest swift_parser_py.tests.test_block3_parser
python -m unittest swift_parser_py.tests.test_patterns
python -m unittest swift_parser_py.tests.test_comprehensive
```

Sample test output:

```
=== SWIFT MESSAGE PARSING RESULTS ===

BLOCK 1 (BASIC HEADER):
  Application ID: F
  Service ID: 01
  Receiving LT ID: EXAMPLEBANK0
  Session Number: 0010
  Sequence Number: 00001

BLOCK 2 (APPLICATION HEADER):
  Message Type: MT103
  Direction: I
  BIC: RECEIVERBA
  Priority: N

BLOCK 3 (USER HEADER):
  Tag 108: MSGREF2023
  Tag 121: REF-XYZ-789

BLOCK 4 (TEXT BLOCK):
  Field 20: CUSTREF2023-001
  Field 23B: CRED
  Field 32A: 230803USD5000,00
  Field 33B: USD5000,00
  Field 50K: /87654321...
  Field 52A: ORDERBANK
  Field 53A: SENDERBANK
  Field 57A: RECEIVERBANK
  Field 59: /12345678...
  Field 70: PAYMENT FOR SERVICES...
  Field 71A: SHA
  Field 72: /ACC/INTERNAL TRANSFER
```

The test suite includes:
* Tests for various message types (MT103, MT940, MT202, etc.)
* Tests for messages with and without Block 3
* Tests for complex nested blocks and multi-line fields
* Tests for structured fields like 50K and 59
* Tests for field pattern parsing
* Tests for error handling and edge cases

## Contributing

Contributions are welcome! If you'd like to contribute, please:

1. Fork the repository
2. Create a feature branch
3. Add your changes and tests
4. Submit a pull request

## Advanced Features

### Custom Field Patterns

```python
import json
from swift_parser_py.swift_parser import SwiftParser

# Load custom patterns
with open('custom_patterns.json', 'r') as file:
    custom_patterns = json.load(file)

# Initialize parser with custom patterns
parser = SwiftParser(field_patterns=custom_patterns)
```

### Integration with APIs

```python
from flask import Flask, request, jsonify
from swift_parser_py.swift_parser import SwiftParser

app = Flask(__name__)
parser = SwiftParser()

@app.route('/parse', methods=['POST'])
def parse_message():
    if 'message' not in request.json:
        return jsonify({'error': 'No message provided'}), 400

    swift_message = request.json['message']
    try:
        result = parser.process(swift_message)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## Future Enhancements

Potential areas for future development:
* Support for Block 5 (Trailer)
* Message validation against ISO 15022 standards
* Message generation capabilities
* Support for additional message types and field formats
* Performance optimizations for large message volumes
* Integration with message queues and event-driven architectures

## License

Licensed under the MIT License. See [LICENSE](LICENSE) for more information.
