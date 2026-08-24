"""Shade-deficit schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ShadeMetrics(BaseModel):
    """Shade and land-cover information for a bus stop."""

    buffer_meters: int = 100
    vegetation_fraction: float | None = Field(None, ge=0.0, le=1.0)
    impervious_fraction: float | None = Field(None, ge=0.0, le=1.0)
    building_fraction: float | None = Field(None, ge=0.0, le=1.0)
    canopy_fraction: float | None = Field(None, ge=0.0, le=1.0)
    shade_deficit: float = Field(ge=0.0, le=1.0, description="1.0 = no shade, 0.0 = full shade")
    shelter_status: str | None = None  # "present", "absent", "unknown"
    confidence: float = Field(ge=0.0, le=1.0, default=0.7)
    source: str = "satellite_landcover_proxy"
    disclaimer: str = (
        "Land-cover data is a proxy estimate. It does not directly measure "
        "shade at the passenger waiting position."
    )
