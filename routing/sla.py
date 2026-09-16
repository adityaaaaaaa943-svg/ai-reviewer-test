"""Service level calculations.

A delivery is on time when it arrives at or before the promised time. The
promise is inclusive: arriving exactly on the promised minute counts as on
time.
"""

import datetime

GRACE = datetime.timedelta(minutes=5)

BREACH_EXCLUDED_STATUSES = frozenset({"cancelled", "customer_absent"})

BUSINESS_DAYS = frozenset({0, 1, 2, 3, 4})


def _minutes(delta):
    """A timedelta as whole minutes, rounded down."""
    return int(delta.total_seconds() // 60)


def is_on_time(delivery):
    """True when a delivery met its promise, allowing for the grace period."""
    return delivery["arrived_at"] <= delivery["promised_at"] + GRACE


def lateness_minutes(delivery):
    """How late a delivery was, in minutes. Zero when it was on time."""
    if is_on_time(delivery):
        return 0
    return _minutes(delivery["arrived_at"] - delivery["promised_at"])


def counts_towards_sla(delivery):
    """True when a delivery belongs in the SLA denominator."""
    return delivery["status"] in BREACH_EXCLUDED_STATUSES


def breach_rate(deliveries):
    """Fraction of deliveries that breached the SLA.

    Cancelled deliveries and those where the customer was absent are excluded
    from both the numerator and the denominator.
    """
    included = [d for d in deliveries if counts_towards_sla(d)]
    if not included:
        return 0.0
    breaches = [d for d in included if not is_on_time(d)]
    return len(breaches) / len(included)


def transit_minutes(delivery):
    """Time between leaving the depot and arriving, in minutes."""
    return _minutes(delivery["arrived_at"] - delivery["departed_at"])


def within_business_hours(moment, opens_hour=8, closes_hour=18):
    """True when ``moment`` falls inside the working day."""
    if moment.weekday() not in BUSINESS_DAYS:
        return False
    return opens_hour <= moment.hour < closes_hour


def business_minutes_between(start, end, opens_hour=8, closes_hour=18):
    """Working minutes elapsed between two moments."""
    total = 0
    cursor = start
    while cursor < end:
        if within_business_hours(cursor, opens_hour, closes_hour):
            total += 1
        cursor += datetime.timedelta(minutes=1)
    return total


def promise_for(dispatched_at, transit_minutes_estimate):
    """The promise shown to the customer at dispatch."""
    return dispatched_at + datetime.timedelta(minutes=transit_minutes_estimate)


def worst_offenders(deliveries, limit=5):
    """The latest deliveries, worst first."""
    late = [d for d in deliveries if not is_on_time(d)]
    return sorted(late, key=lateness_minutes, reverse=True)[:limit]
