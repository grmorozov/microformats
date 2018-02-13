import json
from bs4 import BeautifulSoup, Tag
from typing import List, Optional
from urllib.parse import urljoin
from tags import HtmlTag


#   todo: ignore <template> elements
#   todo: add backward compatibility

DEFAULT_HTML_PARSER = 'html.parser'
SUPPORTED_HTML_PARSERS = ['html.parser', 'html5lib']


def parse_html(html: str, html_parser: Optional[str] = None) -> dict:
    parser = Parser()
    if not html_parser or html_parser not in SUPPORTED_HTML_PARSERS:
        html_parser = DEFAULT_HTML_PARSER
    return parser.parse(html=html, html_parser=html_parser)


def parse_from_url(url: str) -> dict:
    # todo: crawl url
    # todo: check response headers for base url
    raise NotImplementedError()


def parse_from_file(path: str) -> dict:
    with open(path, 'r') as file:
        html = file.read()
    return parse_html(html)


def convert_dict_to_json(source_dict: dict) -> str:
    return json.dumps(source_dict)


class Parser:

    def parse(self, html: str, html_parser: str = DEFAULT_HTML_PARSER, base_url: Optional[str] = None) -> dict:
        soup = BeautifulSoup(html, html_parser)
        base = soup.find(name='base')
        base_url = base['href'] if base else base_url
        tags = self._get_top_level_tags(soup)
        items = [HtmlTag(t)._parse_h_tag(base_url) for t in tags]

        link_tags = soup.findAll('a') + soup.findAll('area') + soup.findAll('link')
        rels, rel_urls = self._parse_hyperlinks(link_tags, base_url)

        result = {'items': items, 'rels': rels, 'rel-urls': rel_urls}
        return result

    @staticmethod
    def _has_h_class(tag):
        return tag.has_attr('class') and any([a for a in tag['class'] if a.startswith('h-')])

    def _parents_do_not_have_h_class(self, parents):
        return not any([p for p in parents if self._has_h_class(p)])

    def _has_h_class_on_top_level(self, tag):
        return self._has_h_class(tag) and self._parents_do_not_have_h_class(tag.parents)

    def _get_top_level_tags(self, soup: BeautifulSoup) -> list:  # List[Tag]:
        return soup.find_all(self._has_h_class_on_top_level)

    @staticmethod
    def _resolve_relative_url(url: str, base_url: Optional[str]):
        if not base_url:
            return url
        return urljoin(base_url, url)

    def _get_text_content(self, tag: Tag) -> str:
        self._remove_nested_elements(tag, ['style', 'script'])
        return tag.text.strip()

    def _parse_hyperlinks(self, tags: List[Tag], base_url: str) -> (dict, dict):
        rels = {}
        rel_urls = {}
        for tag in tags:
            if not tag.has_attr('rel') or not tag['rel']:
                continue
            if not tag.has_attr('href'):
                continue
            url = tag['href']
            url = self._resolve_relative_url(url, base_url)
            values = tag['rel']
            for value in values:
                if value not in rels.keys():
                    rels[value] = []
                if url not in rels[value]:
                    rels[value].append(url)
            if url not in rel_urls.keys():
                rel_urls[url] = {}
            value_attrs = ['hreflang', 'media', 'title', 'type']
            for attr in value_attrs:
                if tag.has_attr(attr) and attr not in rel_urls[url].keys():
                    rel_urls[url][attr] = tag[attr]
            text = self._get_text_content(tag)
            if text and 'text' not in rel_urls[url].keys():
                rel_urls[url]['text'] = text
            if 'rels' not in rel_urls[url].keys():
                rel_urls[url]['rels'] = []
            rel_urls[url]['rels'] = list(set(values + rel_urls[url]['rels']))
        return rels, rel_urls

    @staticmethod
    def _remove_nested_elements(tag: Tag, types: List[str]):
        for t in types:
            [e.decompose() for e in tag.findAll(t)]