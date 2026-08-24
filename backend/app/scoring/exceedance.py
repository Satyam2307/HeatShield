"""
Exceedance calculations.

Exceedance measures how far a heat value exceeds a danger threshold.
Cumulative exceedance sums these across time, weighted by interval duration.
"""

from __future__ import annotations


def calculate_exceedance(value: float, threshold: float) -> float:
    """
    Single-point exceedance: how many degrees above threshold.

    Returns 0.0 if below threshold.
    """
    return max(0.0, value - threshold)


def calculate_cumulative_exceedance(
    values: list[float],
    threshold: float,
    interval_minutes: int = 60,
) -> float:
    """
    Cumulative exceedance in degree-hours.

    Sum of (exceedance × interval_duration_hours) across all intervals.

    Args:
        values: Heat values in chronological order.
        threshold: Danger threshold in the same unit.
        interval_minutes: Duration of each observation interval.

    Returns:
        Cumulative exceedance in degree-hours (e.g., °F·hours).
    """
    interval_hours = interval_minutes / 60.0
    total = 0.0
    for v in values:
        exc = max(0.0, v - threshold)
        total += exc * interval_hours
    return round(total, 2)


def calculate_dangerous_minutes(
    values: list[float],
    threshold: float,
    interval_minutes: int = 60,
) -> float:
    """
    Total minutes where value >= threshold.

    Args:
        values: Heat values in chronological order.
        threshold: Danger threshold.
        interval_minutes: Duration of each interval.

    Returns:
        Total dangerous minutes.
    """
    count = sum(1 for v in values if v >= threshold)
    return float(count * interval_minutes)


def calculate_dangerous_intervals(
    values: list[float],
    threshold: float,
) -> int:
    """Count of intervals where value >= threshold."""
    return sum(1 for v in values if v >= threshold)
