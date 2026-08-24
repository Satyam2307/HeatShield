"use client";

import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ShieldAlert, TrendingDown, ArrowDownRight, RefreshCw, BarChart3, AlertTriangle } from "lucide-react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, Legend } from "recharts";
import { AssetDetails } from "@/lib/types";
import { apiClient } from "@/lib/api-client";

interface InterventionSimulatorProps {
  detail: AssetDetails;
  weights: any;
}

export default function InterventionSimulator({
  detail,
  weights,
}: InterventionSimulatorProps) {
  const [scenario, setScenario] = useState<"conservative" | "moderate" | "high">("moderate");

  // Fetch simulation results from API route
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["simulate-intervention", detail.id, scenario, weights],
    queryFn: () =>
      apiClient.simulateIntervention(
        {
          analysis_id: "analysis-001",
          asset_id: detail.id,
          intervention_type: "shade_structure",
          scenario,
        },
        weights
      ),
  });

  const chartData = data
    ? [
        {
          name: "Dangerous Exposure (mins)",
          Baseline: data.baseline_dangerous_minutes,
          Projected: data.projected_dangerous_minutes,
        },
        {
          name: "Priority Score",
          Baseline: data.baseline_priority_score,
          Projected: data.projected_priority_score,
        },
      ]
    : [];

  return (
    <div className="space-y-6 select-none">
      {/* Simulation Scenario Selectors */}
      <div className="space-y-2">
        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
          Intervention: Shade Structure
        </label>
        <div className="grid grid-cols-3 gap-2 bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs font-bold">
          {(["conservative", "moderate", "high"] as const).map((scen) => (
            <button
              key={scen}
              onClick={() => setScenario(scen)}
              className={`py-2 rounded-md capitalize transition-all ${
                scenario === scen
                  ? "bg-white text-slate-900 shadow-sm border border-slate-200/50"
                  : "text-slate-500 hover:text-slate-800"
              }`}
            >
              {scen}
            </button>
          ))}
        </div>
        <p className="text-[10px] text-slate-400">
          Scenarios assume: Conservative (20% heat reduction), Moderate (35%), High (50%).
        </p>
      </div>

      {isLoading ? (
        <div className="py-12 flex flex-col items-center justify-center gap-3 text-slate-400">
          <RefreshCw className="h-6 w-6 animate-spin text-red-500" />
          <span className="text-xs font-medium">Running shade simulation...</span>
        </div>
      ) : isError || !data ? (
        <div className="py-6 text-center border border-red-100 bg-red-50 text-red-700 rounded-lg text-xs space-y-2">
          <span>Failed to simulate scenario.</span>
          <button
            onClick={() => refetch()}
            className="block mx-auto bg-white border border-red-200 px-2.5 py-1 rounded shadow-sm font-semibold"
          >
            Retry
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Key Simulation Results */}
          <div className="grid grid-cols-2 gap-3.5">
            {/* Exposure Reduction Card */}
            <div className="border border-slate-150 rounded-lg p-3 bg-slate-50 relative overflow-hidden">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                Exposure Reduction
              </span>
              <div className="flex items-baseline gap-1.5 mt-1">
                <span className="text-3xl font-extrabold text-emerald-600">
                  -{data.exposure_reduction_pct}%
                </span>
              </div>
              <div className="text-[9px] text-emerald-700 font-semibold mt-1">
                Avoided: {data.avoided_dangerous_minutes} mins
              </div>
            </div>

            {/* Rank Shift Card */}
            <div className="border border-slate-150 rounded-lg p-3 bg-slate-50">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                Projected Rank Shift
              </span>
              <div className="flex items-baseline gap-1 mt-1">
                <span className="text-3xl font-extrabold text-slate-900">
                  {detail.rank} &rarr; {detail.rank + data.rank_change}
                </span>
              </div>
              <div className="text-[9px] text-slate-500 font-semibold mt-1 flex items-center gap-0.5">
                <ArrowDownRight className="h-3.5 w-3.5 text-emerald-600" />
                <span>Dropped {data.rank_change} places in priority queue</span>
              </div>
            </div>
          </div>

          {/* Comparison Bar Chart */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <BarChart3 className="h-4.5 w-4.5 text-slate-400" />
              <span>Before vs. After Intervention</span>
            </h3>
            <div className="border border-slate-150 rounded-xl p-3 bg-white h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ left: -25, right: 5, top: 10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="name" tick={{ fontSize: 9, fontWeight: 500 }} />
                  <YAxis tick={{ fontSize: 9 }} />
                  <ChartTooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="bg-slate-950 text-white border border-slate-800 p-2.5 shadow-md rounded text-xs space-y-1">
                            <span className="font-bold block border-b border-slate-800 pb-1 mb-1 text-[10px] text-slate-400">
                              {payload[0].payload.name}
                            </span>
                            <div className="flex justify-between gap-4">
                              <span>Baseline:</span>
                              <span className="font-bold text-red-400">{payload[0].value}</span>
                            </div>
                            <div className="flex justify-between gap-4">
                              <span>Projected:</span>
                              <span className="font-bold text-emerald-400">{payload[1].value}</span>
                            </div>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: 9 }} />
                  <Bar dataKey="Baseline" fill="#ef4444" radius={[4, 4, 0, 0]} barSize={20} />
                  <Bar dataKey="Projected" fill="#10b981" radius={[4, 4, 0, 0]} barSize={20} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Assumption Box */}
          <div className="bg-slate-100 border border-slate-200 rounded-xl p-3.5 space-y-2 text-xs">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
              Simulation Parameters & Assumptions
            </span>
            <p className="text-slate-600 leading-relaxed text-[11px]">
              {data.assumptions}
            </p>
            <div className="flex gap-1.5 items-start text-[10.5px] font-semibold text-amber-700 leading-normal border-t border-slate-200/60 pt-2">
              <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0" />
              <span>This is a planning scenario, not a final engineering estimate.</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
