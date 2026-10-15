"""FastAPI routes for dynamic scenario event inspection and manual injection."""

from typing import List
from fastapi import APIRouter
from .schemas import EventInjectRequest, EventInjectResponse
from ..models.event import ScenarioEvent
from .session import session_manager

router = APIRouter(prefix="/api/events", tags=["Dynamic Events"])


@router.get("", response_model=List[ScenarioEvent])
def list_events():
    """Retrieve all scheduled, injected, and applied events in the current session."""
    with session_manager.lock:
        return session_manager.world_state.events


@router.post("/inject", response_model=EventInjectResponse)
def inject_event(req: EventInjectRequest):
    """
    Manually inject an environmental event (road closure, boat failure, shelter overflow,
    conflicting report, or road reopening) into the active simulation.
    """
    return session_manager.inject_event(req)
