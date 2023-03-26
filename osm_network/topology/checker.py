from typing import Dict, List
from typing import TYPE_CHECKING

import copy

from shapely import Point

if TYPE_CHECKING:
    from osm_network.features_manager.feature import Feature


class TopologyChecker:
    _TOPOLOGY_FIELD = "topo_status"

    _features = None
    _directed = None

    def __init__(self, features: "List[Feature]", directed: bool = False) -> None:
        self._features = features
        self._directed = directed  # TODO: seems not useful

    @property
    def lines_unchanged(self) -> List[Dict]:
        unchanged = list(filter(lambda feature: feature.topo_status == "unchanged", self._features))
        return [feature.to_dict() for feature in unchanged]

    @property
    def lines_added(self) -> List[Dict]:
        lines_added = filter(lambda feature: feature.topo_status == "added", self._features)
        return [feature.to_dict() for feature in lines_added]

    @property
    def nodes_added(self) -> List[Dict]:
        nodes_added = []
        for node in self.lines_added:
            node["geometry"] = Point(node["geometry"].coords[0])
            nodes_added.append(node)
        return nodes_added

    @property
    def lines_split(self):
        split = list(filter(lambda feature: feature.topo_status == "split", self._features))
        return [feature.to_dict() for feature in split]

    @property
    def intersections_added(self):
        intersections_added = []
        split = self.lines_split
        for node in split:
            for coords in [node["geometry"].coords[0], node["geometry"].coords[-1]]:
                feature_copy = copy.deepcopy(node)
                feature_copy["geometry"] = Point(coords)
                intersections_added.append(feature_copy)

        return intersections_added
