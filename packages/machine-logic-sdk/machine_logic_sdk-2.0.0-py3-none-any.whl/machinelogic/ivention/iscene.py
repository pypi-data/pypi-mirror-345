"""_summary_"""
from abc import abstractmethod
from typing import Any

from ..decorators.future_api import future_api
from ..ivention.icalibration_frame import ICalibrationFrame


class IScene:
    """
    A software representation of the scene containing assets
    that describe and define reference frames and targets for robots.

    Only a single instance of this object should exist in your program.
    """

    @abstractmethod
    def get_calibration_frame(self, name: str) -> ICalibrationFrame:
        """Gets a calibration frame from scene assets by name

        Args:
            name (str): Friendly name of the calibration frame asset

        Raises:
            SceneException: If the scene asset is not found

        Returns:
            ICalibrationFrame: The found calibration frame
        """

    @future_api
    def get_reference_frame(self, name: str) -> Any:
        """_summary_

        Args:
            name (str): _description_
        """

    @future_api
    def get_cartesian_target(self, name: str) -> Any:
        """_summary_

        Args:
            name (str): _description_
        """

    @future_api
    def get_joint_target(self, name: str) -> Any:
        """_summary_

        Args:
            name (str): _description_
        """
