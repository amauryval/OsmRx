from typing import Dict, List, Literal

from shapely.geometry.base import BaseGeometry
from shapely import LineString, Point


class ArcFeature:
    __slots__ = ("_topo_uuid", "_geometry", "_topo_status", "_direction", "_attributes", "_direction")

    def __init__(self, geometry: LineString):
        self._topo_uuid = None
        self._geometry = None
        self._topo_status = None
        self._direction = "forward"
        self._attributes = {}

        self._geometry = geometry

    @property
    def topo_uuid(self) -> str:
        return self._topo_uuid

    @topo_uuid.setter
    def topo_uuid(self, topo_uuid: str):
        self._topo_uuid = topo_uuid

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, direction: Literal["forward", "backward"]):
        self._direction = direction

    @property
    def geometry(self) -> LineString:
        # TODO: improve condition
        if self._direction == "forward":
            return self._geometry
        else:
            return LineString(self.coordinates[::-1])

    @property
    def coordinates(self) -> List[float]:
        return list(self._geometry.coords)

    @property
    def start_point(self) -> Point:
        return Point(self.coordinates[0])

    @property
    def end_point(self) -> Point:
        return Point(self.coordinates[-1])

    @property
    def topo_status(self) -> str:
        return self._topo_status

    @topo_status.setter
    def topo_status(self, topo_status: str):
        self._topo_status = topo_status

    @property
    def attributes(self) -> Dict[str, any]:
        return self._attributes

    @attributes.setter
    def attributes(self, attributes: Dict):
        self._attributes = attributes

    def to_dict(self) -> Dict[str, any]:
        return {
            **{"topo_uuid": self.topo_uuid},
            **{"topo_status": self.topo_status},
            **{"geometry": self.geometry},
            **self.attributes
        }
