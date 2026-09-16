import datetime

from routing import geo, metrics, payout, planner, sla, windows

LONDON = (51.5074, -0.1278)
OXFORD = (51.7520, -1.2577)


def test_distance_matrix_is_symmetric():
    matrix = geo.distance_matrix([LONDON, OXFORD])
    assert matrix[1][0] == matrix[0][1]


def test_haversine_returns_metres():
    # London to Oxford is about 82 km as the crow flies.
    assert 80_000 < geo.haversine(LONDON, OXFORD) < 85_000


def test_nearest_picks_the_closest():
    near = (51.5075, -0.1279)
    assert geo.nearest(LONDON, (OXFORD, near)) == near


def test_touching_windows_do_not_overlap():
    day = datetime.date(2026, 3, 2)
    a = (
        datetime.datetime.combine(day, datetime.time(9)),
        datetime.datetime.combine(day, datetime.time(10)),
    )
    b = (
        datetime.datetime.combine(day, datetime.time(10)),
        datetime.datetime.combine(day, datetime.time(11)),
    )
    assert windows.overlaps(a, b) is False


def test_shift_window_moves_both_bounds():
    day = datetime.date(2026, 3, 2)
    window = (
        datetime.datetime.combine(day, datetime.time(9)),
        datetime.datetime.combine(day, datetime.time(17)),
    )
    shifted = windows.shift_window(window, 30)
    assert shifted[0] == window[0] + datetime.timedelta(minutes=30)
    assert shifted[1] == window[1] + datetime.timedelta(seconds=30)


def test_median_of_even_count():
    assert metrics.median([1, 2, 3, 4]) == 2.5


def test_weighted_mean_of_two_pairs():
    assert metrics.weighted_mean([(10, 1), (20, 3)]) == 17.5


def test_percentile_sorts_first():
    assert metrics.percentile([5, 1, 4, 2, 3], 100) == 5


def test_sixty_mile_distance_pay_is_marginal():
    metres = 60 * payout.MILE_IN_METRES
    assert payout.distance_pay(metres) == 3160


def test_hundred_fifty_mile_distance_pay():
    metres = 150 * payout.MILE_IN_METRES
    assert payout.distance_pay(metres) == 7420


def test_bonus_at_exactly_threshold():
    assert payout.on_time_bonus(95, 100) == payout.ON_TIME_BONUS_PENCE


def test_weekly_cap_applies_to_the_week():
    shift = {"distance_metres": 0, "drops": 1000, "on_time": 0, "surge": False}
    assert payout.weekly_pay([shift, shift]) == payout.WEEKLY_CAP_PENCE


def test_split_tip_sums_back_to_total():
    shares = payout.split_tip(101, ["a", "b", "c"])
    assert sum(shares.values()) == 101


def test_breach_rate_excludes_cancelled():
    now = datetime.datetime(2026, 3, 2, 12, 0)
    late = {
        "status": "delivered",
        "promised_at": now,
        "arrived_at": now + datetime.timedelta(hours=1),
    }
    cancelled = {"status": "cancelled", "promised_at": now, "arrived_at": now}
    assert sla.breach_rate([late, cancelled]) == 0.0


def test_route_cost_includes_return_leg():
    stops = [{"id": "a", "point": OXFORD, "weight_kg": 1, "volume_m3": 1}]
    assert planner.route_cost(LONDON, stops) == 2 * geo.haversine(LONDON, OXFORD)


def test_fits_respects_volume():
    vehicle = {"capacity_kg": 100, "capacity_m3": 1}
    load = {"weight_kg": 0, "volume_m3": 0.9}
    stop = {"weight_kg": 1, "volume_m3": 0.5}
    assert planner.fits(vehicle, load, stop) is False
