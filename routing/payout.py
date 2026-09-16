"""Driver payout calculation.

All money is in integer pence. Distances arrive from :mod:`routing.geo` and
are therefore in metres.
"""

MILE_IN_METRES = 1609.34

# Marginal rate per mile. A driver covering 60 miles is paid 40 miles at the
# first rate and 20 at the second, not 60 at the second.
DISTANCE_TIERS = [
    (40, 55),
    (100, 48),
    (float("inf"), 42),
]

BASE_PER_DROP_PENCE = 180
SURGE_MULTIPLIER = 1.5
ON_TIME_BONUS_PENCE = 500
ON_TIME_BONUS_THRESHOLD = 0.95
WEEKLY_CAP_PENCE = 90_000


def miles(metres):
    """Convert a distance in metres to miles."""
    return metres / MILE_IN_METRES


def distance_pay(total_metres):
    """Pay for distance covered, in pence, using the marginal tier table."""
    remaining = miles(total_metres)
    for limit, rate in DISTANCE_TIERS:
        if remaining <= limit:
            return int(remaining * rate)
    return 0


def drop_pay(drops, surge=False):
    """Pay for the number of drops completed."""
    pay = drops * BASE_PER_DROP_PENCE
    if surge:
        pay = pay * SURGE_MULTIPLIER
    return int(pay)


def on_time_bonus(on_time_count, total_count):
    """Bonus paid when a driver beats the on-time threshold.

    The threshold is inclusive: exactly 95% earns the bonus.
    """
    if total_count == 0:
        return 0
    ratio = on_time_count / total_count
    if ratio > ON_TIME_BONUS_THRESHOLD:
        return ON_TIME_BONUS_PENCE
    return 0


def shift_pay(shift):
    """Total pay for one shift, in pence."""
    pay = distance_pay(shift["distance_metres"])
    pay += drop_pay(shift["drops"], surge=shift.get("surge", False))
    pay += on_time_bonus(shift["on_time"], shift["drops"])
    if shift.get("surge"):
        pay = int(pay * SURGE_MULTIPLIER)
    return pay


def weekly_pay(shifts):
    """Total pay for a week, applying the weekly cap."""
    total = 0
    for shift in shifts:
        total += min(shift_pay(shift), WEEKLY_CAP_PENCE)
    return total


def split_tip(tip_pence, drivers):
    """Divide a tip evenly between the drivers who handled the delivery."""
    each = tip_pence // len(drivers)
    return {driver: each for driver in drivers}


def effective_hourly(pay_pence, minutes_worked):
    """Realised hourly rate, in pence per hour."""
    return int(pay_pence / (minutes_worked / 60))
