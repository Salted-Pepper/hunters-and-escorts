"""
Receptors track the pheromones for the spread and contain local statistics (e.g. weather conditions) per region
"""
import time

import matplotlib.patches

import constants
import general_maths
from points import Point
from general_maths import calculate_distance

import numpy as np
import matplotlib.pyplot as plt
import math

import os
import logging
import datetime

date = datetime.date.today()
logging.basicConfig(level=logging.DEBUG, filename=os.path.join(os.getcwd(),
                    'logs/pheromone_navy_log_' + str(date) + '.log'),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%H:%M:%S")
logger = logging.getLogger("RECEPTORS")
logger.setLevel(logging.DEBUG)

# Constants only needed for Pheromone Management
PHEROMONE_DEPRECIATION_FACTOR_PER_TIME_DELTA = 0.99
RECEPTOR_RADIUS_MULTIPLIER = 10


class Receptor:
    def __init__(self, x, y, in_polygon=False) -> None:
        self.visible = True
        if in_polygon:
            self.coalition_pheromones = 100
            self.china_pheromones = 100
            self.decay = False
        elif not is_in_area_of_interest(Point(x, y)):
            self.coalition_pheromones = 100
            self.china_pheromones = 100
            self.decay = False
        else:
            self.coalition_pheromones = np.random.uniform(0, 0.1)
            self.china_pheromones = np.random.uniform(0, 0.1)
            self.decay = True

        # Sea State Variables
        self.sea_state = 2  # common start sea-state
        self.last_uniform_value = 0.5  # just to define previous value, expected value of uniform
        self.new_uniform_value = 0.5

        self.location = Point(x, y)
        self.in_polygon = in_polygon

        self.patch = None

    def __str__(self):
        return (f"Receptor at: {self.location} - with alpha: {self.coalition_pheromones}, beta: {self.china_pheromones},"
                f"sea state: {self.sea_state}")

    def initiate_plot(self, axes, cmap):
        if not self.decay:
            return axes

        if not constants.PLOTTING_MODE:
            return axes

        if constants.RECEPTOR_PLOT_PARAMETER == 'None':
            self.visible = False
            return axes

        elif constants.RECEPTOR_PLOT_PARAMETER == "Coalition Pheromones":
            self.patch = matplotlib.patches.Circle((self.location.x, self.location.y),
                                                   radius=0.05, color=cmap(self.coalition_pheromones / 100),
                                                   alpha=0.5, linewidth=None)
        elif constants.RECEPTOR_PLOT_PARAMETER == "China Pheromones":
            self.patch = matplotlib.patches.Circle((self.location.x, self.location.y),
                                                   radius=0.05, color=cmap(self.china_pheromones / 100),
                                                   alpha=0.5, linewidth=None)
        elif constants.RECEPTOR_PLOT_PARAMETER == "Sea States":
            self.patch = matplotlib.patches.Circle((self.location.x, self.location.y),
                                                   radius=0.05, color=cmap(self.sea_state / 6),
                                                   alpha=0.5, linewidth=None)
        axes.add_patch(self.patch)
        return axes

    def update_plot(self, axes, cmap):
        if not constants.PLOTTING_MODE:
            return
        if not self.decay:
            return

        if constants.RECEPTOR_PLOT_PARAMETER == "None":
            if self.visible:
                self.visible = False
                self.patch.set_visible(False)
        else:
            if not self.visible:
                self.visible = True
                self.patch.set_visible(True)

        if constants.RECEPTOR_PLOT_PARAMETER == "coalition_pheromones":
            self.patch.set_facecolor(cmap(self.coalition_pheromones / 100))
            self.patch.set_edgecolor(cmap(self.coalition_pheromones / 100))
        elif constants.RECEPTOR_PLOT_PARAMETER == "china_pheromones":
            self.patch.set_facecolor(cmap(self.china_pheromones / 100))
            self.patch.set_edgecolor(cmap(self.china_pheromones / 100))
        elif constants.RECEPTOR_PLOT_PARAMETER == "sea_states":
            self.patch.set_facecolor(cmap(self.sea_state / 6))
            self.patch.set_edgecolor(cmap(self.sea_state / 6))

        return axes

    def in_range_of_point(self, point: Point, radius: float) -> bool:
        if point.distance_to_point(self.location) <= radius:
            return True
        else:
            return False


class ReceptorGrid:
    def __init__(self, polygons: list, world) -> None:
        self.receptors = []

        self.max_cols = None
        self.max_rows = None

        self.world = world

        self.polygons = polygons

        self.initiate_grid(polygons)

        if constants.RECEPTOR_PLOT_PARAMETER == "pheromones":
            self.cmap = plt.get_cmap("Greens")
        elif constants.RECEPTOR_PLOT_PARAMETER == "sea_states":
            self.cmap = plt.get_cmap("OrRd")
        else:
            self.cmap = plt.get_cmap("Greys")

    def initiate_grid(self, polygons) -> None:
        """
        Creates all receptors in the grid given the settings.
        Initiates the pheromone values (0 for empty, inf for in polygon)
        """
        # Add a frame around the AoI, to ensure UAVs don't just hover the edge
        min_lat = constants.MIN_LAT - constants.LAT_GRID_EXTRA
        max_lat = constants.MAX_LAT + constants.LAT_GRID_EXTRA

        min_lon = constants.MIN_LONG - constants.LONG_GRID_EXTRA
        max_lon = constants.MAX_LONG + constants.LONG_GRID_EXTRA

        num_cols = (max_lon - min_lon) // constants.GRID_WIDTH
        num_rows = (max_lat - min_lat) // constants.GRID_HEIGHT

        self.max_cols = int(np.ceil(num_cols))
        self.max_rows = int(np.ceil(num_rows))

        for row in range(self.max_rows):
            for col in range(self.max_cols):
                x_location = min_lat + row * constants.GRID_HEIGHT
                y_location = min_lon + col * constants.GRID_WIDTH

                in_polygon = general_maths.check_if_point_in_polygons(polygons, Point(x_location, y_location),
                                                                      exclude_edges=False)
                self.receptors.append(Receptor(x=x_location, y=y_location, in_polygon=in_polygon))

        self.set_up_adjacent_connections()

    def set_up_adjacent_connections(self):
        for receptor in self.receptors:
            if is_in_area_of_interest(receptor.location):
                x, y = receptor.location.x, receptor.location.y
                receptor.adjacent_N = self.get_receptor_at_location(Point(x, y + constants.GRID_HEIGHT))
                receptor.adjacent_NE = self.get_receptor_at_location(Point(x + constants.GRID_WIDTH,
                                                                           y + constants.GRID_HEIGHT))
                receptor.adjacent_E = self.get_receptor_at_location(Point(x + constants.GRID_WIDTH,
                                                                          y))
                receptor.adjacent_SE = self.get_receptor_at_location(Point(x + constants.GRID_WIDTH,
                                                                           y - constants.GRID_HEIGHT))
                receptor.adjacent_S = self.get_receptor_at_location(Point(x,
                                                                          y - constants.GRID_HEIGHT))
                receptor.adjacent_SW = self.get_receptor_at_location(Point(x - constants.GRID_WIDTH,
                                                                           y - constants.GRID_HEIGHT))
                receptor.adjacent_W = self.get_receptor_at_location(Point(x - constants.GRID_WIDTH,
                                                                          y))
                receptor.adjacent_NW = self.get_receptor_at_location(Point(x - constants.GRID_WIDTH,
                                                                           y + constants.GRID_HEIGHT))

    def get_receptor_at_location(self, point: Point) -> Receptor | None:
        min_lat = constants.MIN_LAT - constants.LAT_GRID_EXTRA
        max_lat = constants.MAX_LAT + constants.LAT_GRID_EXTRA

        min_lon = constants.MIN_LONG - constants.LONG_GRID_EXTRA
        max_lon = constants.MAX_LONG + constants.LONG_GRID_EXTRA

        if max_lat < point.x or point.x < min_lat or max_lon < point.y or point.y < min_lon:
            return None

        row = int((point.x - min_lat) / constants.GRID_HEIGHT)
        col = int((point.y - min_lon) / constants.GRID_WIDTH)
        index = row * self.max_cols + col

        return self.receptors[index]

    def select_receptors_in_radius(self, point: Point, radius: float) -> list:
        """
        Select all the receptors within a radius of a point.
        Prevents having to cycle through all points by using how the list of receptors was created
        :param point: Point object
        :param radius: Radius around the point
        :return:
        """
        global RECEPTOR_RADIUS_MULTIPLIER

        t_0 = time.perf_counter()
        # Adjust radius to an upperbound of the coordinate transformation
        lon_lat_radius = max(radius / 100, constants.GRID_WIDTH / 2)
        # only check receptors in the rectangle of size radius - select receptors in the list based on
        # how the list is constructed.
        x, y = point.x, point.y
        min_x = x - lon_lat_radius
        max_x = x + lon_lat_radius
        min_y = y - lon_lat_radius
        max_y = y + lon_lat_radius

        # see in which rows and columns this rectangle is:
        min_row = int(max(np.floor((min_x - (constants.MIN_LAT - constants.LAT_GRID_EXTRA))
                                   / constants.GRID_HEIGHT), 0))
        max_row = int(min(np.ceil((max_x - (constants.MIN_LAT - constants.LAT_GRID_EXTRA))
                                  / constants.GRID_HEIGHT), self.max_rows))

        min_col = int(max(np.floor((min_y - (constants.MIN_LONG - constants.LONG_GRID_EXTRA))
                                   / constants.GRID_WIDTH), 0))
        max_col = int(min(np.ceil((max_y - (constants.MIN_LONG - constants.LONG_GRID_EXTRA))
                                  / constants.GRID_WIDTH), self.max_cols))

        receptors_in_radius = []
        for row_index in range(min_row, max_row):
            for col_index in range(min_col, max_col):
                index = self.max_cols * row_index + col_index
                r = self.receptors[index]

                if r.in_range_of_point(point, radius * RECEPTOR_RADIUS_MULTIPLIER):
                    receptors_in_radius.append(r)

        t_1 = time.perf_counter()
        constants.time_spent_selecting_receptors += (t_1 - t_0)
        return receptors_in_radius

    def get_closest_receptor(self, point: Point) -> Receptor:
        h_space_between_receptors = constants.GRID_WIDTH
        v_space_between_receptors = constants.GRID_HEIGHT

        radius = max(h_space_between_receptors, v_space_between_receptors)

        potential_receptors = self.select_receptors_in_radius(point, radius * constants.LATITUDE_CONVERSION_FACTOR)
        dist = math.inf

        selected_receptor = None

        for receptor in potential_receptors:
            distance_to_receptor = receptor.location.distance_to_point(point)
            if distance_to_receptor < dist:
                dist = distance_to_receptor
                selected_receptor = receptor

        if selected_receptor is None:
            point.add_point_to_plot(constants.axes_plot, color="purple")
            radius_patch = matplotlib.patches.Circle((point.x, point.y),
                                                     radius=radius,
                                                     color="purple", alpha=0.1, linewidth=None)
            constants.axes_plot.add_patch(radius_patch)
            raise ValueError(f"Failed to find suitable receptor at {point} - {radius=} - {point.x, point.y}.")

        return selected_receptor

    def depreciate_pheromones(self):
        global PHEROMONE_DEPRECIATION_FACTOR_PER_TIME_DELTA

        for receptor in self.receptors:
            if receptor.decay:
                receptor.coalition_pheromones = (receptor.coalition_pheromones *
                                                 PHEROMONE_DEPRECIATION_FACTOR_PER_TIME_DELTA
                                                 ** (1 / self.world.time_delta))
                receptor.china_pheromones = (receptor.china_pheromones *
                                             PHEROMONE_DEPRECIATION_FACTOR_PER_TIME_DELTA
                                             ** (1 / self.world.time_delta))

    def calculate_cop(self, point: Point, radius: float, pheromone_type="beta") -> (float, list):
        """
        Calculates the concentration of pheromones (c_o_p)
        :param point:
        :param radius:
        :param pheromone_type: Type of pheromone (Taiwan is alpha pheromones, China is beta pheromones)
        :return:
        """
        # Increase radius of receptors selected by a factor 2 to make more future-proof decisions
        receptors = self.select_receptors_in_radius(point, radius * 2)

        if not is_in_area_of_interest(point):
            return math.inf, receptors

        for polygon in self.polygons:
            if polygon.check_if_contains_point(point, exclude_edges=False):
                return math.inf, receptors

        c_o_p = 0
        if pheromone_type == "coalition":
            for receptor in receptors:
                c_o_p += (1 / max(0.1, calculate_distance(a=point, b=receptor.location))) * receptor.coalition_pheromones
        elif pheromone_type == "china":
            for receptor in receptors:
                c_o_p += (1 / max(0.1, calculate_distance(a=point, b=receptor.location))) * receptor.china_pheromones
        # logger.debug(f"Calculated c_o_p at {point} with rad {radius}: {c_o_p} - from {len(receptors)} receptors.")
        return c_o_p, receptors


def is_in_area_of_interest(point: Point) -> bool:
    if constants.MIN_LAT <= point.x <= constants.MAX_LAT and constants.MIN_LONG <= point.y <= constants.MAX_LONG:
        return True
    else:
        return False
