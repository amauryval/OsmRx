from osm_network import NetworkFromBbox
from osm_network import NetworkFromLocation


def test_get_network_from_bbox(bbox_values):
    network = NetworkFromBbox("vehicle",  bbox_values)

    assert network


def test_get_network_from_location(location_name):
    network = NetworkFromLocation("pedestrian",  location_name)

    assert network