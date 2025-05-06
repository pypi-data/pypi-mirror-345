from enum import Enum
from typing import TypedDict, Union

from .robot_pose import Position, Rotation


class AssetMapping(str, Enum):
    CALIBRATION_FRAME = "RobotCalibrationFrame"
    REFERENCE_FRAME = "ReferenceFrame"
    CARTESIAN_TARGET = "RobotWaypoint"
    JOINT_TARGET = "RobotJointPosition"


class AssetParametersBase(TypedDict):
    name: str
    scope: str
    scopeId: str


class AssetBase(TypedDict):
    """Dictionary representing a typical asset structure"""

    id: str
    type: AssetMapping


class CalibrationFrameParameters(AssetParametersBase):
    position: Position
    rotation: Rotation


class CalibrationFrameAsset(AssetBase):
    parameters: CalibrationFrameParameters


# Right now, this is only CalibrationFrame assets, but in the future will
# inclue ReferenceFrame, CartesianTarget and JointTarget Assets/
SceneAssets = Union[CalibrationFrameAsset]
