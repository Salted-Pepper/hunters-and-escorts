import numpy as np
import matplotlib.pyplot as plt

import constants as cs
import constant_coords
import zones
from polygons import Polygon
from receptors import ReceptorGrid
import weather_data

from managers import (MerchantManager, CNManager, TaiwanEscortManager, JapanEscortManager, USAEscortManager,
                      UAVManager, OTHManager)

# Logging
import datetime
import logging
import os

if not os.path.exists("logs"):
    os.makedirs("logs")

date = datetime.date.today()

logging.basicConfig(level=logging.DEBUG, filename=os.path.join(os.getcwd(), 'logs/navy_log_' + str(date) + '.log'),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%H:%M:%S", filemode='w')
logger = logging.getLogger("WORLD")
logger.setLevel(logging.DEBUG)

logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)
logging.getLogger("PIL.PngImagePlugin").setLevel(logging.WARNING)
logging.getLogger("fiona.ogrext").setLevel(logging.WARNING)
logging.getLogger("GEOPOLYGON").setLevel(logging.WARNING)


class World:
    def __init__(self, time_delta: float, coalition_level: int, china_level: int):
        cs.world = self
        # Time Management
        self.time_delta = time_delta
        self.sub_time_delta = int(np.ceil(cs.UAV_MOVEMENT_SPLITS_P_H * self.time_delta))
        self.world_time = 0
        self.time_of_day = 0
        self.time_last_weather_update = 0

        # Geography
        self.landmasses = []
        self.zones = []
        self.china_polygon = None
        self.initiate_land_masses()
        self.initiate_zones()

        # Data Management Through Receptors
        self.receptor_grid = None
        self.initiate_receptor_grid()

        # World Player Input Fixed Parameters
        self.coalition_escalation_level = coalition_level
        self.china_escalation_level = china_level

        # ---- World Player Input Fixed Parameters ----
        # Taiwan weekly merchants count
        self.tw_container_ships = None
        self.tw_bulk_ships = None
        self.tw_petrol_ships = None
        self.tw_lng_ships = None

        # Japan weekly merchants count
        self.jp_container_ships = None
        self.jp_bulk_ships = None
        self.jp_petrol_ships = None
        self.jp_lng_ships = None

        # US weekly merchants count
        self.us_container_ships = None
        self.us_bulk_ships = None
        self.us_petrol_ships = None
        self.us_lng_ships = None
        # ----------------------------------------------

        # ----- Managers -----
        self.MerchantManager = MerchantManager()
        self.OTHManager = OTHManager()
        self.CNManager = CNManager()
        self.TaiwanEscortManager = TaiwanEscortManager()
        self.JapanEscortManager = JapanEscortManager()
        self.USAEscortManager = USAEscortManager()
        self.UAVManager = UAVManager()
        self.managers = [self.MerchantManager,
                         self.OTHManager,
                         self.CNManager,
                         self.TaiwanEscortManager,
                         self.JapanEscortManager,
                         self.USAEscortManager,
                         self.UAVManager]

        # Plotting
        self.fig = None
        self.ax = None
        self.plot_world(True)

    def initiate_land_masses(self) -> None:
        self.landmasses = zones.TAIWAN_AND_ISLANDS + zones.JAPAN_AND_ISLANDS + zones.OTHER_LAND

        self.china_polygon = zones.CHINA

    def initiate_zones(self) -> None:
        pass

    def initiate_receptor_grid(self):
        self.receptor_grid = ReceptorGrid(self.landmasses + [self.china_polygon], self)

    def plot_world(self, include_receptors=False) -> None:
        if not cs.PLOTTING_MODE and not cs.DEBUG_MODE:
            return
        self.fig, self.ax = plt.subplots(1, figsize=(cs.PLOT_SIZE, cs.PLOT_SIZE))
        cs.axes_plot = self.ax
        self.ax.set_title(f"Sea Map - time is {self.world_time}")
        self.ax.set_facecolor("#2596be")
        self.ax.set_xlim(left=cs.MIN_LAT, right=cs.MAX_LAT)
        self.ax.set_xlabel("Latitude")
        self.ax.set_ylim(bottom=cs.MIN_LONG, top=cs.MAX_LONG)
        self.ax.set_ylabel("Longitude")

        for landmass in self.landmasses:
            logging.debug(f"Plotting {landmass}")
            self.ax = landmass.add_polygon_to_plot(self.ax)

        self.ax = self.china_polygon.add_polygon_to_plot(self.ax)

        for manager in self.managers:
            for base in manager.bases:
                base.add_to_plot()

        if include_receptors:
            for receptor in self.receptor_grid.receptors:
                self.ax = receptor.initiate_plot(self.ax, self.receptor_grid.cmap)

        plt.show()
        self.fig.canvas.draw()

    def plot_world_update(self) -> None:
        if not cs.PLOTTING_MODE:
            return

        self.ax.set_title(f"Sea Map - time is {self.world_time: .3f}")

        for receptor in self.receptor_grid.receptors:
            receptor.update_plot(self.ax, self.receptor_grid.cmap)

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.show()

    def update_weather_conditions(self):
        """
        Updates the weather and samples sea states pending.
        :return:
        """
        if self.world_time - self.time_last_weather_update > cs.WEATHER_RESAMPLING_TIME_SPLIT:
            logger.debug("Updating weather...")
            self.time_last_weather_update = self.world_time
            weather_data.update_sea_states(self)
            return

    def time_step(self) -> None:
        print(f"Starting iteration {self.world_time: .3f}")
        self.world_time += self.time_delta
        self.time_of_day = self.world_time % 24

        self.update_weather_conditions()

        for manager in self.managers:
            logger.debug(f"{manager} is working...")
            manager.manage_agents()

        self.receptor_grid.depreciate_pheromones()

        self.plot_world_update()

        logger.debug(f"End of iteration {self.world_time: .3f} \n")

