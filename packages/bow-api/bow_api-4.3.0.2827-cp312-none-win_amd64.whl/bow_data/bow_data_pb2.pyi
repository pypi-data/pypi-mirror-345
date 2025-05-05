import bow_data_common_pb2 as _bow_data_common_pb2
import bow_data_tactile_pb2 as _bow_data_tactile_pb2
import bow_data_audio_pb2 as _bow_data_audio_pb2
import bow_data_vision_pb2 as _bow_data_vision_pb2
import bow_data_exteroception_pb2 as _bow_data_exteroception_pb2
import bow_data_interoception_pb2 as _bow_data_interoception_pb2
import bow_data_motor_pb2 as _bow_data_motor_pb2
import bow_data_octree_pb2 as _bow_data_octree_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ColorChannelOrder(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    RGBA32: _ClassVar[ColorChannelOrder]
    BGRA32: _ClassVar[ColorChannelOrder]
RGBA32: ColorChannelOrder
BGRA32: ColorChannelOrder

class TimeSync(_message.Message):
    __slots__ = ["TOrigin_0", "TReceiver", "TOrigin_1", "ReturnTrip"]
    TORIGIN_0_FIELD_NUMBER: _ClassVar[int]
    TRECEIVER_FIELD_NUMBER: _ClassVar[int]
    TORIGIN_1_FIELD_NUMBER: _ClassVar[int]
    RETURNTRIP_FIELD_NUMBER: _ClassVar[int]
    TOrigin_0: int
    TReceiver: int
    TOrigin_1: int
    ReturnTrip: bool
    def __init__(self, TOrigin_0: _Optional[int] = ..., TReceiver: _Optional[int] = ..., TOrigin_1: _Optional[int] = ..., ReturnTrip: bool = ...) -> None: ...

class Recording(_message.Message):
    __slots__ = ["ImageSamples", "AudioSamples", "ProprioceptionSamples", "TactileSamples", "MotorSamples", "VoiceSamples", "SpeechSamples", "ExteroceptionSamples", "InteroceptionSamples", "OctreeSamples", "Tstamp"]
    IMAGESAMPLES_FIELD_NUMBER: _ClassVar[int]
    AUDIOSAMPLES_FIELD_NUMBER: _ClassVar[int]
    PROPRIOCEPTIONSAMPLES_FIELD_NUMBER: _ClassVar[int]
    TACTILESAMPLES_FIELD_NUMBER: _ClassVar[int]
    MOTORSAMPLES_FIELD_NUMBER: _ClassVar[int]
    VOICESAMPLES_FIELD_NUMBER: _ClassVar[int]
    SPEECHSAMPLES_FIELD_NUMBER: _ClassVar[int]
    EXTEROCEPTIONSAMPLES_FIELD_NUMBER: _ClassVar[int]
    INTEROCEPTIONSAMPLES_FIELD_NUMBER: _ClassVar[int]
    OCTREESAMPLES_FIELD_NUMBER: _ClassVar[int]
    TSTAMP_FIELD_NUMBER: _ClassVar[int]
    ImageSamples: _containers.RepeatedCompositeFieldContainer[_bow_data_vision_pb2.ImageSamples]
    AudioSamples: _containers.RepeatedCompositeFieldContainer[_bow_data_audio_pb2.AudioSamples]
    ProprioceptionSamples: _containers.RepeatedCompositeFieldContainer[_bow_data_motor_pb2.ProprioceptionSample]
    TactileSamples: _containers.RepeatedCompositeFieldContainer[_bow_data_tactile_pb2.TactileSamples]
    MotorSamples: _containers.RepeatedCompositeFieldContainer[_bow_data_motor_pb2.MotorSample]
    VoiceSamples: _containers.RepeatedCompositeFieldContainer[_bow_data_audio_pb2.AudioSamples]
    SpeechSamples: _containers.RepeatedCompositeFieldContainer[StringSample]
    ExteroceptionSamples: _containers.RepeatedCompositeFieldContainer[_bow_data_exteroception_pb2.ExteroceptionSample]
    InteroceptionSamples: _containers.RepeatedCompositeFieldContainer[_bow_data_interoception_pb2.InteroceptionSample]
    OctreeSamples: _containers.RepeatedCompositeFieldContainer[_bow_data_octree_pb2.OctreeNode]
    Tstamp: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, ImageSamples: _Optional[_Iterable[_Union[_bow_data_vision_pb2.ImageSamples, _Mapping]]] = ..., AudioSamples: _Optional[_Iterable[_Union[_bow_data_audio_pb2.AudioSamples, _Mapping]]] = ..., ProprioceptionSamples: _Optional[_Iterable[_Union[_bow_data_motor_pb2.ProprioceptionSample, _Mapping]]] = ..., TactileSamples: _Optional[_Iterable[_Union[_bow_data_tactile_pb2.TactileSamples, _Mapping]]] = ..., MotorSamples: _Optional[_Iterable[_Union[_bow_data_motor_pb2.MotorSample, _Mapping]]] = ..., VoiceSamples: _Optional[_Iterable[_Union[_bow_data_audio_pb2.AudioSamples, _Mapping]]] = ..., SpeechSamples: _Optional[_Iterable[_Union[StringSample, _Mapping]]] = ..., ExteroceptionSamples: _Optional[_Iterable[_Union[_bow_data_exteroception_pb2.ExteroceptionSample, _Mapping]]] = ..., InteroceptionSamples: _Optional[_Iterable[_Union[_bow_data_interoception_pb2.InteroceptionSample, _Mapping]]] = ..., OctreeSamples: _Optional[_Iterable[_Union[_bow_data_octree_pb2.OctreeNode, _Mapping]]] = ..., Tstamp: _Optional[_Iterable[int]] = ...) -> None: ...

class BlobSample(_message.Message):
    __slots__ = ["BytesArray", "IntArray", "FloatArray", "String", "Transform"]
    BYTESARRAY_FIELD_NUMBER: _ClassVar[int]
    INTARRAY_FIELD_NUMBER: _ClassVar[int]
    FLOATARRAY_FIELD_NUMBER: _ClassVar[int]
    STRING_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    BytesArray: _containers.RepeatedScalarFieldContainer[bytes]
    IntArray: _containers.RepeatedScalarFieldContainer[int]
    FloatArray: _containers.RepeatedScalarFieldContainer[float]
    String: str
    Transform: _bow_data_common_pb2.Transform
    def __init__(self, BytesArray: _Optional[_Iterable[bytes]] = ..., IntArray: _Optional[_Iterable[int]] = ..., FloatArray: _Optional[_Iterable[float]] = ..., String: _Optional[str] = ..., Transform: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ...) -> None: ...

class StringSample(_message.Message):
    __slots__ = ["Data"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    Data: str
    def __init__(self, Data: _Optional[str] = ...) -> None: ...
