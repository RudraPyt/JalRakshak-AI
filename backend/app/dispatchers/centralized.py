"""Centralized Greedy Baseline Dispatcher for JalRakshak AI.

Implements an omniscient, deterministic centralized dispatcher that orders incidents
by composite urgency and starvation-preventing waiting time, evaluates feasible boat
and shelter combinations under strict capacity and safety constraints, and commits
transparent assignments.
"""

import math
from typing import Dict, List, Optional, Tuple
from .base import BaseDispatcher
from ..models.assignment import Assignment, AssignmentStatus
from ..models.incident import Incident
from ..models.boat import Boat
from ..models.shelter import Shelter
from ..models.enums import (
    UrgencyLevel,
    VerificationStatus,
    IncidentLifecycleStatus,
    BoatStatus,
    ActionType,
)


class CentralizedGreedyDispatcher(BaseDispatcher):
    """
    Centralized baseline dispatcher with starvation prevention, capacity enforcement,
    and explainable selection/rejection logging.
    """

    def __init__(self, waiting_weight: float = 1.5, max_waiting_bonus: float = 50.0):
        self.waiting_weight = waiting_weight
        self.max_waiting_bonus = max_waiting_bonus

    @property
    def name(self) -> str:
        return "Centralized Greedy Baseline"

    def compute_priority_score(self, incident: Incident, current_minute: int) -> float:
        """
        Calculate composite priority score:
        Score = (Base Urgency + Waiting Time Bonus) * Source Confidence * Verification Factor
        """
        base_urgency = incident.reported_urgency.priority_weight

        # Waiting time bonus: incorporates initial report age + simulation minutes elapsed
        elapsed_min = incident.report_age_min + max(0, current_minute - incident.reported_at_minute)
        waiting_bonus = min(self.max_waiting_bonus, self.waiting_weight * elapsed_min)

        # Verification factor
        verification_factors = {
            VerificationStatus.VERIFIED: 1.0,
            VerificationStatus.REPORTED: 0.90,
            VerificationStatus.POSSIBLE_DUPLICATE: 0.70,
            VerificationStatus.UNVERIFIED: 0.60,
            VerificationStatus.DUPLICATE_RESOLVED: 0.50,
        }
        ver_factor = verification_factors.get(incident.verification_status, 0.80)

        # Composite score
        priority = (base_urgency + waiting_bonus) * incident.source_confidence * ver_factor
        return round(priority, 2)

    def dispatch(self, world_state) -> List[Assignment]:
        """
        Execute centralized greedy dispatch:
        1. Identify pending incidents with stranded individuals.
        2. Rank incidents by composite priority score.
        3. Match available boats and shelters.
        4. Commit valid assignments or log explicit rejection reasons.
        """
        # Step 1: Collect eligible incidents awaiting rescue
        eligible_incidents = [
            inc for inc in world_state.incidents.values()
            if inc.people_awaiting_pickup > 0
            and inc.lifecycle_status not in (
                IncidentLifecycleStatus.FULLY_SERVED,
                IncidentLifecycleStatus.CANCELLED,
            )
            # Cannot be currently assigned to a boat that is actively en route
            and inc.assigned_boat_id is None
        ]

        if not eligible_incidents:
            return []

        # Step 2: Sort incidents by Priority Score descending (deterministic tie-break by incident_id)
        current_minute = world_state.clock.current_minute
        ranked_incidents = sorted(
            eligible_incidents,
            key=lambda inc: (
                self.compute_priority_score(inc, current_minute),
                -inc.people_awaiting_pickup,
                inc.incident_id,
            ),
            reverse=True,
        )

        committed_assignments: List[Assignment] = []

        # Step 3: Iterate through prioritized incidents
        for inc in ranked_incidents:
            p_score = self.compute_priority_score(inc, current_minute)

            # Available operational boats
            available_boats = world_state.get_available_boats()
            if not available_boats:
                world_state.logger.log(
                    timestamp_min=current_minute,
                    action_type=ActionType.BID_REJECTED,
                    entity_id=inc.incident_id,
                    rule_applied="RESOURCE_UNAVAILABLE",
                    explanation=f"Incident {inc.incident_id} (priority {p_score}) deferred: all rescue boats currently deployed or failed.",
                )
                break  # No boats remaining for lower priority requests either

            # Open shelters with capacity
            available_shelters = [
                s for s in world_state.shelters.values()
                if s.is_available and s.remaining_capacity > 0
            ]
            if not available_shelters:
                inc.lifecycle_status = IncidentLifecycleStatus.UNMET_SHELTER_BOTTLENECK
                inc.status_explanation = "Regional shelter capacity exhausted (0 spaces remaining)."
                world_state.logger.log(
                    timestamp_min=current_minute,
                    action_type=ActionType.BID_REJECTED,
                    entity_id=inc.incident_id,
                    rule_applied="SHELTER_CAPACITY_BOTTLENECK",
                    explanation=f"Incident {inc.incident_id} cannot be assigned: total regional shelter capacity exhausted.",
                )
                continue

            # Evaluate candidate (boat, shelter) pairs
            best_candidate = None
            best_utility = float("-inf")
            rejection_reasons = []

            for boat in available_boats:
                # Path 1: Boat to incident
                route_b_to_inc = world_state.router.find_shortest_path(boat.current_zone, inc.zone)
                if not route_b_to_inc:
                    rejection_reasons.append(f"Boat {boat.boat_id} has no open route to {inc.zone}")
                    continue

                for shelter in available_shelters:
                    # Path 2: Incident to shelter
                    route_inc_to_s = world_state.router.find_shortest_path(inc.zone, shelter.zone_id)
                    if not route_inc_to_s:
                        rejection_reasons.append(f"No open route from {inc.zone} to shelter {shelter.shelter_id}")
                        continue

                    # Feasible headcount for this trip
                    headcount = min(
                        boat.capacity_people,
                        inc.people_awaiting_pickup,
                        shelter.remaining_capacity,
                    )
                    if headcount <= 0:
                        continue

                    # Travel durations (in minutes)
                    b_speed = boat.speed_units_per_min * boat.safety_factor
                    time_to_inc = route_b_to_inc.total_travel_time_min / b_speed if b_speed > 0 else 999.0
                    time_to_s = route_inc_to_s.total_travel_time_min / b_speed if b_speed > 0 else 999.0
                    total_time = time_to_inc + time_to_s

                    # Greedy utility: prioritize urgency and headcounts, penalize total travel time
                    utility = (p_score * headcount) - (1.5 * total_time)

                    if utility > best_utility:
                        best_utility = utility
                        best_candidate = {
                            "boat": boat,
                            "shelter": shelter,
                            "headcount": headcount,
                            "route_to_inc": route_b_to_inc,
                            "route_to_s": route_inc_to_s,
                            "time_to_inc": math.ceil(time_to_inc),
                            "time_to_s": math.ceil(time_to_s),
                            "total_time": round(total_time, 2),
                        }

            # Step 4: Commit best candidate if found
            if best_candidate:
                b = best_candidate["boat"]
                s = best_candidate["shelter"]
                count = best_candidate["headcount"]

                rationale = (
                    f"Selected highest-utility pair: Boat {b.boat_id} (cap {b.capacity_people}) "
                    f"and Shelter {s.shelter_id} ({s.remaining_capacity} remaining). "
                    f"Priority score: {p_score}, planned extraction: {count}/{inc.people_awaiting_pickup} people, "
                    f"est. travel time: {best_candidate['total_time']} min."
                )

                # Create commitment in WorldState
                asg = world_state.create_assignment(
                    incident_id=inc.incident_id,
                    boat_id=b.boat_id,
                    shelter_id=s.shelter_id,
                    people_count=count,
                    rationale=rationale,
                )

                # Populate leg durations for discrete simulation execution
                asg.pickup_travel_duration = best_candidate["time_to_inc"]
                asg.shelter_travel_duration = best_candidate["time_to_s"]
                asg.minutes_in_leg = 0
                asg.current_leg = "to_incident"
                asg.status = AssignmentStatus.EN_ROUTE_PICKUP

                committed_assignments.append(asg)
            else:
                # Log why this incident could not be dispatched
                reason_summary = "; ".join(rejection_reasons[:3]) if rejection_reasons else "No viable boat-shelter combination"
                if "no open route" in reason_summary.lower():
                    inc.lifecycle_status = IncidentLifecycleStatus.UNREACHABLE
                    inc.status_explanation = f"Unreachable: {reason_summary}"
                world_state.logger.log(
                    timestamp_min=current_minute,
                    action_type=ActionType.BID_REJECTED,
                    entity_id=inc.incident_id,
                    rule_applied="DISPATCH_INFEASIBLE",
                    explanation=f"Incident {inc.incident_id} (priority {p_score}) cannot be dispatched this tick: {reason_summary}.",
                )

        return committed_assignments
