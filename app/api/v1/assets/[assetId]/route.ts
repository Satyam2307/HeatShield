import { NextRequest, NextResponse } from "next/server";
import { getAssetDetails } from "@/lib/fixtures/bus-stops";

export async function GET(
  req: NextRequest,
  { params }: { params: { assetId: string } }
) {
  try {
    const assetId = params.assetId;
    const detail = getAssetDetails(assetId);

    if (!detail) {
      return NextResponse.json({ error: "Asset not found" }, { status: 404 });
    }

    return NextResponse.json(detail);
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch asset details" }, { status: 500 });
  }
}
