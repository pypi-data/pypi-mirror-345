import os
import json
import sys
from typing import Dict, Any, Optional, Callable

from .parsers.fin_parser import FinParser
from .parsers.mt_parser import MtParser
from .parsers.block1_parser import parse as block1_parse
from .parsers.block2_parser import parse as block2_parse
from .parsers.block3_parser import parse as block3_parse
from .utils.field_regexp_factory import FieldParser

class SwiftParser:
    def __init__(self, field_patterns=None):
        self.field_patterns = field_patterns
        if not field_patterns:
            # Get the directory of the current file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            patterns_path = os.path.join(current_dir, 'metadata', 'patterns.json')
            with open(patterns_path, 'r') as file:
                self.field_patterns = json.load(file)

        self.field_parser = FieldParser(self.field_patterns)

    def process(self, swift_message: str) -> Dict[str, Any]:
        """Process a SWIFT message and return its AST (Abstract Syntax Tree)"""
        # Parse the complete message structure
        ast = FinParser.parse(swift_message)

        # Parse the individual blocks
        ast["block1"] = block1_parse(ast["block1"]["content"][0])
        ast["block2"] = block2_parse(ast["block2"]["content"][0])

        # Parse Block 3 (User Header) if present
        if "block3" in ast:
            # Block 3 is optional - simplify by just passing the content
            ast["block3"] = block3_parse(ast["block3"])

        # Parse the message fields in block4
        ast["block4"]["fields"] = MtParser.parse(ast["block4"]["content"][0])

        # Parse each field's content
        for field in ast["block4"]["fields"]:
            field_code = field["type"] + (field.get("option", "") or "")
            parsed_field = self.field_parser.parse(field_code, field["fieldValue"])
            field["ast"] = parsed_field

        return ast

    def parse(self, swift_message: str, callback: Callable[[Optional[Exception], Optional[Dict[str, Any]]], None]) -> None:
        """Parse a SWIFT message and invoke the callback with the result"""
        try:
            ast = self.process(swift_message)
            callback(None, ast)
        except Exception as e:
            callback(e, None)


def main():
    """Command-line entry point"""
    if len(sys.argv) != 2:
        print("Usage: python swift_parser.py <swift file>")
        return

    filename = sys.argv[1]
    try:
        with open(filename, 'r', encoding='ascii') as file:
            content = file.read()

        parser = SwiftParser()

        def callback(err, ast):
            if err:
                raise err
            print(json.dumps(ast, indent=2))

        parser.parse(content, callback)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()