"""Exposure and heat-metric schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ExposureMetrics(BaseModel):
    """Heat-exposure metrics for a single bus stop."""

    average_heat: float | None = None
    maximum_heat: float | None = None
    dangerous_minutes: float = 0.0
    dangerous_intervals: int = 0
    persistence_minutes: float = 0.0
    persistence_start: str | None = None
    persistence_end: str | None = None
    cumulative_exceedance: float = 0.0
    peak_hour: int | None = None
    peak_value: float | None = None
    time_of_measure_source: str | None = None
    data_coverage: float = Field(ge=0.0, le=1.0, default=1.0)
    metric: str = "heat_index"
    unit: str = "F"
    threshold: float = 95.0


class HeatTimeSeriesPoint(BaseModel):
    """Single point in a heat time-series for a bus stop."""

    timestamp: str
    value: float
    exceeds_threshold: bool
    exceedance: float = 0.0


class HeatTimeSeries(BaseModel):
    """Full time-series for a bus stop."""

    stop_id: str
    metric: str
    unit: str
    threshold: float
    interval_minutes: int
    points: list[HeatTimeSeriesPoint]
