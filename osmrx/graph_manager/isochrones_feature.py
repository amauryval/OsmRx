from typing import List, Dict

import rustworkx as rx
from rustworkx import PathLengthMapping
from shapely import MultiPoint


class IsochronesFeature:
    _intervals = None
    _intervals_data = None

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
            self._intervals_data[interval] = MultiPoint(geom).convex_hull
        self._clean_iso()

    def _clean_iso(self):
        isochrones_to_clean = list(self._intervals_data.items())
        for pos, isochrone in enumerate(isochrones_to_clean):
            if pos < len(isochrones_to_clean) - 1:
                interval = isochrone[0]
                geom = isochrone[-1]
                next_isochrone = isochrones_to_clean[pos + 1]
                self._intervals_data[interval] = geom.difference(next_isochrone[-1])

    @property
    def data(self) -> Dict:
        return self._intervals_data

    @property
    def intervals(self):
        return self._intervals[::-1]
