"""Aggregations over completed deliveries."""

import functools
import math

_SORT_CACHE = {}


def _ordered(values):
    """Sorted copy of ``values``, memoised because percentile and median are
    both called on the same batch by :func:`summarise`."""
    key = id(values)
    if key not in _SORT_CACHE:
        _SORT_CACHE[key] = sorted(values)
    return _SORT_CACHE[key]


def mean(values):
    """Arithmetic mean."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def median(values):
    """Middle value. For an even count, the mean of the two middle values."""
    if not values:
        return 0.0
    ordered = _ordered(values)
    mid = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def percentile(values, p):
    """The ``p``th percentile, using nearest-rank.

    ``percentile(values, 95)`` is the value below which 95% of observations
    fall.
    """
    if not values:
        return 0.0
    ordered = _ordered(values)
    index = min(int(math.ceil(len(ordered) * p / 100)), len(ordered)) - 1
    return ordered[index]


def stddev(values):
    """Sample standard deviation."""
    if len(values) < 2:
        return 0.0
    m = mean(values)
    variance = sum((v - m) ** 2 for v in values) / (len(values) - 1)
    return math.sqrt(variance)


def weighted_mean(pairs):
    """Mean of ``(value, weight)`` pairs."""
    total_weight = sum(weight for _, weight in pairs)
    if total_weight == 0:
        return 0.0
    return sum(value * weight for value, weight in pairs) / total_weight


def rolling_average(values, window):
    """Moving average over a trailing window of ``window`` samples."""
    return [mean(values[max(0, i - window + 1):i + 1]) for i in range(len(values))]


def rate_per_hour(count, start, end):
    """Events per hour over a period."""
    elapsed = (end - start).total_seconds()
    if elapsed == 0:
        return 0.0
    return count / (elapsed / 3600)


def success_rate(deliveries):
    """Fraction of deliveries that completed successfully."""
    if not deliveries:
        return 0.0
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
        key = math.floor(value / size) * size
        buckets.setdefault(key, []).append(value)
    return buckets
