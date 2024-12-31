from typing import Dict, List
from typing import Set
from typing import TYPE_CHECKING

from osmrx.apis_handler.core import ApiCore

if TYPE_CHECKING:
    from logging import Logger


class ErrorNominatimApi(ValueError):
    pass


class NominatimApi(ApiCore):

    nominatim_url = "https://nominatim.openstreetmap.org/search.php?"
    query_parameter = "q"
    other_query_parameter: Set[str] = {
        "street",
        "city",
        "county",
        "state",
        "country",
        "postalcode",
    }
    format_parameter: Dict = {"format": "jsonv2", "polygon": "1", "polygon_geojson": "1"}
    headers: Dict = {'User-Agent': 'Mozilla/5.0'}

    def __init__(self, logger: "Logger", **params) -> None:
        _values = None
        super().__init__(logger=logger)

        parameters: Dict = self.__check_parameters(params)
        self.items = self.request_query(self.nominatim_url, parameters, headers=self.headers)

    def __check_parameters(self, input_parameters: Dict) -> Dict:

        if self.query_parameter in input_parameters:
            # clean arguments set
            for param_key in self.other_query_parameter:
                try:
                    del input_parameters[param_key]
                except KeyError:
                    pass

        elif not any(
            [
                input_key in self.other_query_parameter
                for input_key in input_parameters.keys()
            ]
        ):
            raise ErrorNominatimApi(
                f"{', '.join(self.other_query_parameter)} not found!"
            )

        input_parameters.update(self.format_parameter)

        return input_parameters

    @property
    def items(self) -> List[Dict]:
        return self._values

    @items.setter
    def items(self, data_found: List[Dict]) -> None:
        self._values = data_found

