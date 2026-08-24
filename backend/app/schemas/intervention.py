"""Intervention simulation schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class InterventionRequest(BaseModel):
    """Request body for POST /api/v1/interventions/simulate."""

    analysis_id: str
    asset_id: str
    intervention_type: str = "shade_structure"
    scenario: Literal["conservative", "moderate", "high"] = "moderate"


class InterventionAssumptions(BaseModel):
    """Documented assumptions for an intervention scenario."""

    intervention_type: str = "shade_structure"
    scenario: str
    effectiveness_factor: float
    coverage_factor: float
    description: str
    disclaimer: str = (
        "These are planning assumptions for comparison purposes. "
        "They are not engineering guarantees of temperature reduction."
    )


class InterventionResult(BaseModel):
    """Result of simulating a shade intervention on a bus stop."""

    analysis_id: str
    asset_id: str
    stop_name: str | None = None

    # Baseline
    baseline_dangerous_minutes: float
    baseline_cumulative_exceedance: float
    baseline_heat_score: float
    baseline_priority_score: float
    baseline_rank: int

    # Projected
    projected_dangerous_minutes: float
    projected_cumulative_exceedance: float
    projected_heat_score: float
    projected_priority_score: float
    projected_rank: int

    # Deltas
    avoided_dangerous_minutes: float
    avoided_cumulative_exceedance: float
    percentage_reduction: float = Field(ge=0.0, le=100.0)
    rank_change: int  # positive = improved (lower rank number)

    # Metadata
    assumptions: InterventionAssumptions
    confidence: float = Field(ge=0.0, le=1.0, default=0.7)
