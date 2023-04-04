from typing import List, Dict

import pytest

import rustworkx as rx

from osmrx.globals.queries import OsmFeatureModes
from osmrx.graph_manager.graph_manager import GraphManager
from osmrx.helpers.logger import Logger

from tests.common.geom_builder import build_network_features


@pytest.fixture()
def features(some_line_features, some_point_features) -> List[Dict]:
    features = build_network_features(some_line_features, some_point_features, None)

    return [feature.to_dict() for feature in features]


def test_pedestrian_graph_building(features):

    graph_manager = GraphManager(Logger().logger, OsmFeatureModes.pedestrian)
    graph_manager.features = features

    assert len(graph_manager.features) == 19
    assert graph_manager.connected_nodes is None
    assert not graph_manager.directed
    assert isinstance(graph_manager.graph, rx.PyGraph)
    assert len(graph_manager.graph.edge_list()) == 19
    assert len(graph_manager.graph.nodes()) == 21
    assert len(set(graph_manager.graph.nodes())) == 21


def test_vehicle_graph_building(some_line_features, some_point_features):

    graph_manager = GraphManager(Logger().logger, OsmFeatureModes.vehicle)
    graph_manager.connected_nodes = some_point_features
    graph_manager.features = some_line_features

    assert len(graph_manager.features) == 36
    assert len(graph_manager.connected_nodes) == len(some_point_features)
    assert graph_manager.directed
    assert isinstance(graph_manager.graph, rx.PyDiGraph)
    assert len(graph_manager.graph.edge_list()) == 36

    assert len(graph_manager.graph.nodes()) == 21
    assert len(set(graph_manager.graph.nodes())) == 21


def test_compute_shortest_path(some_line_features, some_point_features):
    graph_manager = GraphManager(Logger().logger, OsmFeatureModes.vehicle)
    graph_manager.connected_nodes = some_point_features
    graph_manager.features = some_line_features

    edges = graph_manager.compute_shortest_path(
        some_point_features[3]["geometry"],
        some_point_features[9]["geometry"]
    )

    assert len(edges) == 1
    edge = edges[0]
    assert len(edge.features()) == 10
    assert edge.path.length == 0.0013097046149922122
