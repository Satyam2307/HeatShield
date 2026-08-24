import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json([
    {
      id: "hartford-ct",
      name: "Hartford",
      state: "Connecticut",
      timezone: "America/New_York",
      bbox: [-72.713, 41.738, -72.65, 41.797],
    },
  ]);
}
