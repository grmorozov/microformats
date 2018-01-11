from parser import Parser


def test_get_date_from_img_alt_attribute():
    html = '<div class="h-card"><p class="dt-start"><img class="value" alt="2013-03-14"></img>March 14 2013</p></div>'
    parser = Parser()
    result_dict = parser.parse(html)
    assert result_dict['items'][0]['properties']['start'] == ['2013-03-14']


def test_get_date_from_area_alt_attribute():
    html = '<div class="h-card"><p class="dt-start"><area class="value" alt="2013-03-14"></area>March 14 2013</p></div>'
    parser = Parser()
    result_dict = parser.parse(html)
    assert result_dict['items'][0]['properties']['start'] == ['2013-03-14']


def test_get_date_from_data_value_attribute():
    html = '<div class="h-card"><p class="dt-start"><data class="value" value="2013-03-14"></data></p></div>'
    parser = Parser()
    result_dict = parser.parse(html)
    assert result_dict['items'][0]['properties']['start'] == ['2013-03-14']


def test_get_date_from_abbr_title_attribute():
    html = '<div class="h-card"><p class="dt-start"><abbr class="value" title="2013-03-14"></abbr></p></div>'
    parser = Parser()
    result_dict = parser.parse(html)
    assert result_dict['items'][0]['properties']['start'] == ['2013-03-14']


def test_get_date_from_time_datetime_attribute():
    html = '<div class="h-card"><p class="dt-start"><time class="value" datetime="2013-03-14" /></p></div>'
    parser = Parser()
    result_dict = parser.parse(html)
    assert result_dict['items'][0]['properties']['start'] == ['2013-03-14']


def test_get_date_from_del_datetime_attribute():
    html = '<div class="h-card"><p class="dt-start"><del class="value" datetime="2013-03-14" /></p></div>'
    parser = Parser()
    result_dict = parser.parse(html)
    assert result_dict['items'][0]['properties']['start'] == ['2013-03-14']


def test_get_date_from_ins_datetime_attribute():
    html = '<div class="h-card"><p class="dt-start"><ins class="value" datetime="2013-03-14" /></p></div>'
    parser = Parser()
    result_dict = parser.parse(html)
    assert result_dict['items'][0]['properties']['start'] == ['2013-03-14']


def test_get_date_from_data_inner_text():
    html = '<div class="h-card"><p class="dt-start"><data class="value">2013-03-14</data></p></div>'
    parser = Parser()
    result_dict = parser.parse(html)
    assert result_dict['items'][0]['properties']['start'] == ['2013-03-14']
