import json
import re

import attr
from attr.validators import instance_of, in_
import troposphere

from .exceptions import EventSerializationException
from .util import get_reason_from_exception

@attr.s(frozen=True)
class Request(object):
    request_type = attr.ib(
        validator=in_(('Create', 'Update', 'Delete')),
    )
    request_id = attr.ib(
         validator=instance_of(str),
    )
    response_url = attr.ib(
         validator=instance_of(str),
    )
    resource_type = attr.ib(
         validator=instance_of(str),
    )
    logical_resource_id = attr.ib(
         validator=instance_of(str),
    )
    stack_id = attr.ib(
         validator=instance_of(str),
    )
    resource_properties = attr.ib(
         validator=instance_of(dict),
    )

    @classmethod
    def from_dict(cls, obj):
        request_cls = globals().get(obj.get('RequestType', cls.__name__), cls)
        request_cls_attrs = set(field.name for field in attr.fields(request_cls))
        kwargs = {re.sub('(?!^)([A-Z]+)', r'_\1', k).lower(): v for k, v in obj.items()}
        request_cls_kwargs = {k: v for k, v in kwargs.items() if k in request_cls_attrs}
        try:
            return request_cls(**request_cls_kwargs)
        except ValueError as ex:
            raise EventSerializationException(
                "Couldn't instantiate request object: {}; ".format(get_reason_from_exception(ex)) +
                "Source object: {}".format(json.dumps(obj, sort_keys=True)),
            )


@attr.s(frozen=True)
class Create(Request):
    pass


@attr.s(frozen=True)
class Update(Request):
    physical_resource_id = attr.ib(
         validator=instance_of(str),
    )
    old_resource_properties = attr.ib(
         validator=instance_of(dict),
    )


@attr.s(frozen=True)
class Delete(Request):
    physical_resource_id = attr.ib(
        validator=instance_of(str),
    )


@attr.s(frozen=True)
class Response(object):
    physical_resource_id = attr.ib(
        validator=instance_of(str),
    )
    stack_id = attr.ib(
        validator=instance_of(str),
    )
    request_id = attr.ib(
        validator=instance_of(str),
    )
    logical_resource_id = attr.ib(
        validator=instance_of(str),
    )
    status = attr.ib(
        converter=lambda x: ('FAILED', 'SUCCESS')[x] if isinstance(x, bool) else x,
        validator=in_(('FAILED', 'SUCCESS')),
    )
    reason = attr.ib(
        validator=instance_of(str),
        default='',
    )
    data = attr.ib(
        validator=instance_of(dict),
        default=attr.Factory(dict),
    )
    no_echo = attr.ib(
        validator=instance_of(bool),
        default=False,
    )

    @classmethod
    def from_request(cls, request, **kwargs):
        kwargs.update({
            'stack_id': request.stack_id,
            'request_id': request.request_id,
            'logical_resource_id': request.logical_resource_id,
        })
        if 'physical_resource_id' not in kwargs and hasattr(request, 'physical_resource_id'):
            kwargs['physical_resource_id'] = request.physical_resource_id
        return cls(**kwargs)

    def to_dict(self):
        return {k.title().replace('_', ''): v for k, v in attr.asdict(self).items()}

    @physical_resource_id.validator
    def _physical_resource_id_validator(self, attribute, value):
        if len(value) > 1024:
            raise EventSerializationException('Physical resource ID can be up to 1KB in size')
