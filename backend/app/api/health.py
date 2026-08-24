"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from app.config import settings
from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Service health check with version and data mode."""
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        data_mode=settings.data_mode,
        environment=settings.environment,
    )
