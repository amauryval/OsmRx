from osm_network.apis_handler.models import Location, Bbox

from osm_network.main.pois import Pois
from osm_network.main.roads import Roads

from osm_network.topology.checker import TopologyChecker


def test_get_pois_from_location(location_name):
    pois_session = Pois()
    pois_session.from_location(location_name)

    assert isinstance(pois_session.geo_filter, Location)
    assert pois_session.geo_filter.location_name == "roanne"
    assert "node" in pois_session.query
    assert len(pois_session.data) > 0
    assert isinstance(pois_session.data, list)
    assert isinstance(pois_session.data[0], dict)
    assert not hasattr(pois_session, "network_data")


def test_get_pois_from_bbox(bbox_values):
    pois_session = Pois()
    pois_session.from_bbox(bbox_values)

    assert isinstance(pois_session.geo_filter, Bbox)
    assert pois_session.geo_filter.location_name == str(bbox_values)[1:-1]
    assert "node" in pois_session.query
    assert len(pois_session.data) > 0
    assert isinstance(pois_session.data, list)
    assert isinstance(pois_session.data[0], dict)
    assert not hasattr(pois_session, "network_data")


def test_get_vehicle_network_from_location(vehicle_mode, location_name):
    roads_session = Roads(vehicle_mode)
    roads_session.from_location(location_name)

    assert isinstance(roads_session.geo_filter, Location)
    assert len(roads_session.geo_filter.location_name) > 1
    assert "way" in roads_session.query
    assert len(roads_session.data) > 0
    assert len(roads_session.network_data.features) > 0


def test_get_vehicle_network_from_bbox(pedestrian_mode, bbox_values):
    roads_session = Roads(pedestrian_mode)
    roads_session.from_bbox(bbox_values)

    assert isinstance(roads_session.geo_filter, Bbox)
    assert len(roads_session.geo_filter.location_name) > 1
    assert "way" in roads_session.query
    assert len(roads_session.data) > 0
    assert len(roads_session.network_data.features) > 0

    topology_checked = roads_session.network_data.topology_checker()
    assert len(topology_checked.intersections_added) > 0
    assert len(topology_checked.lines_split) > 0
    assert len(topology_checked.lines_unchanged) > 0
    assert len(topology_checked.nodes_added) == 0
    assert len(topology_checked.lines_added) == 0


def test_get_vehicle_network_from_location_with_pois(vehicle_mode, location_name):
    pois_session = Pois()
    pois_session.from_location(location_name)

    roads_session = Roads(vehicle_mode)
    roads_session.from_location(location_name)
    roads_session.add_nodes = pois_session.data

    assert len(roads_session.data) > 0
    assert len(roads_session.network_data.features) > 0

    topology_checked = roads_session.network_data.topology_checker()
    assert len(topology_checked.intersections_added) > 0
    assert len(topology_checked.lines_split) > 0
    assert len(topology_checked.lines_unchanged) > 0
    assert len(topology_checked.nodes_added) > 0
    assert len(topology_checked.lines_added) > 0
