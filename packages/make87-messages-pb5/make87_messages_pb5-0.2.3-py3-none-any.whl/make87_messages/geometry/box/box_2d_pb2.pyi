from make87_messages.core import header_pb2 as _header_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Box2D(_message.Message):
    __slots__ = ("header", "x", "y", "width", "height", "rotation")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    ROTATION_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    x: float
    y: float
    width: float
    height: float
    rotation: float
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., x: _Optional[float] = ..., y: _Optional[float] = ..., width: _Optional[float] = ..., height: _Optional[float] = ..., rotation: _Optional[float] = ...) -> None: ...
