from bs4 import Tag
from typing import Optional, List

from urllib.parse import urljoin


class HtmlTag:
    tag: Tag

    def __init__(self, tag: Tag):
        self.tag = tag

    def _has_h_class(self):
        return self.tag.has_attr('class') and any([a for a in self.tag['class'] if a.startswith('h-')])

    def _get_implied_name(self) -> str:

        def _get_name_from_only_child(tag: HtmlTag) -> Optional[str]:
            return tag._get_only_child_of_type('img', 'alt') or \
                   tag._get_only_child_of_type('area', 'alt') or \
                   tag._get_only_child_of_type('abbr', 'title')

        return self._get_tag_attribute_value(['img', 'area'], 'alt') or \
               self._get_tag_attribute_value(['abbr'], 'title') or \
               self._get_implied_property_from_only_child(_get_name_from_only_child) or \
               self.tag.text.strip()

    def _get_only_child(self):
        children = self.tag.findChildren(recursive=False)
        if len(children) == 1 and isinstance(children[0], Tag) and not HtmlTag(children[0])._has_h_class():
            return HtmlTag(children[0])
        return None

    def _get_only_child_of_type(self, type_name: str, attr_name: str) -> Optional[str]:
        children = self.tag.findAll(name=type_name, recursive=False)
        if len(children) == 1 and not HtmlTag(children[0])._has_h_class() and children[0].has_attr(attr_name):
            return children[0][attr_name]
        return None

    def _get_implied_property_from_only_child(self, func) -> Optional[str]:
        value = func(self)
        if value:
            return value
        child = self._get_only_child()
        if child:
            return func(child)
        return None

    def _is_value_class(self) -> bool:
        return any([child for child in self.tag.findChildren(attrs={'class': 'value'}, recursive=False)])

    def _is_value_title_class(self) -> bool:
        child = self._get_only_child()
        return child and child.tag.name == 'span' and child.tag.has_attr('class') and child.tag['class'] == ['value-title']

    def _parse_value_tag(self) -> str:
        return self._get_tag_attribute_value(['img', 'area'], 'alt') or \
               self._get_tag_attribute_value_or_text(['data'], 'value') or \
               self._get_tag_attribute_value_or_text(['abbr'], 'title') or \
               self.tag.text    # todo: check if tag.text is equal to innerText

    def _get_tag_attribute_value(self, tags: List[str], attr: str) -> Optional[str]:
        if self.tag.name in tags and self.tag.has_attr(attr):
            return self.tag[attr]
        return None

    def _get_tag_attribute_value_or_text(self, tags: List[str], attr: str) -> Optional[str]:
        return self._get_attribute_or_text(attr) if self.tag.name in tags else None

    def _get_attribute_or_text(self, attribute: str) -> str:
        return self.tag[attribute] if self.tag.has_attr(attribute) else self.tag.text

    def _parse_value_title_class(self) -> str:
        child = self._get_only_child()
        return child.tag['title']

    def _parse_value_class(self) -> str:
        value_tags = [HtmlTag(child) for child in self.tag.findChildren(attrs={'class': 'value'}, recursive=False)]
        if len(value_tags) == 1:
            if self._is_datetime_tag():
                return value_tags[0]._parse_date_time_value_tag()
            return value_tags[0]._parse_value_tag()
        # todo: implement special rules for date-time parsing
        if self._is_datetime_tag():
            result = ''
            for vt in value_tags:
                value = vt._parse_date_time_value_tag()
                result += value
        else:
            values = [vt._parse_value_tag() for vt in value_tags]
            result = ''.join(values)
        return result

    def _is_datetime_tag(self) -> bool:
        return self.tag.has_attr('class') and any([a for a in self.tag['class'] if a.startswith('dt-')])

    def _get_text_content(self) -> str:
        copy = HtmlTag(self.tag.__copy__())
        copy._remove_nested_elements(['style', 'script'])
        return copy.tag.text.strip()

    def _remove_nested_elements(self, types: List[str]):
        for t in types:
            [e.decompose() for e in self.tag.findAll(t)]

    def _is_property_tag(self) -> bool:
        return self.tag.has_attr('class') and \
               any([c for c in self.tag['class'] if
                    c.startswith('p-') or
                    c.startswith('u-') or
                    c.startswith('dt-') or
                    c.startswith('e-')])

    def _parse_h_tag(self, base_url: Optional[str]) -> dict:
        tag_types = [t for t in self.tag['class'] if t.startswith('h-')]
        properties = {}
        children_list = []
        child_tags = [HtmlTag(t) for t in self.tag.contents if isinstance(t, Tag)]
        for child in child_tags:
            child._parse_tag(properties, base_url)
            if not child._is_property_tag() and child._has_h_class():
                children = child._parse_h_tag(base_url)
                if children:
                    children_list.append(children)

        # parsing for implied properties
        if not properties.get('name'):
            properties['name'] = [self._get_implied_name()]

        if not properties.get('photo'):
            photo = self._get_implied_photo()
            if photo:
                photo = self._resolve_relative_url(photo, base_url)
                properties['photo'] = [photo]

        if not properties.get('url'):
            url = self._get_implied_url()
            if url:
                url = self._resolve_relative_url(url, base_url)
                properties['url'] = [url]

        result = {'type': tag_types, 'properties': properties}
        if any(children_list):
            result['children'] = children_list
        return result

    def _parse_tag(self, properties: dict, base_url: Optional[str]):
        if self.tag.has_attr('class'):
            if any([c for c in self.tag['class'] if c.startswith('p-')]):
                self._parse_p_property(properties, base_url)
            if any([c for c in self.tag['class'] if c.startswith('u-')]):
                self._parse_u_property(properties, base_url)
            if any([c for c in self.tag['class'] if c.startswith('dt-')]):
                self._parse_dt_property(properties)
            if any([c for c in self.tag['class'] if c.startswith('e-')]):
                self._parse_e_property(properties)

        if not self._has_h_class():
            for child in self.tag.children:
                if isinstance(child, Tag):
                    HtmlTag(child)._parse_tag(properties, base_url)

    def _parse_p_property(self, properties: dict, base_url: Optional[str]):
        class_names = [c[2:] for c in self.tag['class'] if c.startswith('p-')]

        if self._is_value_class():
            data = self._parse_value_class()
        elif self._is_value_title_class():
            data = self._parse_value_title_class()
        elif self._has_h_class():
            data = self._parse_h_tag(base_url)
            names = data['properties'].get('name')
            if names:
                value = names[0]
            else:
                value = ''  # todo get value
            data['value'] = value
        else:
            # todo: replace any nested <img> elements with their alt attribute, if present;
            # otherwise their src attribute, if present, adding a space at the beginning and end,
            # resolving any relative URLs, and removing all leading/trailing whitespace.
            data = self._get_tag_attribute_value(['abbr'], 'title') or \
                   self._get_tag_attribute_value(['data', 'input'], 'value') or \
                   self._get_tag_attribute_value(['img', 'area'], 'alt') or \
                   self._get_text_content()
        if data:
            for name in class_names:
                if properties.get(name) is not None:
                    properties[name].append(data)
                else:
                    properties[name] = [data]

    def _parse_u_property(self, properties: dict, base_url: Optional[str]):
        class_names = [c[2:] for c in self.tag['class'] if c.startswith('u-')]
        data = self._get_tag_attribute_value(['a', 'area'], 'href') or \
               self._get_tag_attribute_value(['img', 'audio', 'video', 'source'], 'src') or \
               self._get_tag_attribute_value(['video'], 'poster') or \
               self._get_tag_attribute_value(['object'], 'data')
        if data:
            data = self._resolve_relative_url(data, base_url)
        elif self._is_value_class():
            data = self._parse_value_class()
        elif self._is_value_title_class():
            data = self._parse_value_title_class()
        elif self._has_h_class():
            data = self._parse_h_tag(base_url)
            urls = data['properties'].get('url')
            if urls:
                value = urls[0]
            else:
                value = ''  # todo get value
            data['value'] = value
        else:
            data = self._get_tag_attribute_value(['abbr'], 'title') or \
                   self._get_tag_attribute_value(['data', 'input'], 'value') or \
                   self._get_text_content()

        if data:
            for name in class_names:
                if properties.get(name) is not None:
                    properties[name].append(data)
                else:
                    properties[name] = [data]

    def _parse_dt_property(self, properties: dict):
        class_names = [c[3:] for c in self.tag['class'] if c.startswith('dt-')]
        if self._is_value_class():
            data = self._parse_value_class()
        elif self._is_value_title_class():
            data = self._parse_value_title_class()
        else:
            data = self._get_tag_attribute_value(['time', 'ins', 'del'], 'datetime') or \
                   self._get_tag_attribute_value(['abbr'], 'title') or \
                   self._get_tag_attribute_value(['data', 'input'], 'value') or \
                   self._get_text_content()

        if data:
            for name in class_names:
                if properties.get(name) is not None:
                    properties[name].append(data)
                else:
                    properties[name] = [data]

    def _parse_e_property(self, properties: dict):
        class_names = [c[2:] for c in self.tag['class'] if c.startswith('e-')]
        inner_html = self.tag.encode_contents().decode('utf-8')
        html = inner_html.strip()
        value = self._get_text_content()
        data = {'value': value, 'html': html}
        for name in class_names:
            if properties.get(name) is not None:
                properties[name].append(data)
            else:
                properties[name] = [data]

    def _get_implied_photo(self) -> Optional[str]:
        def _get_photo_from_only_child(tag: HtmlTag) -> Optional[str]:
            return tag._get_only_child_of_type('img', 'src') or \
                   tag._get_only_child_of_type('object', 'data')

        return self._get_tag_attribute_value(['img'], 'src') or \
               self._get_tag_attribute_value(['object'], 'data') or \
               self._get_implied_property_from_only_child(_get_photo_from_only_child)

    def _get_implied_url(self) -> Optional[str]:

        def _get_url_from_only_child(tag: HtmlTag) -> Optional[str]:
            return tag._get_only_child_of_type('a', 'href') or \
                   tag._get_only_child_of_type('area', 'href')

        return self._get_tag_attribute_value(['a', 'area'], 'href') or \
               self._get_implied_property_from_only_child(_get_url_from_only_child)

    @staticmethod
    def _resolve_relative_url(url: str, base_url: Optional[str]):
        if not base_url:
            return url
        return urljoin(base_url, url)

    def _parse_date_time_value_tag(self) -> str:
        return self._get_tag_attribute_value(['img', 'area'], 'alt') or \
               self._get_tag_attribute_value(['data'], 'value') or \
               self._get_tag_attribute_value(['abbr'], 'title') or \
               self._get_tag_attribute_value(['del', 'ins', 'time'], 'datetime') or \
               self.tag.text
