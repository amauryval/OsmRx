from osm_network.querier.overpass import OverpassApi


def overpass_query_result():

    query = 'area(3600134383)->.searchArea;(way["highway"]["area"!~"."](area.searchArea););out geom;(._;>;);'
    return OverpassApi().query(query)


def test_api_overpass_railway_lines():
    osm_data = overpass_query_result()

    assert len(osm_data) == 4
    assert len(osm_data["elements"]) > 0
