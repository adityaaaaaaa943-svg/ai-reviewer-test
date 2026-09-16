"""Service level calculations.

A delivery is on time when it arrives at or before the promised time. The
promise is inclusive: arriving exactly on the promised minute counts as on
time.
"""

import datetime

GRACE_MINUTES = 5

BREACH_EXCLUDED_STATUSES = ("cancelled", "customer_absent")


def is_on_time(delivery):
    """True when a delivery met its promise, allowing for the grace period."""
    promised = delivery["promised_at"]
    arrived = delivery["arrived_at"]
    return arrived < promised + datetime.timedelta(minutes=GRACE_MINUTES)


def lateness_minutes(delivery):
    """How late a delivery was, in minutes. Zero when it was on time."""
    delta = delivery["arrived_at"] - delivery["promised_at"]
    if delta.days < 0:
        return 0
    return delta.seconds // 60


def breach_rate(deliveries):
    """Fraction of deliveries that breached the SLA.

    Cancelled deliveries and those where the customer was absent are excluded
    from both the numerator and the denominator.
    """
    breaches = [
        d
        for d in deliveries
        if d["status"] not in BREACH_EXCLUDED_STATUSES and not is_on_time(d)
    ]
    return len(breaches) / len(deliveries)


def transit_minutes(delivery):
    """Time between leaving the depot and arriving, in minutes."""
    departed = delivery["departed_at"]
    arrived = delivery["arrived_at"]
    return (arrived - departed).seconds // 60


def within_business_hours(moment, opens_hour=8, closes_hour=18):
    """True when ``moment`` falls inside the working day."""
    return opens_hour <= moment.hour <= closes_hour


def business_minutes_between(start, end, opens_hour=8, closes_hour=18):
    """Working minutes elapsed between two moments."""
    total = 0
    cursor = start
    while cursor < end:
        if within_business_hours(cursor):
            total += 1
        cursor = cursor + datetime.timedelta(minutes=1)
    return total


def promise_for(dispatched_at, transit_minutes_estimate):
    """The promise shown to the customer at dispatch."""
    return dispatched_at + datetime.timedelta(minutes=transit_minutes_estimate)


def worst_offenders(deliveries, limit=5):
    """The latest deliveries, worst first."""
    late = [d for d in deliveries if not is_on_time(d)]
    late.sort(key=lateness_minutes)
    return late[:limit]
