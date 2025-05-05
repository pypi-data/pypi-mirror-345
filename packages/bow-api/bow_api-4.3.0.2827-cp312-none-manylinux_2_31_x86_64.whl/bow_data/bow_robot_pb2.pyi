import bow_structs_pb2 as _bow_structs_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Robot(_message.Message):
    __slots__ = ["robot_id", "make", "model", "name", "hardware_hash", "license", "join_date", "robot_config", "robot_state", "CoreVersion", "RobotVersion", "DriverVersion", "DriverLanguage", "URDFPath", "ObjectivesJson"]
    ROBOT_ID_FIELD_NUMBER: _ClassVar[int]
    MAKE_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    HARDWARE_HASH_FIELD_NUMBER: _ClassVar[int]
    LICENSE_FIELD_NUMBER: _ClassVar[int]
    JOIN_DATE_FIELD_NUMBER: _ClassVar[int]
    ROBOT_CONFIG_FIELD_NUMBER: _ClassVar[int]
    ROBOT_STATE_FIELD_NUMBER: _ClassVar[int]
    COREVERSION_FIELD_NUMBER: _ClassVar[int]
    ROBOTVERSION_FIELD_NUMBER: _ClassVar[int]
    DRIVERVERSION_FIELD_NUMBER: _ClassVar[int]
    DRIVERLANGUAGE_FIELD_NUMBER: _ClassVar[int]
    URDFPATH_FIELD_NUMBER: _ClassVar[int]
    OBJECTIVESJSON_FIELD_NUMBER: _ClassVar[int]
    robot_id: str
    make: str
    model: str
    name: str
    hardware_hash: str
    license: _bow_structs_pb2.License
    join_date: int
    robot_config: RobotConfig
    robot_state: RobotState
    CoreVersion: str
    RobotVersion: str
    DriverVersion: str
    DriverLanguage: str
    URDFPath: str
    ObjectivesJson: str
    def __init__(self, robot_id: _Optional[str] = ..., make: _Optional[str] = ..., model: _Optional[str] = ..., name: _Optional[str] = ..., hardware_hash: _Optional[str] = ..., license: _Optional[_Union[_bow_structs_pb2.License, _Mapping]] = ..., join_date: _Optional[int] = ..., robot_config: _Optional[_Union[RobotConfig, _Mapping]] = ..., robot_state: _Optional[_Union[RobotState, _Mapping]] = ..., CoreVersion: _Optional[str] = ..., RobotVersion: _Optional[str] = ..., DriverVersion: _Optional[str] = ..., DriverLanguage: _Optional[str] = ..., URDFPath: _Optional[str] = ..., ObjectivesJson: _Optional[str] = ...) -> None: ...

class RobotConfig(_message.Message):
    __slots__ = ["enableRemote", "available_public", "input_modalities", "output_modalities", "internal_modalities", "StrAudioParams", "features"]
    ENABLEREMOTE_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_PUBLIC_FIELD_NUMBER: _ClassVar[int]
    INPUT_MODALITIES_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_MODALITIES_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_MODALITIES_FIELD_NUMBER: _ClassVar[int]
    STRAUDIOPARAMS_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    enableRemote: bool
    available_public: bool
    input_modalities: _containers.RepeatedScalarFieldContainer[str]
    output_modalities: _containers.RepeatedScalarFieldContainer[str]
    internal_modalities: _containers.RepeatedScalarFieldContainer[str]
    StrAudioParams: _bow_structs_pb2.AudioParams
    features: str
    def __init__(self, enableRemote: bool = ..., available_public: bool = ..., input_modalities: _Optional[_Iterable[str]] = ..., output_modalities: _Optional[_Iterable[str]] = ..., internal_modalities: _Optional[_Iterable[str]] = ..., StrAudioParams: _Optional[_Union[_bow_structs_pb2.AudioParams, _Mapping]] = ..., features: _Optional[str] = ...) -> None: ...

class RobotState(_message.Message):
    __slots__ = ["available", "location", "IP", "NetworkMode", "MacAddress", "availableUntil"]
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    NETWORKMODE_FIELD_NUMBER: _ClassVar[int]
    MACADDRESS_FIELD_NUMBER: _ClassVar[int]
    AVAILABLEUNTIL_FIELD_NUMBER: _ClassVar[int]
    available: bool
    location: _bow_structs_pb2.Location
    IP: str
    NetworkMode: str
    MacAddress: str
    availableUntil: int
    def __init__(self, available: bool = ..., location: _Optional[_Union[_bow_structs_pb2.Location, _Mapping]] = ..., IP: _Optional[str] = ..., NetworkMode: _Optional[str] = ..., MacAddress: _Optional[str] = ..., availableUntil: _Optional[int] = ...) -> None: ...
