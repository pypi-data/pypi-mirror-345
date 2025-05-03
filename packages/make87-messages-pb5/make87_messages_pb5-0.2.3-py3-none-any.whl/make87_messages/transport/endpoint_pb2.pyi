from make87_messages.core import header_pb2 as _header_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Endpoint(_message.Message):
    __slots__ = ("header", "protocol", "host", "port", "path", "query_params")
    class QueryParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    HEADER_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    HOST_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    QUERY_PARAMS_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    protocol: str
    host: str
    port: int
    path: str
    query_params: _containers.ScalarMap[str, str]
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., protocol: _Optional[str] = ..., host: _Optional[str] = ..., port: _Optional[int] = ..., path: _Optional[str] = ..., query_params: _Optional[_Mapping[str, str]] = ...) -> None: ...
