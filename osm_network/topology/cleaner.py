from typing import Tuple
from typing import List
from typing import Dict
from typing import Optional
from typing import Set
from typing import Union
from typing import Iterator

from scipy import spatial

from shapely.geometry import LineString

import rtree

import numpy as np

from collections import Counter

from more_itertools import split_at

import concurrent.futures

from osm_network import Logger
from osm_network.globals.osm import forward_tag, backward_tag
from osm_network.globals.queries import OsmFeatures


class NetworkTopologyError(Exception):
    pass


class TopologyStats:
    _added = None
    _split = None

    def __init__(self):
        self.reset()

    def __repr__(self):
        return f"added: {self.added} ; split: {self.split}"

    def reset(self):
        self._added = 0
        self._split = 0

    @property
    def added(self):
        return self._added

    @added.setter
    def added(self, count):
        self._added += count

    @property
    def split(self):
        return self._split

    @split.setter
    def split(self, count):
        self._split += count


class TopologyCore:
    logger = None
    _uuid_field = None

    _network_data = None
    _additional_nodes = None
    _intersections = None
    _network_data_extended = None

    _GEOMETRY_FIELD: str = "geometry"
    _COORDINATES_FIELD: str = "coordinates"
    _CLEANING_FIELD_STATUS: str = "topology"
    _TOPOLOGY_TAG_SPLIT: str = "split"
    _TOPOLOGY_TAG_ADDED: str = "added"
    _TOPOLOGY_TAG_UNCHANGED: str = "unchanged"

    def __init__(self, logger: Logger, uuid_field: str):
        self.logger = logger
        self._uuid_field = uuid_field  # values must be an integer.. thank rtree...

    @property
    def network_data(self) -> Dict[str, Dict]:
        return self._network_data

    @network_data.setter
    def network_data(self, features: List[Dict]):
        self._network_data = {
            feature[self._uuid_field]: {
                **{self._COORDINATES_FIELD: feature[self._GEOMETRY_FIELD].coords[:]},
                **feature,
                **{self._CLEANING_FIELD_STATUS: self._TOPOLOGY_TAG_UNCHANGED},
            }
            for feature in features
        }

    @property
    def additional_nodes(self) -> Dict[str, Dict]:
        return self._additional_nodes

    @additional_nodes.setter
    def additional_nodes(self, features: List[Dict] | None):
        if features is not None:
            self._additional_nodes = {
                feature[self._uuid_field]: {
                    **{self._COORDINATES_FIELD: feature[self._GEOMETRY_FIELD].coords[0]},
                    **feature,
                }
                for feature in features
            }
        else:
            self._additional_nodes: Dict = {}

    @property
    def intersections(self) -> Set[Tuple[float, float]]:
        return self._intersections

    @intersections.setter
    def intersections(self, items):
        self._intersections = items
        self.logger.info("Intersections found")

    @property
    def network_data_extended(self) -> Dict[str, Dict]:
        return self._network_data_extended


class TopologyCleaner(TopologyCore):
    _post_proc_mode = None
    _output_line_improved = None
    _additional_nodes = None
    _original_field_id = None

    __INTERPOLATION_LEVEL: int = 7
    __INTERPOLATION_LINE_LEVEL: int = 4
    __NB_OF_NEAREST_LINE_ELEMENTS_TO_FIND: int = 10

    __NUMBER_OF_NODES_INTERSECTIONS: int = 2
    __ITEM_LIST_SEPARATOR_TO_SPLIT_LINE: str = "_"

    # OSM fields
    __ONEWAY_FIELD: str = "oneway"
    __ONEWAY_VALUE: str = "yes"
    __JUNCTION_FIELD: str = "junction"
    __JUNCTION_VALUES: List[str] = ["roundabout", "jughandle"]

    __INSERT_OPTIONS: Dict = {"after": 1, "before": -1, None: 0}

    _topology_stats = None

    def __init__(
        self,
        logger,
        network_data: List[Dict],
        additional_nodes: Optional[List[Dict]],
        uuid_field: str,
        original_field_id: str,
        post_proc_mode: OsmFeatures,
        output_line_improved: bool = False,
    ) -> None:
        super().__init__(logger=logger, uuid_field=uuid_field)

        self._topology_stats = TopologyStats()

        self._post_proc_mode = post_proc_mode
        self._output_line_improved = output_line_improved  # link to __INTERPOLATION_LINE_LEVEL
        self._original_field_id = original_field_id

        self.network_data = network_data
        self.additional_nodes = additional_nodes

        self.logger.info("Network cleaning...")

        self._connections_added: Dict = {}
        self._output: List[Dict] = []

    def run(self) -> List[Dict]:

        # connect all the added nodes
        self.extend_network()

        # find all the existing intersection from coordinates
        self.find_intersections_from_ways()

        self.logger.info("Build lines")
        for feature in self.network_data_extended.values():
            self.build_lines(feature)

        return self._output

    def build_lines(self, feature: Dict) -> None:
        # compare line coords and intersections points
        coordinates_list = set(feature[self._COORDINATES_FIELD])
        points_intersections: Set[Tuple[float, float]] = coordinates_list.intersection(self.intersections)

        # rebuild linestring
        if len(set(feature[self._COORDINATES_FIELD])) > 1:
            lines_coordinates_rebuild = self._topology_builder(
                feature[self._COORDINATES_FIELD], points_intersections
            )

            if len(lines_coordinates_rebuild) > 1:

                for new_suffix_id, line_coordinates in enumerate(
                    lines_coordinates_rebuild
                ):
                    feature_updated = dict(feature)
                    feature_updated[
                        self._uuid_field
                    ] = f"{feature_updated[self._uuid_field]}_{new_suffix_id}"
                    feature_updated[
                        self._CLEANING_FIELD_STATUS
                    ] = self._TOPOLOGY_TAG_SPLIT
                    feature_updated[self._COORDINATES_FIELD] = line_coordinates

                    new_features = self.mode_processing(feature_updated)
                    self._output.extend(new_features)
            else:
                # nothing to change
                feature[self._uuid_field] = feature[self._uuid_field]
                new_features = self.mode_processing(feature)
                self._output.extend(new_features)

    def mode_processing(self, input_feature):
        new_elements = []

        if self._post_proc_mode == OsmFeatures.vehicle:
            # by default
            new_forward_feature = self._direction_processing(input_feature, forward_tag)
            new_elements.extend(new_forward_feature)
            if input_feature.get(self.__JUNCTION_FIELD, None) in self.__JUNCTION_VALUES:
                return new_elements

            if input_feature.get(self.__ONEWAY_FIELD, None) != self.__ONEWAY_VALUE:

                new_backward_feature = self._direction_processing(
                    input_feature, backward_tag
                )
                new_elements.extend(new_backward_feature)

        elif self._post_proc_mode == OsmFeatures.pedestrian:
            # it's the default behavior

            feature = self._direction_processing(input_feature)
            new_elements.extend(feature)

        return new_elements

    def _direction_processing(
        self, input_feature: Dict, direction: Optional[str] = None
    ):
        new_features = []
        input_feature_copy = dict(input_feature)

        if self._output_line_improved:
            new_coords = list(
                self._split_line(input_feature_copy, self.__INTERPOLATION_LINE_LEVEL)
            )
            new_lines_coords = list(zip(new_coords, new_coords[1:]))
            del input_feature_copy[self._COORDINATES_FIELD]

            for idx, sub_line_coords in enumerate(new_lines_coords):
                new_features.append(
                    self.__proceed_direction_geom(
                        direction, input_feature_copy, sub_line_coords, idx
                    )
                )
        else:
            new_coords = list(self._split_line(input_feature_copy, 1))
            del input_feature_copy[self._COORDINATES_FIELD]
            new_features.append(
                self.__proceed_direction_geom(direction, input_feature_copy, new_coords)
            )

        return new_features

    def __proceed_direction_geom(
        self, direction, input_feature, sub_line_coords, idx=None
    ):
        feature = dict(input_feature)

        if idx is not None:
            idx = f"_{idx}"
        else:
            idx = ""

        if direction == "backward":
            new_linestring = LineString(sub_line_coords[::-1])
        elif direction in ["forward", None]:
            new_linestring = LineString(sub_line_coords)
        else:
            raise NetworkTopologyError(f"Direction issue: value '{direction}' found")
        feature[self._GEOMETRY_FIELD] = new_linestring

        if direction is not None:
            feature[self._uuid_field] = f"{feature[self._uuid_field]}{idx}_{direction}"
        else:
            feature[self._uuid_field] = f"{feature[self._uuid_field]}{idx}"

        return feature

    def _split_line(self, feature: Dict, interpolation_level: int) -> List:
        new_line_coords = interpolate_curve_based_on_original_points(
            np.array(feature[self._COORDINATES_FIELD]), interpolation_level,
        )
        return new_line_coords

    def extend_network(self):
        if len(self.additional_nodes) > 0:

            self.logger.info("Starting: Adding new nodes on the network")

            self.logger.info("Find nearest line for each node")
            node_keys_by_nearest_lines_filled = (
                self.__find_nearest_line_for_each_key_nodes()
            )

            self.logger.info("Split line")
            # for nearest_line_key in node_keys_by_nearest_lines_filled:
            #     self.split_line(nearest_line_key)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(self.split_line, node_keys_by_nearest_lines_filled)

            self._network_data_extended = {**self.network_data, **self._connections_added}

            self.logger.info(
                f"Topology lines checker: {self._topology_stats}"
            )
        else:
            self._network_data_extended = self.network_data

    def compute_added_node_connections(self) -> Dict:
        self.logger.info("Starting: Adding new nodes on the network")

        self.logger.info("Find nearest line for each node")
        node_keys_by_nearest_lines_filled = (
            self.__find_nearest_line_for_each_key_nodes()
        )

        self.logger.info("Split line")
        # for nearest_line_key in node_keys_by_nearest_lines_filled:
        #     self.split_line(nearest_line_key)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.split_line, node_keys_by_nearest_lines_filled)

        network_data: Dict = {**self.network_data, **self._connections_added}

        self.logger.info(
            f"Topology lines checker: {self._topology_stats}"
        )

        return network_data

    def split_line(self, node_key_by_nearest_lines):
        nearest_line_content = self.__node_by_nearest_lines[node_key_by_nearest_lines]
        default_line_updater = self.proceed_nodes_on_network(
            (node_key_by_nearest_lines, nearest_line_content)
        )
        if default_line_updater is not None:
            self.insert_new_nodes_on_its_line(default_line_updater)

    def insert_new_nodes_on_its_line(self, item):
        original_line_key = item["original_line_key"]
        end_points_found = item["end_points_found"]

        linestring_with_new_nodes = self.network_data[original_line_key][
            self._COORDINATES_FIELD
        ]
        linestring_with_new_nodes.extend(end_points_found)
        linestring_with_new_nodes = set(linestring_with_new_nodes)
        self._topology_stats.split = len(linestring_with_new_nodes.intersection(end_points_found))

        # build new LineStrings
        linestring_linked_updated = list(
            filter(lambda x: x in linestring_with_new_nodes, item["interpolated_line"],)
        )

        self.network_data[original_line_key][
            self._COORDINATES_FIELD
        ] = linestring_linked_updated

    def proceed_nodes_on_network(self, nearest_line_content):
        nearest_line_key, node_keys = nearest_line_content

        interpolated_line_coords = interpolate_curve_based_on_original_points(
            np.array(self.network_data[nearest_line_key][self._COORDINATES_FIELD]),
            self.__INTERPOLATION_LEVEL,
        )
        line_tree = spatial.cKDTree(interpolated_line_coords)
        interpolated_line_coords_rebuilt = list(map(tuple, interpolated_line_coords))

        nodes_coords = [
            self.additional_nodes[node_key][self._COORDINATES_FIELD]
            for node_key in node_keys
        ]
        _, nearest_line_object_idxes = line_tree.query(nodes_coords)
        end_points_found = [
            interpolated_line_coords_rebuilt[nearest_line_key]
            for nearest_line_key in nearest_line_object_idxes
        ]

        connections_coords = list(
            zip(node_keys, list(zip(nodes_coords, end_points_found)))
        )
        self._topology_stats.added = len(connections_coords)

        connections_coords_valid = list(
            filter(lambda x: len(set(x[-1])) > 0, connections_coords)
        )
        for node_key, connection in connections_coords_valid:

            # to split line at node (and also if node is on the network). it builds intersection used to split lines
            # additional are converted to lines
            self._connections_added[f"from_node_id_{node_key}"] = {
                self._COORDINATES_FIELD: connection,
                self._GEOMETRY_FIELD: connection,
                self._CLEANING_FIELD_STATUS: self._TOPOLOGY_TAG_ADDED,
                self._uuid_field: f"{self._TOPOLOGY_TAG_ADDED}_{node_key}",
                self._original_field_id: f"{self._TOPOLOGY_TAG_ADDED}_{node_key}",
            }

        return {
            "interpolated_line": interpolated_line_coords_rebuilt,
            "original_line_key": nearest_line_key,
            "end_points_found": end_points_found,
        }

    def _topology_builder(
        self,
        coordinates: List[Tuple[float, float]],
        points_intersections: Set[Tuple[float, float]],
    ):

        is_rebuild = False
        coordinates_updated: List[List[Tuple[float, float]]] = []

        # split coordinates found at intersection to respect the topology
        first_value, *middle_coordinates_values, last_value = coordinates
        for point_intersection in points_intersections:

            point_intersection = tuple(point_intersection)

            if point_intersection in middle_coordinates_values:
                # we get the middle values from coordinates to avoid to catch the first and last value when editing

                middle_coordinates_values = self._insert_value(
                    middle_coordinates_values,
                    point_intersection,
                    tuple([point_intersection]),
                )

                middle_coordinates_values = self._insert_value(
                    middle_coordinates_values,
                    point_intersection,
                    self.__ITEM_LIST_SEPARATOR_TO_SPLIT_LINE,
                    "after",
                )
                coordinates = [first_value] + middle_coordinates_values + [last_value]
                is_rebuild = True

        if is_rebuild:
            coordinates_updated = list(split_at(coordinates, lambda x: x == "_"))

        if not is_rebuild:
            coordinates_updated = list([coordinates])

        return coordinates_updated

    def find_intersections_from_ways(self) -> None:
        self.logger.info("Starting: Find intersections")
        all_coord_points = Counter(
            [
                coords
                for feature in self.network_data_extended.values()
                for coords in feature[self._COORDINATES_FIELD]
            ],
        )

        intersections_found = dict(
            filter(
                lambda x: x[1] > 1,  # intersection/count must be > 1
                all_coord_points.items(),
            )
        ).keys()
        self.intersections = set(intersections_found)

    def __rtree_generator_func(
        self,
    ) -> Iterator[Tuple[int, Tuple[str, str, str, float], None]]:
        for fid, feature in self._network_data.items():
            # fid is an integer
            yield fid, feature[self._GEOMETRY_FIELD].bounds, None

    def __find_nearest_line_for_each_key_nodes(self) -> Iterator[int]:
        # find the nearest network arc to interpolate
        self.__tree_index = rtree.index.Index(self.__rtree_generator_func())

        # find nearest line
        self.__node_by_nearest_lines = dict(
            (key, []) for key in self.network_data.keys()
        )

        # not working because rtree cannot be MultiThreaded
        # with concurrent.futures.ThreadPoolExecutor(4) as executor:
        #     executor.map(self.__get_nearest_line, self._additional_nodes.items())
        for node_info in self._additional_nodes.items():
            self.__get_nearest_line(node_info)

        node_keys_by_nearest_lines_filled = filter(
            lambda x: len(self.__node_by_nearest_lines[x]) > 0,
            self.__node_by_nearest_lines,
        )

        return node_keys_by_nearest_lines_filled

    def __get_nearest_line(self, node_info: Tuple[int, Dict]) -> None:
        node_uuid, node = node_info
        distances_computed: List[Tuple[float, int]] = []
        node_geom = node[self._GEOMETRY_FIELD]

        for index_feature in self.__tree_index.nearest(
            node_geom.bounds, self.__NB_OF_NEAREST_LINE_ELEMENTS_TO_FIND
        ):
            line_geom = self._network_data[index_feature][self._GEOMETRY_FIELD]
            distance_from_node_to_line = node_geom.distance(line_geom)
            if distance_from_node_to_line == 0:
                # means that we node is on the network, looping is not necessary anymore
                distances_computed = [(distance_from_node_to_line, index_feature)]
                break
            distances_computed.append((distance_from_node_to_line, index_feature))

        _, line_min_index = min(distances_computed)
        self.__node_by_nearest_lines[line_min_index].append(node_uuid)

    def _insert_value(
        self,
        list_object: List[Tuple[float, float]],
        search_value: Tuple[float, float],
        value_to_add: Union[str, Tuple[Tuple[float, float]]],
        position: Optional[str] = None,
    ) -> List[Tuple[float, float]]:

        assert position in self.__INSERT_OPTIONS.keys()

        index_increment = self.__INSERT_OPTIONS[position]
        index: int = list_object.index(search_value) + index_increment
        list_object[index:index] = value_to_add

        return list_object


def interpolate_curve_based_on_original_points(x, n):
    # source :
    # https://stackoverflow.com/questions/31243002/higher-order-local-interpolation-of-implicit-curves-in-python/31335255
    if n > 1:
        m = 0.5 * (x[:-1] + x[1:])
        if x.ndim == 2:
            m_size = (x.shape[0] + m.shape[0], x.shape[1])
        else:
            raise NotImplementedError
        x_new = np.empty(m_size, dtype=x.dtype)
        x_new[0::2] = x
        x_new[1::2] = m
        return interpolate_curve_based_on_original_points(x_new, n - 1)

    elif n == 1:
        return x

    else:
        raise ValueError
