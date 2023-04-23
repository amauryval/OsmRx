import pytest
from shapely import Point, LineString

from osmrx.main.roads import GraphAnalysis


def test_get_vehicle_network_shortest_path(vehicle_mode, location_name):
    roads_object = GraphAnalysis(vehicle_mode,
                                  [Point(4.0793058, 46.0350304), Point(4.0725246, 46.0397676)])
    paths_found = roads_object.get_shortest_path()
    paths = [path for path in paths_found]
    assert len(paths) == 1
    assert isinstance(paths[0].path, LineString)
    assert paths[0].path.length == 0.014511463826761944  # could change if oms data is updated
    assert len(paths[0].features()) == 37  # could change if oms data is updated
    assert sum(feat["geometry"].length for feat in paths[0].features()) == paths[0].path.length


def test_get_pedestrian_network_from_location_shortest_path_with_2_points(pedestrian_mode, location_name):
    roads_object = GraphAnalysis(pedestrian_mode,
                                  [Point(4.062595199999999, 46.0262591), Point(4.085804300000001, 46.0442448)])
    paths_found = roads_object.get_shortest_path()
    paths = [path for path in paths_found]
    assert len(paths) == 1
    assert isinstance(paths[0].path, LineString)
    path_found_length = 0.03366448962206039  # could change if oms data is updated
    assert paths[0].path.length == path_found_length
    assert sum(feat["geometry"].length for feat in paths[0].features()) == path_found_length
    assert len(paths[0].path.coords[:]) == 152
    assert len(paths[0].features()) == 74  # could change if oms data is updated


def test_get_pedestrian_network_from_location_shortest_path_with_2_equals_points(pedestrian_mode, location_name):
    roads_object = GraphAnalysis(pedestrian_mode,
                                  [Point(4.0793058, 46.0350304), Point(4.0793058, 46.0350304)])
    with pytest.raises(AssertionError) as err:
        _ = roads_object.get_shortest_path()
        assert err.value.args[0] == 'Your points must be different'


def test_get_pedestrian_network_from_location_shortest_path_with_3_points(pedestrian_mode, location_name):
    roads_object = GraphAnalysis(pedestrian_mode,
                                 [Point(4.0793058, 46.0350304), Point(4.0725246, 46.0397676), Point(4.0793058, 46.0350304)])
    paths_found = roads_object.get_shortest_path()
    paths = [path for path in paths_found]
    assert len(paths) == 2
    assert isinstance(paths[0].path, LineString)
    assert isinstance(paths[-1].path, LineString)

    assert len(paths[0].features()) == 33  # could change if oms data is updated
    assert len(paths[0].features()) == len(paths[-1].features())

    assert paths[0].path.length == paths[-1].path.length
    assert paths[0].path.length == 0.011108054721315923  # could change if oms data is updated
    assert sum(feat["geometry"].length for feat in paths[0].features()) == 0.011108054721315926


def test_get_vehicle_network_from_location_shortest_path_with_3_points(vehicle_mode, location_name):
    roads_object = GraphAnalysis(vehicle_mode,
                                 [Point(4.0793058, 46.0350304), Point(4.0725246, 46.0397676), Point(4.0793058, 46.0350304)])
    paths_found = roads_object.get_shortest_path()
    paths = [path for path in paths_found]
    assert len(paths) == 2
    assert isinstance(paths[0].path, LineString)
    assert isinstance(paths[-1].path, LineString)
    assert paths[0].path.length == 0.014511463826761944  # could change if oms data is updated
    assert sum(feat["geometry"].length for feat in paths[0].features()) == paths[0].path.length
    assert len(paths[0].features()) == 37  # could change if oms data is updated
    assert paths[-1].path.length == 0.013127330294668097  # could change if oms data is updated
    assert len(paths[-1].features()) == 43  # could change if oms data is updated


def test_shortest_path_performance(vehicle_mode):
    roads_object = GraphAnalysis(vehicle_mode,
                                 [Point(4.0202469917540675, 46.04077488623058),
                                  Point(3.897097653410804, 46.14197681774039)])
    paths_found = roads_object.get_shortest_path()
    paths = [path for path in paths_found]
    assert len(paths) == 1
    assert isinstance(paths[0].path, LineString)
    assert paths[0].path.length == 0.1897312918236447  # could change if oms data is updated
    assert len(paths[0].features()) == 110  # could change if oms data is updated


def test_pedestrian_isochrones(pedestrian_mode, location_name):
    analysis_object = GraphAnalysis(pedestrian_mode, [Point(4.0793058, 46.0350304)])
    isochrones_built = analysis_object.isochrones_from_distance([0, 250, 500, 1000])

    assert len(isochrones_built.intervals) == 3
    assert len(isochrones_built.data) == 3

    areas_list = [geom["geometry"].area for geom in isochrones_built.data][::-1]
    assert all(areas_list[idx] <= areas_list[idx + 1] for idx in range(len(areas_list) - 1))


def test_vehicle_isochrone(vehicle_mode, location_name):
    analysis_object = GraphAnalysis(vehicle_mode, [Point(4.0793058, 46.0350304)])
    isochrones_built = analysis_object.isochrones_from_distance([0, 250, 500, 1000, 1500])

    assert len(isochrones_built.intervals) == 4
    assert len(isochrones_built.data) == 4

    areas_list = [geom["geometry"].area for geom in isochrones_built.data][::-1]
    assert all(areas_list[idx] <= areas_list[idx + 1] for idx in range(len(areas_list) - 1))
