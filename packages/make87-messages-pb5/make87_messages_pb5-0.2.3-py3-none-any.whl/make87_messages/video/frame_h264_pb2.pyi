from make87_messages.core import header_pb2 as _header_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FrameH264(_message.Message):
    __slots__ = ("header", "data", "width", "height", "is_keyframe", "pts", "dts", "duration", "time_base")
    class Fraction(_message.Message):
        __slots__ = ("num", "den")
        NUM_FIELD_NUMBER: _ClassVar[int]
        DEN_FIELD_NUMBER: _ClassVar[int]
        num: int
        den: int
        def __init__(self, num: _Optional[int] = ..., den: _Optional[int] = ...) -> None: ...
    HEADER_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    IS_KEYFRAME_FIELD_NUMBER: _ClassVar[int]
    PTS_FIELD_NUMBER: _ClassVar[int]
    DTS_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    TIME_BASE_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    data: bytes
    width: int
    height: int
    is_keyframe: bool
    pts: int
    dts: int
    duration: int
    time_base: FrameH264.Fraction
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., data: _Optional[bytes] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., is_keyframe: bool = ..., pts: _Optional[int] = ..., dts: _Optional[int] = ..., duration: _Optional[int] = ..., time_base: _Optional[_Union[FrameH264.Fraction, _Mapping]] = ...) -> None: ...

class FrameMpegTsH264(_message.Message):
    __slots__ = ("header", "data")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    data: bytes
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., data: _Optional[bytes] = ...) -> None: ...
