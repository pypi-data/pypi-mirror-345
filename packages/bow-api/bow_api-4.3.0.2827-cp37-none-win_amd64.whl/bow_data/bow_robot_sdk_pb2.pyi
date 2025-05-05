import bow_robot_pb2 as _bow_robot_pb2
import bow_common_pb2 as _bow_common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SetupRobotProto(_message.Message):
    __slots__ = ["logDir", "Debug"]
    LOGDIR_FIELD_NUMBER: _ClassVar[int]
    DEBUG_FIELD_NUMBER: _ClassVar[int]
    logDir: str
    Debug: bool
    def __init__(self, logDir: _Optional[str] = ..., Debug: bool = ...) -> None: ...

class StartRobotCommsProto(_message.Message):
    __slots__ = ["startLocal", "startRemote", "robot"]
    STARTLOCAL_FIELD_NUMBER: _ClassVar[int]
    STARTREMOTE_FIELD_NUMBER: _ClassVar[int]
    ROBOT_FIELD_NUMBER: _ClassVar[int]
    startLocal: bool
    startRemote: bool
    robot: _bow_robot_pb2.Robot
    def __init__(self, startLocal: bool = ..., startRemote: bool = ..., robot: _Optional[_Union[_bow_robot_pb2.Robot, _Mapping]] = ...) -> None: ...

class RobotConfigProto(_message.Message):
    __slots__ = ["robot", "error"]
    ROBOT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    robot: _bow_robot_pb2.Robot
    error: _bow_common_pb2.Error
    def __init__(self, robot: _Optional[_Union[_bow_robot_pb2.Robot, _Mapping]] = ..., error: _Optional[_Union[_bow_common_pb2.Error, _Mapping]] = ...) -> None: ...

class TestRobot(_message.Message):
    __slots__ = ["robot_id", "make"]
    ROBOT_ID_FIELD_NUMBER: _ClassVar[int]
    MAKE_FIELD_NUMBER: _ClassVar[int]
    robot_id: str
    make: str
    def __init__(self, robot_id: _Optional[str] = ..., make: _Optional[str] = ...) -> None: ...

class ChangeConfigProto(_message.Message):
    __slots__ = ["robot", "startLocal", "startRemote"]
    ROBOT_FIELD_NUMBER: _ClassVar[int]
    STARTLOCAL_FIELD_NUMBER: _ClassVar[int]
    STARTREMOTE_FIELD_NUMBER: _ClassVar[int]
    robot: TestRobot
    startLocal: bool
    startRemote: bool
    def __init__(self, robot: _Optional[_Union[TestRobot, _Mapping]] = ..., startLocal: bool = ..., startRemote: bool = ...) -> None: ...
