import { BusStop, SimulationResult, ExplanationResult, Weights } from './types';

const API_BASE = '/api/v1';

export async function fetchRankings(weights?: Weights, dangerThreshold: number = 95): Promise<BusStop[]> {
  try {
    const res = await fetch(`${API_BASE}/analysis`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        city_id: 'hartford-ct',
        start_time: '2024-07-15T10:00:00-04:00',
        end_time: '2024-07-15T18:00:00-04:00',
        heat_metric: 'heat_index',
        heat_unit: 'F',
        danger_threshold: dangerThreshold,
        weights: weights || { heat: 0.40, shade: 0.25, vulnerability: 0.20, transit: 0.15 }
      })
    });
    if (res.ok) {
      const data = await res.json();
      return data.rankings;
    }
  } catch (err) {
    console.warn('Backend API unreachable, attempting direct fixture fallback:', err);
  }

  // Fallback to static fixture data
  const fallbackRes = await fetch('/data/hartford_demo.json');
  if (fallbackRes.ok) {
    const data = await fallbackRes.json();
    return data.rankings;
  }
  throw new Error('Failed to load bus stop rankings data');
}

export async function simulateIntervention(
  assetId: string,
  scenario: 'conservative' | 'moderate' | 'high' = 'moderate'
): Promise<SimulationResult> {
  try {
    const res = await fetch(`${API_BASE}/interventions/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        analysis_id: 'hartford-demo-2024-07-15',
        asset_id: assetId,
        intervention_type: 'shade_structure',
        scenario: scenario
      })
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Simulation API offline:', err);
  }
  throw new Error('Intervention simulation failed');
}

export async function fetchExplanation(assetId: string): Promise<ExplanationResult> {
  try {
    const res = await fetch(`${API_BASE}/explanations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        analysis_id: 'hartford-demo-2024-07-15',
        asset_id: assetId
      })
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Explanation API offline:', err);
  }
  throw new Error('Failed to fetch explanation');
}

export function downloadReportCSV() {
  window.open(`${API_BASE}/reports/hartford-demo-2024-07-15`, '_blank');
}
