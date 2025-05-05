import bow_data_common_pb2 as _bow_data_common_pb2
import bow_data_octree_pb2 as _bow_data_octree_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ActionEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    GOTO: _ClassVar[ActionEnum]
    TOUCH: _ClassVar[ActionEnum]
    POINT: _ClassVar[ActionEnum]
    LOOK_AT: _ClassVar[ActionEnum]
    GRASP: _ClassVar[ActionEnum]

class BodyPartTypeEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    ROOT: _ClassVar[BodyPartTypeEnum]
    LIMB: _ClassVar[BodyPartTypeEnum]
    GRIPPER: _ClassVar[BodyPartTypeEnum]
    EFFECTOR: _ClassVar[BodyPartTypeEnum]

class GripperModeEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    PERCENTAGE_MODE: _ClassVar[GripperModeEnum]
    TRANSFORM_MODE_WRT_WRIST: _ClassVar[GripperModeEnum]
    TRANSFORM_MODE_WRT_CAPSULE: _ClassVar[GripperModeEnum]
    TRANSFORM_MODE_WRT_CUSTOM_REF: _ClassVar[GripperModeEnum]
    JOINT_MODE: _ClassVar[GripperModeEnum]
GOTO: ActionEnum
TOUCH: ActionEnum
POINT: ActionEnum
LOOK_AT: ActionEnum
GRASP: ActionEnum
ROOT: BodyPartTypeEnum
LIMB: BodyPartTypeEnum
GRIPPER: BodyPartTypeEnum
EFFECTOR: BodyPartTypeEnum
PERCENTAGE_MODE: GripperModeEnum
TRANSFORM_MODE_WRT_WRIST: GripperModeEnum
TRANSFORM_MODE_WRT_CAPSULE: GripperModeEnum
TRANSFORM_MODE_WRT_CUSTOM_REF: GripperModeEnum
JOINT_MODE: GripperModeEnum

class MotorSample(_message.Message):
    __slots__ = ["ControlMode", "Locomotion", "Objectives", "Obstacles", "RawJoints", "WorkspaceReceived", "IKSettings", "GazeTarget", "GripperObjective", "GaitSettings"]
    class ControlModeEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        USE_OBJECTIVE: _ClassVar[MotorSample.ControlModeEnum]
        USE_DIRECT_JOINTS: _ClassVar[MotorSample.ControlModeEnum]
    USE_OBJECTIVE: MotorSample.ControlModeEnum
    USE_DIRECT_JOINTS: MotorSample.ControlModeEnum
    CONTROLMODE_FIELD_NUMBER: _ClassVar[int]
    LOCOMOTION_FIELD_NUMBER: _ClassVar[int]
    OBJECTIVES_FIELD_NUMBER: _ClassVar[int]
    OBSTACLES_FIELD_NUMBER: _ClassVar[int]
    RAWJOINTS_FIELD_NUMBER: _ClassVar[int]
    WORKSPACERECEIVED_FIELD_NUMBER: _ClassVar[int]
    IKSETTINGS_FIELD_NUMBER: _ClassVar[int]
    GAZETARGET_FIELD_NUMBER: _ClassVar[int]
    GRIPPEROBJECTIVE_FIELD_NUMBER: _ClassVar[int]
    GAITSETTINGS_FIELD_NUMBER: _ClassVar[int]
    ControlMode: MotorSample.ControlModeEnum
    Locomotion: VelocityTarget
    Objectives: _containers.RepeatedCompositeFieldContainer[ObjectiveCommand]
    Obstacles: _containers.RepeatedCompositeFieldContainer[Object]
    RawJoints: _containers.RepeatedCompositeFieldContainer[Joint]
    WorkspaceReceived: bool
    IKSettings: IKOptimiser
    GazeTarget: GazeTarget
    GripperObjective: Gripper
    GaitSettings: QuadGait
    def __init__(self, ControlMode: _Optional[_Union[MotorSample.ControlModeEnum, str]] = ..., Locomotion: _Optional[_Union[VelocityTarget, _Mapping]] = ..., Objectives: _Optional[_Iterable[_Union[ObjectiveCommand, _Mapping]]] = ..., Obstacles: _Optional[_Iterable[_Union[Object, _Mapping]]] = ..., RawJoints: _Optional[_Iterable[_Union[Joint, _Mapping]]] = ..., WorkspaceReceived: bool = ..., IKSettings: _Optional[_Union[IKOptimiser, _Mapping]] = ..., GazeTarget: _Optional[_Union[GazeTarget, _Mapping]] = ..., GripperObjective: _Optional[_Union[Gripper, _Mapping]] = ..., GaitSettings: _Optional[_Union[QuadGait, _Mapping]] = ...) -> None: ...

class QuadGait(_message.Message):
    __slots__ = ["UseCustomGait", "CommonXTranslation", "SwingHeight", "StanceDepth", "StanceDuration", "SwingDuration", "NominalHeight", "GaitOrientation"]
    USECUSTOMGAIT_FIELD_NUMBER: _ClassVar[int]
    COMMONXTRANSLATION_FIELD_NUMBER: _ClassVar[int]
    SWINGHEIGHT_FIELD_NUMBER: _ClassVar[int]
    STANCEDEPTH_FIELD_NUMBER: _ClassVar[int]
    STANCEDURATION_FIELD_NUMBER: _ClassVar[int]
    SWINGDURATION_FIELD_NUMBER: _ClassVar[int]
    NOMINALHEIGHT_FIELD_NUMBER: _ClassVar[int]
    GAITORIENTATION_FIELD_NUMBER: _ClassVar[int]
    UseCustomGait: bool
    CommonXTranslation: float
    SwingHeight: float
    StanceDepth: float
    StanceDuration: float
    SwingDuration: float
    NominalHeight: float
    GaitOrientation: _bow_data_common_pb2.Vector3
    def __init__(self, UseCustomGait: bool = ..., CommonXTranslation: _Optional[float] = ..., SwingHeight: _Optional[float] = ..., StanceDepth: _Optional[float] = ..., StanceDuration: _Optional[float] = ..., SwingDuration: _Optional[float] = ..., NominalHeight: _Optional[float] = ..., GaitOrientation: _Optional[_Union[_bow_data_common_pb2.Vector3, _Mapping]] = ...) -> None: ...

class GazeTarget(_message.Message):
    __slots__ = ["GazeVector", "VectorType"]
    class TargetTypeEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        ABSOLUTE: _ClassVar[GazeTarget.TargetTypeEnum]
        RELATIVE: _ClassVar[GazeTarget.TargetTypeEnum]
    ABSOLUTE: GazeTarget.TargetTypeEnum
    RELATIVE: GazeTarget.TargetTypeEnum
    GAZEVECTOR_FIELD_NUMBER: _ClassVar[int]
    VECTORTYPE_FIELD_NUMBER: _ClassVar[int]
    GazeVector: _bow_data_common_pb2.Vector3
    VectorType: GazeTarget.TargetTypeEnum
    def __init__(self, GazeVector: _Optional[_Union[_bow_data_common_pb2.Vector3, _Mapping]] = ..., VectorType: _Optional[_Union[GazeTarget.TargetTypeEnum, str]] = ...) -> None: ...

class ObjectiveCommand(_message.Message):
    __slots__ = ["TargetEffector", "TargetBodyPart", "ControlMode", "PoseTarget", "VelocityTarget", "TorqueTarget", "Enabled", "CustomName"]
    TARGETEFFECTOR_FIELD_NUMBER: _ClassVar[int]
    TARGETBODYPART_FIELD_NUMBER: _ClassVar[int]
    CONTROLMODE_FIELD_NUMBER: _ClassVar[int]
    POSETARGET_FIELD_NUMBER: _ClassVar[int]
    VELOCITYTARGET_FIELD_NUMBER: _ClassVar[int]
    TORQUETARGET_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    CUSTOMNAME_FIELD_NUMBER: _ClassVar[int]
    TargetEffector: str
    TargetBodyPart: str
    ControlMode: _bow_data_common_pb2.ControllerEnum
    PoseTarget: PoseTarget
    VelocityTarget: VelocityTarget
    TorqueTarget: TorqueTarget
    Enabled: bool
    CustomName: str
    def __init__(self, TargetEffector: _Optional[str] = ..., TargetBodyPart: _Optional[str] = ..., ControlMode: _Optional[_Union[_bow_data_common_pb2.ControllerEnum, str]] = ..., PoseTarget: _Optional[_Union[PoseTarget, _Mapping]] = ..., VelocityTarget: _Optional[_Union[VelocityTarget, _Mapping]] = ..., TorqueTarget: _Optional[_Union[TorqueTarget, _Mapping]] = ..., Enabled: bool = ..., CustomName: _Optional[str] = ...) -> None: ...

class IKOptimiser(_message.Message):
    __slots__ = ["Preset", "CustomSettings", "GlobalObjectiveWeights"]
    class OptimiserPreset(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        LOW_LATENCY: _ClassVar[IKOptimiser.OptimiserPreset]
        HIGH_ACCURACY: _ClassVar[IKOptimiser.OptimiserPreset]
        BALANCED: _ClassVar[IKOptimiser.OptimiserPreset]
        CUSTOM: _ClassVar[IKOptimiser.OptimiserPreset]
    LOW_LATENCY: IKOptimiser.OptimiserPreset
    HIGH_ACCURACY: IKOptimiser.OptimiserPreset
    BALANCED: IKOptimiser.OptimiserPreset
    CUSTOM: IKOptimiser.OptimiserPreset
    PRESET_FIELD_NUMBER: _ClassVar[int]
    CUSTOMSETTINGS_FIELD_NUMBER: _ClassVar[int]
    GLOBALOBJECTIVEWEIGHTS_FIELD_NUMBER: _ClassVar[int]
    Preset: IKOptimiser.OptimiserPreset
    CustomSettings: CustomOptimiser
    GlobalObjectiveWeights: GlobalObjectiveWeights
    def __init__(self, Preset: _Optional[_Union[IKOptimiser.OptimiserPreset, str]] = ..., CustomSettings: _Optional[_Union[CustomOptimiser, _Mapping]] = ..., GlobalObjectiveWeights: _Optional[_Union[GlobalObjectiveWeights, _Mapping]] = ...) -> None: ...

class CustomOptimiser(_message.Message):
    __slots__ = ["OptimiserMethod", "Iterations", "UseEvolution"]
    class OptimiserMethodEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        BOUNDED_BFGS: _ClassVar[CustomOptimiser.OptimiserMethodEnum]
        BFGS: _ClassVar[CustomOptimiser.OptimiserMethodEnum]
        LBFGS: _ClassVar[CustomOptimiser.OptimiserMethodEnum]
        GRAD: _ClassVar[CustomOptimiser.OptimiserMethodEnum]
        CG: _ClassVar[CustomOptimiser.OptimiserMethodEnum]
        NM: _ClassVar[CustomOptimiser.OptimiserMethodEnum]
    BOUNDED_BFGS: CustomOptimiser.OptimiserMethodEnum
    BFGS: CustomOptimiser.OptimiserMethodEnum
    LBFGS: CustomOptimiser.OptimiserMethodEnum
    GRAD: CustomOptimiser.OptimiserMethodEnum
    CG: CustomOptimiser.OptimiserMethodEnum
    NM: CustomOptimiser.OptimiserMethodEnum
    OPTIMISERMETHOD_FIELD_NUMBER: _ClassVar[int]
    ITERATIONS_FIELD_NUMBER: _ClassVar[int]
    USEEVOLUTION_FIELD_NUMBER: _ClassVar[int]
    OptimiserMethod: CustomOptimiser.OptimiserMethodEnum
    Iterations: int
    UseEvolution: bool
    def __init__(self, OptimiserMethod: _Optional[_Union[CustomOptimiser.OptimiserMethodEnum, str]] = ..., Iterations: _Optional[int] = ..., UseEvolution: bool = ...) -> None: ...

class PoseTarget(_message.Message):
    __slots__ = ["Action", "TargetType", "TargetScheduleType", "Transform", "Object", "MovementDurationMs", "TargetAccuracy", "LocalObjectiveWeights"]
    class TargetTypeEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        TRANSFORM: _ClassVar[PoseTarget.TargetTypeEnum]
        CAPSULE: _ClassVar[PoseTarget.TargetTypeEnum]
    TRANSFORM: PoseTarget.TargetTypeEnum
    CAPSULE: PoseTarget.TargetTypeEnum
    class SchedulerEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        SEQUENTIAL: _ClassVar[PoseTarget.SchedulerEnum]
        INSTANTANEOUS: _ClassVar[PoseTarget.SchedulerEnum]
    SEQUENTIAL: PoseTarget.SchedulerEnum
    INSTANTANEOUS: PoseTarget.SchedulerEnum
    ACTION_FIELD_NUMBER: _ClassVar[int]
    TARGETTYPE_FIELD_NUMBER: _ClassVar[int]
    TARGETSCHEDULETYPE_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    MOVEMENTDURATIONMS_FIELD_NUMBER: _ClassVar[int]
    TARGETACCURACY_FIELD_NUMBER: _ClassVar[int]
    LOCALOBJECTIVEWEIGHTS_FIELD_NUMBER: _ClassVar[int]
    Action: ActionEnum
    TargetType: PoseTarget.TargetTypeEnum
    TargetScheduleType: PoseTarget.SchedulerEnum
    Transform: _bow_data_common_pb2.Transform
    Object: Object
    MovementDurationMs: float
    TargetAccuracy: float
    LocalObjectiveWeights: LocalObjectiveWeights
    def __init__(self, Action: _Optional[_Union[ActionEnum, str]] = ..., TargetType: _Optional[_Union[PoseTarget.TargetTypeEnum, str]] = ..., TargetScheduleType: _Optional[_Union[PoseTarget.SchedulerEnum, str]] = ..., Transform: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ..., Object: _Optional[_Union[Object, _Mapping]] = ..., MovementDurationMs: _Optional[float] = ..., TargetAccuracy: _Optional[float] = ..., LocalObjectiveWeights: _Optional[_Union[LocalObjectiveWeights, _Mapping]] = ...) -> None: ...

class GlobalObjectiveWeights(_message.Message):
    __slots__ = ["Displacement"]
    DISPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    Displacement: float
    def __init__(self, Displacement: _Optional[float] = ...) -> None: ...

class LocalObjectiveWeights(_message.Message):
    __slots__ = ["Position", "Orientation"]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    ORIENTATION_FIELD_NUMBER: _ClassVar[int]
    Position: float
    Orientation: float
    def __init__(self, Position: _Optional[float] = ..., Orientation: _Optional[float] = ...) -> None: ...

class Joint(_message.Message):
    __slots__ = ["Name", "Type", "Position", "Velocity", "Acceleration", "Torque", "Min", "Max", "Default", "Temperature", "Healthy", "Mimic", "MaxVelocity", "MaxAcceleration", "MaxTorque"]
    class JointTypeEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        FIXED: _ClassVar[Joint.JointTypeEnum]
        LINEAR_PRISMATIC: _ClassVar[Joint.JointTypeEnum]
        REVOLUTE: _ClassVar[Joint.JointTypeEnum]
        CONTINUOUS: _ClassVar[Joint.JointTypeEnum]
    FIXED: Joint.JointTypeEnum
    LINEAR_PRISMATIC: Joint.JointTypeEnum
    REVOLUTE: Joint.JointTypeEnum
    CONTINUOUS: Joint.JointTypeEnum
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    VELOCITY_FIELD_NUMBER: _ClassVar[int]
    ACCELERATION_FIELD_NUMBER: _ClassVar[int]
    TORQUE_FIELD_NUMBER: _ClassVar[int]
    MIN_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    HEALTHY_FIELD_NUMBER: _ClassVar[int]
    MIMIC_FIELD_NUMBER: _ClassVar[int]
    MAXVELOCITY_FIELD_NUMBER: _ClassVar[int]
    MAXACCELERATION_FIELD_NUMBER: _ClassVar[int]
    MAXTORQUE_FIELD_NUMBER: _ClassVar[int]
    Name: str
    Type: Joint.JointTypeEnum
    Position: float
    Velocity: float
    Acceleration: float
    Torque: float
    Min: float
    Max: float
    Default: float
    Temperature: float
    Healthy: bool
    Mimic: bool
    MaxVelocity: float
    MaxAcceleration: float
    MaxTorque: float
    def __init__(self, Name: _Optional[str] = ..., Type: _Optional[_Union[Joint.JointTypeEnum, str]] = ..., Position: _Optional[float] = ..., Velocity: _Optional[float] = ..., Acceleration: _Optional[float] = ..., Torque: _Optional[float] = ..., Min: _Optional[float] = ..., Max: _Optional[float] = ..., Default: _Optional[float] = ..., Temperature: _Optional[float] = ..., Healthy: bool = ..., Mimic: bool = ..., MaxVelocity: _Optional[float] = ..., MaxAcceleration: _Optional[float] = ..., MaxTorque: _Optional[float] = ...) -> None: ...

class VelocityTarget(_message.Message):
    __slots__ = ["TranslationalVelocity", "RotationalVelocity"]
    TRANSLATIONALVELOCITY_FIELD_NUMBER: _ClassVar[int]
    ROTATIONALVELOCITY_FIELD_NUMBER: _ClassVar[int]
    TranslationalVelocity: _bow_data_common_pb2.Vector3
    RotationalVelocity: _bow_data_common_pb2.Vector3
    def __init__(self, TranslationalVelocity: _Optional[_Union[_bow_data_common_pb2.Vector3, _Mapping]] = ..., RotationalVelocity: _Optional[_Union[_bow_data_common_pb2.Vector3, _Mapping]] = ...) -> None: ...

class TorqueTarget(_message.Message):
    __slots__ = ["TranslationalTorque", "RotationalTorque"]
    TRANSLATIONALTORQUE_FIELD_NUMBER: _ClassVar[int]
    ROTATIONALTORQUE_FIELD_NUMBER: _ClassVar[int]
    TranslationalTorque: _bow_data_common_pb2.Vector3
    RotationalTorque: _bow_data_common_pb2.Vector3
    def __init__(self, TranslationalTorque: _Optional[_Union[_bow_data_common_pb2.Vector3, _Mapping]] = ..., RotationalTorque: _Optional[_Union[_bow_data_common_pb2.Vector3, _Mapping]] = ...) -> None: ...

class BodyPart(_message.Message):
    __slots__ = ["Name", "Type", "RootLink", "Effectors", "Parent"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ROOTLINK_FIELD_NUMBER: _ClassVar[int]
    EFFECTORS_FIELD_NUMBER: _ClassVar[int]
    PARENT_FIELD_NUMBER: _ClassVar[int]
    Name: str
    Type: BodyPartTypeEnum
    RootLink: str
    Effectors: _containers.RepeatedCompositeFieldContainer[Effector]
    Parent: str
    def __init__(self, Name: _Optional[str] = ..., Type: _Optional[_Union[BodyPartTypeEnum, str]] = ..., RootLink: _Optional[str] = ..., Effectors: _Optional[_Iterable[_Union[Effector, _Mapping]]] = ..., Parent: _Optional[str] = ...) -> None: ...

class Effector(_message.Message):
    __slots__ = ["EffectorLinkName", "EndTransform", "RootTransform", "Reach", "JointArray", "AvailableActions", "Workspace", "Objectives", "IsControllable", "Type"]
    EFFECTORLINKNAME_FIELD_NUMBER: _ClassVar[int]
    ENDTRANSFORM_FIELD_NUMBER: _ClassVar[int]
    ROOTTRANSFORM_FIELD_NUMBER: _ClassVar[int]
    REACH_FIELD_NUMBER: _ClassVar[int]
    JOINTARRAY_FIELD_NUMBER: _ClassVar[int]
    AVAILABLEACTIONS_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    OBJECTIVES_FIELD_NUMBER: _ClassVar[int]
    ISCONTROLLABLE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    EffectorLinkName: str
    EndTransform: _bow_data_common_pb2.Transform
    RootTransform: _bow_data_common_pb2.Transform
    Reach: float
    JointArray: _containers.RepeatedCompositeFieldContainer[Joint]
    AvailableActions: _containers.RepeatedScalarFieldContainer[ActionEnum]
    Workspace: _bow_data_octree_pb2.OctreeNode
    Objectives: _containers.RepeatedCompositeFieldContainer[ObjectiveFeedback]
    IsControllable: bool
    Type: BodyPartTypeEnum
    def __init__(self, EffectorLinkName: _Optional[str] = ..., EndTransform: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ..., RootTransform: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ..., Reach: _Optional[float] = ..., JointArray: _Optional[_Iterable[_Union[Joint, _Mapping]]] = ..., AvailableActions: _Optional[_Iterable[_Union[ActionEnum, str]]] = ..., Workspace: _Optional[_Union[_bow_data_octree_pb2.OctreeNode, _Mapping]] = ..., Objectives: _Optional[_Iterable[_Union[ObjectiveFeedback, _Mapping]]] = ..., IsControllable: bool = ..., Type: _Optional[_Union[BodyPartTypeEnum, str]] = ...) -> None: ...

class ObjectiveFeedback(_message.Message):
    __slots__ = ["Status", "ControlType", "TargetTransform", "CurrentTransform", "EuclideanError", "PositionError", "OrientationError", "ErrorDescription"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CONTROLTYPE_FIELD_NUMBER: _ClassVar[int]
    TARGETTRANSFORM_FIELD_NUMBER: _ClassVar[int]
    CURRENTTRANSFORM_FIELD_NUMBER: _ClassVar[int]
    EUCLIDEANERROR_FIELD_NUMBER: _ClassVar[int]
    POSITIONERROR_FIELD_NUMBER: _ClassVar[int]
    ORIENTATIONERROR_FIELD_NUMBER: _ClassVar[int]
    ERRORDESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    Status: _bow_data_common_pb2.ObjectiveStatusEnum
    ControlType: _bow_data_common_pb2.ControllerEnum
    TargetTransform: _bow_data_common_pb2.Transform
    CurrentTransform: _bow_data_common_pb2.Transform
    EuclideanError: float
    PositionError: _bow_data_common_pb2.Vector3
    OrientationError: _bow_data_common_pb2.Vector3
    ErrorDescription: str
    def __init__(self, Status: _Optional[_Union[_bow_data_common_pb2.ObjectiveStatusEnum, str]] = ..., ControlType: _Optional[_Union[_bow_data_common_pb2.ControllerEnum, str]] = ..., TargetTransform: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ..., CurrentTransform: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ..., EuclideanError: _Optional[float] = ..., PositionError: _Optional[_Union[_bow_data_common_pb2.Vector3, _Mapping]] = ..., OrientationError: _Optional[_Union[_bow_data_common_pb2.Vector3, _Mapping]] = ..., ErrorDescription: _Optional[str] = ...) -> None: ...

class ProprioceptionSample(_message.Message):
    __slots__ = ["Parts", "Effectors", "Objects", "RawJoints", "WorkspaceByteArray"]
    PARTS_FIELD_NUMBER: _ClassVar[int]
    EFFECTORS_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    RAWJOINTS_FIELD_NUMBER: _ClassVar[int]
    WORKSPACEBYTEARRAY_FIELD_NUMBER: _ClassVar[int]
    Parts: _containers.RepeatedCompositeFieldContainer[BodyPart]
    Effectors: _containers.RepeatedCompositeFieldContainer[Effector]
    Objects: _containers.RepeatedCompositeFieldContainer[Object]
    RawJoints: _containers.RepeatedCompositeFieldContainer[Joint]
    WorkspaceByteArray: bytes
    def __init__(self, Parts: _Optional[_Iterable[_Union[BodyPart, _Mapping]]] = ..., Effectors: _Optional[_Iterable[_Union[Effector, _Mapping]]] = ..., Objects: _Optional[_Iterable[_Union[Object, _Mapping]]] = ..., RawJoints: _Optional[_Iterable[_Union[Joint, _Mapping]]] = ..., WorkspaceByteArray: _Optional[bytes] = ...) -> None: ...

class VelocityTargetStatus(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GripperStatus(_message.Message):
    __slots__ = ["GripperJointArray", "GripperOccupied"]
    GRIPPERJOINTARRAY_FIELD_NUMBER: _ClassVar[int]
    GRIPPEROCCUPIED_FIELD_NUMBER: _ClassVar[int]
    GripperJointArray: _containers.RepeatedCompositeFieldContainer[Joint]
    GripperOccupied: bool
    def __init__(self, GripperJointArray: _Optional[_Iterable[_Union[Joint, _Mapping]]] = ..., GripperOccupied: bool = ...) -> None: ...

class Gripper(_message.Message):
    __slots__ = ["GripperControlMode", "HandMapPercentage", "HandMapTransform", "JointArray"]
    GRIPPERCONTROLMODE_FIELD_NUMBER: _ClassVar[int]
    HANDMAPPERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    HANDMAPTRANSFORM_FIELD_NUMBER: _ClassVar[int]
    JOINTARRAY_FIELD_NUMBER: _ClassVar[int]
    GripperControlMode: GripperModeEnum
    HandMapPercentage: HandMapPercentage
    HandMapTransform: HandMapTransform
    JointArray: _containers.RepeatedCompositeFieldContainer[Joint]
    def __init__(self, GripperControlMode: _Optional[_Union[GripperModeEnum, str]] = ..., HandMapPercentage: _Optional[_Union[HandMapPercentage, _Mapping]] = ..., HandMapTransform: _Optional[_Union[HandMapTransform, _Mapping]] = ..., JointArray: _Optional[_Iterable[_Union[Joint, _Mapping]]] = ...) -> None: ...

class HandMapPercentage(_message.Message):
    __slots__ = ["Thumb", "Index", "Middle", "Ring", "Pinky", "FingerAdduction", "ThumbOpposition"]
    THUMB_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    MIDDLE_FIELD_NUMBER: _ClassVar[int]
    RING_FIELD_NUMBER: _ClassVar[int]
    PINKY_FIELD_NUMBER: _ClassVar[int]
    FINGERADDUCTION_FIELD_NUMBER: _ClassVar[int]
    THUMBOPPOSITION_FIELD_NUMBER: _ClassVar[int]
    Thumb: float
    Index: float
    Middle: float
    Ring: float
    Pinky: float
    FingerAdduction: float
    ThumbOpposition: float
    def __init__(self, Thumb: _Optional[float] = ..., Index: _Optional[float] = ..., Middle: _Optional[float] = ..., Ring: _Optional[float] = ..., Pinky: _Optional[float] = ..., FingerAdduction: _Optional[float] = ..., ThumbOpposition: _Optional[float] = ...) -> None: ...

class HandMapTransform(_message.Message):
    __slots__ = ["CustomRef", "Thumb", "Index", "Middle", "Ring", "Pinky", "TargetObject"]
    CUSTOMREF_FIELD_NUMBER: _ClassVar[int]
    THUMB_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    MIDDLE_FIELD_NUMBER: _ClassVar[int]
    RING_FIELD_NUMBER: _ClassVar[int]
    PINKY_FIELD_NUMBER: _ClassVar[int]
    TARGETOBJECT_FIELD_NUMBER: _ClassVar[int]
    CustomRef: _bow_data_common_pb2.Transform
    Thumb: _bow_data_common_pb2.Transform
    Index: _bow_data_common_pb2.Transform
    Middle: _bow_data_common_pb2.Transform
    Ring: _bow_data_common_pb2.Transform
    Pinky: _bow_data_common_pb2.Transform
    TargetObject: Object
    def __init__(self, CustomRef: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ..., Thumb: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ..., Index: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ..., Middle: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ..., Ring: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ..., Pinky: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ..., TargetObject: _Optional[_Union[Object, _Mapping]] = ...) -> None: ...

class Object(_message.Message):
    __slots__ = ["name", "Origin", "EndA", "EndB", "Radius", "RatioAB"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    ENDA_FIELD_NUMBER: _ClassVar[int]
    ENDB_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    RATIOAB_FIELD_NUMBER: _ClassVar[int]
    name: str
    Origin: _bow_data_common_pb2.Transform
    EndA: _bow_data_common_pb2.Vector3
    EndB: _bow_data_common_pb2.Vector3
    Radius: float
    RatioAB: float
    def __init__(self, name: _Optional[str] = ..., Origin: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ..., EndA: _Optional[_Union[_bow_data_common_pb2.Vector3, _Mapping]] = ..., EndB: _Optional[_Union[_bow_data_common_pb2.Vector3, _Mapping]] = ..., Radius: _Optional[float] = ..., RatioAB: _Optional[float] = ...) -> None: ...
