from typing import Dict

from osmrx.apis_handler.core import ApiCore


class ErrorOverpassApi(ValueError):
    pass


class OverpassApi(ApiCore):

    __OVERPASS_URL: str = "https://www.overpass-api.de/api/interpreter"
    __OVERPASS_QUERY_PREFIX: str = "[out:json];"

    def _build_parameters(self, query: str) -> Dict:
        return {
            "data": f"{self.__OVERPASS_QUERY_PREFIX}{query}"
        }

    def query(self, query: str) -> Dict:
        parameters = self._build_parameters(query)
        return self.request_query(self.__OVERPASS_URL, parameters, {})
