import React from 'react';
import { X, BookOpen, Database, ShieldCheck, Check } from 'lucide-react';

interface MethodologyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MethodologyModal: React.FC<MethodologyModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="glass-panel w-full max-w-2xl rounded-2xl border border-slate-800 p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-orange-400" />
            <h2 className="text-base font-bold text-white font-display">HeatShield: ShadeStop Methodology</h2>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-4 text-xs text-slate-300">
          <div>
            <h3 className="font-bold text-slate-100 text-sm mb-1">1. Priority Score Formula</h3>
            <p className="text-slate-400">
              The priority score ranks Hartford bus stops on a 0–100 percentile scale:
            </p>
            <div className="bg-slate-900 p-3 rounded-lg border border-slate-800 mt-2 font-mono text-orange-300">
              Priority Score = 40% Heat Exposure + 25% Shade Deficit + 20% Vulnerability + 15% Transit
            </div>
          </div>

          <div>
            <h3 className="font-bold text-slate-100 text-sm mb-1">2. Heat Exposure Metrics</h3>
            <div className="bg-slate-900 p-3 rounded-lg border border-slate-800 font-mono text-red-300">
              Heat Score = 50% Cumulative Exceedance + 30% Dangerous Duration + 20% Persistence
            </div>
            <ul className="list-disc pl-4 mt-2 space-y-1 text-slate-400">
              <li><strong>Cumulative Exceedance:</strong> sum(max(0, heat_index - 95°F) * interval_hours)</li>
              <li><strong>Persistence:</strong> Longest continuous period above the 95°F threshold</li>
              <li><strong>Time of Measure:</strong> Identifies exact daily peak heat hour (FortyGuard analytic_type=3)</li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold text-slate-100 text-sm mb-1">3. Integrated Datasets</h3>
            <div className="grid grid-cols-2 gap-2 mt-2">
              <div className="bg-slate-900 p-2.5 rounded border border-slate-800">
                <strong className="text-slate-200 block">FortyGuard API</strong>
                <span className="text-[11px] text-slate-400">Heat index, exceedance, persistence & satellite land cover</span>
              </div>
              <div className="bg-slate-900 p-2.5 rounded border border-slate-800">
                <strong className="text-slate-200 block">US Census ACS (2022)</strong>
                <span className="text-[11px] text-slate-400">Zero-vehicle households, median income, older adults & children</span>
              </div>
              <div className="bg-slate-900 p-2.5 rounded border border-slate-800">
                <strong className="text-slate-200 block">CTtransit GTFS</strong>
                <span className="text-[11px] text-slate-400">Hartford bus stop coordinates, routes & ridership proxies</span>
              </div>
              <div className="bg-slate-900 p-2.5 rounded border border-slate-800">
                <strong className="text-slate-200 block">Census TIGER / PostGIS</strong>
                <span className="text-[11px] text-slate-400">Hartford City boundary & EPSG:3437 projected 100m spatial buffers</span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-bold text-slate-100 text-sm mb-1">4. Hackathon Track & City Scope</h3>
            <p className="text-slate-400">
              Built for <strong>Track 1 — Resilient Cities & Infrastructure</strong>. Focused specifically on Hartford, CT bus stops as the primary municipal asset.
            </p>
          </div>
        </div>

        <div className="pt-2 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-orange-600 hover:bg-orange-500 text-white font-medium text-xs transition-all"
          >
            Close Methodology
          </button>
        </div>
      </div>
    </div>
  );
};
