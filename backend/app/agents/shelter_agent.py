"""Shelter Agent managing evacuation facility capacity and reservations."""

from typing import Optional
from ..models.shelter import Shelter
from ..models.agent import ShelterBidResponse
from ..models.enums import ShelterStatus
from .route_agent import RouteAgent


class ShelterAgent:
    """Autonomous agent managing capacity and reservations for an evacuation shelter."""

    def __init__(self, shelter: Shelter):
        self.shelter = shelter

    @property
    def shelter_id(self) -> str:
        return self.shelter.shelter_id

    @property
    def zone_id(self) -> str:
        return self.shelter.zone_id

    @property
    def remaining_capacity(self) -> int:
        return self.shelter.remaining_capacity

    @property
    def is_available(self) -> bool:
        return self.shelter.status == ShelterStatus.OPEN and self.remaining_capacity > 0

    def evaluate_capacity_request(
        self,
        incident_id: str,
        incident_zone: str,
        requested_spaces: int,
        route_agent: RouteAgent,
    ) -> ShelterBidResponse:
        """
        Evaluate a request for emergency shelter spaces:
        1. Checks current remaining capacity buffer.
        2. Verifies open, safe route from incident zone to shelter.
        Returns a granted or declined response with explanation.
        """
        if not self.is_available or self.remaining_capacity <= 0:
            return ShelterBidResponse(
                shelter_id=self.shelter_id,
                incident_id=incident_id,
                requested_spaces=requested_spaces,
                granted=False,
                granted_spaces=0,
                reason=f"Shelter {self.shelter_id} has zero remaining capacity (0/{self.shelter.capacity_people} available)",
            )

        # Check route feasibility from incident zone to shelter
        route_to_shelter = route_agent.find_route(incident_zone, self.zone_id)
        if not route_to_shelter:
            return ShelterBidResponse(
                shelter_id=self.shelter_id,
                incident_id=incident_id,
                requested_spaces=requested_spaces,
                granted=False,
                granted_spaces=0,
                reason=f"No accessible open route from incident zone '{incident_zone}' to shelter zone '{self.zone_id}'",
            )

        grantable = min(requested_spaces, self.remaining_capacity)
        return ShelterBidResponse(
            shelter_id=self.shelter_id,
            incident_id=incident_id,
            requested_spaces=requested_spaces,
            granted=True,
            granted_spaces=grantable,
            route_to_shelter=route_to_shelter,
            reason=f"Granted {grantable} spaces at {self.shelter.name} (remaining: {self.remaining_capacity - grantable})",
        )

    def reserve(self, count: int) -> None:
        """Commit a reservation for incoming passengers."""
        if count > self.remaining_capacity:
            raise ValueError(f"Cannot reserve {count} spaces: exceeds remaining capacity {self.remaining_capacity}")
        self.shelter.reserved_capacity += count

    def release_reservation(self, count: int) -> None:
        """Release a reservation if a contract is invalidated or cancelled."""
        self.shelter.reserved_capacity = max(0, self.shelter.reserved_capacity - count)

    def receive_arrival(self, count: int) -> None:
        """Process physical arrival of rescuees into the shelter."""
        self.shelter.current_occupancy += count
        self.shelter.reserved_capacity = max(0, self.shelter.reserved_capacity - count)
