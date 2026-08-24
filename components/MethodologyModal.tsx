"use client";

import React, { useState } from "react";
import { X, BookOpen, Layers, CheckCircle2, ShieldAlert, Sparkles } from "lucide-react";

interface MethodologyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type TabType = "formula" | "sources" | "assumptions";

export default function MethodologyModal({ isOpen, onClose }: MethodologyModalProps) {
  const [activeTab, setActiveTab] = useState<TabType>("formula");

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      {/* Modal Card */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-2xl w-full max-w-2xl flex flex-col max-h-[85vh] overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-slate-200 bg-slate-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-red-400" />
            <h2 className="text-base font-bold">Methodology & Data Sources</h2>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 hover:bg-slate-800 rounded transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Inner Tabs */}
        <div className="flex border-b border-slate-200 bg-slate-50 text-xs font-bold select-none">
          <button
            onClick={() => setActiveTab("formula")}
            className={`flex-1 py-3 text-center border-b-2 transition-all ${
              activeTab === "formula"
                ? "border-b-red-500 text-red-600 bg-white"
                : "border-b-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            Ranking Formulas
          </button>
          <button
            onClick={() => setActiveTab("sources")}
            className={`flex-1 py-3 text-center border-b-2 transition-all ${
              activeTab === "sources"
                ? "border-b-red-500 text-red-600 bg-white"
                : "border-b-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            Data Sources
          </button>
          <button
            onClick={() => setActiveTab("assumptions")}
            className={`flex-1 py-3 text-center border-b-2 transition-all ${
              activeTab === "assumptions"
                ? "border-b-red-500 text-red-600 bg-white"
                : "border-b-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            Assumptions & Limitations
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 text-sm text-slate-700 leading-relaxed">
          {activeTab === "formula" && (
            <div className="space-y-4">
              <div>
                <h3 className="font-bold text-slate-900 flex items-center gap-1.5 mb-1.5">
                  <Sparkles className="h-4.5 w-4.5 text-red-500" />
                  <span>Priority Scoring Model</span>
                </h3>
                <p className="text-xs text-slate-650">
                  HeatShield uses a multi-criteria decision analysis (MCDA) framework to score and rank Hartford's bus stops. The final priority score is calculated using four normalized percentile components:
                </p>
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 my-3 text-center">
                  <code className="text-xs font-bold text-slate-800 font-mono">
                    Priority Score = w_heat * Heat + w_shade * Shade + w_vuln * Vuln + w_transit * Transit
                  </code>
                  <p className="text-[10px] text-slate-400 mt-2">
                    Default weights: Heat (40%), Shade Deficit (25%), Vulnerability (20%), Transit Importance (15%)
                  </p>
                </div>
              </div>

              <hr className="border-slate-150" />

              <div>
                <h4 className="font-bold text-slate-800 text-xs mb-2">Component Specifications</h4>
                <ul className="space-y-3 text-xs">
                  <li className="flex items-start gap-2.5">
                    <span className="bg-red-100 text-red-700 text-[10px] font-bold px-1.5 py-0.5 rounded shrink-0">Heat</span>
                    <div>
                      <span className="font-semibold text-slate-900">Heat Exposure Score</span>: Combines cumulative exceedance, duration above threshold, and persistence (duration of longest heat event).
                      <br />
                      <code className="text-[10px] text-slate-500 font-mono">Heat = 0.50 * Exceedance + 0.30 * Duration + 0.20 * Persistence</code>
                    </div>
                  </li>
                  <li className="flex items-start gap-2.5">
                    <span className="bg-orange-100 text-orange-700 text-[10px] font-bold px-1.5 py-0.5 rounded shrink-0">Shade</span>
                    <div>
                      <span className="font-semibold text-slate-900">Shade Deficit Score</span>: Proxy derived from vegetation fraction, building heights, and impervious pavement surface cover in a 100-meter buffer around the stop.
                    </div>
                  </li>
                  <li className="flex items-start gap-2.5">
                    <span className="bg-yellow-100 text-yellow-700 text-[10px] font-bold px-1.5 py-0.5 rounded shrink-0">Vuln</span>
                    <div>
                      <span className="font-semibold text-slate-900">Community Vulnerability Score</span>: Calculated from ACS census indicators including households with zero vehicles, older adults (age &ge; 65), children (age &le; 5), and median household income.
                    </div>
                  </li>
                  <li className="flex items-start gap-2.5">
                    <span className="bg-blue-100 text-blue-700 text-[10px] font-bold px-1.5 py-0.5 rounded shrink-0">Transit</span>
                    <div>
                      <span className="font-semibold text-slate-900">Transit Importance Score</span>: Derived from route overlaps (route count), scheduled frequency, and observed average daily passenger ridership.
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          )}

          {activeTab === "sources" && (
            <div className="space-y-4">
              <h3 className="font-bold text-slate-900 flex items-center gap-1.5 mb-1 text-sm">
                <Layers className="h-4.5 w-4.5 text-red-500" />
                <span>Integrated Datasets</span>
              </h3>
              <p className="text-xs text-slate-500">
                To build an evidence-based mitigation strategy, three primary external layers were joined geospatially to the Hartford transit stop network:
              </p>

              <table className="w-full border-collapse text-left border border-slate-200 text-xs">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-bold uppercase text-[9px]">
                    <th className="p-2.5 border-r border-slate-200">Data Type</th>
                    <th className="p-2.5 border-r border-slate-200">Source Provider</th>
                    <th className="p-2.5">Application in Model</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  <tr>
                    <td className="p-2.5 border-r border-slate-200 font-semibold text-slate-900">Heat Observations</td>
                    <td className="p-2.5 border-r border-slate-200">FortyGuard Environmental Analytics</td>
                    <td className="p-2.5">Gridded surface heat index observations, cumulative exceedance minutes, and persistence durations.</td>
                  </tr>
                  <tr>
                    <td className="p-2.5 border-r border-slate-200 font-semibold text-slate-900">Social Vulnerability</td>
                    <td className="p-2.5 border-r border-slate-205 font-semibold">U.S. Census Bureau ACS (2022 5-Year)</td>
                    <td className="p-2.5">Tract-level household vehicle accessibility, age demographics, and median household income indicators.</td>
                  </tr>
                  <tr>
                    <td className="p-2.5 border-r border-slate-200 font-semibold text-slate-900">Transit Network</td>
                    <td className="p-2.5 border-r border-slate-200">CTtransit GTFS feed</td>
                    <td className="p-2.5">Bus stop coordinate verification, route counts, and boarding statistics.</td>
                  </tr>
                  <tr>
                    <td className="p-2.5 border-r border-slate-200 font-semibold text-slate-900">Impervious/Shade</td>
                    <td className="p-2.5 border-r border-slate-200">Sentinel-2 Satellite & Land Cover</td>
                    <td className="p-2.5">Land classification percentages (vegetation fraction, pavement grid) inside 100m stop buffers.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}

          {activeTab === "assumptions" && (
            <div className="space-y-4">
              <h3 className="font-bold text-slate-900 flex items-center gap-1.5 mb-1.5 text-sm">
                <ShieldAlert className="h-4.5 w-4.5 text-amber-600" />
                <span>Intervention Simulator Assumptions</span>
              </h3>
              <p className="text-xs text-slate-600">
                The Shade Intervention Simulator provides approximate planners' assessments based on established research of microclimate shelter efficiency. The conservative, moderate, and high options utilize these standardized reduction assumptions:
              </p>

              <div className="bg-amber-50/50 border border-amber-200/70 text-amber-950 p-4 rounded-xl space-y-2 text-xs">
                <div className="flex gap-2">
                  <CheckCircle2 className="h-4.5 w-4.5 text-emerald-600 shrink-0 mt-0.5" />
                  <span>
                    <strong>Conservative (20% reduction)</strong>: Corresponds to basic lightweight canopy fabrics or small young tree buffers.
                  </span>
                </div>
                <div className="flex gap-2">
                  <CheckCircle2 className="h-4.5 w-4.5 text-emerald-600 shrink-0 mt-0.5" />
                  <span>
                    <strong>Moderate (35% reduction)</strong>: Corresponds to standard insulated municipal transit shelter roof panels.
                  </span>
                </div>
                <div className="flex gap-2">
                  <CheckCircle2 className="h-4.5 w-4.5 text-emerald-600 shrink-0 mt-0.5" />
                  <span>
                    <strong>High (50% reduction)</strong>: Corresponds to green-roofed active-cooled shelters or thick mature tree groupings.
                  </span>
                </div>
              </div>

              <div className="border border-slate-150 rounded-xl p-4 bg-slate-50 space-y-2 text-xs">
                <h4 className="font-bold text-slate-800">Critical Limitations Disclaimer</h4>
                <ul className="list-disc list-inside space-y-1.5 text-slate-500">
                  <li>Calculated shade deficits are estimated proxies, not visual checks of precise seat placement.</li>
                  <li>Simulator reductions do not account for wind chill, air humidity variations, or time-of-day shadow angles.</li>
                  <li>These calculations are meant to support city planning budgets and do not represent final engineering or building assessments.</li>
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-200 bg-slate-50 flex justify-end">
          <button
            onClick={onClose}
            className="bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs px-4 py-2 rounded-lg transition-colors shadow"
          >
            Close Panel
          </button>
        </div>
      </div>
    </div>
  );
}
