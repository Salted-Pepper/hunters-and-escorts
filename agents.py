import constants
import missions
import zones
from points import Point
from bases import Base
from zones import Zone
from routes import create_route, Route
import copy

import matplotlib.patches
from abc import ABC, abstractmethod

import os
import logging
import datetime

date = datetime.date.today()
logging.basicConfig(level=logging.DEBUG, filename=os.path.join(os.getcwd(), 'logs/log_' + str(date) + '.log'),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%H:%M")
logger = logging.getLogger("AGENT")
logger.setLevel(logging.DEBUG)

agent_id = 0


class Agent:
    def __init__(self, manager, base: Base, model: str):
        """
        General Agent type
        """
        # ----- Identification -----
        global agent_id
        self.agent_id = agent_id
        agent_id += 1
        self.manager = manager
        self.team = None
        self.major_category = None
        self.base = base
        self.model = model
        self.service = None

        # ----- Detection -----
        self.surface_visibility = None
        self.air_visibility = None
        self.sub_visibility = None

        self.air_detection_range: str | None = None
        self.surface_detection_range: str | None = None
        self.sub_detection_range: str | None = None

        # ----- Movement -----
        self.assigned_zone = None
        self.legal_zones = []
        self.convoy = None

        self.location = base.location
        self.displacement = None
        self.speed_current = 0
        self.speed_cruising = None
        self.speed_max = None

        self.endurance = None
        self.remaining_endurance = None
        self.movement_left_in_turn = None

        # ----- Routing -----
        self.obstacles = []
        self.route = None
        self.past_points = []
        self.remaining_points = []
        self.last_location = None
        self.next_point = None

        # ----- Combat -----
        self.engaged_in_combat = False
        self.current_health = None
        self.CTL = False

        self.located_agent = None

        self.anti_surface_weapons = []
        self.anti_air_weapons = []
        self.anti_sub_weapons = []

        self.able_to_attack = None
        self.sub_ammo_max = None
        self.surf_ammo_max = None
        self.air_ammo_max = None
        self.sub_ammo_current = None
        self.surf_ammo_current = None
        self.air_ammo_current = None
        self.air_attack_range = None
        self.surface_attack_range = None
        self.submarine_attack_range = None

        # ----- Mission Status -----
        self.mission: str | None = None
        self.trailing_agents = []
        self.guarding_agents = []
        self.support_agents = []
        self.guarding_target = None

        # ----- Agent States -----
        self.activated = False
        self.destroyed = False
        self.is_returning = False
        self.is_trailing = False
        self.is_patrolling = False

        self.maintenance_time = 24 * 3
        self.remaining_maintenance_time = 0

        # ----- Plotting -----
        self.color = None
        self.radius = None
        self.marker_type = None
        self.marker = None
        self.radius_patch = None
        self.route_plot = None

    def generate_route(self, destination: Point = None) -> None:
        """
                Creates a route from current location to a certain point, while avoiding the default list of obstacles
                provided for the agent
                :param destination: Reachable location for the agent
                :return:
                """
        try:
            self.route = create_route(point_a=self.location, point_b=destination,
                                      polygons_to_avoid=copy.deepcopy(self.obstacles))
        except ValueError:
            self.location.add_point_to_plot(constants.world.ax, color="purple")
            destination.add_point_to_plot(constants.world.ax, color="violet")
            logger.error(f"Failed to create route from {self.location} to {destination}")
        self.past_points.append(self.route.points[0])
        self.last_location = self.location
        self.next_point = self.route.points[1]
        self.remaining_points = self.route.points[2:]

    def remove_from_plot(self):
        if not constants.PLOTTING_MODE:
            return
        if self.marker is not None:
            for m in self.marker:
                m.remove()
            self.text.remove()
            self.marker = None

        if self.radius_patch is not None:
            self.radius_patch.remove()
            self.radius_patch = None

        if constants.DEBUG_MODE:
            if self.route_plot is not None:
                for lines in self.route_plot:
                    line = lines.pop(0)
                    line.remove()
                self.route_plot = None

    def update_plot(self) -> None:
        if not constants.PLOTTING_MODE:
            return

        self.remove_from_plot()

        if not self.activated:
            return

        # Re-add new plots
        if constants.DEBUG_MODE and self.route is not None:
            remaining_route = Route(points=([self.location] + [self.next_point] + self.remaining_points))
            self.route_plot = remaining_route.add_route_to_plot(constants.axes_plot, color=self.color)
            # self.route_plot = self.route.add_route_to_plot(constants.axes_plot)  # Plots entire route instead

        if self.radius is not None:
            self.radius_patch = matplotlib.patches.Circle((self.location.x, self.location.y),
                                                          radius=self.radius / constants.LATITUDE_CONVERSION_FACTOR,
                                                          color=self.color, alpha=0.1, linewidth=None)

            constants.world.ax.add_patch(self.radius_patch)
        self.marker = constants.world.ax.plot(self.location.x, self.location.y, color=self.color,
                                              marker=self.marker_type,
                                              markersize=constants.WORLD_MARKER_SIZE - 1,
                                              markeredgecolor="black")

        self.text = constants.world.ax.text(self.location.x, self.location.y - 0.001, s=str(self), color="white",
                                            fontsize=6)

    def take_turn(self) -> None:
        """
        Make the agent take the turn for the current iteration. I.e.:
        0. Check if they have the endurance to continue
        1. Calculate how much distance to travel this turn
        2. Move location based on current mission
        3. Take any actions related to the location
        :return:
        :return:
        """
        raise NotImplementedError("Not implemented on AGENT level.")

    def can_continue(self) -> bool:
        """
        See if Agent can continue current actions or has to return to resupply
        :return:
        """
        # Check heuristically - to prevent route creation for all instances
        dist_to_base = self.location.distance_to_point(self.base.location)
        required_endurance_max = (1.5 * dist_to_base)
        if required_endurance_max < self.remaining_endurance:
            return True

        base_route = create_route(self.location, self.base.location, self.obstacles)
        if self.remaining_endurance * (1 + constants.SAFETY_ENDURANCE) <= base_route.length:
            self.return_to_base()
        else:
            return True

    def activate(self, mission: str, zone: Zone = None, target: object = None):
        """
        Start executing assigned mission in assigned zone
        :param mission:
        :param zone:
        :param target:
        :return:
        """
        self.activated = True
        self.mission = mission

        if mission == missions.START_PATROL:
            self.assigned_zone = zone
            logger.debug(f"{self} starting patrol in zone {zone}")
            patrol_location = zone.sample_patrol_location(obstacles=self.obstacles)
            self.generate_route(destination=patrol_location)

        elif mission == missions.TRAIL:
            if target is None:
                raise ValueError("Trying to trail with None target")
            self.start_trailing(target)
            # self.is_trailing = True
            # self.located_agent = target
            # self.generate_route(destination=target.location)
            logger.debug(f"{self} set to target {target}")

        else:
            raise ValueError(f"Invalid mission {mission}.")

    def allowed_to_attack(self, target: object) -> bool:
        """
        Checks if agent is allowed to attack a target based on the Targeting Rules and the RoE
        :param target:
        :return:
        """
        # Check RoE
        if self.team == constants.TEAM_COALITION:
            """ Value of 1, 2, 3, 4:
            1 - Can attack in any circumstances
            2 - Can only attack aggressive units
            3 - Can only attack unmanned units
            4 - Forbidden - attacking is not allowed. """
            # First get RoE value
            c_rules = constants.coalition_rules
            c_level = constants.COALITION_SELECTED_LEVEL
            rule_level = c_rules[c_level][self.service][target.determine_current_zone()]
            if rule_level == 1:
                return True
            elif rule_level == 4:
                return False
            elif rule_level == 2:
                if target.engaged_in_combat:
                    return True
                else:
                    return False
            elif rule_level == 3:
                if target.service == "UAV":
                    return True
                else:
                    return False

        elif self.team == constants.TEAM_CHINA:
            # Check targeting rules
            t_rules = constants.targeting_rules
            allowed = t_rules[self.service][target.service]
            return allowed

        else:
            raise ValueError(f"Unknown team - {self.team}")

    def attempt_attack(self):
        pass
        # TODO:
        #  1. Check which weapon will be used
        #  2. Ensure we are in range to attack the agent
        #  3. Follow the weapons & ammunition table to roll an outcome of the attack

    def reach_and_return(self, location) -> bool:
        """
        Test if agent can travel to the target location and still return to base before endurance runs out.
        :param location: Goal location to reach
        :return:
        """
        # First check if the distance is possible without obstacles to prevent unnecessary heavier computations
        dist_to_point = self.location.distance_to_point(location)
        dist_to_base = location.distance_to_point(self.base.location)
        min_endurance_required = (dist_to_point + dist_to_base)

        if min_endurance_required * (1 + constants.SAFETY_ENDURANCE) > self.remaining_endurance:
            return False

        path_to_point = create_route(self.location, location, polygons_to_avoid=self.obstacles)
        path_to_base = create_route(location, self.base.location, polygons_to_avoid=self.obstacles)
        total_length = path_to_point.length + path_to_base.length
        endurance_required = total_length
        # See if we have enough endurance remaining, plus small penalty to ensure we can trail
        if endurance_required * (1 + constants.SAFETY_ENDURANCE) < self.remaining_endurance:
            return True
        else:
            return False

    def start_trailing(self, agent) -> None:
        """
        Make this agent start trailing the provided agent.
        :param agent: Agent to start following
        :return:
        """
        if self.is_patrolling:
            self.is_patrolling = False
        elif self.is_returning:
            logger.warning(
                f"Tried calling Agent {self} for trailing while routing to base - Continuing return to base")
            return

        self.is_trailing = True
        self.mission = missions.TRAIL
        if self in agent.trailing_agents:
            raise ValueError(f"Duplicate trailing for {self} to {agent}")
        agent.trailing_agents.append(self)
        self.located_agent = agent
        self.update_trail_route()
        logger.debug(f"{self} is now trailing {agent}")

        self.speed_current = self.speed_max

    def stop_trailing(self, reason: str, new_mission: str = missions.PATROL) -> None:
        """
        Makes the agent stop trailing any agent it is trailing.
        :param new_mission: Mission to continue with once stopped trailing
        :param reason: String describing why the trailing was aborted
        :return:
        """
        if not self.is_trailing and self.mission != missions.TRAIL:
            logger.error(f"Agent {self} was not trailing - ordered to stop trailing {self.located_agent} - "
                         f"{self.mission}")

        self.is_trailing = False
        self.mission = new_mission
        logger.debug(f"{self} stopped trailing {self.located_agent} - {reason}")

        self.speed_current = self.speed_cruising
        # print(f"Removing {self} from {self.located_agent} - {[str(a) for a in self.located_agent.trailing_agents]}")
        self.located_agent.trailing_agents.remove(self)
        self.located_agent = None

        self.release_support_agents()
        self.return_to_base()

    def stop_guarding(self):
        self.guarding_target = None
        self.return_to_base()

    def release_support_agents(self) -> None:
        """
        Any agents called in to support will stop the current mission and return to base.
        :return:
        """
        for agent in self.support_agents:
            agent.return_to_base()
        self.support_agents = []

    def return_to_base(self) -> None:
        self.mission = missions.RETURN
        self.generate_route(destination=self.base.location)

        self.assigned_zone = None

        if self.is_trailing:
            self.stop_trailing("Returning to base", new_mission=self.mission)
        self.is_returning = True
        self.is_patrolling = False

    def enter_base(self) -> None:
        logger.debug(f"{self} has entered {self.base}")
        self.is_returning = False
        self.activated = False

        self.manager.active_agents.remove(self)
        self.manager.inactive_agents.append(self)
        self.engaged_in_combat = False

        self.remove_guarding_agents()
        self.remove_trailing_agents("Reached base")
        self.entered_base_log()
        self.remove_from_plot()

        self.start_maintenance()

    def entered_base_log(self) -> None:
        """
        Logs for entering the base
        :return:
        """

    def start_maintenance(self) -> None:
        self.remaining_maintenance_time = self.maintenance_time

        if not self.CTL:
            self.base.maintenance_queue.append(self)

    def complete_maintenance(self):
        logger.debug(f"{self} completed maintenance")
        self.remaining_endurance = self.endurance
        self.air_ammo_current = self.air_ammo_max
        self.surf_ammo_current = self.sub_ammo_max
        self.sub_ammo_current = self.sub_ammo_max
        self.past_points = []

    def update_trail_route(self) -> None:
        """
        Update the agents route to route it to the located agent that it is trailing.
        :return:
        """
        if self.located_agent is not None and self.is_trailing:
            if not self.located_agent.activated:
                logger.debug(f"Agent {self} (Located {self.located_agent}) "
                             f"is forced to stop chasing {self.located_agent} left area of interest.")
                self.stop_trailing("Target Reached Safe Zone", new_mission="trail")
                return
            elif self.located_agent.destroyed:
                logger.debug(f"Agent {self} has stopped chasing {self.located_agent} - was destroyed.")
                self.stop_trailing("Target Destroyed")
                return
            # TODO: Check if this is in any of the agents legal zones rather than assigned zone
            elif not self.check_target_in_legal_zone():
                self.stop_trailing("Left area of interest")
                return

            for polygon in self.obstacles:
                if polygon.check_if_contains_point(self.located_agent.location, exclude_edges=False):
                    logger.debug(
                        f"Agent {self} is forced to stop chasing {self.located_agent} - in safe zone.")
                    self.stop_trailing("Target Entered Safe Zone")
                    return

            self.generate_route(destination=self.located_agent.location)

        elif self.guarding_target is not None and self.mission == missions.GUARDING:
            if not self.guarding_target.activated or self.guarding_target.destroyed:
                self.stop_guarding()
                return
            for polygon in self.obstacles:
                # TODO: Also make this check based on legal zones
                if polygon.check_if_contains_point(self.guarding_target.location):
                    logger.debug(f"Agent {self} is forced to stop guarding {self.guarding_target} - left allowed zone.")
                    self.stop_guarding()
                    return

            self.generate_route(destination=self.guarding_target.location)

        if constants.DEBUG_MODE:
            self.debug()

    def update_legal_zones(self):
        if "MERCHANT" in self.service:
            self.legal_zones = zones.ZONE_A
            return
        if self.team == constants.TEAM_CHINA:
            assignments = zones.zone_assignment_hunter[self.service]
        elif self.team == constants.TEAM_COALITION:
            assignments = zones.zone_assignment_coalition[self.service]
        else:
            raise ValueError(f"Invalid team {self.team}")
        self.legal_zones = [zone for zone in assignments.keys() if assignments[zone] > 0]

    def check_target_in_legal_zone(self) -> bool:
        return any([zone.check_if_agent_in_zone(self.located_agent) for zone in self.legal_zones])

    def remove_trailing_agents(self, reason: str) -> None:
        """
        Makes other agents stop trailing this agent if they were
        :param reason:
        :return:
        """
        for agent in self.trailing_agents:
            agent.stop_trailing(reason)

    def remove_guarding_agents(self, ) -> None:
        """
        Makes other agents stop guarding this agent if they were
        :return:
        """
        for agent in self.guarding_agents:
            agent.stop_guarding()

    def was_destroyed(self) -> None:
        self.activated = False
        self.manager.active_agents.remove(self)
        self.destroyed = True
        self.remove_trailing_agents("Agent Destroyed")
        self.remove_guarding_agents()
        self.remove_from_plot()
        self.destroyed_log_update()

    def check_if_in_zone(self, zone) -> bool:
        """
        Check if the Agent is in a ZONE object
        :param zone:
        :return:
        """
        if zone.polygon.check_if_contains_point(self.location):
            return True
        else:
            return False

    def determine_current_zone(self) -> Zone:
        """
        Checks if agent is in a zone going from the highest zone to the lowest zone
        (highest as in smallest, that overrules, lowest as in no zone rule)
        :return:
        """
        for zone in zones.ZONES:
            if zone.check_if_agent_in_zone(self):
                return zone

    @abstractmethod
    def reached_end_of_route(self) -> None:
        """
        Set of instructions to follow once the end of agent route is reached.
        Not provided on Agent level
        :return:
        """
        raise NotImplementedError(f"Reach end of route function not implemented for standard AGENT type.")

    @abstractmethod
    def destroyed_log_update(self) -> None:
        """
        Update written to the log and added to statistics
        :return:
        """
        raise NotImplementedError(f"Destroyed log not implemented on Agent level.")

    @abstractmethod
    def surface_detection(self) -> object | None:
        pass

    @abstractmethod
    def air_detection(self) -> object | None:
        pass

    @abstractmethod
    def sub_detection(self) -> object | None:
        pass

    def debug(self) -> None:
        """
        Checks if any rules and/or logic are violated
        :return:
        """
        for polygon in self.obstacles:
            if polygon.check_if_contains_point(P=self.location, exclude_edges=True):
                self.location.add_point_to_plot(axes=constants.axes_plot, color="yellow")
                if self.last_location is not None:
                    self.last_location.add_point_to_plot(axes=constants.axes_plot, color="purple", text="LAST")
                self.next_point.add_point_to_plot(axes=constants.axes_plot, color="red", text="NEXT")

                if self.located_agent is not None:
                    self.located_agent.location.add_point_to_plot(axes=constants.axes_plot,
                                                                  color="green", text="Current")
                    self.located_agent.next_point.add_point_to_plot(axes=constants.axes_plot,
                                                                    color="green", text="Next")
                    self.located_agent.past_points[-1].add_point_to_plot(axes=constants.axes_plot,
                                                                         color="green", text="Last")

                for p in self.past_points:
                    p.add_point_to_plot(axes=constants.axes_plot, color="black", text=p.point_id)
                if self.route is not None:
                    self.route.add_route_to_plot(axes=constants.axes_plot)
                raise PermissionError(f"Agent {self} at illegal location: \n"
                                      f"({self.location.x: .3f}, {self.location.y: .3f}). \n"
                                      f"Route is {[str(p) for p in self.route.points]} \n"
                                      f"Routing to base: {self.is_returning} \n"
                                      f"Activated? {self.activated} \n"
                                      f"next point: {self.next_point} \n"
                                      f"last point: {self.last_location} \n"
                                      f"trailing? : {self.is_trailing}. \n"
                                      f"Last location = ({self.last_location.x}, {self.last_location.y}). \n"
                                      f"this falls in polygon {[str(p) for p in polygon.points]}")
