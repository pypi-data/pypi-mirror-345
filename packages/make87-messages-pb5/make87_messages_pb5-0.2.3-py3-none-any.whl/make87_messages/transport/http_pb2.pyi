from make87_messages.core import header_pb2 as _header_pb2
from make87_messages.transport import endpoint_pb2 as _endpoint_pb2
from make87_messages.transport import auth_pb2 as _auth_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HTTPMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNSPECIFIED: _ClassVar[HTTPMethod]
    GET: _ClassVar[HTTPMethod]
    POST: _ClassVar[HTTPMethod]
    PUT: _ClassVar[HTTPMethod]
    DELETE: _ClassVar[HTTPMethod]
    HEAD: _ClassVar[HTTPMethod]
    OPTIONS: _ClassVar[HTTPMethod]
    PATCH: _ClassVar[HTTPMethod]
UNSPECIFIED: HTTPMethod
GET: HTTPMethod
POST: HTTPMethod
PUT: HTTPMethod
DELETE: HTTPMethod
HEAD: HTTPMethod
OPTIONS: HTTPMethod
PATCH: HTTPMethod

class HTTPRequest(_message.Message):
    __slots__ = ("header", "endpoint", "method", "headers", "body", "basic_auth", "digest_auth", "bearer_token")
    class HeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    HEADER_FIELD_NUMBER: _ClassVar[int]
    ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    BASIC_AUTH_FIELD_NUMBER: _ClassVar[int]
    DIGEST_AUTH_FIELD_NUMBER: _ClassVar[int]
    BEARER_TOKEN_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    endpoint: _endpoint_pb2.Endpoint
    method: HTTPMethod
    headers: _containers.ScalarMap[str, str]
    body: bytes
    basic_auth: _auth_pb2.BasicAuth
    digest_auth: _auth_pb2.DigestAuth
    bearer_token: _auth_pb2.BearerToken
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., endpoint: _Optional[_Union[_endpoint_pb2.Endpoint, _Mapping]] = ..., method: _Optional[_Union[HTTPMethod, str]] = ..., headers: _Optional[_Mapping[str, str]] = ..., body: _Optional[bytes] = ..., basic_auth: _Optional[_Union[_auth_pb2.BasicAuth, _Mapping]] = ..., digest_auth: _Optional[_Union[_auth_pb2.DigestAuth, _Mapping]] = ..., bearer_token: _Optional[_Union[_auth_pb2.BearerToken, _Mapping]] = ...) -> None: ...
