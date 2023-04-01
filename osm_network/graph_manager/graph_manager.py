import copy
from typing import List, Dict
from typing import TYPE_CHECKING

import rustworkx as rx
from shapely import LineString
from shapely import wkt

from osm_network.data_processing.overpass_data_builder import TOPO_FIELD
from osm_network.data_processing.overpass_data_builder import ID_OSM_FIELD
from osm_network.graph_manager.path_feature import PathFeature
from osm_network.topology.cleaner import TopologyCleaner

from osm_network.globals.queries import OsmFeatureModes

if TYPE_CHECKING:
    from osm_network.graph_manager.arc_feature import ArcFeature


class GraphCore:

    def __init__(self, directed: bool = False):
        self._graph = None
        self._nodes_mapping = {}
        self._edges_mapping = {}

        if directed:
            self._graph = rx.PyDiGraph(multigraph=False)  # noqa
        else:
            self._graph = rx.PyGraph(multigraph=False)  # noqa

    @property
    def graph(self) -> rx.PyDiGraph | rx.PyGraph:
        """Return the graph"""
        return self._graph

    def _add_nodes(self, node_value: str) -> int:
        """Add a node"""
        if node_value not in self._nodes_mapping:
            self._nodes_mapping[node_value] = self.graph.add_node(node_value)
        return self.get_node_indice(node_value)

    def add_edge(self, from_node_value: str, to_node_value: str, attr: "ArcFeature") -> None:
        """add ege based on 2 nodes"""
        from_indice = self._add_nodes(from_node_value)
        to_indice = self._add_nodes(to_node_value)
        indice = f"{from_indice}_{to_indice}"
        if indice not in self._edges_mapping:
            self._edges_mapping[indice] = self.graph.add_edge(from_indice, to_indice, attr)

    def get_node_indice(self, node_value: str) -> int | None:
        """Return the node value from indice"""
        if node_value in self._nodes_mapping:
            return self._nodes_mapping[node_value]
        raise ValueError(f"{node_value} node not found!")

    def compute_shortest_path(self, from_node: str, to_node: str) -> List[PathFeature]:
        edges = rx.dijkstra_shortest_paths(
            self.graph,
            self.get_node_indice(from_node),
            self.get_node_indice(to_node),
            weight_fn=lambda edge: edge.length)

        return [
            PathFeature(self.graph, node_indices)
            for _, node_indices in edges.items()
        ]


class GraphManager(GraphCore):

    def __init__(self, logger, mode: OsmFeatureModes):
        self._mode = mode

        super().__init__(directed=self.directed)

        self.logger = logger

        self._features = None
        self._connected_nodes = None

    @property
    def directed(self) -> bool:
        """Return the graph mode"""
        if self._mode == OsmFeatureModes.vehicle:
            return True
        return False

    @property
    def connected_nodes(self) -> List[Dict]:
        """return the connected nodes added"""
        return self._connected_nodes

    @connected_nodes.setter
    def connected_nodes(self, connected_nodes: List[Dict]):
        """Set the nodes to connect on the network"""
        self._connected_nodes = connected_nodes

    @property
    def features(self) -> "List[ArcFeature]":
        """Return the graph features from the graph"""
        return self.graph.edges()

    @features.setter
    def features(self, network_data: List[Dict] | None):
        features = TopologyCleaner(self.logger, network_data, self._connected_nodes, TOPO_FIELD, ID_OSM_FIELD).run()

        for arc_feature in features:
            self.add_edge(
                arc_feature.from_point.wkt,
                arc_feature.to_point.wkt,
                arc_feature
            )
            if self._mode == OsmFeatureModes.vehicle:
                if arc_feature.is_junction_or_roundabout():
                    # do nothing
                    continue

                if not arc_feature.is_oneway():
                    arc_feature_backward = copy.deepcopy(arc_feature)
                    arc_feature_backward.direction = "backward"
                    self.add_edge(
                        arc_feature_backward.to_point.wkt,
                        arc_feature_backward.to_point.wkt,
                        arc_feature_backward
                    )
        self.logger.info("Graph built")
