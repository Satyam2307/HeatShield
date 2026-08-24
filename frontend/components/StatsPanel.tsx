"use client";

import React from "react";
import { ShieldAlert, TrendingUp, HelpCircle, Layers } from "lucide-react";
import { RankingItem } from "@/lib/types";

interface StatsPanelProps {
  items: RankingItem[];
  onSelectTopStop: (stopId: string) => void;
}

export default function StatsPanel({ items, onSelectTopStop }: StatsPanelProps) {
  const totalStops = items.length;
  const criticalStops = items.filter((s) => s.priority_category === "Critical").length;
  
  const avgDangerousMins = totalStops > 0 
    ? Math.round(items.reduce((sum, s) => sum + s.dangerous_minutes, 0) / totalStops)
    : 0;

  const topStop = items[0];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 p-6 bg-white border-b border-slate-200">
      {/* Total Stops Card */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex items-start gap-4">
        <div className="bg-blue-100 text-blue-700 p-2.5 rounded-lg">
          <Layers className="h-5 w-5" />
        </div>
        <div>
          <span className="text-slate-500 text-xs font-medium uppercase tracking-wider block">Stops Analyzed</span>
          <span className="text-2xl font-bold text-slate-800">{totalStops}</span>
          <span className="text-slate-400 text-xs block mt-0.5">Hartford municipal area</span>
        </div>
      </div>

      {/* Critical Stops Card */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex items-start gap-4">
        <div className="bg-red-100 text-red-700 p-2.5 rounded-lg">
          <ShieldAlert className="h-5 w-5" />
        </div>
        <div>
          <span className="text-slate-500 text-xs font-medium uppercase tracking-wider block">Critical Prioritizations</span>
          <span className="text-2xl font-bold text-red-600">{criticalStops}</span>
          <span className="text-slate-400 text-xs block mt-0.5">Priority score &ge; 80 / 100</span>
        </div>
      </div>

      {/* Average Exposure Card */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex items-start gap-4">
        <div className="bg-amber-100 text-amber-700 p-2.5 rounded-lg">
          <TrendingUp className="h-5 w-5" />
        </div>
        <div>
          <span className="text-slate-500 text-xs font-medium uppercase tracking-wider block">Avg. Exposure Duration</span>
          <span className="text-2xl font-bold text-slate-800">{avgDangerousMins} min</span>
          <span className="text-slate-400 text-xs block mt-0.5">Time above risk threshold</span>
        </div>
      </div>

      {/* Top Priority Stop Card */}
      {topStop ? (
        <div className="bg-red-50 border border-red-100 hover:border-red-200 cursor-pointer rounded-xl p-4 flex items-start gap-4 transition-all"
             onClick={() => onSelectTopStop(topStop.bus_stop_id)}>
          <div className="bg-red-500 text-white p-2.5 rounded-lg shadow-sm">
            <ShieldAlert className="h-5 w-5 animate-pulse" />
          </div>
          <div className="flex-1 min-w-0">
            <span className="text-red-700 text-xs font-semibold uppercase tracking-wider block">Top Recommendation</span>
            <span className="text-base font-bold text-red-950 truncate block mt-0.5" title={topStop.stop_name}>
              {topStop.stop_name}
            </span>
            <span className="text-red-600 text-xs font-semibold block mt-0.5">
              Rank #1 — Score {topStop.priority_score}
            </span>
          </div>
        </div>
      ) : (
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex items-start gap-4">
          <div className="bg-slate-200 text-slate-400 p-2.5 rounded-lg">
            <HelpCircle className="h-5 w-5" />
          </div>
          <div>
            <span className="text-slate-500 text-xs font-medium uppercase tracking-wider block">Top Recommendation</span>
            <span className="text-slate-800 text-sm font-semibold block mt-1">No data loaded</span>
          </div>
        </div>
      )}
    </div>
  );
}
