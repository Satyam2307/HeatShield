import React from 'react';
import { BusStop } from '../types';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, ReferenceLine, CartesianGrid } from 'recharts';
import { Flame, Clock, Sun, Users, Bus, Shield, AlertTriangle } from 'lucide-react';

interface StopDetailPanelProps {
  stop: BusStop;
}

export const StopDetailPanel: React.FC<StopDetailPanelProps> = ({ stop }) => {
  const chartData = stop.timeseries.map((ts) => ({
    time: `${ts.hour > 12 ? ts.hour - 12 : ts.hour} ${ts.hour >= 12 ? 'PM' : 'AM'}`,
    heatIndex: ts.heat_index,
    exceedance: ts.exceedance
  }));

  const peakHourAmPm =
    stop.metrics.peak_hour > 12
      ? `${stop.metrics.peak_hour - 12} PM`
      : stop.metrics.peak_hour < 12
      ? `${stop.metrics.peak_hour} AM`
      : '12 PM';

  return (
    <div className="space-y-4">
      {/* Title & Priority Header */}
      <div className="glass-card rounded-xl p-4 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded bg-orange-500/20 text-orange-400 font-mono font-bold text-xs">
              Rank #{stop.rank}
            </span>
            <h3 className="text-base font-bold text-white font-display">{stop.name}</h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            {stop.corridor} • {stop.vulnerability_details.neighborhood_name}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right">
            <span className="text-[10px] text-slate-400 block uppercase tracking-wider font-semibold">Priority Score</span>
            <div className="text-2xl font-extrabold text-orange-400 font-mono leading-none">{stop.priority_score}</div>
          </div>
          <div className="h-8 w-px bg-slate-800"></div>
          <div>
            <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-red-500/20 text-red-400 border border-red-500/30">
              {stop.priority_category}
            </span>
          </div>
        </div>
      </div>

      {/* Component Breakdown Bars */}
      <div className="glass-card rounded-xl p-4 border border-slate-800">
        <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider mb-3 flex items-center gap-1.5">
          <Shield className="h-3.5 w-3.5 text-orange-400" />
          <span>Priority Score Components Breakdown</span>
        </h4>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="bg-slate-900/90 p-2.5 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-400 block">Heat Exposure (40%)</span>
            <strong className="text-red-400 font-mono text-base">{stop.components.heat}/100</strong>
          </div>
          <div className="bg-slate-900/90 p-2.5 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-400 block">Shade Deficit (25%)</span>
            <strong className="text-amber-400 font-mono text-base">{stop.components.shade}/100</strong>
          </div>
          <div className="bg-slate-900/90 p-2.5 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-400 block">Vulnerability (20%)</span>
            <strong className="text-purple-400 font-mono text-base">{stop.components.vulnerability}/100</strong>
          </div>
          <div className="bg-slate-900/90 p-2.5 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-400 block">Transit Importance (15%)</span>
            <strong className="text-blue-400 font-mono text-base">{stop.components.transit}/100</strong>
          </div>
        </div>
      </div>

      {/* FortyGuard Heat Index Profile Chart */}
      <div className="glass-card rounded-xl p-4 border border-slate-800">
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
            <Flame className="h-3.5 w-3.5 text-red-400" />
            <span>FortyGuard Heat Index Profile (10:00 AM – 6:00 PM)</span>
          </h4>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
              <Clock className="h-3 w-3" />
              Peak Heat: {peakHourAmPm}
            </span>
          </div>
        </div>

        <div className="h-44 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 10 }} />
              <YAxis domain={[85, 'dataMax + 2']} stroke="#64748b" tick={{ fontSize: 10 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
                labelStyle={{ color: '#94a3b8' }}
              />
              <ReferenceLine y={95} stroke="#ef4444" strokeDasharray="4 4" label={{ value: '95°F Threshold', fill: '#ef4444', fontSize: 10, position: 'insideTopLeft' }} />
              <Line type="monotone" dataKey="heatIndex" stroke="#f97316" strokeWidth={2.5} dot={{ r: 3, fill: '#f97316' }} activeDot={{ r: 5 }} name="Heat Index (°F)" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="grid grid-cols-3 gap-2 mt-3 text-center text-xs">
          <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
            <span className="text-[10px] text-slate-400 block">Dangerous Minutes</span>
            <strong className="text-red-400 font-mono text-sm">{stop.metrics.dangerous_minutes} mins</strong>
          </div>
          <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
            <span className="text-[10px] text-slate-400 block">Persistence Period</span>
            <strong className="text-orange-400 font-mono text-sm">{stop.metrics.persistence_minutes} mins</strong>
          </div>
          <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
            <span className="text-[10px] text-slate-400 block">Cumulative Exceedance</span>
            <strong className="text-amber-400 font-mono text-sm">{stop.metrics.cumulative_exceedance} °F·hr</strong>
          </div>
        </div>
      </div>

      {/* Community Vulnerability & Shade Details Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Vulnerability Card */}
        <div className="glass-card rounded-xl p-4 border border-slate-800 space-y-2">
          <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
            <Users className="h-3.5 w-3.5 text-purple-400" />
            <span>Community Vulnerability (ACS)</span>
          </h4>
          <div className="text-xs space-y-1.5 text-slate-300">
            <div className="flex justify-between border-b border-slate-800 pb-1">
              <span className="text-slate-400">Neighborhood:</span>
              <strong className="text-white">{stop.vulnerability_details.neighborhood_name}</strong>
            </div>
            <div className="flex justify-between border-b border-slate-800 pb-1">
              <span className="text-slate-400">Zero-Vehicle Households:</span>
              <strong className="text-purple-300 font-mono">
                {Math.round(stop.vulnerability_details.zero_vehicle_fraction * 100)}%
              </strong>
            </div>
            <div className="flex justify-between border-b border-slate-800 pb-1">
              <span className="text-slate-400">Median Household Income:</span>
              <strong className="text-emerald-400 font-mono">
                ${stop.vulnerability_details.median_income.toLocaleString()}
              </strong>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Older Adults (65+):</span>
              <strong className="text-slate-200 font-mono">
                {Math.round(stop.vulnerability_details.older_adult_fraction * 100)}%
              </strong>
            </div>
          </div>
        </div>

        {/* Shade & Satellite Proxy Card */}
        <div className="glass-card rounded-xl p-4 border border-slate-800 space-y-2">
          <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
            <Sun className="h-3.5 w-3.5 text-amber-400" />
            <span>Shade & Satellite Proxy</span>
          </h4>
          <div className="text-xs space-y-1.5 text-slate-300">
            <div className="flex justify-between border-b border-slate-800 pb-1">
              <span className="text-slate-400">Shelter Status:</span>
              <strong className="text-white">{stop.shade_details.shelter_status}</strong>
            </div>
            <div className="flex justify-between border-b border-slate-800 pb-1">
              <span className="text-slate-400">Shade Deficit Proxy:</span>
              <strong className="text-amber-400 font-mono">
                {Math.round(stop.shade_details.shade_deficit * 100)}% Deficit
              </strong>
            </div>
            <div className="flex justify-between border-b border-slate-800 pb-1">
              <span className="text-slate-400">Surrounding Vegetation:</span>
              <strong className="text-emerald-400 font-mono">
                {Math.round(stop.shade_details.vegetation_fraction * 100)}%
              </strong>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Pavement / Impervious:</span>
              <strong className="text-slate-200 font-mono">
                {Math.round(stop.shade_details.impervious_fraction * 100)}%
              </strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
