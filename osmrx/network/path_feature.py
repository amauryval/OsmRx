from typing import List, Dict

from shapely import LineString

from osmrx.network.arc_feature import ArcFeature


class PathFeature:
    _graph = None
    _nodes_indices = None
    _features = None

    def __init__(self, graph, nodes_indice: List[int]):
        self._graph = graph
        self._nodes_indices = nodes_indice
        self._features = self._build_features()

    @property
    def path(self) -> LineString:
        """Return the path as a LineString geometry"""
        return LineString([self._graph.get_node_data(indice)
                           for indice in self._nodes_indices])

    def features(self) -> List[Dict]:
        """Return each LineStrings composing the path with their attributes"""
        return [feature.to_dict(with_attr=True) for feature in self._build_features()]

    def _build_features(self) -> List[ArcFeature]:
        """Get all the ArcFeature composing the path found"""
        return [self._graph.get_all_edge_data(*indices)[0]
                for indices in list(zip(self._nodes_indices, self._nodes_indices[1:]))]
