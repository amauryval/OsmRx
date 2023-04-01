from typing import List

from shapely import LineString, wkt


class PathFeature:
    _nodes_indices = None
    _graph = None

    def __init__(self, graph, nodes_indice: List[int]):
        self._graph = graph
        self._nodes_indices = nodes_indice

    @property
    def path(self):
        return LineString([wkt.loads(self._graph.get_node_data(indice))
                           for indice in self._nodes_indices])

    @property
    def features(self):
        return [self._graph.get_all_edge_data(*indices)[0]
                for indices in list(zip(self._nodes_indices, self._nodes_indices[1:]))]
