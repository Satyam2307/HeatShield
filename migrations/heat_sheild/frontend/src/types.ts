export interface Weights {
  heat: number;
  shade: number;
  vulnerability: number;
  transit: number;
}

export interface Components {
  heat: number;
  shade: number;
  vulnerability: number;
  transit: number;
}

export interface Metrics {
  average_heat: number;
  maximum_heat: number;
  dangerous_minutes: number;
  dangerous_intervals: number;
  persistence_minutes: number;
  cumulative_exceedance: number;
  peak_hour: number;
}

export interface ShadeDetails {
  vegetation_fraction: number;
  impervious_fraction: number;
  building_fraction: number;
  shade_deficit: number;
  shelter_status: string;
}

export interface VulnerabilityDetails {
  geography_id: string;
  neighborhood_name: string;
  median_income: number;
  zero_vehicle_fraction: number;
  older_adult_fraction: number;
  children_fraction: number;
  population_density: number;
}

export interface TransitDetails {
  route_count: number;
  routes: string[];
  ridership: number;
  transit_value_type: string;
}

export interface TimeSeriesObservation {
  hour: number;
  timestamp: string;
  heat_index: number;
  unit: string;
  exceedance: number;
  is_dangerous: boolean;
}

export interface BusStop {
  asset_id: string;
  rank: number;
  name: string;
  corridor: string;
  latitude: number;
  longitude: number;
  priority_score: number;
  priority_category: 'Critical' | 'High' | 'Moderate' | 'Low' | string;
  components: Components;
  metrics: Metrics;
  shade_details: ShadeDetails;
  vulnerability_details: VulnerabilityDetails;
  transit_details: TransitDetails;
  metadata: {
    shade_is_proxy: boolean;
    transit_is_proxy: boolean;
    data_coverage: number;
    confidence: number;
  };
  timeseries: TimeSeriesObservation[];
}

export interface SimulationResult {
  asset_id: string;
  stop_name: string;
  intervention_type: string;
  scenario: string;
  scenario_description: string;
  effectiveness_factor: number;
  baseline_dangerous_minutes: number;
  projected_dangerous_minutes: number;
  avoided_dangerous_minutes: number;
  baseline_cumulative_exceedance: number;
  projected_cumulative_exceedance: number;
  baseline_heat_score: number;
  projected_heat_score: number;
  baseline_priority_score: number;
  projected_priority_score: number;
  baseline_rank: number;
  projected_rank: number;
  rank_change: number;
  confidence: number;
  assumptions: {
    exposure_reduction_pct: number;
    planning_assumption_only: boolean;
  };
}

export interface ExplanationResult {
  asset_id: string;
  rank: number;
  priority_score: number;
  priority_category: string;
  summary_explanation: string;
  key_drivers: string[];
  structured_evidence: {
    dangerous_minutes: number;
    persistence_minutes: number;
    peak_hour: number;
    shade_deficit: number;
    zero_vehicle_pct: number;
    route_count: number;
  };
}
