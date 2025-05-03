from neutrino.utils.tools import extract_code_blocks_with_type

def test_extract_code_blocks_with_type(test_markdown):
    result = extract_code_blocks_with_type(test_markdown)
    assert len(result) == 1
    assert result[0][0] == 'python'
    assert result[0][1] == '''def hello_world():
        print("Hello, world!")'''