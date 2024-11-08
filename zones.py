import random

import constants
from polygons import Polygon
from points import Point
import constants as cs
import constant_coords as ccs

# Forbidden zones are one of 'none', 'territorial' (C, E, G), 'semi-territorial' (E, G), or 'all' (A)
china_forbidden_zones = {'Level 1': {'CCG': 'territorial',
                                     'MSA': 'territorial',
                                     'PAFMM': 'territorial',
                                     'submarine': 'all',
                                     'minelayer': 'all',
                                     'PLAN': 'all',
                                     'uav_armed': 'territorial',
                                     'uav_unarmed': 'territorial',
                                     'planes_armed': 'all',
                                     'planes_unarmed': 'territorial',
                                     'missiles': 'all'},
                         'Level 2': {'CCG': 'territorial',
                                     'MSA': 'territorial',
                                     'PAFMM': 'territorial',
                                     'submarine': 'none',
                                     'minelayer': 'none',
                                     'PLAN': 'all',
                                     'uav_armed': 'territorial',
                                     'uav_unarmed': 'territorial',
                                     'planes_armed': 'all',
                                     'planes_unarmed': 'territorial',
                                     'missiles': 'all'},
                         'Level 3': {'CCG': 'territorial',
                                     'MSA': 'territorial',
                                     'PAFMM': 'territorial',
                                     'submarine': 'none',
                                     'minelayer': 'none',
                                     'PLAN': 'territorial',
                                     'uav_armed': 'territorial',
                                     'uav_unarmed': 'territorial',
                                     'planes_armed': 'territorial',
                                     'planes_unarmed': 'territorial',
                                     'missiles': 'territorial'},
                         'Level 4': {'CCG': 'semi-territorial',
                                     'MSA': 'semi-territorial',
                                     'PAFMM': 'semi-territorial',
                                     'submarine': 'none',
                                     'minelayer': 'none',
                                     'PLAN': 'semi-territorial',
                                     'uav_armed': 'semi-territorial',
                                     'uav_unarmed': 'semi-territorial',
                                     'planes_armed': 'semi-territorial',
                                     'planes_unarmed': 'semi-territorial',
                                     'missiles': 'semi-territorial'},
                         'Level 5': {'CCG': 'none',
                                     'MSA': 'none',
                                     'PAFMM': 'none',
                                     'submarine': 'none',
                                     'minelayer': 'none',
                                     'PLAN': 'none',
                                     'uav_armed': 'none',
                                     'uav_unarmed': 'none',
                                     'planes_armed': 'none',
                                     'planes_unarmed': 'none',
                                     'missiles': 'none'},
                         }

# Landmasses
TAIWAN_LAND = Polygon(name="taiwan", points=ccs.TAIWAN_POINTS,
                      color=ccs.TAIWAN_COLOR)
ORCHID = Polygon(name="orchid_island", points=ccs.ORCHID_ISLAND_POINTS,
                 color=ccs.TAIWAN_COLOR)
GREEN_ISLAND = Polygon(name="green_island", points=ccs.GREEN_ISLAND_POINTS,
                       color=ccs.TAIWAN_COLOR)
PENGHU = Polygon(name="penghu", points=ccs.PENGHU_COUNTRY_POINTS,
                 color=ccs.TAIWAN_COLOR)
WANGAN = Polygon(name="wangan", points=ccs.WANGAN_POINTS,
                 color=ccs.TAIWAN_COLOR)
QIMEI = Polygon(name="qimei", points=ccs.QIMEI_POINTS,
                color=ccs.TAIWAN_COLOR)
TAIWAN_AND_ISLANDS = [TAIWAN_LAND, ORCHID, GREEN_ISLAND, PENGHU, WANGAN, QIMEI]

YONAGUNI = Polygon(name="yonaguni", points=ccs.YONAGUNI_POINTS,
                   color=ccs.JAPAN_COLOR)
TAKETOMI = Polygon(name="taketomi", points=ccs.TAKETOMI_POINTS,
                   color=ccs.JAPAN_COLOR)
ISHIGAKI = Polygon(name="ishigaki", points=ccs.ISHIGAKE_POINTS,
                   color=ccs.JAPAN_COLOR)
MIYAKOJIMA = Polygon(name="miyakojima", points=ccs.MIYAKOJIMA_POINTS,
                     color=ccs.JAPAN_COLOR)
OKINAWA = Polygon(name="okinawa", points=ccs.OKINAWA_POINTS,
                  color=ccs.JAPAN_COLOR)
OKINOERABUJIMA = Polygon(name="okinoerabujima",
                         points=ccs.OKINOERABUJIMA_POINTS,
                         color=ccs.JAPAN_COLOR)
TOKUNOSHIMA = Polygon(name="tokunoshima", points=ccs.TOKUNOSHIMA_POINTS,
                      color=ccs.JAPAN_COLOR)
AMAMI = Polygon(name="amami_oshima", points=ccs.AMAMI_OSHIMA_POINTS,
                color=ccs.JAPAN_COLOR)
YAKUSHIMA = Polygon(name="yakushima", points=ccs.YAKUSHIMA_POINTS,
                    color=ccs.JAPAN_COLOR)
TANEGASHIMA = Polygon(name="tanegashima", points=ccs.TANEGASHIMA_POINTS,
                      color=ccs.JAPAN_COLOR)
JAPAN_LAND = Polygon(name="japan", points=ccs.JAPAN_POINTS,
                     color=ccs.JAPAN_COLOR)

JAPAN_AND_ISLANDS = [YONAGUNI, TAKETOMI, ISHIGAKI, MIYAKOJIMA, OKINAWA, OKINOERABUJIMA, TOKUNOSHIMA,
                     AMAMI, YAKUSHIMA, TANEGASHIMA, JAPAN_LAND]

KOREA = Polygon(name="korea", points=ccs.KOREA_POINTS,
                color=ccs.OTHER_COLOR)
JEJUDO = Polygon(name="jejudo", points=ccs.JEJUDO_POINTS,
                 color=ccs.OTHER_COLOR)
PHILIPPINES = Polygon(name="philippines", points=ccs.PHILIPPINES_POINTS,
                      color=ccs.OTHER_COLOR)
OTHER_LAND = [KOREA, JEJUDO, PHILIPPINES]

CHINA = Polygon(name="china", points=ccs.CHINA_POINTS,
                color=ccs.CHINA_COLOR)


class Zone:
    def __init__(self, name: str, polygon: Polygon):
        self.name = name
        self.polygon = polygon

    def check_if_agent_in_zone(self, agent) -> bool:
        return self.polygon.check_if_contains_point(agent.location)

    def sample_patrol_location(self, obstacles=None):
        valid_point = False

        attempts = 0
        while not valid_point:
            attempts += 1
            if attempts >= constants.ITERATION_LIMIT:
                raise TimeoutError(f"Unable to sample patrol location in {self.name} - {[obs.name for obs in obstacles]}")
            sample_point = Point(x=random.uniform(self.polygon.min_x, self.polygon.max_x),
                                 y=random.uniform(self.polygon.min_y,
                                                  max(self.polygon.min_y + 1, min(40, self.polygon.max_y)))
                                 )
            if (self.polygon.check_if_contains_point(sample_point, exclude_edges=False) and
                    not any([obstacle.check_if_contains_point(sample_point, exclude_edges=False)
                             for obstacle in obstacles])):
                return sample_point


# Zones
ZONE_A = Zone(name="A - All Zones", polygon=Polygon(points=ccs.A_ALL_ZONES))
ZONE_B = Zone(name="B - TAIWAN Contiguous", polygon=Polygon(ccs.B_TAIWAN_CONT))
ZONE_C = Zone(name="C - TAIWAN Territorial", polygon=Polygon(ccs.C_TAIWAN_TERRITORIAL))
ZONE_D = Zone(name="D - JAPAN Contiguous", polygon=Polygon(ccs.D_JAPAN_CONT))
ZONE_E = Zone(name="E - JAPAN Territorial", polygon=Polygon(ccs.E_JAPAN_TERRITORIAL))
ZONE_F = Zone(name="F - FP Contiguous", polygon=Polygon(ccs.F_FILIPINO_CONT))
ZONE_G = Zone(name="G - FP Territorial", polygon=Polygon(ccs.G_FILIPINO_TERRITORIAL))
ZONE_H = Zone(name="H - Out CN 10 DASH", polygon=Polygon(ccs.H_OUTSIDE_10_DASH))
ZONE_I = Zone(name="I - In CN 10 DASH", polygon=Polygon(ccs.I_INSIDE_10_DASH))
ZONE_L = Zone(name="L - Inside Median Line", polygon=Polygon(ccs.L_INSIDE_MEDIAN_LINE))
# Sort zones from top zones to lower zones
ZONES = [ZONE_C, ZONE_B, ZONE_E, ZONE_D, ZONE_G, ZONE_F, ZONE_I, ZONE_L, ZONE_H, ZONE_A]
HUNTER_ILLEGAL_ZONES = JAPAN_AND_ISLANDS + [ZONE_B.polygon, ZONE_C.polygon]
COALITION_ILLEGAL_ZONES = [CHINA]

NAVY_ILLEGAL_ZONES = JAPAN_AND_ISLANDS + [CHINA] + OTHER_LAND

# Nested Dictionary of - Key: Escalation Level - Key: Country - Key: Zone - Value: maximum rule
coalition_maxima = {1: {cs.TAIWAN: {ZONE_A.name: 4, ZONE_B.name: 2, ZONE_C.name: 1, ZONE_D.name: 4, ZONE_E.name: 4,
                                    ZONE_F.name: 4, ZONE_G.name: 4, ZONE_H.name: 2, ZONE_I.name: 4, ZONE_L.name: 4},
                        cs.USA: {ZONE_A.name: 4, ZONE_B.name: 4, ZONE_C.name: 4, ZONE_D.name: 4, ZONE_E.name: 4,
                                 ZONE_F.name: 4, ZONE_G.name: 4, ZONE_H.name: 4, ZONE_I.name: 4, ZONE_L.name: 4},
                        cs.JAPAN: {ZONE_A.name: 4, ZONE_B.name: 4, ZONE_C.name: 4, ZONE_D.name: 2, ZONE_E.name: 1,
                                   ZONE_F.name: 4, ZONE_G.name: 4, ZONE_H.name: 4, ZONE_I.name: 4, ZONE_L.name: 4}},

                    2: {cs.TAIWAN: {ZONE_A.name: 4, ZONE_B.name: 2, ZONE_C.name: 1, ZONE_D.name: 4, ZONE_E.name: 4,
                                    ZONE_F.name: 4, ZONE_G.name: 4, ZONE_H.name: 2, ZONE_I.name: 1, ZONE_L.name: 4},
                        cs.USA: {ZONE_A.name: 4, ZONE_B.name: 4, ZONE_C.name: 4, ZONE_D.name: 4, ZONE_E.name: 4,
                                 ZONE_F.name: 4, ZONE_G.name: 4, ZONE_H.name: 4, ZONE_I.name: 4, ZONE_L.name: 4},
                        cs.JAPAN: {ZONE_A.name: 4, ZONE_B.name: 4, ZONE_C.name: 4, ZONE_D.name: 2, ZONE_E.name: 1,
                                   ZONE_F.name: 4, ZONE_G.name: 4, ZONE_H.name: 4, ZONE_I.name: 4, ZONE_L.name: 4}},

                    3: {cs.TAIWAN: {ZONE_A.name: 1, ZONE_B.name: 1, ZONE_C.name: 1, ZONE_D.name: 1, ZONE_E.name: 2,
                                    ZONE_F.name: 1, ZONE_G.name: 2, ZONE_H.name: 1, ZONE_I.name: 1, ZONE_L.name: 4},
                        cs.USA: {ZONE_A.name: 2, ZONE_B.name: 2, ZONE_C.name: 1, ZONE_D.name: 2, ZONE_E.name: 2,
                                 ZONE_F.name: 2, ZONE_G.name: 2, ZONE_H.name: 2, ZONE_I.name: 2, ZONE_L.name: 4},
                        cs.JAPAN: {ZONE_A.name: 4, ZONE_B.name: 4, ZONE_C.name: 4, ZONE_D.name: 2, ZONE_E.name: 1,
                                   ZONE_F.name: 4, ZONE_G.name: 4, ZONE_H.name: 4, ZONE_I.name: 4, ZONE_L.name: 4}},

                    4: {cs.TAIWAN: {ZONE_A.name: 1, ZONE_B.name: 1, ZONE_C.name: 1, ZONE_D.name: 1, ZONE_E.name: 1,
                                    ZONE_F.name: 1, ZONE_G.name: 1, ZONE_H.name: 1, ZONE_I.name: 1, ZONE_L.name: 4},
                        cs.USA: {ZONE_A.name: 1, ZONE_B.name: 1, ZONE_C.name: 1, ZONE_D.name: 2, ZONE_E.name: 1,
                                 ZONE_F.name: 2, ZONE_G.name: 1, ZONE_H.name: 2, ZONE_I.name: 2, ZONE_L.name: 4},
                        cs.JAPAN: {ZONE_A.name: 2, ZONE_B.name: 2, ZONE_C.name: 2, ZONE_D.name: 1, ZONE_E.name: 1,
                                   ZONE_F.name: 4, ZONE_G.name: 4, ZONE_H.name: 2, ZONE_I.name: 2, ZONE_L.name: 4}},

                    5: {cs.TAIWAN: {ZONE_A.name: 1, ZONE_B.name: 1, ZONE_C.name: 1, ZONE_D.name: 1, ZONE_E.name: 1,
                                    ZONE_F.name: 1, ZONE_G.name: 1, ZONE_H.name: 1, ZONE_I.name: 1, ZONE_L.name: 1},
                        cs.USA: {ZONE_A.name: 1, ZONE_B.name: 1, ZONE_C.name: 1, ZONE_D.name: 1, ZONE_E.name: 1,
                                 ZONE_F.name: 1, ZONE_G.name: 1, ZONE_H.name: 1, ZONE_I.name: 1, ZONE_L.name: 1},
                        cs.JAPAN: {ZONE_A.name: 1, ZONE_B.name: 1, ZONE_C.name: 1, ZONE_D.name: 1, ZONE_E.name: 1,
                                   ZONE_F.name: 4, ZONE_G.name: 2, ZONE_H.name: 1, ZONE_I.name: 1, ZONE_L.name: 1}}
                    }

coalition_rules = coalition_maxima.copy()

zone_assignment_hunter = {agent: {zone: 0 for zone in ZONES} for agent in cs.HUNTER_TYPES}
zone_assignment_coalition = {agent: {zone: 0 for zone in ZONES} for agent in cs.COALITION_ACTIVE_TYPES}

