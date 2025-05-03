from make87_messages.core import header_pb2 as _header_pb2
from make87_messages.audio import frame_pcm_s16le_pb2 as _frame_pcm_s16le_pb2
from make87_messages.audio import frame_aac_pb2 as _frame_aac_pb2
from make87_messages.audio import frame_opus_pb2 as _frame_opus_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FrameAny(_message.Message):
    __slots__ = ("header", "pcm_s16le", "aac", "opus")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    PCM_S16LE_FIELD_NUMBER: _ClassVar[int]
    AAC_FIELD_NUMBER: _ClassVar[int]
    OPUS_FIELD_NUMBER: _ClassVar[int]
    header: _header_pb2.Header
    pcm_s16le: _frame_pcm_s16le_pb2.FramePcmS16le
    aac: _frame_aac_pb2.FrameAac
    opus: _frame_opus_pb2.FrameOpus
    def __init__(self, header: _Optional[_Union[_header_pb2.Header, _Mapping]] = ..., pcm_s16le: _Optional[_Union[_frame_pcm_s16le_pb2.FramePcmS16le, _Mapping]] = ..., aac: _Optional[_Union[_frame_aac_pb2.FrameAac, _Mapping]] = ..., opus: _Optional[_Union[_frame_opus_pb2.FrameOpus, _Mapping]] = ...) -> None: ...
