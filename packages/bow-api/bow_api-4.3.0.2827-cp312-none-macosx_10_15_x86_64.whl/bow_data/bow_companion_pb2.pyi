import bow_common_pb2 as _bow_common_pb2
import bow_structs_pb2 as _bow_structs_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DriverMessage(_message.Message):
    __slots__ = ["Action", "Performance", "DriverActive", "version", "Error", "IP", "port"]
    class DriverAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        GET_PERFORMANCE: _ClassVar[DriverMessage.DriverAction]
        CHANGE_DRIVER_STATE: _ClassVar[DriverMessage.DriverAction]
        INSTALL_UPDATE: _ClassVar[DriverMessage.DriverAction]
    GET_PERFORMANCE: DriverMessage.DriverAction
    CHANGE_DRIVER_STATE: DriverMessage.DriverAction
    INSTALL_UPDATE: DriverMessage.DriverAction
    class DriverState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        START: _ClassVar[DriverMessage.DriverState]
        STOP: _ClassVar[DriverMessage.DriverState]
        RESTART: _ClassVar[DriverMessage.DriverState]
    START: DriverMessage.DriverState
    STOP: DriverMessage.DriverState
    RESTART: DriverMessage.DriverState
    ACTION_FIELD_NUMBER: _ClassVar[int]
    PERFORMANCE_FIELD_NUMBER: _ClassVar[int]
    DRIVERACTIVE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    Action: DriverMessage.DriverAction
    Performance: _containers.RepeatedCompositeFieldContainer[_bow_structs_pb2.Performance]
    DriverActive: bool
    version: _bow_common_pb2.VersionInfo
    Error: _bow_common_pb2.Error
    IP: str
    port: str
    def __init__(self, Action: _Optional[_Union[DriverMessage.DriverAction, str]] = ..., Performance: _Optional[_Iterable[_Union[_bow_structs_pb2.Performance, _Mapping]]] = ..., DriverActive: bool = ..., version: _Optional[_Union[_bow_common_pb2.VersionInfo, _Mapping]] = ..., Error: _Optional[_Union[_bow_common_pb2.Error, _Mapping]] = ..., IP: _Optional[str] = ..., port: _Optional[str] = ...) -> None: ...

class InstallDriverMessage(_message.Message):
    __slots__ = ["isUpdate", "username", "password", "robotID", "robotName", "robotUser", "robotPassword", "robotIP", "pairCode", "storeLocally", "logDir"]
    ISUPDATE_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    ROBOTID_FIELD_NUMBER: _ClassVar[int]
    ROBOTNAME_FIELD_NUMBER: _ClassVar[int]
    ROBOTUSER_FIELD_NUMBER: _ClassVar[int]
    ROBOTPASSWORD_FIELD_NUMBER: _ClassVar[int]
    ROBOTIP_FIELD_NUMBER: _ClassVar[int]
    PAIRCODE_FIELD_NUMBER: _ClassVar[int]
    STORELOCALLY_FIELD_NUMBER: _ClassVar[int]
    LOGDIR_FIELD_NUMBER: _ClassVar[int]
    isUpdate: bool
    username: str
    password: str
    robotID: str
    robotName: str
    robotUser: str
    robotPassword: str
    robotIP: str
    pairCode: str
    storeLocally: bool
    logDir: str
    def __init__(self, isUpdate: bool = ..., username: _Optional[str] = ..., password: _Optional[str] = ..., robotID: _Optional[str] = ..., robotName: _Optional[str] = ..., robotUser: _Optional[str] = ..., robotPassword: _Optional[str] = ..., robotIP: _Optional[str] = ..., pairCode: _Optional[str] = ..., storeLocally: bool = ..., logDir: _Optional[str] = ...) -> None: ...
