"""FastAPI routes for traceable explainable decision logs."""

from typing import Optional
from fastapi import APIRouter, Query
from ..models.enums import ActionType
from .schemas import LogsResponse
from .session import session_manager

router = APIRouter(prefix="/api/logs", tags=["Decision Logs"])


@router.get("/decisions", response_model=LogsResponse)
def get_decision_logs(
    action_type: Optional[ActionType] = Query(default=None, description="Filter by action type"),
    entity_id: Optional[str] = Query(default=None, description="Filter by affected entity ID"),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """Retrieve filterable, paginated audit logs with transparent reasoning for decisions."""
    return session_manager.get_logs(
        action_type=action_type,
        entity_id=entity_id,
        limit=limit,
        offset=offset,
    )
