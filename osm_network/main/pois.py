from typing import Tuple

from osm_network.apis_handler.models import Bbox, Location
from osm_network.globals.queries import OsmFeatureModes
from osm_network.main.core import OsmNetworkCore


class OsmNetworkPoi(OsmNetworkCore):

    def __init__(self):
        super().__init__(osm_feature_mode=OsmFeatureModes.poi.value)

    def _execute_query(self) -> None:
        """Execute the query with the Overpass API"""
        raw_data = super()._execute_query()
        if raw_data is not None:
            self._raw_data = raw_data.point_features()


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
