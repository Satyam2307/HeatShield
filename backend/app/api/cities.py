"""City endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.geospatial.boundary import load_hartford_boundary, get_hartford_bbox
from app.schemas.city import CityResponse

router = APIRouter(prefix="/api/v1", tags=["cities"])


@router.get("/cities", response_model=list[CityResponse])
async def list_cities():
    """List available cities. MVP: Hartford only."""
    boundary = load_hartford_boundary()
    bbox = get_hartford_bbox(boundary)

    return [
        CityResponse(
            id="hartford-ct",
            name="Hartford",
            state="Connecticut",
            timezone="America/New_York",
            bbox=bbox,
        )
    ]
