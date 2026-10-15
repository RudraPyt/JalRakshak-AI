"""Multi-Agent Strategy Dispatcher for JalRakshak AI."""

from typing import Dict, List
from .base import BaseDispatcher
from ..models.assignment import Assignment
from ..agents.incident_agent import IncidentAgent
from ..agents.boat_agent import BoatAgent
from ..agents.route_agent import RouteAgent
from ..agents.shelter_agent import ShelterAgent
from ..agents.coordinator import CoordinatorAgent


class MultiAgentDispatcher(BaseDispatcher):
    """
    Decentralized dispatch strategy utilizing the Contract Net Protocol (CNP)
    where independent agents for Incidents, Boats, Shelters, and Routes negotiate
    feasible commitments facilitated by a Coordinator Agent.
    """

    def __init__(self, fairness_weight: float = 5.0):
        self.coordinator = CoordinatorAgent(fairness_weight=fairness_weight)
        self.route_agent: RouteAgent = None  # type: ignore
        self.boat_agents: Dict[str, BoatAgent] = {}
        self.shelter_agents: Dict[str, ShelterAgent] = {}
        self.incident_agents: Dict[str, IncidentAgent] = {}

    @property
    def name(self) -> str:
        return "Decentralized Multi-Agent Strategy (CNP)"

    def _sync_agents(self, world_state) -> None:
        """Synchronize autonomous agents with the authoritative world state."""
        if self.route_agent is None or self.route_agent.router != world_state.router:
            self.route_agent = RouteAgent(world_state.router)

        # Sync Boat Agents
        for bid, boat in world_state.boats.items():
            if bid not in self.boat_agents:
                self.boat_agents[bid] = BoatAgent(boat)
            else:
                self.boat_agents[bid].boat = boat

        # Sync Shelter Agents
        for sid, shelter in world_state.shelters.items():
            if sid not in self.shelter_agents:
                self.shelter_agents[sid] = ShelterAgent(shelter)
            else:
                self.shelter_agents[sid].shelter = shelter

        # Sync Incident Agents
        for iid, incident in world_state.incidents.items():
            if iid not in self.incident_agents:
                self.incident_agents[iid] = IncidentAgent(incident)
            else:
                self.incident_agents[iid].incident = incident

    def dispatch(self, world_state) -> List[Assignment]:
        """
        Execute decentralised multi-agent negotiation cycle:
        1. Sync agent instances with current world state.
        2. Facilitate negotiation via CoordinatorAgent using CNP.
        3. Return committed assignments.
        """
        self._sync_agents(world_state)

        return self.coordinator.negotiate_cycle(
            incident_agents=list(self.incident_agents.values()),
            boat_agents=list(self.boat_agents.values()),
            shelter_agents=list(self.shelter_agents.values()),
            route_agent=self.route_agent,
            world_state=world_state,
        )
