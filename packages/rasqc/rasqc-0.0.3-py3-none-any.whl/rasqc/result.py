"""Module for defining the RasqcResult class and related functionality."""

from geopandas import GeoDataFrame

from dataclasses import dataclass
from enum import Enum
from json import JSONEncoder
from typing import Any, List, Optional


class ResultStatus(Enum):
    """Enumeration of possible check result statuses.

    Attributes
    ----------
        OK: Check passed successfully.
        WARNING: Check passed with warnings.
        ERROR: Check failed.
    """

    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


class RasqcResultEncoder(JSONEncoder):
    """JSON encoder for RasqcResult objects.

    Handles serialization of Enum values and GeoDataFrames.
    """

    def default(self, obj: Any) -> Any:
        """Convert objects to JSON serializable types.

        Parameters
        ----------
            obj: The object to serialize.

        Returns
        -------
            A JSON serializable representation of the object.
        """
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, GeoDataFrame):
            return obj.to_json()
        return super().default(obj)


@dataclass
class RasqcResult:
    """Result of a quality control check on a HEC-RAS model.

    Attributes
    ----------
        result: The status of the check (OK, WARNING, ERROR).
        name: The name of the check.
        filename: The filename of the checked file.
        message: Optional message providing details about the check result.
        pattern: Optional regular expression related to the check.
        gdf: Optional GeoDataFrame containing spatial data related to the check.
    """

    result: ResultStatus
    name: str
    filename: str
    element: Optional[str] | Optional[List[str]] = None
    message: Optional[str] = None
    pattern: Optional[str] | Optional[List[str]] = None
    examples: Optional[str] = None
    gdf: Optional[GeoDataFrame] = None
