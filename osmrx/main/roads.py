from typing import Tuple, List, Dict, Any, Generator

from shapely import Point
import rustworkx as rx
import geopandas as gpd

from osmrx.apis_handler.models import Location, Bbox
from osmrx.graph_manager.isochrones_feature import IsochronesFeature
from osmrx.graph_manager.path_feature import PathFeature
from osmrx.main.core import OsmNetworkCore
from osmrx.topology.checker import TopologyChecker


class OsmNetworkRoads(OsmNetworkCore):

    def __init__(self, osm_feature_mode: str) -> None:
        super().__init__(osm_feature_mode=osm_feature_mode)

    def _execute_query(self) -> None:
        """Execute the query with the Overpass API"""
        raw_data = super()._execute_query()
        if raw_data is not None:
            self._raw_data = raw_data.line_features()

    @property
    def additional_nodes(self) -> List[Dict]:
        """return the nodes defined to connect on the network"""
        return self._graph_manager.connected_nodes

    @additional_nodes.setter
    def additional_nodes(self, additional_nodes: List[Dict]):
        """set the nodes defined to connect on the network"""
        self._graph_manager.connected_nodes = additional_nodes

    def build_graph(self) -> None:
        """Fix topology issues for LineString features and build graph"""
        if self._raw_data is not None:
            self._graph_manager.features = self._raw_data

    def topology_checker(self) -> TopologyChecker:
        topology_result = TopologyChecker(self._graph_manager.features)
        self.logger.info("Topology analysis built.")
        return topology_result

    @property
    def data(self) -> gpd.GeoDataFrame:
        """Return the data"""
        return self._graph_manager.features

    def graph(self) -> rx.PyGraph | rx.PyDiGraph:
        return self._graph_manager.graph

    def shortest_path(self, from_point: Point, to_point: Point) -> Generator[PathFeature, Any, None]:
        """Compute a shortest path from a node to an other node"""
        paths = self._graph_manager.compute_shortest_path(from_point.wkt, to_point.wkt)
        self.logger.info(f"Shortest path(s) built from {from_point.wkt} to {to_point.wkt}.")
        for path in paths:
            yield path

    def isochrones_from_distance(self, from_point: Point, intervals: List[int]) -> IsochronesFeature:
        """Compute isochrones from a node based on distances"""
        isochrones = self._graph_manager.compute_isochrone_from_distance(from_point.wkt, intervals)
        self.logger.info(f"Isochrones {isochrones.intervals} built from {from_point.wkt}.")
        return isochrones


class Roads(OsmNetworkRoads):
    """To manage roads"""

    def __init__(self, mode: str):
        super().__init__(osm_feature_mode=mode)

    def from_bbox(self, bounds: Tuple[float, float, float, float]):
        """Find roads from bbox"""
        self.geo_filter = Bbox(*bounds)
        base_query = self._build_query()
        self._query = base_query.from_bbox(self.geo_filter)
        self._execute_query()

    def from_location(self, location: str):
        """Find roads from location"""
        self.geo_filter = Location(location, logger=self.logger)
        base_query = self._build_query()
        self._query = base_query.from_location(self.geo_filter)
        self._execute_query()
