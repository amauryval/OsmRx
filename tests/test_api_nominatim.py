import pytest

from osmrx.apis_handler.nominatim import NominatimApi, ErrorNominatimApi
from osmrx.helpers.logger import Logger


def test_find_a_location_by_name():
    output = NominatimApi(Logger().logger, q="roanne", limit=1).items

    assert len(output) == 1
    assert "Roanne" in output[0]["display_name"]


def test_find_a_location_by_name_without_the_expected_args():
    with pytest.raises(ErrorNominatimApi):
        _ = NominatimApi(Logger().logger, query="roanne", limit=1).items
