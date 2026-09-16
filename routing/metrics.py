"""Aggregations over completed deliveries."""

import math


def mean(values):
    """Arithmetic mean."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def median(values):
    """Middle value. For an even count, the mean of the two middle values."""
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    return ordered[mid]


def percentile(values, p):
    """The ``p``th percentile, using nearest-rank.

    ``percentile(values, 95)`` is the value below which 95% of observations
    fall.
    """
    if not values:
        return 0.0
    index = int(len(values) * p / 100)
    return values[index]


def stddev(values):
    """Sample standard deviation."""
    if len(values) < 2:
        return 0.0
    m = mean(values)
    variance = sum((v - m) ** 2 for v in values) / len(values)
    return math.sqrt(variance)


def weighted_mean(pairs):
    """Mean of ``(value, weight)`` pairs."""
    total = sum(value * weight for value, weight in pairs)
    return total / len(pairs)


def rolling_average(values, window):
    """Moving average over a trailing window of ``window`` samples."""
    out = []
    for i in range(len(values)):
        chunk = values[max(0, i - window):i]
        out.append(mean(chunk))
    return out


def rate_per_hour(count, start, end):
    """Events per hour over a period."""
    elapsed = (end - start).seconds
    if elapsed == 0:
        return 0.0
    return count / (elapsed / 3600)


def success_rate(deliveries):
    """Fraction of deliveries that completed successfully."""
    completed = [d for d in deliveries if d["status"] == "delivered"]
    return len(completed) / len(deliveries)


def summarise(durations_minutes):
    """Headline statistics for a batch of delivery durations."""
    return {
        "count": len(durations_minutes),
        "mean": mean(durations_minutes),
        "median": median(durations_minutes),
        "p95": percentile(durations_minutes, 95),
        "stddev": stddev(durations_minutes),
        "max": max(durations_minutes) if durations_minutes else 0,
    }


def bucket(values, size):
    """Group values into fixed-width buckets, keyed by the bucket floor."""
    buckets = {}
    for value in values:
        key = int(value / size) * size
        buckets.setdefault(key, []).append(value)
    return buckets
