from parser import Parser


def test_get_implied_title_from_abbr():
    html = '<abbr class="h-card" title="Jane Doe">JD</abbr>'
    parser = Parser()
    result_dict = parser.parse(html)
    assert len(result_dict['items'][0]['properties']) == 1
    assert result_dict['items'][0]['properties']['name'] == ['Jane Doe']


def test_get_implied_alt_from_img():
    html = '<div class="h-card"><img src="jane.html" alt="Jane Doe"/></div>'
    parser = Parser()
    result_dict = parser.parse(html)
    assert result_dict['items'][0]['properties']['name'] == ['Jane Doe']


def test_get_implied_title_from_inner_abbr():
    html = '<div class="h-card"><abbr title="Jane Doe">JD</abbr></div>'
    parser = Parser()
    result_dict = parser.parse(html)
    assert result_dict['items'][0]['properties']['name'] == ['Jane Doe']