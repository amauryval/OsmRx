from typing import Tuple

import pytest


@pytest.fixture()
def bbox_values() -> Tuple[float, float, float, float]:
    return 4.0237426757812, 46.019674567761, 4.1220188140869, 46.072575637028


@pytest.fixture()
def location_name() -> str:
    return "roanne"
