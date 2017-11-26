import json
from bs4 import BeautifulSoup, Tag, NavigableString
from typing import List, Dict, Optional
from urllib.parse import urljoin


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
        items = [self._parse_h_tag(t, base_url) for t in tags]

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

    def _parse_h_tag(self, tag: Tag, base_url: Optional[str]) -> dict:
        tag_types = [t for t in tag['class'] if t.startswith('h-')]
        properties = {}
        children_list = []
        child_tags = [t for t in tag.contents if isinstance(t, Tag)]
        for child in child_tags:
            self._parse_tag(child, properties, base_url)
            if not self._is_property_tag(child) and self._has_h_class(child):
                children = self._parse_h_tag(child, base_url)
                if children:
                    children_list.append(children)

        # parsing for implied properties
        if not properties.get('name'):
            properties['name'] = [self._get_implied_name(tag)]

        if not properties.get('photo'):
            photo = self._get_implied_photo(tag)
            if photo:
                photo = self._resolve_relative_url(photo, base_url)
                properties['photo'] = [photo]

        if not properties.get('url'):
            url = self._get_implied_url(tag)
            if url:
                url = self._resolve_relative_url(url, base_url)
                properties['url'] = [url]

        result = {'type': tag_types, 'properties': properties}
        if any(children_list):
            result['children'] = children_list
        return result

    @staticmethod
    def _is_property_tag(tag: Tag) -> bool:
        return tag.has_attr('class') and \
               any([c for c in tag['class'] if
                    c.startswith('p-') or
                    c.startswith('u-') or
                    c.startswith('dt-') or
                    c.startswith('e-')])

    def _parse_tag(self, tag: Tag, properties: dict, base_url: Optional[str]):
        if tag.has_attr('class'):
            if any([c for c in tag['class'] if c.startswith('p-')]):
                self._parse_p_property(tag, properties, base_url)
            if any([c for c in tag['class'] if c.startswith('u-')]):
                self._parse_u_property(tag, properties, base_url)
            if any([c for c in tag['class'] if c.startswith('dt-')]):
                self._parse_dt_property(tag, properties)
            if any([c for c in tag['class'] if c.startswith('e-')]):
                self._parse_e_property(tag, properties)

        if not self._has_h_class(tag):
            for child in tag.children:
                if isinstance(child, Tag):
                    self._parse_tag(child, properties, base_url)

    def _get_implied_name(self, tag: Tag) -> str:
        if tag.name in ('img', 'area') and tag.has_attr('alt'):
            return tag['alt']
        if tag.name == 'abbr' and tag.has_attr('title'):
            return tag['title']
        name = self._get_only_child_of_type(tag, 'img', 'alt') or \
               self._get_only_child_of_type(tag, 'area', 'alt') or \
               self._get_only_child_of_type(tag, 'abbr', 'title')
        if name:
            return name

        child = self._get_only_child(tag)
        if child:
            name = self._get_only_child_of_type(child, 'img', 'alt') or \
                   self._get_only_child_of_type(child, 'area', 'alt') or \
                   self._get_only_child_of_type(child, 'abbr', 'title')
            if name:
                return name
        return tag.text.strip()

    def _get_implied_photo(self, tag: Tag) -> Optional[str]:
        if tag.name == 'img' and tag.has_attr('src'):
            return tag['src']
        if tag.name == 'object' and tag.has_attr('data'):
            return tag['data']
        photo = self._get_only_child_of_type(tag, 'img', 'src') or \
                self._get_only_child_of_type(tag, 'object', 'data')
        if photo:
            return photo
        child = self._get_only_child(tag)
        if child:
            photo = self._get_only_child_of_type(child, 'img', 'src') or \
                    self._get_only_child_of_type(child, 'object', 'data')
            if photo:
                return photo

        return None

    def _get_implied_url(self, tag: Tag) -> Optional[str]:
        if tag.name in ('a', 'area') and tag.has_attr('href'):
            return tag['href']
        url = self._get_only_child_of_type(tag, 'a', 'href') or self._get_only_child_of_type(tag, 'area', 'href')
        if url:
            return url
        child = self._get_only_child(tag)
        if child:
            url = self._get_only_child_of_type(child, 'a', 'href') or \
                  self._get_only_child_of_type(child, 'area', 'href')
            if url:
                return url

        return None

    def _get_only_child(self, tag: Tag) -> Optional[Tag]:
        children = tag.findChildren(recursive=False)
        if len(children) == 1 and isinstance(children[0], Tag) and not self._has_h_class(children[0]):
            return children[0]
        return None

    def _get_only_child_of_type(self, tag: Tag, type_name: str, attr_name: str) -> Optional[str]:
        children = tag.findAll(name=type_name, recursive=False)
        if len(children) == 1 and not self._has_h_class(children[0]) and children[0].has_attr(attr_name):
            return children[0][attr_name]
        return None

    def _parse_p_property(self, tag: Tag, properties: dict, base_url: Optional[str]):
        class_names = [c[2:] for c in tag['class'] if c.startswith('p-')]

        if self._is_value_class(tag):
            data = self._parse_value_class(tag)
        elif self._is_value_title_class(tag):
            data = self._parse_value_title_class(tag)
        elif self._has_h_class(tag):
            # todo: test
            data = self._parse_h_tag(tag, base_url)
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
            data = self._get_text_content(tag)
        if data:
            for name in class_names:
                if properties.get(name) is not None:
                    properties[name].append(data)
                else:
                    properties[name] = [data]

    def _parse_u_property(self, tag: Tag, properties: dict, base_url: Optional[str]):
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
            data = self._resolve_relative_url(data, base_url)
        elif self._is_value_class(tag):
            data = self._parse_value_class(tag)
        elif self._is_value_title_class(tag):
            data = self._parse_value_title_class(tag)
        elif self._has_h_class(tag):
            data = self._parse_h_tag(tag, base_url)
            urls = data['properties'].get('url')
            if urls:
                value = urls[0]
            else:
                value = ''  # todo get value
            data['value'] = value
        elif tag.name == 'abbr' and tag.has_attr('title'):
            data = tag['title']
        elif tag.name in ('data', 'input') and tag.has_attr('value'):
            data = tag['value']
        else:
            data = self._get_text_content(tag)

        if data:
            for name in class_names:
                if properties.get(name) is not None:
                    properties[name].append(data)
                else:
                    properties[name] = [data]

    def _parse_dt_property(self, tag: Tag, properties: dict):
        class_names = [c[3:] for c in tag['class'] if c.startswith('dt-')]
        if self._is_value_class(tag):
            data = self._parse_value_class(tag)
        elif self._is_value_title_class(tag):
            data = self._parse_value_title_class(tag)
        elif tag.name in ('time', 'ins', 'del') and tag.has_attr('datetime'):
            data = tag['datetime']
        elif tag.name == 'abbr' and tag.has_attr('title'):
            data = tag['title']
        elif tag.name in ('data', 'input') and tag.has_attr('value'):
            data = tag['value']
        else:
            data = self._get_text_content(tag)

        if data:
            for name in class_names:
                if properties.get(name) is not None:
                    properties[name].append(data)
                else:
                    properties[name] = [data]

    def _parse_e_property(self, tag: Tag, properties: dict):
        class_names = [c[2:] for c in tag['class'] if c.startswith('e-')]
        inner_html = tag.encode_contents().decode('utf-8')
        html = inner_html.strip()
        value = self._get_text_content(tag)
        data = {'value': value, 'html': html}
        for name in class_names:
            if properties.get(name) is not None:
                properties[name].append(data)
            else:
                properties[name] = [data]

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

    def _parse_value_class(self, tag: Tag) -> str:
        value_tags = [child for child in tag.findChildren(attrs={'class': 'value'}, recursive=False)]
        # todo: implement special rules for date-time parsing
        values = [self._parse_value_tag(vt) for vt in value_tags]
        result = ''.join(values)
        return result

    @staticmethod
    def _is_value_class(tag: Tag) -> bool:
        return any([child for child in tag.findChildren(attrs={'class': 'value'}, recursive=False)])

    def _is_value_title_class(self, tag: Tag) -> bool:
        child = self._get_only_child(tag)
        return child and child.name == 'span' and child.has_attr('class') and child['class'] == ['value-title']

    def _parse_value_title_class(self, tag) -> str:
        child = self._get_only_child(tag)
        return child['title']

    @staticmethod
    def _parse_value_tag(tag: Tag) -> str:
        # todo: check if tag.text is equal to innerText
        if tag.name in ('img', 'area') and tag.has_attr('alt'):
            return tag['alt']
        if tag.name == 'data':
            return tag['value'] if tag.has_attr('value') else tag.text
        if tag.name == 'abbr':
            return tag['title'] if tag.has_attr('title') else tag.text
        return tag.text
