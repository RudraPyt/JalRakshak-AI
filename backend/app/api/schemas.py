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


# ---------------------------------------------------------------------------
# Google Gemini AI Emergency Situation Analyst Schemas
# ---------------------------------------------------------------------------


class CriticalIncidentAnalysis(BaseModel):
    incident_id: str = Field(description="Incident identifier, e.g. INC01")
    location: str = Field(description="Zone or node location of the incident")
    urgency: str = Field(description="Urgency level from simulation data: CRITICAL, HIGH, MEDIUM, LOW")
    affected_population: int = Field(description="Total people affected recorded in simulation")
    waiting_population: int = Field(description="People still awaiting pickup")
    reason: str = Field(description="Data-supported reason why this incident needs immediate attention")


class ResourceStatusAnalysis(BaseModel):
    total_boats: int = Field(description="Total boats in fleet")
    available_boats: int = Field(description="Boats currently available/idle")
    dispatched_boats: int = Field(description="Boats currently in-transit or servicing")
    failed_boats: int = Field(description="Boats in failed/maintenance state")
    total_shelter_capacity: int = Field(description="Total capacity across all shelters")
    shelter_current_occupancy: int = Field(description="Total persons currently accommodated")
    shelter_remaining_capacity: int = Field(description="Remaining safe shelter capacity")
    shortages_and_notes: str = Field(description="Evidence-based shortage notes and capacity constraints")


class BottleneckOrRisk(BaseModel):
    category: str = Field(description="E.g., Road Blockage, Shelter Capacity, Vessel Failure, High Uncertainty, Safety Invariant")
    description: str = Field(description="Concise description of the bottleneck or operational risk")
    severity: Literal["low", "medium", "high", "critical"] = Field(description="Risk severity level")
    evidence: str = Field(description="Specific data points, IDs, or measurements supporting this risk")


class RecommendedAction(BaseModel):
    action_id: str = Field(description="Sequential identifier, e.g. ACT-1")
    title: str = Field(description="Short operational recommendation title")
    rationale: str = Field(description="Why this action is suggested based strictly on data")
    priority: Literal["low", "medium", "high", "critical"] = Field(description="Suggested urgency")
    target_entity: Optional[str] = Field(default=None, description="Target entity ID, e.g. BOAT01, SH02, Zone Z3")
    advisory_note: str = Field(
        default="Advisory recommendation for human operator review only; not autonomous dispatch.",
        description="Explicit notice that this is for human operator review"
    )


class StrategyPerformanceAnalysis(BaseModel):
    current_strategy: str = Field(description="Currently active strategy (centralized or multi_agent)")
    measurements_available: bool = Field(description="True if comparative evaluation measurements exist, false otherwise")
    summary: str = Field(description="Factual summary of strategy performance or statement that comparative benchmark is not yet run")
    comparison_details: Optional[Dict[str, Any]] = Field(default=None, description="Actual metrics if available")


class DataLimitationsAnalysis(BaseModel):
    has_limitations: bool = Field(description="Whether there are data limitations, stale data, or unobserved factors")
    limitations: List[str] = Field(description="List of specific data gaps, e.g. lack of comparative run, simulated environment")


class SituationReportResponse(BaseModel):
    simulation_minute: int = Field(description="Simulation minute snapshot analyzed")
    generated_at_utc: str = Field(description="UTC timestamp of report generation")
    model_used: str = Field(description="Gemini model used for analysis")
    advisory_disclaimer: str = Field(
        default=(
            "ADVISORY DISCLAIMER: This emergency situation report is generated by AI for simulation decision-support "
            "and human operator review only. It does NOT execute autonomous commands, dispatch assets, modify simulation "
            "state, or supersede safety invariants. Recommendations are not verified real-world rescue instructions."
        ),
        description="Legal and operational advisory disclaimer"
    )
    situation_overview: str = Field(description="Concise summary of the current simulated emergency situation")
    critical_incidents: List[CriticalIncidentAnalysis] = Field(description="Incidents requiring attention supported by data")
    resource_status: ResourceStatusAnalysis = Field(description="Current status of boats and shelters")
    bottlenecks_and_risks: List[BottleneckOrRisk] = Field(description="Evidence-based issues affecting rescue progress")
    recommended_actions: List[RecommendedAction] = Field(description="Practical recommendations for human operator review")
    strategy_performance: StrategyPerformanceAnalysis = Field(description="Strategy performance based on available measurements")
    data_limitations: DataLimitationsAnalysis = Field(description="Missing, stale, or insufficient data")


class SituationReportRequest(BaseModel):
    focus_area: Optional[str] = Field(
        default=None,
        description="Optional operational focus, e.g., 'evacuation', 'shelter_capacity', 'road_blockages'"
    )
