"""Common schemas shared across the application."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DataQuality(BaseModel):
    """Data quality and provenance metadata attached to every result."""

    data_coverage: float = Field(ge=0.0, le=1.0, description="Fraction of expected data present")
    missing_fields: list[str] = Field(default_factory=list)
    used_proxies: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    source_timestamps: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    assumptions: list[str] = Field(default_factory=list)


class PaginatedResponse(BaseModel):
    """Wrapper for paginated list responses."""

    items: list[Any]
    total: int
    page: int = 1
    per_page: int = 50


class ErrorResponse(BaseModel):
    """Standard error envelope."""

    error: str
    detail: str | None = None
    code: str | None = None


class HealthResponse(BaseModel):
    """Response from GET /health."""

    status: str = "ok"
    version: str
    data_mode: str
    environment: str
