import copy
from typing import List, Dict
from typing import TYPE_CHECKING

import rustworkx as rx
from shapely import Point

from osmrx.helpers.logger import Logger
from osmrx.network.isochrones_feature import IsochronesFeature
from osmrx.network.path_feature import PathFeature
from osmrx.topology.cleaner import TopologyCleaner

from osmrx.globals.queries import OsmFeatureModes

if TYPE_CHECKING:
    from osmrx.network.arc_feature import ArcFeature


class GraphCore:
    """Class dedicated to manage/wrappe graph function"""

    def __init__(self, directed: bool = False):
        self.logger = None
        self._graph = None
        self._nodes_mapping = {}
        self._edges_mapping = {}
        self.directed = directed

        if directed:
            self._graph = rx.PyDiGraph(multigraph=False)  # noqa
        else:
            self._graph = rx.PyGraph(multigraph=False)  # noqa

    @property
    def directed(self) -> bool:
        """Return if the graph is directed"""
        return self._directed

    @directed.setter
    def directed(self, directed: bool):
        """Set the directed graph status"""
        self._directed = directed

    @property
    def graph(self) -> rx.PyDiGraph | rx.PyGraph:
        """Return the graph"""
        return self._graph

    def _add_nodes(self, node_value: Point) -> int:
        """Add a node"""
        if node_value not in self._nodes_mapping:
            self._nodes_mapping[node_value] = self.graph.add_node(node_value)
        return self._nodes_mapping[node_value]

    def add_edge(self, from_node_value: Point, to_node_value: Point, attr: "ArcFeature") -> None:
        """add ege based on 2 nodes"""
        from_indice = self._add_nodes(from_node_value)
        to_indice = self._add_nodes(to_node_value)
        if attr.topo_uuid not in self._edges_mapping:
            self._edges_mapping[attr.topo_uuid] = self.graph.add_edge(from_indice, to_indice, attr)
        else:
            raise ValueError(f"{attr.topo_uuid} edge exists: it should not!")

    def get_node_indice(self, node_value: Point) -> int | None:
        """Return the node value from indice"""
        if node_value in self._nodes_mapping:
            return self._nodes_mapping[node_value]
        raise ValueError(f"{node_value} node not found!")

    def compute_shortest_path(self, from_node: Point, to_node: Point) -> List[PathFeature]:
        """Compute a shortest path from a node to an ohter node"""
        edges = rx.dijkstra_shortest_paths(
            self.graph,
            self.get_node_indice(from_node),
            self.get_node_indice(to_node),
            weight_fn=lambda edge: edge.length)

        return [
            PathFeature(self.graph, node_indices)
            for _, node_indices in edges.items()
        ]

    def compute_isochrone_from_distance(self, from_node: Point, intervals: List[int],
                                        precision: float | int = 1.0) -> IsochronesFeature:
        """Compute isochrone from a distance interval"""
        intervals.sort()
        assert intervals[0] == 0, "The intervals must start with 0"

        from_node_indice = self.get_node_indice(from_node)
        weight_attribute_func = lambda edge: edge.length  # noqa

        if self._directed:
            edges = rx.digraph_dijkstra_shortest_path_lengths(self.graph, from_node_indice, weight_attribute_func)
        else:
            edges = rx.dijkstra_shortest_path_lengths(self.graph, from_node_indice, weight_attribute_func)

        iso_session = IsochronesFeature(from_node, precision)
        iso_session.from_distances(intervals)
        iso_session.build(self.graph, edges)
        return iso_session

    def _build_data_and_graph(self):

        self._features = self.graph.edges()
        self.logger.info("Graph built")


class NetworkRxCore(GraphCore):
    """Base class to build a graph from data"""
    def __init__(self, directed: bool = False, logger: Logger | None = None):

        super().__init__(directed=directed)

        self._features = None

        self._connected_nodes = None
        self._line_features = []  # TODO support None value

        if logger is None:
            self.logger = Logger().logger
        else:
            self.logger = logger  # TODO: add a logger if not set

    @property
    def line_features(self) -> List[Dict]:
        """return the connected nodes added"""
        return self._line_features

    @line_features.setter
    def line_features(self, line_features: List[Dict]):
        """Set the nodes to connect on the network and build the graph
        Be careful, set the connected nodes before using this function"""
        self._line_features = line_features
        self._build_data_and_graph()

    @property
    def connected_nodes(self) -> List[Dict] | None:
        """return the connected nodes added"""
        return self._connected_nodes

    @connected_nodes.setter
    def connected_nodes(self, connected_nodes: List[Dict]):
        """Set the nodes to connect on the network, avoid to add duplicated nodes"""
        self._connected_nodes = connected_nodes

    @property
    def features(self) -> "List[ArcFeature]":
        """Return the graph features from the graph"""
        return self._features

    def _build_data_and_graph(self):
        """Topology cleaning and graph building"""
        # TODO remove ids attributes constraint on TopologyCleaner
        arc_features = TopologyCleaner(self.logger, self._line_features, self.connected_nodes, 
                                       None).build_arc_features()

        _ = [self._adding_edge(arc_feature)
             for arc_feature in arc_features]
        super()._build_data_and_graph()

    def _adding_edge(self, arc_feature: "ArcFeature"):
        """Add edge on graph function"""
        self.add_edge(
            arc_feature.from_point,
            arc_feature.to_point,
            arc_feature
        )


class OsmNetworkManager(NetworkRxCore):
    """Class to build a graph from OSM data regarding its attributes"""

    def __init__(self, mode: OsmFeatureModes, logger: Logger | None = None):
        self._mode = mode

        super().__init__(directed=mode == OsmFeatureModes.vehicle,
                         logger=logger)

    @property
    def mode(self) -> OsmFeatureModes:
        return self._mode

    def _adding_edge(self, arc_feature: "ArcFeature"):
        super()._adding_edge(arc_feature=arc_feature)

        if self._mode == OsmFeatureModes.vehicle:
            if arc_feature.attributes.get("junction", None) in ["roundabout", "jughandle"]:
                # do nothing
                return

            if not arc_feature.attributes.get("oneway", None) == "yes":
                arc_feature_backward = copy.deepcopy(arc_feature)
                arc_feature_backward.direction = "backward"
                self.add_edge(
                    arc_feature_backward.from_point,
                    arc_feature_backward.to_point,
                    arc_feature_backward
                )
