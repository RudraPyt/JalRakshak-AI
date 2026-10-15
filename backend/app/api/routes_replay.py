"""FastAPI routes for after-action historical replay."""

from fastapi import APIRouter
from .schemas import ReplayTimelineResponse, ReplaySnapshot
from .session import session_manager

router = APIRouter(prefix="/api/replay", tags=["After-Action Replay"])


@router.get("/timeline", response_model=ReplayTimelineResponse)
def get_replay_timeline():
    """Retrieve chronological timeline index of all recorded simulation minutes."""
    return session_manager.get_replay_timeline()


@router.get("/snapshot/{minute}", response_model=ReplaySnapshot)
def get_replay_snapshot(minute: int):
    """Retrieve full deep-copy world state snapshot recorded at a specific simulation minute."""
    return session_manager.get_replay_snapshot(minute)
