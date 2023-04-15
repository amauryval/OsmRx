from typing import Tuple, List, Dict

from osmrx.apis_handler.models import Bbox, Location
from osmrx.globals.queries import OsmFeatureModes
from osmrx.main.core import OsmNetworkHandler


class OsmNetworkPoi(OsmNetworkHandler):

    def __init__(self):
        super().__init__(osm_feature_mode=OsmFeatureModes.poi.value)

    def _execute_query(self) -> None:
        """Execute the query with the Overpass API"""
        raw_data = super()._execute_query()
        if raw_data is not None:
            self._raw_data = raw_data.point_features()

    @property
    def data(self) -> List[Dict]:
        return self._raw_data


class Pois(OsmNetworkPoi):
    """To manage Points of interest"""

    def __init__(self):
        super().__init__()

    def from_bbox(self, bounds: Tuple[float, float, float, float]):
        """Find Points of interest from bbox"""
        self.geo_filter = Bbox(*bounds)
        self._execute()

    def from_location(self, location: str):
        """Find Points of interest from location"""
        self.geo_filter = Location(location, logger=self.logger)
        self._execute()
