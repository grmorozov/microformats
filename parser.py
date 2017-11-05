import json
from bs4 import BeautifulSoup


def parse(html=None, path=None, url=None) -> dict:
    if html:
        parser = Parser('html.parser')
        return parser.parse(html=html)
    elif path:
        with open(path, 'r') as file:
            html = file.read()
        return parse(html)
    elif url:
        raise NotImplementedError()
        # todo: crawl url
        # return parse(html)
    else:
        raise ValueError()


def parse_to_json(html=None, path=None, url=None) -> str:
    return json.dumps(parse(html, path, url))


class Parser:
    _html_parser = None

    def __init__(self, html_parser):
        self._html_parser = html_parser

    @staticmethod
    def _has_class_h_card(tag):
        return tag.has_attr('class') and 'h-card' in tag['class']

    def parse(self, html) -> dict:
        items = []
        rels = {}
        rel_urls = {}
        soup = BeautifulSoup(html, self._html_parser)
        # div = soup.find(self._has_class_h_card)

        result = {'items': items, 'rels': rels, 'rel-urls': rel_urls}
        return result
