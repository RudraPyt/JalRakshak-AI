"""Unit tests for safety invariants checker (INV-1 through INV-8)."""

import pytest
from backend.app.core.state import WorldState
from backend.app.core.invariants import InvariantChecker, InvariantViolationError
from backend.app.models.enums import BoatStatus, IncidentLifecycleStatus
from backend.app.models.assignment import AssignmentStatus


@pytest.fixture
def state():
    ws = WorldState()
    return ws


def test_initial_state_has_zero_invariant_violations(state):
    """The clean initial scenario must pass all invariants."""
    violations = InvariantChecker.check_invariants(state, strict=False)
    assert len(violations) == 0, f"Expected 0 violations on clean state, got: {violations}"


def test_inv1_closed_route_traversal_detected(state):
    """INV-1: An assignment traversing a closed edge must be flagged as a violation."""
    # Commit BOAT01 to rescue INC004 at LowBridge to SH01
    asg = state.create_assignment(
        incident_id="INC004",
        boat_id="BOAT01",
        shelter_id="SH01",
        people_count=5,
    )
    # Edge N2 is used by this route. Now artificially close N2 without invalidating the assignment
    state.router.close_edge("N2")

    violations = InvariantChecker.check_invariants(state)
    assert any("INV-1 Violation" in v and "N2" in v for v in violations)


def test_inv2_unavailable_boat_assignment_detected(state):
    """INV-2: A failed boat holding an active assignment must be flagged."""
    asg = state.create_assignment(
        incident_id="INC004",
        boat_id="BOAT01",
        shelter_id="SH01",
        people_count=5,
    )
    # Artificially set boat to FAILED while leaving assignment active
    state.boats["BOAT01"].status = BoatStatus.FAILED

    violations = InvariantChecker.check_invariants(state)
    assert any("INV-2 Violation" in v and "BOAT01" in v for v in violations)


def test_inv3_double_booking_detected(state):
    """INV-3: A boat holding two active assignments simultaneously must be flagged."""
    state.create_assignment(
        incident_id="INC004",
        boat_id="BOAT01",
        shelter_id="SH01",
        people_count=4,
    )
    # Artificially add second simultaneous assignment for BOAT01
    asg2 = state.assignments[list(state.assignments.keys())[0]].model_copy()
    asg2.assignment_id = "ASG-DUPLICATE-BOAT01"
    asg2.incident_id = "INC002"
    state.assignments["ASG-DUPLICATE-BOAT01"] = asg2

    violations = InvariantChecker.check_invariants(state)
    assert any("INV-3 Violation" in v and "BOAT01" in v for v in violations)


def test_inv4_shelter_overcapacity_detected(state):
    """INV-4: Shelter occupancy + reservations exceeding capacity must be flagged."""
    sh = state.shelters["SH03"]  # capacity: 30, occ: 28, rem: 2
    sh.reserved_capacity = 5  # 28 + 5 = 33 > 30!

    violations = InvariantChecker.check_invariants(state)
    assert any("INV-4 Violation" in v and "SH03" in v for v in violations)


def test_inv5_false_completion_detected(state):
    """INV-5: Incident marked FULLY_SERVED when people_rescued < people_affected must be flagged."""
    inc = state.incidents["INC001"]  # 14 affected
    inc.people_rescued = 8
    inc.lifecycle_status = IncidentLifecycleStatus.FULLY_SERVED

    violations = InvariantChecker.check_invariants(state)
    assert any("INV-5 Violation" in v and "INC001" in v for v in violations)
