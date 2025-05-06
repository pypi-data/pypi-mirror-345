from dataclasses import dataclass
from typing import Dict


@dataclass
class Timestamp:
    """
    A timestamp since epoch, UTC
        attributes:
            secs: seconds since epoch
            nsecs: nanoseconds since epoch
    """

    secs: float
    nsecs: float

    @staticmethod
    def into(data: Dict[str, float]) -> "Timestamp":
        """
        Convert a dictionary into a Timestamp object.

        Args:
            data: Dictionary containing the timestamp data

        Returns:
            Timestamp object
        """
        return Timestamp(float(data["secs"]), float(data["nsecs"]))
