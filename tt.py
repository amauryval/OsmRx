from bokeh.plotting import show

import geopandas as gpd

from gdf2bokeh import Gdf2Bokeh

from osmrx import DataFromLocation


location = "Roanne"
pois = DataFromLocation("poi", location)

network_vehicle = DataFromLocation("vehicle", location)
network_vehicle.additional_nodes = pois.data
network_data = network_vehicle.build_graph


map_session = Gdf2Bokeh(
    "My roads and POIs - from OsmNetwork (https://github.com/amauryval)",
)

data = gpd.GeoDataFrame(network_data.to_gdf(), geometry="geometry", crs=f"epsg:{4326}")
data_p = gpd.GeoDataFrame(pois.data, geometry="geometry", crs=f"epsg:{4326}")

map_session.add_layer_from_geodataframe("Roads",
                                     data, from_epsg=4326,
                                     color="black")
map_session.add_layer_from_geodataframe("POIs",
                                     data_p, from_epsg=4326,
                                     color="blue", size=9)

show(map_session.figure)
