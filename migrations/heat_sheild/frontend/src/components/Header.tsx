import React from 'react';
import { Flame, ShieldCheck, MapPin, Download, BookOpen, Layers } from 'lucide-react';

interface HeaderProps {
  onExportCSV: () => void;
  onOpenMethodology: () => void;
  totalStops: number;
}

export const Header: React.FC<HeaderProps> = ({ onExportCSV, onOpenMethodology, totalStops }) => {
  return (
    <header className="glass-panel border-b border-slate-800/80 px-6 py-4 sticky top-0 z-50 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <div className="h-11 w-11 rounded-xl bg-gradient-to-tr from-orange-600 via-amber-500 to-red-600 p-0.5 shadow-lg shadow-orange-950/40 flex items-center justify-center">
          <div className="h-full w-full bg-slate-950 rounded-[10px] flex items-center justify-center">
            <Flame className="h-6 w-6 text-orange-500 animate-pulse" />
          </div>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-white tracking-tight font-display">HeatShield: ShadeStop</h1>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-orange-500/20 text-orange-400 border border-orange-500/30">
              Hartford MVP
            </span>
          </div>
          <p className="text-xs text-slate-400 flex items-center gap-1.5 mt-0.5">
            <MapPin className="h-3.5 w-3.5 text-orange-400 inline" /> Hartford, Connecticut • Bus Stop Prioritization Engine
          </p>
        </div>
      </div>

      <div className="flex items-center flex-wrap gap-2.5">
        <div className="px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-300 flex items-center gap-2">
          <Layers className="h-3.5 w-3.5 text-blue-400" />
          <span>Analyzed Assets: <strong className="text-white">{totalStops} Stops</strong></span>
        </div>

        <div className="px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-300 flex items-center gap-2">
          <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
          <span>FortyGuard + ACS + GTFS</span>
        </div>

        <button
          onClick={onOpenMethodology}
          className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-all flex items-center gap-1.5 border border-slate-700/60"
        >
          <BookOpen className="h-3.5 w-3.5 text-slate-400" />
          <span>Methodology</span>
        </button>

        <button
          onClick={onExportCSV}
          className="px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white text-xs font-medium shadow-md shadow-orange-950/30 transition-all flex items-center gap-1.5"
        >
          <Download className="h-3.5 w-3.5" />
          <span>Export CSV Report</span>
        </button>
      </div>
    </header>
  );
};
