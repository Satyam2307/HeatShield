import { NextRequest, NextResponse } from "next/server";
import { BUS_STOPS_LIST, getAssetDetails } from "@/lib/fixtures/bus-stops";

export async function GET(
  req: NextRequest,
  { params }: { params: { analysisId: string } }
) {
  try {
    const { searchParams } = new URL(req.url);
    const limit = parseInt(searchParams.get("limit") || "100", 10);

    const results = BUS_STOPS_LIST.slice(0, limit).map((stop) => {
      const detail = getAssetDetails(stop.bus_stop_id);
      return {
        rank: stop.rank,
        stop_id: stop.bus_stop_id,
        stop_name: stop.stop_name,
        latitude: stop.latitude,
        longitude: stop.longitude,
        priority_score: stop.priority_score,
        priority_category: stop.priority_category,
        dangerous_minutes: stop.dangerous_minutes,
        cumulative_exceedance: stop.cumulative_exceedance,
        shade_deficit_pct: stop.shade_deficit,
        routes_count: stop.routes_served.length,
        vulnerability_score: stop.vulnerability_score,
        median_income: detail?.community_vulnerability.median_income || 35000,
        zero_vehicle_pct: Math.round((detail?.community_vulnerability.zero_vehicle_fraction || 0.3) * 100),
        recommended_intervention: stop.recommended_intervention,
      };
    });

    return NextResponse.json({
      analysis_id: params.analysisId,
      total: results.length,
      results,
    });
  } catch (error) {
    return NextResponse.json({ error: "Failed to generate report" }, { status: 500 });
  }
}
