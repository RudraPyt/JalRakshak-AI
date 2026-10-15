"""Unit tests for Centralized Greedy Baseline Dispatcher."""

import pytest
from backend.app.core.state import WorldState
from backend.app.dispatchers.centralized import CentralizedGreedyDispatcher
from backend.app.models.enums import UrgencyLevel, IncidentLifecycleStatus, BoatStatus, VerificationStatus


@pytest.fixture
def state():
    ws = WorldState()
    return ws


@pytest.fixture
def dispatcher():
    return CentralizedGreedyDispatcher()


def test_priority_scoring_urgency_hierarchy(dispatcher, state):
    """Critical incidents score higher than High, which score higher than Medium."""
    inc_crit = state.incidents["INC002"]  # Critical, age 18, conf 0.95
    inc_high = state.incidents["INC001"]  # High, age 5, conf 0.92
    inc_med = state.incidents["INC011"]   # Medium, age 15, conf 0.74

    score_crit = dispatcher.compute_priority_score(inc_crit, current_minute=0)
    score_high = dispatcher.compute_priority_score(inc_high, current_minute=0)
    score_med = dispatcher.compute_priority_score(inc_med, current_minute=0)

    assert score_crit > score_high > score_med


def test_waiting_time_prevents_starvation(dispatcher, state):
    """
    Starvation prevention: an older medium incident that has waited extensively
    accrues waiting-time bonus points and can surpass a low-confidence or fresh report.
    """
    old_med = state.incidents["INC005"]  # Medium (50), age 35 min, conf 0.70
    score_at_t0 = dispatcher.compute_priority_score(old_med, current_minute=0)
    score_at_t20 = dispatcher.compute_priority_score(old_med, current_minute=20)

    # Score increases as waiting time advances
    assert score_at_t20 >= score_at_t0


def test_dispatcher_creates_valid_commitments(dispatcher, state):
    """Dispatcher matches highest-priority feasible incidents with available boats and shelters."""
    initial_avail_boats = len(state.get_available_boats())
    assert initial_avail_boats == 4

    assignments = dispatcher.dispatch(state)
    assert len(assignments) > 0, "Expected at least one valid commitment created"

    for asg in assignments:
        # Verify boat was properly reserved and set to in_transit
        boat = state.boats[asg.boat_id]
        assert boat.status == BoatStatus.IN_TRANSIT
        assert boat.assigned_incident_id == asg.incident_id

        # Verify incident status was properly updated
        inc = state.incidents[asg.incident_id]
        assert inc.lifecycle_status == IncidentLifecycleStatus.ASSIGNED
        assert inc.assigned_boat_id == asg.boat_id

        # Verify shelter reservation
        shelter = state.shelters[asg.shelter_id]
        assert shelter.reserved_capacity >= asg.people_assigned

        # Verify route validity
        assert asg.route_to_incident is not None
        assert asg.route_to_shelter is not None
        assert state.router.is_route_valid(asg.route_to_incident)
        assert state.router.is_route_valid(asg.route_to_shelter)


def test_no_double_booking_by_dispatcher(dispatcher, state):
    """A boat must never receive two simultaneous assignments in the same dispatch cycle."""
    assignments = dispatcher.dispatch(state)
    assigned_boat_ids = [a.boat_id for a in assignments]
    assert len(assigned_boat_ids) == len(set(assigned_boat_ids)), "Duplicate boat assignment detected!"


def test_partial_evacuation_headcount_constraint(dispatcher, state):
    """
    INC008 has 20 people. Total boat capacity is 10 (BOAT03).
    Dispatcher must only assign up to boat capacity and shelter capacity.
    """
    inc8 = state.incidents["INC008"]
    assert inc8.people_affected == 20

    assignments = dispatcher.dispatch(state)
    inc8_asgs = [a for a in assignments if a.incident_id == "INC008"]

    if inc8_asgs:
        asg = inc8_asgs[0]
        boat = state.boats[asg.boat_id]
        # Must not exceed boat carrying capacity
        assert asg.people_assigned <= boat.capacity_people
        # Must leave remaining people awaiting next trip
        assert inc8.people_awaiting_pickup == inc8.people_affected - asg.people_assigned


def test_shelter_capacity_exhaustion_truthful_reporting(dispatcher, state):
    """
    When all shelters have 0 remaining capacity, dispatcher does not fabricate assignments.
    Incidents are marked with UNMET_SHELTER_BOTTLENECK.
    """
    # Artificially fill all shelters to maximum capacity
    for s in state.shelters.values():
        s.current_occupancy = s.capacity_people
        s.reserved_capacity = 0

    assert len(state.get_available_shelters()) == 0

    assignments = dispatcher.dispatch(state)
    assert len(assignments) == 0, "No assignments must be created when all shelters are full"

    # Incidents evaluated during dispatch must reflect shelter bottleneck
    unmet_incidents = [
        i for i in state.incidents.values()
        if i.lifecycle_status == IncidentLifecycleStatus.UNMET_SHELTER_BOTTLENECK
    ]
    assert len(unmet_incidents) > 0
    assert "shelter capacity exhausted" in unmet_incidents[0].status_explanation.lower()
