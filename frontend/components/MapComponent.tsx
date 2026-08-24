"use client";

import React, { useEffect, useRef, useState } from "react";
import { Info, Maximize2, Minimize2, Map as MapIcon, ShieldAlert } from "lucide-react";
import { HartfordBoundaryGeoJSON } from "@/lib/fixtures/hartford-boundary";
import { RankingItem } from "@/lib/types";

interface MapComponentProps {
  items: RankingItem[];
  selectedStopId: string | null;
  onSelectStop: (stopId: string) => void;
}

export default function MapComponent({
  items,
  selectedStopId,
  onSelectStop,
}: MapComponentProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<any>(null);
  const [useFallback, setUseFallback] = useState(false);
  const [hoveredStop, setHoveredStop] = useState<RankingItem | null>(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });

  // MapLibre Colors matching priority categories
  const getColorForCategory = (category: string) => {
    switch (category) {
      case "Critical":
        return "#dc2626"; // Dark Red
      case "High":
        return "#ea580c"; // Orange
      case "Moderate":
        return "#eab308"; // Yellow-Gold
      case "Low":
        return "#2563eb"; // Blue
      default:
        return "#64748b"; // Slate
    }
  };

  // Try to load MapLibre GL JS
  useEffect(() => {
    if (useFallback || !mapContainerRef.current) return;

    let mapInstance: any = null;
    let isCancelled = false;

    const initMap = async () => {
      try {
        // Dynamic import to prevent SSR issues
        const maplibregl = (await import("maplibre-gl")).default;

        if (isCancelled) return;

        mapInstance = new maplibregl.Map({
          container: mapContainerRef.current!,
          style: "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
          center: [-72.678, 41.765], // Center of Hartford CT
          zoom: 11.8,
          minZoom: 10,
          maxZoom: 16,
        });

        mapInstance.addControl(new maplibregl.NavigationControl(), "top-right");

        mapInstance.on("load", () => {
          if (isCancelled) return;

          // Add Hartford Boundary source and layers
          mapInstance.addSource("hartford-boundary", {
            type: "geojson",
            data: HartfordBoundaryGeoJSON,
          });

          // Hartford Fill Layer
          mapInstance.addLayer({
            id: "boundary-fill",
            type: "fill",
            source: "hartford-boundary",
            paint: {
              "fill-color": "#94a3b8",
              "fill-opacity": 0.07,
            },
          });

          // Hartford Border Outline
          mapInstance.addLayer({
            id: "boundary-line",
            type: "line",
            source: "hartford-boundary",
            paint: {
              "line-color": "#475569",
              "line-width": 1.5,
              "line-dasharray": [2, 2],
            },
          });

          // Add Bus Stops points source
          const stopsGeoJSON = {
            type: "FeatureCollection",
            features: items.map((stop) => ({
              type: "Feature",
              properties: {
                id: stop.bus_stop_id,
                name: stop.stop_name,
                priority_score: stop.priority_score,
                priority_category: stop.priority_category,
              },
              geometry: {
                type: "Point",
                coordinates: [stop.longitude, stop.latitude],
              },
            })),
          };

          mapInstance.addSource("bus-stops", {
            type: "geojson",
            data: stopsGeoJSON,
          });

          // Bus Stops Circle Layer
          mapInstance.addLayer({
            id: "stops-points",
            type: "circle",
            source: "bus-stops",
            paint: {
              "circle-radius": [
                "case",
                ["==", ["get", "id"], selectedStopId || ""],
                10,
                6,
              ],
              "circle-color": [
                "match",
                ["get", "priority_category"],
                "Critical",
                "#dc2626",
                "High",
                "#ea580c",
                "Moderate",
                "#eab308",
                "Low",
                "#2563eb",
                "#64748b",
              ],
              "circle-stroke-width": [
                "case",
                ["==", ["get", "id"], selectedStopId || ""],
                3,
                1,
              ],
              "circle-stroke-color": [
                "case",
                ["==", ["get", "id"], selectedStopId || ""],
                "#ffffff",
                "#1e293b",
              ],
            },
          });

          // Click handler to select stop
          mapInstance.on("click", "stops-points", (e: any) => {
            if (e.features && e.features.length > 0) {
              const stopId = e.features[0].properties.id;
              onSelectStop(stopId);
            }
          });

          // Change cursor on hover
          mapInstance.on("mouseenter", "stops-points", (e: any) => {
            mapInstance.getCanvas().style.cursor = "pointer";
          });

          mapInstance.on("mouseleave", "stops-points", () => {
            mapInstance.getCanvas().style.cursor = "";
          });

          setMap(mapInstance);
        });
      } catch (err) {
        console.warn("MapLibre GL initialization failed. Switching to SVG Vector map.", err);
        setUseFallback(true);
      }
    };

    initMap();

    return () => {
      isCancelled = true;
      if (mapInstance) {
        mapInstance.remove();
      }
    };
  }, [useFallback]);

  // Update map source features when stop weights/scores change
  useEffect(() => {
    if (!map || useFallback) return;

    const source = map.getSource("bus-stops");
    if (source) {
      source.setData({
        type: "FeatureCollection",
        features: items.map((stop) => ({
          type: "Feature",
          properties: {
            id: stop.bus_stop_id,
            name: stop.stop_name,
            priority_score: stop.priority_score,
            priority_category: stop.priority_category,
          },
          geometry: {
            type: "Point",
            coordinates: [stop.longitude, stop.latitude],
          },
        })),
      });
    }
  }, [items, map, useFallback]);

  // Update selection highlight size dynamically
  useEffect(() => {
    if (!map || useFallback) return;

    const layer = map.getLayer("stops-points");
    if (layer) {
      map.setPaintProperty("stops-points", "circle-radius", [
        "case",
        ["==", ["get", "id"], selectedStopId || ""],
        10,
        6,
      ]);
      map.setPaintProperty("stops-points", "circle-stroke-width", [
        "case",
        ["==", ["get", "id"], selectedStopId || ""],
        3,
        1,
      ]);
    }
  }, [selectedStopId, map, useFallback]);

  // Fallback Coordinates mapping (from spherical coords to SVG viewBox 0-100)
  // Hartford dimensions approx: Lng [-72.715, -72.630], Lat [41.720, 41.810]
  const minLng = -72.715;
  const maxLng = -72.630;
  const minLat = 41.720;
  const maxLat = 41.810;

  const getSvgCoords = (lat: number, lng: number) => {
    // Linear map to SVG grid (0 to 500)
    // Flip Y because SVG 0,0 is top-left
    const x = ((lng - minLng) / (maxLng - minLng)) * 500;
    const y = 500 - ((lat - minLat) / (maxLat - minLat)) * 500;
    return { x, y };
  };

  // Convert Hartford polygon coordinates to SVG points string
  const boundaryPointsStr = HartfordBoundaryGeoJSON.geometry.coordinates[0]
    .map((coord) => {
      const { x, y } = getSvgCoords(coord[1], coord[0]);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  const handleSvgCircleHover = (e: React.MouseEvent, stop: RankingItem) => {
    const rect = e.currentTarget.parentElement?.getBoundingClientRect();
    if (rect) {
      const x = e.clientX - rect.left + 15;
      const y = e.clientY - rect.top - 40;
      setTooltipPos({ x, y });
      setHoveredStop(stop);
    }
  };

  return (
    <div className="flex-1 bg-slate-100 rounded-xl border border-slate-200 shadow-inner overflow-hidden relative min-h-[400px] flex flex-col">
      {/* Map Header Panel */}
      <div className="absolute top-4 left-4 z-10 bg-white/95 backdrop-blur border border-slate-200 rounded-lg px-3.5 py-2 shadow-md flex items-center gap-2 text-xs">
        <MapIcon className="h-4 w-4 text-slate-500" />
        <span className="font-semibold text-slate-800">Hartford Bus Stop Priority Map</span>
      </div>

      {/* Map Legend Overlay */}
      <div className="absolute bottom-4 left-4 z-10 bg-white/95 backdrop-blur border border-slate-200 rounded-lg p-3 shadow-md text-xs select-none">
        <span className="font-bold text-slate-800 block mb-1.5 uppercase tracking-wider text-[10px]">
          Priority Legend
        </span>
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-red-600 border border-slate-700" />
            <span className="text-slate-700 font-medium">Critical (80-100)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-orange-500 border border-slate-700" />
            <span className="text-slate-700 font-medium">High (60-79)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-yellow-500 border border-slate-700" />
            <span className="text-slate-700 font-medium">Moderate (40-59)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-blue-600 border border-slate-700" />
            <span className="text-slate-700 font-medium">Low (0-39)</span>
          </div>
        </div>
      </div>

      {/* Real Map Container */}
      {!useFallback && (
        <div ref={mapContainerRef} className="w-full flex-1" />
      )}

      {/* Fallback Vector SVG Map */}
      {useFallback && (
        <div className="w-full flex-1 relative bg-slate-50 flex items-center justify-center p-4">
          <div className="absolute top-4 right-4 bg-amber-50 border border-amber-200 text-amber-800 rounded px-2.5 py-1 text-[10px] flex items-center gap-1.5 shadow-sm font-medium z-10">
            <ShieldAlert className="h-3.5 w-3.5" />
            <span>WebGL unavailable. Displaying interactive vector map.</span>
          </div>

          <svg
            viewBox="0 0 500 500"
            className="w-full h-full max-h-[500px] max-w-[500px]"
            xmlns="http://www.w3.org/2000/svg"
          >
            {/* Hartford Boundary Polygon */}
            <polygon
              points={boundaryPointsStr}
              fill="#e2e8f0"
              fillOpacity="0.5"
              stroke="#64748b"
              strokeWidth="2"
              strokeDasharray="4,4"
            />

            {/* Bus Stop Points */}
            {items.map((stop) => {
              const { x, y } = getSvgCoords(stop.latitude, stop.longitude);
              const isSelected = stop.bus_stop_id === selectedStopId;
              const color = getColorForCategory(stop.priority_category);

              return (
                <circle
                  key={stop.bus_stop_id}
                  cx={x}
                  cy={y}
                  r={isSelected ? 10 : 5.5}
                  fill={color}
                  stroke={isSelected ? "#ffffff" : "#1e293b"}
                  strokeWidth={isSelected ? 2.5 : 1}
                  className="cursor-pointer transition-all hover:scale-125"
                  onClick={() => onSelectStop(stop.bus_stop_id)}
                  onMouseEnter={(e) => handleSvgCircleHover(e, stop)}
                  onMouseLeave={() => setHoveredStop(null)}
                />
              );
            })}
          </svg>

          {/* SVG Tooltip */}
          {hoveredStop && (
            <div
              className="absolute bg-white border border-slate-200 shadow-md p-2.5 rounded text-xs z-20 pointer-events-none min-w-[180px]"
              style={{ left: tooltipPos.x, top: tooltipPos.y }}
            >
              <div className="font-bold text-slate-800 truncate mb-1">
                {hoveredStop.stop_name}
              </div>
              <div className="flex justify-between items-center text-slate-600">
                <span>Priority Score:</span>
                <span className="font-bold" style={{ color: getColorForCategory(hoveredStop.priority_category) }}>
                  {hoveredStop.priority_score}
                </span>
              </div>
              <div className="text-[10px] text-slate-400 mt-0.5">
                {hoveredStop.priority_category} Priority
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
