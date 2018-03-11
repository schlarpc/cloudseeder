import collections
import importlib
import json
import pkgutil
import sys
import textwrap
import types
import uuid

import jinja2
import markdown
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter
import troposphere

from .. import loader

def type_to_name(obj):
    typemap = {
        str: 'String',
        int: 'Integer',
        bool: 'Boolean',
        float: 'Number',
        troposphere.Tags: 'AWS CloudFormation Resource Tags',
    }
    for cls, name in typemap.items():
        if obj == cls:
            return name
    if isinstance(obj, list):
        return 'List of {}'.format(type_to_name(tuple(obj)))
    if isinstance(obj, tuple):
        return ' or '.join([type_to_name(item) for item in obj])
    return obj.__name__


class PlaceholderEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super(PlaceholderEncoder, self).__init__(*args, **kwargs)
        self._placeholder_cache = {}

    def encode(self, obj):
        result = super(PlaceholderEncoder, self).encode(obj)
        for placeholder, replacement in self._placeholder_cache.items():
            result = result.replace(placeholder, replacement)
        return result

    def default(self, obj):
        placeholder = str(uuid.uuid4())
        self._placeholder_cache[json.dumps(placeholder)] = type_to_name(obj)
        return placeholder


def to_highlighted_json(obj):
    json_doc = json.dumps(obj, indent=2, cls=PlaceholderEncoder)
    highlighted = highlight(json_doc, JsonLexer(), HtmlFormatter())
    return highlighted


def main(argv=None):

    env = jinja2.Environment(
        loader=jinja2.PackageLoader(__name__),
        autoescape=jinja2.select_autoescape(['html']),
    )
    template = env.get_template('resource.html')

    for resource in loader.load_custom_resources():
        print(template.render({
            'title': resource.resource_type,
            'summary': markdown.markdown(textwrap.dedent(resource.__doc__ or '')),
            'json_syntax': to_highlighted_json(collections.OrderedDict([
                ('Type', resource.resource_type),
                ('Properties', collections.OrderedDict([
                    (prop_name, prop_type)
                    for prop_name, (prop_type, required)
                    in sorted(resource.props.items(), key=lambda x: x[0])
                ])),
            ])),
            'properties': [
                {
                    'name': prop_name,
                    'type': type_to_name(prop_type),
                    'required': required,
                }
                for prop_name, (prop_type, required)
                in sorted(resource.props.items(), key=lambda x: x[0])
            ],
        }))





