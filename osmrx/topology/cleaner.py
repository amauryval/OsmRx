import itertools
from typing import Tuple, Generator, Any
from typing import List
from typing import Dict
from typing import Optional
from typing import Set
from typing import Union
from typing import Iterator

from numpy import ndarray
from scipy import spatial

from shapely.geometry import LineString

import rtree

import numpy as np

from collections import Counter

from more_itertools import split_at

import concurrent.futures

from osmrx.network.arc_feature import ArcFeature


class NetworkTopologyError(Exception):
    pass


class LineBuilder:
    __TOPOLOGY_TAG_SPLIT: str = "split"

    __CLEANING_FILED_STATUS: str = "topology"

    __LINESTRING_SEPARATOR: str = "_"

    def __init__(self, feature: Dict, intersection_nodes: set[tuple[float, float]],
                 interpolate_level: int | None = None):
        self._feature = feature
        del self._feature["geometry"]
        self._coordinates = self._feature.pop("coordinates")
        self._unique_coordinates = set(self._coordinates)
        self._intersection_nodes = intersection_nodes
        self._interpolate_level = interpolate_level

        self._output = []

    def build_features(self) -> List[ArcFeature]:
        if not self.is_line_valid():
            return []

        geometry_lines = self.split_line_at_intersections(
            self._coordinates, self.intersections_points()
        )
        if len(geometry_lines) > 1:
            self._feature[self.__CLEANING_FILED_STATUS] = self.__TOPOLOGY_TAG_SPLIT

            data = []
            for suffix_id, line_coordinates in enumerate(geometry_lines):
                feature_copy = self.feature_copy()
                feature_copy["topo_uuid"] = f"{feature_copy['topo_uuid']}_{suffix_id}"
                data.append([feature_copy, line_coordinates])

                # feature_updated[self.__COORDINATES_FIELD] = line_coordinates
                self._direction_processing(feature_copy, line_coordinates)
            # with concurrent.futures.ThreadPoolExecutor() as executor:
            #     executor.map(lambda f: self._direction_processing(*f), data)
        else:
            self._direction_processing(self._feature, geometry_lines[0])

        return self._output

    def _direction_processing(self, input_feature: Dict, new_coordinates: list[tuple[float, float]]):

        if self._interpolate_level:
            new_coords = list(
                self._split_line(new_coordinates, self._interpolate_level)
            )
            new_lines_coords = list(zip(new_coords, new_coords[1:]))

            for idx, sub_line_coords in enumerate(new_lines_coords):
                feature_copy = dict(input_feature)
                self.__proceed_direction_geom(feature_copy, sub_line_coords, idx)

        else:
            self.__proceed_direction_geom(input_feature, new_coordinates, None)

    def __proceed_direction_geom(self, input_feature, sub_line_coords, idx: int | None):
        # TODO maybe useless: check parent method

        position = ""
        if idx:
            position = f"_{idx}"

        new_feature = ArcFeature(LineString(sub_line_coords))
        new_feature.topo_uuid = f"{input_feature.pop('topo_uuid')}{position}"
        new_feature.topo_status = input_feature.pop(self.__CLEANING_FILED_STATUS)
        new_feature.attributes = input_feature

        self._output.append(new_feature)

    @staticmethod
    def _split_line(coordinates: list[tuple[float, float]], interpolation_level: int) -> ndarray:
        return interpolate_curve_based_on_original_points(
            np.array(coordinates), interpolation_level,
        )

    def feature_copy(self) -> Dict:
        return dict(self._feature)

    def intersections_points(self) -> Set[Tuple[float, float]]:
        """Return intersections points matching with the feature"""
        return self._unique_coordinates.intersection(self._intersection_nodes)

    def is_line_valid(self) -> True:
        # meaning that there is none point or line length is equals to 0
        return not len(self._unique_coordinates) <= 1

    def split_line_at_intersections(self, coordinates: List[Tuple[float, float]],
                                    points_intersections: Set[Tuple[float, float]]) -> List[List[Tuple[float, float]]]:

        if len(points_intersections) > 0:

            # split coordinates found at intersection to respect the topology
            first_value, *middle_coordinates_values, last_value = coordinates
            for point_intersection in points_intersections:

                if point_intersection in middle_coordinates_values:
                    # we get the middle values from coordinates to avoid to catch the first and last value when editing

                    # duplicate the intersection point
                    index: int = middle_coordinates_values.index(point_intersection)
                    middle_coordinates_values[index:index] = [point_intersection]
                    # add an _ to split the line at the intersection point index
                    middle_coordinates_values[index + 1:index + 1] = self.__LINESTRING_SEPARATOR

            coordinates = [first_value] + middle_coordinates_values + [last_value]
            coordinates_updated = list(split_at(coordinates, lambda x: x == self.__LINESTRING_SEPARATOR))
        else:
            coordinates_updated = list([coordinates])

        return coordinates_updated


class TopologyCleaner:
    __FIELD_ID: str = "topo_uuid"  # values linked must be integer.. due to rtree...

    # if increased, the node connections will be better, but will generate more feature
    __INTERPOLATION_LEVEL: int = 7
    __NB_OF_NEAREST_LINE_ELEMENTS_TO_FIND: int = 10

    __NUMBER_OF_NODES_INTERSECTIONS: int = 2

    __CLEANING_FILED_STATUS: str = "topology"
    __GEOMETRY_FIELD: str = "geometry"
    __COORDINATES_FIELD: str = "coordinates"

    __TOPOLOGY_TAG_ADDED: str = "added"
    __TOPOLOGY_TAG_UNCHANGED: str = "unchanged"

    def __init__(
        self,
        logger,  # TODO: add a logger if not set
        network_data: List[Dict],
        additional_nodes: Optional[List[Dict]],
        interpolation_line_level: int | None = None,  # 4 is a good value
    ) -> None:

        self.logger = logger
        self.logger.info("Network cleaning...")

        self._network_data: Union[List[Dict], Dict] = network_data
        self._interpolation_line_level = interpolation_line_level  # link to __INTERPOLATION_LINE_LEVEL

        self._additional_nodes = additional_nodes
        if self._additional_nodes is None:
            self._additional_nodes: Dict = {}

        self._intersections_found: Optional[Set[Tuple[float, float]]] = None
        self.__connections_added: Dict = {}

    def build_arc_features(self) -> Generator[ArcFeature, Any, None]:
        self._prepare_data()

        # connect all the added nodes
        if len(self._additional_nodes) > 0:
            self.compute_added_node_connections()

        # find all the existing intersection from coordinates
        intersections_found = self.find_intersections_from_ways()

        self.logger.info("Build lines")

        for feature in self._network_data.values():
            for feature_built in LineBuilder(feature, intersections_found,
                                             self._interpolation_line_level).build_features():
                yield feature_built

    def _prepare_data(self):

        self._network_data = {
            idx: {  # idx: topology processing need an int
                self.__COORDINATES_FIELD: feature[self.__GEOMETRY_FIELD].coords[:],
                self.__CLEANING_FILED_STATUS: self.__TOPOLOGY_TAG_UNCHANGED,
                self.__FIELD_ID: idx,
                **feature,
            }
            for idx, feature in enumerate(self._network_data, start=1)
        }
        self._additional_nodes = {
            idx: {  # idx: topology processing need an int
                self.__COORDINATES_FIELD: feature[self.__GEOMETRY_FIELD].coords[0],
                self.__FIELD_ID: idx,
                **feature,
            }
            for idx, feature in enumerate(self._additional_nodes, start=1)
        }

    def compute_added_node_connections(self):
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

        self._network_data: Dict = self._network_data | self.__connections_added

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

        linestring_with_new_nodes = self._network_data[original_line_key][self.__COORDINATES_FIELD]
        linestring_with_new_nodes.extend(end_points_found)
        linestring_with_new_nodes = set(linestring_with_new_nodes)

        # build new LineStrings
        linestring_linked_updated = list(filter(lambda x: x in linestring_with_new_nodes, item["interpolated_line"]))

        self._network_data[original_line_key][self.__COORDINATES_FIELD] = linestring_linked_updated

    def proceed_nodes_on_network(self, nearest_line_content):
        nearest_line_key, node_keys = nearest_line_content

        interpolated_line_coords = interpolate_curve_based_on_original_points(
            np.array(self._network_data[nearest_line_key][self.__COORDINATES_FIELD]),
            self.__INTERPOLATION_LEVEL,
        )
        line_tree = spatial.cKDTree(interpolated_line_coords)
        interpolated_line_coords_rebuilt = list(map(tuple, interpolated_line_coords))

        nodes_coords = [
            self._additional_nodes[node_key][self.__COORDINATES_FIELD]
            for node_key in node_keys
        ]
        _, nearest_line_object_idxes = line_tree.query(nodes_coords)
        end_points_found = [
            interpolated_line_coords_rebuilt[nearest_line_key]
            for nearest_line_key in nearest_line_object_idxes
        ]

        connections_coords = zip(node_keys, list(zip(nodes_coords, end_points_found)))
        connections_coords_valid = filter(lambda x: len(set(x[-1])) > 0, connections_coords)
        for node_key, connection in connections_coords_valid:

            # to split line at node (and also if node is on the network). it builds intersection used to split lines
            # additional are converted to lines
            self.__connections_added[f"from_node_id_{node_key}"] = {
                self.__COORDINATES_FIELD: connection,
                self.__GEOMETRY_FIELD: connection,
                self.__CLEANING_FILED_STATUS: self.__TOPOLOGY_TAG_ADDED,
                self.__FIELD_ID: f"{self.__TOPOLOGY_TAG_ADDED}_{node_key}",
            }

        return {
            "interpolated_line": interpolated_line_coords_rebuilt,
            "original_line_key": nearest_line_key,
            "end_points_found": end_points_found,
        }

    def find_intersections_from_ways(self) -> Set[Tuple[float, float]]:
        self.logger.info("Starting: Find intersections")
        all_coord_points = Counter(
            itertools.chain.from_iterable([
                feature[self.__COORDINATES_FIELD]
                for feature in self._network_data.values()
            ]),
        )

        intersections_found = dict(
            filter(
                lambda x: x[1] >= self.__NUMBER_OF_NODES_INTERSECTIONS,
                all_coord_points.items(),
            )
        ).keys()
        self.logger.info("Done: Find intersections")

        return set(intersections_found)

    def __rtree_generator_func(
        self,
    ) -> Iterator[Tuple[int, Tuple[str, str, str, float], None]]:
        for fid, feature in self._network_data.items():
            # fid is an integer
            yield fid, feature[self.__GEOMETRY_FIELD].bounds, None

    def __find_nearest_line_for_each_key_nodes(self) -> Iterator[int]:
        # find the nearest network arc to interpolate
        self._tree_index = rtree.index.Index(self.__rtree_generator_func())

        # find the nearest line
        self.__node_by_nearest_lines = dict(
            (key, []) for key in self._network_data.keys()
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
        node_geom = node[self.__GEOMETRY_FIELD]

        for index_feature in self._tree_index.nearest(node_geom.bounds, self.__NB_OF_NEAREST_LINE_ELEMENTS_TO_FIND):
            line_geom = self._network_data[index_feature][self.__GEOMETRY_FIELD]
            distance_from_node_to_line = node_geom.distance(line_geom)
            distances_computed.append((distance_from_node_to_line, index_feature))
            if distance_from_node_to_line == 0:
                # means that the node is on the network, looping is not necessary anymore
                break

        _, line_min_index = min(distances_computed)
        self.__node_by_nearest_lines[line_min_index].append(node_uuid)


def interpolate_curve_based_on_original_points(values: np.array, interpolation_factor: int) -> np.ndarray:
    # Convert values to a 2D array (if necessary) and remove single-dimensional entries
    values = np.squeeze(np.atleast_2d(values))

    # Compute the total number of points after interpolation
    n_interpolated_points = len(values) * interpolation_factor

    # Create an array with indices of the original points
    original_indices = np.arange(0, n_interpolated_points, interpolation_factor)

    # Create an array with indices of the new points
    new_indices = np.arange(n_interpolated_points - 1)

    # Compute the interpolated x and y coordinates
    x_interpolated = np.interp(new_indices, original_indices, values[:, 0])
    y_interpolated = np.interp(new_indices, original_indices, values[:, 1])

    # Combine the x and y coordinates into a single array and return it
    interpolated_values = np.column_stack((x_interpolated, y_interpolated))
    return interpolated_values
