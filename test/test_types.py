import pytest

from cloudseeder import exceptions, types

def test_delete_request(delete_event):
    request = types.Request.from_dict(delete_event)
    assert isinstance(request, types.Delete)
    assert 'key1' in request.resource_properties

def test_create_request(create_event):
    request = types.Request.from_dict(create_event)
    assert isinstance(request, types.Create)
    assert 'key1' in request.resource_properties

def test_update_request(update_event):
    request = types.Request.from_dict(update_event)
    assert isinstance(request, types.Update)
    assert 'key1' in request.old_resource_properties

def test_response(create_event):
    request = types.Request.from_dict(create_event)
    response = types.Response.from_request(
        request,
        status='SUCCESS',
        reason='foo',
        physical_resource_id='bar',
    )
    assert response.status == 'SUCCESS'
    serialized = response.to_dict()
    assert 'PhysicalResourceId' in serialized

def test_response_auto_physical_id(update_event):
    request = types.Request.from_dict(update_event)
    response = types.Response.from_request(
        request,
        status='SUCCESS',
        reason='foo',
    )
    assert response.status == 'SUCCESS'
    serialized = response.to_dict()
    assert 'PhysicalResourceId' in serialized

def test_response_too_big(create_event):
    request = types.Request.from_dict(create_event)
    with pytest.raises(exceptions.EventSerializationException):
        response = types.Response.from_request(
            request,
            status='SUCCESS',
            reason='foo',
            physical_resource_id='bar' * 1000,
        )
