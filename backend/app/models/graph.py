"""Graph data models for road/water network topology."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from .enums import EdgeStatus


class ZoneNode(BaseModel):
    """A spatial node representing a neighbourhood, junction, or operational sector."""
    zone_id: str = Field(..., description="Unique identifier of the zone (e.g., Northbank-1)")
    x: float = Field(..., description="Simulation X-coordinate")
    y: float = Field(..., description="Simulation Y-coordinate")
    description: Optional[str] = Field(default=None, description="Human-readable description or sector notes")


class NetworkEdge(BaseModel):
    """A road or water connection between two zones."""
    edge_id: str = Field(..., description="Unique edge identifier (e.g., N1, N2)")
    from_zone: str = Field(..., description="Origin zone identifier")
    to_zone: str = Field(..., description="Destination zone identifier")
    distance_units: float = Field(..., ge=0.0, description="Spatial distance in simulation units")
    travel_time_min: float = Field(..., gt=0.0, description="Estimated traversal time in minutes")
    status: EdgeStatus = Field(default=EdgeStatus.OPEN, description="Current accessibility status")
    uncertainty: float = Field(default=0.0, ge=0.0, le=1.0, description="Uncertainty score (0.0 to 1.0)")
    closure_reason: Optional[str] = Field(default=None, description="Reason if the edge is closed")

    @field_validator("to_zone")
    @classmethod
    def prevent_self_loops(cls, v: str, info) -> str:
        if "from_zone" in info.data and v == info.data["from_zone"]:
            raise ValueError(f"Self-loop detected: from_zone and to_zone cannot be identical ({v})")
        return v


class RoutePath(BaseModel):
    """Calculated path between two nodes in the network."""
    origin_zone: str
    destination_zone: str
    zones: List[str] = Field(..., description="Ordered list of zone nodes along the route")
    edge_ids: List[str] = Field(..., description="Ordered list of edge IDs traversed")
    total_travel_time_min: float = Field(..., ge=0.0, description="Total expected travel time in minutes")
    effective_cost: float = Field(..., ge=0.0, description="Cost including uncertainty penalties")
    is_valid: bool = Field(default=True, description="False if any edge on path is closed")
