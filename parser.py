import json
from bs4 import BeautifulSoup, Tag, NavigableString
from typing import List, Dict, Optional


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

    def __init__(self, html_parser: str = 'html.parser'):
        self._html_parser = html_parser

    def parse(self, html: str) -> dict:
        rels = {}
        rel_urls = {}
        soup = BeautifulSoup(html, self._html_parser)
        tags = self._get_top_level_tags(soup)
        items = [self.parse_h_tag(t) for t in tags]

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

    def parse_h_tag(self, tag: Tag) -> dict:
        tag_types = [t for t in tag['class'] if t.startswith('h-')]
        properties = {}
        child_tags = [t for t in tag.contents if isinstance(t, Tag)]
        for child in child_tags:
            self.parse_tag(child, properties)

        # parsing for implied properties
        if not properties.get('name'):
            properties['name'] = [self.get_implied_name(tag)]

        if not properties.get('photo'):
            photo = self.get_implied_photo(tag)
            # if there is a gotten photo value, return the normalized absolute URL of it,
            # following the containing document's language's rules for resolving relative URLs
            # (e.g. in HTML, use the current URL context as determined by the page, and first <base> element, if any).
            if photo:
                properties['photo'] = [photo]  # todo: resolve relative urls

        if not properties.get('url'):
            url = self.get_implied_url(tag)
            if url:
                properties['url'] = [url]  # todo: resolve relative urls

        return {'type': tag_types, 'properties': properties}

    def parse_tag(self, tag: Tag, properties: dict):
        is_property = False
        if tag.has_attr('class'):
            if any([c for c in tag['class'] if c.startswith('p-')]):
                self.parse_p_property(tag, properties)
                is_property = True
            if any([c for c in tag['class'] if c.startswith('u-')]):
                self.parse_u_property(tag, properties)
                is_property = True
            if any([c for c in tag['class'] if c.startswith('dt-')]):
                self.parse_dt_property(tag, properties)
                is_property = True
            if any([c for c in tag['class'] if c.startswith('e-')]):
                self.parse_e_property(tag, properties)
                is_property = True
        if self._has_h_class(tag):
            if not is_property:
                children = [self.parse_h_tag(tag)]
                if children:
                    properties['children'] = children
        else:
            for child in tag.children:
                if isinstance(child, Tag):
                    self.parse_tag(child, properties)

    def get_implied_name(self, tag: Tag) -> str:
        if tag.name in ('img', 'area') and tag.has_attr('alt'):
            return tag['alt']
        if tag.name == 'abbr' and tag.has_attr('title'):
            return tag['title']
        name = self.get_only_child_of_type(tag, 'img', 'alt') or \
               self.get_only_child_of_type(tag, 'area', 'alt') or \
               self.get_only_child_of_type(tag, 'abbr', 'title')
        if name:
            return name

        child = self.get_only_child(tag)
        if child:
            name = self.get_only_child_of_type(child, 'img', 'alt') or \
                   self.get_only_child_of_type(child, 'area', 'alt') or \
                   self.get_only_child_of_type(child, 'abbr', 'title')
            if name:
                return name
        return tag.text.strip()

    def get_implied_photo(self, tag: Tag) -> Optional[str]:
        if tag.name == 'img' and tag.has_attr('src'):
            return tag['src']
        if tag.name == 'object' and tag.has_attr('data'):
            return tag['data']
        photo = self.get_only_child_of_type(tag, 'img', 'src') or \
                self.get_only_child_of_type(tag, 'object', 'data')
        if photo:
            return photo
        child = self.get_only_child(tag)
        if child:
            photo = self.get_only_child_of_type(tag, 'img', 'src') or \
                    self.get_only_child_of_type(tag, 'object', 'data')
            if photo:
                return photo

        return None

    def get_implied_url(self, tag: Tag) -> Optional[str]:
        if tag.name in ('a', 'area') and tag.has_attr('href'):
            return tag['href']
        url = self.get_only_child_of_type(tag, 'a', 'href') or self.get_only_child_of_type(tag, 'area', 'href')
        if url:
            return url
        child = self.get_only_child(tag)
        if child:
            url = self.get_only_child_of_type(child, 'a', 'href') or \
                  self.get_only_child_of_type(child, 'area', 'href')
            if url:
                return url

        return None

    def get_only_child(self, tag: Tag) -> Optional[Tag]:
        children = tag.findChildren()
        if len(children) == 1 and isinstance(children[0], Tag) and not self._has_h_class(children[0]):
            return children[0]
        return None

    def get_only_child_of_type(self, tag: Tag, type_name: str, attr_name: str) -> Optional[str]:
        children = tag.findAll(name=type_name, recursive=False)
        if len(children) == 1 and not self._has_h_class(children[0]) and children[0].has_attr(attr_name):
            return children[0][attr_name]
        return None

    def parse_p_property(self, tag: Tag, properties: dict):
        class_names = [c[2:] for c in tag['class'] if c.startswith('p-')]

        if self.is_value_class(tag):
            data = self.parse_value_class(tag)
        elif self._has_h_class(tag):
            # todo: test
            data = self.parse_h_tag(tag)
            names = data['properties'].get('name')
            if names:
                value = names[0]
            else:
                value = ''  # todo get value
            data['value'] = value
        elif tag.name == 'abbr' and tag.has_attr('title'):
            data = tag['title']
        elif tag.name in ('data', 'input') and tag.has_attr('value'):
            data = tag['value']
        elif tag.name in ('img', 'area') and tag.has_attr('alt'):
            data = tag['alt']
        else:
            # todo: replace any nested <img> elements with their alt attribute, if present;
            # otherwise their src attribute, if present, adding a space at the beginning and end,
            # resolving any relative URLs, and removing all leading/trailing whitespace.
            data = tag.text
        if data:
            for name in class_names:
                if properties.get(name) is not None:
                    properties[name].append(data)
                else:
                    properties[name] = [data]

    def parse_u_property(self, tag: Tag, properties: dict):
        class_names = [c[2:] for c in tag['class'] if c.startswith('u-')]
        data = None
        if tag.name in ('a', 'area') and tag.has_attr('href'):
            data = tag['href']
        elif tag.name in ('img', 'audio', 'video', 'source') and tag.has_attr('src'):
            data = tag['src']
        elif tag.name == 'video' and tag.has_attr('poster'):
            data = tag['poster']
        elif tag.name == 'object' and tag.has_attr('data'):
            data = tag['data']
        if data:
            data = data # todo: return the normalized absolute URL of it, following the containing document's
            # language's rules for resolving relative URLs (e.g. in HTML, use the current URL context as determined by
            # the page, and first <base> element, if any).
        elif self.is_value_class(tag):
            data = self.parse_value_class(tag)
        elif tag.name == 'abbr' and tag.has_attr('title'):
            data = tag['title']
        elif tag.name in ('data', 'input') and tag.has_attr('value'):
            data = tag['value']
        else:
            data = tag.text.strip()  # todo: return the textContent of the element after removing all leading/trailing
            # whitespace and nested <script> & <style> elements.

        if data:
            for name in class_names:
                if properties.get(name) is not None:
                    properties[name].append(data)
                else:
                    properties[name] = [data]

    def parse_dt_property(self, tag: Tag, properties: dict) -> dict:
        return {}

    def parse_e_property(self, tag: Tag, properties: dict) -> dict:
        return {}

    def parse_value_class(self, tag: Tag) -> str:
        value_tags = [child for child in tag.findChildren(attrs={'class': 'value'}, recursive=False)]
        # todo: implement special rules for date-time parsing
        values = [self.parse_value_tag(vt) for vt in value_tags]
        result = ''.join(values)
        return result

    @staticmethod
    def is_value_class(tag: Tag) -> bool:
        return any([child for child in tag.findChildren(attrs={'class': 'value'}, recursive=False)])

    @staticmethod
    def parse_value_tag(tag: Tag) -> str:
        # todo: check if tag.text is equal to innerText
        if tag.name in ('img', 'area') and tag.has_attr('alt'):
            return tag['alt']
        if tag.name == 'data':
            return tag['value'] if tag.has_attr('value') else tag.text
        if tag.name == 'abbr':
            return tag['title'] if tag.has_attr('title') else tag.text
        return tag.text


test_html = '<html>' \
            '<title>test example</title>' \
            '<body>' \
            '<div class="h-card">' \
            '    <a class="p-name u-url" href="http://blog.lizardwrangler.com/">Mitchell Baker</a>' \
            '    (<a class="h-org h-card" href="http://mozilla.org/"><span class="p-name">Mozilla Foundation</span></a>)' \
            '</div>' \
            '</body>' \
            '</html>'

pp = Parser('html.parser')
d = pp.parse(test_html)
print(d)
