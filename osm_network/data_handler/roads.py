from typing import Tuple

from osm_network.apis_handler.models import Location, Bbox
from osm_network.data_handler.core import OsmNetworkRoads


class RoadsFromBbox(OsmNetworkRoads):

    def __init__(self, mode: str, geo_filter: Tuple[float, float, float, float]) -> None:
        super().__init__(osm_feature_mode=mode)
        self.geo_filter = Bbox(*geo_filter)
        self.logger.info(f"Building {mode} from {self.geo_filter.to_str}")
        self._execute_query()

    def _build_query(self) -> None:
        """Build the query"""
        base_query = super()._build_query()
        if base_query:
            self._query = base_query.from_bbox(self.geo_filter)


class RoadsFromLocation(OsmNetworkRoads):

    def __init__(self, mode: str, geo_filter: str) -> None:
        super().__init__(osm_feature_mode=mode)
        self.logger.info(f"Building {mode} from {geo_filter}")
        self.geo_filter = Location(geo_filter, logger=self.logger)
        self._execute_query()

    def _build_query(self) -> None:
        """Build the query"""
        base_query = super()._build_query()
        if base_query:
            self._query = base_query.from_location(self.geo_filter)
