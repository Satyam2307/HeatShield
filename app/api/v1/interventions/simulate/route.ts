import { NextRequest, NextResponse } from "next/server";
import { InterventionRequestSchema, InterventionResponse } from "@/lib/types";
import { BUS_STOPS_LIST, getAssetDetails } from "@/lib/fixtures/bus-stops";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const result = InterventionRequestSchema.safeParse(body);

    if (!result.success) {
      return NextResponse.json(
        { error: "Invalid simulation request parameters", details: result.error.errors },
        { status: 400 }
      );
    }

    const { asset_id, scenario } = result.data;
    const detail = getAssetDetails(asset_id);

    if (!detail) {
      return NextResponse.json({ error: "Asset not found" }, { status: 404 });
    }

    const { searchParams } = new URL(req.url);
    const wHeat = parseFloat(searchParams.get("heat") ?? "0.40");
    const wShade = parseFloat(searchParams.get("shade") ?? "0.25");
    const wVuln = parseFloat(searchParams.get("vulnerability") ?? "0.20");
    const wTransit = parseFloat(searchParams.get("transit") ?? "0.15");

    const sum = wHeat + wShade + wVuln + wTransit;
    const normalize = (val: number) => (sum > 0 ? val / sum : 0.25);
    const nHeat = normalize(wHeat);
    const nShade = normalize(wShade);
    const nVuln = normalize(wVuln);
    const nTransit = normalize(wTransit);

    const reductionMap = {
      conservative: 0.20,
      moderate: 0.35,
      high: 0.50,
    };
    const reduction = reductionMap[scenario];

    const baseline_dangerous_minutes = detail.dangerous_minutes;
    const projected_dangerous_minutes = Math.round(baseline_dangerous_minutes * (1 - reduction));
    const avoided_dangerous_minutes = baseline_dangerous_minutes - projected_dangerous_minutes;
    const exposure_reduction_pct = Math.round(reduction * 100);

    const baseline_heat_score = detail.score_breakdown.heat_score;
    const projected_heat_score = Math.round(baseline_heat_score * (1 - reduction));
    
    const baseline_shade_deficit = detail.shade_deficit;
    const shadeReductionMap = { conservative: 0.30, moderate: 0.60, high: 0.90 };
    const projected_shade_deficit = Math.round(baseline_shade_deficit * (1 - shadeReductionMap[scenario]));

    const baseline_priority_score = detail.priority_score;
    
    const rawProjectedScore = (
      nHeat * projected_heat_score +
      nShade * projected_shade_deficit +
      nVuln * detail.score_breakdown.vulnerability_score +
      nTransit * detail.score_breakdown.transit_score
    );
    const projected_priority_score = Math.round(Math.max(0, Math.min(100, rawProjectedScore)));

    const stopScores = BUS_STOPS_LIST.map((stop) => {
      if (stop.bus_stop_id === asset_id) {
        return { id: stop.bus_stop_id, score: projected_priority_score };
      }
      
      const itemDetail = getAssetDetails(stop.bus_stop_id);
      if (!itemDetail) return { id: stop.bus_stop_id, score: stop.priority_score };

      const score = Math.round(
        nHeat * itemDetail.score_breakdown.heat_score +
        nShade * itemDetail.shade_deficit +
        nVuln * itemDetail.score_breakdown.vulnerability_score +
        nTransit * itemDetail.score_breakdown.transit_score
      );
      return { id: stop.bus_stop_id, score };
    });

    stopScores.sort((a, b) => b.score - a.score);
    const newRank = stopScores.findIndex((s) => s.id === asset_id) + 1;
    const rank_change = newRank - detail.rank;

    const response: InterventionResponse = {
      baseline_dangerous_minutes,
      projected_dangerous_minutes,
      avoided_dangerous_minutes,
      exposure_reduction_pct,
      baseline_priority_score,
      projected_priority_score,
      rank_change,
      assumptions: `Based on a mathematical projection where the ${scenario} shade structure scenario reduces direct thermal exposure by ${exposure_reduction_pct}% and reduces the local shade deficit by ${Math.round(shadeReductionMap[scenario] * 100)}%. This is a planning scenario, not a final engineering estimate.`,
    };

    return NextResponse.json(response);
  } catch (error) {
    return NextResponse.json({ error: "Failed to run simulation" }, { status: 500 });
  }
}
