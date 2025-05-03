from make87_messages.core import header_pb2 as _header_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RelativePathFile(_message.Message):
    __slots__ = ("header", "path", "data")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    path: str
    data: bytes
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., path: _Optional[str] = ..., data: _Optional[bytes] = ...) -> None: ...

class AbsolutePathFile(_message.Message):
    __slots__ = ("header", "path", "data")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    path: str
    data: bytes
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., path: _Optional[str] = ..., data: _Optional[bytes] = ...) -> None: ...
