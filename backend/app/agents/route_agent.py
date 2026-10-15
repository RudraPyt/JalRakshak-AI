"""Route Agent representing network topology and path validation."""

from typing import List, Optional
from ..core.router import NetworkRouter
from ..models.graph import RoutePath
from ..config import settings


class RouteAgent:
    """Agent responsible for network reachability, shortest-path routing, and closure detection."""

    def __init__(self, router: NetworkRouter):
        self.router = router

    def find_route(
        self,
        origin_zone: str,
        destination_zone: str,
        uncertainty_lambda: float = settings.DEFAULT_UNCERTAINTY_LAMBDA,
    ) -> Optional[RoutePath]:
        """Query shortest safe path between two zones, excluding closed edges."""
        return self.router.find_shortest_path(origin_zone, destination_zone, uncertainty_lambda)

    def is_route_valid(self, route: Optional[RoutePath]) -> bool:
        """Check if an existing route remains traversable."""
        if not route:
            return False
        return self.router.is_route_valid(route)

    def get_closed_edges(self) -> List[str]:
        """Return all currently impassable edges."""
        return self.router.get_closed_edge_ids()
