from parser import Parser


def test_simplest_p_property():
    html = '<div class="h-card"><span class="p-name">Test name</span></div>'
    parser = Parser()
    result_dict = parser.parse(html)
    assert result_dict['items'][0]['properties']['name'] == 'Test name'


def test_get_implied_title_from_abbr():
    html = '<abbr class="h-card" title="Jane Doe">JD</abbr>'
    parser = Parser()
    result_dict = parser.parse(html)
    assert len(result_dict['items'][0]['properties']) == 1, 'Extra properties'
    assert result_dict['items'][0]['properties']['name'] == ['Jane Doe']
