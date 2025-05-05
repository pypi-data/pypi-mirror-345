import bow_structs_pb2 as _bow_structs_pb2
import bow_robot_pb2 as _bow_robot_pb2
import bow_common_pb2 as _bow_common_pb2
import bow_client_pb2 as _bow_client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UserDetails(_message.Message):
    __slots__ = ["SecurityToken", "User", "Location"]
    SECURITYTOKEN_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    SecurityToken: str
    User: _bow_client_pb2.User
    Location: _bow_structs_pb2.Location
    def __init__(self, SecurityToken: _Optional[str] = ..., User: _Optional[_Union[_bow_client_pb2.User, _Mapping]] = ..., Location: _Optional[_Union[_bow_structs_pb2.Location, _Mapping]] = ...) -> None: ...

class AppDetails(_message.Message):
    __slots__ = ["SecurityToken", "ID", "Email", "Password", "Name", "Author", "Location", "InputModalities", "OutputModalities", "InternalModalities"]
    SECURITYTOKEN_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    INPUTMODALITIES_FIELD_NUMBER: _ClassVar[int]
    OUTPUTMODALITIES_FIELD_NUMBER: _ClassVar[int]
    INTERNALMODALITIES_FIELD_NUMBER: _ClassVar[int]
    SecurityToken: str
    ID: str
    Email: str
    Password: str
    Name: str
    Author: str
    Location: _bow_structs_pb2.Location
    InputModalities: _containers.RepeatedCompositeFieldContainer[Source]
    OutputModalities: _containers.RepeatedCompositeFieldContainer[Sink]
    InternalModalities: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, SecurityToken: _Optional[str] = ..., ID: _Optional[str] = ..., Email: _Optional[str] = ..., Password: _Optional[str] = ..., Name: _Optional[str] = ..., Author: _Optional[str] = ..., Location: _Optional[_Union[_bow_structs_pb2.Location, _Mapping]] = ..., InputModalities: _Optional[_Iterable[_Union[Source, _Mapping]]] = ..., OutputModalities: _Optional[_Iterable[_Union[Sink, _Mapping]]] = ..., InternalModalities: _Optional[_Iterable[str]] = ...) -> None: ...

class Source(_message.Message):
    __slots__ = ["SourceID", "InputModalities"]
    SOURCEID_FIELD_NUMBER: _ClassVar[int]
    INPUTMODALITIES_FIELD_NUMBER: _ClassVar[int]
    SourceID: str
    InputModalities: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, SourceID: _Optional[str] = ..., InputModalities: _Optional[_Iterable[str]] = ...) -> None: ...

class Sink(_message.Message):
    __slots__ = ["SinkID", "OutputModalities"]
    SINKID_FIELD_NUMBER: _ClassVar[int]
    OUTPUTMODALITIES_FIELD_NUMBER: _ClassVar[int]
    SinkID: str
    OutputModalities: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, SinkID: _Optional[str] = ..., OutputModalities: _Optional[_Iterable[str]] = ...) -> None: ...

class ModuleConfig(_message.Message):
    __slots__ = ["audio_params", "latencyLogging", "useSystemConnection"]
    AUDIO_PARAMS_FIELD_NUMBER: _ClassVar[int]
    LATENCYLOGGING_FIELD_NUMBER: _ClassVar[int]
    USESYSTEMCONNECTION_FIELD_NUMBER: _ClassVar[int]
    audio_params: _bow_structs_pb2.AudioParams
    latencyLogging: bool
    useSystemConnection: bool
    def __init__(self, audio_params: _Optional[_Union[_bow_structs_pb2.AudioParams, _Mapping]] = ..., latencyLogging: bool = ..., useSystemConnection: bool = ...) -> None: ...

class SetupClientProto(_message.Message):
    __slots__ = ["logDir", "audio_params", "latencyLogging", "useSystemConnection"]
    LOGDIR_FIELD_NUMBER: _ClassVar[int]
    AUDIO_PARAMS_FIELD_NUMBER: _ClassVar[int]
    LATENCYLOGGING_FIELD_NUMBER: _ClassVar[int]
    USESYSTEMCONNECTION_FIELD_NUMBER: _ClassVar[int]
    logDir: str
    audio_params: _bow_structs_pb2.AudioParams
    latencyLogging: bool
    useSystemConnection: bool
    def __init__(self, logDir: _Optional[str] = ..., audio_params: _Optional[_Union[_bow_structs_pb2.AudioParams, _Mapping]] = ..., latencyLogging: bool = ..., useSystemConnection: bool = ...) -> None: ...

class LoginProto(_message.Message):
    __slots__ = ["username", "password", "systrayLogin"]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    SYSTRAYLOGIN_FIELD_NUMBER: _ClassVar[int]
    username: str
    password: str
    systrayLogin: bool
    def __init__(self, username: _Optional[str] = ..., password: _Optional[str] = ..., systrayLogin: bool = ...) -> None: ...

class GetRobotsProtoRequest(_message.Message):
    __slots__ = ["getLocal", "getRemote", "systrayRobot", "georange"]
    GETLOCAL_FIELD_NUMBER: _ClassVar[int]
    GETREMOTE_FIELD_NUMBER: _ClassVar[int]
    SYSTRAYROBOT_FIELD_NUMBER: _ClassVar[int]
    GEORANGE_FIELD_NUMBER: _ClassVar[int]
    getLocal: bool
    getRemote: bool
    systrayRobot: bool
    georange: _bow_structs_pb2.GeoStruct
    def __init__(self, getLocal: bool = ..., getRemote: bool = ..., systrayRobot: bool = ..., georange: _Optional[_Union[_bow_structs_pb2.GeoStruct, _Mapping]] = ...) -> None: ...

class GetRobotsProtoReply(_message.Message):
    __slots__ = ["robots", "localSearchError", "remoteSearchError"]
    ROBOTS_FIELD_NUMBER: _ClassVar[int]
    LOCALSEARCHERROR_FIELD_NUMBER: _ClassVar[int]
    REMOTESEARCHERROR_FIELD_NUMBER: _ClassVar[int]
    robots: _containers.RepeatedCompositeFieldContainer[_bow_robot_pb2.Robot]
    localSearchError: _bow_common_pb2.Error
    remoteSearchError: _bow_common_pb2.Error
    def __init__(self, robots: _Optional[_Iterable[_Union[_bow_robot_pb2.Robot, _Mapping]]] = ..., localSearchError: _Optional[_Union[_bow_common_pb2.Error, _Mapping]] = ..., remoteSearchError: _Optional[_Union[_bow_common_pb2.Error, _Mapping]] = ...) -> None: ...

class ChosenRobotProto(_message.Message):
    __slots__ = ["chosenOne"]
    CHOSENONE_FIELD_NUMBER: _ClassVar[int]
    chosenOne: _bow_robot_pb2.Robot
    def __init__(self, chosenOne: _Optional[_Union[_bow_robot_pb2.Robot, _Mapping]] = ...) -> None: ...

class OpenModalityProto(_message.Message):
    __slots__ = ["modalityName", "fps"]
    MODALITYNAME_FIELD_NUMBER: _ClassVar[int]
    FPS_FIELD_NUMBER: _ClassVar[int]
    modalityName: str
    fps: int
    def __init__(self, modalityName: _Optional[str] = ..., fps: _Optional[int] = ...) -> None: ...

class GetModalityProto(_message.Message):
    __slots__ = ["sample", "error"]
    SAMPLE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    sample: _bow_structs_pb2.DataMessage
    error: _bow_common_pb2.Error
    def __init__(self, sample: _Optional[_Union[_bow_structs_pb2.DataMessage, _Mapping]] = ..., error: _Optional[_Union[_bow_common_pb2.Error, _Mapping]] = ...) -> None: ...

class ActionProto(_message.Message):
    __slots__ = ["sample", "modalityName", "error"]
    SAMPLE_FIELD_NUMBER: _ClassVar[int]
    MODALITYNAME_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    sample: _bow_structs_pb2.DataMessage
    modalityName: str
    error: _bow_common_pb2.Error
    def __init__(self, sample: _Optional[_Union[_bow_structs_pb2.DataMessage, _Mapping]] = ..., modalityName: _Optional[str] = ..., error: _Optional[_Union[_bow_common_pb2.Error, _Mapping]] = ...) -> None: ...

class UserAction(_message.Message):
    __slots__ = ["tokentype", "action", "user", "password", "token", "error"]
    TOKENTYPE_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    tokentype: int
    action: int
    user: _bow_client_pb2.User
    password: str
    token: str
    error: _bow_common_pb2.Error
    def __init__(self, tokentype: _Optional[int] = ..., action: _Optional[int] = ..., user: _Optional[_Union[_bow_client_pb2.User, _Mapping]] = ..., password: _Optional[str] = ..., token: _Optional[str] = ..., error: _Optional[_Union[_bow_common_pb2.Error, _Mapping]] = ...) -> None: ...
