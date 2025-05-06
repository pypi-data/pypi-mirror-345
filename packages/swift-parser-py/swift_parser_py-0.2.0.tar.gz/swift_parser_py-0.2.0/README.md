# SWIFT Parser (Python)

A Python parser for [ISO 15022](http://www.iso15022.org/) messages used for messaging in securities trading by the [SWIFT network](http://www.swift.com/). This parser is designed to handle the standard format of SWIFT financial messages.

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

## Installation

### From PyPI (Coming Soon)

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
$ cd swift_parser_py
$ python swift_parser.py path/to/message.txt
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
{1:F01BANKBEBB1234567890}{2:I103BANKDEFFXXXXN}{3:{108:ILOVESWIFT}}{4:
:20:REFERENCE123456
:23B:CRED
:32A:210623EUR100000,00
:50K:/12345678901234567890
CUSTOMER NAME
CUSTOMER ADDRESS
:59:/12345678901234
BENEFICIARY NAME
BENEFICIARY ADDRESS
:70:PAYMENT FOR INVOICE 123456
MORE DETAILS
:71A:SHA
:72:/ACC/INVOICE 123456
-}
```

Results in a structured dictionary with blocks and parsed fields:

```json
{
  "block1": {
    "block_id": 1,
    "content": "F01BANKBEBB1234567890",
    "application_id": "F",
    "service_id": "01",
    "receiving_lt_id": "BANKBEBB123456",
    "session_number": "7890",
    "sequence_number": ""
  },
  "block2": {
    "content": "I103BANKDEFFXXXXN",
    "block_id": 2,
    "direction": "I",
    "msg_type": "103",
    "bic": "BANKDEFF",
    "prio": "N"
  },
  "block3": {
    "block_id": 3,
    "tags": {
      "108": "ILOVESWIFT"
    },
    "content": [
      {
        "name": "108",
        "content": [
          "ILOVESWIFT"
        ]
      }
    ]
  },
  "block4": {
    "fields": [
      {
        "type": "20",
        "option": "",
        "fieldValue": "REFERENCE123456",
        "content": ":20:REFERENCE123456",
        "ast": {
          "Reference Number": "REFERENCE123456"
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
        "fieldValue": "210623EUR100000,00",
        "content": ":32A:210623EUR100000,00",
        "ast": {
          "Date": "210623",
          "Currency": "EUR",
          "Amount": "100000,00"
        }
      },
      {
        "type": "50",
        "option": "K",
        "fieldValue": "/12345678901234567890\nCUSTOMER NAME\nCUSTOMER ADDRESS",
        "content": ":50K:/12345678901234567890\nCUSTOMER NAME\nCUSTOMER ADDRESS",
        "ast": {
          "Account": "/12345678901234567890",
          "Name": "CUSTOMER NAME",
          "Address": ["CUSTOMER ADDRESS"],
          "Name and Address": ["CUSTOMER NAME", "CUSTOMER ADDRESS"]
        }
      },
      // Additional fields omitted for brevity
    ]
  }
}

## Testing

The project includes comprehensive tests in the `tests` directory:

```python
# Run all tests
python -m unittest discover -s swift_parser_py/tests

# Run a specific test file
python -m unittest swift_parser_py/tests/test_comprehensive.py
```

The test suite includes:
* Tests for various message types (MT103, MT940, MT202, etc.)
* Tests for messages with and without Block 3
* Tests for complex nested blocks and multi-line fields
* Tests for structured fields like 50K and 59

## Contributing

Contributions are welcome! If you'd like to contribute, please:

1. Fork the repository
2. Create a feature branch
3. Add your changes and tests
4. Submit a pull request

## Future Enhancements

Potential areas for future development:
* Support for Block 5 (Trailer)
* Message validation against ISO 15022 standards
* Message generation capabilities
* Support for additional message types and field formats
* Performance optimizations for large message volumes

## License

Licensed under the MIT License. See [LICENSE](LICENSE) for more information.
