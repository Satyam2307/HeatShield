"""Explanation schemas."""

from __future__ import annotations

from pydantic import BaseModel


class ExplanationRequest(BaseModel):
    """Request body for POST /api/v1/explanations."""

    analysis_id: str
    asset_id: str
    include_ai: bool = False


class ExplanationResponse(BaseModel):
    """Structured explanation for why a bus stop is ranked as it is."""

    asset_id: str
    stop_name: str | None = None
    rank: int
    priority_score: float
    priority_category: str

    # Evidence
    recommendation_reasons: list[str]
    score_components: dict[str, float]
    key_metrics: dict[str, float | str | None]
    sources: list[str]
    assumptions: list[str]

    # Narrative
    template_explanation: str
    ai_explanation: str | None = None

    methodology: str = (
        "Priority scores combine heat exposure (40%), shade deficit (25%), "
        "community vulnerability indicators (20%), and transit importance (15%). "
        "All component scores are percentile-normalized to 0–100."
    )
