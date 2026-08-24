import React, { useState, useEffect } from 'react';
import { BusStop, SimulationResult } from '../types';
import { simulateIntervention } from '../api';
import { Sparkles, ArrowRight, ShieldCheck, TrendingDown, Info } from 'lucide-react';

interface InterventionSimulatorProps {
  selectedStop: BusStop;
}

export const InterventionSimulator: React.FC<InterventionSimulatorProps> = ({ selectedStop }) => {
  const [scenario, setScenario] = useState<'conservative' | 'moderate' | 'high'>('moderate');
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    simulateIntervention(selectedStop.asset_id, scenario)
      .then((res) => {
        if (isMounted) {
          setResult(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error(err);
        if (isMounted) setLoading(false);
      });
    return () => {
      isMounted = false;
    };
  }, [selectedStop.asset_id, scenario]);

  return (
    <div className="glass-card rounded-xl p-4 border border-orange-500/30 bg-gradient-to-br from-slate-900/90 via-slate-900/95 to-orange-950/20 shadow-xl space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-sm font-bold text-white font-display flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-amber-400" />
            <span>Shade Intervention Scenario Simulator</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Simulate expected heat exposure reduction for <strong className="text-white">{selectedStop.name}</strong>
          </p>
        </div>

        {/* Scenario Toggle */}
        <div className="flex items-center bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs">
          <button
            onClick={() => setScenario('conservative')}
            className={`px-2.5 py-1 rounded font-medium transition-all ${
              scenario === 'conservative'
                ? 'bg-orange-500 text-white font-bold shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Conservative (20%)
          </button>
          <button
            onClick={() => setScenario('moderate')}
            className={`px-2.5 py-1 rounded font-medium transition-all ${
              scenario === 'moderate'
                ? 'bg-orange-500 text-white font-bold shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Moderate (35%)
          </button>
          <button
            onClick={() => setScenario('high')}
            className={`px-2.5 py-1 rounded font-medium transition-all ${
              scenario === 'high'
                ? 'bg-orange-500 text-white font-bold shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            High (50%)
          </button>
        </div>
      </div>

      {loading || !result ? (
        <div className="py-6 text-center text-xs text-slate-400 animate-pulse">
          Calculating intervention simulation model...
        </div>
      ) : (
        <div className="space-y-4">
          {/* Key Metrics Impact Comparison */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {/* Dangerous Minutes Card */}
            <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 block uppercase font-semibold">Dangerous Heat Minutes</span>
              <div className="flex items-center gap-2">
                <span className="text-slate-400 line-through text-xs">{result.baseline_dangerous_minutes}m</span>
                <ArrowRight className="h-3 w-3 text-orange-400" />
                <span className="text-emerald-400 font-bold font-mono text-lg">{result.projected_dangerous_minutes}m</span>
              </div>
              <div className="text-[10px] text-emerald-400 font-medium flex items-center gap-1">
                <TrendingDown className="h-3 w-3 inline" />
                <span>Avoided {result.avoided_dangerous_minutes} dangerous mins ({result.assumptions.exposure_reduction_pct}% reduction)</span>
              </div>
            </div>

            {/* Priority Score Impact */}
            <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 block uppercase font-semibold">Priority Score Shift</span>
              <div className="flex items-center gap-2">
                <span className="text-red-400 font-bold text-xs">{result.baseline_priority_score}</span>
                <ArrowRight className="h-3 w-3 text-orange-400" />
                <span className="text-amber-300 font-bold font-mono text-lg">{result.projected_priority_score}</span>
              </div>
              <span className="text-[10px] text-slate-400 block">
                Reduced urgency after shade installation
              </span>
            </div>

            {/* Priority Rank Shift */}
            <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 block uppercase font-semibold">Action List Rank Shift</span>
              <div className="flex items-center gap-2">
                <span className="text-orange-400 font-bold text-xs">#{result.baseline_rank}</span>
                <ArrowRight className="h-3 w-3 text-orange-400" />
                <span className="text-emerald-400 font-bold font-mono text-lg">#{result.projected_rank}</span>
              </div>
              <span className="text-[10px] text-emerald-400 font-medium">
                Drops {result.rank_change} positions in city priority
              </span>
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-orange-950/30 border border-orange-500/20 text-xs text-slate-300 flex items-start gap-2">
            <Info className="h-4 w-4 text-orange-400 shrink-0 mt-0.5" />
            <p>
              <strong>Scenario Assumption:</strong> {result.scenario_description}.
              This simulation reflects heat exposure reduction planning estimates for municipal transit intervention design.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
