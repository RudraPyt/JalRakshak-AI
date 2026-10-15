"""Enumeration definitions for JalRakshak AI."""

from enum import Enum


class UrgencyLevel(str, Enum):
    """Urgency level reported for an incident."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @property
    def priority_weight(self) -> int:
        """Numerical priority for triage ordering (higher is more urgent)."""
        weights = {
            UrgencyLevel.CRITICAL: 100,
            UrgencyLevel.HIGH: 75,
            UrgencyLevel.MEDIUM: 50,
            UrgencyLevel.LOW: 25,
        }
        return weights[self]


class VerificationStatus(str, Enum):
    """Verification status of an incident report."""
    VERIFIED = "verified"
    REPORTED = "reported"
    UNVERIFIED = "unverified"
    POSSIBLE_DUPLICATE = "possible_duplicate"
    DUPLICATE_RESOLVED = "duplicate_resolved"


class IncidentLifecycleStatus(str, Enum):
    """Lifecycle stages of an incident from report to full resolution."""
    REPORTED = "reported"
    AWAITING_ASSESSMENT = "awaiting_assessment"
    PENDING_ASSIGNMENT = "pending_assignment"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    PARTIALLY_SERVED = "partially_served"
    FULLY_SERVED = "fully_served"
    UNREACHABLE = "unreachable"
    UNMET_SHELTER_BOTTLENECK = "unmet_shelter_bottleneck"
    CANCELLED = "cancelled"


class BoatStatus(str, Enum):
    """Operational status of a rescue boat resource."""
    AVAILABLE = "available"
    IN_TRANSIT = "in_transit"
    SERVICING = "servicing"
    FAILED = "failed"
    MAINTENANCE = "maintenance"


class ShelterStatus(str, Enum):
    """Status of an evacuation shelter."""
    OPEN = "open"
    FULL = "full"
    CLOSED = "closed"


class EdgeStatus(str, Enum):
    """Accessibility status of a graph connection / road-water edge."""
    OPEN = "open"
    CLOSED = "closed"
    UNCERTAIN = "uncertain"


class EventType(str, Enum):
    """Types of dynamic scenario events injected into the simulation."""
    ROAD_CLOSURE = "road_closure"
    BOAT_FAILURE = "boat_failure"
    SHELTER_OVERFLOW = "shelter_overflow"
    CONFLICTING_REPORT = "conflicting_report"
    ROAD_REOPEN = "road_reopen"


class ActionType(str, Enum):
    """Action categories for explainable decision logging."""
    PROPOSAL = "PROPOSAL"
    BID_SUBMITTED = "BID_SUBMITTED"
    BID_ACCEPTED = "BID_ACCEPTED"
    BID_REJECTED = "BID_REJECTED"
    COMMITTED = "COMMITTED"
    INVALIDATED = "INVALIDATED"
    REROUTED = "REROUTED"
    REASSIGNED = "REASSIGNED"
    PASSENGERS_LOADED = "PASSENGERS_LOADED"
    PASSENGERS_DELIVERED = "PASSENGERS_DELIVERED"
    SERVED = "SERVED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"
