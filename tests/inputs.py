from typing import Tuple, List, Dict

import pytest
from shapely import Point
from shapely import LineString


@pytest.fixture()
def bbox_values() -> Tuple[float, float, float, float]:
    return 4.0237426757812, 46.019674567761, 4.1220188140869, 46.072575637028


@pytest.fixture()
def location_name() -> str:
    return "roanne"


@pytest.fixture
def some_line_features() -> List[Dict]:
    return [
        {
            "geometry": LineString(
                [
                    (4.07114907206290066, 46.03760345278882937),
                    (4.07091681769133018, 46.03699538217645681),
                    (4.07079583285433966, 46.03660928470699787),
                ]
            ),
            "uuid": 10, "id": "10",
        },
        {
            "geometry": LineString(
                [
                    (4.07079583285433966, 46.03660928470699787),
                    (4.07085925751677191, 46.03660294861677471),
                    (4.07086909165722677, 46.03667793393773877),
                    (4.07093731600662867, 46.03674923145603515),
                    (4.0710313549747239, 46.03670313392265712),
                    (4.07098587207512264, 46.03662323153146474),
                ]
            ),
            "uuid": 11, "id": "11",
        },
        {
            "geometry": LineString(
                [
                    (4.07132541293213457, 46.03636692445581957),
                    (4.07195460627399886, 46.0366250550576126),
                    (4.07215358194621313, 46.03668152112675216),
                    (4.0724305345710512, 46.03630508066581228),
                ]
            ),
            "uuid": 12, "id": "12", "oneway": "yes",
        },
    ]


@pytest.fixture
def some_point_features() -> List[Dict]:
    return [
        {
            "geometry": Point((4.07083953255024333, 46.03693156996429536)),
            "uuid": 1, "id": "1",
        },  # outside
        {
            "geometry": Point((4.07089961963211167, 46.03664388029959298)),
            "uuid": 2, "id": "2",
        },  # outside
        {
            "geometry": Point((4.07097056291628423, 46.03710105075762726)),
            "uuid": 3, "id": "3",
        },  # outside
        {
            "geometry": Point((4.07114907206290066, 46.03760345278882937)),
            "uuid": 4, "id": "4",
        },  # at the line start node
        {
            "geometry": Point((4.07091681769133018, 46.03699538217645681)),
            "uuid": 5, "id": "5",
        },  # at one linestring node
        {
            "geometry": Point((4.070811393410536, 46.036724772414075)),
            "uuid": 6, "id": "6",
        },
        {
            "geometry": Point((4.07088624242873376, 46.03680095802188532)),
            "uuid": 7, "id": "7",
        },
        {
            "geometry": Point((4.07103594046512729, 46.03720327149468972)),
            "uuid": 8, "id": "8",
        },
        {
            "geometry": Point((4.07101188185213569, 46.0373516329414727)),
            "uuid": 9, "id": "9",
        },
    ]
