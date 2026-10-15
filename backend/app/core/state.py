"""Authoritative World State manager for JalRakshak AI.

Maintains the authoritative ground truth for all entities (zones, edges, boats, shelters,
incidents, events, commitments), advances the discrete simulation clock, executes the 7-step
simulation event loop, enforces real-time capacity reservations, and executes dynamic events.
"""

import math
from typing import Dict, List, Optional, Tuple, Any
from ..models.enums import (
    BoatStatus,
    ShelterStatus,
    EdgeStatus,
    EventType,
    ActionType,
    IncidentLifecycleStatus,
    VerificationStatus,
)
from ..models.graph import ZoneNode, NetworkEdge, RoutePath
from ..models.boat import Boat
from ..models.shelter import Shelter
from ..models.incident import Incident
from ..models.event import ScenarioEvent
from ..models.assignment import Assignment, AssignmentStatus
from .data_loader import DataLoader
from .router import NetworkRouter
from .clock import SimulationClock
from .logger import ExplainableLogger
from .invariants import InvariantChecker, InvariantViolationError


class WorldState:
    """The authoritative simulation world state."""

    def __init__(self, data_loader: Optional[DataLoader] = None, dispatcher=None):
        self.data_loader = data_loader or DataLoader()
        self.clock = SimulationClock()
        self.logger = ExplainableLogger()
        self.dispatcher = dispatcher

        self.zones: Dict[str, ZoneNode] = {}
        self.edges: Dict[str, NetworkEdge] = {}
        self.boats: Dict[str, Boat] = {}
        self.shelters: Dict[str, Shelter] = {}
        self.incidents: Dict[str, Incident] = {}
        self.events: List[ScenarioEvent] = []
        self.assignments: Dict[str, Assignment] = {}

        self.router: NetworkRouter = None  # type: ignore
        self.reset_to_initial_conditions()

    def reset_to_initial_conditions(self) -> None:
        """Reset all simulation components back to the initial dataset conditions."""
        self.clock.reset()
        self.logger.clear()
        self.assignments.clear()

        zones, edges, boats, shelters, incidents, events = self.data_loader.load_all()
        self.zones = zones
        self.edges = {e.edge_id: e for e in edges}
        self.boats = {b.boat_id: b for b in boats}
        self.shelters = {s.shelter_id: s for s in shelters}
        self.incidents = {i.incident_id: i for i in incidents}
        self.events = events

        # Initialize routing engine
        self.router = NetworkRouter(edges)

        # Preserve dispatcher configured on the state instance

        self.logger.log(
            timestamp_min=0,
            action_type=ActionType.PROPOSAL,
            entity_id="SYSTEM",
            rule_applied="INITIAL_SETUP",
            explanation="Simulation initialized with 11 zones, 12 edges, 4 boats, 4 shelters, 12 incidents.",
        )

    def get_pending_incidents(self) -> List[Incident]:
        """Return incidents awaiting rescue dispatch."""
        return [
            inc for inc in self.incidents.values()
            if inc.lifecycle_status in (
                IncidentLifecycleStatus.PENDING_ASSIGNMENT,
                IncidentLifecycleStatus.PARTIALLY_SERVED,
            ) and inc.people_awaiting_pickup > 0
        ]

    def get_available_boats(self) -> List[Boat]:
        """Return operational boats ready for assignment."""
        return [
            b for b in self.boats.values()
            if b.status == BoatStatus.AVAILABLE and b.is_operational
        ]

    def get_available_shelters(self, required_spaces: int = 1) -> List[Shelter]:
        """Return shelters with sufficient remaining capacity."""
        return [
            s for s in self.shelters.values()
            if s.is_available and s.remaining_capacity >= required_spaces
        ]

    def create_assignment(
        self,
        incident_id: str,
        boat_id: str,
        shelter_id: str,
        people_count: int,
        rationale: str = "Standard dispatch commitment",
    ) -> Assignment:
        """
        Create and commit a verified rescue contract adhering to capacity and route invariants.
        """
        incident = self.incidents.get(incident_id)
        boat = self.boats.get(boat_id)
        shelter = self.shelters.get(shelter_id)

        if not incident or not boat or not shelter:
            raise ValueError(f"Cannot commit assignment: invalid entity references ({incident_id}, {boat_id}, {shelter_id})")

        if not boat.is_operational or boat.status != BoatStatus.AVAILABLE:
            raise ValueError(f"Cannot assign boat {boat_id}: status is {boat.status}")

        if people_count > boat.capacity_people:
            raise ValueError(f"Cannot assign {people_count} passengers: exceeds boat {boat_id} capacity ({boat.capacity_people})")

        if people_count > shelter.remaining_capacity:
            raise ValueError(
                f"Cannot assign to shelter {shelter_id}: requires {people_count} but only {shelter.remaining_capacity} remaining"
            )

        # Plan verified paths
        route_to_inc = self.router.find_shortest_path(boat.current_zone, incident.zone)
        if not route_to_inc:
            raise ValueError(f"No feasible open route from boat {boat_id} ({boat.current_zone}) to incident ({incident.zone})")

        route_to_shelter = self.router.find_shortest_path(incident.zone, shelter.zone_id)
        if not route_to_shelter:
            raise ValueError(f"No feasible open route from incident ({incident.zone}) to shelter ({shelter.zone_id})")

        # Reserve shelter capacity
        shelter.reserved_capacity += people_count

        # Commit boat and incident state
        boat.status = BoatStatus.IN_TRANSIT
        boat.assigned_incident_id = incident_id
        boat.target_shelter_id = shelter_id
        boat.planned_route_zones = route_to_inc.zones + route_to_shelter.zones[1:]

        incident.lifecycle_status = IncidentLifecycleStatus.ASSIGNED
        incident.assigned_boat_id = boat_id
        incident.assigned_shelter_id = shelter_id

        # Calculate discrete leg travel times (in minutes)
        b_speed = boat.speed_units_per_min * boat.safety_factor
        pickup_duration = math.ceil(route_to_inc.total_travel_time_min / b_speed) if b_speed > 0 else 1
        shelter_duration = math.ceil(route_to_shelter.total_travel_time_min / b_speed) if b_speed > 0 else 1

        aid = f"ASG-{incident_id}-{boat_id}-{self.clock.current_minute}"
        assignment = Assignment(
            assignment_id=aid,
            incident_id=incident_id,
            boat_id=boat_id,
            shelter_id=shelter_id,
            people_assigned=people_count,
            route_to_incident=route_to_inc,
            route_to_shelter=route_to_shelter,
            status=AssignmentStatus.COMMITTED,
            pickup_travel_duration=pickup_duration,
            shelter_travel_duration=shelter_duration,
            minutes_in_leg=0,
            current_leg="to_incident",
            created_at_minute=self.clock.current_minute,
            rationale=rationale,
        )
        self.assignments[aid] = assignment

        self.logger.log(
            timestamp_min=self.clock.current_minute,
            action_type=ActionType.COMMITTED,
            entity_id=boat_id,
            target_id=incident_id,
            rule_applied="DISPATCH_COMMITMENT",
            explanation=f"Committed {boat_id} to rescue {people_count} people from {incident_id} to shelter {shelter_id}. {rationale}",
            previous_state=BoatStatus.AVAILABLE.value,
            new_state=BoatStatus.IN_TRANSIT.value,
        )

        return assignment

    def invalidate_assignment(self, assignment_id: str, reason: str) -> None:
        """
        Explicitly invalidate an active commitment when environment or resource changes make it infeasible.
        Enforces clean rollback of shelter reservations and boat status.
        """
        assignment = self.assignments.get(assignment_id)
        if not assignment:
            return

        assignment.status = AssignmentStatus.INVALIDATED
        assignment.invalidation_reason = reason
        assignment.current_leg = "invalidated"

        # Rollback shelter reservation
        shelter = self.shelters.get(assignment.shelter_id)
        if shelter:
            shelter.reserved_capacity = max(0, shelter.reserved_capacity - assignment.people_assigned)

        # Release boat if operational and empty
        boat = self.boats.get(assignment.boat_id)
        if boat:
            if boat.onboard_people == 0 and boat.is_operational:
                boat.status = BoatStatus.AVAILABLE
                boat.assigned_incident_id = None
                boat.target_shelter_id = None
                boat.planned_route_zones = []

        # Reset incident to pending re-evaluation if not yet picked up
        incident = self.incidents.get(assignment.incident_id)
        if incident and incident.people_onboard == 0:
            incident.lifecycle_status = IncidentLifecycleStatus.PENDING_ASSIGNMENT
            incident.assigned_boat_id = None
            incident.assigned_shelter_id = None
            incident.status_explanation = f"Commitment invalidated: {reason}"

        self.logger.log(
            timestamp_min=self.clock.current_minute,
            action_type=ActionType.INVALIDATED,
            entity_id=assignment.boat_id,
            target_id=assignment.incident_id,
            rule_applied="SAFETY_INVARIANT_7",
            explanation=f"Assignment {assignment_id} invalidated: {reason}",
            previous_state=AssignmentStatus.COMMITTED.value,
            new_state=AssignmentStatus.INVALIDATED.value,
        )

    def load_passengers(self, boat_id: str, incident_id: str, count: int) -> None:
        """
        Load stranded passengers onto a boat at the incident zone.
        Strict invariant: Pickup alone is NEVER counted as delivered rescue!
        """
        boat = self.boats.get(boat_id)
        incident = self.incidents.get(incident_id)

        if not boat or not incident:
            raise ValueError(f"Invalid boat or incident ID ({boat_id}, {incident_id})")

        if not boat.is_operational:
            raise ValueError(f"Boat {boat_id} is failed or unavailable")

        if count > boat.remaining_carrying_capacity:
            raise ValueError(f"Load count ({count}) exceeds boat {boat_id} remaining capacity ({boat.remaining_carrying_capacity})")

        if count > incident.people_awaiting_pickup:
            raise ValueError(f"Load count ({count}) exceeds people awaiting pickup ({incident.people_awaiting_pickup})")

        boat.onboard_people += count
        boat.status = BoatStatus.SERVICING
        incident.people_onboard += count
        incident.lifecycle_status = IncidentLifecycleStatus.IN_TRANSIT

        self.logger.log(
            timestamp_min=self.clock.current_minute,
            action_type=ActionType.PASSENGERS_LOADED,
            entity_id=boat_id,
            target_id=incident_id,
            rule_applied="PASSENGER_EXTRACTION",
            explanation=f"Boat {boat_id} loaded {count} passengers from incident {incident_id}. (Awaiting shelter transport).",
        )

    def deliver_passengers(self, boat_id: str, shelter_id: str, count: int) -> None:
        """
        Safely unload passengers at destination shelter.
        This is the ONLY transition where people_rescued increments and incident can reach FULLY_SERVED.
        """
        boat = self.boats.get(boat_id)
        shelter = self.shelters.get(shelter_id)

        if not boat or not shelter:
            raise ValueError(f"Invalid boat or shelter ID ({boat_id}, {shelter_id})")

        if count > boat.onboard_people:
            raise ValueError(f"Delivery count ({count}) exceeds passengers onboard boat {boat_id} ({boat.onboard_people})")

        if shelter.current_occupancy + count > shelter.capacity_people:
            raise ValueError(f"Delivery of {count} people would exceed shelter {shelter_id} capacity ({shelter.capacity_people})")

        # Update boat & shelter
        boat.onboard_people -= count
        shelter.current_occupancy += count
        shelter.reserved_capacity = max(0, shelter.reserved_capacity - count)

        # Update associated incident
        if boat.assigned_incident_id:
            incident = self.incidents.get(boat.assigned_incident_id)
            if incident:
                incident.people_onboard = max(0, incident.people_onboard - count)
                incident.people_rescued += count

                if incident.people_rescued >= incident.people_affected:
                    incident.lifecycle_status = IncidentLifecycleStatus.FULLY_SERVED
                    incident.served_at_minute = self.clock.current_minute
                    incident.assigned_boat_id = None
                    incident.assigned_shelter_id = None
                    incident.status_explanation = f"All {incident.people_affected} rescued individuals delivered to shelter {shelter_id}"
                    self.logger.log(
                        timestamp_min=self.clock.current_minute,
                        action_type=ActionType.SERVED,
                        entity_id=incident.incident_id,
                        target_id=shelter_id,
                        rule_applied="FULL_SERVICE_COMPLETION",
                        explanation=f"Incident {incident.incident_id} is FULLY_SERVED at minute {self.clock.current_minute}.",
                    )
                else:
                    incident.lifecycle_status = IncidentLifecycleStatus.PARTIALLY_SERVED
                    incident.assigned_boat_id = None
                    incident.status_explanation = (
                        f"Delivered {incident.people_rescued}/{incident.people_affected} to shelter {shelter_id}. "
                        f"{incident.people_awaiting_pickup} awaiting next extraction trip."
                    )

        # Release boat if empty
        if boat.onboard_people == 0:
            boat.status = BoatStatus.AVAILABLE
            boat.assigned_incident_id = None
            boat.target_shelter_id = None
            boat.planned_route_zones = []

        self.logger.log(
            timestamp_min=self.clock.current_minute,
            action_type=ActionType.PASSENGERS_DELIVERED,
            entity_id=boat_id,
            target_id=shelter_id,
            rule_applied="SHELTER_DELIVERY",
            explanation=f"Boat {boat_id} safely delivered {count} individuals to shelter {shelter_id}.",
        )

    def apply_event(self, event: ScenarioEvent) -> None:
        """
        Execute an environmental event, updating components and invalidating compromised commitments.
        """
        event.applied = True

        if event.event_type == EventType.ROAD_CLOSURE:
            self.router.close_edge(event.target_id, reason=event.description)
            # Find and invalidate any active assignment whose route used this edge
            affected = []
            for aid, assignment in self.assignments.items():
                if assignment.status in (
                    AssignmentStatus.COMMITTED,
                    AssignmentStatus.EN_ROUTE_PICKUP,
                    AssignmentStatus.SERVICING_PICKUP,
                    AssignmentStatus.EN_ROUTE_SHELTER,
                ):
                    traversed = []
                    if assignment.route_to_incident:
                        traversed.extend(assignment.route_to_incident.edge_ids)
                    if assignment.route_to_shelter:
                        traversed.extend(assignment.route_to_shelter.edge_ids)
                    if event.target_id in traversed:
                        affected.append(aid)

            for aid in affected:
                self.invalidate_assignment(aid, reason=f"Traversed edge {event.target_id} closed ({event.description})")

            self.logger.log(
                timestamp_min=self.clock.current_minute,
                action_type=ActionType.INVALIDATED,
                entity_id=event.target_id,
                rule_applied="ROAD_CLOSURE_EVENT",
                explanation=f"Edge {event.target_id} closed: {event.description}. Invalidated {len(affected)} assignments.",
            )

        elif event.event_type == EventType.BOAT_FAILURE:
            boat = self.boats.get(event.target_id)
            if boat:
                boat.status = BoatStatus.FAILED
                boat.failure_reason = event.description
                boat.failed_until_minute = self.clock.current_minute + 10  # 10 minute failure from EV002

                # Invalidate boat's active assignment
                for aid, assignment in list(self.assignments.items()):
                    if assignment.boat_id == boat.boat_id and assignment.status in (
                        AssignmentStatus.COMMITTED,
                        AssignmentStatus.EN_ROUTE_PICKUP,
                        AssignmentStatus.SERVICING_PICKUP,
                        AssignmentStatus.EN_ROUTE_SHELTER,
                    ):
                        self.invalidate_assignment(aid, reason=f"Assigned boat {boat.boat_id} failed ({event.description})")

                self.logger.log(
                    timestamp_min=self.clock.current_minute,
                    action_type=ActionType.FAILED,
                    entity_id=boat.boat_id,
                    rule_applied="BOAT_FAILURE_EVENT",
                    explanation=f"Boat {boat.boat_id} failed: {event.description}.",
                )

        elif event.event_type == EventType.SHELTER_OVERFLOW:
            shelter = self.shelters.get(event.target_id)
            if shelter:
                # Force occupancy to capacity so remaining capacity drops to 0
                shelter.current_occupancy = shelter.capacity_people
                shelter.status = ShelterStatus.FULL

                # Invalidate any pending inbound assignments that were relying on this shelter
                affected = []
                for aid, assignment in self.assignments.items():
                    if assignment.shelter_id == shelter.shelter_id and assignment.status in (
                        AssignmentStatus.COMMITTED,
                        AssignmentStatus.EN_ROUTE_PICKUP,
                    ):
                        affected.append(aid)

                for aid in affected:
                    self.invalidate_assignment(aid, reason=f"Destination shelter {shelter.shelter_id} reached capacity overflow")

                self.logger.log(
                    timestamp_min=self.clock.current_minute,
                    action_type=ActionType.INVALIDATED,
                    entity_id=shelter.shelter_id,
                    rule_applied="SHELTER_OVERFLOW_EVENT",
                    explanation=f"Shelter {shelter.shelter_id} overflow: {event.description}. Invalidated {len(affected)} inbound commitments.",
                )

        elif event.event_type == EventType.ROAD_REOPEN:
            self.router.reopen_edge(event.target_id)
            self.logger.log(
                timestamp_min=self.clock.current_minute,
                action_type=ActionType.REROUTED,
                entity_id=event.target_id,
                rule_applied="ROAD_REOPEN_EVENT",
                explanation=f"Edge {event.target_id} reopened: {event.description}.",
            )

        elif event.event_type == EventType.CONFLICTING_REPORT:
            incident = self.incidents.get(event.target_id)
            if incident:
                incident.verification_status = VerificationStatus.POSSIBLE_DUPLICATE
                incident.status_explanation = f"Conflicting information received: {event.description}"
                self.logger.log(
                    timestamp_min=self.clock.current_minute,
                    action_type=ActionType.PROPOSAL,
                    entity_id=incident.incident_id,
                    rule_applied="UNCERTAINTY_CONFLICT_EVENT",
                    explanation=f"Conflicting report for {incident.incident_id}: {event.description}",
                )

    def step(self) -> int:
        """
        Execute the rigorous 7-step discrete simulation event loop:
        1. Advance the simulation clock.
        2. Ingest and apply scheduled scenario events.
        3. Validate active commitments and detect newly infeasible routes/resources.
        4. Reconcile reservations and roll back invalidated contracts.
        5. Replan using the configured dispatcher (Centralized Baseline or MAS).
        6. Advance movements, process pickups at incidents, and deliveries at shelters.
        7. Record audit logs, update resource metrics, and evaluate safety invariants.
        """
        # Step 1: Advance simulation clock
        t = self.clock.tick()

        # Step 2: Apply scheduled scenario events for current minute
        for event in self.events:
            if not event.applied and event.simulation_minute == t:
                self.apply_event(event)

        # Check boat maintenance / recovery timer
        for boat in self.boats.values():
            if boat.status == BoatStatus.FAILED and boat.failed_until_minute is not None:
                if t >= boat.failed_until_minute:
                    boat.status = BoatStatus.AVAILABLE
                    boat.failure_reason = None
                    boat.failed_until_minute = None
                    self.logger.log(
                        timestamp_min=t,
                        action_type=ActionType.COMMITTED,
                        entity_id=boat.boat_id,
                        rule_applied="BOAT_RECOVERY",
                        explanation=f"Boat {boat.boat_id} repairs complete; restored to operational availability.",
                    )

        # Step 3 & 4: Invalidate any active commitments compromised by current state
        for aid, asg in list(self.assignments.items()):
            if asg.status in (
                AssignmentStatus.COMMITTED,
                AssignmentStatus.EN_ROUTE_PICKUP,
                AssignmentStatus.EN_ROUTE_SHELTER,
            ):
                boat = self.boats.get(asg.boat_id)
                if not boat or not boat.is_operational:
                    self.invalidate_assignment(aid, reason=f"Assigned boat {asg.boat_id} is unavailable")
                    continue

                if asg.current_leg == "to_incident" and asg.route_to_incident:
                    if not self.router.is_route_valid(asg.route_to_incident):
                        self.invalidate_assignment(aid, reason="Pickup route contains closed edges")
                        continue

                if asg.current_leg == "to_shelter" and asg.route_to_shelter:
                    if not self.router.is_route_valid(asg.route_to_shelter):
                        self.invalidate_assignment(aid, reason="Shelter route contains closed edges")
                        continue

        # Step 5: Replan using the active dispatcher
        if self.dispatcher:
            self.dispatcher.dispatch(self)

        # Step 6: Advance movement, process passenger pickups and shelter deliveries
        for aid, asg in list(self.assignments.items()):
            if asg.status in (
                AssignmentStatus.COMMITTED,
                AssignmentStatus.EN_ROUTE_PICKUP,
                AssignmentStatus.SERVICING_PICKUP,
                AssignmentStatus.EN_ROUTE_SHELTER,
            ):
                boat = self.boats.get(asg.boat_id)
                inc = self.incidents.get(asg.incident_id)
                shelter = self.shelters.get(asg.shelter_id)

                if not boat or not inc or not shelter or not boat.is_operational:
                    continue

                if asg.status == AssignmentStatus.COMMITTED:
                    asg.status = AssignmentStatus.EN_ROUTE_PICKUP

                # Leg 1: En route to incident for pickup
                if asg.current_leg == "to_incident":
                    asg.minutes_in_leg += 1
                    # Check arrival at incident
                    if asg.minutes_in_leg >= asg.pickup_travel_duration:
                        boat.current_zone = inc.zone
                        # Process passenger boarding
                        if inc.people_awaiting_pickup > 0 and boat.remaining_carrying_capacity > 0:
                            actual_load = min(asg.people_assigned, inc.people_awaiting_pickup, boat.remaining_carrying_capacity)
                            self.load_passengers(boat.boat_id, inc.incident_id, actual_load)
                        asg.current_leg = "to_shelter"
                        asg.minutes_in_leg = 0
                        asg.status = AssignmentStatus.EN_ROUTE_SHELTER

                # Leg 2: En route from incident to shelter for delivery
                elif asg.current_leg == "to_shelter":
                    asg.minutes_in_leg += 1
                    # Check arrival at destination shelter
                    if asg.minutes_in_leg >= asg.shelter_travel_duration:
                        boat.current_zone = shelter.zone_id
                        # Process passenger disembarkation
                        if boat.onboard_people > 0:
                            actual_deliver = min(asg.people_assigned, boat.onboard_people)
                            self.deliver_passengers(boat.boat_id, shelter.shelter_id, actual_deliver)
                        asg.current_leg = "delivered"
                        asg.status = AssignmentStatus.DELIVERED
                        asg.completed_at_minute = t

        # Step 7: Update operational metrics and audit invariants
        for boat in self.boats.values():
            if boat.is_operational:
                if boat.status == BoatStatus.AVAILABLE:
                    boat.total_idle_minutes += 1
                else:
                    boat.total_service_minutes += 1

        # Check invariants at every step
        InvariantChecker.check_invariants(self, strict=False)

        return t
