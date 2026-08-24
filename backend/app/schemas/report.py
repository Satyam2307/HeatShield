"""Report export schemas."""

from __future__ import annotations

from pydantic import BaseModel


class ReportMetadata(BaseModel):
    """Metadata included in exported reports."""

    analysis_id: str
    city: str
    analysis_date: str
    generated_at: str
    total_stops: int
    scoring_version: str
    data_sources: list[str]
    methodology: str
    assumptions: list[str]
    limitations: list[str]


class ReportResponse(BaseModel):
    """Response for GET /api/v1/reports/{analysis_id}."""

    metadata: ReportMetadata
    format: str = "csv"
    download_url: str | None = None
    content: str | None = None  # CSV string for inline return
