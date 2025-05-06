import re


def extract_code_blocks_with_type(markdown_text):
    """
    Extract code blocks and their types from a Markdown string.

    Parameters:
        markdown_text (str): The Markdown content as a string.

    Returns:
        list: A list of tuples, each containing (code_type, code_content).
              If no type is specified, code_type will be an empty string.
    """
    # Regex pattern to match code blocks with or without a code type
    pattern = r"```(\w+)?\n(.*?)```"

    # Use re.DOTALL to capture code content spanning multiple lines
    matches = re.findall(pattern, markdown_text, re.DOTALL)

    # Normalize the results
    return [
        (code_type if code_type else "", code_content.strip())
        for code_type, code_content in matches
    ]
