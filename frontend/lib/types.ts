import { z } from "zod";

// City schema & type
export const CitySchema = z.object({
  id: z.string(),
  name: z.string(),
  state: z.string(),
  timezone: z.string(),
});
export type City = z.infer<typeof CitySchema>;

// Weights schema & type
export const WeightsSchema = z.object({
  heat: z.number(),
  shade: z.number(),
  vulnerability: z.number(),
  transit: z.number(),
});
export type Weights = z.infer<typeof WeightsSchema>;

// AnalysisRequest schema & type
export const AnalysisRequestSchema = z.object({
  city_id: z.string(),
  start_time: z.string(),
  end_time: z.string(),
  heat_metric: z.string(),
  heat_unit: z.string(),
  danger_threshold: z.number(),
  weights: WeightsSchema,
});
export type AnalysisRequest = z.infer<typeof AnalysisRequestSchema>;

// AnalysisResponse schema & type
export const AnalysisResponseSchema = z.object({
  analysis_id: z.string(),
  city_id: z.string(),
  start_time: z.string(),
  end_time: z.string(),
  heat_metric: z.string(),
  danger_threshold: z.number(),
  weights: WeightsSchema,
  status: z.enum(["processing", "completed", "failed"]),
  created_at: z.string(),
});
export type AnalysisResponse = z.infer<typeof AnalysisResponseSchema>;

// RankingItem schema & type
export const RankingItemSchema = z.object({
  rank: z.number(),
  bus_stop_id: z.string(),
  stop_name: z.string(),
  priority_category: z.enum(["Critical", "High", "Moderate", "Low"]),
  priority_score: z.number(),
  dangerous_minutes: z.number(),
  cumulative_exceedance: z.number(),
  shade_deficit: z.number(), // 0 to 100 or fraction
  vulnerability_score: z.number(),
  transit_score: z.number(),
  routes_served: z.array(z.string()),
  recommended_intervention: z.string(),
  latitude: z.number(),
  longitude: z.number(),
});
export type RankingItem = z.infer<typeof RankingItemSchema>;

// ScoreBreakdown schema
export const ScoreBreakdownSchema = z.object({
  heat_score: z.number(),
  shade_score: z.number(),
  vulnerability_score: z.number(),
  transit_score: z.number(),
});
export type ScoreBreakdown = z.infer<typeof ScoreBreakdownSchema>;

// CommunityVulnerability indicators
export const CommunityVulnerabilitySchema = z.object({
  zero_vehicle_fraction: z.number(),
  older_adult_fraction: z.number(),
  children_fraction: z.number(),
  median_income: z.number(),
  population_density: z.number().optional(),
});
export type CommunityVulnerability = z.infer<typeof CommunityVulnerabilitySchema>;

// TransitImportance indicators
export const TransitImportanceSchema = z.object({
  route_count: z.number(),
  service_frequency: z.number(), // buses per hour
  ridership: z.number().nullable(), // ridership count (if observed) or null if estimated/proxy
  status: z.enum(["Observed", "Estimated", "Proxy"]),
});
export type TransitImportance = z.infer<typeof TransitImportanceSchema>;

// AssetDetails schema & type
export const AssetDetailsSchema = z.object({
  id: z.string(),
  name: z.string(),
  routes_served: z.array(z.string()),
  priority_score: z.number(),
  rank: z.number(),
  score_breakdown: ScoreBreakdownSchema,
  average_heat: z.number(),
  maximum_heat: z.number(),
  dangerous_minutes: z.number(),
  longest_continuous_dangerous_period: z.number(), // in minutes
  cumulative_exceedance: z.number(),
  shade_deficit: z.number(),
  community_vulnerability: CommunityVulnerabilitySchema,
  transit_importance: TransitImportanceSchema,
  data_coverage: z.number(), // fraction or percentage (e.g. 0.95 or 95)
  data_source: z.string(),
  recommendation_explanation: z.string(),
  latitude: z.number(),
  longitude: z.number(),
});
export type AssetDetails = z.infer<typeof AssetDetailsSchema>;

// TimeSeriesPoint schema & type
export const TimeSeriesPointSchema = z.object({
  timestamp: z.string(),
  value: z.number(),
});
export type TimeSeriesPoint = z.infer<typeof TimeSeriesPointSchema>;

// InterventionRequest schema & type
export const InterventionRequestSchema = z.object({
  analysis_id: z.string(),
  asset_id: z.string(),
  intervention_type: z.string(), // e.g. "shade_structure"
  scenario: z.enum(["conservative", "moderate", "high"]),
});
export type InterventionRequest = z.infer<typeof InterventionRequestSchema>;

// InterventionResponse schema & type
export const InterventionResponseSchema = z.object({
  baseline_dangerous_minutes: z.number(),
  projected_dangerous_minutes: z.number(),
  avoided_dangerous_minutes: z.number(),
  exposure_reduction_pct: z.number(),
  baseline_priority_score: z.number(),
  projected_priority_score: z.number(),
  rank_change: z.number(),
  assumptions: z.string(),
});
export type InterventionResponse = z.infer<typeof InterventionResponseSchema>;

// ExplanationResponse schema & type
export const ExplanationResponseSchema = z.object({
  explanation: z.string(),
});
export type ExplanationResponse = z.infer<typeof ExplanationResponseSchema>;
