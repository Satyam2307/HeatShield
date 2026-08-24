"use client";

import React, { useState, useMemo } from "react";
import { ArrowUpDown, Search, ShieldAlert, ArrowUp, ArrowDown } from "lucide-react";
import { RankingItem } from "@/lib/types";

interface RankingsTableProps {
  items: RankingItem[];
  selectedStopId: string | null;
  onSelectStop: (stopId: string) => void;
}

type SortField =
  | "rank"
  | "stop_name"
  | "priority_score"
  | "dangerous_minutes"
  | "cumulative_exceedance"
  | "shade_deficit"
  | "vulnerability_score"
  | "transit_score";

type SortOrder = "asc" | "desc";

export default function RankingsTable({
  items,
  selectedStopId,
  onSelectStop,
}: RankingsTableProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [activeCategory, setActiveCategory] = useState<string>("All");
  const [sortField, setSortField] = useState<SortField>("priority_score");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");

  // Priority categories colors
  const getBadgeClass = (category: string) => {
    switch (category) {
      case "Critical":
        return "bg-red-100 text-red-800 border-red-200";
      case "High":
        return "bg-orange-100 text-orange-800 border-orange-200";
      case "Moderate":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      default:
        return "bg-blue-100 text-blue-800 border-blue-200";
    }
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortOrder("desc"); // Default to desc on new fields
    }
  };

  // Filter & Sort Logic
  const filteredAndSortedItems = useMemo(() => {
    let result = [...items];

    // Filter by Search Term
    if (searchTerm.trim() !== "") {
      result = result.filter((item) =>
        item.stop_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by Category Tab
    if (activeCategory !== "All") {
      result = result.filter((item) => item.priority_category === activeCategory);
    }

    // Sort items
    result.sort((a, b) => {
      let aVal: any = a[sortField as keyof RankingItem];
      let bVal: any = b[sortField as keyof RankingItem];

      if (typeof aVal === "string") {
        return sortOrder === "asc"
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }

      // Numeric comparisons
      aVal = aVal ?? 0;
      bVal = bVal ?? 0;
      return sortOrder === "asc" ? aVal - bVal : bVal - aVal;
    });

    return result;
  }, [items, searchTerm, activeCategory, sortField, sortOrder]);

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) {
      return <ArrowUpDown className="h-3 w-3 text-slate-400 group-hover:text-slate-600" />;
    }
    return sortOrder === "asc" ? (
      <ArrowUp className="h-3.5 w-3.5 text-slate-900" />
    ) : (
      <ArrowDown className="h-3.5 w-3.5 text-slate-900" />
    );
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col flex-1 min-h-[400px]">
      {/* Filtering & Search Bar */}
      <div className="p-4 border-b border-slate-200 bg-slate-50 flex flex-col sm:flex-row gap-3 items-center justify-between">
        {/* Category Tabs */}
        <div className="flex gap-1.5 p-1 bg-slate-200/70 border border-slate-200/50 rounded-lg select-none shrink-0 self-start sm:self-auto">
          {["All", "Critical", "High", "Moderate", "Low"].map((category) => {
            const count = category === "All" 
              ? items.length 
              : items.filter(s => s.priority_category === category).length;
            
            return (
              <button
                key={category}
                onClick={() => setActiveCategory(category)}
                className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
                  activeCategory === category
                    ? "bg-white text-slate-900 shadow-sm"
                    : "text-slate-500 hover:text-slate-800"
                }`}
              >
                {category} <span className="opacity-60 font-normal">({count})</span>
              </button>
            );
          })}
        </div>

        {/* Search Input */}
        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search Hartford stops..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-xs focus:outline-none focus:border-red-500 bg-white"
          />
        </div>
      </div>

      {/* Table Container */}
      <div className="flex-1 overflow-auto max-h-[500px]">
        {filteredAndSortedItems.length > 0 ? (
          <table className="w-full border-collapse text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-[10px] text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-200 sticky top-0 z-10">
              <tr>
                {/* Headers */}
                <th
                  onClick={() => handleSort("rank")}
                  className="px-4 py-3 cursor-pointer group hover:bg-slate-100 min-w-[60px]"
                >
                  <div className="flex items-center gap-1.5 font-bold">
                    Rank <SortIcon field="rank" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort("stop_name")}
                  className="px-4 py-3 cursor-pointer group hover:bg-slate-100 min-w-[200px]"
                >
                  <div className="flex items-center gap-1.5 font-bold">
                    Bus Stop Name <SortIcon field="stop_name" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort("priority_score")}
                  className="px-4 py-3 cursor-pointer group hover:bg-slate-100"
                >
                  <div className="flex items-center gap-1.5 font-bold">
                    Priority Score <SortIcon field="priority_score" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort("dangerous_minutes")}
                  className="px-4 py-3 cursor-pointer group hover:bg-slate-100"
                >
                  <div className="flex items-center gap-1.5 font-bold">
                    Danger Mins <SortIcon field="dangerous_minutes" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort("cumulative_exceedance")}
                  className="px-4 py-3 cursor-pointer group hover:bg-slate-100"
                >
                  <div className="flex items-center gap-1.5 font-bold flex-col sm:flex-row sm:items-center">
                    Cum. Exceedance <SortIcon field="cumulative_exceedance" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort("shade_deficit")}
                  className="px-4 py-3 cursor-pointer group hover:bg-slate-100"
                >
                  <div className="flex items-center gap-1.5 font-bold">
                    Shade Deficit <SortIcon field="shade_deficit" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort("vulnerability_score")}
                  className="px-4 py-3 cursor-pointer group hover:bg-slate-100"
                >
                  <div className="flex items-center gap-1.5 font-bold">
                    Vulner. Score <SortIcon field="vulnerability_score" />
                  </div>
                </th>
                <th className="px-4 py-3 font-bold">Intervention</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredAndSortedItems.map((item) => {
                const isSelected = item.bus_stop_id === selectedStopId;
                return (
                  <tr
                    key={item.bus_stop_id}
                    onClick={() => onSelectStop(item.bus_stop_id)}
                    className={`cursor-pointer transition-colors ${
                      isSelected
                        ? "bg-red-50/70 border-l-4 border-l-red-500 hover:bg-red-50"
                        : "hover:bg-slate-50"
                    }`}
                  >
                    <td className="px-4 py-3 font-semibold text-slate-800">
                      #{item.rank}
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-semibold text-slate-900 leading-tight">
                        {item.stop_name}
                      </div>
                      <div className="text-[10px] text-slate-400 mt-0.5 flex gap-1">
                        {item.routes_served.slice(0, 3).join(", ")}
                        {item.routes_served.length > 3 && ` +${item.routes_served.length - 3} more`}
                      </div>
                    </td>
                    <td className="px-4 py-3 font-bold">
                      <div className="flex items-center gap-2">
                        <span
                          className={`w-2.5 h-2.5 rounded-full`}
                          style={{
                            backgroundColor:
                              item.priority_category === "Critical"
                                ? "#dc2626"
                                : item.priority_category === "High"
                                ? "#ea580c"
                                : item.priority_category === "Moderate"
                                ? "#eab308"
                                : "#2563eb",
                          }}
                        />
                        <span className="text-slate-950 font-bold">{item.priority_score}</span>
                        <span
                          className={`px-1.5 py-0.5 border text-[9px] font-bold rounded ${getBadgeClass(
                            item.priority_category
                          )}`}
                        >
                          {item.priority_category}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 font-medium text-slate-800">
                      {item.dangerous_minutes} mins
                    </td>
                    <td className="px-4 py-3 text-slate-500">
                      {item.cumulative_exceedance} &deg;F-min
                    </td>
                    <td className="px-4 py-3 font-medium">
                      <div className="flex items-center gap-1.5">
                        <div className="w-12 h-1.5 bg-slate-100 border rounded-full overflow-hidden shrink-0 hidden sm:block">
                          <div
                            className="h-full bg-slate-500"
                            style={{ width: `${item.shade_deficit}%` }}
                          />
                        </div>
                        <span>{item.shade_deficit}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-800 font-medium">
                      {item.vulnerability_score}/100
                    </td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-1 bg-slate-100 text-slate-700 text-[10px] font-semibold rounded-md border border-slate-200">
                        {item.recommended_intervention}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          <div className="py-12 px-4 text-center">
            <Search className="h-8 w-8 text-slate-300 mx-auto mb-2" />
            <h3 className="font-bold text-slate-700">No stops match your query</h3>
            <p className="text-slate-400 text-xs mt-1">
              Try adjusting your search criteria or selecting a different priority category.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
