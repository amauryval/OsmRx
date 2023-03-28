from typing import Tuple, List, Dict

from osm_network.apis_handler.models import Location, Bbox
from osm_network.network_manager.network_manager import NetworkManager
from osm_network.main.core import OsmNetworkCore


class OsmNetworkRoads(OsmNetworkCore):

    def __init__(self, osm_feature_mode: str) -> None:
        super().__init__(osm_feature_mode=osm_feature_mode)
        self._additional_nodes = None

    def _execute_query(self) -> None:
        """Execute the query with the Overpass API"""

        raw_data = super()._execute_query()
        if raw_data is not None:
            self._raw_data = raw_data.line_features()

    @property
    def additional_nodes(self) -> List[Dict]:
        """return the nodes defined to connect on the network"""
        return self._additional_nodes

    @additional_nodes.setter
    def additional_nodes(self, additional_nodes: List[Dict]):
        """set the nodes defined to connect on the network"""
        self._additional_nodes = additional_nodes
        self._features_manager.connected_nodes = additional_nodes

    @property
    def network_data(self) -> NetworkManager | None:
        """Fix topology issues for LineString features only"""
        if self._raw_data is not None:
            self._features_manager.features = self._raw_data
            return self._features_manager


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
