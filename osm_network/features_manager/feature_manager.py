from typing import List, Dict
from typing import TYPE_CHECKING

from osm_network.data_processing.overpass_data_builder import TOPO_FIELD
from osm_network.data_processing.overpass_data_builder import ID_OSM_FIELD

from osm_network.topology.cleaner import TopologyCleaner

if TYPE_CHECKING:
    from osm_network.features_manager.feature import Feature
    from osm_network.globals.queries import OsmFeatureModes


class FeaturesManager:
    _mode = None
    _connected_nodes = None
    _features = None

    def __init__(self, logger):
        self.logger = logger

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode: "OsmFeatureModes"):
        self._mode = mode

    @property
    def connected_nodes(self):
        return self._connected_nodes

    @connected_nodes.setter
    def connected_nodes(self, connected_nodes: List[Dict]):
        self._connected_nodes = connected_nodes

    @property
    def features(self) -> "List[Feature]":
        return self._features

    @features.setter
    def features(self, network_data: List[Dict] | None):
        self._features = TopologyCleaner(self.logger, network_data, self._connected_nodes, TOPO_FIELD, ID_OSM_FIELD).run()
