import json
from bs4 import BeautifulSoup, Tag, NavigableString
# from typing import List, Dict, Optional


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
        # todo: check best practices
        raise ValueError()


def parse_to_json(html=None, path=None, url=None) -> str:
    return json.dumps(parse(html, path, url))


class Parser:
    _html_parser = None

    def __init__(self, html_parser):
        self._html_parser = html_parser

    def parse(self, html: str) -> dict:
        rels = {}
        rel_urls = {}
        soup = BeautifulSoup(html, self._html_parser)
        tags = self._get_top_level_tags(soup)
        items = [self.parse_tag(t) for t in tags]

        result = {'items': items, 'rels': rels, 'rel-urls': rel_urls}
        return result

    @staticmethod
    def _has_h_class(tag):
        return tag.has_attr('class') and any([a for a in tag['class'] if a.startswith('h-')])

    def _parents_do_not_have_h_class(self, parents):
        return not any([p for p in parents if self._has_h_class(p)])

    def _has_h_class_on_top_level(self, tag):
        return self._has_h_class(tag) and self._parents_do_not_have_h_class(tag.parents)

    def _get_top_level_tags(self, soup: BeautifulSoup) -> list:     # List[Tag]:
        return soup.find_all(self._has_h_class_on_top_level)

    def parse_tag(self, tag: Tag) -> dict:
        tag_type = [t for t in tag['class']]
        properties = {}
        for child in tag.contents:
            if isinstance(child, NavigableString):
                properties['name'] = [str(child)]
            elif isinstance(child, Tag):
                items = self.parse_property(child)
                for key in items.keys():
                    properties[key] = items[key]
        return {'type': tag_type, 'properties': properties}

    def parse_property(self, tag: Tag) -> dict:
        if not tag.has_attr('class'):
            return {}
        for c in tag['class']:
            p = self.parse_p_property(tag, c[2:]) if c.startswith('p-') else {}
            u = self.parse_u_property(tag) if c.startswith('u-') else {}
            dt = self.parse_dt_property(tag) if c.startswith('dt-') else {}
            e = self.parse_e_property(tag) if c.startswith('e-') else {}
            h = self.parse_h_property(tag) if c.startswith('h-') else {}

        d = {'value': h}

        return {**p, **u, **dt, **e, **d}

    def parse_p_property(self, tag: Tag, cl: str) -> dict:
        # todo: value-class-pattern
        if tag.name == 'abbr' and tag.has_attr('title'):
            return {cl: tag['title']}
        elif tag.name in ('data', 'input') and tag.has_attr('value'):
            return {cl: tag['value']}
        elif tag.name in ('img', 'area') and tag.has_attr('alt'):
            return {cl: tag['alt']}
        else:
            # todo: replace any nested <img> elements with their alt attribute, if present;
            # otherwise their src attribute, if present, adding a space at the beginning and end,
            # resolving any relative URLs, and removing all leading/trailing whitespace.
            return {cl: tag.get_text()}

    def parse_u_property(self, tag: Tag) -> dict:
        return {}

    def parse_dt_property(self, tag: Tag) -> dict:
        return {}

    def parse_e_property(self, tag: Tag) -> dict:
        return {}

    def parse_h_property(self, tag: Tag) -> dict:
        return {}


test_html = '<html>' \
       '<title>test example</title>' \
       '<body>' \
       '<div class="h-card">Grey wolf</div>' \
       '<div class="h-adr">London</div>' \
       '<div class="h-card">' \
       '    <a class="p-name u-url" href="http://blog.lizardwrangler.com/">Mitchell Baker</a>' \
       '    (<a class="p-org h-card" href="http://mozilla.org/">Mozilla Foundation</a>)' \
       '</div>' \
       '</body>' \
       '</html>'

pp = Parser('html.parser')
d = pp.parse(test_html)
print(d)
