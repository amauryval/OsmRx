from osm_network.apis_handler.overpass import OverpassApi
from osm_network.helpers.logger import Logger


def overpass_query_result():

    query = 'area(3600134383)->.searchArea;(way["highway"]["area"!~"."](area.searchArea););out geom;(._;>;);'
    return OverpassApi(Logger().logger).query(query)


def test_api_overpass_highway_lines():
    osm_data = overpass_query_result()

    assert len(osm_data) == 4
    assert len(osm_data["elements"]) > 0
