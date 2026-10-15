"""Evaluation and comparative benchmarking metrics for JalRakshak AI.

Computes quantitative metrics across Time-to-Service, Unmet Requests, Resource Idle Time,
Committed Route Violations, Neighbourhood Fairness (Jain's Index), and Failure Recovery Time.
"""

from typing import Any, Dict, List, Optional
from ..models.enums import IncidentLifecycleStatus, BoatStatus, EdgeStatus, ActionType
from .invariants import InvariantChecker


class SimulationMetrics:
    """Evaluates and compares dispatch strategy performance on identical scenario runs."""

    @classmethod
    def evaluate_run(cls, world_state, strategy_name: str) -> Dict[str, Any]:
        """
        Extract quantitative evaluation metrics from a completed or running WorldState instance.
        """
        incidents = list(world_state.incidents.values())
        boats = list(world_state.boats.values())
        shelters = list(world_state.shelters.values())
        assignments = list(world_state.assignments.values())

        # -------------------------------------------------------------
        # 1. Time to Service (MTTS)
        # -------------------------------------------------------------
        served_times: List[float] = []
        for inc in incidents:
            if inc.served_at_minute is not None and inc.lifecycle_status == IncidentLifecycleStatus.FULLY_SERVED:
                wait_time = inc.served_at_minute - inc.reported_at_minute
                served_times.append(float(wait_time))

        mtts = round(sum(served_times) / len(served_times), 2) if served_times else None

        # -------------------------------------------------------------
        # 2. Unmet Requests & Headcounts
        # -------------------------------------------------------------
        total_incidents = len(incidents)
        fully_served = sum(1 for i in incidents if i.lifecycle_status == IncidentLifecycleStatus.FULLY_SERVED)
        partially_served = sum(1 for i in incidents if i.lifecycle_status == IncidentLifecycleStatus.PARTIALLY_SERVED)
        unserved = sum(1 for i in incidents if i.people_rescued == 0)

        total_affected_people = sum(i.people_affected for i in incidents)
        total_rescued_people = sum(i.people_rescued for i in incidents)
        total_onboard_people = sum(i.people_onboard for i in incidents)
        total_stranded_people = sum(i.people_awaiting_pickup for i in incidents)

        unmet_incidents_pct = round((unserved / total_incidents) * 100, 1) if total_incidents > 0 else 0.0
        unmet_people_pct = round((total_stranded_people / total_affected_people) * 100, 1) if total_affected_people > 0 else 0.0

        # Bottleneck counts
        shelter_bottlenecks = sum(
            1 for i in incidents
            if i.lifecycle_status == IncidentLifecycleStatus.UNMET_SHELTER_BOTTLENECK or (
                i.status_explanation and "shelter capacity" in i.status_explanation.lower()
            )
        )

        # -------------------------------------------------------------
        # 3. Resource Idle Time
        # -------------------------------------------------------------
        total_idle_min = sum(b.total_idle_minutes for b in boats)
        total_service_min = sum(b.total_service_minutes for b in boats)
        total_boat_min = total_idle_min + total_service_min
        idle_ratio = round((total_idle_min / total_boat_min) * 100, 1) if total_boat_min > 0 else 0.0

        # -------------------------------------------------------------
        # 4. Route Violations
        # -------------------------------------------------------------
        closed_edge_ids = set(world_state.router.get_closed_edge_ids())
        route_violations = 0
        for asg in assignments:
            if asg.status != "INVALIDATED":
                if asg.route_to_incident:
                    if any(eid in closed_edge_ids for eid in asg.route_to_incident.edge_ids):
                        route_violations += 1
                if asg.route_to_shelter:
                    if any(eid in closed_edge_ids for eid in asg.route_to_shelter.edge_ids):
                        route_violations += 1

        # -------------------------------------------------------------
        # 5. Neighbourhood Fairness (Jain's Fairness Index)
        # -------------------------------------------------------------
        # Measure ratio of rescued / affected per zone
        zone_affected: Dict[str, int] = {}
        zone_rescued: Dict[str, int] = {}

        for inc in incidents:
            zone_affected[inc.zone] = zone_affected.get(inc.zone, 0) + inc.people_affected
            zone_rescued[inc.zone] = zone_rescued.get(inc.zone, 0) + inc.people_rescued

        # Ratios per populated zone
        ratios = []
        for z, aff in zone_affected.items():
            if aff > 0:
                ratios.append(zone_rescued.get(z, 0) / aff)

        n = len(ratios)
        if n > 0 and sum(r**2 for r in ratios) > 0:
            sum_r = sum(ratios)
            sum_sq_r = sum(r**2 for r in ratios)
            jains_index = round((sum_r ** 2) / (n * sum_sq_r), 3)
        else:
            jains_index = 0.0

        # -------------------------------------------------------------
        # 6. Safety Invariant Check
        # -------------------------------------------------------------
        violations = InvariantChecker.check_invariants(world_state, strict=False)

        # -------------------------------------------------------------
        # 7. Audit Log Summary
        # -------------------------------------------------------------
        logs = world_state.logger.get_logs()
        proposals_count = sum(1 for l in logs if l.action_type == ActionType.PROPOSAL)
        bids_submitted_count = sum(1 for l in logs if l.action_type == ActionType.BID_SUBMITTED)
        bids_accepted_count = sum(1 for l in logs if l.action_type in (ActionType.COMMITTED, ActionType.BID_ACCEPTED))
        bids_rejected_count = sum(1 for l in logs if l.action_type == ActionType.BID_REJECTED)
        invalidations_count = sum(1 for l in logs if l.action_type == ActionType.INVALIDATED)

        return {
            "strategy_name": strategy_name,
            "simulation_minute": world_state.clock.current_minute,
            "time_to_service": {
                "mean_time_to_service_min": mtts,
                "fully_served_count": fully_served,
                "note": "Computed only over fully served incidents; unserved requests reported separately below.",
            },
            "unmet_requests": {
                "total_incidents": total_incidents,
                "fully_served_incidents": fully_served,
                "partially_served_incidents": partially_served,
                "unserved_incidents": unserved,
                "unmet_incidents_percentage": unmet_incidents_pct,
                "total_people_in_distress": total_affected_people,
                "people_rescued_to_shelters": total_rescued_people,
                "people_onboard_boats": total_onboard_people,
                "people_awaiting_pickup": total_stranded_people,
                "unmet_people_percentage": unmet_people_pct,
                "shelter_bottleneck_count": shelter_bottlenecks,
            },
            "resource_utilization": {
                "total_boat_idle_minutes": total_idle_min,
                "total_boat_service_minutes": total_service_min,
                "idle_percentage": idle_ratio,
            },
            "safety": {
                "committed_route_violations": route_violations,
                "active_invariant_violations_count": len(violations),
                "invariant_violations": violations,
            },
            "fairness": {
                "jains_fairness_index": jains_index,
                "scale": "1/n (least fair) to 1.0 (perfectly fair across all zones)",
                "zone_distribution": {
                    z: {"affected": zone_affected[z], "rescued": zone_rescued.get(z, 0)}
                    for z in zone_affected
                },
            },
            "negotiation_and_audit": {
                "total_decision_logs": len(logs),
                "proposals": proposals_count,
                "bids_submitted": bids_submitted_count,
                "bids_accepted": bids_accepted_count,
                "bids_rejected": bids_rejected_count,
                "commitments_invalidated": invalidations_count,
            },
        }

    @classmethod
    def compare_strategies(
        cls,
        centralized_state,
        mas_state,
    ) -> Dict[str, Any]:
        """Produce a side-by-side comparative benchmark between Centralized Baseline and MAS."""
        cent_eval = cls.evaluate_run(centralized_state, "Centralized Greedy Baseline")
        mas_eval = cls.evaluate_run(mas_state, "Decentralized Multi-Agent Strategy (CNP)")

        return {
            "comparison_summary": {
                "simulation_minutes": centralized_state.clock.current_minute,
                "centralized": {
                    "people_rescued": cent_eval["unmet_requests"]["people_rescued_to_shelters"],
                    "people_onboard": cent_eval["unmet_requests"]["people_onboard_boats"],
                    "people_awaiting": cent_eval["unmet_requests"]["people_awaiting_pickup"],
                    "idle_percentage": cent_eval["resource_utilization"]["idle_percentage"],
                    "jains_fairness": cent_eval["fairness"]["jains_fairness_index"],
                    "route_violations": cent_eval["safety"]["committed_route_violations"],
                    "decision_logs": cent_eval["negotiation_and_audit"]["total_decision_logs"],
                },
                "multi_agent": {
                    "people_rescued": mas_eval["unmet_requests"]["people_rescued_to_shelters"],
                    "people_onboard": mas_eval["unmet_requests"]["people_onboard_boats"],
                    "people_awaiting": mas_eval["unmet_requests"]["people_awaiting_pickup"],
                    "idle_percentage": mas_eval["resource_utilization"]["idle_percentage"],
                    "jains_fairness": mas_eval["fairness"]["jains_fairness_index"],
                    "route_violations": mas_eval["safety"]["committed_route_violations"],
                    "decision_logs": mas_eval["negotiation_and_audit"]["total_decision_logs"],
                },
            },
            "detailed_centralized": cent_eval,
            "detailed_multi_agent": mas_eval,
        }
