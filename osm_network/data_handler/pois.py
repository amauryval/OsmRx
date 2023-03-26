from typing import Tuple

from osm_network.apis_handler.models import Bbox, Location
from osm_network.data_handler.core import OsmNetworkPoi
from osm_network.globals.queries import OsmFeatureModes


class PoisFromBbox(OsmNetworkPoi):

    def __init__(self, geo_filter: Tuple[float, float, float, float]) -> None:
        super().__init__()
        self.geo_filter = Bbox(*geo_filter)
        self.logger.info(f"Building {OsmFeatureModes.poi.value} from {self.geo_filter.to_str}")
        self._execute_query()

    def _build_query(self) -> None:
        """Build the query"""
        base_query = super()._build_query()
        if base_query:
            self._query = base_query.from_bbox(self.geo_filter)


class PoisFromLocation(OsmNetworkPoi):

    def __init__(self, geo_filter: str) -> None:
        super().__init__()
        self.logger.info(f"Building {OsmFeatureModes.poi.value} from {geo_filter}")
        self.geo_filter = Location(geo_filter, logger=self.logger)
        self._execute_query()

    def _build_query(self) -> None:
        """Build the query"""
        base_query = super()._build_query()
        if base_query:
            self._query = base_query.from_location(self.geo_filter)

