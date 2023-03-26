from typing import Tuple, Dict, List

import geopandas as gpd
from osm_network.apis_handler.models import Bbox, Location
from osm_network.apis_handler.overpass import OverpassApi
from osm_network.apis_handler.query_builder import QueryBuilder
from osm_network.features_manager.feature_manager import FeaturesManager
from osm_network.helpers.logger import Logger
from osm_network.data_processing.overpass_data_builder import OverpassDataBuilder
from osm_network.features_manager.feature import Feature
from osm_network.globals.queries import OsmFeatureModes


class OsmNetworkCore(Logger):
    
    _geo_filter = None
    _osm_feature_mode = None
    _query = None
    _raw_data = None
    _nodes_added = None
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

    def _execute_query(self) -> None:
        """Execute the query with the Overpass API"""
        if self._query is not None:
            self.logger.info("Execute the query")
            raw_data = OverpassApi(logger=self.logger).query(self._query)

            formated_data = OverpassDataBuilder(raw_data["elements"])
            if self.osm_feature_mode in [OsmFeatureModes.pedestrian, OsmFeatureModes.vehicle]:
                self._raw_data = formated_data.line_features()
            elif self.osm_feature_mode == OsmFeatureModes.poi:
                self._raw_data = formated_data.point_features()
            else:
                raise Exception(f"{self.osm_feature_mode} not supported")

    @property
    def data(self) -> gpd.GeoDataFrame:
        return self._raw_data

    @property
    def add_nodes(self) -> List[Dict]:
        return self._nodes_added

    @add_nodes.setter
    def add_nodes(self, nodes_added: List[Dict]):
        self._nodes_added = nodes_added

    @property
    def network_data(self) -> FeaturesManager | None:
        """Fix topology issue for LineString features only"""
        if self._raw_data is not None and self.osm_feature_mode != OsmFeatureModes.poi:
            self._features_manager.connected_nodes = self._nodes_added
            self._features_manager.features = self._raw_data
            return self._features_manager

    def _inputs_validated(self) -> bool:
        """Check if inputs are defined"""
        return all([
            self.osm_feature_mode is not None,
            self.geo_filter is not None
        ])


class DataFromBbox(OsmNetworkCore):

    def __init__(self, mode: str, geo_filter: Tuple[float, float, float, float]) -> None:
        super().__init__(osm_feature_mode=mode)
        self.geo_filter = Bbox(*geo_filter)
        self.logger.info(f"Building {mode} from {self.geo_filter.to_str}")
        self._execute_query()

    def _build_query(self) -> None:
        """Build the query"""
        base_query = super()._build_query()
        if base_query:
            self._query = base_query.from_bbox(self.geo_filter)


class DataFromLocation(OsmNetworkCore):

    def __init__(self, mode: str, geo_filter: str) -> None:
        super().__init__(osm_feature_mode=mode)
        self.logger.info(f"Building {mode} from {geo_filter}")
        self.geo_filter = Location(geo_filter, logger=self.logger)
        self._execute_query()

    def _build_query(self) -> None:
        """Build the query"""
        base_query = super()._build_query()
        if base_query:
            self._query = base_query.from_location(self.geo_filter)
