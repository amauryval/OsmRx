from typing import Tuple, List, Dict, Any, Generator

from shapely import Point, MultiPoint
import rustworkx as rx

from osmrx.apis_handler.models import Location, Bbox
from osmrx.graph_manager.isochrones_feature import IsochronesFeature
from osmrx.graph_manager.path_feature import PathFeature
from osmrx.helpers.misc import buffer_point
from osmrx.main.core import OsmNetworkCore
from osmrx.topology.checker import TopologyChecker


class OsmNetworkRoads(OsmNetworkCore):

    def __init__(self, osm_feature_mode: str, nodes_to_connect: List[Dict] | None = None) -> None:
        super().__init__(osm_feature_mode=osm_feature_mode)
        self._graph_manager.connected_nodes = nodes_to_connect

    def _execute_query(self) -> None:
        """Execute the query with the Overpass API"""
        raw_data = super()._execute_query()
        if raw_data is not None:
            self._raw_data = raw_data.line_features()

    @property
    def additional_nodes(self) -> List[Dict] | None:
        """return the nodes defined to connect on the network"""
        return self._graph_manager.connected_nodes

    def _build_graph(self) -> None:
        """Fix topology issues for LineString features and build graph"""
        if self._raw_data is not None:
            self._graph_manager.features = self._raw_data

    def topology_checker(self) -> TopologyChecker:
        """Return topology data"""
        topology_result = TopologyChecker(self._graph_manager.features)
        self.logger.info("Topology analysis built.")
        return topology_result

    @property
    def data(self) -> List[Dict] | None:
        """Return the data"""
        if self._graph_manager.features is not None:
            return [feature.to_dict(with_attr=True) for feature in self._graph_manager.features]

    @property
    def graph(self) -> rx.PyGraph | rx.PyDiGraph:
        return self._graph_manager.graph

    def _execute(self):
        """Continue the execution by building the graph"""
        super()._execute()
        self._build_graph()


class Roads(OsmNetworkRoads):
    """To manage roads"""

    def __init__(self, mode: str, nodes_to_connect: List[Dict] | None = None):
        super().__init__(osm_feature_mode=mode, nodes_to_connect=nodes_to_connect)

    def from_bbox(self, bounds: Tuple[float, float, float, float]):
        """Find roads from bbox"""
        self.geo_filter = Bbox(*bounds)
        self._execute()

    def from_location(self, location: str):
        """Find roads from location"""
        self.geo_filter = Location(location, logger=self.logger)
        self._execute()


class GraphAnalysis(Roads):
    # TODO improvements needed

    def __init__(self, mode: str, nodes_to_connect: List[Point]):
        # must be ordered
        nodes_to_connect = [{"topo_uuid": 999999 + enum, "geometry": node}
                            for enum, node in enumerate(nodes_to_connect)]
        super().__init__(mode=mode, nodes_to_connect=nodes_to_connect)

    def get_shortest_path(self) -> Generator[PathFeature, Any, None]:
        # TODO improve: code is ugly
        """Compute a shortest path from a source node to a target node"""
        assert len(self.additional_nodes) == 2, "You need 2 points to compute a path"
        assert not self.additional_nodes[0]["geometry"].equals(self.additional_nodes[-1]["geometry"]), "Your points must be different"

        from_point = self.additional_nodes[0]["geometry"]
        to_point = self.additional_nodes[-1]["geometry"]

        area = MultiPoint([from_point, to_point]).buffer(from_point.distance(to_point) / 2).bounds
        self.from_bbox(tuple([area[1], area[0], area[3], area[2]]))
        paths = self._graph_manager.compute_shortest_path(from_point, to_point)
        for path in paths:
            yield path
        self.logger.info(f"Shortest path(s) built from {from_point.wkt} to {to_point.wkt}.")

    def isochrones_from_distance(self, intervals: List[int], precision: float = 1.0) -> IsochronesFeature:
        """Compute isochrones from a node based on distances"""
        assert len(self.additional_nodes) == 1, "You need 1 point to compute an isochrone"
        nodes = [node["geometry"] for node in self.additional_nodes]

        for node in nodes:
            area = buffer_point(node.y, node.x, max(intervals) + 100).bounds
            self.from_bbox(tuple([area[1], area[0], area[3], area[2]]))
            isochrones = self._graph_manager.compute_isochrone_from_distance(node, intervals, precision)
            self.logger.info(f"Isochrones {isochrones.intervals} built from {node.wkt}.")
            return isochrones
