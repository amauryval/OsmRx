from typing import Dict, List

from osm_network.apis_handler.models import Bbox, Location
from osm_network.apis_handler.overpass import OverpassApi
from osm_network.apis_handler.query_builder import QueryBuilder
from osm_network.features_manager.feature_manager import FeaturesManager
from osm_network.helpers.logger import Logger
from osm_network.data_processing.overpass_data_builder import OverpassDataBuilder
from osm_network.globals.queries import OsmFeatureModes


class OsmNetworkCore(Logger):
    _geo_filter = None
    _osm_feature_mode = None
    _query = None
    _raw_data = None
    _features_manager = None

    def __init__(self, osm_feature_mode: str):
        super().__init__()
        self._features_manager = FeaturesManager(self.logger)
        self.osm_feature_mode = OsmFeatureModes[osm_feature_mode]

    @property
    def osm_feature_mode(self) -> OsmFeatureModes:
        """Return the osm feature"""
        return self._osm_feature_mode

    @osm_feature_mode.setter
    def osm_feature_mode(self, feature_mode: OsmFeatureModes) -> None:
        """Set the osm feature type to use"""
        self._osm_feature_mode = feature_mode
        self._features_manager.mode = feature_mode
        self._build_query()

    @property
    def geo_filter(self) -> Bbox | Location:
        """Return the geo filter"""
        return self._geo_filter

    @geo_filter.setter
    def geo_filter(self, geo_filter: Bbox | Location) -> None:
        """Set the geo filter"""
        self._geo_filter = geo_filter
        self._build_query()

    @property
    def query(self) -> str:
        """Return the query"""
        return self._query

    def _build_query(self) -> QueryBuilder | None:
        """Method must be implemented on children.
        Initialize the query. The geo filter must be set on the output"""
        if self._inputs_validated():
            self.logger.info("Building the query")
            return QueryBuilder(self.osm_feature_mode)

    def _execute_query(self) -> OverpassDataBuilder:
        """Execute the query with the Overpass API"""
        if self._query is not None:
            self.logger.info("Execute the query")
            raw_data = OverpassApi(logger=self.logger).query(self._query)

            return OverpassDataBuilder(raw_data["elements"])

    @property
    def data(self) -> List[Dict]:
        return self._raw_data

    def _inputs_validated(self) -> bool:
        """Check if inputs are defined"""
        return all([
            self.osm_feature_mode is not None,
            self.geo_filter is not None
        ])


# class FromBboxCore(OsmNetworkCore):
#
#     def __init__(self, mode: str, geo_filter: Tuple[float, float, float, float]) -> None:
#         super().__init__(osm_feature_mode=mode)
#         self.geo_filter = Bbox(*geo_filter)
#         self.logger.info(f"Building {mode} from {self.geo_filter.to_str}")
#         self._execute_query()
#
#     def _build_query(self) -> None:
#         """Build the query"""
#         base_query = super()._build_query()
#         if base_query:
#             self._query = base_query.from_bbox(self.geo_filter)
#
#
# class FromLocationCore(OsmNetworkCore):
#
#     def __init__(self, mode: str, geo_filter: str) -> None:
#         super().__init__(osm_feature_mode=mode)
#         self.logger.info(f"Building {mode} from {geo_filter}")
#         self.geo_filter = Location(geo_filter, logger=self.logger)
#         self._execute_query()
#
#     def _build_query(self) -> None:
#         """Build the query"""
#         base_query = super()._build_query()
#         if base_query:
#             self._query = base_query.from_location(self.geo_filter)


class OsmNetworkPoi(OsmNetworkCore):

    def __init__(self):
        super().__init__(osm_feature_mode=OsmFeatureModes.poi.value)

    def _execute_query(self) -> None:
        """Execute the query with the Overpass API"""

        raw_data = super()._execute_query()
        if raw_data is not None:
            self._raw_data = raw_data.point_features()


class OsmNetworkRoads(OsmNetworkCore):
    _nodes_added = None

    def __init__(self, osm_feature_mode: str):
        super().__init__(osm_feature_mode=osm_feature_mode)

    def _execute_query(self) -> None:
        """Execute the query with the Overpass API"""

        raw_data = super()._execute_query()
        if raw_data is not None:
            self._raw_data = raw_data.line_features()

    @property
    def add_nodes(self) -> List[Dict]:
        """network mode"""
        return self._nodes_added

    @add_nodes.setter
    def add_nodes(self, nodes_added: List[Dict]):
        """network mode"""
        self._nodes_added = nodes_added

    @property
    def network_data(self) -> FeaturesManager | None:
        """network mode - Fix topology issue for LineString features only"""
        if self._raw_data is not None:
            self._features_manager.connected_nodes = self._nodes_added
            self._features_manager.features = self._raw_data
            return self._features_manager


