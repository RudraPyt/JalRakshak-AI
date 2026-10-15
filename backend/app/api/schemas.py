"""Pydantic request and response schemas for FastAPI endpoints."""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from ..models.enums import EventType, UrgencyLevel, BoatStatus, ShelterStatus, EdgeStatus, IncidentLifecycleStatus, ActionType
from ..models.graph import ZoneNode, NetworkEdge
from ..models.incident import Incident
from ..models.boat import Boat
from ..models.shelter import Shelter
from ..models.assignment import Assignment
from ..models.decision_log import DecisionLogEntry


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    service: str = "JalRakshak AI — Adaptive Flood Rescue Coordination API"


class SimulationResetRequest(BaseModel):
    strategy: Literal["centralized", "multi_agent"] = Field(
        default="centralized",
        description="Dispatch strategy to activate: 'centralized' (baseline) or 'multi_agent' (CNP)",
    )


class SimulationStepResponse(BaseModel):
    minute: int
    strategy: str
    is_running: bool
    active_assignments_count: int
    newly_invalidated_count: int
    kpis: Dict[str, Any]
    invariants_passed: bool
    invariant_violations: List[str] = Field(default_factory=list)


class SimulationStateResponse(BaseModel):
    minute: int
    strategy: str
    is_running: bool
    kpis: Dict[str, Any]
    zones: List[ZoneNode]
    edges: List[NetworkEdge]
    boats: List[Boat]
    shelters: List[Shelter]
    incidents: List[Incident]
    active_assignments: List[Assignment]


class EventInjectRequest(BaseModel):
    event_type: EventType
    target_id: str = Field(..., description="Target edge ID, boat ID, shelter ID, or incident ID")
    description: str = Field(..., description="Human-readable reason for the event")
    simulation_minute: Optional[int] = Field(
        default=None,
        ge=0,
        description="Minute at which event triggers. Defaults to immediate execution at current minute.",
    )
    source_confidence: str = Field(default="high", description="'high', 'medium', or 'low'")


class EventInjectResponse(BaseModel):
    event_id: str
    event_type: EventType
    target_id: str
    simulation_minute: int
    applied: bool
    message: str


class ReplaySnapshot(BaseModel):
    minute: int
    strategy: str
    kpis: Dict[str, Any]
    boats: List[Dict[str, Any]]
    shelters: List[Dict[str, Any]]
    incidents: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    assignments: List[Dict[str, Any]]
    invariants_ok: bool


class ReplayTimelineResponse(BaseModel):
    total_snapshots: int
    recorded_minutes: List[int]
    active_strategy: str


class CompareRequest(BaseModel):
    simulation_minutes: int = Field(default=15, ge=1, le=60, description="Duration to evaluate both strategies")
    include_stretch_events: bool = Field(default=False, description="Whether to include simultaneous stretch failures")


class LogsResponse(BaseModel):
    total_count: int
    returned_count: int
    logs: List[DecisionLogEntry]
