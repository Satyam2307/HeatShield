import React from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Polygon, Tooltip } from 'react-leaflet';
import { BusStop } from '../types';
import { Layers } from 'lucide-react';

interface MapViewProps {
  stops: BusStop[];
  selectedStop: BusStop | null;
  onSelectStop: (stop: BusStop) => void;
}

// Approximate Hartford Polygon boundary coords for map overlay
const HARTFORD_POLYGON_COORDS: [number, number][] = [
  [41.7483, -72.7166],
  [41.8025, -72.7150],
  [41.8080, -72.6900],
  [41.8040, -72.6480],
  [41.7700, -72.6500],
  [41.7220, -72.6650],
  [41.7300, -72.7000],
  [41.7483, -72.7166]
];

export const MapView: React.FC<MapViewProps> = ({ stops, selectedStop, onSelectStop }) => {
  const getMarkerColor = (category: string) => {
    switch (category) {
      case 'Critical': return '#ef4444';
      case 'High': return '#f97316';
      case 'Moderate': return '#eab308';
      case 'Low': return '#10b981';
      default: return '#3b82f6';
    }
  };

  return (
    <div className="relative h-full w-full rounded-xl overflow-hidden glass-panel border border-slate-800 shadow-xl">
      <MapContainer
        center={[41.7658, -72.6800]}
        zoom={13}
        scrollWheelZoom={true}
        className="h-full w-full z-0"
      >
        {/* CartoDB Dark Matter basemap */}
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://openstreetmap.org">OpenStreetMap</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {/* Hartford Boundary Line */}
        <Polygon
          positions={HARTFORD_POLYGON_COORDS}
          pathOptions={{
            color: '#f97316',
            weight: 2,
            dashArray: '6, 6',
            fillColor: '#f97316',
            fillOpacity: 0.05
          }}
        >
          <Tooltip sticky>Hartford City Boundary</Tooltip>
        </Polygon>

        {/* Bus Stop Circle Markers */}
        {stops.map((stop) => {
          const isSelected = selectedStop?.asset_id === stop.asset_id;
          const color = getMarkerColor(stop.priority_category);
          return (
            <CircleMarker
              key={stop.asset_id}
              center={[stop.latitude, stop.longitude]}
              radius={isSelected ? 10 : (stop.priority_category === 'Critical' ? 7 : 5)}
              pathOptions={{
                color: isSelected ? '#ffffff' : color,
                weight: isSelected ? 3 : 1.5,
                fillColor: color,
                fillOpacity: isSelected ? 0.95 : 0.75
              }}
              eventHandlers={{
                click: () => onSelectStop(stop)
              }}
            >
              <Tooltip direction="top" offset={[0, -5]} opacity={0.95}>
                <div className="text-xs font-sans">
                  <div className="font-bold text-slate-900">#{stop.rank} {stop.name}</div>
                  <div className="text-slate-700">Priority Score: {stop.priority_score} ({stop.priority_category})</div>
                  <div className="text-red-600 font-semibold">{stop.metrics.dangerous_minutes} dangerous mins</div>
                </div>
              </Tooltip>

              <Popup className="custom-popup">
                <div className="p-1 font-sans text-xs">
                  <div className="font-bold text-slate-900 text-sm">#{stop.rank} {stop.name}</div>
                  <div className="text-slate-600 mb-2">{stop.corridor}</div>
                  <div className="grid grid-cols-2 gap-1 mb-2">
                    <div className="bg-slate-100 p-1.5 rounded">
                      <span className="text-slate-500 block text-[10px]">Priority Score</span>
                      <strong className="text-orange-600 text-sm">{stop.priority_score}</strong>
                    </div>
                    <div className="bg-slate-100 p-1.5 rounded">
                      <span className="text-slate-500 block text-[10px]">Category</span>
                      <strong className="text-slate-800 text-xs">{stop.priority_category}</strong>
                    </div>
                  </div>
                  <button
                    onClick={() => onSelectStop(stop)}
                    className="w-full py-1 bg-orange-600 text-white rounded text-xs font-medium hover:bg-orange-500 transition-all"
                  >
                    Select & Simulate Shade
                  </button>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>

      {/* Map Legend Overlay */}
      <div className="absolute bottom-4 left-4 z-10 glass-panel p-3 rounded-lg text-xs space-y-1.5 border border-slate-800 pointer-events-auto">
        <div className="font-semibold text-slate-200 flex items-center gap-1.5 mb-1">
          <Layers className="h-3.5 w-3.5 text-orange-400" />
          <span>Priority Categories</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300">
          <span className="h-3 w-3 rounded-full bg-red-500 inline-block shadow-sm shadow-red-950"></span>
          <span>Critical (80–100)</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300">
          <span className="h-3 w-3 rounded-full bg-orange-500 inline-block shadow-sm shadow-orange-950"></span>
          <span>High (60–79)</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300">
          <span className="h-3 w-3 rounded-full bg-yellow-500 inline-block shadow-sm shadow-yellow-950"></span>
          <span>Moderate (40–59)</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300">
          <span className="h-3 w-3 rounded-full bg-emerald-500 inline-block shadow-sm shadow-emerald-950"></span>
          <span>Low (0–39)</span>
        </div>
      </div>
    </div>
  );
};
