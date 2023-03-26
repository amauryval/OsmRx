from osm_network import PoisFromLocation
from osm_network import PoisFromBbox

from osm_network import RoadsFromLocation
from osm_network import RoadsFromBbox

from osm_network.apis_handler.models import Location, Bbox
from osm_network.topology.checker import TopologyChecker


def test_get_pois_from_location(location_name):
    pois_session = PoisFromLocation(location_name)

    assert isinstance(pois_session.geo_filter, Location)
    assert pois_session.geo_filter.location_name == "roanne"
    assert "node" in pois_session.query
    assert len(pois_session.data) > 0
    assert isinstance(pois_session.data, list)
    assert isinstance(pois_session.data[0], dict)
    assert not hasattr(pois_session, "network_data")


def test_get_pois_from_bbox(bbox_values):
    pois_session = PoisFromBbox(bbox_values)

    assert isinstance(pois_session.geo_filter, Bbox)
    assert pois_session.geo_filter.to_str == str(bbox_values)[1:-1]
    assert "node" in pois_session.query
    assert len(pois_session.data) > 0
    assert isinstance(pois_session.data, list)
    assert isinstance(pois_session.data[0], dict)
    assert not hasattr(pois_session, "network_data")


def test_get_vehicle_network_from_location(vehicle_mode, location_name):
    network = RoadsFromLocation(vehicle_mode, location_name)

    assert isinstance(network.geo_filter, Location)
    assert len(network.geo_filter.location_name) > 1
    assert "way" in network.query
    assert len(network.data) > 0
    assert len(network.network_data.features) > 0


def test_get_vehicle_network_from_bbox(pedestrian_mode, bbox_values):
    network = RoadsFromBbox(pedestrian_mode, bbox_values)

    assert isinstance(network.geo_filter, Bbox)
    assert len(network.geo_filter.to_str) > 1
    assert "way" in network.query
    assert len(network.data) > 0
    assert len(network.network_data.features) > 0

    data = [f.to_dict() for f in network.network_data.features]
    topology_checked = TopologyChecker(data, True)
    assert len(topology_checked.intersections_added) > 0
    assert len(topology_checked.lines_split) > 0
    assert len(topology_checked.lines_unchanged) > 0
    assert len(topology_checked.nodes_added) == 0
