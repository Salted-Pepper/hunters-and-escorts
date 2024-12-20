# ---- Debug Constants ----
axes_plot = None

ITERATION_LIMIT = 150
DEBUG_MODE = True
PLOTTING_MODE = True

RECEPTOR_PLOT_PARAMETER = "Sea States"

# ---- global access ----

sub_time_delta = None
world = None
interface = None

# ---- Naming Conventions ----

# Teams
TEAM_COALITION = 1
TEAM_CHINA = 2

# Hunter Types
HUNTER_NAVY = "CN NAVY"
HUNTER_CCG = "CCG"
HUNTER_MSA = "MSA"
HUNTER_PAFMM = "PAFMM"
HUNTER_PLAN = "PLAN SURFACE SHIPS"

HUNTER_SUBMARINE = "CN SUB"

HUNTER_MINELAYER = "MINELAYER"

HUNTER_UAV = "UAV"
HUNTER_AIRCRAFT = "CN MANNED AIRCRAFT"
HUNTER_MISSILE = "CN MISSILE"
HUNTER_TYPES = [HUNTER_CCG, HUNTER_MSA, HUNTER_PAFMM, HUNTER_SUBMARINE, HUNTER_MINELAYER,
                HUNTER_PLAN, HUNTER_UAV, HUNTER_AIRCRAFT, HUNTER_MISSILE]

# Coalition Types
MERCHANT = "MERCHANT"
COALITION_TW_MERCHANT = "TW MERCHANT"
COALITION_US_MERCHANT = "US MERCHANT"
COALITION_JP_MERCHANT = "JP MERCHANT"

COALITION_ESCORT = "COALTION ESCORT"
COALITION_TW_ESCORT = "TW ESCORT"
COALITION_US_ESCORT = "US ESCORT"
COALITION_JP_ESCORT = "JP ESCORT"

COALITION_AIRCRAFT = "COALITION AIRCRAFT"
COALITION_TW_AIRCRAFT = "TW AIRCRAFT"
COALITION_US_AIRCRAFT = "US AIRCRAFT"
COALITION_JP_AIRCRAFT = "JP AIRCRAFT"

COALITION_SUB = "COALITION SUB"
COALITION_TW_SUB = "TW SUB"
COALITION_US_SUB = "US SUB"
COALITION_JP_SUB = "JP SUB"

# Merchant types
MERCHANT_CONTAINER = "Container"
MERCHANT_BULK = "Bulk"
MERCHANT_PETROL = "Petroleum"
MERCHANT_LNG = "LNG"
MERCHANT_TYPES = [MERCHANT_CONTAINER, MERCHANT_BULK, MERCHANT_PETROL, MERCHANT_LNG]

COALITION_ALL_TYPES = [COALITION_TW_MERCHANT, COALITION_US_MERCHANT, COALITION_JP_MERCHANT,
                       COALITION_TW_ESCORT, COALITION_TW_AIRCRAFT, COALITION_TW_SUB,
                       COALITION_US_ESCORT, COALITION_US_AIRCRAFT, COALITION_US_SUB,
                       COALITION_JP_ESCORT, COALITION_JP_AIRCRAFT, COALITION_JP_SUB]
COALITION_ACTIVE_TYPES = [COALITION_TW_ESCORT, COALITION_TW_AIRCRAFT, COALITION_TW_SUB,
                          COALITION_US_ESCORT, COALITION_US_AIRCRAFT, COALITION_US_SUB,
                          COALITION_JP_ESCORT, COALITION_JP_AIRCRAFT, COALITION_JP_SUB]

TAIWAN = "Taiwan"
USA = "USA"
JAPAN = "Japan"

# World Options
CHINA_ESCALATION_LEVELS = [1, 2, 3, 4, 5]
COALITION_ESCALATION_LEVELS = [1, 2, 3, 4, 5]

CHINA_SELECTED_LEVEL = None
COALITION_SELECTED_LEVEL = None

# ---- Plotting Constants -----
WORLD_MARKER_SIZE = 6
STANDARD_ROUTE_COLOR = "red"
ROUTE_OPACITY = 0.5
RANGE_BAND_OPACITY = 0.3
MERCHANT_COLOR = "black"
TAIWAN_ESCORT_COLOR = "forestgreen"
JAPAN_ESCORT_COLOR = "white"
US_ESCORT_COLOR = "navy"
UAV_COLOR = "indianred"
CHINESE_NAVY_COLOR = "red"
RECEPTOR_COLOR = "green"

# ---- World Constants ----
WEATHER_RESAMPLING_TIME_SPLIT = 1

# ---- Flexible Scenario Settings ----
# Taiwan weekly merchants count
tw_container_ships = None
tw_bulk_ships = None
tw_petrol_ships = None
tw_lng_ships = None

# Japan weekly merchants count
jp_container_ships = None
jp_bulk_ships = None
jp_petrol_ships = None
jp_lng_ships = None

# US weekly merchants count
us_container_ships = None
us_bulk_ships = None
us_petrol_ships = None
us_lng_ships = None

# ------ SETTING DICTIONARIES ------

merchant_quantities = {country: {merchant: None for merchant in MERCHANT_TYPES}
                       for country in [TAIWAN, JAPAN, USA]}

hunter_quantities = {model: 0 for model in HUNTER_TYPES}

coalition_rules = None

targeting_rules = None

merchant_rules = {1: {'market': 'submit',
                      TAIWAN: 'evade',
                      USA: 'submit',
                      JAPAN: 'submit'},
                  2: {'market': 'submit',
                      TAIWAN: 'resist',
                      USA: 'submit',
                      JAPAN: 'submit'},
                  3: {'market': 'submit',
                      TAIWAN: 'resist',
                      USA: 'evade',
                      JAPAN: 'submit'},
                  4: {'market': 'submit',
                      TAIWAN: 'resist',
                      USA: 'resist',
                      JAPAN: 'submit'},
                  5: {'market': 'submit',
                      TAIWAN: 'resist',
                      USA: 'resist',
                      JAPAN: 'resist'}}

# Size Settings
stealth = "stealthy"
vsmall = "very small"
small = "small"
medium = "medium"
large = "large"

# ---- GEO Constants ----
EXPANSION_PARAMETER = 0.001  # Parameter to slightly extend polygons to prevent overlaps when selecting a point

LATITUDE_CONVERSION_FACTOR = 110.574
LONGITUDE_CONVERSION_FACTOR = 111.320
MIN_LAT = 110
MAX_LAT = 150

MIN_LONG = 15
MAX_LONG = 42

GRID_WIDTH = 1
GRID_HEIGHT = GRID_WIDTH

PLOT_SIZE = 7

LAT_GRID_EXTRA = 6
LONG_GRID_EXTRA = 6

# ---- Detection Parameters ----
UAV_MOVEMENT_SPLITS_P_H = 24  # (24 is at least 2 every 5 mins) Splits per hour - gets recalculated per timedelta
PATROL_LOCATIONS = 10  # Number of locations to sample and compare

K_CONSTANT = 39_633

# ---- General behavioural settings ----
SAFETY_ENDURANCE = 0.1

# ---- PERFORMANCE MEASURING ----
time_spent_creating_routes = 0
time_spent_calculating_distance = 0
time_spent_making_patrol_moves = 0
time_spent_observing_area = 0
time_spreading_pheromones = 0
time_spent_updating_trail_route = 0
time_spent_uav_route_move = 0
time_spent_checking_uav_return = 0
time_spent_depreciating_pheromones = 0
time_spent_following_route = 0
time_spent_launching_drones = 0
time_spent_selecting_receptors = 0
