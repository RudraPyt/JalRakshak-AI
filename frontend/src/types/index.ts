/**
 * TypeScript definitions for JalRakshak AI — Flood Rescue Command Center.
 * Aligned strictly with FastAPI backend Pydantic models.
 */

export type UrgencyLevel = 'critical' | 'high' | 'medium' | 'low';

export type VerificationStatus =
  | 'verified'
  | 'reported'
  | 'unverified'
  | 'possible_duplicate'
  | 'duplicate_resolved';

export type IncidentLifecycleStatus =
  | 'reported'
  | 'awaiting_assessment'
  | 'pending_assignment'
  | 'assigned'
  | 'in_transit'
  | 'partially_served'
  | 'fully_served'
  | 'unreachable'
  | 'unmet_shelter_bottleneck'
  | 'cancelled';

export type BoatStatus =
  | 'available'
  | 'in_transit'
  | 'servicing'
  | 'failed'
  | 'maintenance';

export type ShelterStatus = 'open' | 'full' | 'closed';

export type EdgeStatus = 'open' | 'closed' | 'uncertain';

export type EventType =
  | 'road_closure'
  | 'boat_failure'
  | 'shelter_overflow'
  | 'conflicting_report'
  | 'road_reopen';

export type ActionType =
  | 'PROPOSAL'
  | 'BID_SUBMITTED'
  | 'BID_ACCEPTED'
  | 'BID_REJECTED'
  | 'COMMITTED'
  | 'INVALIDATED'
  | 'REROUTED'
  | 'REASSIGNED'
  | 'PASSENGERS_LOADED'
  | 'PASSENGERS_DELIVERED'
  | 'SERVED'
  | 'FAILED'
  | 'ABORTED';

export interface ZoneNode {
  zone_id: string;
  x: number;
  y: number;
  description?: string;
}

export interface NetworkEdge {
  edge_id: string;
  from_zone: string;
  to_zone: string;
  distance_units: number;
  travel_time_min: number;
  status: EdgeStatus;
  uncertainty: number;
  closure_reason?: string;
}

export interface Boat {
  boat_id: string;
  current_zone: string;
  x: number;
  y: number;
  capacity_people: number;
  speed_units_per_min: number;
  status: BoatStatus;
  safety_factor: number;
  onboard_people: number;
  assigned_incident_id?: string;
  target_shelter_id?: string;
  planned_route_zones: string[];
  failed_until_minute?: number;
  failure_reason?: string;
  total_idle_minutes: number;
  total_service_minutes: number;
}

export interface Shelter {
  shelter_id: string;
  name: string;
  zone_id: string;
  x: number;
  y: number;
  capacity_people: number;
  current_occupancy: number;
  reserved_capacity: number;
  status: ShelterStatus;
  remaining_capacity?: number;
}

export interface Incident {
  incident_id: string;
  zone: string;
  x: number;
  y: number;
  people_affected: number;
  people_rescued: number;
  people_onboard: number;
  people_awaiting_pickup?: number;
  report_age_min: number;
  reported_urgency: UrgencyLevel;
  source_confidence: number;
  verification_status: VerificationStatus;
  lifecycle_status: IncidentLifecycleStatus;
  assigned_boat_id?: string;
  assigned_shelter_id?: string;
  reported_at_minute: number;
  served_at_minute?: number;
  status_explanation?: string;
}

export interface Assignment {
  assignment_id: string;
  boat_id: string;
  incident_id: string;
  shelter_id: string;
  people_allocated: number;
  created_at_minute: number;
  route_zones: string[];
  status: string;
  is_active: boolean;
}

export interface DecisionLogEntry {
  entry_id: string;
  timestamp_min: number;
  action_type: ActionType;
  entity_id: string;
  target_id?: string;
  rule_applied: string;
  explanation: string;
  previous_state?: string;
  new_state?: string;
}

export interface SimulationKPIs {
  total_people_affected?: number;
  people_rescued_to_shelters?: number;
  people_onboard_boats?: number;
  people_awaiting_pickup?: number;
  incidents_fully_served?: number;
  incidents_partially_served?: number;
  incidents_unserved?: number;
  boats_active?: number;
  boats_failed?: number;
  shelter_total_capacity?: number;
  shelter_current_occupancy?: number;
  shelter_remaining_capacity?: number;

  total_affected_people?: number;
  total_delivered_people?: number;
  total_onboard_people?: number;
  total_awaiting_people?: number;
  delivery_rate_pct?: number;
  active_boats_count?: number;
  total_boats_count?: number;
  shelter_occupancy_total?: number;
  shelter_capacity_total?: number;
  shelter_remaining_total?: number;
  unmet_incidents_count?: number;
  invariant_violations_count?: number;
}


export interface SimulationStateResponse {
  minute: int;
  strategy: 'centralized' | 'multi_agent';
  is_running: boolean;
  kpis: SimulationKPIs;
  zones: ZoneNode[];
  edges: NetworkEdge[];
  boats: Boat[];
  shelters: Shelter[];
  incidents: Incident[];
  active_assignments: Assignment[];
}

export type int = number;

export interface SimulationStepResponse {
  minute: number;
  strategy: string;
  is_running: boolean;
  active_assignments_count: number;
  newly_invalidated_count: number;
  kpis: SimulationKPIs;
  invariants_passed: boolean;
  invariant_violations: string[];
}

export interface ScenarioEvent {
  event_id: string;
  simulation_minute: number;
  event_type: EventType;
  target_id: string;
  description: string;
  source_confidence: string;
  applied: boolean;
  applied_at_minute?: number;
}

export interface EventInjectRequest {
  event_type: EventType;
  target_id: string;
  description: string;
  simulation_minute?: number;
  source_confidence?: string;
}

export interface EventInjectResponse {
  event_id: string;
  event_type: EventType;
  target_id: string;
  simulation_minute: number;
  applied: boolean;
  message: string;
}

export interface ReplayTimelineResponse {
  total_snapshots: number;
  recorded_minutes: number[];
  active_strategy: string;
}

export interface ReplaySnapshot {
  minute: number;
  strategy: string;
  kpis: SimulationKPIs;
  boats: Boat[];
  shelters: Shelter[];
  incidents: Incident[];
  edges: NetworkEdge[];
  assignments: Assignment[];
  invariants_ok: boolean;
}

export interface StrategyMetrics {
  strategy_name: string;
  total_delivered_people: number;
  total_onboard_people: number;
  total_stranded_people: number;
  delivery_rate_pct: number;
  unmet_requests_count: number;
  unmet_requests_pct: number;
  mean_time_to_service_min: number;
  total_boat_idle_minutes: number;
  total_boat_service_minutes: number;
  fleet_idle_ratio_pct: number;
  route_violations_detected: number;
  neighbourhood_fairness_jains_index: number;
  neighbourhood_service_rates: Record<string, number>;
  failure_recovery_time_min: number;
}

export interface ComparisonReport {
  evaluation_minutes: number;
  stretch_challenge_evaluated: boolean;
  centralized: StrategyMetrics;
  multi_agent: StrategyMetrics;
  summary_observations: string[];
}

export interface LogsResponse {
  total_count: number;
  returned_count: number;
  logs: DecisionLogEntry[];
}
