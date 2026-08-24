"""
Persistence analysis.

Persistence measures the longest continuous period above the danger threshold.
This is more meaningful than total dangerous minutes because it captures
sustained exposure risk.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PersistenceResult:
    """Result of a persistence analysis."""

    persistence_minutes: float
    persistence_start: str | None  # ISO timestamp of start
    persistence_end: str | None    # ISO timestamp of end
    event_count: int               # Number of separate dangerous events
    all_events: list[dict]         # [{start, end, duration_minutes}]


def calculate_persistence(
    values: list[float],
    timestamps: list[str],
    threshold: float,
    interval_minutes: int = 60,
) -> PersistenceResult:
    """
    Find the longest continuous sequence where value >= threshold.

    Args:
        values: Heat values in chronological order.
        timestamps: Corresponding ISO timestamps.
        threshold: Danger threshold.
        interval_minutes: Duration of each interval.

    Returns:
        PersistenceResult with longest event details and all events.
    """
    if not values or len(values) != len(timestamps):
        return PersistenceResult(
            persistence_minutes=0.0,
            persistence_start=None,
            persistence_end=None,
            event_count=0,
            all_events=[],
        )

    events: list[dict] = []
    current_start: int | None = None

    for i, v in enumerate(values):
        if v >= threshold:
            if current_start is None:
                current_start = i
        else:
            if current_start is not None:
                duration = (i - current_start) * interval_minutes
                events.append({
                    "start": timestamps[current_start],
                    "end": timestamps[i - 1],
                    "duration_minutes": duration,
                })
                current_start = None

    # Handle event that extends to end of series
    if current_start is not None:
        duration = (len(values) - current_start) * interval_minutes
        events.append({
            "start": timestamps[current_start],
            "end": timestamps[-1],
            "duration_minutes": duration,
        })

    if not events:
        return PersistenceResult(
            persistence_minutes=0.0,
            persistence_start=None,
            persistence_end=None,
            event_count=0,
            all_events=[],
        )

    # Find longest event
    longest = max(events, key=lambda e: e["duration_minutes"])

    return PersistenceResult(
        persistence_minutes=longest["duration_minutes"],
        persistence_start=longest["start"],
        persistence_end=longest["end"],
        event_count=len(events),
        all_events=events,
    )
