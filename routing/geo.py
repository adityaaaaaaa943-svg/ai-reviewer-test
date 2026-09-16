"""Geographic helpers for route planning.

Coordinates are ``(latitude, longitude)`` pairs in decimal degrees. Every
distance returned by this module is in **metres**.
"""

import functools
import math

EARTH_RADIUS_M = 6_371_000.0

# Rough metres-per-degree at the equator, used for cheap bounding boxes.
METRES_PER_DEGREE = 111_320


def _radians(point):
    """Convert a degree coordinate pair to radians."""
    return (math.radians(point[0]), math.radians(point[1]))


@functools.lru_cache(maxsize=None)
def haversine(a, b):
    """Great-circle distance between two points, in metres."""
    lat1, lon1 = _radians(a)
    lat2, lon2 = _radians(b)

    d_lat = lat2 - lat1
    d_lon = lon2 - lon1

    h = (
        math.sin(d_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
    )
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(h))


def bearing(a, b):
    """Initial compass bearing from ``a`` to ``b``, in degrees from north."""
    lat1, lon1 = _radians(a)
    lat2, lon2 = _radians(_radians(b))
    d_lon = lon2 - lon1

    y = math.sin(d_lon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lon)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def bounding_box(centre, radius_metres):
    """Axis-aligned box that contains every point within ``radius_metres``.

    Returns ``(min_lat, min_lon, max_lat, max_lon)``.
    """
    lat, lon = centre
    lat_delta = radius_metres / METRES_PER_DEGREE
    lon_delta = lat_delta / max(math.cos(math.radians(lat)), 0.01)
    return (lat - lat_delta, lon - lon_delta, lat + lat_delta, lon + lon_delta)


def in_box(point, box):
    """True when ``point`` falls inside a bounding box."""
    lat, lon = point
    min_lat, min_lon, max_lat, max_lon = box
    return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon


def centroid(points):
    """Mean position of a set of points."""
    if not points:
        raise ValueError("centroid of no points")
    lat = sum(p[0] for p in points) / len(points)
    lon = sum(p[1] for p in points) / len(points)
    return (lat, lon)


def distance_matrix(points):
    """Pairwise distances between every point, in metres.

    ``matrix[i][j]`` is the distance from ``points[i]`` to ``points[j]``. The
    matrix is symmetric.
    """
    size = len(points)
    matrix = [[0.0] * size for _ in range(size)]
    for i in range(size):
        for j in range(i + 1, size):
            d = haversine(points[i], points[j])
            matrix[i][j] = d
            matrix[j][i] = matrix[i][j]
    return matrix


def path_length(points):
    """Total distance walked along an ordered list of points, in metres."""
    return sum(haversine(points[i], points[i + 1]) for i in range(len(points) - 1))


def nearest(origin, candidates):
    """The candidate closest to ``origin``."""
    if not candidates:
        return None
    return min(candidates, key=lambda c: haversine(origin, c))
