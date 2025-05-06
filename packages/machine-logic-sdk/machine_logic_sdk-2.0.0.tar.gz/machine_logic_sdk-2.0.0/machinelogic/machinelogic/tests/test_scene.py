# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=duplicate-code
import unittest
from typing import Any, List
from unittest.mock import MagicMock, patch

from ...ivention.exception import SceneException
from ...ivention.types.scene_assets import AssetMapping, CalibrationFrameAsset
from ...machinelogic.api import Api
from ...machinelogic.calibration_frame import CalibrationFrame
from ...machinelogic.scene import Scene
from ...measurements.angle import UnitOfAngle
from ...measurements.distance import UnitOfDistance


class TestScene(unittest.TestCase):
    def setUp(self) -> None:
        # Create mock configurations and names

        def create_calibration_frame_json(
            name: str, cartesian_pose: List[float]
        ) -> CalibrationFrameAsset:
            return {
                "id": "1234",
                "type": AssetMapping.CALIBRATION_FRAME,
                "parameters": {
                    "name": name,
                    "scope": "someScope",
                    "scopeId": "someScopeId",
                    "position": {
                        "x": {
                            "value": cartesian_pose[0],
                            "unit": UnitOfDistance.MILLIMETERS,
                        },
                        "y": {
                            "value": cartesian_pose[1],
                            "unit": UnitOfDistance.MILLIMETERS,
                        },
                        "z": {
                            "value": cartesian_pose[2],
                            "unit": UnitOfDistance.MILLIMETERS,
                        },
                    },
                    "rotation": {
                        "i": {"value": cartesian_pose[3], "unit": UnitOfAngle.DEGREE},
                        "j": {"value": cartesian_pose[4], "unit": UnitOfAngle.DEGREE},
                        "k": {"value": cartesian_pose[5], "unit": UnitOfAngle.DEGREE},
                    },
                },
            }

        self.create_calibration_frame_json = create_calibration_frame_json

        mock_configuration1 = MagicMock()
        mock_configuration1.name = "frame1"
        mock_configuration1.uuid = "uuid1"
        mock_configuration1.default_value = [1, 1, 1, 1, 1, 1]

        mock_configuration2 = MagicMock()
        mock_configuration2.name = "frame2"
        mock_configuration2.uuid = "uuid2"
        mock_configuration2.default_value = [2, 2, 2, 2, 2, 2]

        # Create mock calibration frames and set their _configuration attributes
        self.mock_calibration_frame1 = MagicMock(spec=CalibrationFrame)
        self.mock_calibration_frame1._configuration = mock_configuration1

        self.mock_calibration_frame2 = MagicMock(spec=CalibrationFrame)
        self.mock_calibration_frame2._configuration = mock_configuration2

        self.api_mock = MagicMock(spec=Api)
        # Create a Scene
        self.scene = Scene(self.api_mock)

        self.get_scene_assets_spy = MagicMock()
        self.api_mock.get_scene_assets = self.get_scene_assets_spy

    def test_initialize_assets(self) -> None:
        # Arrange
        calibration_frame_json = self.create_calibration_frame_json(
            "frame1", [1, 1, 1, 90, 90, 90]
        )
        scene_assets_json = {"assets": [calibration_frame_json]}
        self.api_mock.get_scene_assets.return_value = scene_assets_json

        calibration_frame_parameters = calibration_frame_json["parameters"]
        expected_uuid = calibration_frame_json["id"]
        expected_name = calibration_frame_parameters["name"]
        position = calibration_frame_parameters["position"]
        rotation = calibration_frame_parameters["rotation"]
        expected_default_value = [
            position["x"]["value"],
            position["y"]["value"],
            position["z"]["value"],
            rotation["i"]["value"],
            rotation["j"]["value"],
            rotation["k"]["value"],
        ]

        # Act
        self.scene._initialize_assets(self.api_mock)
        initialized_calibration_frame = self.scene._calibration_frame_list[0]
        initialized_calibration_config = initialized_calibration_frame._configuration

        # Assert
        self.assertEqual(len(self.scene._calibration_frame_list), 1)
        self.assertEqual(initialized_calibration_config.uuid, expected_uuid)
        self.assertEqual(initialized_calibration_config.name, expected_name)
        self.assertEqual(
            initialized_calibration_config.default_value, expected_default_value
        )

    def test_get_calibration_frame_where_calibration_frames_exists(self) -> None:
        # Arrange
        self.scene._calibration_frame_list = [
            self.mock_calibration_frame1,
            self.mock_calibration_frame2,
        ]
        # Test getting a calibration frame that exists
        result = self.scene.get_calibration_frame("frame1")
        self.assertEqual(result, self.mock_calibration_frame1)

        result = self.scene.get_calibration_frame("frame2")
        self.assertEqual(result, self.mock_calibration_frame2)

    @patch("machinelogic.machinelogic.scene.logging.warning")
    def test_get_calibration_frame_multiple_matches_expect_to_log_warning(
        self, mock_logger_warning: Any
    ) -> None:
        # Arrange
        self.scene._calibration_frame_list = [
            self.mock_calibration_frame1,
            self.mock_calibration_frame1,
        ]

        # Act
        result = self.scene.get_calibration_frame("frame1")

        # Assert
        self.assertEqual(result, self.mock_calibration_frame1)
        mock_logger_warning.assert_called_once()

    def test_get_calibration_frame_where_calibration_frames_do_not_exists(self) -> None:
        # Test getting a calibration frame that does not exist
        with self.assertRaises(SceneException):
            self.scene.get_calibration_frame("nonexistent_frame")

    def test_given_create_scene_calls_api_get_scene_assets(self) -> None:
        Scene(self.api_mock)
        self.get_scene_assets_spy.assert_called_once()


if __name__ == "__main__":
    unittest.main()
