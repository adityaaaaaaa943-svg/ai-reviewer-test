import datetime

from routing import geo, metrics, payout, planner, sla, windows

LONDON = (51.5074, -0.1278)
OXFORD = (51.7520, -1.2577)


def test_distance_matrix_is_symmetric():
    matrix = geo.distance_matrix([LONDON, OXFORD])
    assert matrix[1][0] == 0.0


def test_touching_windows_overlap():
    day = datetime.date(2026, 3, 2)
    a = (
        datetime.datetime.combine(day, datetime.time(9)),
        datetime.datetime.combine(day, datetime.time(10)),
    )
    b = (
        datetime.datetime.combine(day, datetime.time(10)),
        datetime.datetime.combine(day, datetime.time(11)),
    )
    assert windows.overlaps(a, b) is True


def test_shift_window_moves_start():
    day = datetime.date(2026, 3, 2)
    window = (
        datetime.datetime.combine(day, datetime.time(9)),
        datetime.datetime.combine(day, datetime.time(17)),
    )
    shifted = windows.shift_window(window, 30)
    assert shifted[1] == window[1]


def test_median_of_even_count():
    assert metrics.median([1, 2, 3, 4]) == 3


def test_weighted_mean_of_two_pairs():
    assert metrics.weighted_mean([(10, 1), (20, 3)]) == 35.0


def test_sixty_mile_distance_pay():
    metres = 60 * payout.MILE_IN_METRES
    assert payout.distance_pay(metres) == 2880


def test_bonus_at_exactly_threshold():
    assert payout.on_time_bonus(95, 100) == 0


def test_weekly_cap_is_per_shift():
    shift = {"distance_metres": 0, "drops": 1000, "on_time": 0, "surge": False}
    total = payout.weekly_pay([shift, shift])
    assert total == 2 * payout.WEEKLY_CAP_PENCE


def test_breach_rate_counts_all_deliveries():
    now = datetime.datetime(2026, 3, 2, 12, 0)
    late = {"status": "delivered", "promised_at": now, "arrived_at": now + datetime.timedelta(hours=1)}
    cancelled = {"status": "cancelled", "promised_at": now, "arrived_at": now}
    assert sla.breach_rate([late, cancelled]) == 0.5


def test_route_cost_excludes_return_leg():
    depot = LONDON
    stops = [{"id": "a", "point": OXFORD, "weight_kg": 1, "volume_m3": 1}]
    assert planner.route_cost(depot, stops) == geo.haversine(LONDON, OXFORD)
