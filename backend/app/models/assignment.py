"""Assignment and dispatch commitment data models."""

from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field
from .graph import RoutePath


class AssignmentStatus(str, Enum):
    """Execution status of an active rescue commitment."""
    COMMITTED = "COMMITTED"
    EN_ROUTE_PICKUP = "EN_ROUTE_PICKUP"
    SERVICING_PICKUP = "SERVICING_PICKUP"
    EN_ROUTE_SHELTER = "EN_ROUTE_SHELTER"
    DELIVERED = "DELIVERED"
    INVALIDATED = "INVALIDATED"
    CANCELLED = "CANCELLED"


class Assignment(BaseModel):
    """A binding contract committing a boat to serve an incident and deliver to a shelter."""
    assignment_id: str = Field(..., description="Unique commitment identifier")
    incident_id: str = Field(..., description="Target incident ID")
    boat_id: str = Field(..., description="Assigned boat ID")
    shelter_id: str = Field(..., description="Target shelter ID")
    people_assigned: int = Field(..., gt=0, description="Number of passengers allocated for this trip")
    route_to_incident: Optional[RoutePath] = Field(default=None, description="Path from boat's origin to incident")
    route_to_shelter: Optional[RoutePath] = Field(default=None, description="Path from incident to shelter")
    status: AssignmentStatus = Field(default=AssignmentStatus.COMMITTED)

    # Dynamic leg tracking
    pickup_travel_duration: int = Field(default=0, ge=0, description="Minutes required to reach incident")
    shelter_travel_duration: int = Field(default=0, ge=0, description="Minutes required to reach shelter from incident")
    minutes_in_leg: int = Field(default=0, ge=0, description="Elapsed simulation minutes in current leg")
    current_leg: str = Field(default="to_incident", description="'to_incident', 'to_shelter', 'delivered', 'invalidated'")

    # Timestamps & audit
    created_at_minute: int = Field(default=0, ge=0)
    completed_at_minute: Optional[int] = Field(default=None)
    invalidation_reason: Optional[str] = Field(default=None)
    rationale: Optional[str] = Field(default=None, description="Explainable reason for selection")
