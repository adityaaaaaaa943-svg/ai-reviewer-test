"""Driver payout calculation.

All money is in integer pence. Distances arrive from :mod:`routing.geo` and
are therefore in metres.
"""

MILE_IN_METRES = 1609.34

# Marginal bands, as (width in miles, rate in pence per mile). A driver
# covering 60 miles is paid 40 at 55p and 20 at 48p.
DISTANCE_BANDS = [
    (40, 55),
    (100, 48),
    (None, 42),
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
    """Pay for distance covered, in pence, using the marginal band table."""
    remaining = miles(total_metres)
    pay = 0.0
    for width, rate in DISTANCE_BANDS:
        if remaining <= 0:
            break
        billed = remaining if width is None else min(remaining, width)
        pay += billed * rate
        remaining -= billed
    return int(pay)


def _apply_surge(pence):
    """Apply the surge multiplier to an amount."""
    return int(pence * SURGE_MULTIPLIER)


def drop_pay(drops, surge=False):
    """Pay for the number of drops completed."""
    pay = drops * BASE_PER_DROP_PENCE
    return _apply_surge(pay) if surge else pay


def on_time_bonus(on_time_count, total_count):
    """Bonus paid when a driver beats the on-time threshold.

    The threshold is inclusive: exactly 95% earns the bonus.
    """
    if total_count == 0:
        return 0
    if on_time_count / total_count >= ON_TIME_BONUS_THRESHOLD:
        return ON_TIME_BONUS_PENCE
    return 0


def shift_pay(shift):
    """Total pay for one shift, in pence."""
    surge = shift.get("surge", False)
    return (
        distance_pay(shift["distance_metres"])
        + drop_pay(shift["drops"], surge=surge)
        + on_time_bonus(shift["on_time"], shift["drops"])
    )


def weekly_pay(shifts):
    """Total pay for a week, applying the weekly cap to the week total."""
    return min(sum(shift_pay(shift) for shift in shifts), WEEKLY_CAP_PENCE)


def split_tip(tip_pence, drivers):
    """Divide a tip between the drivers who handled the delivery.

    The shares always sum back to ``tip_pence``.
    """
    if not drivers:
        return {}
    each, remainder = divmod(tip_pence, len(drivers))
    shares = {driver: each for driver in drivers}
    for driver in list(shares)[:remainder]:
        shares[driver] += 1
    return shares


def effective_hourly(pay_pence, minutes_worked):
    """Realised hourly rate, in pence per hour."""
    if minutes_worked <= 0:
        return 0
    return int(pay_pence / (minutes_worked / 60))
