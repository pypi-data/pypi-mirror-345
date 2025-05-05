import bow_data_common_pb2 as _bow_data_common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AudioSamples(_message.Message):
    __slots__ = ["Samples"]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    Samples: _containers.RepeatedCompositeFieldContainer[AudioSample]
    def __init__(self, Samples: _Optional[_Iterable[_Union[AudioSample, _Mapping]]] = ...) -> None: ...

class AudioSample(_message.Message):
    __slots__ = ["Source", "Data", "Channels", "SampleRate", "NumSamples", "Compression", "Transform", "Designation"]
    class CompressionFormatEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        RAW: _ClassVar[AudioSample.CompressionFormatEnum]
        SPEEX: _ClassVar[AudioSample.CompressionFormatEnum]
    RAW: AudioSample.CompressionFormatEnum
    SPEEX: AudioSample.CompressionFormatEnum
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    SAMPLERATE_FIELD_NUMBER: _ClassVar[int]
    NUMSAMPLES_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    DESIGNATION_FIELD_NUMBER: _ClassVar[int]
    Source: str
    Data: bytes
    Channels: int
    SampleRate: int
    NumSamples: int
    Compression: AudioSample.CompressionFormatEnum
    Transform: _bow_data_common_pb2.Transform
    Designation: _bow_data_common_pb2.StereoDesignationEnum
    def __init__(self, Source: _Optional[str] = ..., Data: _Optional[bytes] = ..., Channels: _Optional[int] = ..., SampleRate: _Optional[int] = ..., NumSamples: _Optional[int] = ..., Compression: _Optional[_Union[AudioSample.CompressionFormatEnum, str]] = ..., Transform: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ..., Designation: _Optional[_Union[_bow_data_common_pb2.StereoDesignationEnum, str]] = ...) -> None: ...
