from typing import Tuple

from osm_network.globals.queries import NetworkModes
from osm_network.globals.queries import network_queries

from osm_network.components.models import Bbox, Location


class ErrorQueryBuilder(Exception):
    pass


class QueryBuilder:
    
    _output_format = "out geom;(._;>;)"
    _area_tag_query: str = "area.searchArea"

    _mode_query = None
    _query = None

    def __init__(self, mode: NetworkModes) -> None:
        self._mode_query = network_queries[mode]["query"]

    def from_bbox(self, bbox: Bbox) -> str:
        """build a query from a bbox"""
        query = self._mode_query.format(geo_filter=bbox.to_str())
        return self._build_query(query)
    
    def from_location(self, location: Location) -> str:
        """build a query from a location"""
        query = self._mode_query.format(geo_filter=self._area_tag_query)
        # TODO get location_osm_id
        #return f"area({location_osm_id})->.searchArea;({query});{out_geom_query};"
        return "None"
    
    def _build_query(self, query_with_geofilter: str) -> str:
        """Finalize the query with the output format"""
        return f"({query_with_geofilter});{self._output_format};"
