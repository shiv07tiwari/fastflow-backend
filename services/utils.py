import re


def extract_links(text):
    # Regular expression to detect URLs
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[\w/_\-?=&#.%]*(?:[\w/]+)'
    # Find all non-overlapping matches of the URL regex pattern in the text
    results = re.findall(url_pattern, text)
    return results