import React, { useState, useEffect } from 'react';
import { BusStop, Weights } from './types';
import { fetchRankings, downloadReportCSV } from './api';
import { Header } from './components/Header';
import { ScenarioBar } from './components/ScenarioBar';
import { MapView } from './components/MapView';
import { RankingsTable } from './components/RankingsTable';
import { StopDetailPanel } from './components/StopDetailPanel';
import { InterventionSimulator } from './components/InterventionSimulator';
import { ExplanationCard } from './components/ExplanationCard';
import { MethodologyModal } from './components/MethodologyModal';

export const App: React.FC = () => {
  const [stops, setStops] = useState<BusStop[]>([]);
  const [selectedStop, setSelectedStop] = useState<BusStop | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [isRecalculating, setIsRecalculating] = useState<boolean>(false);
  const [isMethodologyOpen, setIsMethodologyOpen] = useState<boolean>(false);

  const [dangerThreshold, setDangerThreshold] = useState<number>(95);
  const [weights, setWeights] = useState<Weights>({
    heat: 0.40,
    shade: 0.25,
    vulnerability: 0.20,
    transit: 0.15
  });

  const loadData = (customWeights?: Weights, threshold?: number) => {
    setIsRecalculating(true);
    fetchRankings(customWeights || weights, threshold || dangerThreshold)
      .then((data) => {
        setStops(data);
        if (data.length > 0) {
          // Maintain selected stop or default to #1 top ranked
          setSelectedStop((prev) => {
            if (prev) {
              const updated = data.find((s) => s.asset_id === prev.asset_id);
              return updated || data[0];
            }
            return data[0];
          });
        }
        setLoading(false);
        setIsRecalculating(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
        setIsRecalculating(false);
      });
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      {/* Top Header */}
      <Header
        onExportCSV={downloadReportCSV}
        onOpenMethodology={() => setIsMethodologyOpen(true)}
        totalStops={stops.length}
      />

      {/* Scenario Control Bar */}
      <ScenarioBar
        weights={weights}
        dangerThreshold={dangerThreshold}
        onWeightsChange={(w) => setWeights(w)}
        onThresholdChange={(t) => setDangerThreshold(t)}
        onRecalculate={() => loadData(weights, dangerThreshold)}
        isRecalculating={isRecalculating}
      />

      {/* Main Dashboard Workspace */}
      <main className="flex-1 p-4 grid grid-cols-1 lg:grid-cols-12 gap-4 max-w-[1920px] w-full mx-auto">
        {/* Left Column: Interactive Map (Top) + Priority Rankings Table (Bottom) */}
        <div className="lg:col-span-7 flex flex-col gap-4 min-h-[700px]">
          <div className="h-[380px] w-full">
            <MapView
              stops={stops}
              selectedStop={selectedStop}
              onSelectStop={(s) => setSelectedStop(s)}
            />
          </div>
          <div className="flex-1 min-h-[320px]">
            <RankingsTable
              stops={stops}
              selectedStop={selectedStop}
              onSelectStop={(s) => setSelectedStop(s)}
            />
          </div>
        </div>

        {/* Right Column: Selected Stop Details + Intervention Simulator + Explanation Evidence */}
        <div className="lg:col-span-5 space-y-4 overflow-y-auto max-h-[calc(100vh-140px)] pr-1">
          {loading || !selectedStop ? (
            <div className="glass-panel p-8 rounded-xl text-center text-slate-400 animate-pulse">
              Loading Hartford bus stop analytics...
            </div>
          ) : (
            <>
              {/* Selected Stop Details & Heat Profile */}
              <StopDetailPanel stop={selectedStop} />

              {/* Shade Intervention Simulator */}
              <InterventionSimulator selectedStop={selectedStop} />

              {/* Recommendation Evidence Card */}
              <ExplanationCard selectedStop={selectedStop} />
            </>
          )}
        </div>
      </main>

      {/* Methodology Modal */}
      <MethodologyModal
        isOpen={isMethodologyOpen}
        onClose={() => setIsMethodologyOpen(false)}
      />
    </div>
  );
};
