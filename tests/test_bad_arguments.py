from parser import parse_html


empty_dict = {'items': [], 'rels': {}, 'rel-urls': {}}


def test_parse_empty_html_gives_empty_dict():
    parse_result = parse_html(html='')
    assert parse_result == empty_dict


def test_parse_html_without_micro_formats_gives_empty_dict():
    parse_result = parse_html(html='<html></html>')
    assert parse_result == empty_dict
