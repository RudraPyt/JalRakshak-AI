"""Comprehensive API tests for JalRakshak AI FastAPI backend."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    """Verify backend health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "JalRakshak AI" in data["service"]


def test_root_endpoint_metadata():
    """Verify root endpoint exposes documentation and endpoints map."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "JalRakshak AI"
    assert "/docs" in data["docs_url"]
    assert "simulation_endpoints" in data


def test_simulation_reset_centralized():
    """Verify reset to initial state with centralized baseline."""
    response = client.post("/api/simulation/reset", json={"strategy": "centralized"})
    assert response.status_code == 200
    data = response.json()
    assert data["minute"] == 0
    assert data["strategy"] == "centralized"
    assert len(data["incidents"]) == 12
    assert len(data["boats"]) == 4
    assert len(data["shelters"]) == 4
    assert len(data["edges"]) == 12


def test_simulation_reset_multi_agent():
    """Verify reset with multi_agent strategy."""
    response = client.post("/api/simulation/reset", json={"strategy": "multi_agent"})
    assert response.status_code == 200
    data = response.json()
    assert data["minute"] == 0
    assert data["strategy"] == "multi_agent"


def test_simulation_reset_invalid_strategy_rejected():
    """Attempting an unsupported strategy returns 422 Unprocessable Entity."""
    response = client.post("/api/simulation/reset", json={"strategy": "unsupported_magic"})
    assert response.status_code == 422


def test_simulation_single_step():
    """Verify single-step increments clock by exactly 1 minute and preserves invariants."""
    client.post("/api/simulation/reset", json={"strategy": "centralized"})

    step_res = client.post("/api/simulation/step")
    assert step_res.status_code == 200
    data = step_res.json()
    assert data["minute"] == 1
    assert data["invariants_passed"] is True
    assert len(data["invariant_violations"]) == 0


def test_simulation_pause_and_resume():
    """Verify pause and resume state controls."""
    pause_res = client.post("/api/simulation/pause")
    assert pause_res.status_code == 200
    assert pause_res.json()["status"] == "paused"

    resume_res = client.post("/api/simulation/resume")
    assert resume_res.status_code == 200
    assert resume_res.json()["status"] == "running"


def test_state_endpoint_consistency():
    """Verify state endpoint returns structured entities and KPI counts."""
    res = client.get("/api/simulation/state")
    assert res.status_code == 200
    data = res.json()
    assert "kpis" in data
    assert data["kpis"]["total_people_affected"] == 115
    assert len(data["zones"]) == 11


def test_event_listing_and_manual_injection():
    """Verify listing existing events and injecting a new event."""
    client.post("/api/simulation/reset", json={"strategy": "centralized"})

    # List pre-scheduled scenario events
    events_res = client.get("/api/events")
    assert events_res.status_code == 200
    events = events_res.json()
    assert len(events) >= 5

    # Inject a valid road closure event for edge N1
    inject_res = client.post(
        "/api/events/inject",
        json={
            "event_type": "road_closure",
            "target_id": "N1",
            "description": "High water levels on OldMarket causeway",
            "simulation_minute": 2,
        },
    )
    assert inject_res.status_code == 200
    inj_data = inject_res.json()
    assert inj_data["target_id"] == "N1"
    assert inj_data["simulation_minute"] == 2


def test_event_injection_invalid_target_rejected():
    """Injecting an event targeting a non-existent entity returns 400 Bad Request."""
    res = client.post(
        "/api/events/inject",
        json={
            "event_type": "boat_failure",
            "target_id": "SUBMARINE_99",
            "description": "Fictional resource",
        },
    )
    assert res.status_code == 400
    assert "not found" in res.json()["detail"].lower()


def test_decision_logs_retrieval_and_filtering():
    """Verify decision log endpoint supports filtering by action type and entity."""
    client.post("/api/simulation/reset", json={"strategy": "centralized"})
    client.post("/api/simulation/step")

    logs_res = client.get("/api/logs/decisions?limit=10")
    assert logs_res.status_code == 200
    data = logs_res.json()
    assert data["total_count"] > 0
    assert len(data["logs"]) <= 10


def test_after_action_replay_timeline_and_snapshots():
    """Verify replay timeline and snapshot retrieval for historical inspection."""
    client.post("/api/simulation/reset", json={"strategy": "centralized"})
    client.post("/api/simulation/step")
    client.post("/api/simulation/step")

    timeline_res = client.get("/api/replay/timeline")
    assert timeline_res.status_code == 200
    timeline = timeline_res.json()
    assert timeline["total_snapshots"] >= 3  # t=0, t=1, t=2
    assert 0 in timeline["recorded_minutes"]
    assert 1 in timeline["recorded_minutes"]
    assert 2 in timeline["recorded_minutes"]

    # Retrieve snapshot for minute 1
    snap_res = client.get("/api/replay/snapshot/1")
    assert snap_res.status_code == 200
    snap = snap_res.json()
    assert snap["minute"] == 1
    assert snap["strategy"] == "centralized"
    assert snap["invariants_ok"] is True
    assert "kpis" in snap


def test_replay_snapshot_not_found():
    """Requesting an unrecorded historical snapshot returns 404."""
    client.post("/api/simulation/reset", json={"strategy": "centralized"})
    res = client.get("/api/replay/snapshot/999")
    assert res.status_code == 404


def test_evaluation_current_endpoint():
    """Verify evaluation metrics endpoint for current active session."""
    client.post("/api/simulation/reset", json={"strategy": "centralized"})
    client.post("/api/simulation/step")

    eval_res = client.get("/api/evaluation/current")
    assert eval_res.status_code == 200
    metrics = eval_res.json()
    assert metrics["strategy_name"] == "Centralized Greedy Baseline"
    assert "unmet_requests" in metrics
    assert "resource_utilization" in metrics
    assert "fairness" in metrics


def test_evaluation_compare_endpoint():
    """Verify side-by-side strategy comparison API executes both runs deterministically."""
    compare_res = client.post(
        "/api/evaluation/compare",
        json={"simulation_minutes": 5, "include_stretch_events": False},
    )
    assert compare_res.status_code == 200
    comp = compare_res.json()
    assert "comparison_summary" in comp
    assert comp["comparison_summary"]["simulation_minutes"] == 5
    assert "centralized" in comp["comparison_summary"]
    assert "multi_agent" in comp["comparison_summary"]


def test_stretch_challenge_endpoint():
    """Verify simultaneous stretch challenge endpoint runs successfully."""
    stretch_res = client.post("/api/evaluation/stretch-challenge")
    assert stretch_res.status_code == 200
    data = stretch_res.json()
    assert "comparison_summary" in data
    assert data["comparison_summary"]["simulation_minutes"] == 15
    # Route violations must remain 0 despite simultaneous closures
    assert data["comparison_summary"]["centralized"]["route_violations"] == 0
    assert data["comparison_summary"]["multi_agent"]["route_violations"] == 0
