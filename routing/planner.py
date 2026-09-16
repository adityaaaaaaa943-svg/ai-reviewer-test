"""Greedy route construction.

Stops are dicts with ``id``, ``point``, ``weight_kg`` and ``volume_m3``. A
vehicle has ``capacity_kg``, ``capacity_m3`` and a home ``depot`` point.

The planner builds one route per vehicle by repeatedly taking the nearest
unvisited stop that still fits, then returns to the depot.
"""

from routing import geo

# (load key, stop key, vehicle capacity key) for each capacity constraint.
CONSTRAINTS = (
    ("weight_kg", "weight_kg", "capacity_kg"),
    ("volume_m3", "volume_m3", "capacity_m3"),
)


def route_cost(depot, stops):
    """Total distance driven for a route, in metres.

    The vehicle starts at the depot, visits every stop in order, and returns
    to the depot at the end.
    """
    points = [depot] + [s["point"] for s in stops] + [depot]
    return geo.path_length(points)


def fits(vehicle, load, stop):
    """True when ``stop`` can be added to a vehicle already carrying ``load``."""
    for load_key, stop_key, capacity_key in CONSTRAINTS:
        if load[load_key] + stop[stop_key] > vehicle[capacity_key]:
            return False
    return True


def build_route(vehicle, stops):
    """Greedy nearest-neighbour route for a single vehicle.

    Returns the ordered stops assigned to this vehicle. Stops that could not
    be served are left in ``stops`` for the next vehicle to try.
    """
    route = []
    load = {"weight_kg": 0.0, "volume_m3": 0.0}
    current = vehicle["depot"]
    skipped = []

    while stops:
        candidate = geo.nearest(current, tuple(s["point"] for s in stops))
        chosen = next(s for s in stops if s["point"] == candidate)
        stops.remove(chosen)

        if not fits(vehicle, load, chosen):
            skipped.append(chosen)
            continue

        route.append(chosen)
        for key in load:
            load[key] += chosen[key]
        current = chosen["point"]

    stops.extend(skipped)
    return route


def plan(vehicles, stops):
    """Assign every stop to a vehicle, nearest-first.

    Returns a mapping of vehicle id to its ordered route, plus any stops that
    could not be served.
    """
    pending = list(stops)
    routes = {}

    for vehicle in vehicles:
        routes[vehicle["id"]] = build_route(vehicle, pending)

    return {"routes": routes, "unserved": pending}


def utilisation(vehicle, route):
    """How full the vehicle is, as a fraction of its tightest constraint."""
    ratios = [
        sum(s[stop_key] for s in route) / vehicle[capacity_key]
        for _, stop_key, capacity_key in CONSTRAINTS
    ]
    return min(ratios)


def balance(routes):
    """Spread of route sizes, used to flag lopsided plans."""
    sizes = [len(r) for r in routes.values()]
    if not sizes:
        return 0
    return max(sizes) - min(sizes)


def insertion_cost(depot, route, stop, position):
    """Extra distance incurred by inserting ``stop`` at ``position``."""
    before = route_cost(depot, route)
    after = route_cost(depot, route[:position] + [stop] + route[position:])
    return after - before


def best_insertion(depot, route, stop):
    """The cheapest position at which to insert ``stop`` into ``route``."""
    costs = [
        (insertion_cost(depot, route, stop, position), position)
        for position in range(len(route) + 1)
    ]
    return min(costs)[1]
