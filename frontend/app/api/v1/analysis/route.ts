import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json().catch(() => ({}));
    return NextResponse.json({
      analysis_id: "analysis-001",
      city_id: body.city_id || "hartford-ct",
      status: "completed",
      total_stops: 105,
      scoring_version: "v1.0",
      created_at: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json({ error: "Failed to create analysis" }, { status: 500 });
  }
}
