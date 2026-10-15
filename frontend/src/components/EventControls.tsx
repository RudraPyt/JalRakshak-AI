import React, { useState, useEffect } from 'react';
import {
  Sliders,
  Flame,
  CheckCircle2,
  XCircle,
  Send,
  Zap,
} from 'lucide-react';
import type {
  EventType,
  EventInjectRequest,
  ScenarioEvent,
  NetworkEdge,
  Boat,
  Shelter,
} from '../types';
import { api } from '../services/api';


interface EventControlsProps {
  currentMinute: number;
  edges: NetworkEdge[];
  boats: Boat[];
  shelters: Shelter[];
  onEventApplied: () => void;
}

export const EventControls: React.FC<EventControlsProps> = ({
  currentMinute,
  edges,
  boats,
  shelters,
  onEventApplied,
}) => {
  const [eventType, setEventType] = useState<EventType>('road_closure');
  const [targetId, setTargetId] = useState<string>('N2');
  const [description, setDescription] = useState<string>('Submerged under swift flood currents');
  const [confidence, setConfidence] = useState<string>('high');
  const [targetMinute, setTargetMinute] = useState<number | ''>('');
  
  const [eventsList, setEventsList] = useState<ScenarioEvent[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<{ status: 'success' | 'error'; message: string } | null>(null);

  // Fetch events list
  const fetchEvents = async () => {
    try {
      const list = await api.getEvents();
      setEventsList(list);
    } catch (err) {
      console.error('Failed to load events:', err);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [currentMinute]);

  // Adjust default target options when event type changes
  const handleTypeChange = (type: EventType) => {
    setEventType(type);
    if (type === 'road_closure' || type === 'road_reopen') {
      setTargetId(edges[0]?.edge_id || 'N2');
      setDescription(type === 'road_closure' ? 'Flash flood water washed over bridge deck' : 'Debris cleared, route restored');
    } else if (type === 'boat_failure') {
      setTargetId(boats[0]?.boat_id || 'BOAT03');
      setDescription('Engine fouled by submerged storm debris');
    } else if (type === 'shelter_overflow') {
      setTargetId(shelters[0]?.shelter_id || 'SH02');
      setDescription('Unscheduled walk-in flood refugees filled remaining capacity');
    } else if (type === 'conflicting_report') {
      setTargetId('INC010');
      setDescription('Conflicting caller report claiming higher trapped headcount');
    }
  };

  // Submit manual event injection
  const handleInject = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setFeedback(null);

    const payload: EventInjectRequest = {
      event_type: eventType,
      target_id: targetId,
      description,
      source_confidence: confidence,
      simulation_minute: targetMinute === '' ? undefined : Number(targetMinute),
    };

    try {
      const res = await api.injectEvent(payload);
      setFeedback({
        status: res.applied ? 'success' : 'error',
        message: res.message,
      });
      fetchEvents();
      onEventApplied();
    } catch (err: any) {
      setFeedback({
        status: 'error',
        message: err.message || 'Failed to inject scenario event',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Simultaneous Stretch Challenge Trigger
  const handleStretchChallenge = async () => {
    setIsSubmitting(true);
    setFeedback(null);
    try {
      // Inject the 3 simultaneous stretch events:
      // 1. Road Closure: Bridge N2
      // 2. Boat Failure: BOAT03
      // 3. Shelter Overflow: SH02
      await api.injectEvent({
        event_type: 'road_closure',
        target_id: 'N2',
        description: 'STRETCH CHALLENGE: LowBridge washed out by rapid surge',
        simulation_minute: currentMinute,
      });
      await api.injectEvent({
        event_type: 'boat_failure',
        target_id: 'BOAT03',
        description: 'STRETCH CHALLENGE: High-capacity BOAT03 propeller failure',
        simulation_minute: currentMinute,
      });
      await api.injectEvent({
        event_type: 'shelter_overflow',
        target_id: 'SH02',
        description: 'STRETCH CHALLENGE: SH02 overflowed by sudden influx',
        simulation_minute: currentMinute,
      });

      setFeedback({
        status: 'success',
        message: 'Simultaneous Stretch Challenge injected! (N2 Bridge + BOAT03 Failure + SH02 Overflow). Observe adaptive rerouting and replanning in the next steps.',
      });
      fetchEvents();
      onEventApplied();
    } catch (err: any) {
      setFeedback({
        status: 'error',
        message: `Stretch challenge injection error: ${err.message}`,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
      {/* 1. Manual Event Injection Card */}
      <div className="glass-panel" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
          <Sliders size={18} color="var(--cyan-bright)" />
          <h2 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>
            Dynamic Scenario Event Injection
          </h2>
        </div>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
          Inject road disruptions, mechanical failures, and shelter bottlenecks into the active simulation to test replanning resiliency.
        </p>

        {feedback && (
          <div
            style={{
              padding: '0.65rem 0.85rem',
              borderRadius: '8px',
              fontSize: '0.775rem',
              marginBottom: '1rem',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '0.5rem',
              background: feedback.status === 'success' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)',
              border: feedback.status === 'success' ? '1px solid var(--emerald-safe)' : '1px solid var(--rose-crit)',
              color: feedback.status === 'success' ? '#a7f3d0' : '#fda4af',
            }}
          >
            {feedback.status === 'success' ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
            <span>{feedback.message}</span>
          </div>
        )}

        <form onSubmit={handleInject} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {/* Event Type */}
          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>
              Event Type
            </label>
            <select
              value={eventType}
              onChange={(e) => handleTypeChange(e.target.value as EventType)}
              style={{
                width: '100%',
                padding: '0.45rem 0.65rem',
                fontSize: '0.8rem',
                borderRadius: '6px',
                border: '1px solid var(--border-subtle)',
                background: 'var(--bg-input)',
                color: 'var(--text-main)',
                outline: 'none',
              }}
            >
              <option value="road_closure">Road / Waterway Closure</option>
              <option value="boat_failure">Boat Mechanical Breakdown</option>
              <option value="shelter_overflow">Shelter Capacity Overflow</option>
              <option value="conflicting_report">Conflicting Incident Report</option>
              <option value="road_reopen">Road / Bridge Reopening</option>
            </select>
          </div>

          {/* Target Selector */}
          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>
              Target Entity
            </label>
            {(eventType === 'road_closure' || eventType === 'road_reopen') && (
              <select
                value={targetId}
                onChange={(e) => setTargetId(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.45rem 0.65rem',
                  fontSize: '0.8rem',
                  borderRadius: '6px',
                  border: '1px solid var(--border-subtle)',
                  background: 'var(--bg-input)',
                  color: 'var(--text-main)',
                  outline: 'none',
                }}
              >
                {edges.map((e) => (
                  <option key={e.edge_id} value={e.edge_id}>
                    {e.edge_id}: {e.from_zone} ↔ {e.to_zone} ({e.status})
                  </option>
                ))}
              </select>
            )}

            {eventType === 'boat_failure' && (
              <select
                value={targetId}
                onChange={(e) => setTargetId(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.45rem 0.65rem',
                  fontSize: '0.8rem',
                  borderRadius: '6px',
                  border: '1px solid var(--border-subtle)',
                  background: 'var(--bg-input)',
                  color: 'var(--text-main)',
                  outline: 'none',
                }}
              >
                {boats.map((b) => (
                  <option key={b.boat_id} value={b.boat_id}>
                    {b.boat_id} ({b.status}, cap: {b.capacity_people})
                  </option>
                ))}
              </select>
            )}

            {eventType === 'shelter_overflow' && (
              <select
                value={targetId}
                onChange={(e) => setTargetId(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.45rem 0.65rem',
                  fontSize: '0.8rem',
                  borderRadius: '6px',
                  border: '1px solid var(--border-subtle)',
                  background: 'var(--bg-input)',
                  color: 'var(--text-main)',
                  outline: 'none',
                }}
              >
                {shelters.map((s) => (
                  <option key={s.shelter_id} value={s.shelter_id}>
                    {s.shelter_id} — {s.name} (cap: {s.capacity_people})
                  </option>
                ))}
              </select>
            )}

            {eventType === 'conflicting_report' && (
              <input
                type="text"
                value={targetId}
                onChange={(e) => setTargetId(e.target.value)}
                placeholder="Incident ID (e.g. INC010)"
                style={{
                  width: '100%',
                  padding: '0.45rem 0.65rem',
                  fontSize: '0.8rem',
                  borderRadius: '6px',
                  border: '1px solid var(--border-subtle)',
                  background: 'var(--bg-input)',
                  color: 'var(--text-main)',
                  outline: 'none',
                }}
              />
            )}
          </div>

          {/* Description */}
          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>
              Operational Reason / Description
            </label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '0.45rem 0.65rem',
                fontSize: '0.8rem',
                borderRadius: '6px',
                border: '1px solid var(--border-subtle)',
                background: 'var(--bg-input)',
                color: 'var(--text-main)',
                outline: 'none',
              }}
            />
          </div>

          {/* Timing & Confidence */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>
                Trigger Minute
              </label>
              <input
                type="number"
                min="0"
                placeholder={`Now (${currentMinute})`}
                value={targetMinute}
                onChange={(e) => setTargetMinute(e.target.value === '' ? '' : Number(e.target.value))}
                style={{
                  width: '100%',
                  padding: '0.45rem 0.65rem',
                  fontSize: '0.8rem',
                  borderRadius: '6px',
                  border: '1px solid var(--border-subtle)',
                  background: 'var(--bg-input)',
                  color: 'var(--text-main)',
                  outline: 'none',
                }}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>
                Confidence
              </label>
              <select
                value={confidence}
                onChange={(e) => setConfidence(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.45rem 0.65rem',
                  fontSize: '0.8rem',
                  borderRadius: '6px',
                  border: '1px solid var(--border-subtle)',
                  background: 'var(--bg-input)',
                  color: 'var(--text-main)',
                  outline: 'none',
                }}
              >
                <option value="high">High (0.95)</option>
                <option value="medium">Medium (0.75)</option>
                <option value="low">Low (0.50)</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={isSubmitting}
            style={{ marginTop: '0.5rem' }}
          >
            <Send size={15} />
            Inject Scenario Event
          </button>
        </form>
      </div>

      {/* 2. Simultaneous Stretch Challenge Card */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div
          className="glass-panel"
          style={{
            padding: '1.25rem',
            border: '1px solid rgba(244, 63, 94, 0.4)',
            background: 'linear-gradient(135deg, rgba(244, 63, 94, 0.08) 0%, var(--bg-card) 100%)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <Zap size={18} color="var(--rose-crit)" />
            <h2 style={{ fontSize: '1rem', fontWeight: 700, color: '#fca5a5' }}>
              Simultaneous-Failure Stretch Challenge
            </h2>
          </div>
          <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)', marginBottom: '0.85rem', lineHeight: '1.45' }}>
            Stress tests system resiliency by executing a multi-point cascading catastrophe at the current simulation minute:
          </p>

          <ul style={{ fontSize: '0.75rem', color: 'var(--text-main)', paddingLeft: '1.25rem', marginBottom: '1rem', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            <li><strong>Bridge N2 Cut Off:</strong> LowBridge route severed; boats must reroute via EastColony/ClinicQuarter.</li>
            <li><strong>BOAT03 Mechanical Breakdown:</strong> High-capacity 10-person vessel stalled with invalidation of active contracts.</li>
            <li><strong>SH02 Shelter Overflow:</strong> CommunityHall fully exhausted, forcing evacuees to redirect to remaining shelters.</li>
          </ul>

          <button
            className="btn btn-danger"
            onClick={handleStretchChallenge}
            disabled={isSubmitting}
            style={{ width: '100%', padding: '0.65rem' }}
          >
            <Flame size={16} />
            Trigger Simultaneous Stretch Challenge
          </button>
        </div>

        {/* 3. Event Timeline List */}
        <div className="glass-panel" style={{ padding: '1rem', flex: 1, display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <h3 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)' }}>
              Scenario Event Log ({eventsList.length})
            </h3>
            <span style={{ fontSize: '0.725rem', color: 'var(--text-dim)' }}>
              Clock: T+{currentMinute}m
            </span>
          </div>

          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.4rem', maxHeight: '200px' }}>
            {eventsList.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '1rem', color: 'var(--text-dim)', fontSize: '0.75rem' }}>
                No scenario events logged.
              </div>
            ) : (
              eventsList.map((ev) => (
                <div
                  key={ev.event_id}
                  style={{
                    padding: '0.45rem 0.65rem',
                    borderRadius: '6px',
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-subtle)',
                    fontSize: '0.75rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <span className="mono" style={{ fontWeight: 700, color: 'var(--cyan-bright)' }}>
                        T+{ev.simulation_minute}m
                      </span>
                      <span className="status-badge status-badge-low" style={{ fontSize: '0.65rem' }}>
                        {ev.event_type}
                      </span>
                      <span className="mono" style={{ color: '#fff' }}>{ev.target_id}</span>
                    </div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem', marginTop: '0.15rem' }}>
                      {ev.description}
                    </div>
                  </div>

                  <span
                    className={`status-badge ${ev.applied ? 'status-badge-safe' : 'status-badge-high'}`}
                    style={{ fontSize: '0.65rem' }}
                  >
                    {ev.applied ? 'Applied' : 'Pending'}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
