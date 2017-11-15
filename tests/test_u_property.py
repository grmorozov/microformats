from parser import Parser


def test_implied_u_name_and_photo():
    html = '<div class="h-card"><span><img src="jane.html" alt="Jane Doe"/></span></div>'
    parser = Parser()
    result_dict = parser.parse(html)
    assert result_dict['items'][0]['properties']['name'] == ['Jane Doe']
    assert result_dict['items'][0]['properties']['photo'] == ['jane.html']
