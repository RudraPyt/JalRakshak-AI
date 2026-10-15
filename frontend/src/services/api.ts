/**
 * API Service for JalRakshak AI Command Center.
 * Connects to FastAPI backend with full error handling and configuration.
 */

import type {
  SimulationStateResponse,
  SimulationStepResponse,
  ScenarioEvent,
  EventInjectRequest,
  EventInjectResponse,
  ReplayTimelineResponse,
  ReplaySnapshot,
  LogsResponse,
  ComparisonReport,
  StrategyMetrics,
} from '../types';


const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = `HTTP ${res.status}: ${res.statusText}`;
    try {
      const body = await res.json();
      if (body.detail) {
        errorDetail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail);
      }
    } catch {
      // Ignore json parse error on error response
    }
    throw new Error(errorDetail);
  }
  return res.json();
}

export const api = {
  // System Health
  async getHealth(): Promise<{ status: string; version: string; service: string }> {
    const res = await fetch(`${BASE_URL}/health`);
    return handleResponse(res);
  },

  // Simulation Controls & State
  async getSimulationState(): Promise<SimulationStateResponse> {
    const res = await fetch(`${BASE_URL}/api/simulation/state`);
    return handleResponse<SimulationStateResponse>(res);
  },

  async stepSimulation(): Promise<SimulationStepResponse> {
    const res = await fetch(`${BASE_URL}/api/simulation/step`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    return handleResponse<SimulationStepResponse>(res);
  },

  async resetSimulation(strategy: 'centralized' | 'multi_agent'): Promise<SimulationStateResponse> {
    const res = await fetch(`${BASE_URL}/api/simulation/reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ strategy }),
    });
    return handleResponse<SimulationStateResponse>(res);
  },

  async pauseSimulation(): Promise<{ status: string; minute: number; is_running: boolean }> {
    const res = await fetch(`${BASE_URL}/api/simulation/pause`, {
      method: 'POST',
    });
    return handleResponse(res);
  },

  async resumeSimulation(): Promise<{ status: string; minute: number; is_running: boolean }> {
    const res = await fetch(`${BASE_URL}/api/simulation/resume`, {
      method: 'POST',
    });
    return handleResponse(res);
  },

  // Dynamic Scenario Events
  async getEvents(): Promise<ScenarioEvent[]> {
    const res = await fetch(`${BASE_URL}/api/events`);
    return handleResponse<ScenarioEvent[]>(res);
  },

  async injectEvent(payload: EventInjectRequest): Promise<EventInjectResponse> {
    const res = await fetch(`${BASE_URL}/api/events/inject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<EventInjectResponse>(res);
  },

  // Decision & Audit Logs
  async getDecisionLogs(params?: {
    action_type?: string;
    entity_id?: string;
    limit?: number;
    offset?: number;
  }): Promise<LogsResponse> {
    const url = new URL(`${BASE_URL}/api/logs/decisions`);
    if (params?.action_type) url.searchParams.set('action_type', params.action_type);
    if (params?.entity_id) url.searchParams.set('entity_id', params.entity_id);
    if (params?.limit) url.searchParams.set('limit', params.limit.toString());
    if (params?.offset !== undefined) url.searchParams.set('offset', params.offset.toString());

    const res = await fetch(url.toString());
    return handleResponse<LogsResponse>(res);
  },

  // After-Action Replay
  async getReplayTimeline(): Promise<ReplayTimelineResponse> {
    const res = await fetch(`${BASE_URL}/api/replay/timeline`);
    return handleResponse<ReplayTimelineResponse>(res);
  },

  async getReplaySnapshot(minute: number): Promise<ReplaySnapshot> {
    const res = await fetch(`${BASE_URL}/api/replay/snapshot/${minute}`);
    return handleResponse<ReplaySnapshot>(res);
  },

  // Evaluation & Strategy Comparison
  async getCurrentEvaluation(): Promise<StrategyMetrics> {
    const res = await fetch(`${BASE_URL}/api/evaluation/current`);
    return handleResponse<StrategyMetrics>(res);
  },

  async compareStrategies(simulationMinutes = 15, includeStretch = false): Promise<ComparisonReport> {
    const res = await fetch(`${BASE_URL}/api/evaluation/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        simulation_minutes: simulationMinutes,
        include_stretch_events: includeStretch,
      }),
    });
    return handleResponse<ComparisonReport>(res);
  },

  async runStretchChallenge(): Promise<ComparisonReport> {
    const res = await fetch(`${BASE_URL}/api/evaluation/stretch-challenge`, {
      method: 'POST',
    });
    return handleResponse<ComparisonReport>(res);
  },
};
