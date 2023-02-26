from typing import Tuple

from osm_network.querier.models import Bbox, Location
from osm_network.querier.query_builder import QueryBuilder
from osm_network.globals.queries import NetworkModes


class OsmNetworkCore:
    _geo_filter = None
    _mode = None
    _query = None

    @property
    def mode(self) -> NetworkModes:
        return self._mode

    @mode.setter
    def mode(self, mode: NetworkModes) -> None:
        self._mode = mode
        self._build_query()

    @property
    def geo_filter(self) -> Bbox | Location:
        return self._geo_filter

    @geo_filter.setter
    def geo_filter(self, geo_filter: Bbox | Location) -> None:
        self._geo_filter = geo_filter
        self._build_query()

    @property
    def query(self) -> str:
        return self._query

    def _build_query(self) -> bool:
        """Method must be implemented on children.
        Here we are checking if inputs has been set
        in order to build the query"""
        return all([
            self.mode is not None,
            self.geo_filter is not None
        ])


class NetworkFromBbox(OsmNetworkCore):

    def __init__(self, mode: str, geo_filter: Tuple[float, float, float, float]):
        self.mode = NetworkModes[mode]
        self.geo_filter = Bbox(*geo_filter)

    def _build_query(self):
        if super()._build_query():
            self._query = QueryBuilder(self.mode).from_bbox(self.geo_filter)


class NetworkFromLocation(OsmNetworkCore):

    def __init__(self, mode: str, geo_filter: str):
        self.mode = NetworkModes[mode]
        self.geo_filter = Location(geo_filter)

    def _build_query(self):
        if super()._build_query():
            self._query = QueryBuilder(self.mode).from_location(self.geo_filter)
