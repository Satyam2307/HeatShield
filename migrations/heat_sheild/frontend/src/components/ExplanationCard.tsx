import React, { useState, useEffect } from 'react';
import { BusStop, ExplanationResult } from '../types';
import { fetchExplanation } from '../api';
import { FileText, CheckCircle2, ShieldAlert } from 'lucide-react';

interface ExplanationCardProps {
  selectedStop: BusStop;
}

export const ExplanationCard: React.FC<ExplanationCardProps> = ({ selectedStop }) => {
  const [explanation, setExplanation] = useState<ExplanationResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    fetchExplanation(selectedStop.asset_id)
      .then((res) => {
        if (isMounted) {
          setExplanation(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error(err);
        if (isMounted) setLoading(false);
      });
    return () => {
      isMounted = false;
    };
  }, [selectedStop.asset_id]);

  return (
    <div className="glass-card rounded-xl p-4 border border-slate-800 space-y-3">
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
        <FileText className="h-4 w-4 text-orange-400" />
        <h3 className="text-sm font-bold text-white font-display">Structured Recommendation Evidence</h3>
      </div>

      {loading || !explanation ? (
        <div className="py-4 text-center text-xs text-slate-400 animate-pulse">
          Generating evidence summary...
        </div>
      ) : (
        <div className="space-y-3 text-xs">
          <p className="text-slate-300 leading-relaxed bg-slate-900/80 p-3 rounded-lg border border-slate-800/80">
            "{explanation.summary_explanation}"
          </p>

          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1.5">
              Key Priority Drivers:
            </span>
            <ul className="space-y-1">
              {explanation.key_drivers.map((driver, i) => (
                <li key={i} className="flex items-start gap-2 text-slate-300">
                  <CheckCircle2 className="h-3.5 w-3.5 text-orange-400 shrink-0 mt-0.5" />
                  <span>{driver}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
