from interface import Interface
from world import World
import constants as cs

# Zone Constants and Limits
zones = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
escalation_level = [1, 2, 3, 4, 5]

# Merchant rules with escalation level key, then type of merchant and action

hunter_targeting = {hunter: {target: False for target in cs.COALITION_ALL_TYPES} for hunter in cs.HUNTER_TYPES}


class Game:
    def __init__(self):
        # Fixed Scenario Settings
        self.world = None
        self.time_delta = None
        self.coalition_escalation_level = None
        self.china_escalation_level = None

        # ---- Rules Information Dictionaries ----
        self.escort_rules_of_engagement = None

        self.interface = Interface(self)
        self.interface.mainloop()

    def create_world(self):
        self.world = World(self.time_delta, self.coalition_escalation_level, self.china_escalation_level)

    def initiate_rules_of_engagement(self, entry_info: dict[dict]):
        """
        Updates the escort_rules_of_engagement to a nested dictionary containing:
        Key for country
        Key for zone
        Value for Rule of Engagements
        Based on the entered values in the panel
        :return:
        """
        self.escort_rules_of_engagement = entry_info
