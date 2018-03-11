import mock
import pytest
import requests.exceptions

from cloudseeder import exceptions, handler, resources, types


class MyCustomResourceType(resources.Resource):
    props = {
        'key1': (str, True),
        'key2': ([str], True),
        'key3': (dict, True),
    }

    def create(self, request, session):
        return None

@pytest.fixture
def patch_get_custom_resources_mapping():
    with mock.patch('cloudseeder.handler.get_custom_resources_mapping') as m:
        m.return_value = {
            'Custom::MyCustomResourceType': MyCustomResourceType,
        }
        yield m

@pytest.fixture
def patch_requests_put():
    with mock.patch('cloudseeder.handler.requests.put') as m:
        yield m

def test_handler(create_event, patch_get_custom_resources_mapping, patch_requests_put):
    handler_result = handler.handler(create_event, None)
    assert patch_requests_put.call_count == 1
    args, kwargs = patch_requests_put.call_args
    assert handler_result == kwargs['json']
    assert handler_result['Status'] == 'SUCCESS'

def test_handler_bad_resource_type(create_event, patch_get_custom_resources_mapping, patch_requests_put):
    create_event['ResourceType'] = 'Custom::WrongAnswer'
    handler_result = handler.handler(create_event, None)
    assert patch_requests_put.call_count == 1
    assert handler_result['Status'] == 'FAILED'
    assert 'WrongAnswer' in handler_result['Reason']

def test_handler_extra_request_keys(create_event, patch_get_custom_resources_mapping, patch_requests_put):
    create_event['Bingo'] = 'Was his name-o.'
    handler_result = handler.handler(create_event, None)
    assert patch_requests_put.call_count == 1
    assert handler_result['Status'] == 'SUCCESS'

def test_handler_unknown_method(create_event, patch_get_custom_resources_mapping, patch_requests_put):
    with pytest.raises(exceptions.EventSerializationException):
        create_event['RequestType'] = 'Handstand'
        handler_result = handler.handler(create_event, None)
    assert patch_requests_put.call_count == 0

def test_handler_put_error(create_event, patch_get_custom_resources_mapping, patch_requests_put):
    patch_requests_put.side_effect = requests.exceptions.ConnectionError()
    with pytest.raises(exceptions.CloudFormationReportingException):
        handler.handler(create_event, None)
    assert patch_requests_put.call_count == 1

def test_get_custom_resources_mapping():
    assert handler.get_custom_resources_mapping()

def test_unpack_response_str(create_request):
    response = handler.unpack_response(create_request, 'foo')
    assert response.physical_resource_id == 'foo'
    assert response.data == {}

def test_unpack_response_tuple(create_request):
    response = handler.unpack_response(create_request, ('foo', {'a': 'b'}))
    assert response.physical_resource_id == 'foo'
    assert response.data == {'a': 'b'}

def test_unpack_response_tuple_wrong_count(create_request):
    with pytest.raises(exceptions.InvalidReturnTypeException):
        handler.unpack_response(create_request, ('foo', {'a': 'b'}, 'baz'))

def test_unpack_response_tuple_wrong_type(create_request):
    with pytest.raises(exceptions.InvalidReturnTypeException):
        handler.unpack_response(create_request, ('foo', 'baz'))

def test_unpack_response_response(create_request):
    sentinel = types.Response.from_request(
        create_request,
        status='SUCCESS',
        reason='foo',
        physical_resource_id='bar',
    )
    response = handler.unpack_response(create_request, sentinel)
    assert response is sentinel
    assert response.physical_resource_id == 'bar'

def test_unpack_response_none(create_request):
    response = handler.unpack_response(create_request, None)
    assert len(response.physical_resource_id) == 256 // 8 * 2
    assert response.data == {}

def test_create_canonical_request_id_create(create_request):
    request_id = handler.create_canonical_request_id(create_request)
    assert len(request_id) == 256 // 8 * 2

def test_create_canonical_request_id_update(update_request):
    request_id = handler.create_canonical_request_id(update_request)
    assert len(request_id) != 256 // 8 * 2
    assert request_id == update_request.physical_resource_id
