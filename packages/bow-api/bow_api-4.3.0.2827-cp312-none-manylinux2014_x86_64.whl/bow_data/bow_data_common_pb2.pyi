from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RelativeToEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    BASE: _ClassVar[RelativeToEnum]
    HEAD: _ClassVar[RelativeToEnum]
    END_EFFECTOR: _ClassVar[RelativeToEnum]
    END_EFFECTOR_LEFT: _ClassVar[RelativeToEnum]
    END_EFFECTOR_RIGHT: _ClassVar[RelativeToEnum]
    TORSO: _ClassVar[RelativeToEnum]

class StereoDesignationEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    NONE: _ClassVar[StereoDesignationEnum]
    LEFT: _ClassVar[StereoDesignationEnum]
    RIGHT: _ClassVar[StereoDesignationEnum]

class ObjectiveStatusEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    NO_OBJECTIVE: _ClassVar[ObjectiveStatusEnum]
    PLANNING: _ClassVar[ObjectiveStatusEnum]
    IN_PROGRESS: _ClassVar[ObjectiveStatusEnum]
    COLLISION_ERROR: _ClassVar[ObjectiveStatusEnum]
    ERROR: _ClassVar[ObjectiveStatusEnum]
    WARNING: _ClassVar[ObjectiveStatusEnum]
    FINISHED: _ClassVar[ObjectiveStatusEnum]

class ControllerEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    POSITION_CONTROLLER: _ClassVar[ControllerEnum]
    VELOCITY_CONTROLLER: _ClassVar[ControllerEnum]
    TORQUE_CONTROLLER: _ClassVar[ControllerEnum]
BASE: RelativeToEnum
HEAD: RelativeToEnum
END_EFFECTOR: RelativeToEnum
END_EFFECTOR_LEFT: RelativeToEnum
END_EFFECTOR_RIGHT: RelativeToEnum
TORSO: RelativeToEnum
NONE: StereoDesignationEnum
LEFT: StereoDesignationEnum
RIGHT: StereoDesignationEnum
NO_OBJECTIVE: ObjectiveStatusEnum
PLANNING: ObjectiveStatusEnum
IN_PROGRESS: ObjectiveStatusEnum
COLLISION_ERROR: ObjectiveStatusEnum
ERROR: ObjectiveStatusEnum
WARNING: ObjectiveStatusEnum
FINISHED: ObjectiveStatusEnum
POSITION_CONTROLLER: ControllerEnum
VELOCITY_CONTROLLER: ControllerEnum
TORQUE_CONTROLLER: ControllerEnum

class Vector3(_message.Message):
    __slots__ = ["X", "Y", "Z"]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    X: float
    Y: float
    Z: float
    def __init__(self, X: _Optional[float] = ..., Y: _Optional[float] = ..., Z: _Optional[float] = ...) -> None: ...

class Quaternion(_message.Message):
    __slots__ = ["QuatX", "QuatY", "QuatZ", "QuatW"]
    QUATX_FIELD_NUMBER: _ClassVar[int]
    QUATY_FIELD_NUMBER: _ClassVar[int]
    QUATZ_FIELD_NUMBER: _ClassVar[int]
    QUATW_FIELD_NUMBER: _ClassVar[int]
    QuatX: float
    QuatY: float
    QuatZ: float
    QuatW: float
    def __init__(self, QuatX: _Optional[float] = ..., QuatY: _Optional[float] = ..., QuatZ: _Optional[float] = ..., QuatW: _Optional[float] = ...) -> None: ...

class Transform(_message.Message):
    __slots__ = ["Position", "EulerAngles", "LinkName", "Part"]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    EULERANGLES_FIELD_NUMBER: _ClassVar[int]
    LINKNAME_FIELD_NUMBER: _ClassVar[int]
    PART_FIELD_NUMBER: _ClassVar[int]
    Position: Vector3
    EulerAngles: Vector3
    LinkName: str
    Part: str
    def __init__(self, Position: _Optional[_Union[Vector3, _Mapping]] = ..., EulerAngles: _Optional[_Union[Vector3, _Mapping]] = ..., LinkName: _Optional[str] = ..., Part: _Optional[str] = ...) -> None: ...

class Float32Array(_message.Message):
    __slots__ = ["Data"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    Data: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, Data: _Optional[_Iterable[float]] = ...) -> None: ...

class Int64Array(_message.Message):
    __slots__ = ["Data"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    Data: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, Data: _Optional[_Iterable[int]] = ...) -> None: ...

class Environment(_message.Message):
    __slots__ = ["Source", "Type", "Value", "Transform"]
    class SensorTypeEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        Temperature: _ClassVar[Environment.SensorTypeEnum]
        Pressure: _ClassVar[Environment.SensorTypeEnum]
        Humidity: _ClassVar[Environment.SensorTypeEnum]
    Temperature: Environment.SensorTypeEnum
    Pressure: Environment.SensorTypeEnum
    Humidity: Environment.SensorTypeEnum
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    Source: str
    Type: Environment.SensorTypeEnum
    Value: float
    Transform: Transform
    def __init__(self, Source: _Optional[str] = ..., Type: _Optional[_Union[Environment.SensorTypeEnum, str]] = ..., Value: _Optional[float] = ..., Transform: _Optional[_Union[Transform, _Mapping]] = ...) -> None: ...
