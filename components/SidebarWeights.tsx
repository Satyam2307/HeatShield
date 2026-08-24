"use client";

import React, { useState, useEffect } from "react";
import { Sliders, RefreshCw, AlertCircle, Calendar } from "lucide-react";
import { Weights } from "@/lib/types";

interface SidebarWeightsProps {
  initialWeights: Weights;
  dangerThreshold: number;
  onWeightsChange: (weights: Weights) => void;
  onThresholdChange: (threshold: number) => void;
}

export default function SidebarWeights({
  initialWeights,
  dangerThreshold,
  onWeightsChange,
  onThresholdChange,
}: SidebarWeightsProps) {
  const [heatWeight, setHeatWeight] = useState(initialWeights.heat * 100);
  const [shadeWeight, setShadeWeight] = useState(initialWeights.shade * 100);
  const [vulnWeight, setVulnWeight] = useState(initialWeights.vulnerability * 100);
  const [transitWeight, setTransitWeight] = useState(initialWeights.transit * 100);
  const [threshold, setThreshold] = useState(dangerThreshold);

  // Keep internal states in sync with props
  useEffect(() => {
    setHeatWeight(initialWeights.heat * 100);
    setShadeWeight(initialWeights.shade * 100);
    setVulnWeight(initialWeights.vulnerability * 100);
    setTransitWeight(initialWeights.transit * 100);
  }, [initialWeights]);

  const total = heatWeight + shadeWeight + vulnWeight + transitWeight;

  const handleReset = () => {
    setHeatWeight(40);
    setShadeWeight(25);
    setVulnWeight(20);
    setTransitWeight(15);
    setThreshold(95);
    onWeightsChange({ heat: 0.40, shade: 0.25, vulnerability: 0.20, transit: 0.15 });
    onThresholdChange(95);
  };

  const handleApply = () => {
    // Normalize to sum to 1
    const factor = total > 0 ? 1 / total : 0;
    const weights: Weights = {
      heat: parseFloat((heatWeight * factor).toFixed(3)),
      shade: parseFloat((shadeWeight * factor).toFixed(3)),
      vulnerability: parseFloat((vulnWeight * factor).toFixed(3)),
      transit: parseFloat((transitWeight * factor).toFixed(3)),
    };
    onWeightsChange(weights);
    onThresholdChange(threshold);
  };

  return (
    <div className="w-full lg:w-80 bg-white border-r border-slate-200 p-6 flex flex-col gap-6 select-none shrink-0">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-slate-800 font-bold">
          <Sliders className="h-4.5 w-4.5 text-red-500" />
          <h2>Analysis Settings</h2>
        </div>
        <button
          onClick={handleReset}
          className="text-xs text-slate-500 hover:text-slate-800 flex items-center gap-1 font-medium transition-colors"
          title="Reset weights and threshold to default"
        >
          <RefreshCw className="h-3 w-3" />
          <span>Reset</span>
        </button>
      </div>

      <hr className="border-slate-100" />

      {/* Date and Metric Config */}
      <div className="flex flex-col gap-4">
        <div>
          <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
            Historical Scenario
          </label>
          <div className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 flex items-center gap-2.5 text-sm text-slate-700">
            <Calendar className="h-4 w-4 text-slate-400" />
            <span className="font-medium">Heatwave Day (Jul 15)</span>
          </div>
        </div>

        <div>
          <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1.5">
            Risk Threshold (&deg;F)
          </label>
          <div className="flex items-center gap-3">
            <input
              type="range"
              min="90"
              max="102"
              step="1"
              value={threshold}
              onChange={(e) => setThreshold(parseInt(e.target.value))}
              className="flex-1 accent-red-500 h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer"
            />
            <span className="text-sm font-bold text-slate-800 bg-slate-100 border border-slate-200 px-2 py-0.5 rounded min-w-[3rem] text-center">
              {threshold}&deg;F
            </span>
          </div>
          <p className="text-[10px] text-slate-400 mt-1">
            Temperatures &ge; this value contribute to dangerous exposure minutes.
          </p>
        </div>
      </div>

      <hr className="border-slate-100" />

      {/* Scoring Weight Sliders */}
      <div className="flex flex-col gap-5">
        <div>
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-3">
            Prioritization Weights
          </h3>
          <div className="space-y-4">
            {/* Heat Exposure Slider */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="font-semibold text-slate-700">Heat Exposure</span>
                <span className="font-bold text-slate-900">{Math.round(heatWeight)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={heatWeight}
                onChange={(e) => setHeatWeight(parseInt(e.target.value))}
                className="w-full accent-red-500 h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            {/* Shade Deficit Slider */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="font-semibold text-slate-700">Shade Deficit</span>
                <span className="font-bold text-slate-900">{Math.round(shadeWeight)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={shadeWeight}
                onChange={(e) => setShadeWeight(parseInt(e.target.value))}
                className="w-full accent-red-500 h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            {/* Community Vulnerability Slider */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="font-semibold text-slate-700">Vulnerability</span>
                <span className="font-bold text-slate-900">{Math.round(vulnWeight)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={vulnWeight}
                onChange={(e) => setVulnWeight(parseInt(e.target.value))}
                className="w-full accent-red-500 h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            {/* Transit Importance Slider */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="font-semibold text-slate-700">Transit Importance</span>
                <span className="font-bold text-slate-900">{Math.round(transitWeight)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={transitWeight}
                onChange={(e) => setTransitWeight(parseInt(e.target.value))}
                className="w-full accent-red-500 h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Sum Indicator and Warnings */}
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 flex flex-col gap-2">
          <div className="flex justify-between items-center text-xs font-semibold text-slate-700">
            <span>Cumulative Sum:</span>
            <span className={total === 100 ? "text-emerald-600 font-bold" : "text-amber-600 font-bold"}>
              {total}%
            </span>
          </div>

          {total !== 100 && (
            <div className="flex gap-1.5 items-start text-[10px] text-amber-600 leading-tight">
              <AlertCircle className="h-3.5 w-3.5 shrink-0 mt-0.5" />
              <span>
                Weights do not total 100%. If applied, values will be normalized proportionally.
              </span>
            </div>
          )}

          <button
            onClick={handleApply}
            className="w-full mt-1.5 bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold py-2 rounded-lg transition-colors shadow-sm"
          >
            Apply & Recalculate
          </button>
        </div>
      </div>
    </div>
  );
}
