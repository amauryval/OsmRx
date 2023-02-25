from typing import Dict


class ErrorOverpassApi(ValueError):
    pass


class OverpassApi:

    __OVERPASS_URL: str = "https://www.overpass-api.de/api/interpreter"
    __OVERPASS_QUERY_PREFIX: str = "[out:json];"
    # __OVERPASS_QUERY_SUFFIX = ";(._;>;);out geom;"
    __OVERPASS_QUERY_SUFFIX: str = ""

    def __init__(self, logger):
        super().__init__()
        self.logger = logger

    def _build_parameters(self, query: str) -> Dict:
        return {
            "data": f"{self.__OVERPASS_QUERY_PREFIX}{query}{self.__OVERPASS_QUERY_SUFFIX}"
        }

    def query(self, query: str) -> Dict:
        parameters = self._build_parameters(query)

        session = sessions.FuturesSession(max_workers=self.__NB_WORKER)
        response = session.get(self.__OVERPASS_URL, params=parameters)

        self.check_request_response(response)
        return response.result().json()
