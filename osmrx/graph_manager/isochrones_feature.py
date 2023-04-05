from typing import List, Dict

import rustworkx as rx
from rustworkx import PathLengthMapping
from shapely import MultiPoint, Point


class IsochronesFeature:
    _intervals = None
    _intervals_data = None

    def __init__(self, from_node: Point):
        self._from_node = from_node  # to be sure to have an ischrone on the from node
        self._data = []

    def from_distances(self, intervals: List[int]):
        self._intervals = list(zip(intervals, intervals[1:]))[::-1]
        self._intervals_data = {interval: list() for interval in self._intervals}

    def from_times(self):
        # TODO support time
        ...

    def build(self, graph: rx.PyGraph | rx.PyDiGraph, shortest_path_lengths: PathLengthMapping):
        if self._intervals is None:
            raise ValueError("None interval defined")

        for indice, length in shortest_path_lengths.items():
            for interval in self._intervals:
                if length < interval[-1]:
                    self._intervals_data[interval].append(
                        graph.get_node_data(indice))

        for interval, geom in self._intervals_data.items():
            if 0 in interval:
                geom.append(self._from_node)
            self._intervals_data[interval] = MultiPoint(geom).convex_hull
        self._clean_iso()

    def _clean_iso(self):
        isochrones_to_clean = list(self._intervals_data.items())
        for pos, isochrone in enumerate(isochrones_to_clean):
            interval = isochrone[0]
            geom = isochrone[-1]
            if pos < len(isochrones_to_clean) - 1:
                next_isochrone = isochrones_to_clean[pos + 1]
                print(pos)
                self._data.append({"geometry": geom.difference(next_isochrone[-1]),
                                   "distance": interval})
            else:
                self._data.append({"geometry": geom,
                                   "distance": interval})

    @property
    def data(self) -> List[Dict]:
        return self._data

    @property
    def intervals(self):
        return self._intervals[::-1]
