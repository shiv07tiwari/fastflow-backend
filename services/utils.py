import re
import hashlib


def extract_links(text):
    # Regular expression to detect URLs
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[\w/_\-?=&#.%]*(?:[\w/]+)'
    # Find all non-overlapping matches of the URL regex pattern in the text
    results = re.findall(url_pattern, text)
    return results


def format_input_edges(edges):
    formatted_edges = []
    for edge in edges:
        edge_output = {
            **edge,
            "outputHandle": edge.get('sourceHandle') or edge.get('outputHandle'),
            "inputHandle": edge.get('targetHandle') or edge.get('inputHandle')
        }
        # Remove all keys that are not string or are not required
        edge_output.pop('sourceHandle', None)
        edge_output.pop('targetHandle', None)
        edge_output = {k: v for k, v in edge_output.items() if isinstance(v, str)}

        formatted_edges.append(edge_output)
    return formatted_edges


def format_output_edges(edges):
    output_edges = []
    for edge in edges:
        edge_output = {
            **edge,
            "sourceHandle": edge.get('outputHandle', "response"),
            "targetHandle": edge.get('inputHandle', None)
        }
        edge_output.pop('outputHandle', None)
        edge_output.pop('inputHandle', None)
        output_edges.append(edge_output)
    return output_edges


def string_to_hex(string: str) -> str:
    # Create a SHA-256 hash object
    hash_object = hashlib.sha256()

    # Update the hash object with the input string, encoded to bytes
    hash_object.update(string.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    full_hash_hex = hash_object.hexdigest()

    # Truncate to the first 16 characters
    truncated_hash_hex = full_hash_hex[:16]

    return truncated_hash_hex

def underscore_to_readable(text: str) -> str:
    return ' '.join([word.capitalize() for word in text.split('_')])