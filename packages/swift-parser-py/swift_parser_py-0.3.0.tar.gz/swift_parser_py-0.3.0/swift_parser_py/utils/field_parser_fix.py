"""
Fixes for field parsing issues in the SWIFT parser
"""

from typing import Dict, Any, List, Optional
import re

def fix_bic_field_parsing(field_header: str, field_content: str) -> Dict[str, Any]:
    """
    Special handling for BIC fields that don't match the strict BIC format

    Args:
        field_header: Field header (e.g., '57A')
        field_content: Field content

    Returns:
        Dictionary with parsed field components
    """
    # Check if the content contains a slash (indicating an account)
    if '/' in field_content:
        parts = field_content.split('/')
        if len(parts) == 2:
            return {
                "Account": f"/{parts[0]}",
                "BIC": parts[1]
            }
        elif len(parts) == 3:
            return {
                "Account": f"/{parts[1]}",
                "BIC": parts[2]
            }

    # If no slash, treat the whole content as BIC
    return {
        "BIC": field_content
    }

def fix_field_61_parsing(field_content: str) -> Dict[str, Any]:
    """
    Special handling for field 61 (Statement Line)

    Args:
        field_content: Field content

    Returns:
        Dictionary with parsed field components
    """
    # Remove leading colon if present
    if field_content.startswith(':'):
        field_content = field_content[1:]

    # Try to parse using a simplified pattern
    pattern = re.compile(
        r'(?P<Date>\d{6})(?P<Entry_Date>\d{4})?(?P<D_C_Mark>[DC])(?P<Amount>[\d,\.]+)(?P<Transaction_Type>[A-Z])(?P<Reference>\w{3})(?P<Account_Owner_Reference>[^/]+)(?://(?P<Supplementary_Details>.+))?'
    )

    match = pattern.match(field_content)
    if match:
        result = {}
        for key, value in match.groupdict().items():
            if value:
                result[key.replace('_', ' ')] = value
        return result

    # If parsing fails, return the raw value
    return {"value": field_content}

def fix_field_72_parsing(field_content: str) -> Dict[str, Any]:
    """
    Special handling for field 72 (Sender to Receiver Information)

    Args:
        field_content: Field content

    Returns:
        Dictionary with parsed field components
    """
    # Field 72 often contains structured information with code words
    lines = field_content.replace('\r\n', '\n').replace('\r', '\n').split('\n')

    # Check if it starts with a code word (e.g., /ACC/)
    if lines[0].startswith('/') and '/' in lines[0][1:]:
        code_parts = lines[0].split('/', 3)
        if len(code_parts) >= 3:
            code = code_parts[1]
            info = '/'.join(code_parts[2:])

            # Combine any additional lines
            if len(lines) > 1:
                info += '\n' + '\n'.join(lines[1:])

            return {
                "Code": code,
                "Information": info.strip()
            }

    # If no code word structure, treat as narrative
    return {
        "Narrative": field_content
    }

def apply_field_fixes(field_header: str, field_content: str, parsed_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply fixes to parsed fields based on field header

    Args:
        field_header: Field header (e.g., '57A')
        field_content: Original field content
        parsed_result: Result from the standard parser

    Returns:
        Fixed parsed result
    """
    # Check if there was a parsing error or empty result
    if "error" in parsed_result or not parsed_result:
        # Apply specific fixes based on field type
        if field_header in ["57A", "52A", "53A", "58A"]:
            return fix_bic_field_parsing(field_header, field_content)
        elif field_header == "61":
            return fix_field_61_parsing(field_content)
        elif field_header == "72":
            return fix_field_72_parsing(field_content)

    # If no error or no specific fix, return the original result
    return parsed_result
