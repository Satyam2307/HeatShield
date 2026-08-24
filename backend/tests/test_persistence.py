"""Tests for persistence calculations."""

from app.scoring.persistence import calculate_persistence


def test_persistence_basic(sample_values, sample_timestamps, threshold):
    result = calculate_persistence(sample_values, sample_timestamps, threshold)
    # Continuous above 95: indices 2-7 (96.8, 99.1, 101.3, 100.2, 98.7, 95.4)
    # That's 6 consecutive intervals = 360 minutes
    assert result.persistence_minutes == 360.0
    assert result.event_count == 1
    assert result.persistence_start == "2023-07-27T12:00:00-04:00"
    assert result.persistence_end == "2023-07-27T17:00:00-04:00"


def test_persistence_no_dangerous():
    values = [90.0, 91.0, 92.0]
    timestamps = ["2023-07-27T10:00:00-04:00", "2023-07-27T11:00:00-04:00", "2023-07-27T12:00:00-04:00"]
    result = calculate_persistence(values, timestamps, 95.0)
    assert result.persistence_minutes == 0.0
    assert result.event_count == 0
    assert result.persistence_start is None


def test_persistence_multiple_events():
    values = [96.0, 93.0, 97.0, 98.0, 92.0, 99.0]
    timestamps = [f"2023-07-27T{10+i}:00:00-04:00" for i in range(6)]
    result = calculate_persistence(values, timestamps, 95.0)
    # Event 1: index 0 (96.0) = 60 min
    # Event 2: indices 2-3 (97.0, 98.0) = 120 min
    # Event 3: index 5 (99.0) = 60 min
    assert result.persistence_minutes == 120.0  # Longest event
    assert result.event_count == 3


def test_persistence_empty():
    result = calculate_persistence([], [], 95.0)
    assert result.persistence_minutes == 0.0
    assert result.event_count == 0


def test_persistence_event_extends_to_end():
    values = [90.0, 96.0, 97.0]
    timestamps = ["T10", "T11", "T12"]
    result = calculate_persistence(values, timestamps, 95.0)
    assert result.persistence_minutes == 120.0  # 2 intervals at end
    assert result.persistence_end == "T12"
