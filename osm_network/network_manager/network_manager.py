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


class NetworkCore:
    _graph = None

    def __init__(self, directed: bool = False):
        if directed:
            self._graph = rx.PyDiGraph(multigraph=False)
        else:
            self._graph = rx.PyGraph(multigraph=False)

    @property
    def graph(self):
        return self._graph


class NetworkGraph:

    def __init__(self, directed: bool = False):
        self._graph = None
        self._nodes_mapping = {}
        self._edges_mapping = {}

        if directed:
            self._graph = rx.PyDiGraph(multigraph=False)
        else:
            self._graph = rx.PyGraph(multigraph=False)

    @property
    def graph(self):
        return self._graph

    def _add_nodes(self, node_value: str) -> int:
        if node_value not in self._nodes_mapping:
            node_indice = self.graph.add_node(node_value)
            self._nodes_mapping[node_value] = node_indice
        return self._nodes_mapping[node_value]

    def add_edge(self, from_node_value: str, to_node_value: str, attr: any):
        from_indice = self._add_nodes(from_node_value)
        to_indice = self._add_nodes(to_node_value)
        if f"{from_indice}_{to_indice}" not in self._edges_mapping:
            edge_indice = self.graph.add_edge(from_indice, to_indice, attr)
            self._edges_mapping[f"{from_indice}_{to_indice}"] = edge_indice


class NetworkManager:

    def __init__(self, logger, mode: OsmFeatureModes):
        self._features = None
        self._mode = None
        self._connected_nodes = None
        self._graph = None

        self.logger = logger
        self._mode = mode

    @property
    def mode(self):
        return self._mode

    @property
    def directed(self):
        if self._mode == OsmFeatureModes.vehicle:
            return True
        return False

    @property
    def connected_nodes(self):
        return self._connected_nodes

    @connected_nodes.setter
    def connected_nodes(self, connected_nodes: List[Dict]):
        self._connected_nodes = connected_nodes

    @property
    def features(self) -> "List[ArcFeature]":
        # TODO: return graph data with feature

        return self._graph.graph.edges()

    @features.setter
    def features(self, network_data: List[Dict] | None):
        features = TopologyCleaner(self.logger, network_data, self._connected_nodes, TOPO_FIELD, ID_OSM_FIELD).run()

        graph = NetworkGraph(self.directed)

        for arc_feature in features:
            graph.add_edge(
                arc_feature.start_point.wkt,
                arc_feature.end_point.wkt,
                arc_feature
            )
            if self.mode == OsmFeatureModes.vehicle:
                if arc_feature.attributes.get("junction", None) in ["roundabout", "jughandle"]:
                    # do nothing
                    # continue
                    pass

                if arc_feature.attributes.get("oneway", None) != "yes":
                    arc_feature.direction = "backward"
                    graph.add_edge(
                        arc_feature.end_point.wkt,
                        arc_feature.end_point.wkt,
                        arc_feature
                    )
        self._graph = graph
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

    @property
    def graph(self) -> rx.PyGraph | rx.PyDiGraph:
        return self._graph

    def topology_checker(self) -> TopologyChecker:
        topology_result = TopologyChecker(self.features)
        self.logger.info("Topolgoy analysis done")
        return topology_result
