import re


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
            "outputHandle": edge.get('sourceHandle', "response"),
            "inputHandle": edge.get('targetHandle', None)
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
