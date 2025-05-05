from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OctreeNode(_message.Message):
    __slots__ = ["EffectorLink", "RootLink", "Center", "MinX", "MaxX", "MinY", "MaxY", "MinZ", "MaxZ", "Children", "Leaf", "Depth", "MaxDepth", "Reachable", "ValidOctree"]
    EFFECTORLINK_FIELD_NUMBER: _ClassVar[int]
    ROOTLINK_FIELD_NUMBER: _ClassVar[int]
    CENTER_FIELD_NUMBER: _ClassVar[int]
    MINX_FIELD_NUMBER: _ClassVar[int]
    MAXX_FIELD_NUMBER: _ClassVar[int]
    MINY_FIELD_NUMBER: _ClassVar[int]
    MAXY_FIELD_NUMBER: _ClassVar[int]
    MINZ_FIELD_NUMBER: _ClassVar[int]
    MAXZ_FIELD_NUMBER: _ClassVar[int]
    CHILDREN_FIELD_NUMBER: _ClassVar[int]
    LEAF_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    MAXDEPTH_FIELD_NUMBER: _ClassVar[int]
    REACHABLE_FIELD_NUMBER: _ClassVar[int]
    VALIDOCTREE_FIELD_NUMBER: _ClassVar[int]
    EffectorLink: str
    RootLink: str
    Center: Point
    MinX: float
    MaxX: float
    MinY: float
    MaxY: float
    MinZ: float
    MaxZ: float
    Children: _containers.RepeatedCompositeFieldContainer[OctreeNode]
    Leaf: bool
    Depth: int
    MaxDepth: int
    Reachable: bool
    ValidOctree: bool
    def __init__(self, EffectorLink: _Optional[str] = ..., RootLink: _Optional[str] = ..., Center: _Optional[_Union[Point, _Mapping]] = ..., MinX: _Optional[float] = ..., MaxX: _Optional[float] = ..., MinY: _Optional[float] = ..., MaxY: _Optional[float] = ..., MinZ: _Optional[float] = ..., MaxZ: _Optional[float] = ..., Children: _Optional[_Iterable[_Union[OctreeNode, _Mapping]]] = ..., Leaf: bool = ..., Depth: _Optional[int] = ..., MaxDepth: _Optional[int] = ..., Reachable: bool = ..., ValidOctree: bool = ...) -> None: ...

class Point(_message.Message):
    __slots__ = ["X", "y", "Z"]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    X: float
    y: float
    Z: float
    def __init__(self, X: _Optional[float] = ..., y: _Optional[float] = ..., Z: _Optional[float] = ...) -> None: ...

class Workspaces(_message.Message):
    __slots__ = ["Workspaces"]
    WORKSPACES_FIELD_NUMBER: _ClassVar[int]
    Workspaces: _containers.RepeatedCompositeFieldContainer[OctreeNode]
    def __init__(self, Workspaces: _Optional[_Iterable[_Union[OctreeNode, _Mapping]]] = ...) -> None: ...
