"""Simulation Session Manager for JalRakshak AI.

Controls the authoritative world state, execution stepping, background run controls,
replay snapshot history buffering, and thread-safe dynamic event injection.
"""

import threading
import uuid
from typing import Any, Dict, List, Optional
from fastapi import HTTPException

from ..core.state import WorldState
from ..core.invariants import InvariantChecker
from ..core.metrics import SimulationMetrics
from ..dispatchers.centralized import CentralizedGreedyDispatcher
from ..dispatchers.multi_agent import MultiAgentDispatcher
from ..models.enums import EventType, BoatStatus, ShelterStatus, IncidentLifecycleStatus, ActionType
from ..models.event import ScenarioEvent
from .schemas import (
    SimulationStateResponse,
    SimulationStepResponse,
    ReplaySnapshot,
    ReplayTimelineResponse,
    EventInjectRequest,
    EventInjectResponse,
    LogsResponse,
)


class SimulationSessionManager:
    """Thread-safe session manager maintaining the active simulation run and replay snapshots."""

    def __init__(self):
        self.lock = threading.RLock()
        self.strategy_name = "centralized"
        self.world_state: WorldState = None  # type: ignore
        self.replay_snapshots: Dict[int, ReplaySnapshot] = {}
        self.is_running = False

        # Initialize default centralized state
        self.reset(strategy="centralized")

    def _create_dispatcher(self, strategy: str):
        if strategy == "centralized":
            return CentralizedGreedyDispatcher()
        elif strategy == "multi_agent":
            return MultiAgentDispatcher()
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported strategy '{strategy}'. Choose 'centralized' or 'multi_agent'.",
            )

    def _capture_snapshot(self) -> ReplaySnapshot:
        """Capture deep-copy data snapshot of current state for deterministic replay."""
        m = self.world_state.clock.current_minute
        kpis = self._compute_kpis()
        violations = InvariantChecker.check_invariants(self.world_state, strict=False)

        snapshot = ReplaySnapshot(
            minute=m,
            strategy=self.strategy_name,
            kpis=kpis,
            boats=[b.model_dump() for b in self.world_state.boats.values()],
            shelters=[s.model_dump() for s in self.world_state.shelters.values()],
            incidents=[i.model_dump() for i in self.world_state.incidents.values()],
            edges=[e.model_dump() for e in self.world_state.edges.values()],
            assignments=[a.model_dump() for a in self.world_state.assignments.values()],
            invariants_ok=(len(violations) == 0),
        )
        self.replay_snapshots[m] = snapshot
        return snapshot

    def _compute_kpis(self) -> Dict[str, Any]:
        """Compute real-time operational metrics from world state."""
        incidents = list(self.world_state.incidents.values())
        boats = list(self.world_state.boats.values())
        shelters = list(self.world_state.shelters.values())

        total_affected = sum(i.people_affected for i in incidents)
        total_rescued = sum(i.people_rescued for i in incidents)
        total_onboard = sum(i.people_onboard for i in incidents)
        total_stranded = sum(i.people_awaiting_pickup for i in incidents)

        fully_served = sum(1 for i in incidents if i.lifecycle_status == IncidentLifecycleStatus.FULLY_SERVED)
        partially_served = sum(1 for i in incidents if i.lifecycle_status == IncidentLifecycleStatus.PARTIALLY_SERVED)
        unserved = sum(1 for i in incidents if i.people_rescued == 0)

        active_boats = sum(1 for b in boats if b.is_operational and b.status != BoatStatus.FAILED)
        failed_boats = sum(1 for b in boats if b.status == BoatStatus.FAILED)

        shelter_rem = sum(s.remaining_capacity for s in shelters)
        shelter_occ = sum(s.current_occupancy for s in shelters)
        shelter_cap = sum(s.capacity_people for s in shelters)

        return {
            "total_people_affected": total_affected,
            "people_rescued_to_shelters": total_rescued,
            "people_onboard_boats": total_onboard,
            "people_awaiting_pickup": total_stranded,
            "incidents_fully_served": fully_served,
            "incidents_partially_served": partially_served,
            "incidents_unserved": unserved,
            "boats_active": active_boats,
            "boats_failed": failed_boats,
            "shelter_total_capacity": shelter_cap,
            "shelter_current_occupancy": shelter_occ,
            "shelter_remaining_capacity": shelter_rem,
        }

    def reset(self, strategy: str = "centralized") -> SimulationStateResponse:
        """Reset the simulation environment back to clean initial conditions."""
        with self.lock:
            self.strategy_name = strategy
            dispatcher = self._create_dispatcher(strategy)
            self.world_state = WorldState(dispatcher=dispatcher)
            self.replay_snapshots.clear()
            self.is_running = False

            # Capture baseline initial snapshot at t=0
            self._capture_snapshot()
            return self.get_state()

    def step(self) -> SimulationStepResponse:
        """Advance the simulation clock by exactly 1 minute, enforcing invariants and capturing replay."""
        with self.lock:
            initial_invalidated = sum(1 for a in self.world_state.assignments.values() if a.status == "INVALIDATED")

            # Advance 1 discrete minute through authoritative event loop
            t = self.world_state.step()

            # Capture snapshot for replay
            self._capture_snapshot()

            violations = InvariantChecker.check_invariants(self.world_state, strict=False)
            current_invalidated = sum(1 for a in self.world_state.assignments.values() if a.status == "INVALIDATED")
            newly_invalidated = max(0, current_invalidated - initial_invalidated)

            active_asgs = sum(
                1 for a in self.world_state.assignments.values()
                if a.status in ("COMMITTED", "EN_ROUTE_PICKUP", "SERVICING_PICKUP", "EN_ROUTE_SHELTER")
            )

            return SimulationStepResponse(
                minute=t,
                strategy=self.strategy_name,
                is_running=self.is_running,
                active_assignments_count=active_asgs,
                newly_invalidated_count=newly_invalidated,
                kpis=self._compute_kpis(),
                invariants_passed=(len(violations) == 0),
                invariant_violations=violations,
            )

    def pause(self) -> Dict[str, Any]:
        """Pause automated simulation execution."""
        with self.lock:
            self.is_running = False
            return {"status": "paused", "minute": self.world_state.clock.current_minute}

    def resume(self) -> Dict[str, Any]:
        """Resume execution."""
        with self.lock:
            self.is_running = True
            return {"status": "running", "minute": self.world_state.clock.current_minute}

    def get_state(self) -> SimulationStateResponse:
        """Retrieve authoritative full world state."""
        with self.lock:
            return SimulationStateResponse(
                minute=self.world_state.clock.current_minute,
                strategy=self.strategy_name,
                is_running=self.is_running,
                kpis=self._compute_kpis(),
                zones=list(self.world_state.zones.values()),
                edges=list(self.world_state.edges.values()),
                boats=list(self.world_state.boats.values()),
                shelters=list(self.world_state.shelters.values()),
                incidents=list(self.world_state.incidents.values()),
                active_assignments=[
                    a for a in self.world_state.assignments.values()
                    if a.status != "DELIVERED"
                ],
            )

    def inject_event(self, req: EventInjectRequest) -> EventInjectResponse:
        """Validate and inject an environmental event into the simulation."""
        with self.lock:
            target = req.target_id.strip()

            # Target validation
            if req.event_type in (EventType.ROAD_CLOSURE, EventType.ROAD_REOPEN):
                if target not in self.world_state.edges:
                    raise HTTPException(status_code=400, detail=f"Target edge '{target}' not found in road network")
            elif req.event_type == EventType.BOAT_FAILURE:
                if target not in self.world_state.boats:
                    raise HTTPException(status_code=400, detail=f"Target boat '{target}' not found")
            elif req.event_type == EventType.SHELTER_OVERFLOW:
                if target not in self.world_state.shelters:
                    raise HTTPException(status_code=400, detail=f"Target shelter '{target}' not found")
            elif req.event_type == EventType.CONFLICTING_REPORT:
                if target not in self.world_state.incidents:
                    raise HTTPException(status_code=400, detail=f"Target incident '{target}' not found")

            minute = req.simulation_minute if req.simulation_minute is not None else self.world_state.clock.current_minute

            event_id = f"INJ-{str(uuid.uuid4())[:6]}"
            scenario_event = ScenarioEvent(
                event_id=event_id,
                simulation_minute=minute,
                event_type=req.event_type,
                target_id=target,
                description=req.description,
                source_confidence=req.source_confidence,
                applied=False,
            )

            # If scheduled for current minute, execute immediately
            if minute == self.world_state.clock.current_minute:
                self.world_state.apply_event(scenario_event)
                message = f"Event {event_id} applied immediately at minute {minute}"
            else:
                self.world_state.events.append(scenario_event)
                message = f"Event {event_id} scheduled for future minute {minute}"

            return EventInjectResponse(
                event_id=event_id,
                event_type=req.event_type,
                target_id=target,
                simulation_minute=minute,
                applied=scenario_event.applied,
                message=message,
            )

    def get_replay_timeline(self) -> ReplayTimelineResponse:
        """Retrieve list of all recorded historical snapshots."""
        with self.lock:
            minutes = sorted(list(self.replay_snapshots.keys()))
            return ReplayTimelineResponse(
                total_snapshots=len(minutes),
                recorded_minutes=minutes,
                active_strategy=self.strategy_name,
            )

    def get_replay_snapshot(self, minute: int) -> ReplaySnapshot:
        """Retrieve a specific historical snapshot."""
        with self.lock:
            if minute not in self.replay_snapshots:
                raise HTTPException(status_code=404, detail=f"No replay snapshot found for minute {minute}")
            return self.replay_snapshots[minute]

    def get_logs(
        self,
        action_type: Optional[ActionType] = None,
        entity_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> LogsResponse:
        """Retrieve filterable, paginated explainable decision logs."""
        with self.lock:
            all_logs = self.world_state.logger.get_logs(action_type=action_type, entity_id=entity_id)
            total = len(all_logs)
            paginated = all_logs[offset : offset + limit]
            return LogsResponse(
                total_count=total,
                returned_count=len(paginated),
                logs=paginated,
            )

    def compare_strategies(self, minutes: int = 15, include_stretch: bool = False) -> Dict[str, Any]:
        """Execute a clean, independent side-by-side run of Centralized Baseline vs MAS."""
        cent_state = WorldState(dispatcher=CentralizedGreedyDispatcher())
        mas_state = WorldState(dispatcher=MultiAgentDispatcher())

        if include_stretch:
            stretch_events = [
                ScenarioEvent(event_id="STRETCH-1", simulation_minute=5, event_type=EventType.ROAD_CLOSURE, target_id="N2", description="Simultaneous bridge failure"),
                ScenarioEvent(event_id="STRETCH-2", simulation_minute=5, event_type=EventType.BOAT_FAILURE, target_id="BOAT03", description="Simultaneous engine failure"),
                ScenarioEvent(event_id="STRETCH-3", simulation_minute=5, event_type=EventType.SHELTER_OVERFLOW, target_id="SH02", description="Simultaneous shelter flooding"),
            ]
            cent_state.events.extend(stretch_events)
            mas_state.events.extend(stretch_events)

        for _ in range(minutes):
            cent_state.step()
            mas_state.step()

        return SimulationMetrics.compare_strategies(cent_state, mas_state)


# Global singleton session manager
session_manager = SimulationSessionManager()
