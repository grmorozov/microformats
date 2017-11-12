from parser import Parser


def test_simplest_p_property():
    html = '<div class="h-card"><span class="p-name">Test name</span></div>'
    parser = Parser()
    result_dict = parser.parse(html)
    assert result_dict['items'][0]['properties']['name'] == ['Test name']


def test_abbr_p_property():
    html = '<div class="h-card"><abbr class="p-additional-name" title="Peter">P</abbr></div>'
    parser = Parser()
    result_dict = parser.parse(html)
    assert result_dict['items'][0]['properties']['additional-name'] == ['Peter']


def test_abbr_p_property_recursive():
    html = '<div class="h-card"><span class="p-name"><abbr class="p-additional-name" title="Jon">J</abbr></span></div>'
    parser = Parser()
    result_dict = parser.parse(html)
    assert result_dict['items'][0]['properties']['additional-name'] == ['Jon']


def test_multiple_p_property_name():
    html = '<div class="h-card"><span class="p-name p-fullname">Test name</span></div>'
    parser = Parser()
    result_dict = parser.parse(html)
    assert result_dict['items'][0]['properties']['name'] == ['Test name']
    assert result_dict['items'][0]['properties']['fullname'] == ['Test name']


def test_value_class_pattern():
    html = '<div class="h-card">' \
           '<span class="p-name">' \
           '<span class="p-given-name value">John</span>' \
           '<abbr class="p-additional-name" title="Peter">P</abbr>' \
           '<span class="p-family-name value ">Doe</span>' \
           '</span></div>'
    parser = Parser()
    result_dict = parser.parse(html)
    assert result_dict['items'][0]['properties']['name'] == ['JohnDoe']

