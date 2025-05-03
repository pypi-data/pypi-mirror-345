from make87_messages.core import header_pb2 as _header_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FramePcmS16le(_message.Message):
    __slots__ = ("header", "data", "pts", "time_base", "channels")
    class Fraction(_message.Message):
        __slots__ = ("num", "den")
        NUM_FIELD_NUMBER: _ClassVar[int]
        DEN_FIELD_NUMBER: _ClassVar[int]
        num: int
        den: int
        def __init__(self, num: _Optional[int] = ..., den: _Optional[int] = ...) -> None: ...
    HEADER_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    PTS_FIELD_NUMBER: _ClassVar[int]
    TIME_BASE_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    data: bytes
    pts: int
    time_base: FramePcmS16le.Fraction
    channels: int
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., data: _Optional[bytes] = ..., pts: _Optional[int] = ..., time_base: _Optional[_Union[FramePcmS16le.Fraction, _Mapping]] = ..., channels: _Optional[int] = ...) -> None: ...
