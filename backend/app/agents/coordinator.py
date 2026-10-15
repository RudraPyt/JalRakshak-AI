"""Coordinator Agent orchestrating the Contract Net Protocol (CNP) negotiation."""

import math
from typing import Dict, List, Optional, Tuple
from ..models.agent import TaskAnnouncement, BoatBid, ShelterBidResponse, ContractAward
from ..models.assignment import Assignment, AssignmentStatus
from ..models.enums import ActionType, IncidentLifecycleStatus, BoatStatus
from .incident_agent import IncidentAgent
from .boat_agent import BoatAgent
from .route_agent import RouteAgent
from .shelter_agent import ShelterAgent


class CoordinatorAgent:
    """
    Facilitates the Contract Net Protocol (CNP) negotiation cycle:
    1. Collects Task Announcements from Incident Agents.
    2. Broadcasts CFPs and aggregates Boat Bids.
    3. Solicits Shelter capacity commitments.
    4. Resolves resource contention and neighbourhood fairness.
    5. Awards contracts and creates binding assignments.
    """

    def __init__(self, fairness_weight: float = 5.0):
        self.fairness_weight = fairness_weight
        self.zone_service_counts: Dict[str, int] = {}

    def negotiate_cycle(
        self,
        incident_agents: List[IncidentAgent],
        boat_agents: List[BoatAgent],
        shelter_agents: List[ShelterAgent],
        route_agent: RouteAgent,
        world_state,
    ) -> List[Assignment]:
        """
        Execute one full multi-agent negotiation cycle.
        Returns a list of newly committed assignments.
        """
        current_minute = world_state.clock.current_minute
        newly_committed: List[Assignment] = []

        # -------------------------------------------------------------
        # Step 1: Collect Task Announcements (CFPs) from Incidents
        # -------------------------------------------------------------
        announcements: List[TaskAnnouncement] = []
        for inc_agent in incident_agents:
            cfp = inc_agent.announce_task(current_minute)
            if cfp:
                announcements.append(cfp)
                world_state.logger.log(
                    timestamp_min=current_minute,
                    action_type=ActionType.PROPOSAL,
                    entity_id=inc_agent.incident_id,
                    rule_applied="TASK_ANNOUNCEMENT",
                    explanation=(
                        f"Incident {inc_agent.incident_id} announced need for {cfp.people_in_distress} "
                        f"people at {cfp.zone} (Urgency: {cfp.urgency.value}, Priority: {cfp.priority_score})."
                    ),
                )

        if not announcements:
            return []

        # -------------------------------------------------------------
        # Step 2: Solicit Bids from Available Boat Agents
        # -------------------------------------------------------------
        bids_by_incident: Dict[str, List[BoatBid]] = {a.incident_id: [] for a in announcements}

        for announcement in announcements:
            for boat_agent in boat_agents:
                if boat_agent.is_available:
                    bid = boat_agent.evaluate_task(announcement, route_agent)
                    if bid and bid.feasible:
                        bids_by_incident[announcement.incident_id].append(bid)
                        world_state.logger.log(
                            timestamp_min=current_minute,
                            action_type=ActionType.BID_SUBMITTED,
                            entity_id=boat_agent.boat_id,
                            target_id=announcement.incident_id,
                            rule_applied="BOAT_BID_SUBMISSION",
                            explanation=(
                                f"Boat {boat_agent.boat_id} bid on {announcement.incident_id}: "
                                f"cost {bid.bid_cost}, capacity {bid.offered_capacity}. {bid.reason}"
                            ),
                        )

        # -------------------------------------------------------------
        # Step 3: Match with Shelters and Generate Candidate Contracts
        # -------------------------------------------------------------
        candidate_contracts = []

        for announcement in announcements:
            bids = bids_by_incident.get(announcement.incident_id, [])
            if not bids:
                inc_agent = next(a for a in incident_agents if a.incident_id == announcement.incident_id)
                inc_agent.receive_rejection("No operational boats able to reach incident location")
                world_state.logger.log(
                    timestamp_min=current_minute,
                    action_type=ActionType.BID_REJECTED,
                    entity_id=announcement.incident_id,
                    rule_applied="NO_FEASIBLE_BIDS",
                    explanation=f"No boats submitted bids for incident {announcement.incident_id}.",
                )
                continue

            # Query shelters for capacity
            for bid in bids:
                boat_agent = next(b for b in boat_agents if b.boat_id == bid.boat_id)

                for shelter_agent in shelter_agents:
                    if not shelter_agent.is_available:
                        continue

                    # Request capacity from shelter
                    resp: ShelterBidResponse = shelter_agent.evaluate_capacity_request(
                        incident_id=announcement.incident_id,
                        incident_zone=announcement.zone,
                        requested_spaces=bid.offered_capacity,
                        route_agent=route_agent,
                    )

                    if not resp.granted or resp.granted_spaces <= 0:
                        continue

                    # Both routes verified: boat->incident and incident->shelter
                    speed = boat_agent.boat.speed_units_per_min * boat_agent.boat.safety_factor
                    t_b_to_inc = bid.route_to_incident.total_travel_time_min / speed if speed > 0 else 999.0
                    t_inc_to_s = resp.route_to_shelter.total_travel_time_min / speed if speed > 0 else 999.0
                    total_time = t_b_to_inc + t_inc_to_s

                    # Calculate multi-agent arbitration score
                    # Priority Score * Headcount - Cost penalty + Fairness bonus
                    zone_count = self.zone_service_counts.get(announcement.zone, 0)
                    fairness_penalty = self.fairness_weight * zone_count

                    contract_score = (
                        (announcement.priority_score * resp.granted_spaces)
                        - (1.5 * total_time)
                        - fairness_penalty
                    )

                    candidate_contracts.append({
                        "announcement": announcement,
                        "boat_agent": boat_agent,
                        "shelter_agent": shelter_agent,
                        "headcount": resp.granted_spaces,
                        "route_to_inc": bid.route_to_incident,
                        "route_to_s": resp.route_to_shelter,
                        "total_time": round(total_time, 2),
                        "time_to_inc": math.ceil(t_b_to_inc),
                        "time_to_s": math.ceil(t_inc_to_s),
                        "score": round(contract_score, 2),
                    })

        # -------------------------------------------------------------
        # Step 4: Resolve Resource Contention (Coordinator Decision)
        # -------------------------------------------------------------
        # Sort candidates by arbitration score descending
        candidate_contracts.sort(key=lambda c: c["score"], reverse=True)

        booked_boats = set()
        satisfied_incidents = set()

        for cand in candidate_contracts:
            ann = cand["announcement"]
            b_agent = cand["boat_agent"]
            s_agent = cand["shelter_agent"]
            count = cand["headcount"]

            # Prevent double-booking of boats
            if b_agent.boat_id in booked_boats:
                continue

            # Prevent multiple simultaneous commitments for the same incident in this cycle
            if ann.incident_id in satisfied_incidents:
                continue

            # Verify shelter still has enough capacity right now
            if s_agent.remaining_capacity < count:
                continue

            # Verify boat is still available right now
            if not b_agent.is_available:
                continue

            # Verify routes are still open right now (in case of dynamic closure)
            if not route_agent.is_route_valid(cand["route_to_inc"]) or not route_agent.is_route_valid(cand["route_to_s"]):
                world_state.logger.log(
                    timestamp_min=current_minute,
                    action_type=ActionType.BID_REJECTED,
                    entity_id=ann.incident_id,
                    target_id=b_agent.boat_id,
                    rule_applied="STALE_ROUTE_REJECTION",
                    explanation=f"Route closed between bid and award for {ann.incident_id}.",
                )
                continue

            # -------------------------------------------------------------
            # Step 5: Award Contract
            # -------------------------------------------------------------
            award_id = f"AWD-{ann.incident_id}-{b_agent.boat_id}-{current_minute}"
            award = ContractAward(
                award_id=award_id,
                incident_id=ann.incident_id,
                boat_id=b_agent.boat_id,
                shelter_id=s_agent.shelter_id,
                headcount=count,
                total_travel_time=cand["total_time"],
                score=cand["score"],
                timestamp_min=current_minute,
                rationale=(
                    f"Negotiated contract awarded: Boat {b_agent.boat_id} accepted task for "
                    f"{ann.incident_id} ({count} people) with delivery to {s_agent.shelter_id}. "
                    f"Score: {cand['score']}, ETA: {cand['total_time']} min."
                ),
            )

            # Update agents
            inc_agent = next(a for a in incident_agents if a.incident_id == ann.incident_id)
            inc_agent.receive_award(award)
            b_agent.award_contract(award)
            s_agent.reserve(count)

            # Update zone fairness counts
            self.zone_service_counts[ann.zone] = self.zone_service_counts.get(ann.zone, 0) + 1

            # Commit to authoritative WorldState
            asg = Assignment(
                assignment_id=f"ASG-MAS-{ann.incident_id}-{b_agent.boat_id}-{current_minute}",
                incident_id=ann.incident_id,
                boat_id=b_agent.boat_id,
                shelter_id=s_agent.shelter_id,
                people_assigned=count,
                route_to_incident=cand["route_to_inc"],
                route_to_shelter=cand["route_to_s"],
                status=AssignmentStatus.EN_ROUTE_PICKUP,
                pickup_travel_duration=cand["time_to_inc"],
                shelter_travel_duration=cand["time_to_s"],
                minutes_in_leg=0,
                current_leg="to_incident",
                created_at_minute=current_minute,
                rationale=award.rationale,
            )
            world_state.assignments[asg.assignment_id] = asg

            world_state.logger.log(
                timestamp_min=current_minute,
                action_type=ActionType.BID_ACCEPTED,
                entity_id=b_agent.boat_id,
                target_id=ann.incident_id,
                rule_applied="CONTRACT_AWARD",
                explanation=award.rationale,
                previous_state=BoatStatus.AVAILABLE.value,
                new_state=BoatStatus.IN_TRANSIT.value,
            )

            booked_boats.add(b_agent.boat_id)
            satisfied_incidents.add(ann.incident_id)
            newly_committed.append(asg)

        # -------------------------------------------------------------
        # Step 6: Log Rejections for Unawarded Incidents
        # -------------------------------------------------------------
        for ann in announcements:
            if ann.incident_id not in satisfied_incidents:
                inc_agent = next(a for a in incident_agents if a.incident_id == ann.incident_id)
                # Check if shelter capacity was the reason
                all_shelters_full = all(s.remaining_capacity == 0 for s in shelter_agents)
                if all_shelters_full:
                    inc_agent.receive_rejection("Total regional shelter capacity exhausted (0 spaces remaining)")
                else:
                    inc_agent.receive_rejection("All operational boats engaged on higher-scoring missions")

        return newly_committed
