from typing import Dict, List
from typing import TYPE_CHECKING

import copy

import geopandas as gpd
import pandas as pd
from shapely import Point

if TYPE_CHECKING:
    from osmrx.graph_manager.arc_feature import ArcFeature


class TopologyChecker:
    _features = None
    _directed = None

    def __init__(self, features: gpd.GeoDataFrame, directed: bool = False) -> None:
        self._features = features
        self._directed = directed  # TODO: seems not useful

    @property
    def lines_unchanged(self) -> gpd.GeoDataFrame:
        """Linestring without any changes"""
        return self._features[self._features.topo_status == "unchanged"]

    @property
    def lines_added(self) -> gpd.GeoDataFrame:
        """Linestring added"""
        return self._features[self._features.topo_status == "added"]

    @property
    def nodes_added(self) -> gpd.GeoDataFrame:
        """Nodes added on the graph"""
        nodes_added = copy.deepcopy(self.lines_added)
        nodes_added['geometry'] = nodes_added.geometry.apply(lambda x: Point(x.coords[0]))
        return nodes_added

    @property
    def lines_split(self) -> gpd.GeoDataFrame:
        """Linestring split"""
        return self._features[self._features.topo_status == "split"]


    @property
    def intersections_added(self) -> gpd.GeoDataFrame:
        """Intersections nodes added"""
        start_points = self.lines_split.geometry.apply(lambda x: Point(x.coords[0]))
        end_points = self.lines_split.geometry.apply(lambda x: Point(x.coords[-1]))
        intersections_added = pd.concat([start_points, end_points]).reset_index(drop=True)
        intersections_added = gpd.GeoDataFrame(intersections_added, geometry='geometry')

        return intersections_added
