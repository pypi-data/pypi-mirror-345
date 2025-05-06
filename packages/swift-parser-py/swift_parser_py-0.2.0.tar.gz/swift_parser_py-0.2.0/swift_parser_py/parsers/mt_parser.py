import re
from typing import List, Dict, Any

class MtParser:
    """
    Parser for MT message fields
    
    This parses the fields within Block 4 of SWIFT messages.
    """
    
    @staticmethod
    def parse(input_text: str) -> List[Dict[str, Any]]:
        """
        Parse the fields in the MT message
        
        Args:
            input_text: The content of Block 4
            
        Returns:
            List of field dictionaries
        """
        fields = []
        
        # Normalize line endings to handle both Unix and Windows formats
        normalized_text = input_text.replace('\r\n', '\n').replace('\r', '\n')
        lines = normalized_text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
                
            # Check if the line starts with a field header
            field_header_match = re.match(r':(\d{2})([A-Za-z]?):', line)
            if field_header_match:
                field_type = field_header_match.group(1)
                field_option = field_header_match.group(2)
                
                # Check if it's a complex field (with qualifier)
                complex_field_match = re.match(r':\d{2}[A-Za-z]?:([^/]+)//(.+)', line)
                
                if complex_field_match:
                    # Complex field
                    qualifier = complex_field_match.group(1)
                    field_text = complex_field_match.group(2)
                    
                    # Look ahead for continuation lines
                    field_text, i = collect_field_content(lines, i, field_text)
                    
                    field_value = f":{qualifier}//{field_text}"
                    fields.append({
                        "type": field_type,
                        "option": field_option,
                        "fieldValue": field_value,
                        "content": f":{field_type}{field_option}:{field_value}"
                    })
                else:
                    # Simple field
                    field_text = line[len(f":{field_type}{field_option}:"):]
                    
                    # Look ahead for continuation lines
                    field_text, i = collect_field_content(lines, i, field_text)
                    
                    fields.append({
                        "type": field_type,
                        "option": field_option,
                        "fieldValue": field_text,
                        "content": f":{field_type}{field_option}:{field_text}"
                    })
            
            i += 1
        
        return fields


def collect_field_content(lines: List[str], current_idx: int, initial_text: str) -> tuple:
    """
    Collect content for a field that might span multiple lines
    
    Args:
        lines: All lines in the message
        current_idx: Current line index
        initial_text: Text already collected
        
    Returns:
        Tuple of (complete field content, last line index)
    """
    text = initial_text
    idx = current_idx + 1
    
    while idx < len(lines):
        next_line = lines[idx].strip()
        
        # Skip empty lines
        if not next_line:
            idx += 1
            continue
            
        # Check if the next line starts a new field
        if re.match(r':\d{2}[A-Za-z]?:', next_line) or next_line.startswith("-"):
            break
            
        # Otherwise, append the line to the field content
        text += "\n" + next_line
        idx += 1
    
    return text, idx - 1 