"""
Pydantic schemas matching TRD 2.8 and API requirements.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class WeightsSchema(BaseModel):
    heat: float = Field(default=0.40, ge=0.0, le=1.0)
    shade: float = Field(default=0.25, ge=0.0, le=1.0)
    vulnerability: float = Field(default=0.20, ge=0.0, le=1.0)
    transit: float = Field(default=0.15, ge=0.0, le=1.0)

class AnalysisCreateRequest(BaseModel):
    city_id: str = "hartford-ct"
    start_time: str = "2024-07-15T10:00:00-04:00"
    end_time: str = "2024-07-15T18:00:00-04:00"
    heat_metric: str = "heat_index"
    heat_unit: str = "F"
    danger_threshold: float = 95.0
    weights: WeightsSchema = Field(default_factory=WeightsSchema)

class ComponentsSchema(BaseModel):
    heat: float
    shade: float
    vulnerability: float
    transit: float

class MetricsSchema(BaseModel):
    average_heat: float
    maximum_heat: float
    dangerous_minutes: float
    dangerous_intervals: int
    persistence_minutes: float
    cumulative_exceedance: float
    peak_hour: int

class ShadeDetailsSchema(BaseModel):
    vegetation_fraction: float
    impervious_fraction: float
    building_fraction: float
    shade_deficit: float
    shelter_status: str

class VulnerabilityDetailsSchema(BaseModel):
    geography_id: str
    neighborhood_name: str
    median_income: float
    zero_vehicle_fraction: float
    older_adult_fraction: float
    children_fraction: float
    population_density: float

class TransitDetailsSchema(BaseModel):
    route_count: int
    routes: List[str]
    ridership: float
    transit_value_type: str = "proxy"

class MetadataSchema(BaseModel):
    shade_is_proxy: bool = True
    transit_is_proxy: bool = True
    data_coverage: float = 1.0
    confidence: float = 0.89

class BusStopRankingItem(BaseModel):
    asset_id: str
    rank: int
    name: str
    corridor: str
    latitude: float
    longitude: float
    priority_score: float
    priority_category: str
    components: ComponentsSchema
    metrics: MetricsSchema
    shade_details: ShadeDetailsSchema
    vulnerability_details: VulnerabilityDetailsSchema
    transit_details: TransitDetailsSchema
    metadata: MetadataSchema

class RankingsResponse(BaseModel):
    analysis_id: str
    city: Dict[str, str]
    scenario: Dict[str, Any]
    weights: Dict[str, float]
    total_stops: int
    rankings: List[BusStopRankingItem]

class SimulationRequest(BaseModel):
    analysis_id: str = "hartford-demo-2024-07-15"
    asset_id: str
    intervention_type: str = "shade_structure"
    scenario: str = "moderate"  # conservative, moderate, high

class ExplanationRequest(BaseModel):
    analysis_id: str = "hartford-demo-2024-07-15"
    asset_id: str
