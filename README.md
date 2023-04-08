# OsmRx

A geographic Python library to extract Open Street Map roads (and POIs) from a location or a bounding box, in order to create a graph thanks to [Rustworkx](https://github.com/Qiskit/rustworkx). OsmRx is able to clean a network based on Linestring geometries and connect Point geometries. The graph built is able to process graph-analysis (shortest-path, isochrones...)

Capabilities:
* load data from a location name or a bounding box (roads and pois)
* graph creation (and topology processing and cleaning)
* shortest path
* isochrone builder

[![CI](https://github.com/amauryval/osmrx/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/amauryval/osmrx/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/amauryval/osmrx/branch/master/graph/badge.svg)](https://codecov.io/gh/amauryval/osmrx)

[![PyPI version](https://badge.fury.io/py/osmrx.svg)](https://badge.fury.io/py/osmrx)

Check the demo [here](https://amauryval.github.io/omsrx/)


## How to install it ?

### with pip

```bash
pip install osmrx
```

## How to use it ?

Check the jupyter notebook [here](https://amauryval.github.io/OsmRx/)

Check the wiki: TODO

### Get POIs

Find the Points of interest from a location (Point(s)) or a bounding box: 
* OSM attributes are returned
* features ready to be used with shapely, GeoPandas (...):


```python
from osmrx.main.pois import Pois

location_name = "lyon"  

# Initialize the Pois class
pois_object = Pois()
# call .from_location(location: str) or .from_bbox(bounds: Tuple[float, float, float, float]) to get data from your location
pois_object.from_location(location_name)  # nominatim api is used to get Lyon coordinates

# It returns a list of dictionnaries [{"geometry": Point(...), "attribute": "...", ...}
# Free for you to use it with GeoPandas or something else (epsg=4326)
pois_data_found = pois_object.data
```

### Get Roads

Find the vehicle or pedestrian network (LineString(s)) from a location or a bounding box:
* OSM attributes available
* OSM features ready to be used with shapely, GeoPandas (...):
* data cleaned regarding classical topology rules

```python
from osmrx.main.roads import Roads

# Choose the vehicle or the pedestrian network
roads_object = Roads("vehicle")

# from_location(location: str) is available
roads_object.from_bbox({6.019674, 4.023742, 46.072575, 4.122018})

# It returns a list of dictionnaries [{"geometry": Point(...), "attribute": "...", ...}
# Free for you to use it with GeoPandas or something else (epsg=4326)
roads_data_found = roads_object.data

# return the rustworkx graph (directed for vehicle / undirected for pedestrian)
graph = roads_object.graph
# Free for you to compute graph analysis
```


### Compute a shortest path

Compute the shortest path from an ordered list of Point(s) (at least 2)

```python
from shapely import Point

from osmrx.main.roads import GraphAnalysis

# use the GraphAnalysis class and set:
# the network type (pedestrian or vehicle) and an ordered list of 2 Shapely Points defining the source and the target
# of your shortest path)
analysis_object = GraphAnalysis("pedestrian",
                              [Point(4.0793058, 46.0350304), Point(4.0725246, 46.0397676)])  # (epsg=4326)
paths_built = analysis_object.get_shortest_path()
for path_object in paths_built:
    print(path_object.path)  # LineString shortest path (epsg=4326)
    print(path_object.features())  # List of LineString (with osm attributes) composing the path found
```


### Compute an Isochrone

Build an isochrone (Polygon(s)) from a Point

```python
from shapely import Point

from osmrx.main.roads import GraphAnalysis

# use the GraphAnalysis class and set:
# the network type (pedestrian or vehicle) and a list of one Shapely Point (epsg=4326) to build the isochone
analysis_object = GraphAnalysis("vehicle", [Point(4.0793058, 46.0350304)])

# Set the distance intervals to compute the isochone with a list of integer or float
isochrones_built = analysis_object.isochrones_from_distance([0, 250, 500, 1000, 1500])

# List of Polygons with a distance attributes based on the intervals defined
print(isochrones_built.data)
```

