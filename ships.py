import random
import numpy as np
import copy
import math
from abc import ABC, abstractmethod

import general_maths
import constants
import constant_coords
import model_info
from agents import Agent
from bases import Base
from points import Point
import zones
from zones import Zone

import os
import logging
import datetime

date = datetime.date.today()
logging.basicConfig(level=logging.DEBUG, filename=os.path.join(os.getcwd(), 'logs/navy_SHIP_log_' + str(date) + '.log'),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%H:%M:%S")
logger = logging.getLogger("SHIPS")
logger.setLevel(logging.DEBUG)


class Ship(Agent):
    def __init__(self, manager, base: Base, model: str):
        super().__init__(manager, base, model)
        self.helicopter = False

    def move_through_route(self):
        if self.next_point is not None:
            distance_to_next_point = self.location.distance_to_point(self.next_point)

            distance_travelled = min(self.movement_left_in_turn, distance_to_next_point)
            self.movement_left_in_turn -= distance_travelled
            self.remaining_endurance -= distance_travelled

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

    @abstractmethod
    def surface_detection(self) -> object | None:
        pass

    @abstractmethod
    def air_detection(self) -> object | None:
        pass

    @abstractmethod
    def sub_detection(self) -> object | None:
        pass


class Merchant(Ship):
    def __init__(self, manager, base: Base, country: str, model: str):
        super().__init__(manager, base, model)
        self.team = constants.TEAM_COALITION
        self.country = country
        self.obstacles = constants.world.landmasses
        self.major_category = constants.MERCHANT
        self.service = constants.COALITION_TW_MERCHANT

        self.entry_point = None
        self.generate_entry_point()
        self.is_boarded = False

        self.delivered_cargo = False
        self.cargo_load = None
        self.initialize_model()

        self.activated = True
        self.generate_route(base.location)

        # --- plotting ----
        self.color = constants.MERCHANT_COLOR
        self.marker_type = "*"

    def __str__(self):
        if self.delivered_cargo:
            return f"m{self.agent_id}d"
        elif self.is_boarded:
            return f"m{self.agent_id}b"
        else:
            return f"m{self.agent_id}"

    def initialize_model(self) -> None:
        self.remaining_endurance = math.inf
        self.initialize_cargo()

        self.maintenance_time = 3 * 24

        if self.model == constants.MERCHANT_CONTAINER:
            if self.cargo_load < 10_000:
                self.speed_current = 40
            elif self.cargo_load < 100_000:
                self.speed_current = 44
            else:
                self.speed_current = 44
            self.speed_max = self.speed_current

        elif self.model == constants.MERCHANT_BULK:
            if self.cargo_load < 10_000:
                self.speed_current = 20
            elif self.cargo_load < 100_000:
                self.speed_current = 22
            else:
                self.speed_current = 22
            self.speed_max = self.speed_current

        elif self.model == constants.MERCHANT_PETROL:
            if self.cargo_load < 10_000:
                self.speed_current = 22
            elif self.cargo_load < 100_000:
                self.speed_current = 26
            else:
                self.speed_current = 26
            self.speed_max = self.speed_current

        elif self.model == constants.MERCHANT_LNG:
            if self.cargo_load < 10_000:
                self.speed_current = 25
            elif self.cargo_load < 100_000:
                self.speed_current = 29
            else:
                self.speed_current = 29
            self.speed_max = self.speed_current

    def initialize_cargo(self):
        # ---- Cargo Load ----
        # Temporary placeholder weibull sample for cargo (falls between 0 and 150000)
        # if self.model == constants.MERCHANT_CONTAINER:
        # elif self.model == constants.MERCHANT_BULK:
        # elif self.model == constants.MERCHANT_PETROL:
        # elif self.model == constants.MERCHANT_LNG:
        self.cargo_load = np.random.weibull(1.5) * 50000

        if self.cargo_load < 1_000:
            self.set_visibility(constants.vsmall)
        elif self.cargo_load < 10_000:
            self.set_visibility(constants.small)
        elif self.cargo_load < 100_000:
            self.set_visibility(constants.medium)
        else:
            self.set_visibility(constants.large)

    def set_visibility(self, visibility: str):
        self.surface_visibility = visibility
        self.air_visibility = visibility
        self.submarine_visibility = visibility

    def take_damage(self) -> None:
        """
        Merchant taking damage - transition to destroyed or CTL depending on attack and
        :return:
        """
        random_value = random.uniform(0, 1)

        if self.cargo_load < 10_000:
            if random_value < (7.7 / 100):
                self.was_destroyed()
            elif random_value < (15.4 + 7.7) / 100 and not self.CTL:
                self.CTL = True
        elif self.cargo_load < 20_000:
            if random_value < 3.6 / 100:
                self.was_destroyed()
            elif random_value < (3.6 + 21.4) / 100:
                self.CTL = True
        elif self.cargo_load < 90_000:
            if random_value < 2.4 / 100:
                self.was_destroyed()
            elif random_value < (2.4 + 6) / 100:
                self.CTL = True
        else:
            if random_value < 8.5:
                self.CTL = True

        if self.CTL:
            constants.interface.update_statistics_and_logs(event_code="merchant_damaged",
                                                           log=f"{self} - CTL", )

    def destroyed_log_update(self) -> None:
        constants.interface.update_statistics_and_logs(event_code="merchant_sunk",
                                                       log=f"{self} was sunk.")

    def generate_entry_point(self):
        longitude = random.uniform(constants.MIN_LONG, constants.MAX_LONG)
        latitude = constants.MAX_LAT
        self.entry_point = Point(latitude, longitude)
        self.location = copy.deepcopy(self.entry_point)
        logger.debug(f"Merchant {self.agent_id} enters at {self.entry_point}")
        self.activated = True

    def take_turn(self) -> None:
        self.movement_left_in_turn = self.speed_current * constants.world.time_delta
        self.move_through_route()
        if (self.team == constants.TEAM_CHINA and
                zones.ZONE_L.polygon.check_if_contains_point(self.location)):
            for agent in self.trailing_agents:
                agent.stop_trailing("Merchant crossed median line")
        self.update_plot()

    def reached_end_of_route(self) -> None:
        # Case 1a: Reached harbour non-boarded
        if self.location == self.base.location:
            # Enter base
            self.enter_base()

        # Case 1b: Reached Chinese harbour boarded
        elif self.is_boarded:
            self.enter_base()

        # Case 2: Safely exited the map
        elif self.location == self.entry_point:
            self.activated = False
            self.remove_from_plot()

        # Case 3: Temporary reroute
        else:
            if self.delivered_cargo:
                self.generate_route(self.entry_point)
            else:
                self.generate_route(self.base.location)

    def enter_base(self) -> None:
        print(f"{self} has entered {self.base}")
        self.is_returning = False
        self.activated = False
        self.remove_guarding_agents()
        self.remove_trailing_agents("Reached base")

        if self.is_boarded:
            self.manager.active_agents.remove(self)
        else:
            self.manager.active_agents.remove(self)
            self.manager.inactive_agents.append(self)
            self.start_maintenance()

        self.entered_base_log()

        self.cargo_load = 0
        self.remove_from_plot()

    def entered_base_log(self) -> None:
        if self.is_boarded:
            constants.interface.update_statistics_and_logs(event_code="boarded_merchant_arrived",
                                                           log=f"{self} was seized.")
        else:
            constants.interface.update_statistics_and_logs(event_code="merchant_arrived",
                                                           log=f"{self} has reached {self.base}",
                                                           other=self.cargo_load)

    def complete_maintenance(self):
        self.delivered_cargo = True
        self.past_points = []
        self.generate_route(self.entry_point)
        self.activated = True

    def successful_boarding(self):
        """
        Vessel got boarded by chinese forces and will start moving towards the Chinese coastline
        :return:
        """
        constants.interface.update_statistics_and_logs(event_code=None,
                                                       log=f"{self} has been boarded.")
        self.is_boarded = True
        logger.debug(f"{self} has been boarded.")
        self.team = constants.TEAM_CHINA
        self.obstacles = zones.JAPAN_AND_ISLANDS + zones.OTHER_LAND + [zones.ZONE_B.polygon] + [zones.CHINA]
        boarding_destination = self.select_closest_harbour(constants.world.CNManager.bases)
        self.generate_route(destination=boarding_destination)
        self.color = constants.CHINESE_NAVY_COLOR

        for agent in self.trailing_agents:
            print(f"{agent} stopped trailing as {self} got boarded")
            agent.stop_trailing(reason="Ship was boarded")

    def successful_counter_boarding(self):
        """
        Vessel that was boarded got liberated - seeks route to the closest Taiwanese harbour
        :return:
        """
        logger.debug(f"{self} has been liberated from boarding.")
        self.is_boarded = False
        self.team = constants.TEAM_COALITION
        if self.delivered_cargo:
            self.generate_route(destination=self.entry_point)
        else:
            self.generate_route(destination=self.base.location)

        self.obstacles = constants.world.landmasses

        for agent in self.guarding_agents:
            agent.stop_guarding()

        constants.interface.update_statistics_and_logs(event_code="deterred",
                                                       log=f"{self} has been liberated from boarding.")
        self.color = constants.MERCHANT_COLOR

    def select_closest_harbour(self, list_of_harbours: list) -> Point:
        min_dist = math.inf
        closest_harbour = None

        for harbour in list_of_harbours:
            dist = general_maths.calculate_distance(self.location, harbour.location)
            if dist < min_dist:
                closest_harbour = harbour
                min_dist = dist
        return closest_harbour.location

    def surface_detection(self):
        return None

    def air_detection(self):
        return None

    def sub_detection(self):
        return None


class HunterShip(Ship):
    def __init__(self, manager, base: Base, model: str):
        super().__init__(manager, base, model)
        self.obstacles = zones.HUNTER_ILLEGAL_ZONES + zones.NAVY_ILLEGAL_ZONES
        self.major_category = constants.HUNTER_NAVY
        self.model = model
        self.radius = 12
        self.team = constants.TEAM_CHINA
        self.engaged_in_combat = False
        self.failed_boarding = False

        self.color = constants.CHINESE_NAVY_COLOR
        self.marker_type = "D"

        self.initialize_model()

    def __str__(self):
        if self.mission == "start_patrol":
            return f"h{self.agent_id}s{self.assigned_zone}"
        elif self.mission == "patrol":
            return f"h{self.agent_id}p{self.assigned_zone}"
        elif self.mission == "trail":
            return f"h{self.agent_id}t{self.assigned_zone}"
        elif self.mission == "guarding":
            return f"h{self.agent_id}g{self.assigned_zone}"
        elif self.mission == "return":
            return f"h{self.agent_id}r{self.assigned_zone}"
        else:
            return f"h{self.agent_id}"

    def destroyed_log_update(self):
        # TODO: Implement
        pass

    def surface_detection(self) -> Ship | None:
        active_hostile_ships = [agent
                                for manager in constants.world.managers
                                if manager.team != self.team
                                for agent in manager.active_agents
                                if (agent.activated and issubclass(type(agent), Ship) and agent.team != self.team)]

        for potential_target in active_hostile_ships:
            distance = general_maths.calculate_distance(self.location, potential_target.location)

            if issubclass(type(potential_target), Escort):
                continue

            if distance > 56:
                continue

            if self.surface_detection_range == "Advanced":
                if potential_target.surface_visibility == "VSmall" and distance < 37:
                    return potential_target
                elif potential_target.surface_visibility == "Small" and distance < 37:
                    return potential_target
                elif potential_target.surface_visibility == "Medium" and distance < 56:
                    return potential_target
            else:
                if potential_target.surface_visibility == "Small" and distance < 28:
                    return potential_target
                elif potential_target.surface_visibility == "VSmall" and distance < 17:
                    return potential_target
        return None

    def air_detection(self) -> Agent | None:
        # TODO: Implement
        pass

    def sub_detection(self) -> Agent | None:
        # TODO: Implement
        pass

    def take_turn(self) -> None:
        self.movement_left_in_turn = self.speed_current * constants.world.time_delta

        if not self.can_continue():
            self.return_to_base()
            self.move_through_route()

        i = 0
        while self.movement_left_in_turn > 0:
            i += 1
            if i > 100:
                raise TimeoutError(f"{self} not able to spend movement during mission - {self.mission}")
            if self.mission == "start_patrol":
                self.move_through_route()
            elif self.mission == "trail":
                self.take_trailing_action()
            elif self.mission == "patrol":
                self.move_through_route()
                target = self.surface_detection()
                if target is not None and isinstance(target, Merchant):
                    self.start_trailing(target)
                elif target is issubclass(type(target), Escort):
                    # TODO: treat non-merchant targets - consider redoing finding and treating targets.
                    #  Current issue: might find non-eligible target before eligible one
                    pass
            elif self.mission == "guarding":
                self.update_trail_route()
                self.move_through_route()
                if self.location == self.base.location:
                    self.return_to_base()
                    return
                elif self.location == self.guarding_target.location:
                    self.movement_left_in_turn = 0
                elif not self.guarding_target.activated:
                    self.return_to_base()
            elif self.mission == "return":
                self.move_through_route()
        self.update_plot()

    def take_trailing_action(self) -> None:
        self.update_trail_route()
        self.move_through_route()

        if self.located_agent is not None and self.allowed_to_attack(self.located_agent):
            if not self.failed_boarding:
                self.attempt_boarding()
            else:
                self.attempt_attack()

    def initialize_model(self) -> None:
        information = [row for row in model_info.CN_NAVY_MODELS if row['name'] == self.model][0]

        self.team = information['team']
        self.able_to_attack = True if information['armed'] == 'Y' else False
        self.surface_visibility = information['SurfaceVisibility']
        self.surface_detection_range = information['surface_detection_range']
        self.speed_max = information['SpeedMax']
        self.speed_cruising = information['SpeedCruise']
        self.speed_current = self.speed_cruising
        self.displacement = information['Displacement']
        self.endurance = information['endurance']

        if self.endurance is None:
            self.endurance = 8000.11111111

        self.remaining_endurance = self.endurance

        # TODO: Import weapons in new method

        self.helicopter = True if information['helicopter'] == "Y" else False
        self.service = information['service']

    def detect_agent(self, target):
        """
        Check if we can
        :param target:
        :return:
        """
        detected = False
        distance = general_maths.calculate_distance(a=self, b=target)
        if target.displacement < 10_000:
            if distance < 24:
                detected = True
        elif target.displacement < 100_000:
            if distance < 35:
                detected = True
        else:
            if distance < 24:
                detected = True

        if not detected:
            return

        if isinstance(target, Merchant):
            self.start_trailing(target)
        elif isinstance(target, Escort):
            self.return_to_base()
            constants.interface.update_statistics_and_logs(event_code="deterred",
                                                           text=f"{self} was deterred.")

    def attempt_boarding(self):
        """
        See if Chinese Navy unit is able to board
        :return:
        """
        # 1 - Check if boarding is allowed in zone
        # 2 - if within 12 km attempt boarding
        # 3 - Check if there's an escort
        # 4 - roll boarding attempt (odds based on description in overleaf page 18)
        if general_maths.calculate_distance(self.location, self.located_agent.location) > 12:
            print(f"{self} is looking to board {self.located_agent} - but is out of range")
            return
        elif any([zone.check_if_agent_in_zone(self.located_agent) for zone in [zones.ZONE_I]]):
            self.engaged_in_combat = True
            # Board the ship
            success_probability = 0.22
            if self.service == "CCG" or self.service == "MSA":
                success_probability += 0.2

            if self.helicopter:
                success_probability += 0.2

            receptor = constants.world.receptor_grid.get_closest_receptor(self.location)
            if receptor.sea_state == 3:
                success_probability -= 0.2
            elif receptor.sea_state >= 4:
                success_probability = 0
            # TODO: (Non) Compliance rules

            if success_probability > random.uniform(0, 1):
                logger.debug(f"{self} attempted to board {self.located_agent} - but failed")
                constants.interface.update_statistics_and_logs(event_code=None,
                                                               log=f"{self} failed to board {self.located_agent}.")
                return

        logger.debug(f"{self} has boarded {self.located_agent}")
        self.guarding_target = self.located_agent
        self.is_trailing = False
        self.mission = "guarding"
        self.located_agent.successful_boarding()
        self.generate_route(self.located_agent.location)

    def reached_end_of_route(self) -> None:
        if self.mission == "start_patrol":
            self.mission = "patrol"

        if self.mission == "patrol":
            new_location = self.assigned_zone.sample_patrol_location(self.obstacles)
            self.generate_route(new_location)
        elif self.mission == "trailing":
            self.movement_left_in_turn = 0
        elif self.mission == "return":
            self.movement_left_in_turn = 0
            self.enter_base()
        elif self.mission == "guarding":
            self.movement_left_in_turn = 0


class Escort(Ship):

    def __init__(self, manager, base: Base, model: str):
        super().__init__(manager, base, model)
        self.model = model
        self.obstacles = zones.JAPAN_AND_ISLANDS + zones.OTHER_LAND + [zones.CHINA] + zones.TAIWAN_AND_ISLANDS
        self.initialize_model()
        self.major_category = constants.COALITION_ESCORT

    def __str__(self):
        if self.is_trailing:
            return f"e{self.agent_id}t{self.assigned_zone}"
        elif self.mission == "guarding":
            return f"e{self.agent_id}g{self.assigned_zone}"
        elif self.mission == "start_patrol":
            return f"e{self.agent_id}s{self.assigned_zone}"
        elif self.mission == "patrol":
            return f"e{self.agent_id}p{self.assigned_zone}"
        elif self.mission == "return":
            return f"e{self.agent_id}r{self.assigned_zone}"
        else:
            return f"e{self.agent_id}"

    def initialize_model(self):
        information = [row for row in model_info.SHIP_MODELS if row['name'] == self.model][0]

        self.team = information['team']

        self.surface_visibility = information['SurfaceVisibility']
        self.air_visibility = information['Airvisibility']
        self.sub_visibility = information['UnderseaVisibility']

        self.surface_detection_range = information['surface_detection_range']
        self.air_detection_range = information['air_detection_range']
        self.sub_detection_range = information['submarine_detection_range']

        self.speed_max = information['SpeedMax']
        self.speed_cruising = information['SpeedCruise']
        self.speed_current = self.speed_cruising
        self.displacement = information['Displacement']
        self.endurance = information['endurance']
        if self.endurance is None:
            self.endurance = 8000.11111111
        self.remaining_endurance = self.endurance

        # TODO: Update for new weapon settings

        self.helicopter = True if information['helicopter'] == "Y" else False

    def surface_detection(self) -> Ship | None:
        active_ships = constants.world.CNManager.active_agents

        for potential_target in active_ships:
            distance = general_maths.calculate_distance(self.location, potential_target.location)

            if self.surface_detection_range == "Advanced":
                if potential_target.surface_visibility == "VSmall" and distance < 37:
                    return potential_target
                elif potential_target.surface_visibility == "Small" and distance < 37:
                    return potential_target
                elif potential_target.surface_visibility == "Medium" and distance < 56:
                    return potential_target
            else:
                if potential_target.surface_visibility == "Small" and distance < 28:
                    return potential_target
                elif potential_target.surface_visibility == "VSmall" and distance < 17:
                    return potential_target
        return None

    def air_detection(self) -> object | None:
        pass

    def sub_detection(self) -> object | None:
        pass

    def take_turn(self) -> None:
        self.movement_left_in_turn = self.speed_current * constants.world.time_delta

        if not self.can_continue():
            self.return_to_base()
            self.move_through_route()

        i = 0
        while self.movement_left_in_turn > 0:
            i += 1
            if i > 100:
                raise TimeoutError()
            if self.mission == "start_patrol":
                self.move_through_route()
            elif self.mission == "trail":
                if zones.ZONE_L.check_if_agent_in_zone(self.located_agent):
                    self.stop_trailing("Merchant passed median line")
                    continue
                self.update_trail_route()
                self.move_through_route()
                if isinstance(self.located_agent, Merchant):
                    self.counter_board(self.located_agent)
            elif self.mission == "patrol":
                self.move_through_route()
                if constants.COALITION_SELECTED_LEVEL > 1:
                    target = self.surface_detection()
                    if isinstance(target, Merchant) and len(target.trailing_agents) == 0:
                        self.start_trailing(target)
                    elif isinstance(target, HunterShip):
                        constants.interface.update_statistics_and_logs(event_code="deterred",
                                                                       log=f"{self} deterred {target}")
                        target.return_to_base()
                    else:
                        continue
            elif self.mission == "guarding":
                self.continue_guarding()
            elif self.mission == "return":
                self.move_through_route()
        self.update_plot()

    def counter_board(self, located_agent: Merchant) -> None:
        if general_maths.calculate_distance(self.location, located_agent.location) > 12:
            return

        # if close enough
        located_agent.successful_counter_boarding()
        self.start_guarding(located_agent)

    def continue_guarding(self):
        if self.guarding_target is None:
            self.stop_guarding()
            self.return_to_base()
            self.move_through_route()
        else:
            self.generate_route(self.guarding_target.location)
            self.move_through_route()

    def start_guarding(self, target: Merchant) -> None:
        self.guarding_target = target
        self.mission = "guarding"
        self.generate_route(target.location)

    def stop_guarding(self) -> None:
        logger.debug(f"{self} stopped guarding {self.guarding_target}")
        self.guarding_target = None
        self.generate_route(self.base.location)
        self.mission = "return"

    def reached_end_of_route(self) -> None:
        if self.mission == "start_patrol":
            self.mission = "patrol"
        if self.mission == "patrol":
            new_location = self.assigned_zone.sample_patrol_location(self.obstacles)
            self.generate_route(new_location)
        elif self.mission == "trailing":
            if not self.check_target_in_legal_zone():
                self.stop_trailing(f"{self.located_agent} is in a restricted zone.")
                self.mission = "patrolling"
                self.generate_route(destination=self.assigned_zone.sample_patrol_location(self.obstacles))
            else:
                self.movement_left_in_turn = 0
        elif self.mission == "guarding":
            self.movement_left_in_turn = 0
        elif self.mission == "return":
            self.movement_left_in_turn = 0
            self.enter_base()

    def destroyed_log_update(self) -> None:
        constants.interface.update_statistics_and_logs(event_code="escort_sunk",
                                                       log=f"{self} was sunk.")


class TaiwanEscort(Escort):
    def __init__(self, manager, base: Base, model: str):
        super().__init__(manager, base, model)
        self.service = constants.COALITION_TW_ESCORT

        self.marker_type = "D"
        self.color = constants.TAIWAN_ESCORT_COLOR
        self.radius = 2


class JapanEscort(Escort):
    def __init__(self, manager, base: Base, model: str):
        super().__init__(manager, base, model)
        self.service = constants.COALITION_JP_ESCORT

        self.marker_type = "D"
        self.color = constants.JAPAN_ESCORT_COLOR
        self.radius = 2


class USEscort(Escort):
    def __init__(self, manager, base: Base, model: str):
        super().__init__(manager, base, model)
        self.service = constants.COALITION_US_ESCORT

        self.marker_type = "D"
        self.color = constants.US_ESCORT_COLOR
        self.radius = 2


