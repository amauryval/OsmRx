from shapely import Point

from osmrx.main.roads import GraphAnalysis


def test_shortest_path_performance(vehicle_mode):
    roads_object = GraphAnalysis(vehicle_mode,
                                 [Point(4.0202469917540675, 46.04077488623058),
                                  Point(3.897097653410804, 46.14197681774039)])
    paths_found = roads_object.get_shortest_path()
    paths = [path for path in paths_found]
    assert len(paths) == 1
