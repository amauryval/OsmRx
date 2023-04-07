from osmrx.apis_handler.models import Bbox, Location
from osmrx.apis_handler.overpass import OverpassApi
from osmrx.apis_handler.query_builder import QueryBuilder
from osmrx.network.network_rx import OsmNetworkManager
from osmrx.helpers.logger import Logger
from osmrx.data_processing.overpass_data_builder import OverpassDataBuilder
from osmrx.globals.queries import OsmFeatureModes


class OsmNetworkHandler(Logger):

    def __init__(self, osm_feature_mode: str):
        self._geo_filter = None
        self._query = None
        self._raw_data = None
        self._graph_manager: OsmNetworkManager | None = None

        super().__init__()

        self.osm_feature_mode = OsmFeatureModes[osm_feature_mode]

    @property
    def osm_feature_mode(self) -> OsmFeatureModes:
        """Return the osm feature"""
        return self._osm_feature_mode

    @osm_feature_mode.setter
    def osm_feature_mode(self, feature_mode: OsmFeatureModes) -> None:
        """Set the osm feature type to use"""
        self._osm_feature_mode = feature_mode
        self.logger.info(f"Building {self._osm_feature_mode} Data")
        self._build_query()
        if feature_mode != OsmFeatureModes.poi:
            self._graph_manager = OsmNetworkManager(feature_mode, self.logger)

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
    def data(self) -> None:
        raise NotImplemented

    def _execute(self):
        base_query = self._build_query()
        self._query = base_query.from_geo_filter(self.geo_filter)
        self._execute_query()
