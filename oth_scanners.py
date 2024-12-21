import random
import copy
import math
import matplotlib.patches

from general_maths import calculate_direction_vector, km_to_latitudinal_distance, km_to_longitudinal_distance

import constants
from points import Point
from polygons import Polygon
from ships import Merchant


class OTH:
    def __init__(self, location: Point, direction_point: Point, manager):
        self.manager = manager
        self.team = 2
        self.location = location
        self.direction = None
        self.normalize_direction(direction_point)

        # Degree of the
        self.angle = 35
        # Save degrees and sines/cosines to prevent redoing calculations consistently
        self.pos_cos = math.cos(math.radians(self.angle / 2))
        self.pos_sin = math.sin(math.radians(self.angle / 2))
        # rev: for reverse rotation
        self.rev_cos = math.cos(math.radians(-self.angle / 2))
        self.rev_sin = math.sin(math.radians(-self.angle / 2))

        self.color = "black"

        # Scanning parameters
        self.range_band = 30
        self.scan_time = 1 / 60  # Scan one bandwidth per minute

        self.min_band = 700
        self.max_band = 3500

        self.current_band = self.min_band

        self.scanned_polygon = None
        self.range_band_plot = None

        # Status of actions and located agents
        self.located_agents = []
        self.action_queue = []

    def __str__(self):
        return f"OTH at {self.location.x}, {self.location.y}"

    def normalize_direction(self, direction_point):
        """
        Ensure that the direction of the OTH is a normalized position.
        :return:
        """
        self.direction = calculate_direction_vector(self.location, direction_point)

    def perform_scan(self):
        """
        Perform all the actions for the OTH for each turn
        :return:
        """
        # Take the next step of the range scan
        self.check_scan_area()
        self.call_actions()
        self.update_range_band_plot()

    @staticmethod
    def detected_agent(agent) -> bool:
        receptor = constants.world.receptor_grid.get_closest_receptor(agent.location)
        sea_state = receptor.sea_state
        detected = False

        if isinstance(agent, Merchant):
            if sea_state <= 1:
                detected = True
            elif sea_state == 2 and agent.cargo_load >= 500:
                detected = True
            elif sea_state == 3 and agent.cargo_load >= 1200:
                detected = True
            elif sea_state == 4 and agent.cargo_load >= 10_000:
                detected = True
            elif sea_state == 5 and agent.cargo_load >= 100_000:
                detected = True

        return detected

    def call_actions(self):
        """
        Queues actions for located agents that are executed once the communication delay has passed.
        Tasks are in the format of a dict
        :return:
        """
        # TODO: Redo this - check what we send, why & how
        # tasks_to_remove = []
        # for task in self.action_queue:
        #     action = task['action']
        #     agent_location = task['location']
        #     time = task['time']
        #     if time > constants.world.world_time:
        #         continue
        #
        #     if action == "call UAV":
        #         successful = constants.world.UAV_manager.send_patrol_to_location(agent_location)
        #
        #         if successful:
        #             tasks_to_remove.append(task)
        #     else:
        #         raise NotImplementedError(f"Action {action} not implemented for OTH action call!")
        #
        # for task in tasks_to_remove:
        #     self.action_queue.remove(task)
        #
        # for agent in self.located_agents:
        #     self.action_queue.append({'action': "call UAV",
        #                               'location': copy.deepcopy(agent.location),
        #                               'time': constants.world.world_time + constants.COMMUNICATION_DELAY})
        # self.located_agents = []

    def check_scan_area(self) -> None:

        min_range = self.current_band
        max_range = self.current_band + (constants.world.time_delta / self.scan_time) * self.range_band

        if max_range > self.max_band:
            max_range = self.max_band
            self.current_band = self.min_band
        else:
            self.current_band = max_range

        agents_to_check = [agent
                           for manager in constants.world.managers
                           if manager.team != self.team
                           for agent in manager.active_agents
                           if agent.activated
                           and not agent.destroyed]

        self.scanned_polygon = self.calculate_scanned_polygon(min_range, max_range)

        located_agents = []
        for agent in agents_to_check:
            self.scanned_polygon.check_if_contains_point(agent.location)
            if self.detected_agent(agent):
                located_agents.append(agent)
        self.located_agents.extend(located_agents)

    def calculate_scanned_polygon(self, min_range: float, max_range: float) -> Polygon:
        """
        Calculate the polygon that is evaluated at the current timestep.
        :param min_range: Minimal bandwidth for the current timestep
        :param max_range: Maximum bandwidth for the current timestep
        :return:
        """
        direction_vector_x_min = self.location.x + self.direction[0] * km_to_latitudinal_distance(min_range,
                                                                                                  self.location.y)
        direction_vector_y_min = self.location.y + self.direction[1] * km_to_longitudinal_distance(min_range)

        direction_vector_x_max = self.location.x + self.direction[0] * km_to_latitudinal_distance(max_range,
                                                                                                  self.location.y)
        direction_vector_y_max = self.location.y + self.direction[1] * km_to_longitudinal_distance(max_range)

        dir_point_min = Point(direction_vector_x_min, direction_vector_y_min)
        dir_point_max = Point(direction_vector_x_max, direction_vector_y_max)

        # We now rotate the points with the angle. We have to subtract location to rotate around the origin then re-add
        low_min = Point(self.rev_cos * (direction_vector_x_min - self.location.x)
                        - self.rev_sin * (direction_vector_y_min - self.location.y) + self.location.x,
                        self.rev_sin * (direction_vector_x_min - self.location.x)
                        + self.rev_cos * (direction_vector_y_min - self.location.y) + self.location.y)
        high_min = Point(self.pos_cos * (direction_vector_x_min - self.location.x)
                         - self.pos_sin * (direction_vector_y_min - self.location.y) + self.location.x,
                         self.pos_sin * (direction_vector_x_min - self.location.x)
                         + self.pos_cos * (direction_vector_y_min - self.location.y) + self.location.y)
        low_max = Point(self.rev_cos * (direction_vector_x_max - self.location.x)
                        - self.rev_sin * (direction_vector_y_max - self.location.y) + self.location.x,
                        self.rev_sin * (direction_vector_x_max - self.location.x)
                        + self.rev_cos * (direction_vector_y_max - self.location.y) + self.location.y)
        high_max = Point(self.pos_cos * (direction_vector_x_max - self.location.x)
                         - self.pos_sin * (direction_vector_y_max - self.location.y) + self.location.x,
                         self.pos_sin * (direction_vector_x_max - self.location.x)
                         + self.pos_cos * (direction_vector_y_max - self.location.y) + self.location.y)

        return Polygon(points=[low_min, dir_point_min, high_min, high_max, dir_point_max, low_max],
                       color="salmon")

    def add_to_plot(self):
        """
        Adds just the BASE stations to the plot
        :return:
        """
        self.location.add_point_to_plot(constants.axes_plot, color=self.color, marker="8", plot_text=False,
                                        marker_edge_width=2, markersize=constants.WORLD_MARKER_SIZE - 4)

    def remove_range_band_from_plot(self) -> None:
        if not constants.PLOTTING_MODE:
            return

        if self.range_band_plot is not None:
            self.range_band_plot.remove()
            self.range_band_plot = None

    def update_range_band_plot(self) -> None:
        if not constants.PLOTTING_MODE:
            return

        self.remove_range_band_from_plot()
        if self.scanned_polygon is not None:
            self.add_range_band_to_plot()

    def add_range_band_to_plot(self):
        if self.color is None:
            self.range_band_plot = constants.axes_plot.add_patch(
                matplotlib.patches.Polygon([(p.x, p.y) for p in self.scanned_polygon.points],
                                           color="grey", closed=True, alpha=constants.RANGE_BAND_OPACITY))
        else:
            self.range_band_plot = constants.axes_plot.add_patch(
                matplotlib.patches.Polygon([(p.x, p.y) for p in self.scanned_polygon.points],
                                           closed=True, color=self.color, alpha=constants.RANGE_BAND_OPACITY))
