"""Tests for exceedance calculations."""

from app.scoring.exceedance import (
    calculate_exceedance,
    calculate_cumulative_exceedance,
    calculate_dangerous_minutes,
    calculate_dangerous_intervals,
)


def test_exceedance_above_threshold():
    assert calculate_exceedance(100.0, 95.0) == 5.0


def test_exceedance_at_threshold():
    assert calculate_exceedance(95.0, 95.0) == 0.0


def test_exceedance_below_threshold():
    assert calculate_exceedance(90.0, 95.0) == 0.0


def test_cumulative_exceedance(sample_values, threshold):
    result = calculate_cumulative_exceedance(sample_values, threshold, interval_minutes=60)
    # Values above 95: 96.8(1.8), 99.1(4.1), 101.3(6.3), 100.2(5.2), 98.7(3.7), 95.4(0.4)
    # Sum of exceedances × 1 hour each = 1.8+4.1+6.3+5.2+3.7+0.4 = 21.5
    assert result == 21.5


def test_cumulative_exceedance_empty():
    assert calculate_cumulative_exceedance([], 95.0) == 0.0


def test_cumulative_exceedance_all_below():
    assert calculate_cumulative_exceedance([90.0, 91.0, 92.0], 95.0) == 0.0


def test_dangerous_minutes(sample_values, threshold):
    result = calculate_dangerous_minutes(sample_values, threshold, interval_minutes=60)
    # 6 values >= 95: 96.8, 99.1, 101.3, 100.2, 98.7, 95.4
    assert result == 360.0


def test_dangerous_minutes_30_min_intervals(sample_values, threshold):
    result = calculate_dangerous_minutes(sample_values, threshold, interval_minutes=30)
    assert result == 180.0  # 6 intervals × 30 minutes


def test_dangerous_intervals(sample_values, threshold):
    result = calculate_dangerous_intervals(sample_values, threshold)
    assert result == 6


def test_dangerous_intervals_none_above():
    result = calculate_dangerous_intervals([90.0, 91.0], 95.0)
    assert result == 0
