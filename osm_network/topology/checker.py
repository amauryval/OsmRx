import copy
from typing import Dict, List

from shapely import Point

from osm_network.globals.osm import forward_tag


class TopologyChecker:
    _TOPO_FIELD = "_topo_uuid"
    _TOPOLOGY_FIELD = "_topo_status"
    _TOPOLOGY_FIELDS: List[str] = [_TOPO_FIELD, "id", _TOPOLOGY_FIELD, "osm_url", "_geometry"]

    _network_data = None
    _directed = None

    def __init__(self, network_data: List[Dict], directed: bool = False) -> None:
        self._network_data = network_data
        self._directed = directed

    @property
    def lines_unchanged(self):
        unchanged = list(filter(lambda x: x[self._TOPOLOGY_FIELD] == "unchanged", self._network_data))
        return unchanged

    @property
    def nodes_added(self) -> List[Dict]:
        lines_added = filter(lambda x: x[self._TOPOLOGY_FIELD] == "added", self._network_data)
        if self._directed:
            lines_added = filter(lambda x: forward_tag in x[self._TOPO_FIELD], lines_added)
        nodes_added = list(lines_added)

        for node in nodes_added:
            node["_geometry"] = Point(node["_geometry"].coords[0])
        return nodes_added

    @property
    def lines_split(self):
        split = list(filter(lambda x: x[self._TOPOLOGY_FIELD] == "split", self._network_data))
        return split

    @property
    def intersections_added(self):
        intersections_added = []
        split = self.lines_split
        for node in split:
            from_point = Point(node["_geometry"].coords[0])
            to_point = Point(node["_geometry"].coords[-1])
            for point in [from_point, to_point]:
                feature = copy.deepcopy(node)
                feature["_geometry"] = point
                intersections_added.append(feature)

        return intersections_added
