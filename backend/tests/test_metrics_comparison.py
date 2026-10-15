"""Integration test comparing Centralized Baseline vs. Multi-Agent Strategy."""

import pytest
from backend.app.core.state import WorldState
from backend.app.core.metrics import SimulationMetrics
from backend.app.dispatchers.centralized import CentralizedGreedyDispatcher
from backend.app.dispatchers.multi_agent import MultiAgentDispatcher


def test_comparative_evaluation_under_identical_conditions():
    """
    Run Centralized Greedy Baseline and Multi-Agent Strategy on identical
    15-minute simulation schedules. Compare quantitative outcomes.
    """
    cent_state = WorldState(dispatcher=CentralizedGreedyDispatcher())
    mas_state = WorldState(dispatcher=MultiAgentDispatcher())

    # Run both strategies across the identical 15-minute schedule
    for _ in range(15):
        cent_state.step()
        mas_state.step()

    comparison = SimulationMetrics.compare_strategies(cent_state, mas_state)

    summary = comparison["comparison_summary"]
    cent_summary = summary["centralized"]
    mas_summary = summary["multi_agent"]

    assert summary["simulation_minutes"] == 15

    # Both strategies must produce 0 route violations
    assert cent_summary["route_violations"] == 0
    assert mas_summary["route_violations"] == 0

    # Both strategies must track rescued and awaiting counts
    assert "people_rescued" in cent_summary
    assert "people_rescued" in mas_summary

    # Multi-agent negotiation must produce rich audit logs of bids, proposals, and awards
    assert mas_summary["decision_logs"] > 0
    assert cent_summary["decision_logs"] > 0

    # Ensure detailed breakdown contains valid metrics
    detailed_cent = comparison["detailed_centralized"]
    detailed_mas = comparison["detailed_multi_agent"]
    assert "jains_fairness_index" in detailed_cent["fairness"]
    assert "jains_fairness_index" in detailed_mas["fairness"]
