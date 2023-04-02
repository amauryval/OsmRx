from typing import TYPE_CHECKING

from osmrx.globals.queries import osm_queries

if TYPE_CHECKING:
    from osmrx.globals.queries import OsmFeatureModes
    from osmrx.apis_handler.models import Bbox
    from osmrx.apis_handler.models import Location


class ErrorQueryBuilder(Exception):
    pass


class QueryBuilder:
    
    _output_format = "out geom;(._;>;)"
    _area_tag_query: str = "area.searchArea"

    def __init__(self, mode: "OsmFeatureModes") -> None:
        self._osm_query = None
        self._query = None

        self._osm_query = osm_queries[mode]["query"]

    def from_bbox(self, bbox: "Bbox") -> str:
        """build a query from a bbox"""
        query = self._osm_query.format(geo_filter=bbox.location_name)
        return self._build_query(f"({query})")
    
    def from_location(self, location: "Location") -> str:
        """build a query from a location"""
        query = self._osm_query.format(geo_filter=self._area_tag_query)
        query = f"area({location.values[0].osm_id})->.searchArea;({query})"
        return self._build_query(query)

    def _build_query(self, query_with_geofilter: str) -> str:
        """Finalize the query with the output format"""
        return f"{query_with_geofilter};{self._output_format};"
