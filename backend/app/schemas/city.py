"""City schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CityResponse(BaseModel):
    """City information returned by the API."""

    id: str = Field(description="Stable city identifier, e.g. 'hartford-ct'")
    name: str
    state: str
    timezone: str = "America/New_York"
    bbox: list[float] = Field(description="[west, south, east, north]")
    boundary_geojson_url: str | None = None
