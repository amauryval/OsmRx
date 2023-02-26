from osm_network.querier.nominatim import NominatimApi


def test_find_a_city_by_name():
    output = NominatimApi(q="Lyon", limit=1).items

    assert len(output) == 1
    assert "Lyon" in output[0]["display_name"]
