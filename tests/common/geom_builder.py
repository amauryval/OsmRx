from typing import List

from osm_network.helpers.logger import Logger
from osm_network.topology.arc_feature import ArcFeature
from osm_network.topology.cleaner import TopologyCleaner


def build_network_features(line_features, point_features, interpolation_level: int | None = None
                           ) -> List[ArcFeature]:
    features = TopologyCleaner(
        Logger().logger,
        line_features,
        point_features,
        "topo_uuid",
        "id",
        interpolation_level
    ).run()

    return [feature for feature in features]
