"""Rescue boat resource data model."""

from typing import List, Optional
from pydantic import BaseModel, Field, model_validator
from .enums import BoatStatus


class Boat(BaseModel):
    """A simulated rescue boat resource."""
    boat_id: str = Field(..., description="Unique boat identifier (e.g., BOAT01)")
    current_zone: str = Field(..., description="Current zone location of the boat")
    x: float = Field(..., description="Current simulation X-coordinate")
    y: float = Field(..., description="Current simulation Y-coordinate")
    capacity_people: int = Field(..., gt=0, description="Maximum passenger carrying capacity")
    speed_units_per_min: float = Field(..., gt=0.0, description="Movement speed across distance units per minute")
    status: BoatStatus = Field(default=BoatStatus.AVAILABLE)
    safety_factor: float = Field(default=1.0, gt=0.0, description="Operational safety coefficient")

    # Dynamic mission attributes
    onboard_people: int = Field(default=0, ge=0, description="Number of rescued passengers currently aboard")
    assigned_incident_id: Optional[str] = Field(default=None, description="Incident currently being served")
    target_shelter_id: Optional[str] = Field(default=None, description="Destination shelter for delivery")
    planned_route_zones: List[str] = Field(default_factory=list, description="Waypoints remaining on active mission")
    
    # Failure recovery tracking
    failed_until_minute: Optional[int] = Field(default=None, description="Simulation minute when boat will be repaired")
    failure_reason: Optional[str] = Field(default=None, description="Logged reason for outage")

    # Performance metric tracking
    total_idle_minutes: int = Field(default=0, ge=0, description="Cumulative minutes available without assignment")
    total_service_minutes: int = Field(default=0, ge=0, description="Cumulative minutes actively on mission")

    @property
    def remaining_carrying_capacity(self) -> int:
        """Available passenger spaces on the boat."""
        return max(0, self.capacity_people - self.onboard_people)

    @property
    def is_operational(self) -> bool:
        """True if boat is mechanically sound and not in failed/maintenance state."""
        return self.status not in (BoatStatus.FAILED, BoatStatus.MAINTENANCE)

    @model_validator(mode="after")
    def validate_capacity(self):
        """Invariant: Onboard passengers cannot exceed carrying capacity."""
        if self.onboard_people > self.capacity_people:
            raise ValueError(
                f"Boat {self.boat_id} capacity exceeded: onboard ({self.onboard_people}) "
                f"> capacity ({self.capacity_people})"
            )
        return self
