import json
import re


def filter_signature_key_value_pairs(document_name):
    """
    Filter KEY_VALUE_SET blocks where the key text contains 'sign' or 'signature' (case-insensitive).
    """
    input_file = "amazon_textract_raw/" + document_name.replace(".pdf", "_analysis.json")
    output_file = "geometry_info/" + document_name.replace(".pdf", "_filtered_signature_key_value_pairs.json")
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    blocks = data.get('Blocks', [])
    
    # Create a mapping of block IDs to blocks for easy lookup
    block_map = {block['Id']: block for block in blocks}
    
    # Find all KEY blocks that contain 'sign' or 'signature' in their text
    signature_key_blocks = []
    value_block_ids = set()
    
    for block in blocks:
        if block.get('BlockType') == 'KEY_VALUE_SET' and 'KEY' in block.get('EntityTypes', []):
            # Get the text from child WORD blocks
            key_text = get_text_from_block(block, block_map)
            
            # Use word boundaries to match complete words only
            if re.search(r'\b(signature|sign)\b', key_text, re.IGNORECASE):
                signature_key_blocks.append(block)
                
                # Get associated VALUE block IDs
                for relationship in block.get('Relationships', []):
                    if relationship.get('Type') == 'VALUE':
                        value_block_ids.update(relationship.get('Ids', []))
    
    # Collect all KEY and VALUE blocks
    filtered_blocks = signature_key_blocks.copy()
    for value_id in value_block_ids:
        if value_id in block_map:
            filtered_blocks.append(block_map[value_id])
    
    output_data = {'Blocks': filtered_blocks}
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    #print length of filtered blocks
    print("found "+ str(len(filtered_blocks))//2 + " matching keys + value pairs")
    print("-----------------------------------------------------------")
    


def get_text_from_block(block, block_map):
    """Extract text from a block by following CHILD relationships to WORD blocks."""
    text_parts = []
    
    for relationship in block.get('Relationships', []):
        if relationship.get('Type') == 'CHILD':
            for child_id in relationship.get('Ids', []):
                child_block = block_map.get(child_id, {})
                if child_block.get('BlockType') == 'WORD':
                    text_parts.append(child_block.get('Text', ''))
    
    
    return ' '.join(text_parts)



if __name__ == '__main__':
    result = filter_signature_key_value_pairs(
        'amazon_textract_raw/i20/analyzeDocResponse.json',
        'geometry_info/filtered_signature_key_value_pairs.json'
    )

