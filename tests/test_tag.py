from tags import HtmlTag
from bs4 import BeautifulSoup, Tag


def test_has_h_class():
    html = '<a class=h-ref href="example.com">link</a>'
    soup = BeautifulSoup(html)
    tag = soup.find_all('a')[0]
    assert tag
    html_tag = HtmlTag(tag)
    assert html_tag._has_h_class()


def test_has_no_h_class():
    html = '<a class=c-ref href="example.com">link</a>'
    soup = BeautifulSoup(html)
    tag = soup.find_all('a')[0]
    assert tag
    html_tag = HtmlTag(tag)
    assert not html_tag._has_h_class()
