# pylint: disable=protected-access
import logging
from typing import Any, List

from ..decorators.future_api import future_api
from ..ivention.exception import SceneException
from ..ivention.iscene import IScene
from ..ivention.types.robot_pose import Pose
from ..ivention.types.scene_assets import AssetMapping, CalibrationFrameAsset
from ..ivention.util.inheritance import inherit_docstrings  # type: ignore
from .api import Api
from .calibration_frame import CalibrationFrame
from .utils.robot_pose_conversions import convert_pose_to_cartesian_pose


@inherit_docstrings
class Scene(IScene):
    def __init__(self, api: Api) -> None:
        self._calibration_frame_list: List[CalibrationFrame] = []
        self._initialize_assets(api)

    def get_calibration_frame(self, name: str) -> CalibrationFrame:
        calibration_frame_list = self._calibration_frame_list
        matching_frames = [
            calibration_frame
            for calibration_frame in calibration_frame_list
            if calibration_frame._configuration.name == name
        ]
        if len(matching_frames) == 0:
            raise SceneException(f"Failed to find calibration frame with name: {name}")
        if len(matching_frames) > 1:
            logging.warning(
                "Multiple calibration frames found with name: %s. "
                "Using first one found with id: %s.",
                name,
                matching_frames[0]._configuration.uuid,
            )

        return matching_frames[0]

    @future_api
    def get_reference_frame(self, name: str) -> Any:
        """TO IMPLEMENT IN THE FUTURE"""

    @future_api
    def get_cartesian_target(self, name: str) -> Any:
        """TO IMPLEMENT IN THE FUTURE"""

    @future_api
    def get_joint_target(self, name: str) -> Any:
        """TO IMPLEMENT IN THE FUTURE"""

    def _initialize_assets(self, api: Api) -> None:
        scene_assets_json = api.get_scene_assets()
        for scene_asset_json in scene_assets_json["assets"]:
            scene_asset_type = scene_asset_json["type"]
            if scene_asset_type == AssetMapping.CALIBRATION_FRAME:
                self._calibration_frame_list.append(
                    _create_calibration_frame(scene_asset_json, api)
                )


def _create_calibration_frame(
    calibration_frame_json: CalibrationFrameAsset, api: Api
) -> CalibrationFrame:
    """Takes a calibration frame configuration in JSON format and
        converts it to a CalibrationFrame

    Args:
        calibration_frame_json (CalibrationFrameAsset): The calibration frame in JSON format
        api: The machinelogic api
    Returns:
        CalibrationFrame: An instance of a calibration frame
    """
    calibration_frame_parameters = calibration_frame_json["parameters"]
    uuid = calibration_frame_json["id"]
    name = calibration_frame_parameters["name"]

    # makes sure values are in mm and deg because that's all we can handle right now
    position = calibration_frame_parameters["position"]
    rotation = calibration_frame_parameters["rotation"]
    pose = Pose(position=position, rotation=rotation)
    default_value = convert_pose_to_cartesian_pose(pose)
    return CalibrationFrame(uuid, name, default_value, api)
