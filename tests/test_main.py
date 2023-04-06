from shapely import Point

from osmrx.apis_handler.models import Location, Bbox

from osmrx.main.pois import Pois
from osmrx.main.roads import Roads, GraphAnalysis


def test_get_pois_from_location(location_name):
    pois_object = Pois()
    pois_object.from_location(location_name)

    assert isinstance(pois_object.geo_filter, Location)
    assert pois_object.geo_filter.location_name == "roanne"
    assert "node" in pois_object.query
    assert len(pois_object.data) > 0
    assert isinstance(pois_object.data, list)
    assert isinstance(pois_object.data[0], dict)
    assert {'id', 'osm_url', 'topo_uuid', 'geometry'}.issubset(pois_object.data[0].keys())
    assert not hasattr(pois_object, "network_data")


def test_get_pois_from_bbox(bbox_values):
    pois_object = Pois()
    pois_object.from_bbox(bbox_values)

    assert isinstance(pois_object.geo_filter, Bbox)
    assert pois_object.geo_filter.location_name == str(bbox_values)[1:-1]
    assert "node" in pois_object.query
    assert len(pois_object.data) > 1
    assert isinstance(pois_object.data, list)
    assert isinstance(pois_object.data[0], dict)
    assert {'id', 'osm_url', 'topo_uuid', 'geometry'}.issubset(pois_object.data[0].keys())
    assert not hasattr(pois_object, "network_data")


def test_get_vehicle_network_from_location(vehicle_mode, location_name):
    roads_object = Roads(vehicle_mode)
    roads_object.from_location(location_name)

    assert isinstance(roads_object.geo_filter, Location)
    assert len(roads_object.geo_filter.location_name) > 1
    assert "way" in roads_object.query
    assert len(roads_object.data) > 0
    assert isinstance(roads_object.data, list)
    assert isinstance(roads_object.data[0], dict)
    assert {'id', 'topo_uuid', 'topo_status', 'geometry', 'direction', 'osm_url'}.issubset(roads_object.data[0].keys())


def test_get_pedestrian_network_from_bbox_with_topo_checker(pedestrian_mode, bbox_values):
    """test if calling twice network_data method is working"""
    roads_object = Roads(pedestrian_mode)
    roads_object.from_bbox(bbox_values)

    topology_checked = roads_object.topology_checker()
    assert len(topology_checked.intersections_added) > 1
    assert len(topology_checked.lines_split) > 1
    assert len(topology_checked.lines_unchanged) > 1
    assert len(topology_checked.nodes_added) == 0
    assert len(topology_checked.lines_added) == 0


def test_get_vehicle_network_from_bbox_without_topo_checker(pedestrian_mode, bbox_values):
    """test if calling twice network_data method is working"""
    roads_object = Roads(pedestrian_mode)
    roads_object.from_bbox(bbox_values)

    assert len(roads_object.data) > 1


def test_get_vehicle_network_from_bbox_with_topo_checker_simplified(vehicle_mode, bbox_values):
    roads_object = Roads(vehicle_mode)
    roads_object.from_bbox(bbox_values)

    assert len(roads_object.data) > 10000  # could be changed if osm data is updated

    topology_checked = roads_object.topology_checker()
    assert len(topology_checked.intersections_added) > 1
    assert len(topology_checked.lines_split) > 1
    assert len(topology_checked.lines_unchanged) > 1
    assert len(topology_checked.nodes_added) == 0
    assert len(topology_checked.lines_added) == 0


def test_get_pedestrian_network_from_bbox_with_topo_checker_simplified(pedestrian_mode, bbox_values):
    roads_object = Roads(pedestrian_mode)
    roads_object.from_bbox(bbox_values)

    assert len(roads_object.data) == 9849  # could be change if osm data is updated

    topology_checked = roads_object.topology_checker()
    assert len(topology_checked.intersections_added) > 1
    assert len(topology_checked.lines_split) > 1
    assert len(topology_checked.lines_unchanged) > 1
    assert len(topology_checked.nodes_added) == 0
    assert len(topology_checked.lines_added) == 0


def test_get_vehicle_network_from_location_with_pois_with_topo_checker(vehicle_mode, location_name):
    pois_object = Pois()
    pois_object.from_location(location_name)
    assert len(pois_object.data) > 1

    roads_object = Roads(vehicle_mode, pois_object.data)
    assert roads_object.data is None

    roads_object.from_location(location_name)
    assert len(roads_object.data) > 1

    topology_checked = roads_object.topology_checker()
    assert len(topology_checked.intersections_added) > 1
    assert len(topology_checked.lines_split) > 1
    assert len(topology_checked.lines_unchanged) > 1
    assert len(topology_checked.nodes_added) > 1
    assert len(topology_checked.lines_added) > 1


def test_get_vehicle_network_from_location_with_pois_without_topo_checker(vehicle_mode, location_name):
    pois_object = Pois()
    pois_object.from_location(location_name)

    roads_object = Roads(vehicle_mode, pois_object.data)
    roads_object.from_location(location_name)

    assert len(roads_object.additional_nodes) == len(pois_object.data)
    assert len(roads_object.data) > 0


def test_get_vehicle_network_from_location_shortest_path(vehicle_mode, location_name):
    roads_object = GraphAnalysis(vehicle_mode,
                                  [Point(4.0793058, 46.0350304), Point(4.0725246, 46.0397676)])
    paths_found = roads_object.get_shortest_path()
    paths = [path for path in paths_found]
    assert len(paths) == 1
    assert paths[0].path.length == 0.014231160335524648  # could change if oms data is updated
    assert len(paths[0].features()) == 37  # could change if oms data is updated


def test_get_pedestrian_network_from_location_shortest_path(pedestrian_mode, location_name):
    roads_object = GraphAnalysis(pedestrian_mode,
                                  [Point(4.0793058, 46.0350304), Point(4.0725246, 46.0397676)])
    paths_found = roads_object.get_shortest_path()
    paths = [path for path in paths_found]
    assert len(paths) == 1
    assert paths[0].path.length == 0.011040368374582707  # could change if oms data is updated
    assert len(paths[0].features()) == 33  # 41  # could change if oms data is updated


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
