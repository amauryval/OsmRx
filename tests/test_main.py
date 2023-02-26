
from osm_network import DataFromBbox
from osm_network import Bbox
from osm_network import Location

from osm_network import DataFromLocation


def test_get_vehicle_network_from_bbox(bbox_values):
    network = DataFromBbox("vehicle", bbox_values)

    assert isinstance(network.geo_filter, Bbox)
    assert len(network.geo_filter.to_str) > 1
    assert "way" in network.query
    assert len(network.result["elements"]) > 0


def test_get_pedestrian_network_from_location(location_name):
    network = DataFromLocation("pedestrian", location_name)

    assert isinstance(network.geo_filter, Location)
    assert network.geo_filter.location_name == "roanne"
    assert "way" in network.query
    assert len(network.result["elements"]) > 0


def test_get_pois_from_location(location_name):
    network = DataFromLocation("poi", location_name)

    assert isinstance(network.geo_filter, Location)
    assert network.geo_filter.location_name == "roanne"
    assert "node" in network.query
    assert len(network.result["elements"]) > 0