from make87_messages.core import header_pb2 as _header_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DigestAlgorithm(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNSPECIFIED: _ClassVar[DigestAlgorithm]
    MD5: _ClassVar[DigestAlgorithm]
    MD5_SESS: _ClassVar[DigestAlgorithm]
    SHA_256: _ClassVar[DigestAlgorithm]
    SHA_256_SESS: _ClassVar[DigestAlgorithm]
    SHA_512_256: _ClassVar[DigestAlgorithm]
    SHA_512_256_SESS: _ClassVar[DigestAlgorithm]
UNSPECIFIED: DigestAlgorithm
MD5: DigestAlgorithm
MD5_SESS: DigestAlgorithm
SHA_256: DigestAlgorithm
SHA_256_SESS: DigestAlgorithm
SHA_512_256: DigestAlgorithm
SHA_512_256_SESS: DigestAlgorithm

class BasicAuth(_message.Message):
    __slots__ = ("header", "username", "password")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    username: str
    password: str
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., username: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class DigestAuth(_message.Message):
    __slots__ = ("header", "username", "password", "realm", "nonce", "opaque", "algorithm", "qop")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    REALM_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    OPAQUE_FIELD_NUMBER: _ClassVar[int]
    ALGORITHM_FIELD_NUMBER: _ClassVar[int]
    QOP_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    username: str
    password: str
    realm: str
    nonce: str
    opaque: str
    algorithm: DigestAlgorithm
    qop: str
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., username: _Optional[str] = ..., password: _Optional[str] = ..., realm: _Optional[str] = ..., nonce: _Optional[str] = ..., opaque: _Optional[str] = ..., algorithm: _Optional[_Union[DigestAlgorithm, str]] = ..., qop: _Optional[str] = ...) -> None: ...

class BearerToken(_message.Message):
    __slots__ = ("header", "token")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    token: str
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., token: _Optional[str] = ...) -> None: ...
