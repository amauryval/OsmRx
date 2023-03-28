from typing import List, Dict
from typing import TYPE_CHECKING

import rustworkx as rx
from matplotlib.pyplot import show

from osm_network.data_processing.overpass_data_builder import TOPO_FIELD
from osm_network.data_processing.overpass_data_builder import ID_OSM_FIELD
from osm_network.topology.checker import TopologyChecker
from osm_network.topology.cleaner import TopologyCleaner

from osm_network.globals.queries import OsmFeatureModes

if TYPE_CHECKING:
    from osm_network.topology.arcfeature import ArcFeature


class FeaturesManager:
    _mode = None
    _connected_nodes = None
    _graph = None

    def __init__(self, logger, mode: OsmFeatureModes):
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
        return self._graph.edges()

    @features.setter
    def features(self, network_data: List[Dict] | None):
        # TODO: build graph
        features = TopologyCleaner(self.logger, network_data, self._connected_nodes, TOPO_FIELD, ID_OSM_FIELD).run()

        if self.directed:
            self._graph = rx.PyDiGraph(multigraph=False)
        else:
            self._graph = rx.PyGraph(multigraph=False)

        edges = []
        for arc_feature in features:
            indices = self._graph.add_nodes_from([
                arc_feature.start_point.wkt,
                arc_feature.end_point().wkt
            ])
            edges.append(tuple([indices[0], indices[-1], arc_feature]))

            if self.mode == OsmFeatureModes.vehicle:
                if arc_feature.attributes.get("junction", None) in ["roundabout", "jughandle"]:
                    # do nothing
                    pass
                if arc_feature.attributes.get("oneway", None) != "yes":
                    # TODO correct direction geom getter
                    edges.append(tuple([indices[-1], indices[0], arc_feature]))

        self._graph.add_edges_from(edges)
    @property
    def graph(self) -> rx.PyGraph:
        return self._graph

    def topology_checker(self) -> TopologyChecker:
        return TopologyChecker(self.features)
