"""FastAPI routes for simulation control and state inspection."""

from fastapi import APIRouter
from .schemas import (
    SimulationResetRequest,
    SimulationStepResponse,
    SimulationStateResponse,
)
from .session import session_manager

router = APIRouter(prefix="/api/simulation", tags=["Simulation Control"])


@router.get("/state", response_model=SimulationStateResponse)
def get_simulation_state():
    """Retrieve the authoritative world state, entities, and active assignments."""
    return session_manager.get_state()


@router.post("/step", response_model=SimulationStepResponse)
def step_simulation():
    """Advance the simulation clock by exactly one minute, executing the 7-step event loop."""
    return session_manager.step()


@router.post("/reset", response_model=SimulationStateResponse)
def reset_simulation(req: SimulationResetRequest):
    """Reset the simulation environment to initial state with the selected strategy."""
    return session_manager.reset(strategy=req.strategy)


@router.post("/pause")
def pause_simulation():
    """Pause the simulation."""
    return session_manager.pause()


@router.post("/resume")
def resume_simulation():
    """Resume execution."""
    return session_manager.resume()
