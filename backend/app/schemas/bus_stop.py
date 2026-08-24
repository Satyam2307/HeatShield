"""Bus-stop schemas — list, detail, and map features."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import DataQuality
from app.schemas.exposure import ExposureMetrics
from app.schemas.scoring import ScoreBreakdown, ScoringWeights
from app.schemas.shade import ShadeMetrics
from app.schemas.vulnerability import VulnerabilityMetrics


class TransitImportance(BaseModel):
    """Transit importance information for a bus stop."""

    route_count: int | None = None
    ridership: float | None = None
    service_frequency: str | None = None  # "high", "medium", "low"
    nearby_population: float | None = None
    nearby_essential_services: int | None = None
    transit_score: float = Field(ge=0.0, le=100.0, default=50.0)
    data_type: str = "proxy"  # "observed", "estimated", "proxy"
    source: str = "gtfs"


class BusStopSummary(BaseModel):
    """Compact bus-stop representation for ranked lists."""

    id: str
    external_stop_id: str
    name: str | None = None
    latitude: float
    longitude: float
    priority_score: float
    rank: int
    priority_category: str
    heat_score: float
    shade_score: float
    vulnerability_score: float
    transit_score: float
    dangerous_minutes: float
    persistence_minutes: float
    cumulative_exceedance: float


class BusStopDetail(BaseModel):
    """Full bus-stop detail with all analytics."""

    id: str
    external_stop_id: str
    name: str | None = None
    latitude: float
    longitude: float
    route_count: int | None = None
    shelter_status: str | None = None
    source: str

    # Computed analytics
    exposure: ExposureMetrics
    shade: ShadeMetrics
    vulnerability: VulnerabilityMetrics
    transit: TransitImportance
    score: ScoreBreakdown
    data_quality: DataQuality


class BusStopMapFeature(BaseModel):
    """GeoJSON-compatible feature for map rendering."""

    type: str = "Feature"
    properties: dict
    geometry: dict


class RankingsResponse(BaseModel):
    """Response for GET /analyses/{id}/rankings."""

    analysis_id: str
    total: int
    scoring_version: str
    weights: ScoringWeights
    stops: list[BusStopSummary]


class MapDataResponse(BaseModel):
    """GeoJSON FeatureCollection for map rendering."""

    type: str = "FeatureCollection"
    features: list[dict]
    metadata: dict = Field(default_factory=dict)
