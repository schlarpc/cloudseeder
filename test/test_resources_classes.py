import boto3.session
import mock
import pytest

from cloudseeder import loader, types

@pytest.fixture
def all_custom_resources():
    return list(loader.load_custom_resources())

@pytest.fixture
def mock_session():
    return mock.MagicMock(spec=boto3.session.Session)

def create_mock_resource(resource_cls, include_optionals=False):
    kwargs = {}
    for name, (expected_type, required) in resource_cls.props.items():
        if required or include_optionals:
            if isinstance(expected_type, (tuple, list)):
                kwargs[name] = [mock.MagicMock(spec=expected_type[0])]
            else:
                kwargs[name] = mock.MagicMock(spec=expected_type)
    return resource_cls('MyCleverName', **kwargs)

def create_mock_request(method, spec):
    return mock.MagicMock(spec=spec)

@pytest.fixture
def request_specs(create_request, update_request, delete_request):
    return {
        'create': create_request,
        'update': update_request,
        'delete': delete_request,
    }

@pytest.mark.xfail
@pytest.mark.parametrize('method', ('create', 'update', 'delete'))
@pytest.mark.parametrize('custom_resource', all_custom_resources())
def test_run_resource_method(method, custom_resource, mock_session, request_specs):
    request = create_mock_request(method, request_specs[method])
    resource_method = getattr(create_mock_resource(custom_resource), method)
    resource_method(request, mock_session)
