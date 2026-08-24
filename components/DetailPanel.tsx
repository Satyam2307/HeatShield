"use client";

import React, { useState } from "react";
import { X, ShieldAlert, BarChart3, LineChart as ChartIcon, Thermometer, ShieldAlert as WarningIcon, Users, Bus, FileText, ChevronRight } from "lucide-react";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, ReferenceLine, BarChart, Bar } from "recharts";
import { AssetDetails, TimeSeriesPoint } from "@/lib/types";
import InterventionSimulator from "./InterventionSimulator";

interface DetailPanelProps {
  detail: AssetDetails;
  timeSeries: TimeSeriesPoint[];
  dangerThreshold: number;
  onClose: () => void;
  weights: any;
}

export default function DetailPanel({
  detail,
  timeSeries,
  dangerThreshold,
  onClose,
  weights,
}: DetailPanelProps) {
  const [activeTab, setActiveTab] = useState<"metrics" | "simulator">("metrics");

  const scoreData = [
    { name: "Heat Exposure", score: detail.score_breakdown.heat_score, fill: "#ef4444" },
    { name: "Shade Deficit", score: detail.score_breakdown.shade_score, fill: "#f97316" },
    { name: "Vulnerability", score: detail.score_breakdown.vulnerability_score, fill: "#eab308" },
    { name: "Transit", score: detail.score_breakdown.transit_score, fill: "#3b82f6" },
  ];

  // Map timeseries date strings to readable labels (e.g. 10:00 AM)
  const chartData = timeSeries.map((pt) => {
    const date = new Date(pt.timestamp);
    // Parse to local hour string (e.g., "10:00 AM")
    const label = date.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
      timeZone: "America/New_York",
    });
    return {
      time: label,
      temp: pt.value,
    };
  });

  const getPriorityColor = (category: string) => {
    switch (category) {
      case "Critical":
        return "text-red-600";
      case "High":
        return "text-orange-600";
      case "Moderate":
        return "text-yellow-600";
      default:
        return "text-blue-600";
    }
  };

  return (
    <div className="w-full lg:w-[480px] bg-white border-l border-slate-200 shadow-xl flex flex-col shrink-0 overflow-hidden relative">
      {/* Detail Panel Header */}
      <div className="p-4 border-b border-slate-200 bg-slate-900 text-white flex items-center justify-between">
        <div className="min-w-0">
          <span className="text-[10px] text-red-400 font-bold uppercase tracking-wider block">
            Selected Location (Rank #{detail.rank})
          </span>
          <h2 className="text-base font-bold truncate pr-2" title={detail.name}>
            {detail.name}
          </h2>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-white p-1 hover:bg-slate-800 rounded transition-colors"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 bg-slate-50 select-none">
        <button
          onClick={() => setActiveTab("metrics")}
          className={`flex-1 py-3 text-xs font-bold text-center border-b-2 transition-all flex items-center justify-center gap-2 ${
            activeTab === "metrics"
              ? "border-b-red-500 text-red-600 bg-white"
              : "border-b-transparent text-slate-500 hover:text-slate-800"
          }`}
        >
          <BarChart3 className="h-4 w-4" />
          <span>Evidence & Metrics</span>
        </button>
        <button
          onClick={() => setActiveTab("simulator")}
          className={`flex-1 py-3 text-xs font-bold text-center border-b-2 transition-all flex items-center justify-center gap-2 ${
            activeTab === "simulator"
              ? "border-b-red-500 text-red-600 bg-white"
              : "border-b-transparent text-slate-500 hover:text-slate-800"
          }`}
        >
          <ShieldAlert className="h-4 w-4" />
          <span>Shade Simulator</span>
        </button>
      </div>

      {/* Panel Scrollable Content */}
      <div className="flex-1 overflow-y-auto p-5 space-y-6">
        {activeTab === "metrics" ? (
          <>
            {/* Recommendation Summary */}
            <div className="bg-red-50/50 border border-red-100 rounded-xl p-4 space-y-2">
              <h3 className="text-xs font-bold text-red-800 uppercase tracking-wider flex items-center gap-1.5">
                <WarningIcon className="h-4 w-4 text-red-600" />
                <span>Intervention Recommendation</span>
              </h3>
              <p className="text-xs text-slate-700 leading-relaxed">
                {detail.recommendation_explanation}
              </p>
            </div>

            {/* Score Summary Grid */}
            <div className="grid grid-cols-2 gap-3.5">
              <div className="bg-slate-50 border border-slate-150 rounded-lg p-3">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  Priority Score
                </span>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className="text-3xl font-extrabold text-slate-900">
                    {detail.priority_score}
                  </span>
                  <span className="text-slate-400 text-xs font-medium">/ 100</span>
                </div>
              </div>
              <div className="bg-slate-50 border border-slate-150 rounded-lg p-3">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  Bus Routes Served
                </span>
                <div className="flex items-baseline mt-1 font-bold text-slate-900 text-2xl">
                  {detail.routes_served.length}
                </div>
                <div className="text-[9px] text-slate-400 truncate mt-0.5">
                  {detail.routes_served.join(", ")}
                </div>
              </div>
            </div>

            {/* Score Breakdown Bar Chart */}
            <div className="space-y-2">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <BarChart3 className="h-4 w-4 text-slate-400" />
                <span>Weighting Component Scores</span>
              </h3>
              <div className="border border-slate-150 rounded-xl p-3 bg-white h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={scoreData} layout="vertical" margin={{ left: -10, right: 10, top: 10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                    <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 9 }} />
                    <YAxis dataKey="name" type="category" width={85} tick={{ fontSize: 9, fontWeight: 500 }} />
                    <ChartTooltip
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          return (
                            <div className="bg-white border border-slate-200 p-2 shadow-md rounded text-[10px]">
                              <span className="font-bold text-slate-800">{payload[0].name}</span>:{" "}
                              <span className="font-semibold text-red-600">{payload[0].value} / 100</span>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Bar dataKey="score" radius={[0, 4, 4, 0]} barSize={14} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Heat Exposure & Line Chart */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <Thermometer className="h-4.5 w-4.5 text-slate-400" />
                <span>Hourly Thermal Profile (Jul 15)</span>
              </h3>

              {/* Temperature line chart */}
              <div className="border border-slate-150 rounded-xl p-3 bg-white h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="time" tick={{ fontSize: 8 }} />
                    <YAxis domain={["dataMin - 2", "dataMax + 2"]} tick={{ fontSize: 9 }} />
                    <ChartTooltip
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          return (
                            <div className="bg-slate-900 text-white p-2 shadow-md rounded text-[10px]">
                              <span className="font-medium">{payload[0].payload.time}</span>:{" "}
                              <span className="font-bold text-red-400">{payload[0].value}&deg;F</span>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    {/* Danger threshold reference line */}
                    <ReferenceLine
                      y={dangerThreshold}
                      stroke="#ef4444"
                      strokeDasharray="3 3"
                      label={{
                        value: `Threshold ${dangerThreshold}°F`,
                        position: "top",
                        fill: "#ef4444",
                        fontSize: 8,
                        fontWeight: "bold",
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="temp"
                      stroke="#dc2626"
                      strokeWidth={2.5}
                      dot={{ r: 3, stroke: "#991b1b", strokeWidth: 1 }}
                      activeDot={{ r: 5 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Thermal Statistics Grid */}
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="border border-slate-150 rounded-lg p-2.5 bg-slate-50">
                  <span className="text-slate-400 font-semibold block text-[9px] uppercase">Peak Temp</span>
                  <span className="font-bold text-slate-800 text-sm">{detail.maximum_heat}&deg;F</span>
                </div>
                <div className="border border-slate-150 rounded-lg p-2.5 bg-slate-50">
                  <span className="text-slate-400 font-semibold block text-[9px] uppercase">Average Temp</span>
                  <span className="font-bold text-slate-800 text-sm">{detail.average_heat}&deg;F</span>
                </div>
                <div className="border border-slate-150 rounded-lg p-2.5 bg-slate-50">
                  <span className="text-slate-400 font-semibold block text-[9px] uppercase">Dangerous minutes</span>
                  <span className="font-bold text-slate-800 text-sm">{detail.dangerous_minutes} mins</span>
                </div>
                <div className="border border-slate-150 rounded-lg p-2.5 bg-slate-50">
                  <span className="text-slate-400 font-semibold block text-[9px] uppercase">Longest continuous heat</span>
                  <span className="font-bold text-slate-800 text-sm">{detail.longest_continuous_dangerous_period} mins</span>
                </div>
              </div>
            </div>

            {/* Social & Vulnerability Indicators */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <Users className="h-4.5 w-4.5 text-slate-400" />
                <span>Community Vulnerability Indicators</span>
              </h3>
              <div className="border border-slate-150 rounded-xl divide-y divide-slate-100 bg-white overflow-hidden text-xs">
                <div className="p-3 flex justify-between">
                  <span className="text-slate-600 font-medium">Zero-Vehicle Households:</span>
                  <span className="font-bold text-slate-900">
                    {Math.round(detail.community_vulnerability.zero_vehicle_fraction * 100)}%
                  </span>
                </div>
                <div className="p-3 flex justify-between">
                  <span className="text-slate-600 font-medium">Older Adults (&ge; 65 years):</span>
                  <span className="font-bold text-slate-900">
                    {Math.round(detail.community_vulnerability.older_adult_fraction * 100)}%
                  </span>
                </div>
                <div className="p-3 flex justify-between">
                  <span className="text-slate-600 font-medium">Children (&le; 5 years):</span>
                  <span className="font-bold text-slate-900">
                    {Math.round(detail.community_vulnerability.children_fraction * 100)}%
                  </span>
                </div>
                <div className="p-3 flex justify-between">
                  <span className="text-slate-600 font-medium">Median Household Income:</span>
                  <span className="font-bold text-slate-900">
                    ${detail.community_vulnerability.median_income.toLocaleString()}
                  </span>
                </div>
              </div>
            </div>

            {/* Transit and Technical Metadata */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <Bus className="h-4.5 w-4.5 text-slate-400" />
                <span>Transit Importance</span>
              </h3>
              <div className="border border-slate-150 rounded-xl divide-y divide-slate-100 bg-white overflow-hidden text-xs">
                <div className="p-3 flex justify-between">
                  <span className="text-slate-600 font-medium">Transit Routes:</span>
                  <span className="font-bold text-slate-900">{detail.transit_importance.route_count} routes</span>
                </div>
                <div className="p-3 flex justify-between">
                  <span className="text-slate-600 font-medium">Service Frequency:</span>
                  <span className="font-bold text-slate-900">{detail.transit_importance.service_frequency} buses / hour</span>
                </div>
                <div className="p-3 flex justify-between">
                  <span className="text-slate-600 font-medium">Daily Ridership:</span>
                  <span className="font-bold text-slate-900">
                    {detail.transit_importance.ridership !== null
                      ? `${detail.transit_importance.ridership.toLocaleString()} boardings (${detail.transit_importance.status})`
                      : `No observed counts (${detail.transit_importance.status} proxy used)`}
                  </span>
                </div>
              </div>
            </div>

            <hr className="border-slate-200" />

            {/* Quality metadata */}
            <div className="bg-slate-100 border border-slate-200 rounded-xl p-3.5 text-[10px] text-slate-500 space-y-1">
              <div className="flex justify-between">
                <span>Data Completeness Score:</span>
                <span className="font-bold text-slate-700">{Math.round(detail.data_coverage * 100)}%</span>
              </div>
              <div className="flex justify-between">
                <span>Telemetry Source:</span>
                <span className="font-semibold text-slate-700 truncate max-w-[200px]" title={detail.data_source}>
                  {detail.data_source}
                </span>
              </div>
            </div>
          </>
        ) : (
          <InterventionSimulator
            detail={detail}
            weights={weights}
          />
        )}
      </div>
    </div>
  );
}
