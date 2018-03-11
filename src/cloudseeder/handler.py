"""
Implements the CloudFormation custom resource handler as an AWS Lambda function.
"""

import functools
import hashlib
import json
import logging
import requests

import boto3

from . import exceptions, loader, types
from .util import get_reason_from_exception, lru_cache

logger = logging.getLogger(__name__)

@lru_cache(1)
def get_custom_resources_mapping():
    """
    Gets all custom resources and maps them into a dict by their resource type.
    """
    return {cls.resource_type: cls for cls in loader.load_custom_resources()}

def send_response_data(response_url, response):
    try:
        cfn_response = response.to_dict()
        http_response = requests.put(response_url, json=cfn_response)
        http_response.raise_for_status()
    except requests.exceptions.RequestException as ex:
        raise exceptions.CloudFormationReportingException(
            'Could not send response to Cloudformation. '
            '(Caused by: {})'.format(get_reason_from_exception(ex))
        )
    return cfn_response

def create_canonical_request_id(request):
    if hasattr(request, 'physical_resource_id'):
        return request.physical_resource_id
    canonical_attrs = ('stack_id', 'logical_resource_id', 'resource_properties')
    canonical_dict = {attr: getattr(request, attr) for attr in canonical_attrs}
    canonical_json = json.dumps(canonical_dict, sort_keys=True)
    return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

def is_typed_tuple(obj, types):
    if isinstance(obj, tuple) and len(obj) == len(types):
        return all(isinstance(item, type_) for item, type_ in zip(obj, types))
    return False

def unpack_response(request, return_value):
    data = {}
    if is_typed_tuple(return_value, (str, dict)):
        physical_resource_id, data = return_value
    elif isinstance(return_value, str):
        physical_resource_id = return_value
    elif isinstance(return_value, types.Response):
        return return_value
    elif return_value is None:
        physical_resource_id = create_canonical_request_id(request)
    else:
        raise exceptions.InvalidReturnTypeException(
            'Method returned {!r} (!r), '.format(return_value, type(return_value)) +
            'expecting one of: cloudseeder.types.Response, (str, dict), str, or NoneType.',
        )
    response = types.Response.from_request(
        request,
        status=True,
        physical_resource_id=physical_resource_id,
        data=data,
    )
    return response

def get_resource_class(resource_type):
    resources = get_custom_resources_mapping()
    if resource_type not in resources:
        raise exceptions.UnknownResourceTypeException(
            '{} is not a known resource type'.format(resource_type),
        )
    return resources[resource_type]

def handler(event, _context=None):
    request = types.Request.from_dict(event)
    try:
        resource_cls = get_resource_class(request.resource_type)
        resource = resource_cls.from_dict(request.logical_resource_id, request.resource_properties)
        resource_method = getattr(resource, request.request_type.lower())
        response = unpack_response(request, resource_method(request, boto3.Session()))
    except Exception as ex:
        logger.exception('Caught exception, failing request')
        response = types.Response.from_request(
            request,
            status=False,
            reason=get_reason_from_exception(ex),
            physical_resource_id=create_canonical_request_id(request),
        )
    return send_response_data(request.response_url, response)
