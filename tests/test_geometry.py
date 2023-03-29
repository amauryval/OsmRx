from osm_network.helpers.logger import Logger
from osm_network.topology.checker import TopologyChecker
from osm_network.topology.cleaner import TopologyCleaner


def test_connect_lines(some_line_features, some_point_features):
    raw_data_cleaned = TopologyCleaner(
        Logger().logger,
        some_line_features,
        some_point_features,
        "topo_uuid",
        "id",
        # OsmFeatures.pedestrian,
    ).run()

    features = [feature for feature in raw_data_cleaned]
    assert len(features) == 18

    all_uuid = [feature.topo_uuid for feature in features]
    # check duplicated
    assert len(all_uuid) == len(set(all_uuid))
    assert sorted(all_uuid) == sorted([
        '10_0_forward',
        '10_1_forward',
        '10_2_forward',
        '10_3_forward',
        '10_4_forward',
        '10_5_forward',
        '10_6_forward',
        '10_7_forward',
        '11_0_forward',
        '11_1_forward',
        '12_forward',
        'added_1_forward',
        'added_2_forward',
        'added_3_forward',
        'added_6_forward',
        'added_7_forward',
        'added_8_forward',
        'added_9_forward'
    ])

    for feature in features:
        if feature.topo_status == "unchanged":
            assert "_" in feature.topo_uuid

        if feature.topo_status == "split":
            assert "_" in feature.topo_uuid

        if feature.topo_status == "added":
            assert "added_" in feature.topo_uuid


def test_connect_lines_interpolate_lines(some_line_features, some_point_features):
    raw_data_cleaned = TopologyCleaner(
        Logger().logger,
        some_line_features,
        some_point_features,
        "topo_uuid",
        "id",
        # OsmFeatures.pedestrian,
        True,
    ).run()

    features = [feature for feature in raw_data_cleaned]
    assert len(features) == 192

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
    raw_data_cleaned = TopologyCleaner(
        Logger().logger,
        some_line_features,
        some_point_features,
        "topo_uuid",
        "id",
        False,
    ).run()
    features = [feature for feature in raw_data_cleaned]

    topology = TopologyChecker(features, False)
    assert len(topology.intersections_added) == 20
    assert len(topology.lines_split) == 10
    assert len(topology.lines_unchanged) == 1
    assert len(topology.nodes_added) == 7
