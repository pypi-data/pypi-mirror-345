import bow_common_pb2 as _bow_common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DataMessage(_message.Message):
    __slots__ = ["data_type", "data", "timestamp", "RecordFlag", "PlaybackFlag", "PlaybackActionName"]
    class DataType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        UNKNOWN: _ClassVar[DataMessage.DataType]
        IMAGE: _ClassVar[DataMessage.DataType]
        AUDIO: _ClassVar[DataMessage.DataType]
        STRING: _ClassVar[DataMessage.DataType]
        FLOAT32ARR: _ClassVar[DataMessage.DataType]
        INT64ARR: _ClassVar[DataMessage.DataType]
        COMMAND: _ClassVar[DataMessage.DataType]
        MOTOR: _ClassVar[DataMessage.DataType]
        BLOB: _ClassVar[DataMessage.DataType]
        PROPRIOCEPTION: _ClassVar[DataMessage.DataType]
        TACTILE: _ClassVar[DataMessage.DataType]
        INTEROCEPTION: _ClassVar[DataMessage.DataType]
        EXTEROCEPTION: _ClassVar[DataMessage.DataType]
    UNKNOWN: DataMessage.DataType
    IMAGE: DataMessage.DataType
    AUDIO: DataMessage.DataType
    STRING: DataMessage.DataType
    FLOAT32ARR: DataMessage.DataType
    INT64ARR: DataMessage.DataType
    COMMAND: DataMessage.DataType
    MOTOR: DataMessage.DataType
    BLOB: DataMessage.DataType
    PROPRIOCEPTION: DataMessage.DataType
    TACTILE: DataMessage.DataType
    INTEROCEPTION: DataMessage.DataType
    EXTEROCEPTION: DataMessage.DataType
    DATA_TYPE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RECORDFLAG_FIELD_NUMBER: _ClassVar[int]
    PLAYBACKFLAG_FIELD_NUMBER: _ClassVar[int]
    PLAYBACKACTIONNAME_FIELD_NUMBER: _ClassVar[int]
    data_type: DataMessage.DataType
    data: bytes
    timestamp: int
    RecordFlag: bool
    PlaybackFlag: bool
    PlaybackActionName: str
    def __init__(self, data_type: _Optional[_Union[DataMessage.DataType, str]] = ..., data: _Optional[bytes] = ..., timestamp: _Optional[int] = ..., RecordFlag: bool = ..., PlaybackFlag: bool = ..., PlaybackActionName: _Optional[str] = ...) -> None: ...

class Command(_message.Message):
    __slots__ = ["command", "timestamp"]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    command: str
    timestamp: int
    def __init__(self, command: _Optional[str] = ..., timestamp: _Optional[int] = ...) -> None: ...

class DataArray(_message.Message):
    __slots__ = ["data"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[DataMessage]
    def __init__(self, data: _Optional[_Iterable[_Union[DataMessage, _Mapping]]] = ...) -> None: ...

class Location(_message.Message):
    __slots__ = ["ip", "hostname", "city", "region", "country", "loc", "postal", "org"]
    IP_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    LOC_FIELD_NUMBER: _ClassVar[int]
    POSTAL_FIELD_NUMBER: _ClassVar[int]
    ORG_FIELD_NUMBER: _ClassVar[int]
    ip: str
    hostname: str
    city: str
    region: str
    country: str
    loc: str
    postal: str
    org: str
    def __init__(self, ip: _Optional[str] = ..., hostname: _Optional[str] = ..., city: _Optional[str] = ..., region: _Optional[str] = ..., country: _Optional[str] = ..., loc: _Optional[str] = ..., postal: _Optional[str] = ..., org: _Optional[str] = ...) -> None: ...

class CalendarEntry(_message.Message):
    __slots__ = ["robotID", "unixStart", "unixEnd", "modalities", "recipient", "issuer"]
    ROBOTID_FIELD_NUMBER: _ClassVar[int]
    UNIXSTART_FIELD_NUMBER: _ClassVar[int]
    UNIXEND_FIELD_NUMBER: _ClassVar[int]
    MODALITIES_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_FIELD_NUMBER: _ClassVar[int]
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    robotID: str
    unixStart: int
    unixEnd: int
    modalities: _containers.RepeatedScalarFieldContainer[str]
    recipient: str
    issuer: str
    def __init__(self, robotID: _Optional[str] = ..., unixStart: _Optional[int] = ..., unixEnd: _Optional[int] = ..., modalities: _Optional[_Iterable[str]] = ..., recipient: _Optional[str] = ..., issuer: _Optional[str] = ...) -> None: ...

class AudioParams(_message.Message):
    __slots__ = ["Backends", "SampleRate", "Channels", "SizeInFrames", "TransmitRate", "captureModality", "sinkModality", "deviceID"]
    BACKENDS_FIELD_NUMBER: _ClassVar[int]
    SAMPLERATE_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    SIZEINFRAMES_FIELD_NUMBER: _ClassVar[int]
    TRANSMITRATE_FIELD_NUMBER: _ClassVar[int]
    CAPTUREMODALITY_FIELD_NUMBER: _ClassVar[int]
    SINKMODALITY_FIELD_NUMBER: _ClassVar[int]
    DEVICEID_FIELD_NUMBER: _ClassVar[int]
    Backends: _containers.RepeatedScalarFieldContainer[str]
    SampleRate: int
    Channels: int
    SizeInFrames: bool
    TransmitRate: int
    captureModality: str
    sinkModality: str
    deviceID: str
    def __init__(self, Backends: _Optional[_Iterable[str]] = ..., SampleRate: _Optional[int] = ..., Channels: _Optional[int] = ..., SizeInFrames: bool = ..., TransmitRate: _Optional[int] = ..., captureModality: _Optional[str] = ..., sinkModality: _Optional[str] = ..., deviceID: _Optional[str] = ...) -> None: ...

class GeoStruct(_message.Message):
    __slots__ = ["UpperLat", "LowerLat", "UpperLong", "LowerLong"]
    UPPERLAT_FIELD_NUMBER: _ClassVar[int]
    LOWERLAT_FIELD_NUMBER: _ClassVar[int]
    UPPERLONG_FIELD_NUMBER: _ClassVar[int]
    LOWERLONG_FIELD_NUMBER: _ClassVar[int]
    UpperLat: float
    LowerLat: float
    UpperLong: float
    LowerLong: float
    def __init__(self, UpperLat: _Optional[float] = ..., LowerLat: _Optional[float] = ..., UpperLong: _Optional[float] = ..., LowerLong: _Optional[float] = ...) -> None: ...

class AssetLicense(_message.Message):
    __slots__ = ["asset_id", "asset_license"]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    ASSET_LICENSE_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    asset_license: License
    def __init__(self, asset_id: _Optional[str] = ..., asset_license: _Optional[_Union[License, _Mapping]] = ...) -> None: ...

class RobotLicense(_message.Message):
    __slots__ = ["robot_id", "asset_id", "robot_license", "robot_make", "robot_model", "pair_code", "paired_status", "isFlexible"]
    ROBOT_ID_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    ROBOT_LICENSE_FIELD_NUMBER: _ClassVar[int]
    ROBOT_MAKE_FIELD_NUMBER: _ClassVar[int]
    ROBOT_MODEL_FIELD_NUMBER: _ClassVar[int]
    PAIR_CODE_FIELD_NUMBER: _ClassVar[int]
    PAIRED_STATUS_FIELD_NUMBER: _ClassVar[int]
    ISFLEXIBLE_FIELD_NUMBER: _ClassVar[int]
    robot_id: str
    asset_id: str
    robot_license: License
    robot_make: str
    robot_model: str
    pair_code: str
    paired_status: bool
    isFlexible: bool
    def __init__(self, robot_id: _Optional[str] = ..., asset_id: _Optional[str] = ..., robot_license: _Optional[_Union[License, _Mapping]] = ..., robot_make: _Optional[str] = ..., robot_model: _Optional[str] = ..., pair_code: _Optional[str] = ..., paired_status: bool = ..., isFlexible: bool = ...) -> None: ...

class License(_message.Message):
    __slots__ = ["license_id", "start_date", "duration", "end_date", "reseller"]
    LICENSE_ID_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    RESELLER_FIELD_NUMBER: _ClassVar[int]
    license_id: str
    start_date: int
    duration: int
    end_date: int
    reseller: ResellerInfo
    def __init__(self, license_id: _Optional[str] = ..., start_date: _Optional[int] = ..., duration: _Optional[int] = ..., end_date: _Optional[int] = ..., reseller: _Optional[_Union[ResellerInfo, _Mapping]] = ...) -> None: ...

class Share(_message.Message):
    __slots__ = ["recipient_email", "duration"]
    RECIPIENT_EMAIL_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    recipient_email: str
    duration: int
    def __init__(self, recipient_email: _Optional[str] = ..., duration: _Optional[int] = ...) -> None: ...

class ICEDetails(_message.Message):
    __slots__ = ["details"]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    details: str
    def __init__(self, details: _Optional[str] = ...) -> None: ...

class Asset(_message.Message):
    __slots__ = ["id", "type", "name", "description", "author", "license", "make", "model", "artifacts"]
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    LICENSE_FIELD_NUMBER: _ClassVar[int]
    MAKE_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    ARTIFACTS_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    name: str
    description: str
    author: str
    license: str
    make: str
    model: str
    artifacts: _containers.RepeatedCompositeFieldContainer[Artifact]
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., author: _Optional[str] = ..., license: _Optional[str] = ..., make: _Optional[str] = ..., model: _Optional[str] = ..., artifacts: _Optional[_Iterable[_Union[Artifact, _Mapping]]] = ...) -> None: ...

class Artifact(_message.Message):
    __slots__ = ["path", "asset_id", "OS", "Arch", "VersionMajor", "VersionMinor", "VersionPatch", "language", "timestamp", "checksum"]
    PATH_FIELD_NUMBER: _ClassVar[int]
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    OS_FIELD_NUMBER: _ClassVar[int]
    ARCH_FIELD_NUMBER: _ClassVar[int]
    VERSIONMAJOR_FIELD_NUMBER: _ClassVar[int]
    VERSIONMINOR_FIELD_NUMBER: _ClassVar[int]
    VERSIONPATCH_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CHECKSUM_FIELD_NUMBER: _ClassVar[int]
    path: str
    asset_id: str
    OS: str
    Arch: str
    VersionMajor: int
    VersionMinor: int
    VersionPatch: int
    language: str
    timestamp: int
    checksum: bytes
    def __init__(self, path: _Optional[str] = ..., asset_id: _Optional[str] = ..., OS: _Optional[str] = ..., Arch: _Optional[str] = ..., VersionMajor: _Optional[int] = ..., VersionMinor: _Optional[int] = ..., VersionPatch: _Optional[int] = ..., language: _Optional[str] = ..., timestamp: _Optional[int] = ..., checksum: _Optional[bytes] = ...) -> None: ...

class Performance(_message.Message):
    __slots__ = ["Name", "Description", "AverageFPS", "AverageLatency", "FramesDropped"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    AVERAGEFPS_FIELD_NUMBER: _ClassVar[int]
    AVERAGELATENCY_FIELD_NUMBER: _ClassVar[int]
    FRAMESDROPPED_FIELD_NUMBER: _ClassVar[int]
    Name: str
    Description: str
    AverageFPS: float
    AverageLatency: float
    FramesDropped: float
    def __init__(self, Name: _Optional[str] = ..., Description: _Optional[str] = ..., AverageFPS: _Optional[float] = ..., AverageLatency: _Optional[float] = ..., FramesDropped: _Optional[float] = ...) -> None: ...

class PerformanceReportProto(_message.Message):
    __slots__ = ["robotModalityPerformanceArray", "error"]
    ROBOTMODALITYPERFORMANCEARRAY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    robotModalityPerformanceArray: _containers.RepeatedCompositeFieldContainer[Performance]
    error: _bow_common_pb2.Error
    def __init__(self, robotModalityPerformanceArray: _Optional[_Iterable[_Union[Performance, _Mapping]]] = ..., error: _Optional[_Union[_bow_common_pb2.Error, _Mapping]] = ...) -> None: ...

class ResellerInfo(_message.Message):
    __slots__ = ["CommissionName", "CommissionRegion", "ResellerName", "ResellerRegion", "IssueDate", "AssignedTo"]
    COMMISSIONNAME_FIELD_NUMBER: _ClassVar[int]
    COMMISSIONREGION_FIELD_NUMBER: _ClassVar[int]
    RESELLERNAME_FIELD_NUMBER: _ClassVar[int]
    RESELLERREGION_FIELD_NUMBER: _ClassVar[int]
    ISSUEDATE_FIELD_NUMBER: _ClassVar[int]
    ASSIGNEDTO_FIELD_NUMBER: _ClassVar[int]
    CommissionName: str
    CommissionRegion: str
    ResellerName: str
    ResellerRegion: str
    IssueDate: int
    AssignedTo: str
    def __init__(self, CommissionName: _Optional[str] = ..., CommissionRegion: _Optional[str] = ..., ResellerName: _Optional[str] = ..., ResellerRegion: _Optional[str] = ..., IssueDate: _Optional[int] = ..., AssignedTo: _Optional[str] = ...) -> None: ...
