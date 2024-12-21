import constants
from points import Point

import os
import logging
import datetime

date = datetime.date.today()
logging.basicConfig(level=logging.DEBUG, filename=os.path.join(os.getcwd(), 'logs/log_base_' + str(date) + '.log'),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%H:%M")
logger = logging.getLogger("BASE")
logger.setLevel(logging.DEBUG)


class Base:
    """
    A Harbour/Port/Dock OR an Oiler able to resupply and perform general maintenance
    """
    def __init__(self, name: str, location: Point):
        self.name = name
        self.location = location

        self.currently_served_agent = None
        self.stationed_agents = []
        self.maintenance_queue = []
        self.maintenance_prep_time = 0.1  # Time to switch maintenance from one unit to another.

        self.color = "black"

    def __str__(self):
        return self.name

    def add_to_plot(self) -> None:
        self.location.add_point_to_plot(constants.axes_plot, color=self.color, marker="8", plot_text=False,
                                        marker_edge_width=2, markersize=constants.WORLD_MARKER_SIZE - 4)

    def start_serve_next_agent(self):
        if len(self.maintenance_queue) > 0:
            self.currently_served_agent = self.maintenance_queue.pop(0)
        else:
            self.currently_served_agent = None

    def finish_maintenance_agent(self):
        logger.debug(f"Finished maintenance of {self.currently_served_agent}")
        self.currently_served_agent.complete_maintenance()
        self.start_serve_next_agent()

    def serve_agents(self):
        serving_time = constants.world.time_delta
        while serving_time > 0:
            if self.currently_served_agent is not None:
                # Either complete ship maintenance
                if self.currently_served_agent.remaining_maintenance_time <= serving_time:
                    serving_time -= self.currently_served_agent.remaining_maintenance_time
                    self.currently_served_agent.remaining_maintenance_time = 0
                    self.finish_maintenance_agent()
                # Continue part of the ship service
                else:
                    self.currently_served_agent.remaining_maintenance_time -= serving_time
                    return
            # No Ship is currently served, but queue existing
            elif self.currently_served_agent is None and len(self.maintenance_queue) > 0:
                self.start_serve_next_agent()
                serving_time -= self.maintenance_prep_time
            # Nothing to serve
            else:
                return


class Airbase(Base):
    def __init__(self, name: str, location: Point):
        super().__init__(name, location)
        self.probability = None

    def __str__(self):
        return f"Airbase {self.name} at {self.location}"


class Harbour(Base):
    def __init__(self, name: str, location: Point, probability=None):
        super().__init__(name, location)
        self.probability = probability
