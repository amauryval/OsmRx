from typing import Tuple, TypedDict

from pydantic.dataclasses import dataclass


@dataclass
class GeoFilterTypes:
    pass


@dataclass
class Bbox(GeoFilterTypes):
    value: Tuple[float, float, float, float]

    def to_str(self):
        return ", ".join(map(str, self.value))


@dataclass
class Location(GeoFilterTypes):
    value: str
