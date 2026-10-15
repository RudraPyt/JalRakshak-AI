"""Unit tests for authoritative world state, capacity tracking, and event handling."""

import pytest
from backend.app.core.state import WorldState
from backend.app.models.enums import BoatStatus, IncidentLifecycleStatus, ShelterStatus
from backend.app.models.assignment import AssignmentStatus


@pytest.fixture
def state():
    ws = WorldState()
    return ws


def test_pickup_alone_is_not_delivery(state):
    """
    CRITICAL RULE: Stranded passengers boarding a boat does NOT mark an incident served.
    Passengers must physically arrive at an open shelter.
    """
    # Incident INC004 has 5 people at LowBridge. BOAT01 can pick up 5 people.
    state.boats["BOAT01"].current_zone = "LowBridge"

    state.load_passengers(boat_id="BOAT01", incident_id="INC004", count=5)

    boat = state.boats["BOAT01"]
    inc = state.incidents["INC004"]

    assert boat.onboard_people == 5
    assert boat.status == BoatStatus.SERVICING
    assert inc.people_onboard == 5
    assert inc.people_rescued == 0, "Rescued count must remain 0 until shelter delivery!"
    assert inc.lifecycle_status != IncidentLifecycleStatus.FULLY_SERVED
    assert inc.is_fully_resolved is False


def test_delivery_to_shelter_completes_rescue(state):
    """Full rescue lifecycle: Load at incident -> Deliver to shelter -> Full completion."""
    # INC004 (5 people)
    state.boats["BOAT01"].current_zone = "LowBridge"
    state.load_passengers(boat_id="BOAT01", incident_id="INC004", count=5)

    # Deliver to SH01 (mapped to Northbank-1, capacity remaining: 18)
    initial_sh01_occ = state.shelters["SH01"].current_occupancy
    state.boats["BOAT01"].assigned_incident_id = "INC004"
    state.boats["BOAT01"].current_zone = "Northbank-1"

    state.deliver_passengers(boat_id="BOAT01", shelter_id="SH01", count=5)

    boat = state.boats["BOAT01"]
    shelter = state.shelters["SH01"]
    inc = state.incidents["INC004"]

    assert boat.onboard_people == 0
    assert boat.status == BoatStatus.AVAILABLE
    assert shelter.current_occupancy == initial_sh01_occ + 5
    assert inc.people_rescued == 5
    assert inc.people_onboard == 0
    assert inc.lifecycle_status == IncidentLifecycleStatus.FULLY_SERVED
    assert inc.is_fully_resolved is True


def test_partial_rescue_extractions(state):
    """INC008 has 20 people. BOAT03 has capacity 10. Multi-trip handling."""
    # INC008 has 20 people.
    state.boats["BOAT03"].current_zone = "SchoolBlock"

    # Trip 1: Pick up 10
    state.load_passengers(boat_id="BOAT03", incident_id="INC008", count=10)
    inc = state.incidents["INC008"]
    assert inc.people_awaiting_pickup == 10
    assert inc.people_onboard == 10

    # Deliver 10 to SH01
    state.boats["BOAT03"].assigned_incident_id = "INC008"
    state.boats["BOAT03"].current_zone = "Northbank-1"
    state.deliver_passengers(boat_id="BOAT03", shelter_id="SH01", count=10)

    assert inc.people_rescued == 10
    assert inc.people_onboard == 0
    assert inc.lifecycle_status == IncidentLifecycleStatus.PARTIALLY_SERVED
    assert inc.is_fully_resolved is False
    assert inc.people_awaiting_pickup == 10


def test_event_handling_road_closure_invalidates_assignment(state):
    """At simulation minute 5, EV001 closes N2. Any assignment using N2 must be invalidated."""
    asg = state.create_assignment(
        incident_id="INC004",
        boat_id="BOAT01",
        shelter_id="SH01",
        people_count=5,
    )
    assert asg.status == AssignmentStatus.COMMITTED
    assert "N2" in asg.route_to_incident.edge_ids

    # Step simulation until minute 5
    for _ in range(5):
        state.step()

    assert state.clock.current_minute == 5
    # Assignment must now be INVALIDATED due to N2 closure
    updated_asg = state.assignments[asg.assignment_id]
    assert updated_asg.status == AssignmentStatus.INVALIDATED
    assert "N2" in updated_asg.invalidation_reason
    # Boat must have been released back to operational availability
    assert state.boats["BOAT01"].status == BoatStatus.AVAILABLE


def test_event_handling_boat_failure(state):
    """At simulation minute 8, EV002 causes BOAT03 to fail."""
    for _ in range(8):
        state.step()

    assert state.clock.current_minute == 8
    boat3 = state.boats["BOAT03"]
    assert boat3.status == BoatStatus.FAILED
    assert boat3.is_operational is False


def test_event_handling_shelter_overflow(state):
    """At simulation minute 10, EV003 overflows SH02."""
    for _ in range(10):
        state.step()

    assert state.clock.current_minute == 10
    sh02 = state.shelters["SH02"]
    assert sh02.status == ShelterStatus.FULL
    assert sh02.remaining_capacity == 0
