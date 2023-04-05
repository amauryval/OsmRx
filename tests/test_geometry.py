from osmrx.topology.checker import TopologyChecker
from tests.common.geom_builder import build_network_features


def test_connect_lines(some_line_features, some_point_features):
    features = build_network_features(some_line_features, some_point_features, None)

    assert len(features) == 21

    all_uuid = [feature.topo_uuid for feature in features]
    # check duplicated
    assert len(all_uuid) == len(set(all_uuid))
    assert sorted(all_uuid) == sorted(['10_0_forward',
                                       '10_1_forward',
                                       '10_2_forward',
                                       '10_3_forward',
                                       '10_4_forward',
                                       '10_5_forward',
                                       '10_6_forward',
                                       '10_7_forward',
                                       '10_8_forward',
                                       '11_0_forward',
                                       '11_1_forward',
                                       '11_2_forward',
                                       '11_3_forward',
                                       '12_forward',
                                       'added_1_forward',
                                       'added_2_forward',
                                       'added_3_forward',
                                       'added_6_forward',
                                       'added_7_forward',
                                       'added_8_forward',
                                       'added_9_forward'])

    for feature in features:
        if feature.topo_status == "unchanged":
            assert "_" in feature.topo_uuid

        if feature.topo_status == "split":
            assert "_" in feature.topo_uuid

        if feature.topo_status == "added":
            assert "added_" in feature.topo_uuid


def test_connect_lines_interpolate_lines(some_line_features, some_point_features):
    features = build_network_features(some_line_features, some_point_features, 4)

    assert len(features) == 178

    all_uuid = [feature.topo_uuid for feature in features]

    # check duplicated
    assert len(all_uuid) == len(set(all_uuid))

    for feature in features:
        if feature.topo_status == "unchanged":
            assert "_" in feature.topo_uuid

        if feature.topo_status == "split":
            assert "_" in feature.topo_uuid

        if feature.topo_status == "added":
            assert "added_" in feature.topo_uuid


def test_topology(some_line_features, some_point_features):
    features = build_network_features(some_line_features, some_point_features, None)

    topology = TopologyChecker(features, False)
    assert len(topology.intersections_added) == 26
    assert len(topology.lines_split) == 13
    assert len(topology.lines_unchanged) == 1
    assert len(topology.nodes_added) == 7
