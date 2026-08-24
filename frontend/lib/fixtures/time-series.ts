import { TimeSeriesPoint } from "../types";
import { BUS_STOPS_LIST } from "./bus-stops";

// Cache for generated timeseries to ensure stability
const TIMESERIES_CACHE = new Map<string, TimeSeriesPoint[]>();

export function getTimeSeriesForStop(stopId: string): TimeSeriesPoint[] {
  if (TIMESERIES_CACHE.has(stopId)) {
    return TIMESERIES_CACHE.get(stopId)!;
  }

  const stop = BUS_STOPS_LIST.find((s) => s.bus_stop_id === stopId);
  const score = stop ? stop.priority_score : 50;

  // Base temperatures based on priority score (higher score = hotter stop)
  // Let's create an hourly curve from 10 AM to 6 PM
  const hours = [
    { label: "10:00 AM", offset: -4 },
    { label: "11:00 AM", offset: -2 },
    { label: "12:00 PM", offset: 0 },
    { label: "01:00 PM", offset: 2 },
    { label: "02:00 PM", offset: 4 },
    { label: "03:00 PM", offset: 5 }, // Peak around 3-4 PM
    { label: "04:00 PM", offset: 4.5 },
    { label: "05:00 PM", offset: 2 },
    { label: "06:00 PM", offset: -1 },
  ];

  // Base baseline temperature for a hot day in Hartford
  const baseTemp = 85 + (score / 100) * 10; // 85F to 95F base

  const points: TimeSeriesPoint[] = hours.map((h) => {
    // Add small random variation based on stopId hash
    const hash = parseInt(stopId.replace("stop-", "") || "0") * 3.3;
    const rand = Math.sin(hash + h.offset) * 1.5;
    const temp = Math.round(baseTemp + h.offset + rand);

    return {
      timestamp: `2023-07-15T${h.label.includes("AM") ? h.label.split(":")[0] : String(parseInt(h.label.split(":")[0]) + (h.label.includes("12") ? 0 : 12))}:00:00-04:00`,
      value: temp,
    };
  });

  TIMESERIES_CACHE.set(stopId, points);
  return points;
}
