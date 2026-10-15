"""Boat Agent representing an autonomous rescue boat resource."""

import math
from typing import Optional
from ..models.boat import Boat
from ..models.agent import TaskAnnouncement, BoatBid, ContractAward
from ..models.enums import BoatStatus
from .route_agent import RouteAgent


class BoatAgent:
    """Autonomous agent representing a physical rescue boat."""

    def __init__(self, boat: Boat):
        self.boat = boat

    @property
    def boat_id(self) -> str:
        return self.boat.boat_id

    @property
    def current_zone(self) -> str:
        return self.boat.current_zone

    @property
    def capacity(self) -> int:
        return self.boat.capacity_people

    @property
    def is_available(self) -> bool:
        return self.boat.is_operational and self.boat.status == BoatStatus.AVAILABLE and self.boat.assigned_incident_id is None

    def evaluate_task(
        self,
        announcement: TaskAnnouncement,
        route_agent: RouteAgent,
    ) -> Optional[BoatBid]:
        """
        Evaluate a task announcement based on local capabilities and constraints:
        1. Operational status.
        2. Reachability to incident via open route.
        3. Capacity fit.
        Returns a competitive bid or None if unable to respond.
        """
        if not self.is_available:
            return None

        # Verify open route to incident
        route_to_inc = route_agent.find_route(self.current_zone, announcement.zone)
        if not route_to_inc:
            return None  # Cannot reach incident site

        # Calculate local travel time and cost
        speed_factor = self.boat.speed_units_per_min * self.boat.safety_factor
        travel_time = route_to_inc.total_travel_time_min / speed_factor if speed_factor > 0 else 999.0

        # Capacity matching penalty: slight penalty for overkill (large boat for tiny group)
        offered = min(self.capacity, announcement.people_in_distress)
        capacity_slack = max(0, self.capacity - announcement.people_in_distress)
        capacity_penalty = 0.1 * (capacity_slack / self.capacity)

        # Composite bid cost: lower cost = more attractive bid
        bid_cost = round(travel_time * (1.0 + capacity_penalty), 2)

        return BoatBid(
            bid_id=f"BID-{self.boat_id}-{announcement.announcement_id}",
            announcement_id=announcement.announcement_id,
            incident_id=announcement.incident_id,
            boat_id=self.boat_id,
            current_zone=self.current_zone,
            feasible=True,
            bid_cost=bid_cost,
            offered_capacity=offered,
            route_to_incident=route_to_inc,
            reason=f"Estimated travel time {travel_time:.1f} min from {self.current_zone} with {offered} passenger capacity.",
        )

    def award_contract(self, award: ContractAward) -> None:
        """Lock resources upon winning contract award."""
        self.boat.status = BoatStatus.IN_TRANSIT
        self.boat.assigned_incident_id = award.incident_id
        self.boat.target_shelter_id = award.shelter_id

    def release_contract(self) -> None:
        """Release commitment back to available status."""
        if self.boat.onboard_people == 0 and self.boat.is_operational:
            self.boat.status = BoatStatus.AVAILABLE
            self.boat.assigned_incident_id = None
            self.boat.target_shelter_id = None
            self.boat.planned_route_zones = []
