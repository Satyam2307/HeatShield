"use client";

import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, AlertCircle, RefreshCw, Layers } from "lucide-react";

import { apiClient } from "@/lib/api-client";
import { Weights } from "@/lib/types";

// Component imports
import DashboardHeader from "@/components/DashboardHeader";
import StatsPanel from "@/components/StatsPanel";
import SidebarWeights from "@/components/SidebarWeights";
import MapComponent from "@/components/MapComponent";
import RankingsTable from "@/components/RankingsTable";
import DetailPanel from "@/components/DetailPanel";
import NaturalLanguageBox from "@/components/NaturalLanguageBox";
import MethodologyModal from "@/components/MethodologyModal";

export default function Dashboard() {
  const [selectedStopId, setSelectedStopId] = useState<string | null>("stop-001");
  const [dangerThreshold, setDangerThreshold] = useState<number>(95);
  const [weights, setWeights] = useState<Weights>({
    heat: 0.40,
    shade: 0.25,
    vulnerability: 0.20,
    transit: 0.15,
  });
  const [isMethodologyOpen, setIsMethodologyOpen] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  // Fetch Rankings based on current weights
  const {
    data: rankings,
    isLoading: isRankingsLoading,
    isError: isRankingsError,
    refetch: refetchRankings,
  } = useQuery({
    queryKey: ["rankings", weights],
    queryFn: () => apiClient.getRankings("analysis-001", weights),
  });

  // Fetch Details of the selected stop
  const {
    data: selectedDetail,
    isLoading: isDetailLoading,
    isError: isDetailError,
    refetch: refetchDetail,
  } = useQuery({
    queryKey: ["asset-details", selectedStopId],
    queryFn: () => (selectedStopId ? apiClient.getAssetDetails(selectedStopId) : null),
    enabled: !!selectedStopId,
  });

  // Fetch hourly Time Series of the selected stop
  const {
    data: timeSeries,
    isLoading: isTimeSeriesLoading,
    isError: isTimeSeriesError,
    refetch: refetchTimeSeries,
  } = useQuery({
    queryKey: ["asset-timeseries", selectedStopId],
    queryFn: () => (selectedStopId ? apiClient.getAssetTimeSeries(selectedStopId) : []),
    enabled: !!selectedStopId,
  });

  // Handle CSV Export
  const handleExportCsv = async () => {
    setIsExporting(true);
    try {
      const report = await apiClient.getReport("analysis-001", 100);
      const headers = [
        "Rank",
        "Stop ID",
        "Stop Name",
        "Latitude",
        "Longitude",
        "Priority Score",
        "Priority Category",
        "Dangerous Minutes",
        "Cumulative Exceedance (F-min)",
        "Shade Deficit (%)",
        "Routes Count",
        "Vulnerability Score",
        "Median Income ($)",
        "Zero-Vehicle (%)",
        "Recommended Intervention",
      ];
      
      const rows = report.results.map((item: any) => [
        item.rank,
        item.stop_id,
        `"${item.stop_name}"`,
        item.latitude,
        item.longitude,
        item.priority_score,
        item.priority_category,
        item.dangerous_minutes,
        item.cumulative_exceedance,
        item.shade_deficit_pct,
        item.routes_count,
        item.vulnerability_score,
        item.median_income,
        item.zero_vehicle_pct,
        `"${item.recommended_intervention}"`,
      ]);

      const csvContent = [headers.join(","), ...rows.map((e: any) => e.join(","))].join("\n");
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", `hartford_shade_stop_priority_report.csv`);
      link.style.visibility = "hidden";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error("Exporting report failed:", err);
    } finally {
      setIsExporting(false);
    }
  };

  const handleRetryAll = () => {
    refetchRankings();
    if (selectedStopId) {
      refetchDetail();
      refetchTimeSeries();
    }
  };

  return (
    <div className="flex flex-col flex-1 min-h-screen">
      {/* Top Banner Header */}
      <DashboardHeader
        onOpenMethodology={() => setIsMethodologyOpen(true)}
        onExportCsv={handleExportCsv}
        isExporting={isExporting}
        dangerThreshold={dangerThreshold}
      />

      {/* Local Fixture warning indicator */}
      <div className="bg-amber-50 border-b border-amber-200 px-6 py-2 flex items-center justify-between text-xs text-amber-800">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-4.5 w-4.5 text-amber-600 shrink-0" />
          <span className="font-medium">
            Demo Mode: Showing precomputed FortyGuard heat and ACS vulnerability metrics for Hartford. Next.js Route Handler active.
          </span>
        </div>
      </div>

      {isRankingsError ? (
        /* Error State Screen */
        <div className="flex-1 flex flex-col items-center justify-center p-6 bg-slate-50 gap-4 text-center">
          <AlertCircle className="h-12 w-12 text-red-500" />
          <div>
            <h3 className="text-lg font-bold text-slate-800">Failed to load prioritizing data</h3>
            <p className="text-sm text-slate-500 mt-1 max-w-md">
              There was an issue communicating with the local planning repository. Please verify your environment and click Retry.
            </p>
          </div>
          <button
            onClick={handleRetryAll}
            className="flex items-center gap-2 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs px-4.5 py-2.5 rounded-lg shadow transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Retry Connection</span>
          </button>
        </div>
      ) : isRankingsLoading ? (
        /* Dashboard Loading State */
        <div className="flex-1 flex flex-col items-center justify-center p-6 bg-slate-50 gap-4">
          <RefreshCw className="h-8 w-8 text-red-500 animate-spin" />
          <div className="text-center">
            <h3 className="text-base font-bold text-slate-800">Compiling Priority Rankings</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Normalizing thermal indices, shade deficits, and ACS census tracts...
            </p>
          </div>
        </div>
      ) : (
        /* Standard Loaded Dashboard */
        <div className="flex flex-col flex-1">
          {/* Summary KPIs */}
          <StatsPanel
            items={rankings || []}
            onSelectTopStop={(stopId) => setSelectedStopId(stopId)}
          />

          {/* Main Dashboard Workspace */}
          <div className="flex-1 flex flex-col lg:flex-row overflow-hidden bg-slate-50">
            {/* Left Weighting Sidebar */}
            <SidebarWeights
              initialWeights={weights}
              dangerThreshold={dangerThreshold}
              onWeightsChange={(newWeights) => setWeights(newWeights)}
              onThresholdChange={(newThresh) => setDangerThreshold(newThresh)}
            />

            {/* Center Area: Map, Table, and NL Explain Box */}
            <div className="flex-1 p-6 overflow-y-auto flex flex-col gap-6">
              {/* Top half: Map & Legend */}
              <div className="h-[450px] flex flex-col">
                <MapComponent
                  items={rankings || []}
                  selectedStopId={selectedStopId}
                  onSelectStop={(stopId) => setSelectedStopId(stopId)}
                />
              </div>

              {/* Bottom half: Action Queue Table */}
              <div className="flex-1">
                <RankingsTable
                  items={rankings || []}
                  selectedStopId={selectedStopId}
                  onSelectStop={(stopId) => setSelectedStopId(stopId)}
                />
              </div>

              {/* Natural Language Box */}
              <div className="flex-1">
                <NaturalLanguageBox />
              </div>
            </div>

            {/* Right side Detail Panel drawer */}
            {selectedStopId && selectedDetail && (
              <DetailPanel
                detail={selectedDetail}
                timeSeries={timeSeries || []}
                dangerThreshold={dangerThreshold}
                onClose={() => setSelectedStopId(null)}
                weights={weights}
              />
            )}
          </div>
        </div>
      )}

      {/* Floating Methodology Panel Modal */}
      <MethodologyModal
        isOpen={isMethodologyOpen}
        onClose={() => setIsMethodologyOpen(false)}
      />
    </div>
  );
}
