from osm_network.helpers.logger import Logger
from osm_network.topology.checker import TopologyChecker

from osm_network.topology.cleaner import TopologyCleaner

from osm_network.globals.queries import OsmFeatureModes


def test_connect_lines(some_line_features, some_point_features):
    raw_data_topology_rebuild = TopologyCleaner(
        Logger().logger,
        some_line_features,
        some_point_features,
        "topo_uuid",
        "id",
        # OsmFeatures.pedestrian,
    ).run()

    all_uuid = [feature.topo_uuid for feature in raw_data_topology_rebuild]

    assert len(raw_data_topology_rebuild) == 18
    # check duplicated
    assert len(all_uuid) == len(set(all_uuid))
    assert sorted(all_uuid) == sorted(
        [
            "10_0",
            "10_1",
            "10_2",
            "10_3",
            "10_4",
            "10_5",
            "10_6",
            "10_7",
            "11_0",
            "11_1",
            "12",
            "added_1",
            "added_2",
            "added_3",
            "added_6",
            "added_7",
            "added_8",
            "added_9",
        ]
    )

    for feature in raw_data_topology_rebuild:
        if feature.topo_status == "unchanged":
            assert "_" not in feature.topo_uuid

        if feature.topo_status == "split":
            assert "_" in feature.topo_uuid

        if feature.topo_status == "added":
            assert "added_" in feature.topo_uuid


def test_connect_lines_interpolate_lines(some_line_features, some_point_features):
    raw_data_topology_rebuild = TopologyCleaner(
        Logger().logger,
        some_line_features,
        some_point_features,
        "topo_uuid",
        "id",
        # OsmFeatures.pedestrian,
        True,
    ).run()

    all_uuid = [feature.topo_uuid for feature in raw_data_topology_rebuild]

    assert len(raw_data_topology_rebuild) == 192
    # check duplicated
    assert len(all_uuid) == len(set(all_uuid))

    for feature in raw_data_topology_rebuild:
        if feature.topo_status == "unchanged":
            assert "_" in feature.topo_uuid

        if feature.topo_status == "split":
            assert "_" in feature.topo_uuid

        if feature.topo_status == "added":
            assert "added_" in feature.topo_uuid


def test_topology(some_line_features, some_point_features):
    raw_data_topology_rebuild = TopologyCleaner(
        Logger().logger,
        some_line_features,
        some_point_features,
        "topo_uuid",
        "id",
        # OsmFeatures.pedestrian,
        False,
    ).run()
    data = [f.__dict__ for f in raw_data_topology_rebuild]
    topology_checked = TopologyChecker(data, False)
    assert len(topology_checked.intersections_added) == 20
    assert len(topology_checked.lines_split) == 10
    assert len(topology_checked.lines_unchanged) == 1
    assert len(topology_checked.nodes_added) == 7
