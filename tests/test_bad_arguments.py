from parser import parse
import pytest


empty_dict = {'items': [], 'rels': {}, 'rel-urls': {}}


def test_no_params():
    with pytest.raises(ValueError):
        parse()


def test_all_none_params():
    with pytest.raises(ValueError):
        parse(None, None, None)


def test_empty_html():
    with pytest.raises(ValueError):
        parse(html='')


def test_html_without_micro_formats():
    d = parse(html='<html></html>')
    assert d == empty_dict, 'Empty html string'
