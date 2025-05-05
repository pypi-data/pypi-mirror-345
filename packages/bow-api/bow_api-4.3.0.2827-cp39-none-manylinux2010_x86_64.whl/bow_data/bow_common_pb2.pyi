from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Error(_message.Message):
    __slots__ = ["Success", "Code", "Description"]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    Success: bool
    Code: int
    Description: str
    def __init__(self, Success: bool = ..., Code: _Optional[int] = ..., Description: _Optional[str] = ...) -> None: ...

class VersionInfo(_message.Message):
    __slots__ = ["CoreVersion", "RobotVersion", "ClientVersion", "ClientLanguage", "DriverVersion", "DriverLanguage"]
    COREVERSION_FIELD_NUMBER: _ClassVar[int]
    ROBOTVERSION_FIELD_NUMBER: _ClassVar[int]
    CLIENTVERSION_FIELD_NUMBER: _ClassVar[int]
    CLIENTLANGUAGE_FIELD_NUMBER: _ClassVar[int]
    DRIVERVERSION_FIELD_NUMBER: _ClassVar[int]
    DRIVERLANGUAGE_FIELD_NUMBER: _ClassVar[int]
    CoreVersion: str
    RobotVersion: str
    ClientVersion: str
    ClientLanguage: str
    DriverVersion: str
    DriverLanguage: str
    def __init__(self, CoreVersion: _Optional[str] = ..., RobotVersion: _Optional[str] = ..., ClientVersion: _Optional[str] = ..., ClientLanguage: _Optional[str] = ..., DriverVersion: _Optional[str] = ..., DriverLanguage: _Optional[str] = ...) -> None: ...
