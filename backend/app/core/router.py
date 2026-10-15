"""Dynamic NetworkX routing engine for JalRakshak AI.

Handles shortest-path calculation (Dijkstra/A*), edge closures, edge reopenings,
uncertainty penalties, and strict safety validation ensuring no closed edge is ever traversed.
"""

from typing import Dict, List, Optional, Set, Tuple
import networkx as nx

from ..models.enums import EdgeStatus
from ..models.graph import NetworkEdge, RoutePath
from ..config import settings


class RoutingError(Exception):
    """Raised when an illegal routing operation is attempted."""
    pass


class NetworkRouter:
    """Manages the road and water graph and computes safe, optimal rescue routes."""

    def __init__(self, edges: List[NetworkEdge], bidirectional: bool = settings.DEFAULT_BIDIRECTIONAL_EDGES):
        self.bidirectional = bidirectional
        self.edges_by_id: Dict[str, NetworkEdge] = {}
        self.graph = nx.Graph() if bidirectional else nx.DiGraph()
        self._build_graph(edges)

    def _build_graph(self, edges: List[NetworkEdge]) -> None:
        """Construct the NetworkX graph from a list of NetworkEdges."""
        self.graph.clear()
        self.edges_by_id.clear()

        for edge in edges:
            self.edges_by_id[edge.edge_id] = edge
            # Store edge reference on the graph
            self.graph.add_edge(
                edge.from_zone,
                edge.to_zone,
                edge_id=edge.edge_id,
                distance=edge.distance_units,
                travel_time=edge.travel_time_min,
                uncertainty=edge.uncertainty,
                status=edge.status,
                closure_reason=edge.closure_reason,
            )

    def get_edge(self, edge_id: str) -> Optional[NetworkEdge]:
        """Retrieve an edge by its identifier."""
        return self.edges_by_id.get(edge_id)

    def close_edge(self, edge_id: str, reason: str = "Injected event") -> bool:
        """Mark an edge as closed, preventing all future traversal."""
        edge = self.edges_by_id.get(edge_id)
        if not edge:
            raise RoutingError(f"Cannot close unknown edge '{edge_id}'")

        edge.status = EdgeStatus.CLOSED
        edge.closure_reason = reason

        # Update in NetworkX graph attributes
        if self.graph.has_edge(edge.from_zone, edge.to_zone):
            self.graph[edge.from_zone][edge.to_zone]["status"] = EdgeStatus.CLOSED
            self.graph[edge.from_zone][edge.to_zone]["closure_reason"] = reason
        return True

    def reopen_edge(self, edge_id: str) -> bool:
        """Reopen a previously closed edge."""
        edge = self.edges_by_id.get(edge_id)
        if not edge:
            raise RoutingError(f"Cannot reopen unknown edge '{edge_id}'")

        edge.status = EdgeStatus.OPEN
        edge.closure_reason = None

        if self.graph.has_edge(edge.from_zone, edge.to_zone):
            self.graph[edge.from_zone][edge.to_zone]["status"] = EdgeStatus.OPEN
            self.graph[edge.from_zone][edge.to_zone]["closure_reason"] = None
        return True

    def get_closed_edge_ids(self) -> List[str]:
        """Return a list of all currently closed edge IDs."""
        return [eid for eid, edge in self.edges_by_id.items() if edge.status == EdgeStatus.CLOSED]

    def _get_active_subgraph(self, uncertainty_lambda: float) -> nx.Graph:
        """
        Produce a view/subgraph strictly excluding all closed edges and weighting
        open edges by: travel_time * (1 + lambda * uncertainty).
        """
        active_g = nx.Graph() if self.bidirectional else nx.DiGraph()

        # Add all nodes
        for node in self.graph.nodes:
            active_g.add_node(node)

        # Add only OPEN (or uncertain but traversable) edges
        for u, v, data in self.graph.edges(data=True):
            if data["status"] == EdgeStatus.CLOSED:
                continue  # STRICT INVARIANT: never include closed edges

            base_time = data["travel_time"]
            unc = data.get("uncertainty", 0.0)
            effective_weight = base_time * (1.0 + uncertainty_lambda * unc)

            active_g.add_edge(
                u,
                v,
                edge_id=data["edge_id"],
                distance=data["distance"],
                travel_time=base_time,
                uncertainty=unc,
                effective_weight=effective_weight,
            )

        return active_g

    def find_shortest_path(
        self,
        origin_zone: str,
        destination_zone: str,
        uncertainty_lambda: float = settings.DEFAULT_UNCERTAINTY_LAMBDA,
    ) -> Optional[RoutePath]:
        """
        Compute safe shortest path between origin and destination using Dijkstra's algorithm.
        Returns None if destination is unreachable. Never traverses a closed edge.
        """
        if origin_zone not in self.graph or destination_zone not in self.graph:
            return None

        # Trivial path (already at destination)
        if origin_zone == destination_zone:
            return RoutePath(
                origin_zone=origin_zone,
                destination_zone=destination_zone,
                zones=[origin_zone],
                edge_ids=[],
                total_travel_time_min=0.0,
                effective_cost=0.0,
                is_valid=True,
            )

        active_g = self._get_active_subgraph(uncertainty_lambda)

        if not nx.has_path(active_g, origin_zone, destination_zone):
            return None  # Truthful reporting: no feasible route exists

        try:
            zone_path = nx.shortest_path(
                active_g,
                source=origin_zone,
                target=destination_zone,
                weight="effective_weight",
            )
        except nx.NetworkXNoPath:
            return None

        # Reconstruct traversed edge IDs and cumulative costs
        edge_ids: List[str] = []
        total_travel_time = 0.0
        effective_cost = 0.0

        for i in range(len(zone_path) - 1):
            u = zone_path[i]
            v = zone_path[i + 1]
            edge_data = active_g[u][v]
            edge_ids.append(edge_data["edge_id"])
            total_travel_time += edge_data["travel_time"]
            effective_cost += edge_data["effective_weight"]

        return RoutePath(
            origin_zone=origin_zone,
            destination_zone=destination_zone,
            zones=zone_path,
            edge_ids=edge_ids,
            total_travel_time_min=round(total_travel_time, 2),
            effective_cost=round(effective_cost, 2),
            is_valid=True,
        )

    def is_route_valid(self, route: RoutePath) -> bool:
        """
        Validate whether a previously computed route remains feasible under current network conditions.
        Returns False immediately if any traversed edge has been closed.
        """
        if not route.edge_ids:
            return True

        for eid in route.edge_ids:
            edge = self.edges_by_id.get(eid)
            if not edge or edge.status == EdgeStatus.CLOSED:
                return False
        return True
