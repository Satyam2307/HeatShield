import React, { useState } from 'react';
import { Sliders, Thermometer, Calendar, Clock, RefreshCw } from 'lucide-react';
import { Weights } from '../types';

interface ScenarioBarProps {
  weights: Weights;
  dangerThreshold: number;
  onWeightsChange: (newWeights: Weights) => void;
  onThresholdChange: (newThreshold: number) => void;
  onRecalculate: () => void;
  isRecalculating: boolean;
}

export const ScenarioBar: React.FC<ScenarioBarProps> = ({
  weights,
  dangerThreshold,
  onWeightsChange,
  onThresholdChange,
  onRecalculate,
  isRecalculating
}) => {
  const [showWeights, setShowWeights] = useState(false);

  return (
    <div className="glass-panel px-6 py-3 border-b border-slate-800/80 flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4 text-xs">
      <div className="flex items-center flex-wrap gap-4">
        <div className="flex items-center gap-2 bg-slate-900/90 px-3 py-1.5 rounded-lg border border-slate-800">
          <Calendar className="h-3.5 w-3.5 text-orange-400" />
          <span className="text-slate-400">Date:</span>
          <span className="font-semibold text-white">July 15, 2024 (Historical Heatwave)</span>
        </div>

        <div className="flex items-center gap-2 bg-slate-900/90 px-3 py-1.5 rounded-lg border border-slate-800">
          <Clock className="h-3.5 w-3.5 text-amber-400" />
          <span className="text-slate-400">Window:</span>
          <span className="font-semibold text-white">10:00 AM – 6:00 PM EDT</span>
        </div>

        <div className="flex items-center gap-3 bg-slate-900/90 px-3.5 py-1.5 rounded-lg border border-slate-800">
          <Thermometer className="h-3.5 w-3.5 text-red-400" />
          <span className="text-slate-400">Danger Threshold:</span>
          <span className="font-bold text-red-400 font-mono">{dangerThreshold}°F</span>
          <input
            type="range"
            min="88"
            max="100"
            step="1"
            value={dangerThreshold}
            onChange={(e) => onThresholdChange(Number(e.target.value))}
            className="w-24 accent-orange-500 cursor-pointer"
          />
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={() => setShowWeights(!showWeights)}
          className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition-all flex items-center gap-1.5 ${
            showWeights
              ? 'bg-orange-500/20 border-orange-500/50 text-orange-300'
              : 'bg-slate-900/90 border-slate-800 text-slate-300 hover:bg-slate-800'
          }`}
        >
          <Sliders className="h-3.5 w-3.5" />
          <span>Customize Weights</span>
        </button>

        <button
          onClick={onRecalculate}
          disabled={isRecalculating}
          className="px-3.5 py-1.5 rounded-lg bg-orange-600 hover:bg-orange-500 text-white font-medium text-xs flex items-center gap-1.5 transition-all shadow-md shadow-orange-950/40 disabled:opacity-50"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isRecalculating ? 'animate-spin' : ''}`} />
          <span>Apply Parameters</span>
        </button>
      </div>

      {showWeights && (
        <div className="w-full bg-slate-900/95 border border-slate-800 rounded-xl p-4 mt-2 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="flex justify-between text-slate-300 mb-1">
              <span>Heat Exposure Weight:</span>
              <strong className="text-orange-400">{Math.round(weights.heat * 100)}%</strong>
            </div>
            <input
              type="range"
              min="0.1"
              max="0.7"
              step="0.05"
              value={weights.heat}
              onChange={(e) => onWeightsChange({ ...weights, heat: Number(e.target.value) })}
              className="w-full accent-orange-500 cursor-pointer"
            />
          </div>

          <div>
            <div className="flex justify-between text-slate-300 mb-1">
              <span>Shade Deficit Weight:</span>
              <strong className="text-amber-400">{Math.round(weights.shade * 100)}%</strong>
            </div>
            <input
              type="range"
              min="0.1"
              max="0.5"
              step="0.05"
              value={weights.shade}
              onChange={(e) => onWeightsChange({ ...weights, shade: Number(e.target.value) })}
              className="w-full accent-amber-500 cursor-pointer"
            />
          </div>

          <div>
            <div className="flex justify-between text-slate-300 mb-1">
              <span>Vulnerability Weight:</span>
              <strong className="text-purple-400">{Math.round(weights.vulnerability * 100)}%</strong>
            </div>
            <input
              type="range"
              min="0.1"
              max="0.4"
              step="0.05"
              value={weights.vulnerability}
              onChange={(e) => onWeightsChange({ ...weights, vulnerability: Number(e.target.value) })}
              className="w-full accent-purple-500 cursor-pointer"
            />
          </div>

          <div>
            <div className="flex justify-between text-slate-300 mb-1">
              <span>Transit Weight:</span>
              <strong className="text-blue-400">{Math.round(weights.transit * 100)}%</strong>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.4"
              step="0.05"
              value={weights.transit}
              onChange={(e) => onWeightsChange({ ...weights, transit: Number(e.target.value) })}
              className="w-full accent-blue-500 cursor-pointer"
            />
          </div>
        </div>
      )}
    </div>
  );
};
