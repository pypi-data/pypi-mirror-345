from make87_messages.core import header_pb2 as _header_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ImageRGB(_message.Message):
    __slots__ = ("header", "data", "width", "height")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    data: bytes
    width: int
    height: int
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., data: _Optional[bytes] = ..., width: _Optional[int] = ..., height: _Optional[int] = ...) -> None: ...
