from osmrx import Bbox
from osmrx import Location

from osmrx import DataFromBbox
from osmrx import DataFromLocation

from osmrx.topology.checker import TopologyChecker


def test_get_vehicle_network_from_bbox(vehicle_mode, bbox_values):
    network = DataFromBbox(vehicle_mode, bbox_values)

    assert isinstance(network.geo_filter, Bbox)
    assert len(network.geo_filter.to_str) > 1
    assert "way" in network.query
    assert len(network.clean()) > 0


def test_get_pedestrian_network_from_location(pedestrian_mode, location_name):
    network = DataFromLocation(pedestrian_mode, location_name)

    assert isinstance(network.geo_filter, Location)
    assert network.geo_filter.location_name == "roanne"
    assert "way" in network.query
    network_found = network.clean()
    assert len(network_found) > 0

    topology_checked = TopologyChecker(network_found, True)
    assert len(topology_checked.intersections_added) > 0
    assert len(topology_checked.lines_split) > 0
    assert len(topology_checked.lines_unchanged) > 0
    assert len(topology_checked.nodes_added) == 0


def test_get_pois_from_location(poi_mode, location_name):
    network = DataFromLocation(poi_mode, location_name)

    assert isinstance(network.geo_filter, Location)
    assert network.geo_filter.location_name == "roanne"
    assert "node" in network.query
    assert len(network.clean()) > 0
