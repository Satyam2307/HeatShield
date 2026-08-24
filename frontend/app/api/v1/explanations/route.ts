import { NextRequest, NextResponse } from "next/server";
import { ExplanationResponse } from "@/lib/types";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const question = (body.question || "").trim().toLowerCase();

    let explanation = "";

    if (question.includes("why is this stop ranked first") || question.includes("ranked first") || question.includes("top stop")) {
      explanation = "The first-ranked bus stop (Main St & Gold St) is prioritized because it suffers from a severe combination of heat risk and vulnerability factors. It experiences 240 dangerous minutes above the temperature threshold, has an 85% shade deficit with zero canopy cover, and serves a critical downtown transit node with 5 overlapping routes. Additionally, the surrounding Census tract has a high community vulnerability score (92/100) and a high percentage of zero-vehicle households (60%), making passengers heavily dependent on public transit shelters.";
    } else if (question.includes("which five stops") || question.includes("5 stops") || question.includes("five stops")) {
      explanation = "The top 5 Hartford bus stops recommended for immediate shade intervention are:\n\n1. **Main St & Gold St** (Priority: 86/100, 240 dangerous minutes)\n2. **Albany Ave & Woodland St** (Priority: 82/100, 210 dangerous minutes)\n3. **Farmington Ave & Sigourney St** (Priority: 79/100, 195 dangerous minutes)\n4. **Park St & Broad St** (Priority: 77/100, 180 dangerous minutes)\n5. **Franklin Ave & Maple Ave** (Priority: 72/100, 165 dangerous minutes)\n\nThese stops collectively represent the intersection of highest heat exposure and transit density.";
    } else if (question.includes("persistent heat") || question.includes("persistent locations")) {
      explanation = "The most persistent heat locations are concentrated along major commercial corridors with high impervious surface cover and minimal canopy. Specifically, **Albany Ave & Woodland St** and **Barbour St & Charlotte St** experience the longest continuous periods above the 95°F danger threshold, with uninterrupted heat durations exceeding 140 minutes during peak afternoon hours (1:30 PM to 4:00 PM).";
    } else if (question.includes("vulnerability") || question.includes("more weight")) {
      explanation = "Increasing the weight of community vulnerability (e.g. from 20% to 40%) shifts priority towards the North End (Clay-Arsenal, Northeast) and South Green neighborhoods. Stops like **Barbour St & Charlotte St** (vulnerability score 96) and **Albany Ave & Woodland St** (vulnerability score 95) rise in the rankings, while stops located in lower-density or wealthier tracts (such as Asylum Ave corridors) drop down, reflecting a greater emphasis on transit equity.";
    } else {
      explanation = "Based on Hartford transit planning data, heat exposure and shade deficit remain the key technical drivers of the ranking. Please select one of the preset questions or ask about rankings, top stops, persistent heat, or vulnerability weights to retrieve detailed planning explanations.";
    }

    const response: ExplanationResponse = { explanation };
    return NextResponse.json(response);
  } catch (error) {
    return NextResponse.json({ error: "Failed to generate explanation" }, { status: 500 });
  }
}
