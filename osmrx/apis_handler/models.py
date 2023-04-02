from typing import List
from typing import TYPE_CHECKING
from dataclasses import dataclass

from shapely import Point
from shapely import Polygon
from shapely.geometry import shape

from osmrx.apis_handler.nominatim import NominatimApi

if TYPE_CHECKING:
    from osmrx.helpers.logger import Logger


class Bbox:
    """To manage bbox item"""

    _min_x = None
    _min_y = None
    _max_x = None
    _max_y = None

    def __init__(self, min_x: float, min_y: float, max_x: float, max_y: float) -> None:
        self._min_x = min_x
        self._min_y = min_y
        self._max_x = max_x
        self._max_y = max_y

    @property
    def location_name(self) -> str:
        """Cast to a string"""
        return f"{self._min_x}, {self._min_y}, {self._max_x}, {self._max_y}"


@dataclass
class NominatimItem:
    place_id: int
    licence: str
    _osm_id: int
    bounds: Bbox
    position: Point
    display_name: str
    polygon: Polygon

    @property
    def osm_id(self):
        """Build the osm_id by adding a fixed number: this is it!"""
        return self._osm_id + 3600000000


class Location:
    """To manage location name and attributes from Nominatim"""
    _location_name = None
    _values = None
    _limit = None

    def __init__(self, location_name: str, logger: "Logger", limit: int = 1) -> None:
        self.logger = logger
        self.location_name = location_name
        self._limit = limit

    @property
    def location_name(self) -> str:
        """return the location_name initialized"""
        return self._location_name

    @location_name.setter
    def location_name(self, location_name: str) -> None:
        """location_name setter"""
        self._location_name = location_name
        self.values = location_name

    @property
    def values(self) -> List[NominatimItem]:
        return self._values

    @values.setter
    def values(self, location_name: str) -> None:
        """return the nominatim data found"""
        self._values = []
        data_found = NominatimApi(self.logger, q=location_name, limit=self._limit).items
        for item in data_found:
            self._values.append(
                NominatimItem(
                    place_id=item["place_id"],
                    licence=item["licence"],
                    _osm_id=item["osm_id"],
                    bounds=Bbox(*item["boundingbox"]),
                    position=Point(item["lon"], item["lat"]),
                    display_name=item["display_name"],
                    polygon=shape(item["geojson"]),
                )
            )
