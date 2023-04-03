from typing import Tuple, List, Dict

from osmrx.apis_handler.models import Bbox, Location
from osmrx.globals.queries import OsmFeatureModes
from osmrx.main.core import OsmNetworkCore

import geopandas as gpd


class OsmNetworkPoi(OsmNetworkCore):

    def __init__(self):
        super().__init__(osm_feature_mode=OsmFeatureModes.poi.value)

    def _execute_query(self) -> None:
        """Execute the query with the Overpass API"""
        raw_data = super()._execute_query()
        if raw_data is not None:
            self._raw_data = raw_data.point_features()

    @property
    def data(self) -> gpd.GeoDataFrame:
        return gpd.GeoDataFrame(self._raw_data, geometry="geometry", crs="4326")


class Pois(OsmNetworkPoi):
    """To manage Points of interest"""

    def __init__(self):
        super().__init__()

    def from_bbox(self, bounds: Tuple[float, float, float, float]):
        """Find Points of interest from bbox"""
        self.geo_filter = Bbox(*bounds)
        base_query = self._build_query()
        self._query = base_query.from_bbox(self.geo_filter)
        self._execute_query()

    def from_location(self, location: str):
        """Find Points of interest from location"""
        self.geo_filter = Location(location, logger=self.logger)
        base_query = self._build_query()
        self._query = base_query.from_location(self.geo_filter)
        self._execute_query()
