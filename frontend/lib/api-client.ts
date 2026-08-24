import { z } from "zod";
import * as T from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function fetcher<S extends z.ZodTypeAny>(
  url: string,
  options?: RequestInit,
  schema?: S
): Promise<z.infer<S>> {
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
  });

  if (!response.ok) {
    throw new ApiError(`HTTP error! Status: ${response.status}`, response.status);
  }

  const data = await response.json();
  
  if (schema) {
    const parseResult = schema.safeParse(data);
    if (!parseResult.success) {
      console.error(`Zod validation error for URL ${url}:`, parseResult.error);
      // Return unvalidated data as fallback in case schemas deviate slightly
      return data;
    }
    return parseResult.data;
  }

  return data;
}

export const apiClient = {
  getCities: async (): Promise<T.City[]> => {
    return fetcher(`${BASE_URL}/api/v1/cities`, { method: "GET" }, z.array(T.CitySchema));
  },

  createAnalysis: async (request: T.AnalysisRequest): Promise<T.AnalysisResponse> => {
    return fetcher(
      `${BASE_URL}/api/v1/analysis`,
      {
        method: "POST",
        body: JSON.stringify(request),
      },
      T.AnalysisResponseSchema
    );
  },

  getRankings: async (analysisId: string, weights?: T.Weights): Promise<T.RankingItem[]> => {
    let url = `${BASE_URL}/api/v1/analyses/${analysisId}/rankings`;
    if (weights) {
      const params = new URLSearchParams({
        heat: weights.heat.toString(),
        shade: weights.shade.toString(),
        vulnerability: weights.vulnerability.toString(),
        transit: weights.transit.toString(),
      });
      url += `?${params.toString()}`;
    }
    return fetcher(url, { method: "GET" }, z.array(T.RankingItemSchema));
  },

  getMapData: async (analysisId: string, weights?: T.Weights): Promise<any> => {
    let url = `${BASE_URL}/api/v1/analyses/${analysisId}/map-data`;
    if (weights) {
      const params = new URLSearchParams({
        heat: weights.heat.toString(),
        shade: weights.shade.toString(),
        vulnerability: weights.vulnerability.toString(),
        transit: weights.transit.toString(),
      });
      url += `?${params.toString()}`;
    }
    return fetcher(url, { method: "GET" });
  },

  getAssetDetails: async (assetId: string): Promise<T.AssetDetails> => {
    return fetcher(`${BASE_URL}/api/v1/assets/${assetId}`, { method: "GET" }, T.AssetDetailsSchema);
  },

  getAssetTimeSeries: async (assetId: string): Promise<T.TimeSeriesPoint[]> => {
    return fetcher(
      `${BASE_URL}/api/v1/assets/${assetId}/timeseries`,
      { method: "GET" },
      z.array(T.TimeSeriesPointSchema)
    );
  },

  simulateIntervention: async (
    request: T.InterventionRequest,
    weights?: T.Weights
  ): Promise<T.InterventionResponse> => {
    let url = `${BASE_URL}/api/v1/interventions/simulate`;
    if (weights) {
      const params = new URLSearchParams({
        heat: weights.heat.toString(),
        shade: weights.shade.toString(),
        vulnerability: weights.vulnerability.toString(),
        transit: weights.transit.toString(),
      });
      url += `?${params.toString()}`;
    }
    return fetcher(
      url,
      {
        method: "POST",
        body: JSON.stringify(request),
      },
      T.InterventionResponseSchema
    );
  },

  getExplanation: async (question: string): Promise<T.ExplanationResponse> => {
    return fetcher(
      `${BASE_URL}/api/v1/explanations`,
      {
        method: "POST",
        body: JSON.stringify({ question }),
      },
      T.ExplanationResponseSchema
    );
  },

  getReport: async (analysisId: string, limit = 20): Promise<any> => {
    return fetcher(
      `${BASE_URL}/api/v1/reports/${analysisId}?limit=${limit}`,
      { method: "GET" }
    );
  },
};
