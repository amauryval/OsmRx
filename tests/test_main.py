from shapely import Point

from osmrx.apis_handler.models import Location, Bbox

from osmrx.main.pois import Pois
from osmrx.main.roads import Roads, GraphAnalysis


def test_get_pois_from_location(location_name):
    pois_session = Pois()
    pois_session.from_location(location_name)

    assert isinstance(pois_session.geo_filter, Location)
    assert pois_session.geo_filter.location_name == "roanne"
    assert "node" in pois_session.query
    assert len(pois_session.data) > 0
    assert isinstance(pois_session.data, list)
    assert isinstance(pois_session.data[0], dict)
    assert {'id', 'osm_url', 'topo_uuid', 'geometry'}.issubset(pois_session.data[0].keys())
    assert not hasattr(pois_session, "network_data")


def test_get_pois_from_bbox(bbox_values):
    pois_session = Pois()
    pois_session.from_bbox(bbox_values)

    assert isinstance(pois_session.geo_filter, Bbox)
    assert pois_session.geo_filter.location_name == str(bbox_values)[1:-1]
    assert "node" in pois_session.query
    assert len(pois_session.data) > 1
    assert isinstance(pois_session.data, list)
    assert isinstance(pois_session.data[0], dict)
    assert {'id', 'osm_url', 'topo_uuid', 'geometry'}.issubset(pois_session.data[0].keys())
    assert not hasattr(pois_session, "network_data")


def test_get_vehicle_network_from_location(vehicle_mode, location_name):
    roads_session = Roads(vehicle_mode)
    roads_session.from_location(location_name)

    assert isinstance(roads_session.geo_filter, Location)
    assert len(roads_session.geo_filter.location_name) > 1
    assert "way" in roads_session.query
    assert len(roads_session.data) > 0
    assert isinstance(roads_session.data, list)
    assert isinstance(roads_session.data[0], dict)
    assert {'id', 'topo_uuid', 'topo_status', 'geometry', 'direction', 'osm_url'}.issubset(roads_session.data[0].keys())


def test_get_pedestrian_network_from_bbox_with_topo_checker(pedestrian_mode, bbox_values):
    """test if calling twice network_data method is working"""
    roads_session = Roads(pedestrian_mode)
    roads_session.from_bbox(bbox_values)

    topology_checked = roads_session.topology_checker()
    assert len(topology_checked.intersections_added) > 1
    assert len(topology_checked.lines_split) > 1
    assert len(topology_checked.lines_unchanged) > 1
    assert len(topology_checked.nodes_added) == 0
    assert len(topology_checked.lines_added) == 0


def test_get_vehicle_network_from_bbox_without_topo_checker(pedestrian_mode, bbox_values):
    """test if calling twice network_data method is working"""
    roads_session = Roads(pedestrian_mode)
    roads_session.from_bbox(bbox_values)

    assert len(roads_session.data) > 1


def test_get_vehicle_network_from_bbox_with_topo_checker_simplified(vehicle_mode, bbox_values):
    roads_session = Roads(vehicle_mode)
    roads_session.from_bbox(bbox_values)

    assert len(roads_session.data) > 10000  # could be changed if osm data is updated

    topology_checked = roads_session.topology_checker()
    assert len(topology_checked.intersections_added) > 1
    assert len(topology_checked.lines_split) > 1
    assert len(topology_checked.lines_unchanged) > 1
    assert len(topology_checked.nodes_added) == 0
    assert len(topology_checked.lines_added) == 0


def test_get_pedestrian_network_from_bbox_with_topo_checker_simplified(pedestrian_mode, bbox_values):
    roads_session = Roads(pedestrian_mode)
    roads_session.from_bbox(bbox_values)

    assert len(roads_session.data) == 9849  # could be change if osm data is updated

    topology_checked = roads_session.topology_checker()
    assert len(topology_checked.intersections_added) > 1
    assert len(topology_checked.lines_split) > 1
    assert len(topology_checked.lines_unchanged) > 1
    assert len(topology_checked.nodes_added) == 0
    assert len(topology_checked.lines_added) == 0


def test_get_vehicle_network_from_location_with_pois_with_topo_checker(vehicle_mode, location_name):
    pois_session = Pois()
    pois_session.from_location(location_name)
    assert len(pois_session.data) > 1

    roads_session = Roads(vehicle_mode, pois_session.data)
    assert roads_session.data is None

    roads_session.from_location(location_name)
    assert len(roads_session.data) > 1

    topology_checked = roads_session.topology_checker()
    assert len(topology_checked.intersections_added) > 1
    assert len(topology_checked.lines_split) > 1
    assert len(topology_checked.lines_unchanged) > 1
    assert len(topology_checked.nodes_added) > 1
    assert len(topology_checked.lines_added) > 1


def test_get_vehicle_network_from_location_with_pois_without_topo_checker(vehicle_mode, location_name):
    pois_session = Pois()
    pois_session.from_location(location_name)

    roads_session = Roads(vehicle_mode, pois_session.data)
    roads_session.from_location(location_name)

    assert len(roads_session.additional_nodes) == len(pois_session.data)
    assert len(roads_session.data) > 0


def test_get_vehicle_network_from_location_shortest_path(vehicle_mode, location_name):
    roads_session = GraphAnalysis(vehicle_mode,
                                  [Point(4.0793058, 46.0350304), Point(4.0725246, 46.0397676)])
    paths_found = roads_session.get_shortest_path()
    paths = [path for path in paths_found]
    assert len(paths) == 1
    assert paths[0].path.length == 0.014231160335524648  # could change if oms data is updated
    assert len(paths[0].features()) == 37  # could change if oms data is updated


def test_get_pedestrian_network_from_location_shortest_path(pedestrian_mode, location_name):
    roads_session = GraphAnalysis(pedestrian_mode,
                                  [Point(4.0793058, 46.0350304), Point(4.0725246, 46.0397676)])
    paths_found = roads_session.get_shortest_path()
    paths = [path for path in paths_found]
    assert len(paths) == 1
    assert paths[0].path.length == 0.011040368374582707  # could change if oms data is updated
    assert len(paths[0].features()) == 33  # 41  # could change if oms data is updated


def test_pedestrian_isochrones(pedestrian_mode, location_name):
    roads_session = GraphAnalysis(pedestrian_mode, [Point(4.0793058, 46.0350304)])
    isochrones_built = roads_session.isochrones_from_distance([0, 250, 500, 1000])

    assert len(isochrones_built.intervals) == 3
    assert len(isochrones_built.data) == 3

    isochrone_area = None
    for enum, isochrone in enumerate(isochrones_built.data.values()):
        assert isochrone.area > 0
        assert isochrone.geom_type == "Polygon"
        if enum == 0:
            isochrone_area = isochrone.area
        else:
            assert isochrone_area >= isochrone.area
            isochrone_area = isochrone.area


def test_vehicle_isochrone(vehicle_mode, location_name):
    roads_session = GraphAnalysis(vehicle_mode, [Point(4.0793058, 46.0350304)])
    isochrones_built = roads_session.isochrones_from_distance([0, 250, 500, 1000, 1500])

    assert len(isochrones_built.intervals) == 4
    assert len(isochrones_built.data) == 4

    isochrone_area = None
    for enum, isochrone in enumerate(isochrones_built.data.values()):
        assert isochrone.area > 0
        assert isochrone.geom_type == "Polygon"
        if enum == 0:
            isochrone_area = isochrone.area
        else:
            assert isochrone_area >= isochrone.area
            isochrone_area = isochrone.area
