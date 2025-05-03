from make87_messages.core import header_pb2 as _header_pb2
from make87_messages.transport import endpoint_pb2 as _endpoint_pb2
from make87_messages.transport import auth_pb2 as _auth_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RTSPMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNSPECIFIED: _ClassVar[RTSPMethod]
    OPTIONS: _ClassVar[RTSPMethod]
    DESCRIBE: _ClassVar[RTSPMethod]
    SETUP: _ClassVar[RTSPMethod]
    PLAY: _ClassVar[RTSPMethod]
    PAUSE: _ClassVar[RTSPMethod]
    TEARDOWN: _ClassVar[RTSPMethod]
    GET_PARAMETER: _ClassVar[RTSPMethod]
    SET_PARAMETER: _ClassVar[RTSPMethod]
    RECORD: _ClassVar[RTSPMethod]
UNSPECIFIED: RTSPMethod
OPTIONS: RTSPMethod
DESCRIBE: RTSPMethod
SETUP: RTSPMethod
PLAY: RTSPMethod
PAUSE: RTSPMethod
TEARDOWN: RTSPMethod
GET_PARAMETER: RTSPMethod
SET_PARAMETER: RTSPMethod
RECORD: RTSPMethod

class RTSPRequest(_message.Message):
    __slots__ = ("header", "endpoint", "method", "headers", "basic_auth", "digest_auth")
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
    BASIC_AUTH_FIELD_NUMBER: _ClassVar[int]
    DIGEST_AUTH_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    endpoint: _endpoint_pb2.Endpoint
    method: RTSPMethod
    headers: _containers.ScalarMap[str, str]
    basic_auth: _auth_pb2.BasicAuth
    digest_auth: _auth_pb2.DigestAuth
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., endpoint: _Optional[_Union[_endpoint_pb2.Endpoint, _Mapping]] = ..., method: _Optional[_Union[RTSPMethod, str]] = ..., headers: _Optional[_Mapping[str, str]] = ..., basic_auth: _Optional[_Union[_auth_pb2.BasicAuth, _Mapping]] = ..., digest_auth: _Optional[_Union[_auth_pb2.DigestAuth, _Mapping]] = ...) -> None: ...
