"""Data models for Multi-Agent negotiation and Contract Net Protocol (CNP)."""

from typing import List, Optional
from pydantic import BaseModel, Field
from .graph import RoutePath
from .enums import UrgencyLevel


class TaskAnnouncement(BaseModel):
    """Call for Proposals (CFP) broadcast by an Incident Agent."""
    announcement_id: str
    incident_id: str
    zone: str
    people_in_distress: int = Field(..., gt=0)
    urgency: UrgencyLevel
    priority_score: float
    timestamp_min: int


class BoatBid(BaseModel):
    """Bid submitted by a Boat Agent in response to a TaskAnnouncement."""
    bid_id: str
    announcement_id: str
    incident_id: str
    boat_id: str
    current_zone: str
    feasible: bool = True
    bid_cost: float = Field(..., description="Estimated cost / travel time for the rescue")
    offered_capacity: int = Field(..., gt=0)
    route_to_incident: Optional[RoutePath] = None
    reason: Optional[str] = None


class ShelterBidResponse(BaseModel):
    """Response from a Shelter Agent regarding capacity availability."""
    shelter_id: str
    incident_id: str
    requested_spaces: int
    granted: bool
    granted_spaces: int = 0
    route_to_shelter: Optional[RoutePath] = None
    reason: Optional[str] = None


class ContractAward(BaseModel):
    """Binding agreement issued by the Coordinator Agent confirming an assignment."""
    award_id: str
    incident_id: str
    boat_id: str
    shelter_id: str
    headcount: int
    total_travel_time: float
    score: float
    timestamp_min: int
    rationale: str
