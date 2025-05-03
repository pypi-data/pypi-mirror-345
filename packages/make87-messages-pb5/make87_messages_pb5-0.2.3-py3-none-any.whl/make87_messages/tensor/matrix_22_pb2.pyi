from make87_messages.core import header_pb2 as _header_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Matrix22(_message.Message):
    __slots__ = ("header", "m00", "m01", "m10", "m11")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    M00_FIELD_NUMBER: _ClassVar[int]
    M01_FIELD_NUMBER: _ClassVar[int]
    M10_FIELD_NUMBER: _ClassVar[int]
    M11_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    m00: float
    m01: float
    m10: float
    m11: float
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., m00: _Optional[float] = ..., m01: _Optional[float] = ..., m10: _Optional[float] = ..., m11: _Optional[float] = ...) -> None: ...
