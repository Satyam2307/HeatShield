import { NextRequest, NextResponse } from "next/server";
import { BUS_STOPS_LIST, getAssetDetails } from "@/lib/fixtures/bus-stops";
import { RankingItem } from "@/lib/types";

export async function GET(
  req: NextRequest,
  { params }: { params: { analysisId: string } }
) {
  try {
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

    const items: RankingItem[] = BUS_STOPS_LIST.map((stop) => {
      const detail = getAssetDetails(stop.bus_stop_id);
      
      const heatScore = detail ? detail.score_breakdown.heat_score : 50;
      const shadeScore = detail ? detail.score_breakdown.shade_score : 50;
      const vulnScore = detail ? detail.score_breakdown.vulnerability_score : 50;
      const transitScore = detail ? detail.score_breakdown.transit_score : 50;

      const computedScore = Math.round(
        nHeat * heatScore +
        nShade * shadeScore +
        nVuln * vulnScore +
        nTransit * transitScore
      );

      const finalScore = Math.round(Math.max(0, Math.min(100, computedScore)));

      let category: "Critical" | "High" | "Moderate" | "Low" = "Low";
      if (finalScore >= 80) category = "Critical";
      else if (finalScore >= 60) category = "High";
      else if (finalScore >= 40) category = "Moderate";

      return {
        ...stop,
        priority_score: finalScore,
        priority_category: category,
      };
    });

    items.sort((a, b) => b.priority_score - a.priority_score);
    items.forEach((item, idx) => {
      item.rank = idx + 1;
    });

    return NextResponse.json(items);
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch rankings" }, { status: 500 });
  }
}
