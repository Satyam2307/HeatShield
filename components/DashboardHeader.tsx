"use client";

import React from "react";
import { FileText, Download, HelpCircle, Activity } from "lucide-react";

interface DashboardHeaderProps {
  onOpenMethodology: () => void;
  onExportCsv: () => void;
  isExporting: boolean;
  dangerThreshold: number;
}

export default function DashboardHeader({
  onOpenMethodology,
  onExportCsv,
  isExporting,
  dangerThreshold,
}: DashboardHeaderProps) {
  return (
    <header className="bg-slate-900 text-white border-b border-slate-800 px-6 py-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div className="flex items-center gap-3">
        <div className="bg-red-500 text-white p-2 rounded-lg shadow-inner">
          <Activity className="h-6 w-6" />
        </div>
        <div>
          <h1 className="text-xl font-bold tracking-tight flex items-center gap-2">
            HeatShield: <span className="text-red-400 font-semibold">ShadeStop</span>
          </h1>
          <p className="text-xs text-slate-400">
            Urban Heat Mitigation & Bus Stop Shelter Prioritization Tool
          </p>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3 text-sm">
        {/* Active Metadata Info */}
        <div className="bg-slate-800 border border-slate-700 px-3 py-1.5 rounded-md flex flex-wrap gap-x-4 gap-y-1 text-slate-300">
          <div>
            <span className="text-slate-500 font-semibold uppercase text-[10px] block leading-none mb-0.5">City Target</span>
            <span className="font-semibold text-white">Hartford, CT</span>
          </div>
          <div className="border-l border-slate-700 pl-4">
            <span className="text-slate-500 font-semibold uppercase text-[10px] block leading-none mb-0.5">Date Range</span>
            <span>July 15, 2023</span>
          </div>
          <div className="border-l border-slate-700 pl-4">
            <span className="text-slate-500 font-semibold uppercase text-[10px] block leading-none mb-0.5">Time Frame</span>
            <span>10:00 AM - 6:00 PM</span>
          </div>
          <div className="border-l border-slate-700 pl-4">
            <span className="text-slate-500 font-semibold uppercase text-[10px] block leading-none mb-0.5">Metric & Threshold</span>
            <span>Heat Index &ge; {dangerThreshold}&deg;F</span>
          </div>
        </div>

        {/* Action buttons */}
        <button
          onClick={onOpenMethodology}
          className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-slate-600 text-slate-200 px-3.5 py-1.5 rounded-md transition-colors font-medium shadow-sm"
        >
          <HelpCircle className="h-4 w-4" />
          <span>Methodology</span>
        </button>

        <button
          onClick={onExportCsv}
          disabled={isExporting}
          className="flex items-center gap-2 bg-red-600 hover:bg-red-500 disabled:bg-slate-800 text-white disabled:text-slate-500 px-3.5 py-1.5 rounded-md transition-all font-medium shadow-md hover:shadow-lg disabled:shadow-none"
        >
          <Download className="h-4 w-4" />
          <span>{isExporting ? "Exporting..." : "Export CSV"}</span>
        </button>
      </div>
    </header>
  );
}
