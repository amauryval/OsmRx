from osmrx.apis_handler.models import Location, Bbox
from osmrx.graph_manager.arc_feature import ArcFeature

from osmrx.main.pois import Pois
from osmrx.main.roads import Roads


def test_get_pois_from_location(location_name):
    pois_session = Pois()
    pois_session.from_location(location_name)

    assert isinstance(pois_session.geo_filter, Location)
    assert pois_session.geo_filter.location_name == "roanne"
    assert "node" in pois_session.query
    assert len(pois_session.data) > 0
    assert isinstance(pois_session.data, list)
    assert isinstance(pois_session.data[0], dict)
    assert {'id', 'osm_url', 'topo_uuid', 'geometry'}.issubset(pois_session.data[0].keys())
    assert not hasattr(pois_session, "network_data")


def test_get_pois_from_bbox(bbox_values):
    pois_session = Pois()
    pois_session.from_bbox(bbox_values)

    assert isinstance(pois_session.geo_filter, Bbox)
    assert pois_session.geo_filter.location_name == str(bbox_values)[1:-1]
    assert "node" in pois_session.query
    assert len(pois_session.data) > 1
    assert isinstance(pois_session.data, list)
    assert isinstance(pois_session.data[0], dict)
    assert {'id', 'osm_url', 'topo_uuid', 'geometry'}.issubset(pois_session.data[0].keys())
    assert not hasattr(pois_session, "network_data")


def test_get_vehicle_network_from_location(vehicle_mode, location_name):
    roads_session = Roads(vehicle_mode)
    roads_session.from_location(location_name)

    assert isinstance(roads_session.geo_filter, Location)
    assert len(roads_session.geo_filter.location_name) > 1
    assert "way" in roads_session.query
    roads_session.build_graph()
    assert len(roads_session.data) > 0
    assert isinstance(roads_session.data, list)
    assert isinstance(roads_session.data[0], dict)
    assert {'id', 'topo_uuid', 'topo_status', 'geometry', 'direction', 'osm_url'}.issubset(roads_session.data[0].keys())


def test_get_pedestrian_network_from_bbox_with_topo_checker(pedestrian_mode, bbox_values):
    """test if calling twice network_data method is working"""
    roads_session = Roads(pedestrian_mode)
    roads_session.from_bbox(bbox_values)

    assert isinstance(roads_session.geo_filter, Bbox)
    assert len(roads_session.geo_filter.location_name) > 1
    assert "way" in roads_session.query
    roads_session.build_graph()
    assert len(roads_session.data) > 1
    topology_checked = roads_session.topology_checker()
    assert len(topology_checked.intersections_added) > 1
    assert len(topology_checked.lines_split) > 1
    assert len(topology_checked.lines_unchanged) > 1
    assert len(topology_checked.nodes_added) == 0
    assert len(topology_checked.lines_added) == 0


def test_get_vehicle_network_from_bbox_without_topo_checker(pedestrian_mode, bbox_values):
    """test if calling twice network_data method is working"""
    roads_session = Roads(pedestrian_mode)
    roads_session.from_bbox(bbox_values)

    assert isinstance(roads_session.geo_filter, Bbox)
    assert len(roads_session.geo_filter.location_name) > 1
    assert "way" in roads_session.query

    roads_session.build_graph()
    assert len(roads_session.data) > 1
    # assert len(roads_session.network_data.features) > 1


def test_get_vehicle_network_from_bbox_with_topo_checker_simplified(vehicle_mode, bbox_values):
    roads_session = Roads(vehicle_mode)
    roads_session.from_bbox(bbox_values)

    assert isinstance(roads_session.geo_filter, Bbox)
    assert len(roads_session.geo_filter.location_name) > 1
    assert "way" in roads_session.query

    roads_session.build_graph()
    assert len(roads_session.data) > 10000  # could be changed if osm data is updated

    topology_checked = roads_session.topology_checker()
    assert len(topology_checked.intersections_added) > 1
    assert len(topology_checked.lines_split) > 1
    assert len(topology_checked.lines_unchanged) > 1
    assert len(topology_checked.nodes_added) == 0
    assert len(topology_checked.lines_added) == 0
    # import geopandas as gpd
    # gpd.GeoDataFrame([f.to_dict() for f in roads_session.data], geometry="geometry", crs=f"epsg:{4326}").to_file('vvv.gpkg', driver='GPKG', layer='name')


def test_get_pedestrian_network_from_bbox_with_topo_checker_simplified(pedestrian_mode, bbox_values):
    roads_session = Roads(pedestrian_mode)
    roads_session.from_bbox(bbox_values)

    assert isinstance(roads_session.geo_filter, Bbox)
    assert len(roads_session.geo_filter.location_name) > 1
    assert "way" in roads_session.query

    roads_session.build_graph()
    assert len(roads_session.data) == 9849  # could be change if osm data is updated

    topology_checked = roads_session.topology_checker()
    assert len(topology_checked.intersections_added) > 1
    assert len(topology_checked.lines_split) > 1
    assert len(topology_checked.lines_unchanged) > 1
    assert len(topology_checked.nodes_added) == 0
    assert len(topology_checked.lines_added) == 0


def test_get_vehicle_network_from_location_with_pois_with_topo_checker(vehicle_mode, location_name):
    pois_session = Pois()
    pois_session.from_location(location_name)
    assert len(pois_session.data) > 1

    roads_session = Roads(vehicle_mode)
    roads_session.from_location(location_name)
    roads_session.additional_nodes = pois_session.data

    assert len(roads_session.data) == 0
    roads_session.build_graph()
    assert len(roads_session.data) > 1
    topology_checked = roads_session.topology_checker()
    assert len(topology_checked.intersections_added) > 1
    assert len(topology_checked.lines_split) > 1
    assert len(topology_checked.lines_unchanged) > 1
    assert len(topology_checked.nodes_added) > 1
    assert len(topology_checked.lines_added) > 1


def test_get_vehicle_network_from_location_with_pois_without_topo_checker(vehicle_mode, location_name):
    pois_session = Pois()
    pois_session.from_location(location_name)
    assert len(pois_session.data) > 1

    roads_session = Roads(vehicle_mode)
    roads_session.from_location(location_name)
    roads_session.additional_nodes = pois_session.data

    roads_session.build_graph()
    assert len(roads_session.data) > 0


def test_get_vehicle_network_from_location_shortest_path(vehicle_mode, location_name):
    pois_session = Pois()
    pois_session.from_location(location_name)

    roads_session = Roads(vehicle_mode)
    roads_session.from_location(location_name)
    roads_session.additional_nodes = pois_session.data

    roads_session.build_graph()

    paths_found = roads_session._graph_manager.compute_shortest_path(
        pois_session.data[10]["geometry"].wkt,
        pois_session.data[150]["geometry"].wkt,
    )
    assert len(paths_found) == 1
    assert paths_found[0].path.length == 0.013235288256492393  # could change if oms data is updated
    assert len(paths_found[0].features) == 45  # could change if oms data is updated


def test_get_pedestrian_network_from_location_shortest_path(pedestrian_mode, location_name):
    pois_session = Pois()
    pois_session.from_location(location_name)

    roads_session = Roads(pedestrian_mode)
    roads_session.from_location(location_name)
    roads_session.additional_nodes = pois_session.data

    roads_session.build_graph()

    paths_found = roads_session._graph_manager.compute_shortest_path(
        pois_session.data[10]["geometry"].wkt,
        pois_session.data[150]["geometry"].wkt,
    )
    assert len(paths_found) == 1
    assert paths_found[0].path.length == 0.011041354246022669  # could change if oms data is updated
    assert len(paths_found[0].features) == 41  # could change if oms data is updated


def test_pedestrian_isochrones(pedestrian_mode, location_name):
    pois_session = Pois()
    pois_session.from_location(location_name)

    roads_session = Roads(pedestrian_mode)
    roads_session.from_location(location_name)
    roads_session.additional_nodes = pois_session.data

    roads_session.build_graph()
    isochrones_built = roads_session._graph_manager.isochrone(
        pois_session.data[10]["geometry"].wkt,
    )
    assert len(isochrones_built) == 3
    for isochrone in isochrones_built.values():
        assert isochrone.geom_type == "Polygon"
        assert isochrone.area > 0


def test_vehicle_isochrone(vehicle_mode, location_name):
    pois_session = Pois()
    pois_session.from_location(location_name)

    roads_session = Roads(vehicle_mode)
    roads_session.from_location(location_name)
    roads_session.additional_nodes = pois_session.data

    roads_session.build_graph()
    isochrones_built = roads_session._graph_manager.isochrone(
        pois_session.data[10]["geometry"].wkt,
    )
    assert len(isochrones_built) == 3
    for isochrone in isochrones_built.values():
        assert isochrone.geom_type == "Polygon"
        assert isochrone.area > 0
