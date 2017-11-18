from parser import Parser


# from https://github.com/tommorris/mf2py/blob/master/test/test_parser.py
def test_complex_e_content():
    """When parsing h-* e-* properties, we should fold {"value":..., "html":...}
    into the parsed microformat object, instead of nesting it under an
    unnecessary second layer of "value":
    """
    html = """<!DOCTYPE html><div class="h-entry"><div class="h-card e-content"><p>Hello</p></div></div>"""
    parser = Parser()
    result_dict = parser.parse(html)
    expected_result = {
        "type": ["h-entry"],
        "properties": {
            "content": [{
                "type": [
                    "h-card"
                ],
                "properties": {
                    "name": ["Hello"]
                },
                "html": "<p>Hello</p>",
                "value": "Hello"
            }],
            "name": ["Hello"]
        }
    }
    assert result_dict["items"][0] == expected_result
