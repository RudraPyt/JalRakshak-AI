"""Explainable decision and audit logging for JalRakshak AI."""

from typing import List, Optional
import uuid
from ..models.enums import ActionType
from ..models.decision_log import DecisionLogEntry


class ExplainableLogger:
    """Records and indexes traceable decision explanations throughout the simulation."""

    def __init__(self):
        self.logs: List[DecisionLogEntry] = []

    def log(
        self,
        timestamp_min: int,
        action_type: ActionType,
        entity_id: str,
        rule_applied: str,
        explanation: str,
        target_id: Optional[str] = None,
        previous_state: Optional[str] = None,
        new_state: Optional[str] = None,
    ) -> DecisionLogEntry:
        """Create and store a structured decision record."""
        entry = DecisionLogEntry(
            entry_id=f"LOG-{len(self.logs) + 1:04d}-{str(uuid.uuid4())[:6]}",
            timestamp_min=timestamp_min,
            action_type=action_type,
            entity_id=entity_id,
            target_id=target_id,
            rule_applied=rule_applied,
            explanation=explanation,
            previous_state=previous_state,
            new_state=new_state,
        )
        self.logs.append(entry)
        return entry

    def get_logs(
        self,
        action_type: Optional[ActionType] = None,
        entity_id: Optional[str] = None,
        since_minute: Optional[int] = None,
    ) -> List[DecisionLogEntry]:
        """Filter logged decision entries."""
        filtered = self.logs
        if action_type:
            filtered = [e for e in filtered if e.action_type == action_type]
        if entity_id:
            filtered = [e for e in filtered if e.entity_id == entity_id or e.target_id == entity_id]
        if since_minute is not None:
            filtered = [e for e in filtered if e.timestamp_min >= since_minute]
        return filtered

    def clear(self) -> None:
        """Clear all logged entries."""
        self.logs.clear()
