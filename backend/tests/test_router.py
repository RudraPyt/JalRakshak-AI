"""Unit tests for NetworkX graph routing, edge closures, and route invalidation."""

import pytest
from backend.app.core.data_loader import DataLoader
from backend.app.core.router import NetworkRouter, RoutingError
from backend.app.models.enums import EdgeStatus


@pytest.fixture
def router():
    loader = DataLoader()
    _, edges, _, _, _, _ = loader.load_all()
    return NetworkRouter(edges, bidirectional=True)


def test_shortest_path_basic(router):
    """Test shortest path from Northbank-1 to CanalRoad."""
    # Northbank-1 -> LowBridge (N2, 7min) -> CanalRoad (N5, 6min) = 13min
    route = router.find_shortest_path("Northbank-1", "CanalRoad")
    assert route is not None
    assert route.zones == ["Northbank-1", "LowBridge", "CanalRoad"]
    assert route.edge_ids == ["N2", "N5"]
    assert route.total_travel_time_min == 13.0
    assert route.is_valid is True


def test_same_origin_and_destination(router):
    """Path to the same zone returns zero time and empty edges."""
    route = router.find_shortest_path("DepotLane", "DepotLane")
    assert route is not None
    assert route.zones == ["DepotLane"]
    assert route.edge_ids == []
    assert route.total_travel_time_min == 0.0


def test_edge_closure_and_rerouting(router):
    """Closing edge N2 invalidates the route and forces an alternative path."""
    original_route = router.find_shortest_path("Northbank-1", "CanalRoad")
    assert "N2" in original_route.edge_ids
    assert router.is_route_valid(original_route) is True

    # Close edge N2
    router.close_edge("N2", reason="Bridge impassable")
    assert router.is_route_valid(original_route) is False
    assert "N2" in router.get_closed_edge_ids()

    # Recalculate route: must find an alternative without using N2
    rerouted = router.find_shortest_path("Northbank-1", "CanalRoad")
    assert rerouted is not None
    assert "N2" not in rerouted.edge_ids
    assert router.is_route_valid(rerouted) is True
    # The alternative path is longer
    assert rerouted.total_travel_time_min > original_route.total_travel_time_min


def test_edge_reopening(router):
    """Reopening an edge restores the original shortest route."""
    router.close_edge("N2", reason="Bridge flooded")
    rerouted = router.find_shortest_path("Northbank-1", "CanalRoad")
    assert "N2" not in rerouted.edge_ids

    # Reopen edge
    router.reopen_edge("N2")
    assert "N2" not in router.get_closed_edge_ids()

    restored = router.find_shortest_path("Northbank-1", "CanalRoad")
    assert restored.edge_ids == ["N2", "N5"]
    assert restored.total_travel_time_min == 13.0


def test_unreachable_destination(router):
    """If all connecting edges to an area are closed, router returns None."""
    # WestHamlet is connected to HillSide via N10. If N10 is closed, WestHamlet is isolated.
    router.close_edge("N10", reason="Rockslide")
    route = router.find_shortest_path("Northbank-1", "WestHamlet")
    assert route is None, "Expected unreachable route to return None, not fabricated path"


def test_invalid_edge_closure(router):
    """Attempting to close a non-existent edge raises RoutingError."""
    with pytest.raises(RoutingError):
        router.close_edge("NON_EXISTENT_EDGE")
