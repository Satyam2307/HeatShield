import { NextRequest, NextResponse } from "next/server";
import { getTimeSeriesForStop } from "@/lib/fixtures/time-series";

export async function GET(
  req: NextRequest,
  { params }: { params: { assetId: string } }
) {
  try {
    const assetId = params.assetId;
    const series = getTimeSeriesForStop(assetId);

    if (!series || series.length === 0) {
      return NextResponse.json({ error: "Time series not found for asset" }, { status: 404 });
    }

    return NextResponse.json(series);
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch asset time series" }, { status: 500 });
  }
}
