import bow_data_common_pb2 as _bow_data_common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Battery(_message.Message):
    __slots__ = ["Voltage", "Current", "Charge", "Percentage", "Present", "SupplyStatus"]
    class SupplyStatusEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        Unknown: _ClassVar[Battery.SupplyStatusEnum]
        Charging: _ClassVar[Battery.SupplyStatusEnum]
        Discharging: _ClassVar[Battery.SupplyStatusEnum]
        Not_Charging: _ClassVar[Battery.SupplyStatusEnum]
        Complete: _ClassVar[Battery.SupplyStatusEnum]
    Unknown: Battery.SupplyStatusEnum
    Charging: Battery.SupplyStatusEnum
    Discharging: Battery.SupplyStatusEnum
    Not_Charging: Battery.SupplyStatusEnum
    Complete: Battery.SupplyStatusEnum
    VOLTAGE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_FIELD_NUMBER: _ClassVar[int]
    CHARGE_FIELD_NUMBER: _ClassVar[int]
    PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    PRESENT_FIELD_NUMBER: _ClassVar[int]
    SUPPLYSTATUS_FIELD_NUMBER: _ClassVar[int]
    Voltage: float
    Current: float
    Charge: float
    Percentage: float
    Present: bool
    SupplyStatus: Battery.SupplyStatusEnum
    def __init__(self, Voltage: _Optional[float] = ..., Current: _Optional[float] = ..., Charge: _Optional[float] = ..., Percentage: _Optional[float] = ..., Present: bool = ..., SupplyStatus: _Optional[_Union[Battery.SupplyStatusEnum, str]] = ...) -> None: ...

class InteroceptionSample(_message.Message):
    __slots__ = ["Env", "battery", "Error"]
    ENV_FIELD_NUMBER: _ClassVar[int]
    BATTERY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    Env: _containers.RepeatedCompositeFieldContainer[_bow_data_common_pb2.Environment]
    battery: Battery
    Error: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, Env: _Optional[_Iterable[_Union[_bow_data_common_pb2.Environment, _Mapping]]] = ..., battery: _Optional[_Union[Battery, _Mapping]] = ..., Error: _Optional[_Iterable[str]] = ...) -> None: ...
