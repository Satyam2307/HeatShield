"""Report export endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from app.services import analysis_service, report_service
from app.schemas.report import ReportResponse, ReportMetadata

router = APIRouter(prefix="/api/v1", tags=["reports"])


@router.get("/reports/{analysis_id}")
async def get_report(analysis_id: str, format: str = "csv"):
    """
    Export analysis report.

    format=csv returns a CSV file download.
    format=json returns report metadata.
    """
    result = analysis_service.get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")

    if format == "csv":
        csv_content = report_service.generate_csv_report(result)
        return PlainTextResponse(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=heatshield_report_{analysis_id}.csv"
            },
        )

    # JSON metadata
    metadata = report_service.get_report_metadata(result)
    return ReportResponse(
        metadata=ReportMetadata(**metadata),
        format="json",
    )
