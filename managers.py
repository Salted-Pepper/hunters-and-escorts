import random
import numpy as np

from abc import ABC, abstractmethod

import constants
import general_maths
import zones
from oth_scanners import OTH
from points import Point
import constants as cs
from bases import Airbase, Harbour
from agents import Agent
import model_info

from aircraft import UAV
from ships import Merchant, HunterShip, TaiwanEscort

import os
import logging
import datetime

date = datetime.date.today()
logging.basicConfig(level=logging.DEBUG, filename=os.path.join(os.getcwd(), 'logs/log_agents_' + str(date) + '.log'),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%H:%M")
logger = logging.getLogger("BASE")
logger.setLevel(logging.DEBUG)


class AgentManager:
    """
    A manager ensures that their designated subset of agents work together as intended.
    This includes ensuring the resources are spread out over time.
    Managers can also communicate with each other, but this can cause delays.
    """

    def __init__(self):
        self.team = None
        self.name = None
        self.active_agents = []
        self.inactive_agents = []
        self.destroyed_agents = []
        self.bases = []

        self.utilization_rates = {}

    @abstractmethod
    def initiate_agents(self):
        raise NotImplementedError("Initiate Agents not defined on MANAGER Level")

    @abstractmethod
    def initiate_bases(self):
        raise NotImplementedError("Initiate Bases not defined on MANAGER Level")

    def calculate_utilization_rates(self):
        """
        To be called after initializing agents and bases to calculate the utilization rates for the different models.
        Saves the results in a dictionary with the models as keys.
        :return:
        """
        # TODO: Update and test this a bit more, currently over-utilising
        # models = set([agent.model for agent in self.agents])
        #
        # for model in models:
        #     agent_of_model = [agent for agent in self.agents if agent.model == model][0]
        #     min_time_to_trail = 0.5
        #     min_time_to_travel = 600 / agent_of_model.speed
        #     self.utilization_rates[model] = 0.5 * (
        #             (agent_of_model.endurance - (2 * min_time_to_travel + min_time_to_trail)) /
        #             (agent_of_model.endurance + agent_of_model.maintenance_time))

    def custom_actions(self) -> None:
        """
        Do manager specific custom actions before the regular managing of agents as usual
        :return:
        """

    def manage_agents(self):
        """
        Main managing tool to assign agents to tasks.
        :return:
        """
        # TODO: Redo this based on assigned tasks and quantities. (Probably just activate agents within class)
        #  Needs:
        # 0. Do any custom actions
        # 1. Manage the base
        # 2. Check if we are at utilisation rate or not
        # 3. Make agents make their moves

        # 0. Do any custom actions
        self.custom_actions()

        # 1. Ensure the bases serve (maintain) the agents
        logger.debug(f"{self} serving agents")
        for base in self.bases:
            base.serve_agents()

        # 2. Ensure utilization rate is satisfied

        # 3. Make agents make their moves
        for agent in self.active_agents:
            agent.take_turn()

    def select_random_base(self) -> Harbour:
        """
        Selects a random harbour as destination for the convoy
        :return:
        """
        return random.choices(self.bases, weights=[base.probability
                                                   if base.probability is not None else 1 / len(self.bases)
                                                   for base in self.bases], k=1)[0]

    def select_mission(self) -> tuple[str, zones.Zone]:
        """
        Select mission and area for agent to go to
        :return: Mission and Zone string as tuple
        """

        if self.team == constants.TEAM_CHINA:
            # Select agent to send out
            agent = random.choice(self.inactive_agents)

            # See assignment of zones for agent type
            zone_assignment = zones.zone_assignment_hunter
            zone_probabilities = zone_assignment[agent.service]
            zone = np.random.choice(list(zone_probabilities.keys()), p=list(zone_probabilities.values()))
            return "start_patrol", zone

        elif self.team == constants.TEAM_COALITION:
            agent = random.choice(self.inactive_agents)

            # See assignment of zone for
            # TODO: Assign coalition units based on ccs.coalition_engagement_rules

        else:
            raise ValueError(f"Invalid Team {self.team}")


class OTHManager(AgentManager):
    """
    Chinese OTH Manager
    """

    def __init__(self):
        super().__init__()
        self.team = constants.TEAM_CHINA
        self.active = False

        self.initiate_bases()

    def initiate_bases(self):
        self.bases = [OTH(location=Point(112.70425, 32.33893),
                          direction_point=Point(113.70425, 31.33893),
                          manager=self),
                      OTH(location=Point(111.44, 42.73),
                          direction_point=Point(112.44, 41.73),
                          manager=self)]

    def initiate_agents(self):
        # Agents are coded as locations for the OTH.
        pass

    def manage_agents(self):
        if round(cs.world.time_of_day, 3) == 7:
            self.roll_if_active(time="AM")

        elif round(cs.world.time_of_day, 3) == 19:
            self.roll_if_active(time="PM")

        if not self.active:
            return
        for oth in self.bases:
            oth.perform_scan()

    def roll_if_active(self, time: str) -> None:
        """
        Check if the OTH are active or not for the upcoming 12h block.
        Checks are done at 7am and 7pm world time.

        At 7am, 5% that conditions are too bad - no checks
        At 7pm, 50% chance that no OTH checks are made
        :param time: String either 'AM' or 'PM'
        :return:
        """
        random_value = random.uniform(0, 1)

        if time == "AM":
            if random_value <= 0.05:
                self.active = False
            else:
                self.active = True
        elif time == "PM":
            if random_value <= 0.5:
                self.active = False
            else:
                self.active = True
        else:
            raise NotImplementedError(f"Time {time} not implemented.")

        if not self.active:
            for oth in self.active_agents:
                oth.remove_range_band_from_plot()


class UAVManager(AgentManager):
    """
    Chinese UAV Manager
    """

    def __init__(self):
        super().__init__()
        self.team = constants.TEAM_CHINA
        self.drone_types = []

        self.initiate_bases()
        self.initiate_drones()
        self.calculate_utilization_rates()

    def __str__(self):
        return "UAV Agent Manager"

    def initiate_bases(self):
        self.bases = [Airbase(name="Ningbo", location=Point(121.57, 29.92,
                                                            force_maintain=True, name="Ningbo")),
                      Airbase(name="Fuzhou", location=Point(119.31, 26.00,
                                                            force_maintain=True, name="Fuzhou")),
                      Airbase(name="Liangcheng", location=Point(116.75, 25.68,
                                                                force_maintain=True, name="Liangcheng")),
                      ]

    def initiate_drones(self):
        logger.debug("Initiating Drones...")
        for row in model_info.UAV_MODELS:
            if row['team'] == constants.TEAM_CHINA and row['type'] == "UAV":
                for _ in range(row['numberofagents']):
                    self.inactive_agents.append(UAV(manager=self,
                                                    base=self.select_random_base(),
                                                    model=row['name']))

    def custom_actions(self) -> None:
        """
        Activating agents to mission zones when underutilized
        :return:
        """
        total_agents = len(self.inactive_agents) + len(self.active_agents)
        ready_agents = [agent for agent in self.inactive_agents if agent.remaining_maintenance_time == 0]
        while len(self.active_agents) / total_agents < 0.10 and len(ready_agents):
            new_agent = random.choice(ready_agents)
            mission, zone = self.select_mission()
            new_agent.activate(mission, zone)
            self.inactive_agents.remove(new_agent)
            self.active_agents.append(new_agent)
            ready_agents.remove(new_agent)

    def send_attacker(self, target) -> None:
        agent_to_respond = self.find_uav_able_to_attack(target)
        if agent_to_respond is None:
            return

        print(f"sending out {agent_to_respond} to attack {target} - {agent_to_respond.able_to_attack=}")
        if not agent_to_respond.activated:
            self.inactive_agents.remove(agent_to_respond)
            self.active_agents.append(agent_to_respond)
            agent_to_respond.activate(mission="trail",
                                      zone=zones.ZONE_I,
                                      target=target)
        else:
            agent_to_respond.start_trailing(target)
        constants.interface.update_statistics_and_logs(event_code=None,
                                                       log=f"UAV Detected {target}, sending {agent_to_respond}")

    def find_uav_able_to_attack(self, target: Agent) -> UAV:
        close_active_agents = [agent for agent in self.active_agents if
                               agent.able_to_attack and not agent.is_returning and agent.surf_ammo_current > 0]
        # close_active_agents = sorted(close_active_agents,
        #                              key=lambda x: general_maths.calculate_distance(x.location, target.location))
        if len(close_active_agents) > 0:
            for agent in close_active_agents:
                if agent.reach_and_return(target.location):
                    return agent

        eligible_inactive_agents = [agent for agent in self.inactive_agents
                                    if agent.reach_and_return(target.location) and agent.able_to_attack
                                    and agent.remaining_maintenance_time == 0]
        if len(eligible_inactive_agents) > 0:
            return eligible_inactive_agents[0]
        else:
            return None


class CNManager(AgentManager):
    """
    Chinese Navy Manager
    """
    def __init__(self):
        super().__init__()
        self.team = constants.TEAM_CHINA
        self.name = "Chinese Navy Manager"
        self.initiate_bases()
        self.initiate_agents()

    def __str__(self):
        return self.name

    def initiate_bases(self):
        self.bases = [Harbour(name="Shenzhen", location=Point(114.390, 21.801)),
                      Harbour(name="Quanzhou", location=Point(119.039, 24.684)),
                      Harbour(name="Fuzhou", location=Point(119.994, 26.061)),
                      Harbour(name="Taizhou", location=Point(122.037, 28.231)),
                      Harbour(name="Shanghai", location=Point(122.747, 31.306)),
                      Harbour(name="Qingdao", location=Point(121.105, 35.379))]

    def initiate_agents(self):
        for row in model_info.SHIP_MODELS:
            if row['team'] == constants.TEAM_CHINA and (row['service'] == 'CCG' or row['service'] == 'MSA'):
                for _ in range(row['numberofagents']):
                    self.inactive_agents.append(HunterShip(manager=self,
                                                           base=self.select_random_base(),
                                                           model=row['name']))

    def custom_actions(self) -> None:
        """
        Activating agents to mission zones when underutilized
        :return:
        """
        # if constants.CHINA_SELECTED_LEVEL > 1:
        #     for agent in self.active_agents:
        #         agent.return_to_base()
        #     return

        total_agents = len(self.inactive_agents) + len(self.active_agents)
        ready_agents = [agent for agent in self.inactive_agents if agent.remaining_maintenance_time == 0]
        while len(self.active_agents) / total_agents < 0.3 and len(ready_agents):
            new_agent = random.choice(ready_agents)
            mission, zone = self.select_mission()
            print(f"Sending agent {new_agent} to zone {zone.name}")
            new_agent.activate(mission, zone)
            self.inactive_agents.remove(new_agent)
            self.active_agents.append(new_agent)
            ready_agents.remove(new_agent)



    def send_attacker(self, target: Agent):
        agent_to_respond = self.find_ship_able_to_attack(target)
        if not agent_to_respond.activated:
            self.inactive_agents.remove(agent_to_respond)
            self.active_agents.append(agent_to_respond)
            agent_to_respond.activate(mission="trail",
                                      zone=zones.ZONE_I,
                                      target=target)
        else:
            agent_to_respond.start_trailing(target)
        constants.interface.update_statistics_and_logs(event_code=None,
                                                       log=f"UAV Detected {target}, sending {agent_to_respond}")

    def find_ship_able_to_attack(self, target: Agent) -> HunterShip:
        close_active_agents = [agent for agent in self.active_agents if agent.able_to_attack and not agent.is_returning]
        # close_active_agents = sorted(close_active_agents,
        #                              key=lambda x: general_maths.calculate_distance(x.location, target.location))
        if len(close_active_agents) > 0:
            for agent in close_active_agents:
                if agent.reach_and_return(target.location):
                    return agent

        eligible_inactive_agents = [agent for agent in self.inactive_agents
                                    if agent.reach_and_return(target.location)]
        return eligible_inactive_agents[0]


class MerchantManager(AgentManager):
    """
    Manager for all 'neutral' Merchants
    """

    def __init__(self):
        super().__init__()
        self.team = constants.TEAM_COALITION
        self.name = "MerchantManager"
        self.initiate_bases()

        self.current_waiting_convoy = None

    def __str__(self):
        return "Merchant Manager"

    def initiate_agents(self):
        pass

    def initiate_bases(self) -> None:
        self.bases = [Harbour(name="Kaohsiung",
                              location=Point(120.30, 22.44, name="Kaohsiung", force_maintain=True),
                              probability=0.4),
                      Harbour(name="Tiachung",
                              location=Point(120.42, 24.21, name="Tiachung", force_maintain=True),
                              probability=0.3),
                      Harbour(name="Keelung",
                              location=Point(121.75, 25.19, name="Keelung", force_maintain=True),
                              probability=0.25),
                      Harbour(name="Hualien",
                              location=Point(121.70, 23.96, name="Hualien", force_maintain=True),
                              probability=0.05)
                      ]

    def custom_actions(self):
        self.generate_merchants_entering()

        for merchant in self.inactive_agents:
            if merchant.remaining_maintenance_time == 0 and not merchant.CTL:
                merchant.activated = True
                merchant.generate_route(merchant.entry_point)
                self.inactive_agents.remove(merchant)
                self.active_agents.append(merchant)

    def select_random_base(self) -> Harbour:
        """
        Selects a random harbour as destination for the convoy
        :return:
        """
        return random.choices(self.bases, weights=[base.probability
                                                   if base.probability is not None else 1 / len(self.bases)
                                                   for base in self.bases], k=1)[0]

    def generate_merchants_entering(self) -> None:
        """
        Generate the merchants entering this timestep
        :return:
        """
        option_list = []
        merchants_per_week = constants.merchant_quantities
        total_entering = 0

        for country in merchants_per_week.keys():
            for merchant_type in merchants_per_week[country]:
                number_entering = merchants_per_week[country][merchant_type]
                option_list.append([country, merchant_type, number_entering])
                total_entering += number_entering

        time_steps_per_week = (24 * 7) / constants.world.time_delta
        probability_of_entrance = total_entering / time_steps_per_week

        # If probability >1 guarantee those arrivals
        for _ in range(int(probability_of_entrance // 1)):
            self.create_new_merchant(option_list)

        # Otherwise randomly sample if we send
        if probability_of_entrance % 1 > random.uniform(0, 1):
            print(f"Creating new merchant")
            self.create_new_merchant(option_list)

    def create_new_merchant(self, option_list):
        selected_option = random.choices(option_list, weights=[option[2] for option in option_list])[0]
        country = selected_option[0]
        merchant_type = selected_option[1]
        self.active_agents.append(Merchant(manager=self,
                                           base=self.select_random_base(),
                                           country=country,
                                           model=merchant_type))


class TaiwanEscortManager(AgentManager):
    def __init__(self):
        super().__init__()
        self.team = constants.TEAM_COALITION
        self.name = "Taiwan Escort Manager"
        self.initiate_bases()
        self.initiate_agents()

    def __str__(self):
        return self.name

    def initiate_bases(self) -> None:
        self.bases = [Harbour(name="Kaohsiung",
                              location=Point(120.30, 22.44, name="Kaohsiung", force_maintain=True),
                              probability=0.4),
                      Harbour(name="Tiachung",
                              location=Point(120.42, 24.21, name="Tiachung", force_maintain=True),
                              probability=0.3),
                      Harbour(name="Keelung",
                              location=Point(121.75, 25.19, name="Keelung", force_maintain=True),
                              probability=0.25),
                      Harbour(name="Hualien",
                              location=Point(121.70, 23.96, name="Hualien", force_maintain=True),
                              probability=0.05)
                      ]

    def initiate_agents(self):
        for row in model_info.SHIP_MODELS:
            if row['team'] == 1 and row['base'] == "Taiwan":
                for _ in range(row['numberofagents']):
                    self.inactive_agents.append(TaiwanEscort(manager=self,
                                                             base=self.select_random_base(),
                                                             model=row['name']))

    def custom_actions(self):
        total_agents = len(self.inactive_agents) + len(self.active_agents)
        ready_agents = [agent for agent in self.inactive_agents if agent.remaining_maintenance_time == 0]
        while len(self.active_agents) / total_agents < 0.03 and len(ready_agents):
            new_agent = random.choice(ready_agents)
            mission, zone = self.select_mission()
            new_agent.activate(mission, zone)
            self.inactive_agents.remove(new_agent)
            self.active_agents.append(new_agent)
            ready_agents.remove(new_agent)

        # Send to liberate any captured Merchants
        if constants.COALITION_SELECTED_LEVEL > 1:
            for merchant in constants.world.MerchantManager.active_agents:
                if merchant.is_boarded and not zones.ZONE_L.check_if_agent_in_zone(merchant):
                    escort = self.find_ship_able_to_liberate(merchant)
                    escort.start_trailing(merchant)

    def find_ship_able_to_liberate(self, target: Agent) -> TaiwanEscort:
        close_active_agents = [agent for agent in self.active_agents if
                               agent.able_to_attack and not agent.is_returning]
        # close_active_agents = sorted(close_active_agents,
        #                              key=lambda x: general_maths.calculate_distance(x.location, target.location))
        for agent in close_active_agents:
            if agent.reach_and_return(target.location):
                return agent

        eligible_inactive_agents = [agent for agent in self.inactive_agents
                                    if agent.reach_and_return(target.location)]
        if len(eligible_inactive_agents) > 0:
            return eligible_inactive_agents[0]
