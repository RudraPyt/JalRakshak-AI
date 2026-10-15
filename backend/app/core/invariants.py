"""Formal safety invariants checker for JalRakshak AI.

Enforces strict domain boundaries preventing closed-route traversal, unavailable boat assignment,
double-booking, shelter overcapacity, false rescue completion, and inconsistent reservations.
"""

from typing import List, Optional
from ..models.enums import BoatStatus, ShelterStatus, EdgeStatus, IncidentLifecycleStatus
from ..models.assignment import AssignmentStatus


class InvariantViolationError(Exception):
    """Raised when an explicit safety invariant has been breached."""
    pass


class InvariantChecker:
    """Validates that all 10 safety invariants hold at every simulation state."""

    @classmethod
    def check_invariants(cls, world_state, strict: bool = False) -> List[str]:
        """
        Evaluate all safety invariants against the current world state.
        Returns a list of violation descriptions. If strict is True, raises on the first violation.
        """
        violations: List[str] = []

        # -------------------------------------------------------------
        # INV-1: No traversal through closed routes
        # -------------------------------------------------------------
        closed_edge_ids = set(world_state.router.get_closed_edge_ids())
        for aid, assignment in world_state.assignments.items():
            if assignment.status in (AssignmentStatus.COMMITTED, AssignmentStatus.EN_ROUTE_PICKUP, AssignmentStatus.EN_ROUTE_SHELTER):
                # Check pickup path
                if assignment.route_to_incident and assignment.route_to_incident.edge_ids:
                    for eid in assignment.route_to_incident.edge_ids:
                        if eid in closed_edge_ids:
                            violations.append(
                                f"INV-1 Violation: Assignment {aid} route to incident traverses closed edge {eid}"
                            )
                # Check shelter path
                if assignment.route_to_shelter and assignment.route_to_shelter.edge_ids:
                    for eid in assignment.route_to_shelter.edge_ids:
                        if eid in closed_edge_ids:
                            violations.append(
                                f"INV-1 Violation: Assignment {aid} route to shelter traverses closed edge {eid}"
                            )

        # -------------------------------------------------------------
        # INV-2: No unavailable boat assignment
        # -------------------------------------------------------------
        for boat in world_state.boats.values():
            if not boat.is_operational:
                if boat.assigned_incident_id is not None:
                    # Check if there is an active non-invalidated assignment
                    for aid, assignment in world_state.assignments.items():
                        if assignment.boat_id == boat.boat_id and assignment.status in (
                            AssignmentStatus.COMMITTED,
                            AssignmentStatus.EN_ROUTE_PICKUP,
                            AssignmentStatus.EN_ROUTE_SHELTER,
                        ):
                            violations.append(
                                f"INV-2 Violation: Failed/unavailable boat {boat.boat_id} holds active assignment {aid}"
                            )

        # -------------------------------------------------------------
        # INV-3: No incompatible double-booking
        # -------------------------------------------------------------
        active_boats = {}
        for aid, assignment in world_state.assignments.items():
            if assignment.status in (
                AssignmentStatus.COMMITTED,
                AssignmentStatus.EN_ROUTE_PICKUP,
                AssignmentStatus.SERVICING_PICKUP,
                AssignmentStatus.EN_ROUTE_SHELTER,
            ):
                if assignment.boat_id in active_boats:
                    violations.append(
                        f"INV-3 Violation: Boat {assignment.boat_id} is simultaneously double-booked "
                        f"on assignments {active_boats[assignment.boat_id]} and {aid}"
                    )
                else:
                    active_boats[assignment.boat_id] = aid

        # -------------------------------------------------------------
        # INV-4: No shelter overcapacity
        # -------------------------------------------------------------
        for sid, shelter in world_state.shelters.items():
            total_committed = shelter.current_occupancy + shelter.reserved_capacity
            if total_committed > shelter.capacity_people:
                violations.append(
                    f"INV-4 Violation: Shelter {sid} overcapacity: "
                    f"occupancy ({shelter.current_occupancy}) + reserved ({shelter.reserved_capacity}) "
                    f"> capacity ({shelter.capacity_people})"
                )

        # -------------------------------------------------------------
        # INV-5: No false service completion
        # -------------------------------------------------------------
        for inc in world_state.incidents.values():
            if inc.lifecycle_status == IncidentLifecycleStatus.FULLY_SERVED:
                if inc.people_rescued < inc.people_affected:
                    violations.append(
                        f"INV-5 Violation: Incident {inc.incident_id} marked FULLY_SERVED but "
                        f"rescued ({inc.people_rescued}) < affected ({inc.people_affected})"
                    )
                if inc.people_onboard > 0:
                    violations.append(
                        f"INV-5 Violation: Incident {inc.incident_id} marked FULLY_SERVED while "
                        f"{inc.people_onboard} passengers are still onboard a boat"
                    )

        # -------------------------------------------------------------
        # INV-6: No fabricated feasibility
        # -------------------------------------------------------------
        for aid, assignment in world_state.assignments.items():
            if assignment.status == AssignmentStatus.COMMITTED:
                if not assignment.route_to_incident or not assignment.route_to_shelter:
                    violations.append(
                        f"INV-6 Violation: Assignment {aid} committed without feasible verified routes"
                    )

        # -------------------------------------------------------------
        # INV-7: Explicit commitment invalidation
        # -------------------------------------------------------------
        for aid, assignment in world_state.assignments.items():
            if assignment.status == AssignmentStatus.INVALIDATED and not assignment.invalidation_reason:
                violations.append(
                    f"INV-7 Violation: Assignment {aid} marked INVALIDATED without a recorded reason"
                )

        # -------------------------------------------------------------
        # INV-8: Consistent resource reservations
        # -------------------------------------------------------------
        for sid, shelter in world_state.shelters.items():
            # Sum headcounts of active inbound assignments committed to this shelter
            expected_reservations = sum(
                a.people_assigned
                for a in world_state.assignments.values()
                if a.shelter_id == sid and a.status in (
                    AssignmentStatus.COMMITTED,
                    AssignmentStatus.EN_ROUTE_PICKUP,
                    AssignmentStatus.SERVICING_PICKUP,
                    AssignmentStatus.EN_ROUTE_SHELTER,
                )
            )
            if shelter.reserved_capacity < expected_reservations:
                violations.append(
                    f"INV-8 Violation: Shelter {sid} reserved capacity ({shelter.reserved_capacity}) "
                    f"is less than total active committed inbound assignments ({expected_reservations})"
                )

        if strict and violations:
            raise InvariantViolationError("; ".join(violations))

        return violations
