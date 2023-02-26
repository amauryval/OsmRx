
class Bbox:
    _min_x = None
    _min_y = None
    _max_x = None
    _max_y = None

    def __init__(self, min_x: float, min_y: float, max_x: float, max_y: float) -> None:
        self._min_x = min_x
        self._min_y = min_y
        self._max_x = max_x
        self._max_y = max_y

    def to_str(self) -> str:
        return f"{self._min_x}, {self._min_y}, {self._max_x}, {self._max_y}"


class Location:
    _location_name = None
    def __init__(self, location_name: str) -> None:

        self._location_name = location_name

    @property
    def name(self) -> str:
        return self._location_name
