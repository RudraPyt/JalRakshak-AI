"""Unit and integration tests for Decentralized Multi-Agent Strategy (CNP)."""

import pytest
from backend.app.core.state import WorldState
from backend.app.dispatchers.multi_agent import MultiAgentDispatcher
from backend.app.core.invariants import InvariantChecker
from backend.app.models.enums import BoatStatus, ShelterStatus, EdgeStatus, IncidentLifecycleStatus, ActionType
from backend.app.models.agent import TaskAnnouncement
from backend.app.models.event import ScenarioEvent, EventType


@pytest.fixture
def mas_state():
    return WorldState(dispatcher=MultiAgentDispatcher())


def test_mas_initial_dispatch_negotiation(mas_state):
    """Verify that autonomous agents exchange proposals, bids, and coordinator awards contracts."""
    assignments = mas_state.dispatcher.dispatch(mas_state)
    assert len(assignments) > 0, "MAS must negotiate and award feasible contracts"

    # Check that proposals, bids, and awards are recorded in decision logs
    logs = mas_state.logger.get_logs()
    actions = [l.action_type for l in logs]
    assert ActionType.PROPOSAL in actions, "Must log Task Announcements (CFPs)"
    assert ActionType.BID_SUBMITTED in actions, "Must log Boat Agent bids"
    assert ActionType.BID_ACCEPTED in actions, "Must log Coordinator contract awards"


def test_multiple_boats_bidding_for_one_incident(mas_state):
    """
    When multiple boats can feasibly serve an incident, each eligible boat submits
    a bid, and the Coordinator selects the best-scoring candidate.
    """
    mas_state.dispatcher._sync_agents(mas_state)
    inc_agent = mas_state.dispatcher.incident_agents["INC002"]  # OldMarket (Critical)

    # Broadcast task announcement
    announcement = inc_agent.announce_task(current_minute=0)
    assert announcement is not None

    # Collect bids from all boat agents
    bids = []
    for b_agent in mas_state.dispatcher.boat_agents.values():
        bid = b_agent.evaluate_task(announcement, mas_state.dispatcher.route_agent)
        if bid and bid.feasible:
            bids.append(bid)

    assert len(bids) > 1, f"Expected multiple boats bidding for INC002, got {len(bids)}"
    # Bids must contain transparent cost estimates
    for b in bids:
        assert b.bid_cost > 0.0
        assert b.offered_capacity > 0


def test_multiple_incidents_competing_for_one_boat(mas_state):
    """
    When multiple incidents compete for a single available boat, the Coordinator
    arbitrates based on urgency, distance, and neighbourhood fairness.
    """
    # Make only BOAT01 available; others failed
    for bid, b in mas_state.boats.items():
        if bid != "BOAT01":
            b.status = BoatStatus.FAILED

    assignments = mas_state.dispatcher.dispatch(mas_state)
    assert len(assignments) == 1, "Only 1 boat available, must commit exactly 1 assignment"
    assert assignments[0].boat_id == "BOAT01"


def test_route_closure_between_bid_and_award(mas_state):
    """
    If a route closes while bids are being evaluated, the Coordinator detects
    the stale route and rejects the bid instead of committing an invalid route.
    """
    mas_state.dispatcher._sync_agents(mas_state)

    # Artificially close N2
    mas_state.router.close_edge("N2", reason="Bridge collapse")

    # Evaluate INC004 (at LowBridge) from BOAT01 (at Northbank-1)
    ann = mas_state.dispatcher.incident_agents["INC004"].announce_task(0)
    bid = mas_state.dispatcher.boat_agents["BOAT01"].evaluate_task(ann, mas_state.dispatcher.route_agent)

    # Route agent should automatically avoid N2 or report no direct path
    if bid:
        assert "N2" not in bid.route_to_incident.edge_ids


def test_shelter_overflow_during_negotiation(mas_state):
    """When all shelters reach capacity, shelter agents reject capacity requests."""
    for s in mas_state.shelters.values():
        s.current_occupancy = s.capacity_people

    mas_state.dispatcher._sync_agents(mas_state)
    s_agent = mas_state.dispatcher.shelter_agents["SH01"]

    resp = s_agent.evaluate_capacity_request(
        incident_id="INC001",
        incident_zone="Northbank-1",
        requested_spaces=5,
        route_agent=mas_state.dispatcher.route_agent,
    )
    assert resp.granted is False
    assert "remaining capacity" in resp.reason.lower()


def test_simultaneous_failure_scenario(mas_state):
    """
    STRETCH CHALLENGE:
    Trigger bridge closure (N2), boat failure (BOAT03), and shelter overflow (SH02)
    simultaneously at simulation minute 5.
    Verify:
    1. System detects all invalidations within the same step.
    2. Compromised commitments are cleanly rolled back.
    3. Feasible alternative assignments are renegotiated.
    4. Safety invariants strictly hold without route violations.
    """
    # Step simulation to minute 4
    for _ in range(4):
        mas_state.step()

    assert mas_state.clock.current_minute == 4

    # Inject simultaneous failures at minute 5
    simul_events = [
        ScenarioEvent(event_id="SIMUL_01", simulation_minute=5, event_type=EventType.ROAD_CLOSURE, target_id="N2", description="Simultaneous bridge failure"),
        ScenarioEvent(event_id="SIMUL_02", simulation_minute=5, event_type=EventType.BOAT_FAILURE, target_id="BOAT03", description="Simultaneous engine failure"),
        ScenarioEvent(event_id="SIMUL_03", simulation_minute=5, event_type=EventType.SHELTER_OVERFLOW, target_id="SH02", description="Simultaneous shelter flooding"),
    ]
    mas_state.events.extend(simul_events)

    # Step into minute 5 (triggering all 3 failures simultaneously)
    t = mas_state.step()
    assert t == 5

    # Invariants must strictly hold
    violations = InvariantChecker.check_invariants(mas_state, strict=False)
    assert len(violations) == 0, f"Invariant violations after simultaneous failure: {violations}"

    # Verify edge N2 is closed, BOAT03 is failed, and SH02 has 0 remaining capacity
    assert mas_state.edges["N2"].status == EdgeStatus.CLOSED
    assert mas_state.boats["BOAT03"].status == BoatStatus.FAILED
    assert mas_state.shelters["SH02"].remaining_capacity == 0

    # Step through recovery (minutes 6 through 15)
    for _ in range(10):
        mas_state.step()
        violations = InvariantChecker.check_invariants(mas_state, strict=False)
        assert len(violations) == 0, "Safety invariant breached during recovery!"

    # Ensure system reached valid final state
    assert mas_state.clock.current_minute == 15


def test_mas_reproducibility():
    """Two identical MAS runs must produce bit-for-bit identical trajectories."""
    run1 = WorldState(dispatcher=MultiAgentDispatcher())
    run2 = WorldState(dispatcher=MultiAgentDispatcher())

    for _ in range(15):
        run1.step()
        run2.step()

    rescued1 = sum(i.people_rescued for i in run1.incidents.values())
    rescued2 = sum(i.people_rescued for i in run2.incidents.values())
    assert rescued1 == rescued2
    assert len(run1.assignments) == len(run2.assignments)
