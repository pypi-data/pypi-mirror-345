from make87_messages.core import header_pb2 as _header_pb2
from make87_messages.video import frame_h264_pb2 as _frame_h264_pb2
from make87_messages.video import frame_h265_pb2 as _frame_h265_pb2
from make87_messages.video import frame_av1_pb2 as _frame_av1_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FrameAny(_message.Message):
    __slots__ = ("header", "h264", "h265", "av1")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    H264_FIELD_NUMBER: _ClassVar[int]
    H265_FIELD_NUMBER: _ClassVar[int]
    AV1_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    h264: _frame_h264_pb2.FrameH264
    h265: _frame_h265_pb2.FrameH265
    av1: _frame_av1_pb2.FrameAV1
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., h264: _Optional[_Union[_frame_h264_pb2.FrameH264, _Mapping]] = ..., h265: _Optional[_Union[_frame_h265_pb2.FrameH265, _Mapping]] = ..., av1: _Optional[_Union[_frame_av1_pb2.FrameAV1, _Mapping]] = ...) -> None: ...

class FrameMpegTsAny(_message.Message):
    __slots__ = ("header", "h264", "h265", "av1")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    H264_FIELD_NUMBER: _ClassVar[int]
    H265_FIELD_NUMBER: _ClassVar[int]
    AV1_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    h264: _frame_h264_pb2.FrameMpegTsH264
    h265: _frame_h265_pb2.FrameMpegTsH265
    av1: _frame_av1_pb2.FrameMpegTsAV1
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., h264: _Optional[_Union[_frame_h264_pb2.FrameMpegTsH264, _Mapping]] = ..., h265: _Optional[_Union[_frame_h265_pb2.FrameMpegTsH265, _Mapping]] = ..., av1: _Optional[_Union[_frame_av1_pb2.FrameMpegTsAV1, _Mapping]] = ...) -> None: ...
