import React, { useState } from 'react';
import { BusStop } from '../types';
import { Search, Flame, ShieldAlert, ArrowUpDown, ChevronRight } from 'lucide-react';

interface RankingsTableProps {
  stops: BusStop[];
  selectedStop: BusStop | null;
  onSelectStop: (stop: BusStop) => void;
}

export const RankingsTable: React.FC<RankingsTableProps> = ({ stops, selectedStop, onSelectStop }) => {
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [sortBy, setSortBy] = useState<'rank' | 'priority_score' | 'dangerous_minutes'>('rank');

  const filteredStops = stops
    .filter((stop) => {
      const matchesSearch =
        stop.name.toLowerCase().includes(search.toLowerCase()) ||
        stop.corridor.toLowerCase().includes(search.toLowerCase()) ||
        stop.vulnerability_details.neighborhood_name.toLowerCase().includes(search.toLowerCase());
      const matchesCategory = categoryFilter === 'All' || stop.priority_category === categoryFilter;
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      if (sortBy === 'rank') return a.rank - b.rank;
      if (sortBy === 'priority_score') return b.priority_score - a.priority_score;
      if (sortBy === 'dangerous_minutes') return b.metrics.dangerous_minutes - a.metrics.dangerous_minutes;
      return 0;
    });

  const getCategoryBadgeClass = (category: string) => {
    switch (category) {
      case 'Critical':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'High':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'Moderate':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'Low':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      default:
        return 'bg-slate-700 text-slate-300';
    }
  };

  return (
    <div className="glass-panel rounded-xl p-4 flex flex-col h-full border border-slate-800">
      {/* Header controls */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 mb-3">
        <div className="flex items-center gap-2">
          <ShieldAlert className="h-4 w-4 text-orange-400" />
          <h2 className="text-sm font-bold text-white font-display">Hartford Bus Stop Priority Action List</h2>
          <span className="text-xs text-slate-400 font-mono">({filteredStops.length} stops)</span>
        </div>

        <div className="flex items-center gap-2">
          <div className="relative flex-1 sm:w-48">
            <Search className="h-3.5 w-3.5 text-slate-500 absolute left-2.5 top-2.5" />
            <input
              type="text"
              placeholder="Search stop or neighborhood..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-orange-500/50"
            />
          </div>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none"
          >
            <option value="All">All Categories</option>
            <option value="Critical">Critical (80-100)</option>
            <option value="High">High (60-79)</option>
            <option value="Moderate">Moderate (40-59)</option>
            <option value="Low">Low (0-39)</option>
          </select>
        </div>
      </div>

      {/* Table list */}
      <div className="flex-1 overflow-y-auto pr-1">
        <table className="w-full text-left text-xs">
          <thead className="text-slate-400 bg-slate-900/80 sticky top-0 z-10 border-b border-slate-800">
            <tr>
              <th
                onClick={() => setSortBy('rank')}
                className="py-2 px-2.5 font-semibold cursor-pointer hover:text-white"
              >
                <div className="flex items-center gap-1">
                  <span>Rank</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th className="py-2 px-2.5 font-semibold">Bus Stop Name</th>
              <th className="py-2 px-2.5 font-semibold">Neighborhood</th>
              <th
                onClick={() => setSortBy('priority_score')}
                className="py-2 px-2.5 font-semibold cursor-pointer hover:text-white text-right"
              >
                <div className="flex items-center justify-end gap-1">
                  <span>Priority Score</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th
                onClick={() => setSortBy('dangerous_minutes')}
                className="py-2 px-2.5 font-semibold cursor-pointer hover:text-white text-right"
              >
                <div className="flex items-center justify-end gap-1">
                  <span>Dangerous Mins</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th className="py-2 px-2 font-semibold text-center">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {filteredStops.map((stop) => {
              const isSelected = selectedStop?.asset_id === stop.asset_id;
              return (
                <tr
                  key={stop.asset_id}
                  onClick={() => onSelectStop(stop)}
                  className={`cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-orange-500/15 border-l-2 border-orange-500'
                      : 'hover:bg-slate-800/50 text-slate-300'
                  }`}
                >
                  <td className="py-2.5 px-2.5 font-mono font-bold text-slate-200">
                    #{stop.rank}
                  </td>
                  <td className="py-2.5 px-2.5">
                    <div className="font-semibold text-slate-100">{stop.name}</div>
                    <div className="text-[10px] text-slate-500">{stop.corridor}</div>
                  </td>
                  <td className="py-2.5 px-2.5 text-slate-400">
                    {stop.vulnerability_details.neighborhood_name}
                  </td>
                  <td className="py-2.5 px-2.5 text-right font-mono">
                    <div className="flex items-center justify-end gap-2">
                      <span className="font-bold text-white text-sm">{stop.priority_score}</span>
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] border font-semibold ${getCategoryBadgeClass(
                          stop.priority_category
                        )}`}
                      >
                        {stop.priority_category}
                      </span>
                    </div>
                  </td>
                  <td className="py-2.5 px-2.5 text-right font-mono font-semibold text-red-400">
                    {stop.metrics.dangerous_minutes} min
                  </td>
                  <td className="py-2.5 px-2 text-center text-slate-500">
                    <ChevronRight className={`h-4 w-4 inline ${isSelected ? 'text-orange-400' : ''}`} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
