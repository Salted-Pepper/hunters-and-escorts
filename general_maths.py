import math
import constants

import time
import shapely.geometry

# ----------------------------------------------- LOGGER SET UP ------------------------------------------------
import logging
import datetime
import os

date = datetime.date.today()
logging.basicConfig(level=logging.DEBUG, filename=os.path.join(os.getcwd(), 'logs/gm_navy_log_' + str(date) + '.log'),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%H:%M:%S")
logger = logging.getLogger("GM")
logger.setLevel(logging.DEBUG)


# --------------------------------------------- END LOGGER SET UP ------------------------------------------------

def calculate_distance(a: object, b: object, lon_lat_to_km=True) -> float:
    """
    Calculates Euclidean distance
    :param a: Point
    :param b: Point
    :param lon_lat_to_km: bool, whether distance translated from lon_lat
    :return: Float distance
    """
    t_0 = time.perf_counter()

    if lon_lat_to_km:
        latitudinal_distance_in_km = longitudinal_distance_to_km(a.y, b.y)
        mean_latitude = (a.y + b.y) / 2
        longitudinal_distance_in_km = latitudinal_distance_to_km(a.x, b.x, mean_latitude)
        distance = math.sqrt(latitudinal_distance_in_km ** 2 + longitudinal_distance_in_km ** 2)
    else:
        distance = math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

    t_1 = time.perf_counter()
    constants.time_spent_calculating_distance += (t_1 - t_0)
    return distance


def longitudinal_distance_to_km(lon_1: float, lon_2: float) -> float:
    return abs((lon_1 - lon_2) * constants.LATITUDE_CONVERSION_FACTOR)


def latitudinal_distance_to_km(lat_1: float, lat_2: float, approx_long: float) -> float:
    return abs((lat_1 - lat_2) * (constants.LONGITUDE_CONVERSION_FACTOR *
                                  math.cos(math.radians(approx_long))))


def km_to_longitudinal_distance(kilometers: float) -> float:
    """
    Takes kilometers distance and converts it to approximate longitudinal points
    :param kilometers:
    :return:
    """
    return kilometers / constants.LATITUDE_CONVERSION_FACTOR


def km_to_latitudinal_distance(kilometers: float, approx_long) -> float:
    """
    Takes kilometer distance and converts it to approximate latitudinal points
    :param kilometers:
    :param approx_long:
    :return:
    """
    return kilometers / (constants.LONGITUDE_CONVERSION_FACTOR *
                         math.cos(math.radians(approx_long)))


def is_between_points(a: object, b: object, tested_point: object) -> bool:
    """
    :param a: Point
    :param b: Point
    :param tested_point: Point
    :return:
    """
    cross_product = (tested_point.y - a.y) * (b.x - a.x) - (tested_point.x - a.x) * (b.y - a.y)

    if abs(cross_product) > 0.001:
        return False

    dot_product = (tested_point.x - a.x) * (b.x - a.x) + (tested_point.y - a.y) * (b.y - a.y)
    if dot_product < 0:
        return False

    squaredlengthba = (b.x - a.x) * (b.x - a.x) + (b.y - a.y) * (b.y - a.y)
    if dot_product > squaredlengthba:
        return False

    return True


def orientation(p: object, q: object, r: object) -> int:
    """
    Return numerical orientation
    1 for clockwise
    -1 for counter-clockwise
    0 for collinear
    :param p: Point
    :param q: Point
    :param r: Point
    :return:
    """
    val = ccw(p, q, r)
    if val > 0:
        return 1
    elif val < 0:
        return -1
    else:
        return 0


def ccw(a: object, b: object, c: object) -> float:
    """
    See if going from point b to c is counterclockwise after moving from a to b
    :param a: Point
    :param b: Point
    :param c: Point
    :return:
    """
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)


def next_point_ccw(a: object, b: object, c: object) -> bool:
    """
    Checks if going from point b to c is clockwise or counterclockwise in reference to the line a to b
    :param a: Point
    :param b: Point
    :param c: Point
    :return:
    """
    area = ccw(a, b, c)
    if area < 0:
        return False
    elif area > 0:
        return True
    else:  # Not including collinear points
        return False


def shared_segment(p: object, q: object, r: object) -> bool:
    """
    See if two vectors p->r and q->r have a shared segment
    :param p: Point
    :param q: Point
    :param r: Point
    :return:
    """
    if max(p.x, r.x) >= q.x >= min(p.x, r.x) and max(p.y, r.y) >= q.y >= min(p.y, r.y):
        return True
    else:
        return False


def do_intersect(p1: object, q1: object, p2: object, q2: object) -> bool:
    """
    Check intersection from line p1->q1 and line p2->q2
    :param p1: Point - Start point line 1
    :param q1: Point - End point line 1
    :param p2: Point - Start point line 2
    :param q2: Point - End point line 2
    :return:
    """
    o_1 = orientation(p1, q1, p2)
    o_2 = orientation(p1, q1, q2)
    o_3 = orientation(p2, q2, p1)
    o_4 = orientation(p2, q2, q1)

    # General Case
    if o_1 != o_2 and o_3 != o_4:
        return True
    # Collinear Cases
    elif o_1 == 0 and shared_segment(p1, p2, q1):
        return True
    elif o_2 == 0 and shared_segment(p1, q2, q1):
        return True
    elif o_3 == 0 and shared_segment(p2, p1, q2):
        return True
    elif o_4 == 0 and shared_segment(p2, q1, q2):
        return True
    else:
        return False


def check_if_path_and_polygon_intersect(polygon_line: list, path_line: list, except_end_points=True) -> bool:
    """
    Check if a polygon and a path line intersect.
    The path line endpoints are allowed to be on the polygon_line, but the reverse is not allowed.
    :param except_end_points: Include or except endpoints in the check
    :param polygon_line:
    :param path_line:
    :return:
    """

    geo_path_line = shapely.geometry.LineString([[path_line[0].x, path_line[0].y], [path_line[1].x, path_line[1].y]])
    geo_poly_line = shapely.geometry.LineString([[polygon_line[0].x, polygon_line[0].y],
                                                 [polygon_line[1].x, polygon_line[1].y]])
    if except_end_points:
        # Except if the line shares an endpoint - passing through 2 points on the polygon is handled in the polygon
        if (path_line[0] == polygon_line[0]
                or path_line[1] == polygon_line[0]
                or path_line[0] == polygon_line[1]
                or path_line[1] == polygon_line[1]):
            return False
        # case if point is exactly on the line
        elif (check_if_point_on_line(point=shapely.geometry.Point(path_line[0].x, path_line[0].y),
                                     line=geo_poly_line)
              or check_if_point_on_line(point=shapely.geometry.Point(path_line[1].x, path_line[1].y),
                                        line=geo_poly_line)):
            return False
    intersect = geo_path_line.intersects(geo_poly_line)
    return intersect


def check_if_point_on_line(point, line):
    if isinstance(line, list):
        line = shapely.geometry.LineString([[line[0].x, line[0].y], [line[1].x, line[1].y]])
    if not isinstance(point, shapely.Point):
        point = shapely.geometry.Point(point.x, point.y)

    if line.distance(point) < 1e-8:
        return True
    else:
        return False


def maximize_concavity(path: list, polygons: list) -> list:
    """
    Check if some parts of the provided route is concave - See if we can remove points inbetween
    without violating any polygons and retaining required points
    :param path: list of points across which is travelled
    :param polygons:
    :return:
    """
    # logger.debug(f"Maximizing concavity for path {[str(p) for p in path]}")
    shorter_route = [path[0]]

    i = 0
    j = len(path) - 1

    iterations = 0

    while i < len(path):
        p_i = path[i]
        # logger.debug(f"{i=}, {str(p_i)=}, {j=}, {len(path)=}")
        iterations += 1
        if iterations > constants.ITERATION_LIMIT:
            raise TimeoutError("Concavity Optimization Not Converging.")

        # Otherwise take j the furthest away
        # if not maintain_point:
        p_j = path[j]
        # logger.debug(f"Taking furthest point {str(p_j)}")

        i_to_j = not any([polygon.check_if_line_through_polygon(p_i, p_j) for polygon in polygons])
        if j == len(path) - 1 and i_to_j:
            shorter_route.append(path[-1])

            # logger.debug(f"Able to reach end of path going from {p_i} to {path[-1]} - returning"
            #              f"{[str(p) for p in shorter_route]}")
            return shorter_route

        # if we can't go further than 1 step, make that step (we know it is feasible)
        if j == i + 1:
            shorter_route.append(path[j])
            i = j
            j = len(path) - 1
            # logger.debug(f"Can't make more than one step, going from {p_i} to {p_j}")
            continue

        if i_to_j:
            shorter_route.append(p_j)
            i = j
            j = len(path) - 1
            # logger.debug(f"Going from {p_i} to {p_j} (latest feasible option)")
        else:
            j -= 1
            # logger.debug(f"Not feasible - reducing j")


def calculate_direction_vector(point_a: object, point_b: object) -> list:
    """
    Calculates the normalized direction vector from point a to point b
    :param point_a: point of departure
    :param point_b: point of arrival
    :return:
    """
    if point_a is point_b:
        raise ValueError(f"Traversing between same points: {point_a}")
    normalisation_value = math.sqrt((point_b.x - point_a.x) ** 2 + (point_b.y - point_a.y) ** 2)
    if normalisation_value == 0:
        logger.warning(f"Normalisation value of 0 - direction from {str(point_a)} to {str(point_b)}")

        return [0, 0]
    x_change = (point_b.x - point_a.x) / normalisation_value
    y_change = (point_b.y - point_a.y) / normalisation_value

    return [x_change, y_change]


def find_lowest_point_in_polygon(points: list) -> object:
    return min(points, key=lambda p: p.y)


def calculate_polar_angle(a: object, b: object) -> float:
    """
    calculate polar angle between two points
    :param a: First Point
    :param b: Point relative to first
    :return:
    """
    return math.degrees(math.atan2(b.y - a.y, b.x - a.x))


def graham_scan(points: list) -> list:
    """
    Applies Graham Scan algorithm to make a convex hull out of a set of points.
    An exception is when the graham scan receives points with "force_maintain" characteristics
    This will create a non-convex hull that ensures that these points are contained
    :param points: List of Points objects
    :return:
    """
    # logger.debug("STARTING GRAHAM SCAN")
    # logger.debug(f"Received points: {[str(point) for point in points]}")

    starting_point = find_lowest_point_in_polygon(points)
    points.remove(starting_point)

    points.sort(key=lambda p: calculate_polar_angle(starting_point, p))
    convex_hull = [starting_point, points.pop(0)]

    for index, point in enumerate(points):
        if index > len(points):
            pass
        elif index == len(points):
            if next_point_ccw(convex_hull[-2], convex_hull[-1], starting_point):
                pass
            else:
                convex_hull.pop()
            convex_hull.append(point)
        else:
            if len(convex_hull) > 2:
                iterations = 0
                while not next_point_ccw(convex_hull[-2], convex_hull[-1], point):

                    iterations += 1
                    if iterations > constants.ITERATION_LIMIT:
                        TimeoutError(f"Unable to locate next CCW point: {convex_hull}")

                    if len(convex_hull) > 0:
                        convex_hull.pop()
            convex_hull.append(point)
    return convex_hull


def find_closest_reachable_point(target: object, polygon: object) -> object:
    """
    :param target: Point - Location from which we want to reach to a polygon
    :param polygon: Nearby Polygon object
    :return:
    """
    # logger.debug(f"Finding closest point - polygon is {[str(p) for p in polygon.points]}")
    distances = []
    for p in polygon.points:
        obstructed = polygon.check_if_line_through_polygon(p, target)
        if not obstructed:
            distances.append([p, target.distance_to_point(p)])
        else:
            # logger.debug(f"Unable to reach {p} from {target}.")
            pass

    if len(distances) == 0:
        target.add_point_to_plot(axes=constants.axes_plot, color="yellow", text="T")
        raise ValueError(f"Could not make a line from {target} to {[str(p) for p in polygon.points]} - {polygon.name}")
    closest_point = min(distances, key=lambda x: x[1])[0]
    return closest_point


def check_if_point_in_polygons(polygons, point, exclude_edges=True) -> bool:
    for polygon in polygons:
        if polygon.check_if_contains_point(point, exclude_edges=exclude_edges):
            return True
    return False
