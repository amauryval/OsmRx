from typing import List, Dict

import pytest

import rustworkx as rx

from osmrx.globals.queries import OsmFeatureModes
from osmrx.network.network_rx import OsmNetworkManager, NetworkRxCore
from osmrx.helpers.logger import Logger

from tests.common.geom_builder import build_network_features


@pytest.fixture()
def features(some_line_features, some_point_features) -> List[Dict]:
    features = build_network_features(some_line_features, some_point_features, None)

    return [feature.to_dict() for feature in features]


def test_pedestrian_graph_building(features):

    osm_network_rx = OsmNetworkManager(OsmFeatureModes.pedestrian, Logger().logger)

    assert osm_network_rx.features is None
    assert osm_network_rx.connected_nodes is None
    assert not osm_network_rx.directed
    assert isinstance(osm_network_rx.graph, rx.PyGraph)
    osm_network_rx.line_features = features
    assert len(osm_network_rx.graph.edge_list()) == 19
    assert len(osm_network_rx.graph.nodes()) == 21
    assert len(set(osm_network_rx.graph.nodes())) == 21


def test_vehicle_graph_building(some_line_features, some_point_features):

    osm_network_rx = OsmNetworkManager(OsmFeatureModes.vehicle)
    assert osm_network_rx.features is None
    osm_network_rx.connected_nodes = some_point_features
    assert osm_network_rx.features is None
    osm_network_rx.line_features = some_line_features

    assert len(osm_network_rx.connected_nodes) == len(some_point_features)
    assert osm_network_rx.directed
    assert isinstance(osm_network_rx.graph, rx.PyDiGraph)
    assert len(osm_network_rx.graph.edge_list()) == 36

    assert len(osm_network_rx.graph.nodes()) == 21
    assert len(set(osm_network_rx.graph.nodes())) == 21


def test_compute_shortest_path(some_line_features, some_point_features):
    osm_network_rx = OsmNetworkManager(OsmFeatureModes.vehicle)
    osm_network_rx.connected_nodes = some_point_features
    osm_network_rx.line_features = some_line_features

    edges = osm_network_rx.compute_shortest_path(
        some_point_features[3]["geometry"],
        some_point_features[9]["geometry"]
    )

    assert len(edges) == 1
    edge = edges[0]
    assert len(edge.features()) == 10
    assert edge.path.length == 0.0013983037109325986


def test_build_undirected_graph_network_from_external_data(some_line_features, some_point_features):
    network_rx = NetworkRxCore(directed=False)
    network_rx.connected_nodes = some_point_features
    network_rx.line_features = some_line_features

    assert len(network_rx.connected_nodes) == len(some_point_features)
    assert not network_rx.directed
    assert isinstance(network_rx.graph, rx.PyGraph)
    assert len(network_rx.graph.edge_list()) == 21

    assert len(network_rx.graph.nodes()) == 21
    assert len(set(network_rx.graph.nodes())) == 21


def test_build_directed_graph_network_from_external_data(some_line_features, some_point_features):
    network_rx = NetworkRxCore(directed=True)
    network_rx.connected_nodes = some_point_features
    network_rx.line_features = some_line_features

    assert len(network_rx.connected_nodes) == len(some_point_features)
    assert network_rx.directed
    assert isinstance(network_rx.graph, rx.PyDiGraph)
    assert len(network_rx.graph.edge_list()) == 21

    assert len(network_rx.graph.nodes()) == 21
    assert len(set(network_rx.graph.nodes())) == 21
