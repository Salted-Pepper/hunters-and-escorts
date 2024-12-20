import random
from abc import ABC, abstractmethod
import general_maths
from agents import Agent
from points import Point
from bases import Base
from ships import Ship, Merchant, Escort

from general_maths import calculate_distance
import constants
import model_info
import zones
from zones import Zone

import copy
import math
import numpy as np

import os
import logging
import datetime

date = datetime.date.today()
logging.basicConfig(level=logging.DEBUG, filename=os.path.join(os.getcwd(), 'logs/navy_UAV_log_' + str(date) + '.log'),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%H:%M:%S")
logger = logging.getLogger("UAV")
logger.setLevel(logging.DEBUG)


class Aircraft(Agent):
    def __init__(self, manager, base: Base, model: str):
        super().__init__(manager, base, model)

        self.engaged_in_combat = False
        self.aircraft_type = None

    @abstractmethod
    def surface_detection(self) -> object | None:
        pass

    @abstractmethod
    def air_detection(self) -> object | None:
        pass

    @abstractmethod
    def sub_detection(self) -> object | None:
        pass

    def initialize_model(self) -> None:
        information = [row for row in model_info.UAV_MODELS if row['name'] == self.model][0]

        self.team = information['team']
        self.surface_visibility = information['SurfaceVisibility']
        self.surface_attack_range = information['surface_attack_range']
        self.surface_detection_range = 83
        self.speed_max = information['SpeedMax [km/hr]']
        self.speed_cruising = information['SpeedCruise']
        self.speed_current = self.speed_cruising
        self.endurance = information['endurance']
        self.remaining_endurance = self.endurance

        self.able_to_attack = True if information['armed'] == "Y" else False

        for weapon in str(information['SurfaceWeaponsList']).split(","):
            self.anti_surface_weapons = weapon
            # TODO: Adjust this for multiple weapons
            self.surf_ammo_max = int(information['SurfaceAmmunitionList'])
            self.surf_ammo_current = self.surf_ammo_max
        self.aircraft_type = information['type']


class UAV(Aircraft):
    def __init__(self, manager, base: Base, model: str):
        super().__init__(manager, base, model)
        self.service = constants.HUNTER_UAV
        self.obstacles = zones.JAPAN_AND_ISLANDS + zones.OTHER_LAND + [zones.ZONE_B.polygon]
        self.color = constants.UAV_COLOR
        self.marker_type = "X"
        self.called_in_attacker = False

        self.model = model
        self.initialize_model()
        self.radius = self.surface_attack_range
        self.calculate_maintenance_time()

    def __str__(self):
        if self.mission == "patrolling":
            return f"u{self.agent_id}p"
        elif self.is_returning:
            return f"u{self.agent_id}r"
        elif self.is_trailing:
            return f"u{self.agent_id}t"
        else:
            return f"u{self.agent_id}"

    def take_turn(self) -> None:
        self.movement_left_in_turn = self.speed_current * constants.world.time_delta

        if not self.can_continue():
            self.return_to_base()
            self.move_through_route()

        i = 0
        while self.movement_left_in_turn > 0:

            if not (self in self.manager.active_agents):
                print(f"{self} - {self.mission}")

            i += 1
            if i > 100:
                print(f"{self.mission} - {self.movement_left_in_turn}")
            if self.mission == "start_patrol":
                self.move_through_route()
            elif self.mission == "trail":
                self.update_trail_route()
                self.move_through_route()

                if self.located_agent is not None:
                    if self.location == self.located_agent.location:
                        self.movement_left_in_turn = 0
                    self.take_action_on_agent()

            elif self.mission == "patrol":
                self.move_through_route()
                self.surface_detection()
            elif self.mission == "return":
                self.move_through_route()

            if not (self in self.manager.active_agents):
                print(f"{self} - {self.mission}")

        self.update_plot()

    def take_action_on_agent(self) -> None:
        if zones.ZONE_B.polygon.check_if_contains_point(self.located_agent.location):
            self.stop_trailing("Target in illegal zone")
            return

        if (general_maths.calculate_distance(self.located_agent.location, self.located_agent.location) >
                self.surface_attack_range):
            return

        # Scenario 1: No attacking UAVs
        if constants.CHINA_SELECTED_LEVEL == 1:
            self.call_in_boarder()
        # Scenario 2: Allowed and able to attack
        elif self.able_to_attack and constants.CHINA_SELECTED_LEVEL > 1:
            self.attack()
        elif constants.CHINA_SELECTED_LEVEL > 1:
            self.call_in_attacking_UAV()

    def stop_trailing(self, reason: str) -> None:
        """
        Makes the agent stop trailing any agent it is trailing.
        :param reason: String describing why the trailing was aborted
        :return:
        """
        if not self.is_trailing:
            logger.error(f"Agent {self} was not trailing - ordered to stop trailing {self.located_agent}")
            return

        self.called_in_attacker = False
        self.is_trailing = False
        self.mission = "patrol"
        logger.debug(f"{self} stopped trailing {self.located_agent} - {reason}")

        self.speed_current = self.speed_cruising

        if self in self.located_agent.trailing_agents:
            self.located_agent.trailing_agents.remove(self)
        self.located_agent = None

        self.release_support_agents()
        self.return_to_base()

    def call_in_boarder(self) -> None:
        if not self.called_in_attacker:
            print(f"{self} is calling in boarder on {self.located_agent}")
            constants.world.CNManager.send_attacker(self.located_agent)
            self.called_in_attacker = True

    def call_in_attacking_UAV(self) -> None:
        if not self.called_in_attacker:
            print(f"{self} is calling in attacking UAV on {self.located_agent} - {self.able_to_attack=}")
            constants.world.UAVManager.send_attacker(self.located_agent)
            self.called_in_attacker = True

    def attack(self) -> None:
        distance_to_target = general_maths.calculate_distance(self.located_agent.location, self.location)
        if distance_to_target > self.surface_attack_range:
            return
        elif self.surf_ammo_current > 0:
            self.surf_ammo_current -= 1
            self.located_agent.take_damage()
        else:
            self.return_to_base()

    def calculate_maintenance_time(self) -> None:
        """
        Calculates maintenance times for the type of UAV
        :return:
        """
        self.maintenance_time = 3.4 + 0.68 * self.endurance

    def move_through_route(self):
        if self.next_point is not None:
            distance_to_next_point = self.location.distance_to_point(self.next_point)

            distance_travelled = min(self.movement_left_in_turn, distance_to_next_point)
            self.movement_left_in_turn -= distance_travelled

            # Instance 1: We can reach the next point
            if distance_to_next_point <= distance_travelled:
                self.last_location = self.next_point
                self.past_points.append(self.next_point)
                self.location = copy.deepcopy(self.next_point)

                # Instance 1a: Reached point, getting ready for next point
                if len(self.remaining_points) > 0:
                    self.next_point = self.remaining_points.pop(0)

                # Instance 1b: Reached point, was final point on route
                else:
                    self.reached_end_of_route()
                    if constants.DEBUG_MODE:
                        self.debug()
                    return

            # Instance 2: We travel towards the next point but do not reach it
            else:
                part_of_route = (distance_travelled / distance_to_next_point)
                new_x = self.location.x + part_of_route * (self.next_point.x - self.location.x)
                new_y = self.location.y + part_of_route * (self.next_point.y - self.location.y)
                self.location = Point(new_x, new_y, name=str(self))

                if constants.DEBUG_MODE:
                    self.debug()
                return

    def surface_detection(self) -> None:
        if self.is_returning:
            return

        active_hostile_ships = [agent
                                for manager in constants.world.managers
                                if manager.team != self.team
                                for agent in manager.active_agents
                                if (agent.activated and issubclass(type(agent), Ship))]

        for target_ship in active_hostile_ships:
            # If it's already being trailed, we don't have to double up unless called in
            if len(target_ship.trailing_agents) > 0:
                continue

            # TODO: Update target selection behaviour based on RoE
            # If it's an escort we want to avoid it
            if issubclass(type(target_ship), Escort):
                continue

            # Do a check that the target ship is even remotely close
            radius_travelled = self.speed_current * constants.world.time_delta + self.surface_detection_range
            distance = calculate_distance(a=self.location, b=target_ship.location)
            if distance > radius_travelled:
                continue

            # Break up the detection in smaller time steps
            detection_probabilities = []
            num_of_steps = int(np.ceil(constants.world.time_delta / constants.sub_time_delta))
            for lamb in np.append(np.arange(0, 1, step=1/num_of_steps), 1):
                uav_location = Point(self.location.x * lamb + self.last_location.x * (1 - lamb),
                                     self.location.y * lamb + self.last_location.y * (1 - lamb))
                distance = calculate_distance(a=uav_location, b=target_ship.location)
                if distance <= self.surface_detection_range:
                    detection_probabilities.append(self.roll_surface_detection_check(uav_location,
                                                                                     target_ship, distance))
            probability = 1 - np.prod([(1 - p) ** (1 / num_of_steps) for p in detection_probabilities])
            if np.random.rand() <= probability:
                self.start_trailing(target_ship)

    def air_detection(self) -> object | None:
        pass

    def sub_detection(self) -> object | None:
        pass

    @staticmethod
    def roll_surface_detection_check(uav_location, agent: Agent, distance: float = None) -> float:
        """
        Function for UAVs to detect surface vessels
        :param uav_location:
        :param agent:
        :param distance:
        :return: Detection probability
        """
        if distance is None:
            distance = calculate_distance(a=uav_location, b=agent.location)

        # Get weather conditions in area
        closest_receptor = constants.world.receptor_grid.get_closest_receptor(agent.location)
        sea_state = closest_receptor.sea_state
        sea_state_to_parameter = {0: 0.89,
                                  1: 0.89,
                                  2: 0.77,
                                  3: 0.68,
                                  4: 0.62,
                                  5: 0.53,
                                  6: 0.47}

        if sea_state < 7:
            weather = sea_state_to_parameter[sea_state]
        else:
            weather = 0.40

        height = 10  # Assumed to be 10km

        if agent.air_visibility == constants.stealth:
            rcs = 0.5
        elif agent.air_visibility == constants.vsmall:
            rcs = 0.9
        elif agent.air_visibility == constants.small:
            rcs = 1
        elif agent.air_visibility == constants.medium:
            rcs = 1.25
        elif agent.air_visibility == constants.large:
            rcs = 1.5
        else:
            raise ValueError(f"Invalid air visibility value for {agent} - {agent.air_visibility}.")

        top_frac_exp = constants.K_CONSTANT * height * weather * rcs
        if distance < 1:
            distance = 1
        probability = 1 - math.exp(-top_frac_exp / (distance ** 3))
        return probability

    def reached_end_of_route(self) -> None:
        if self.mission == "start_patrol":
            self.mission = "patrol"
        if self.mission == "patrol":
            new_location = self.assigned_zone.sample_patrol_location(self.obstacles + [constants.world.china_polygon])
            self.generate_route(new_location)
        elif self.mission == "trailing":
            self.movement_left_in_turn = 0
        elif self.mission == "return":
            self.movement_left_in_turn = 0
            self.enter_base()

    def destroyed_log_update(self) -> None:
        pass
