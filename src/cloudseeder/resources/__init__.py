"""
Base classes for custom resources.
"""

import importlib

import six
import troposphere

from ..constants import LAMBDA_ARN_EXPORT

class _ResourceMeta(type):
    def __new__(cls, name, bases, attrs):
        attrs.setdefault('props', {})['ServiceToken'] = (str, True)
        if 'resource_type' not in attrs:
            attrs['resource_type'] = cls._canonicalize_resource_type(name, attrs['__module__'])
        return super(_ResourceMeta, cls).__new__(cls, name, bases, attrs)

    @staticmethod
    def _canonicalize_resource_type(name, module_name):
        module = importlib.import_module(module_name)
        if hasattr(module, 'RESOURCE_TYPE_PREFIX'):
            return 'Custom::{}.{}'.format(module.RESOURCE_TYPE_PREFIX, name)
        return 'Custom::{}'.format(name)


class Resource(six.with_metaclass(_ResourceMeta, troposphere.AWSObject)):
    def __init__(self, *args, **kwargs):
        kwargs['ServiceToken'] = troposphere.ImportValue(LAMBDA_ARN_EXPORT)
        super(Resource, self).__init__(*args, **kwargs)

    def create(self, request, session):
        pass

    def update(self, request, session):
        pass

    def delete(self, request, session):
        pass


class Property(troposphere.AWSProperty):
    pass
