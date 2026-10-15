"""Decision log model for transparent, explainable audit trails."""

from typing import Optional
from pydantic import BaseModel, Field
from .enums import ActionType


class DecisionLogEntry(BaseModel):
    """An auditable record explaining a specific dispatch, routing, or state decision."""
    entry_id: str = Field(..., description="Unique log identifier")
    timestamp_min: int = Field(..., ge=0, description="Simulation minute when decision occurred")
    action_type: ActionType = Field(..., description="Nature of action taken")
    entity_id: str = Field(..., description="Primary entity affected (e.g. BOAT01, INC004)")
    target_id: Optional[str] = Field(default=None, description="Secondary entity (e.g., target shelter, edge)")
    rule_applied: str = Field(..., description="Safety invariant, heuristic, or policy rule name")
    explanation: str = Field(..., description="Human-readable explanation of why this decision was made")
    previous_state: Optional[str] = Field(default=None, description="Previous state before transition")
    new_state: Optional[str] = Field(default=None, description="Resulting state after transition")
