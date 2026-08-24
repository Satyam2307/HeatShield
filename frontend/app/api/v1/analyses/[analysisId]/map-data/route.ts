import { NextRequest, NextResponse } from "next/server";
import { BUS_STOPS_LIST } from "@/lib/fixtures/bus-stops";

export async function GET(
  req: NextRequest,
  { params }: { params: { analysisId: string } }
) {
  try {
    const features = BUS_STOPS_LIST.map((stop) => ({
      type: "Feature",
      geometry: {
        type: "Point",
        coordinates: [stop.longitude, stop.latitude],
      },
      properties: {
        stop_id: stop.bus_stop_id,
        stop_name: stop.stop_name,
        rank: stop.rank,
        priority_score: stop.priority_score,
        priority_category: stop.priority_category,
        dangerous_minutes: stop.dangerous_minutes,
      },
    }));

    return NextResponse.json({
      type: "FeatureCollection",
      features,
    });
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch map data" }, { status: 500 });
  }
}
