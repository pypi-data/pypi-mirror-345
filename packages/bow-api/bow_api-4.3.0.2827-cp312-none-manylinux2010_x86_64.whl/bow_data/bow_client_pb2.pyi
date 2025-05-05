import bow_structs_pb2 as _bow_structs_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SubscriptionTier(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    Lite: _ClassVar[SubscriptionTier]
    STANDARD: _ClassVar[SubscriptionTier]
    PRO: _ClassVar[SubscriptionTier]
Lite: SubscriptionTier
STANDARD: SubscriptionTier
PRO: SubscriptionTier

class User(_message.Message):
    __slots__ = ["user_id", "email", "password", "name", "year_born", "country", "marketing", "termsagreed", "company", "profession", "join_date", "email_validated", "subscription"]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    YEAR_BORN_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    MARKETING_FIELD_NUMBER: _ClassVar[int]
    TERMSAGREED_FIELD_NUMBER: _ClassVar[int]
    COMPANY_FIELD_NUMBER: _ClassVar[int]
    PROFESSION_FIELD_NUMBER: _ClassVar[int]
    JOIN_DATE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_VALIDATED_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    email: str
    password: str
    name: str
    year_born: int
    country: str
    marketing: bool
    termsagreed: bool
    company: str
    profession: str
    join_date: int
    email_validated: bool
    subscription: SubscriptionTier
    def __init__(self, user_id: _Optional[str] = ..., email: _Optional[str] = ..., password: _Optional[str] = ..., name: _Optional[str] = ..., year_born: _Optional[int] = ..., country: _Optional[str] = ..., marketing: bool = ..., termsagreed: bool = ..., company: _Optional[str] = ..., profession: _Optional[str] = ..., join_date: _Optional[int] = ..., email_validated: bool = ..., subscription: _Optional[_Union[SubscriptionTier, str]] = ...) -> None: ...

class UserLicenses(_message.Message):
    __slots__ = ["Email", "asset_licenses", "robot_licenses", "shared_robot_licenses"]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    ASSET_LICENSES_FIELD_NUMBER: _ClassVar[int]
    ROBOT_LICENSES_FIELD_NUMBER: _ClassVar[int]
    SHARED_ROBOT_LICENSES_FIELD_NUMBER: _ClassVar[int]
    Email: str
    asset_licenses: _containers.RepeatedCompositeFieldContainer[_bow_structs_pb2.AssetLicense]
    robot_licenses: _containers.RepeatedCompositeFieldContainer[_bow_structs_pb2.RobotLicense]
    shared_robot_licenses: _containers.RepeatedCompositeFieldContainer[_bow_structs_pb2.RobotLicense]
    def __init__(self, Email: _Optional[str] = ..., asset_licenses: _Optional[_Iterable[_Union[_bow_structs_pb2.AssetLicense, _Mapping]]] = ..., robot_licenses: _Optional[_Iterable[_Union[_bow_structs_pb2.RobotLicense, _Mapping]]] = ..., shared_robot_licenses: _Optional[_Iterable[_Union[_bow_structs_pb2.RobotLicense, _Mapping]]] = ...) -> None: ...
