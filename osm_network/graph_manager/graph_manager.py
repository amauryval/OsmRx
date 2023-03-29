import copy
from typing import List, Dict
from typing import TYPE_CHECKING

import rustworkx as rx

from osm_network.data_processing.overpass_data_builder import TOPO_FIELD
from osm_network.data_processing.overpass_data_builder import ID_OSM_FIELD
from osm_network.topology.checker import TopologyChecker
from osm_network.topology.cleaner import TopologyCleaner

from osm_network.globals.queries import OsmFeatureModes

if TYPE_CHECKING:
    from osm_network.topology.arcfeature import ArcFeature


class GraphCore:

    def __init__(self, directed: bool = False):
        self._graph = None
        self._nodes_mapping = {}
        self._edges_mapping = {}

        if directed:
            self._graph = rx.PyDiGraph(multigraph=False)
        else:
            self._graph = rx.PyGraph(multigraph=False)

    @property
    def graph(self) -> rx.PyDiGraph | rx.PyGraph:
        return self._graph

    def _add_nodes(self, node_value: str) -> int:
        if node_value not in self._nodes_mapping:
            self._nodes_mapping[node_value] = self.graph.add_node(node_value)
        return self._nodes_mapping[node_value]

    def add_edge(self, from_node_value: str, to_node_value: str, attr: "ArcFeature") -> int:
        from_indice = self._add_nodes(from_node_value)
        to_indice = self._add_nodes(to_node_value)
        indice = f"{from_indice}_{to_indice}"
        if indice not in self._edges_mapping:
            self._edges_mapping[indice] = self.graph.add_edge(from_indice, to_indice, attr)


class GraphManager(GraphCore):

    def __init__(self, logger, mode: OsmFeatureModes):
        self._mode = mode

        super().__init__(directed=self.directed)

        self.logger = logger

        self._features = None
        self._connected_nodes = None

    @property
    def directed(self) -> bool:
        if self._mode == OsmFeatureModes.vehicle:
            return True
        return False

    @property
    def connected_nodes(self) -> List[Dict]:
        return self._connected_nodes

    @connected_nodes.setter
    def connected_nodes(self, connected_nodes: List[Dict]):
        self._connected_nodes = connected_nodes

    @property
    def features(self) -> "List[ArcFeature]":
        # TODO: return graph data with feature

        return self.graph.edges()

    @features.setter
    def features(self, network_data: List[Dict] | None):
        features = TopologyCleaner(self.logger, network_data, self._connected_nodes, TOPO_FIELD, ID_OSM_FIELD).run()

        # graph = NetworkGraph(self.directed)

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

        # if self.directed:
        #     self._graph = rx.PyDiGraph(multigraph=False)
        # else:
        #     self._graph = rx.PyGraph(multigraph=False)
        #
        # edges = []
        # for arc_feature in features:
        #     indices = self._graph.add_nodes_from([
        #         arc_feature.start_point.wkt,
        #         arc_feature.end_point().wkt
        #     ])
        #     edges.append(tuple([indices[0], indices[-1], arc_feature]))
        #
        #     if self.mode == OsmFeatureModes.vehicle:
        #         if arc_feature.attributes.get("junction", None) in ["roundabout", "jughandle"]:
        #             # do nothing
        #             pass
        #         if arc_feature.attributes.get("oneway", None) != "yes":
        #             # TODO correct direction geom getter
        #             edges.append(tuple([indices[-1], indices[0], arc_feature]))

        # self._graph.add_edges_from(edges)


