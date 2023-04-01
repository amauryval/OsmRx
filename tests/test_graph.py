import pytest

import rustworkx as rx

from osm_network.globals.queries import OsmFeatureModes
from osm_network.graph_manager.graph_manager import GraphManager
from osm_network.helpers.logger import Logger

from tests.common.geom_builder import build_network_features


@pytest.fixture()
def features(some_line_features, some_point_features) -> str:
    features = build_network_features(some_line_features, some_point_features, None)

    return [feature.to_dict() for feature in features]


def test_pedestrian_graph(features):

    graph_manager = GraphManager(Logger().logger, OsmFeatureModes.pedestrian)
    graph_manager.features = features

    assert len(graph_manager.features) == 18
    assert not graph_manager.directed
    assert isinstance(graph_manager.graph, rx.PyGraph)
    assert len(graph_manager.graph.edge_list()) == 18
    assert len(graph_manager.graph.nodes()) == 20
    assert len(set(graph_manager.graph.nodes())) == 20


def test_vehicle_graph(features):

    graph_manager = GraphManager(Logger().logger, OsmFeatureModes.vehicle)
    graph_manager.features = features

    assert len(graph_manager.features) == 29
    assert graph_manager.directed
    assert isinstance(graph_manager.graph, rx.PyDiGraph)
    assert len(graph_manager.graph.edge_list()) == 29

    assert len(graph_manager.graph.nodes()) == 20
    assert len(set(graph_manager.graph.nodes())) == 20
