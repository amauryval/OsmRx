from osm_network.apis_handler.nominatim import NominatimApi
from osm_network.helpers.logger import Logger


def test_find_a_city_by_name():
    output = NominatimApi(Logger().logger, q="roanne", limit=1).items

    assert len(output) == 1
    assert "Roanne" in output[0]["display_name"]
