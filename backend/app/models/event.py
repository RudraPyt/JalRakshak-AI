"""Scenario event data model."""

from pydantic import BaseModel, Field
from .enums import EventType


class ScenarioEvent(BaseModel):
    """A time-injected dynamic event modifying the simulation environment."""
    event_id: str = Field(..., description="Unique event identifier (e.g., EV001)")
    simulation_minute: int = Field(..., ge=0, description="Simulation minute when event triggers")
    event_type: EventType = Field(..., description="Nature of the environmental change")
    target_id: str = Field(..., description="Target entity ID (Edge, Boat, Shelter, or Incident)")
    description: str = Field(..., description="Human-readable description of the event")
    source_confidence: str = Field(default="high", description="Source confidence rating (high, medium, low)")
    applied: bool = Field(default=False, description="Whether this event has been executed")
