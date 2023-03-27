from typing import List, Dict
from typing import TYPE_CHECKING

from osm_network.data_processing.overpass_data_builder import TOPO_FIELD
from osm_network.data_processing.overpass_data_builder import ID_OSM_FIELD
from osm_network.topology.checker import TopologyChecker
from osm_network.topology.cleaner import TopologyCleaner

from osm_network.globals.queries import OsmFeatureModes

if TYPE_CHECKING:
    from osm_network.topology.feature import Feature


class FeaturesManager:
    _mode = None
    _connected_nodes = None
    _features = None

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
    def features(self) -> "List[Feature]":
        # TODO: return graph data with feature
        return self._features

    @features.setter
    def features(self, network_data: List[Dict] | None):
        # TODO: build graph
        features = TopologyCleaner(self.logger, network_data, self._connected_nodes, TOPO_FIELD, ID_OSM_FIELD).run()
        self._features = list(features)

    def topology_checker(self) -> TopologyChecker:
        return TopologyChecker(self._features)
