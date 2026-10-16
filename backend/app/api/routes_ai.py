"""FastAPI routes for Gemini AI Emergency Situation Analyst."""

from typing import Optional
from fastapi import APIRouter
from .schemas import SituationReportResponse, SituationReportRequest
from .session import session_manager
from ..services.ai_analyst import EmergencySituationAnalyst

router = APIRouter(prefix="/api/ai", tags=["AI Emergency Situation Analyst"])


@router.post("/situation-report", response_model=SituationReportResponse)
def generate_situation_report(req: Optional[SituationReportRequest] = None):
    """
    Generate an AI-powered Emergency Situation Report using Google Gemini.

    Obtains a consistent snapshot of the current simulation, validates required fields,
    prepares a compact structured context, calls Gemini via Google's official `google-genai` SDK,
    and returns a structured advisory report for human operator decision-support.
    """
    with session_manager.lock:
        world_state = session_manager.world_state
        strategy = session_manager.strategy_name

    return EmergencySituationAnalyst.generate_situation_report(
        world_state=world_state,
        strategy_name=strategy,
        req=req,
    )
