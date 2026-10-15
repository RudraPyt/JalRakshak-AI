"""Shelter capacity and reservation data model."""

from pydantic import BaseModel, Field, model_validator
from .enums import ShelterStatus


class Shelter(BaseModel):
    """An evacuation shelter destination."""
    shelter_id: str = Field(..., description="Unique shelter identifier (e.g., SH01)")
    name: str = Field(..., description="Shelter facility name")
    zone_id: str = Field(..., description="Nearest graph zone anchor")
    x: float = Field(..., description="Facility X-coordinate")
    y: float = Field(..., description="Facility Y-coordinate")
    capacity_people: int = Field(..., gt=0, description="Total maximum authorized occupancy")
    current_occupancy: int = Field(default=0, ge=0, description="Individuals physically sheltered right now")
    reserved_capacity: int = Field(default=0, ge=0, description="Spaces reserved for in-transit inbound rescuees")
    status: ShelterStatus = Field(default=ShelterStatus.OPEN)

    @property
    def remaining_capacity(self) -> int:
        """Available capacity strictly considering both physically present and reserved spaces."""
        return max(0, self.capacity_people - self.current_occupancy - self.reserved_capacity)

    @property
    def is_available(self) -> bool:
        """True if shelter is open and has at least one unreserved space."""
        return self.status == ShelterStatus.OPEN and self.remaining_capacity > 0

    @model_validator(mode="after")
    def validate_capacity_invariants(self):
        """Invariant: Physically present plus reserved people cannot exceed maximum capacity."""
        if self.current_occupancy + self.reserved_capacity > self.capacity_people:
            raise ValueError(
                f"Shelter {self.shelter_id} overcapacity violation: "
                f"occupancy ({self.current_occupancy}) + reserved ({self.reserved_capacity}) "
                f"> capacity ({self.capacity_people})"
            )
        # Keep status synchronized with available capacity
        if self.remaining_capacity == 0 and self.status == ShelterStatus.OPEN:
            self.status = ShelterStatus.FULL
        elif self.remaining_capacity > 0 and self.status == ShelterStatus.FULL:
            self.status = ShelterStatus.OPEN
        return self
