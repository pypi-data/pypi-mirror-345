import bow_data_common_pb2 as _bow_data_common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ImageSamples(_message.Message):
    __slots__ = ["Samples"]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    Samples: _containers.RepeatedCompositeFieldContainer[ImageSample]
    def __init__(self, Samples: _Optional[_Iterable[_Union[ImageSample, _Mapping]]] = ...) -> None: ...

class ImageSample(_message.Message):
    __slots__ = ["Source", "Data", "DataShape", "Compression", "ImageType", "Transform", "FrameNumber", "Designation", "HFOV", "VFOV", "NewDataFlag", "Min", "Max"]
    class CompressionFormatEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        H264: _ClassVar[ImageSample.CompressionFormatEnum]
        VP8: _ClassVar[ImageSample.CompressionFormatEnum]
        VP9: _ClassVar[ImageSample.CompressionFormatEnum]
        JPG: _ClassVar[ImageSample.CompressionFormatEnum]
        RAW: _ClassVar[ImageSample.CompressionFormatEnum]
        H265: _ClassVar[ImageSample.CompressionFormatEnum]
    H264: ImageSample.CompressionFormatEnum
    VP8: ImageSample.CompressionFormatEnum
    VP9: ImageSample.CompressionFormatEnum
    JPG: ImageSample.CompressionFormatEnum
    RAW: ImageSample.CompressionFormatEnum
    H265: ImageSample.CompressionFormatEnum
    class ImageTypeEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        RGB: _ClassVar[ImageSample.ImageTypeEnum]
        DEPTH: _ClassVar[ImageSample.ImageTypeEnum]
        STEREO: _ClassVar[ImageSample.ImageTypeEnum]
        INFRARED: _ClassVar[ImageSample.ImageTypeEnum]
    RGB: ImageSample.ImageTypeEnum
    DEPTH: ImageSample.ImageTypeEnum
    STEREO: ImageSample.ImageTypeEnum
    INFRARED: ImageSample.ImageTypeEnum
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    DATASHAPE_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_FIELD_NUMBER: _ClassVar[int]
    IMAGETYPE_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    FRAMENUMBER_FIELD_NUMBER: _ClassVar[int]
    DESIGNATION_FIELD_NUMBER: _ClassVar[int]
    HFOV_FIELD_NUMBER: _ClassVar[int]
    VFOV_FIELD_NUMBER: _ClassVar[int]
    NEWDATAFLAG_FIELD_NUMBER: _ClassVar[int]
    MIN_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    Source: str
    Data: bytes
    DataShape: _containers.RepeatedScalarFieldContainer[int]
    Compression: ImageSample.CompressionFormatEnum
    ImageType: ImageSample.ImageTypeEnum
    Transform: _bow_data_common_pb2.Transform
    FrameNumber: int
    Designation: _bow_data_common_pb2.StereoDesignationEnum
    HFOV: float
    VFOV: float
    NewDataFlag: bool
    Min: int
    Max: int
    def __init__(self, Source: _Optional[str] = ..., Data: _Optional[bytes] = ..., DataShape: _Optional[_Iterable[int]] = ..., Compression: _Optional[_Union[ImageSample.CompressionFormatEnum, str]] = ..., ImageType: _Optional[_Union[ImageSample.ImageTypeEnum, str]] = ..., Transform: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ..., FrameNumber: _Optional[int] = ..., Designation: _Optional[_Union[_bow_data_common_pb2.StereoDesignationEnum, str]] = ..., HFOV: _Optional[float] = ..., VFOV: _Optional[float] = ..., NewDataFlag: bool = ..., Min: _Optional[int] = ..., Max: _Optional[int] = ...) -> None: ...
