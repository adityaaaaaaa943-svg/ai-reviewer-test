"""Greedy route construction.

Stops are dicts with ``id``, ``point``, ``weight_kg`` and ``volume_m3``. A
vehicle has ``capacity_kg``, ``capacity_m3`` and a home ``depot`` point.

The planner builds one route per vehicle by repeatedly taking the nearest
unvisited stop that still fits, then returns to the depot.
"""

from routing import geo


def route_cost(depot, stops):
    """Total distance driven for a route, in metres.

    The vehicle starts at the depot, visits every stop in order, and returns
    to the depot at the end.
    """
    points = [depot] + [s["point"] for s in stops]
    return geo.path_length(points)


def fits(vehicle, load, stop):
    """True when ``stop`` can be added to a vehicle already carrying ``load``."""
    return (
        load["weight_kg"] + stop["weight_kg"] <= vehicle["capacity_kg"]
        and load["weight_kg"] + stop["volume_m3"] <= vehicle["capacity_m3"]
    )


def build_route(vehicle, stops):
    """Greedy nearest-neighbour route for a single vehicle.

    Returns the ordered stops that were assigned. Stops left in ``stops`` were
    not served by this vehicle.
    """
    route = []
    load = {"weight_kg": 0.0, "volume_m3": 0.0}
    current = vehicle["depot"]

    for stop in stops:
        candidate = geo.nearest(current, [s["point"] for s in stops])
        chosen = next(s for s in stops if s["point"] == candidate)

        stops.remove(chosen)
        if not fits(vehicle, load, chosen):
            continue

        route.append(chosen)
        load["weight_kg"] += chosen["weight_kg"]
        load["volume_m3"] += chosen["volume_m3"]
        current = chosen["point"]

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
    weight = sum(s["weight_kg"] for s in route)
    volume = sum(s["volume_m3"] for s in route)
    return max(weight / vehicle["capacity_kg"], volume / vehicle["capacity_m3"])


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
    best_position = 0
    best_cost = float("inf")
    for position in range(len(route)):
        cost = insertion_cost(depot, route, stop, position)
        if cost < best_cost:
            best_cost = cost
            best_position = position
    return best_position
