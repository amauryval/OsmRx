from typing import Dict

import shapely.geometry
from shapely import LineString


class Feature:
    _topo_uuid = None
    _geometry = None
    _topo_status = None
    _direction = None
    _attributes = {}

    def __init__(self, geometry: shapely.geometry.base.BaseGeometry):
        self._geometry = geometry

    @property
    def topo_uuid(self):
        return self._topo_uuid

    @topo_uuid.setter
    def topo_uuid(self, topo_uuid: str):
        self._topo_uuid = topo_uuid

    @property
    def forward(self):
        return self._geometry

    @property
    def backward(self):
        return LineString(self._geometry.coords[::-1])

    @property
    def topo_status(self):
        return self._topo_status

    @topo_status.setter
    def topo_status(self, topo_status: str):
        self._topo_status = topo_status

    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, attributes: Dict):
        self._attributes = attributes

    def to_dict(self) -> Dict:
        return {
            **{"topo_uuid": self.topo_uuid},
            **{"topo_status": self.topo_status},
            **{"geometry": self.forward},
            **self.attributes
        }
