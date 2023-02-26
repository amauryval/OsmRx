from typing import Dict, List

from shapely import Point, LineString

from osm_network.globals.osm import osm_url
from osm_network.globals.queries import OsmFeatureTypes

# constants
GEOMETRY_FIELD: str = "geometry"
LAT_FIELD: str = "lat"
LNG_FIELD: str = "lon"
TOPO_FIELD: str = "topo_uuid"
FEATURE_TYPE_OSM_FIELD: str = "type"
PROPERTIES_OSM_FIELD: str = "tags"
ID_OSM_FIELD: str = "id"
OSM_URL_FIELD: str = "osm_url"
ID_DEFAULT_FIELD: str = "id"


class OverpassDataConverter:
    _grouped_features = None
    _point_features = None
    _line_features = None

    def __init__(self, overpass_data: List[Dict]) -> None:

        self._prepare_data(overpass_data)

    def _prepare_data(self, raw_data: List[Dict]):
        self._grouped_features = {
            "points": filter(
                lambda x: x[FEATURE_TYPE_OSM_FIELD] == OsmFeatureTypes.node.value,
                raw_data,
            ),
            "lines": filter(
                lambda x: x[FEATURE_TYPE_OSM_FIELD] == OsmFeatureTypes.way.value,
                raw_data,
            )
        }

    def point_features(self) -> List[Dict]:
        point_features = []
        data = self._grouped_features["points"]
        for uuid_enum, feature in enumerate(data, start=1):
            geometry = Point(feature[LNG_FIELD], feature[LAT_FIELD])
            point_features.append(self._build_properties(uuid_enum, geometry, feature))
        return point_features

    def line_features(self) -> List[Dict]:
        line_features = []
        data = self._grouped_features["lines"]
        for uuid_enum, feature in enumerate(data, start=1):
            geometry = LineString(
                [(coords[LNG_FIELD], coords[LAT_FIELD]) for coords in feature[GEOMETRY_FIELD]]
            )
            line_features.append(self._build_properties(uuid_enum, geometry, feature))
        return line_features

    @staticmethod
    def _build_properties(uuid_enum: int, geometry: Point | LineString, properties: Dict) -> Dict:
        properties_found = properties.get(PROPERTIES_OSM_FIELD, {})
        properties_found[ID_OSM_FIELD] = str(properties[ID_OSM_FIELD])
        properties_found[OSM_URL_FIELD] = f"{osm_url}/{properties[FEATURE_TYPE_OSM_FIELD]}/" \
                                          f"{properties_found[ID_OSM_FIELD]}"

        # used for topology
        properties_found[TOPO_FIELD] = uuid_enum  # do not cast to str, because topology processing need an int
        properties_found[GEOMETRY_FIELD] = geometry

        return properties_found
