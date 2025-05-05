import bow_data_common_pb2 as _bow_data_common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TactileSamples(_message.Message):
    __slots__ = ["Samples"]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    Samples: _containers.RepeatedCompositeFieldContainer[TactileSample]
    def __init__(self, Samples: _Optional[_Iterable[_Union[TactileSample, _Mapping]]] = ...) -> None: ...

class TactileSample(_message.Message):
    __slots__ = ["Source", "TactileType", "Pressure", "Bumper", "Force", "Torque", "Transform", "NewDataFlag"]
    class TactileTypeEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        UNDEFINED: _ClassVar[TactileSample.TactileTypeEnum]
        PRESSURE: _ClassVar[TactileSample.TactileTypeEnum]
        BUMPER: _ClassVar[TactileSample.TactileTypeEnum]
        FORCE: _ClassVar[TactileSample.TactileTypeEnum]
        TORQUE: _ClassVar[TactileSample.TactileTypeEnum]
    UNDEFINED: TactileSample.TactileTypeEnum
    PRESSURE: TactileSample.TactileTypeEnum
    BUMPER: TactileSample.TactileTypeEnum
    FORCE: TactileSample.TactileTypeEnum
    TORQUE: TactileSample.TactileTypeEnum
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    TACTILETYPE_FIELD_NUMBER: _ClassVar[int]
    PRESSURE_FIELD_NUMBER: _ClassVar[int]
    BUMPER_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    TORQUE_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    NEWDATAFLAG_FIELD_NUMBER: _ClassVar[int]
    Source: str
    TactileType: TactileSample.TactileTypeEnum
    Pressure: float
    Bumper: bool
    Force: _bow_data_common_pb2.Vector3
    Torque: _bow_data_common_pb2.Vector3
    Transform: _bow_data_common_pb2.Transform
    NewDataFlag: bool
    def __init__(self, Source: _Optional[str] = ..., TactileType: _Optional[_Union[TactileSample.TactileTypeEnum, str]] = ..., Pressure: _Optional[float] = ..., Bumper: bool = ..., Force: _Optional[_Union[_bow_data_common_pb2.Vector3, _Mapping]] = ..., Torque: _Optional[_Union[_bow_data_common_pb2.Vector3, _Mapping]] = ..., Transform: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ..., NewDataFlag: bool = ...) -> None: ...
