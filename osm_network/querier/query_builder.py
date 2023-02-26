from osm_network.globals.queries import NetworkModes
from osm_network.globals.queries import network_queries

from osm_network.querier.models import Bbox
from osm_network.querier.models import Location


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
        query = self._mode_query.format(geo_filter=bbox.to_str)
        return self._build_query(f"({query})")
    
    def from_location(self, location: Location) -> str:
        """build a query from a location"""
        query = self._mode_query.format(geo_filter=self._area_tag_query)
        query = f"area({location.values[0].osm_id_useful})->.searchArea;({query})"
        return self._build_query(query)

    def _build_query(self, query_with_geofilter: str) -> str:
        """Finalize the query with the output format"""
        return f"{query_with_geofilter};{self._output_format};"
