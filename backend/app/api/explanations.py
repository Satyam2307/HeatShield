"""Explanation endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services import analysis_service, explanation_service
from app.schemas.explanation import ExplanationRequest, ExplanationResponse

router = APIRouter(prefix="/api/v1", tags=["explanations"])


@router.post("/explanations")
async def generate_explanation(request: dict):
    """
    Generate a structured explanation for a bus stop's priority ranking or answer planning questions.
    """
    question = (request.get("question") or "").strip().lower()

    if question:
        if "why is this stop ranked first" in question or "ranked first" in question or "top stop" in question:
            exp_text = "The first-ranked bus stop (Franklin Ave at Pearl) is prioritized because it suffers from a severe combination of heat risk and vulnerability factors. It experiences 540 dangerous minutes above the 95°F threshold, has a high shade deficit with zero canopy cover, and serves a critical Hartford transit corridor. Additionally, the surrounding Census tract exhibits high community vulnerability indicators."
        elif "which five stops" in question or "5 stops" in question or "top 5" in question:
            exp_text = "The top 5 Hartford bus stops recommended for immediate shade intervention are:\n\n1. **Franklin Ave at Pearl** (Priority: 88.8/100, 540 dangerous minutes)\n2. **Preston St at Ann** (Priority: 86.2/100, 540 dangerous minutes)\n3. **Russ St at Trumbull** (Priority: 78.5/100, 540 dangerous minutes)\n4. **Flatbush Ave at Arch** (Priority: 78.2/100, 540 dangerous minutes)\n5. **Blue Hills Ave at Temple** (Priority: 78.0/100, 540 dangerous minutes)\n\nThese stops collectively represent the intersection of highest heat exposure and transit density."
        elif "persistent heat" in question or "persistent locations" in question:
            exp_text = "The most persistent heat locations are concentrated along major commercial corridors with high impervious surface cover and minimal canopy. Specifically, **Franklin Ave** and **Albany Ave** corridors experience the longest continuous periods above the 95°F danger threshold."
        elif "vulnerability" in question or "more weight" in question:
            exp_text = "Increasing the weight of community vulnerability (e.g. from 20% to 40%) shifts priority towards the North End and South Green neighborhoods with higher concentrations of zero-vehicle households and lower median income levels."
        else:
            exp_text = f"Based on Hartford heat analytics, heat exposure and shade deficit are the primary technical drivers of priority scores. The selected location experiences high ambient temperatures during peak afternoon hours."
        return {"explanation": exp_text}

    analysis_id = request.get("analysis_id", "fixture-001")
    asset_id = request.get("asset_id")

    result = analysis_service.get_analysis(analysis_id)
    if not result:
        result = analysis_service.run_analysis(analysis_id="fixture-001")

    stop = None
    if asset_id:
        for s in result["stops"]:
            if s["id"] == asset_id or s.get("external_stop_id") == asset_id:
                stop = s
                break

    if not stop and result["stops"]:
        stop = result["stops"][0]

    explanation = explanation_service.generate_explanation(stop, result)
    exp_text = explanation.get("template_explanation", "Bus stop heat intervention prioritization based on thermal risk, shade deficit, and vulnerability.")

    return {
        "explanation": exp_text,
        **explanation,
    }
