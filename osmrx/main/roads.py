from typing import Tuple, List, Dict, Any, Generator

from shapely import Point, MultiPolygon
import rustworkx as rx

from osmrx.apis_handler.models import Location, Bbox
from osmrx.network.isochrones_feature import IsochronesFeature
from osmrx.network.path_feature import PathFeature
from osmrx.helpers.misc import buffer_point
from osmrx.main.core import OsmNetworkHandler
from osmrx.topology.checker import TopologyChecker


class OsmNetworkRoads(OsmNetworkHandler):

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
            self._graph_manager.line_features = self._raw_data

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
        """
        nodes_to_connectes: must be ordered
        """
        unique_nodes = set(nodes_to_connect)  # remove duplicate nodes for the graph
        unique_nodes_to_connect = [{"topo_uuid": 999999 + enum, "geometry": node}
                                   for enum, node in enumerate(unique_nodes)]
        super().__init__(mode=mode, nodes_to_connect=unique_nodes_to_connect)

        self._steps_nodes = nodes_to_connect

    def get_shortest_path(self) -> Generator[PathFeature, Any, None]:
        """Compute a shortest path from a source node to a target node"""
        assert len(self._steps_nodes) > 1, "At least, You need 2 points to compute a path"
        bounds = MultiPolygon(list(
            map(lambda point: buffer_point(point.y, point.x, 100), self._steps_nodes)
        )).bounds
        self.from_bbox(tuple([bounds[1], bounds[0], bounds[3], bounds[2]]))
        for from_point, to_point in list(zip(self._steps_nodes, self._steps_nodes[1:])):
            paths = self._graph_manager.compute_shortest_path(from_point, to_point)
            for path in paths:
                yield path
            self.logger.info(f"Shortest path(s) built from {from_point.wkt} to {to_point.wkt}.")

    def isochrones_from_distance(self, intervals: List[int], precision: float = 1.0) -> IsochronesFeature:
        """Compute isochrones from a node based on distances"""
        assert len(self._steps_nodes) == 1, "You need 1 point to compute an isochrone"

        for node in self._steps_nodes:
            area = buffer_point(node.y, node.x, max(intervals) + 100).bounds
            self.from_bbox(tuple([area[1], area[0], area[3], area[2]]))
            isochrones = self._graph_manager.compute_isochrone_from_distance(node, intervals, precision)
            self.logger.info(f"Isochrones {isochrones.intervals} built from {node.wkt}.")
            return isochrones
