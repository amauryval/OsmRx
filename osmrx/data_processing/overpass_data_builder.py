from typing import Dict
from typing import List

from shapely import Point
from shapely import LineString

from osmrx.globals.queries import OsmFeatureTypes

ID_OSM_FIELD: str = "id"


class OverpassDataBuilder:
    __GEOMETRY_FIELD: str = "geometry"
    __LAT_FIELD: str = "lat"
    __LNG_FIELD: str = "lon"
    __FEATURE_TYPE_OSM_FIELD: str = "type"
    __PROPERTIES_OSM_FIELD: str = "tags"
    __OSM_URL_FIELD: str = "osm_url"
    __OSM_URL = "https://www.openstreetmap.org"

    _line_features = None

    def __init__(self, overpass_data: List[Dict]) -> None:

        self._prepare_data(overpass_data)

    def _prepare_data(self, raw_data: List[Dict]):
        self._grouped_features = {
            "points": filter(
                lambda x: x[self.__FEATURE_TYPE_OSM_FIELD] == OsmFeatureTypes.node.value,
                raw_data,
            ),
            "lines": filter(
                lambda x: x[self.__FEATURE_TYPE_OSM_FIELD] == OsmFeatureTypes.way.value,
                raw_data,
            )
        }

    def point_features(self) -> List[Dict]:
        point_features = []
        data = self._grouped_features["points"]
        for uuid_enum, feature in enumerate(data, start=1):
            geometry = Point(feature[self.__LNG_FIELD], feature[self.__LAT_FIELD])
            point_features.append(self._build_properties(uuid_enum, geometry, feature))
        return point_features

    def line_features(self) -> List[Dict]:
        line_features = []
        data = self._grouped_features["lines"]
        for uuid_enum, feature in enumerate(data, start=1):
            geometry = LineString(
                [(coordinates[self.__LNG_FIELD], coordinates[self.__LAT_FIELD])
                 for coordinates in feature[self.__GEOMETRY_FIELD]]
            )
            line_features.append(self._build_properties(uuid_enum, geometry, feature))
        return line_features

    def _build_properties(self, uuid_enum: int, geometry: Point | LineString, properties: Dict) -> Dict:
        tags_attributes = properties.get(self.__PROPERTIES_OSM_FIELD, {})
        return {
            **tags_attributes,
            ID_OSM_FIELD: str(properties[ID_OSM_FIELD]),
            self.__OSM_URL_FIELD: f"{self.__OSM_URL}/{properties[self.__FEATURE_TYPE_OSM_FIELD]}/"
                                  f"{properties[ID_OSM_FIELD]}",
            # TOPO_FIELD: uuid_enum,  # do not cast to str, because topology processing need an int
            self.__GEOMETRY_FIELD: geometry
        }
