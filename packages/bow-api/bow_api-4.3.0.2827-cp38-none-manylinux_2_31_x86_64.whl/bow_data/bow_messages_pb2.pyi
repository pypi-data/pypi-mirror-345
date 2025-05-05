import bow_common_pb2 as _bow_common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AnimusMessage(_message.Message):
    __slots__ = ["SenderID", "ReceiverID", "ClientType", "Action", "ActionState", "Success", "Data", "Timestamp", "Framecount", "Part", "Error", "Token", "ConnectionID", "CoreVersion", "ClientVersion", "SDKVersion", "SDKLanguage"]
    SENDERID_FIELD_NUMBER: _ClassVar[int]
    RECEIVERID_FIELD_NUMBER: _ClassVar[int]
    CLIENTTYPE_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    ACTIONSTATE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    FRAMECOUNT_FIELD_NUMBER: _ClassVar[int]
    PART_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    CONNECTIONID_FIELD_NUMBER: _ClassVar[int]
    COREVERSION_FIELD_NUMBER: _ClassVar[int]
    CLIENTVERSION_FIELD_NUMBER: _ClassVar[int]
    SDKVERSION_FIELD_NUMBER: _ClassVar[int]
    SDKLANGUAGE_FIELD_NUMBER: _ClassVar[int]
    SenderID: str
    ReceiverID: str
    ClientType: int
    Action: int
    ActionState: int
    Success: bool
    Data: bytes
    Timestamp: int
    Framecount: int
    Part: int
    Error: _bow_common_pb2.Error
    Token: str
    ConnectionID: int
    CoreVersion: str
    ClientVersion: str
    SDKVersion: str
    SDKLanguage: str
    def __init__(self, SenderID: _Optional[str] = ..., ReceiverID: _Optional[str] = ..., ClientType: _Optional[int] = ..., Action: _Optional[int] = ..., ActionState: _Optional[int] = ..., Success: bool = ..., Data: _Optional[bytes] = ..., Timestamp: _Optional[int] = ..., Framecount: _Optional[int] = ..., Part: _Optional[int] = ..., Error: _Optional[_Union[_bow_common_pb2.Error, _Mapping]] = ..., Token: _Optional[str] = ..., ConnectionID: _Optional[int] = ..., CoreVersion: _Optional[str] = ..., ClientVersion: _Optional[str] = ..., SDKVersion: _Optional[str] = ..., SDKLanguage: _Optional[str] = ...) -> None: ...

class RegisterRobotMessage(_message.Message):
    __slots__ = ["ID", "Make", "Model", "Name", "DevHash", "License", "RobotUserEmail", "RobotUserPass", "RobotPairCode", "Error"]
    ID_FIELD_NUMBER: _ClassVar[int]
    MAKE_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DEVHASH_FIELD_NUMBER: _ClassVar[int]
    LICENSE_FIELD_NUMBER: _ClassVar[int]
    ROBOTUSEREMAIL_FIELD_NUMBER: _ClassVar[int]
    ROBOTUSERPASS_FIELD_NUMBER: _ClassVar[int]
    ROBOTPAIRCODE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Make: str
    Model: str
    Name: str
    DevHash: str
    License: str
    RobotUserEmail: str
    RobotUserPass: str
    RobotPairCode: str
    Error: _bow_common_pb2.Error
    def __init__(self, ID: _Optional[str] = ..., Make: _Optional[str] = ..., Model: _Optional[str] = ..., Name: _Optional[str] = ..., DevHash: _Optional[str] = ..., License: _Optional[str] = ..., RobotUserEmail: _Optional[str] = ..., RobotUserPass: _Optional[str] = ..., RobotPairCode: _Optional[str] = ..., Error: _Optional[_Union[_bow_common_pb2.Error, _Mapping]] = ...) -> None: ...

class ScannedRobots(_message.Message):
    __slots__ = ["localRobots", "Error", "username", "password"]
    LOCALROBOTS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    localRobots: _containers.RepeatedCompositeFieldContainer[NetworkRobots]
    Error: _bow_common_pb2.Error
    username: str
    password: str
    def __init__(self, localRobots: _Optional[_Iterable[_Union[NetworkRobots, _Mapping]]] = ..., Error: _Optional[_Union[_bow_common_pb2.Error, _Mapping]] = ..., username: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class NetworkRobots(_message.Message):
    __slots__ = ["ID", "IP", "MacAddress", "Name", "Model", "Make"]
    ID_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    MACADDRESS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    MAKE_FIELD_NUMBER: _ClassVar[int]
    ID: str
    IP: str
    MacAddress: str
    Name: str
    Model: str
    Make: str
    def __init__(self, ID: _Optional[str] = ..., IP: _Optional[str] = ..., MacAddress: _Optional[str] = ..., Name: _Optional[str] = ..., Model: _Optional[str] = ..., Make: _Optional[str] = ...) -> None: ...
