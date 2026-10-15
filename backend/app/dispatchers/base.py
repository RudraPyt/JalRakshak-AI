"""Abstract Base Dispatcher interface for JalRakshak AI."""

from abc import ABC, abstractmethod
from typing import List
from ..models.assignment import Assignment


class BaseDispatcher(ABC):
    """Abstract interface that all dispatch strategies must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable strategy name."""
        pass

    @abstractmethod
    def dispatch(self, world_state) -> List[Assignment]:
        """
        Evaluate world state, match pending incidents with feasible boats and shelters,
        and commit safe assignments. Returns newly committed assignments.
        """
        pass
