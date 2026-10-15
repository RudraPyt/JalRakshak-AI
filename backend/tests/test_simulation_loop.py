"""Integration tests for full discrete simulation loop and reproducibility."""

import pytest
from backend.app.core.state import WorldState
from backend.app.dispatchers.centralized import CentralizedGreedyDispatcher
from backend.app.core.invariants import InvariantChecker
from backend.app.models.enums import BoatStatus, ShelterStatus, EdgeStatus, IncidentLifecycleStatus


def test_full_15_minute_simulation_execution():
    """
    Run full 15-minute simulation end-to-end with the Centralized Greedy Dispatcher.
    Enforces all safety invariants at EVERY step, verifies dynamic event handling,
    and inspects final state.
    """
    state = WorldState(dispatcher=CentralizedGreedyDispatcher())
    assert state.clock.current_minute == 0

    # Step through 15 simulated minutes
    for minute in range(1, 16):
        t = state.step()
        assert t == minute

        # Strict invariant checking at every single minute tick
        violations = InvariantChecker.check_invariants(state, strict=False)
        assert len(violations) == 0, f"Invariant violation detected at minute {minute}: {violations}"

        # Check minute 5: Road closure N2
        if minute == 5:
            assert state.edges["N2"].status == EdgeStatus.CLOSED
            assert "N2" in state.router.get_closed_edge_ids()

        # Check minute 8: Boat failure BOAT03
        if minute == 8:
            assert state.boats["BOAT03"].status == BoatStatus.FAILED
            assert state.boats["BOAT03"].is_operational is False

        # Check minute 10: Shelter overflow SH02
        if minute == 10:
            assert state.shelters["SH02"].status == ShelterStatus.FULL
            assert state.shelters["SH02"].remaining_capacity == 0

        # Check minute 15: Road reopen N2
        if minute == 15:
            assert state.edges["N2"].status == EdgeStatus.OPEN
            assert "N2" not in state.router.get_closed_edge_ids()

    # Verify final simulation metrics and states
    fully_served = [i for i in state.incidents.values() if i.lifecycle_status == IncidentLifecycleStatus.FULLY_SERVED]
    partially_served = [i for i in state.incidents.values() if i.lifecycle_status == IncidentLifecycleStatus.PARTIALLY_SERVED]
    total_rescued_people = sum(i.people_rescued for i in state.incidents.values())

    # Total rescued people cannot exceed total shelter capacity available (initial 26 minus SH02 overflow at min 10)
    assert total_rescued_people <= 26, f"Rescued ({total_rescued_people}) exceeded max shelter space (26)"
    assert len(fully_served) + len(partially_served) > 0, "Expected at least some incidents served"

    # All decision logs must have been preserved
    logs = state.logger.get_logs()
    assert len(logs) > 10, "Expected extensive explainable decision log entries"


def test_simulation_reproducibility():
    """
    Given identical initial state and deterministic dispatcher, two full runs
    must yield bit-for-bit identical outcomes.
    """
    run1 = WorldState(dispatcher=CentralizedGreedyDispatcher())
    run2 = WorldState(dispatcher=CentralizedGreedyDispatcher())

    for _ in range(15):
        run1.step()
        run2.step()

    # Compare key results
    rescued1 = sum(i.people_rescued for i in run1.incidents.values())
    rescued2 = sum(i.people_rescued for i in run2.incidents.values())
    assert rescued1 == rescued2, f"Run 1 rescued {rescued1} vs Run 2 rescued {rescued2}"

    served_ids1 = sorted([i.incident_id for i in run1.incidents.values() if i.lifecycle_status == IncidentLifecycleStatus.FULLY_SERVED])
    served_ids2 = sorted([i.incident_id for i in run2.incidents.values() if i.lifecycle_status == IncidentLifecycleStatus.FULLY_SERVED])
    assert served_ids1 == served_ids2

    # Compare boat stats
    for bid in run1.boats:
        b1 = run1.boats[bid]
        b2 = run2.boats[bid]
        assert b1.total_idle_minutes == b2.total_idle_minutes
        assert b1.total_service_minutes == b2.total_service_minutes
        assert b1.current_zone == b2.current_zone
