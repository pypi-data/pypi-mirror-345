import re
from typing import Dict, List, Any

class FinParser:
    """
    Parser for FIN messages structure
    
    This parses the high-level block structure of SWIFT messages.
    """
    
    @staticmethod
    def parse(input_text: str) -> Dict[str, Any]:
        """
        Parse a SWIFT message into blocks
        
        Args:
            input_text: The SWIFT message text
            
        Returns:
            Dictionary with blocks mapped as block1, block2, etc.
        """
        result = parse_blocks(input_text)
        block_map = {}
        
        for block in result:
            block_map[f"block{block['name']}"] = block
            
        return block_map


def parse_blocks(input_text: str) -> List[Dict[str, Any]]:
    """
    Parse the blocks in a SWIFT message
    
    Args:
        input_text: The SWIFT message text
        
    Returns:
        List of blocks with name and content
    """
    blocks = []
    # Find all blocks with pattern {X:content}
    block_pattern = re.compile(r'{([^:]+):((?:[^{}]|{(?:[^{}]|{[^{}]*})*})*)}')
    
    for match in block_pattern.finditer(input_text):
        name = match.group(1)
        content_text = match.group(2)
        
        # Process content which might contain nested blocks
        content = process_content(content_text)
        
        blocks.append({
            "name": name,
            "content": content
        })
    
    return blocks


def process_content(content_text: str) -> List[Any]:
    """
    Process block content, which may contain nested blocks
    
    Args:
        content_text: The content part of a block
        
    Returns:
        List of text and block content
    """
    result = []
    
    # Find nested blocks or text
    nested_block_pattern = re.compile(r'{([^:]+):((?:[^{}]|{(?:[^{}]|{[^{}]*})*})*)}')
    
    last_end = 0
    for match in nested_block_pattern.finditer(content_text):
        # Add text before the block
        if match.start() > last_end:
            text = content_text[last_end:match.start()]
            if text.strip():
                result.append(text)
        
        # Add the nested block
        name = match.group(1)
        nested_content = process_content(match.group(2))
        
        result.append({
            "name": name,
            "content": nested_content
        })
        
        last_end = match.end()
    
    # Add remaining text
    if last_end < len(content_text):
        text = content_text[last_end:]
        if text.strip():
            result.append(text)
    
    return result 