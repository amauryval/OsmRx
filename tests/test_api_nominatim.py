from osm_network.querier.nominatim import NominatimApi


def test_find_a_city_by_name():
    output = NominatimApi(q="roanne", limit=1).items

    assert len(output) == 1
    assert "Roanne" in output[0]["display_name"]
