import troposphere
import pytest

from cloudseeder import types

@pytest.fixture
def template():
    template = troposphere.Template()
    yield template
    assert template.to_json()

@pytest.fixture
def delete_event():
    return {
       "RequestType" : "Delete",
       "RequestId" : "unique id for this delete request",
       "ResponseURL" : "https://example.com/",
       "ResourceType" : "Custom::MyCustomResourceType",
       "LogicalResourceId" : "BigCustomMan",
       "StackId" : "arn:aws:cloudformation:us-east-2:namespace:stack/stack-name/guid",
       "PhysicalResourceId" : "custom resource provider-defined physical id",
       "ResourceProperties" : {
          "key1" : "string",
          "key2" : [ "list" ],
          "key3" : { "key4" : "map" }
       }
    }

@pytest.fixture
def delete_request(delete_event):
    return types.Request.from_dict(delete_event)

@pytest.fixture
def create_event():
    return {
       "RequestType" : "Create",
       "RequestId" : "unique id for this create request",
       "ResponseURL" : "https://example.com/",
       "ResourceType" : "Custom::MyCustomResourceType",
       "LogicalResourceId" : "BigCustomMan",
       "StackId" : "arn:aws:cloudformation:us-east-2:namespace:stack/stack-name/guid",
       "ResourceProperties" : {
          "key1" : "string",
          "key2" : [ "list" ],
          "key3" : { "key4" : "map" }
       }
    }

@pytest.fixture
def create_request(create_event):
    return types.Request.from_dict(create_event)

@pytest.fixture
def update_event():
    return {
       "RequestType" : "Update",
       "RequestId" : "unique id for this update request",
       "ResponseURL" : "https://example.com/",
       "ResourceType" : "Custom::MyCustomResourceType",
       "LogicalResourceId" : "BigCustomMan",
       "StackId" : "arn:aws:cloudformation:us-east-2:namespace:stack/stack-name/guid",
       "PhysicalResourceId" : "custom resource provider-defined physical id",
       "ResourceProperties" : {
          "key1" : "new-string",
          "key2" : [ "new-list" ],
          "key3" : { "key4" : "new-map" }
       },
       "OldResourceProperties" : {
          "key1" : "string",
          "key2" : [ "list" ],
          "key3" : { "key4" : "map" }
       }
    }

@pytest.fixture
def update_request(update_event):
    return types.Request.from_dict(update_event)
