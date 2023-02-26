from typing import Tuple, Dict, List

from osm_network.apis_handler.models import Bbox, Location
from osm_network.apis_handler.overpass import OverpassApi
from osm_network.apis_handler.query_builder import QueryBuilder
from osm_network.core.logger import Logger
from osm_network.data_processing.overpass_data_builder import OverpassDataBuilder, TOPO_FIELD, ID_OSM_FIELD
from osm_network.data_processing.network_topology import NetworkTopology
from osm_network.globals.queries import OsmFeatures


class OsmNetworkCore(Logger):
    _geo_filter = None
    _osm_feature = None
    _query = None
    _raw_data = None

    def __init__(self, osm_feature: str):
        super().__init__()
        self.osm_feature = OsmFeatures[osm_feature]

    @property
    def osm_feature(self) -> OsmFeatures:
        """Return the osm feature"""
        return self._osm_feature

    @osm_feature.setter
    def osm_feature(self, mode: OsmFeatures) -> None:
        """Set the osm feature to use"""
        self._osm_feature = mode
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
            return QueryBuilder(self.osm_feature)

    def _execute_query(self) -> None:
        """Execute the query with the Overpass API"""
        if self._query is not None:
            self.logger.info("Execute the query")
            self._raw_data = OverpassApi(logger=self.logger).query(self._query)

    @property
    def raw_data(self) -> List[Dict]:
        """Raw data found from overpass ; not cleaned only formated
        to be readable"""
        if self._raw_data is not None:
            formated_data = OverpassDataBuilder(self._raw_data["elements"])
            if self.osm_feature in [OsmFeatures.pedestrian, OsmFeatures.vehicle]:
                return formated_data.line_features()
            elif self.osm_feature == OsmFeatures.poi:
                return formated_data.point_features()
            else:
                raise Exception(f"{self.osm_feature} not supported")

    def clean(self, additional_points: List[Dict] | None = None) -> List[Dict]:
        """Fix topology issue for LineString features only"""
        if additional_points is None:
            additional_points = []

        if self.osm_feature in [OsmFeatures.pedestrian, OsmFeatures.vehicle]:
            return NetworkTopology(self.logger, self.raw_data, additional_points, TOPO_FIELD, ID_OSM_FIELD,
                                   self.osm_feature).run()

        elif self.osm_feature == OsmFeatures.poi:
            return self.raw_data

        else:
            raise Exception(f"{self.osm_feature} not supported")

    def _inputs_validated(self) -> bool:
        """Check if inputs are defined"""
        return all([
            self.osm_feature is not None,
            self.geo_filter is not None
        ])


class DataFromBbox(OsmNetworkCore):

    def __init__(self, mode: str, geo_filter: Tuple[float, float, float, float]) -> None:
        super().__init__(osm_feature=mode)
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
        super().__init__(osm_feature=mode)
        self.logger.info(f"Building {mode} from {geo_filter}")
        self.geo_filter = Location(geo_filter, logger=self.logger)
        self._execute_query()

    def _build_query(self) -> None:
        """Build the query"""
        base_query = super()._build_query()
        if base_query:
            self._query = base_query.from_location(self.geo_filter)
