from typing import Tuple, Dict

from osm_network.apis_handler.models import Bbox, Location
from osm_network.apis_handler.overpass import OverpassApi
from osm_network.apis_handler.query_builder import QueryBuilder
from osm_network.globals.queries import OsmFeatures


class OsmNetworkCore:
    _geo_filter = None
    _osm_feature = None
    _query = None
    _result = None

    def __init__(self, osm_feature: str):
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
            return QueryBuilder(self.osm_feature)

    def _execute_query(self) -> None:
        """Execute the query with the Overpass API"""
        if self._query is not None:
            self._result = OverpassApi().query(self._query)

    @property
    def result(self) -> Dict:
        """Return the overpass result"""
        return self._result

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
        self._execute_query()

    def _build_query(self) -> None:
        """Build the query"""
        base_query = super()._build_query()
        if base_query:
            self._query = base_query.from_bbox(self.geo_filter)


class DataFromLocation(OsmNetworkCore):

    def __init__(self, mode: str, geo_filter: str) -> None:
        super().__init__(osm_feature=mode)
        self.geo_filter = Location(geo_filter)
        self._execute_query()

    def _build_query(self) -> None:
        """Build the query"""
        base_query = super()._build_query()
        if base_query:
            self._query = base_query.from_location(self.geo_filter)
