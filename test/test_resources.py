import decimal

import pytest

from cloudseeder.resources import Resource, Property

class MyResource(Resource):
    pass

class MyProperty(Property):
    props = {
        'Nested': (str, True),
    }

class MyResourceWithProps(MyResource):
    props = {
        'Basic': (str, False),
        'ListBasic': ([int], False),
        'Advanced': (MyProperty, False),
        'ListAdvanced': ([MyProperty], False),
        'Tupular': ((float, int), False),
        'TupularList': ([float, int], False),
    }


def test_resource_includes_service_token():
    assert 'ServiceToken' in MyResource.props

def test_resource_has_resource_name():
    assert MyResource.resource_type == 'Custom::MyResource'

def test_resource_serializable(template):
    template.add_resource(MyResource('MyName'))

def test_resource_vivify_properties():
    resource = MyResourceWithProps.from_dict(
        'Whatever',
        {
            'Basic': 'Ayy',
            'ListBasic': [123, 456],
            'Advanced': {'Nested': 'lmao'},
            'ListAdvanced': [{'Nested': 'xor'}, {'Nested': 'nand'}],
            'Tupular': 2.4,
            'TupularList': [2.3, 1],
        },
    )
    assert isinstance(resource.properties['Advanced'], MyProperty)
    assert isinstance(resource.properties['ListAdvanced'][0], MyProperty)

def test_resource_create_default_impl():
    MyResource('Foo').create(None, None)

def test_resource_update_default_impl():
    MyResource('Foo').update(None, None)

def test_resource_delete_default_impl():
    MyResource('Foo').delete(None, None)
