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
        self.osm_feature_mode = OsmFeatureModes[osm_feature_mode]

    @property
    def osm_feature_mode(self) -> OsmFeatureModes:
        """Return the osm feature"""
        return self._osm_feature_mode

    @osm_feature_mode.setter
    def osm_feature_mode(self, feature_mode: OsmFeatureModes) -> None:
        """Set the osm feature type to use"""
        self.logger.info(f"Building {self._osm_feature_mode} Data")
        self._osm_feature_mode = feature_mode
        self._features_manager = FeaturesManager(self.logger, feature_mode)

        # self._features_manager.mode = feature_mode
        self._build_query()

    @property
    def geo_filter(self) -> Bbox | Location:
        """Return the geo filter"""
        return self._geo_filter

    @geo_filter.setter
    def geo_filter(self, geo_filter: Bbox | Location) -> None:
        """Set the geo filter"""
        self._geo_filter = geo_filter
        self.logger.info(f"From {self.geo_filter.location_name}")

    @property
    def query(self) -> str:
        """Return the query"""
        return self._query

    def _build_query(self) -> QueryBuilder:
        """Method must be implemented on children.
        Initialize the query. The geo filter must be set on the output"""
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
