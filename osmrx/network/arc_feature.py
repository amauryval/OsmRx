from typing import Dict, List, Literal

from pyproj import Geod
from shapely import LineString, Point


class ArcFeature:
    __slots__ = ("_topo_uuid", "_geometry", "_topo_status", "_attributes", "_direction")

    def __init__(self, geometry: LineString):
        self._topo_uuid = None
        self._geometry = None
        self._topo_status = None
        self._direction = "forward"
        self._attributes = {}
        self._geometry = geometry

    @property
    def topo_uuid(self) -> str:
        return f"{self._topo_uuid}_{self._direction}"

    @topo_uuid.setter
    def topo_uuid(self, topo_uuid: str):
        self._topo_uuid = topo_uuid

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, direction: Literal["forward", "backward"]):
        self._direction = direction
        self._refresh_geometry()

    @property
    def geometry(self) -> LineString:
        return self._geometry

    def _refresh_geometry(self):
        if self._direction == "backward":
            self._geometry = LineString(self.coordinates[::-1])

    @property
    def coordinates(self) -> List[float]:
        return list(self._geometry.coords)

    @property
    def from_point(self) -> Point:
        return Point(self.coordinates[0])

    @property
    def to_point(self) -> Point:
        return Point(self.coordinates[-1])

    @property
    def topo_status(self) -> str:
        """Return the topology status"""
        return self._topo_status

    @topo_status.setter
    def topo_status(self, topo_status: Literal["added", "split", "unchanged"]):
        """Set the topology status"""
        self._topo_status = topo_status

    @property
    def length(self) -> float:
        """Compute the length of a wg84 LineString in meters"""
        return Geod(ellps="WGS84").geometry_length(self.geometry)

    @property
    def attributes(self) -> Dict[str, any]:
        """Return arc attributes"""
        return self._attributes

    @attributes.setter
    def attributes(self, attributes: Dict):
        """Return arc attributes"""
        self._attributes = attributes

    def to_dict(self, with_attr: bool = False) -> Dict[str, any]:
        """Return all the attributes as a dict"""
        main_attrs = {
            "topo_uuid": self.topo_uuid,
            "topo_status": self.topo_status,
            "geometry": self.geometry,
            "direction": self.direction,
        }
        if with_attr:
            return main_attrs | self.attributes
        return main_attrs
