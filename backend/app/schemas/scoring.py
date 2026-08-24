"""Scoring weight schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ScoringWeights(BaseModel):
    """User-adjustable priority score weights."""

    heat: float = Field(0.40, ge=0.0, le=1.0)
    shade: float = Field(0.25, ge=0.0, le=1.0)
    vulnerability: float = Field(0.20, ge=0.0, le=1.0)
    transit: float = Field(0.15, ge=0.0, le=1.0)


class HeatSubWeights(BaseModel):
    """Weights for sub-components of the heat score."""

    cumulative_exceedance: float = 0.50
    dangerous_minutes: float = 0.30
    persistence: float = 0.20


class ScoreBreakdown(BaseModel):
    """Full priority score breakdown for a single bus stop."""

    heat_score: float = Field(ge=0.0, le=100.0)
    shade_score: float = Field(ge=0.0, le=100.0)
    vulnerability_score: float = Field(ge=0.0, le=100.0)
    transit_score: float = Field(ge=0.0, le=100.0)
    final_score: float = Field(ge=0.0, le=100.0)
    rank: int = Field(ge=1)
    priority_category: str  # Critical, High, Moderate, Low
    scoring_version: str

    # Heat sub-components (percentile-normalized 0-100)
    cumulative_exceedance_percentile: float | None = None
    dangerous_minutes_percentile: float | None = None
    persistence_percentile: float | None = None


class PriorityScoreResponse(BaseModel):
    """Priority score with weights used."""

    score: ScoreBreakdown
    weights: ScoringWeights
