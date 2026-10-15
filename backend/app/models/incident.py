"""Incident data model and lifecycle validation."""

from typing import Optional
from pydantic import BaseModel, Field, model_validator
from .enums import UrgencyLevel, VerificationStatus, IncidentLifecycleStatus


class Incident(BaseModel):
    """An emergency rescue request."""
    incident_id: str = Field(..., description="Unique incident identifier (e.g., INC001)")
    zone: str = Field(..., description="Zone where the incident is located")
    x: float = Field(..., description="Simulation X-coordinate")
    y: float = Field(..., description="Simulation Y-coordinate")
    people_affected: int = Field(..., gt=0, description="Total individuals in distress")
    people_rescued: int = Field(default=0, ge=0, description="Individuals safely transported and delivered to a shelter")
    people_onboard: int = Field(default=0, ge=0, description="Individuals currently in transit on a boat")
    report_age_min: float = Field(default=0.0, ge=0.0, description="Age of report in minutes when loaded")
    reported_urgency: UrgencyLevel = Field(..., description="Reported triage urgency")
    source_confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Reliability score of reporting source")
    verification_status: VerificationStatus = Field(default=VerificationStatus.REPORTED)
    lifecycle_status: IncidentLifecycleStatus = Field(default=IncidentLifecycleStatus.PENDING_ASSIGNMENT)
    
    # Assignment tracking
    assigned_boat_id: Optional[str] = Field(default=None, description="Currently assigned boat, if any")
    assigned_shelter_id: Optional[str] = Field(default=None, description="Destination shelter, if assigned")
    
    # Progress timestamps
    reported_at_minute: int = Field(default=0, ge=0, description="Simulation minute when incident entered system")
    served_at_minute: Optional[int] = Field(default=None, description="Simulation minute when final delivery occurred")
    status_explanation: Optional[str] = Field(default=None, description="Human-readable reason for current status")

    @property
    def people_awaiting_pickup(self) -> int:
        """Individuals still stranded at the incident site."""
        return max(0, self.people_affected - self.people_rescued - self.people_onboard)

    @property
    def is_fully_resolved(self) -> bool:
        """True only if all affected people have been safely delivered to a shelter."""
        return self.people_rescued >= self.people_affected

    @model_validator(mode="after")
    def validate_headcounts(self):
        """Enforce strict invariant: rescued + onboard cannot exceed affected."""
        if self.people_rescued + self.people_onboard > self.people_affected:
            raise ValueError(
                f"Headcount invariant violation on {self.incident_id}: "
                f"rescued ({self.people_rescued}) + onboard ({self.people_onboard}) "
                f"> total affected ({self.people_affected})"
            )
        return self
