"""
conftest.py
"""

import pytest
import os


@pytest.fixture(scope='session')
def test_markdown():

    # Example usage
    markdown_content = """
    # Example Markdown

    This is some text with a Python code block:

    ```python
    def hello_world():
        print("Hello, world!")
    ```
    """

    yield markdown_content


