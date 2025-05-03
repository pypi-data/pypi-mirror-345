from make87_messages.core import header_pb2 as _header_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ModelOntology(_message.Message):
    __slots__ = ("header", "classes")
    class ClassEntry(_message.Message):
        __slots__ = ("id", "label")
        ID_FIELD_NUMBER: _ClassVar[int]
        LABEL_FIELD_NUMBER: _ClassVar[int]
        id: int
        label: str
        def __init__(self, id: _Optional[int] = ..., label: _Optional[str] = ...) -> None: ...
    HEADER_FIELD_NUMBER: _ClassVar[int]
    CLASSES_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    classes: _containers.RepeatedCompositeFieldContainer[ModelOntology.ClassEntry]
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., classes: _Optional[_Iterable[_Union[ModelOntology.ClassEntry, _Mapping]]] = ...) -> None: ...
