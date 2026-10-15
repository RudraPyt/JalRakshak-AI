"""Incident Agent representing an emergency request."""

from typing import Optional
from ..models.incident import Incident
from ..models.agent import TaskAnnouncement, ContractAward
from ..models.enums import UrgencyLevel, IncidentLifecycleStatus, VerificationStatus


class IncidentAgent:
    """Autonomous agent representing a specific reported emergency incident."""

    def __init__(self, incident: Incident):
        self.incident = incident
        self.active_announcement: Optional[TaskAnnouncement] = None

    @property
    def incident_id(self) -> str:
        return self.incident.incident_id

    @property
    def zone(self) -> str:
        return self.incident.zone

    @property
    def people_awaiting_pickup(self) -> int:
        return self.incident.people_awaiting_pickup

    def compute_local_priority(self, current_minute: int) -> float:
        """
        Calculate the incident's subjective urgency and priority score.
        Incorporates base urgency, waiting time to prevent starvation, and source confidence.
        """
        base_urgency = self.incident.reported_urgency.priority_weight
        elapsed = self.incident.report_age_min + max(0, current_minute - self.incident.reported_at_minute)
        waiting_bonus = min(50.0, 1.5 * elapsed)

        ver_weights = {
            VerificationStatus.VERIFIED: 1.0,
            VerificationStatus.REPORTED: 0.9,
            VerificationStatus.POSSIBLE_DUPLICATE: 0.7,
            VerificationStatus.UNVERIFIED: 0.6,
            VerificationStatus.DUPLICATE_RESOLVED: 0.5,
        }
        ver_factor = ver_weights.get(self.incident.verification_status, 0.8)
        priority = (base_urgency + waiting_bonus) * self.incident.source_confidence * ver_factor
        return round(priority, 2)

    def announce_task(self, current_minute: int) -> Optional[TaskAnnouncement]:
        """Formulate a Call for Proposals (CFP) if assistance is needed."""
        if self.people_awaiting_pickup <= 0 or self.incident.assigned_boat_id is not None:
            return None

        priority = self.compute_local_priority(current_minute)
        self.active_announcement = TaskAnnouncement(
            announcement_id=f"CFP-{self.incident_id}-{current_minute}",
            incident_id=self.incident_id,
            zone=self.zone,
            people_in_distress=self.people_awaiting_pickup,
            urgency=self.incident.reported_urgency,
            priority_score=priority,
            timestamp_min=current_minute,
        )
        return self.active_announcement

    def receive_award(self, award: ContractAward) -> None:
        """Process a confirmed rescue contract award from the coordinator."""
        self.incident.assigned_boat_id = award.boat_id
        self.incident.assigned_shelter_id = award.shelter_id
        self.incident.lifecycle_status = IncidentLifecycleStatus.ASSIGNED
        self.incident.status_explanation = f"Contract awarded to boat {award.boat_id} for shelter {award.shelter_id}"
        self.active_announcement = None

    def receive_rejection(self, reason: str) -> None:
        """Handle situation where no feasible bids were committed."""
        if "shelter capacity" in reason.lower():
            self.incident.lifecycle_status = IncidentLifecycleStatus.UNMET_SHELTER_BOTTLENECK
        elif "no open route" in reason.lower():
            self.incident.lifecycle_status = IncidentLifecycleStatus.UNREACHABLE
        self.incident.status_explanation = reason
        self.active_announcement = None

    def receive_invalidation(self, reason: str) -> None:
        """Handle commitment cancellation due to environmental changes."""
        if self.incident.people_onboard == 0:
            self.incident.assigned_boat_id = None
            self.incident.assigned_shelter_id = None
            self.incident.lifecycle_status = IncidentLifecycleStatus.PENDING_ASSIGNMENT
        self.incident.status_explanation = f"Assignment invalidated: {reason}. Awaiting renegotiation."
        self.active_announcement = None
