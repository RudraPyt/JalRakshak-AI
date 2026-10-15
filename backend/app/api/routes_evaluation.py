"""FastAPI routes for performance evaluation and strategy benchmarking."""

from typing import Any, Dict
from fastapi import APIRouter
from .schemas import CompareRequest
from .session import session_manager
from ..core.metrics import SimulationMetrics

router = APIRouter(prefix="/api/evaluation", tags=["Evaluation & Benchmarks"])


@router.get("/current")
def get_current_metrics():
    """Retrieve quantitative performance metrics for the currently running simulation session."""
    with session_manager.lock:
        disp_name = (
            session_manager.world_state.dispatcher.name
            if session_manager.world_state.dispatcher
            else session_manager.strategy_name
        )
        return SimulationMetrics.evaluate_run(
            session_manager.world_state,
            disp_name,
        )


@router.post("/compare")
def compare_strategies(req: CompareRequest):
    """
    Execute an independent, deterministic side-by-side run of both the Centralized Greedy Baseline
    and the Decentralized Multi-Agent Strategy (CNP) across the requested simulation minutes.
    """
    return session_manager.compare_strategies(
        minutes=req.simulation_minutes,
        include_stretch=req.include_stretch_events,
    )


@router.post("/stretch-challenge")
def run_stretch_challenge():
    """
    Execute the official simultaneous stretch challenge:
    Concurrently closes bridge N2, fails BOAT03, and overflows shelter SH02 at minute 5,
    evaluating recovery across both strategies through minute 15.
    """
    return session_manager.compare_strategies(
        minutes=15,
        include_stretch=True,
    )
