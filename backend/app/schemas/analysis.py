"""Analysis scenario schemas — request and response."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.scoring import ScoringWeights


class AnalysisRequest(BaseModel):
    """Request body for POST /api/v1/analysis."""

    city_id: str = "hartford-ct"
    start_time: str = Field(description="ISO-8601, e.g. 2023-07-27T10:00:00-04:00")
    end_time: str = Field(description="ISO-8601, e.g. 2023-07-27T18:00:00-04:00")
    heat_metric: str = "heat_index"
    heat_unit: str = "F"
    danger_threshold: float = 95.0
    interval_minutes: int = 60
    buffer_meters: int = 100
    weights: ScoringWeights | None = None


class AnalysisResponse(BaseModel):
    """Response from POST /api/v1/analysis or GET /api/v1/analyses/{id}."""

    analysis_id: str
    city_id: str
    status: Literal["queued", "processing", "completed", "failed"] = "completed"
    start_time: str
    end_time: str
    heat_metric: str
    heat_unit: str
    danger_threshold: float
    interval_minutes: int
    buffer_meters: int
    scoring_version: str
    total_stops: int = 0
    weights: ScoringWeights | None = None
    created_at: str | None = None
