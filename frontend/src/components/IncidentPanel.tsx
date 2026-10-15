import React, { useState, useMemo } from 'react';
import {
  Search,
  AlertTriangle,
} from 'lucide-react';
import type { Incident } from '../types';


interface IncidentPanelProps {
  incidents: Incident[];
  onSelectIncident: (inc: Incident) => void;
  selectedIncidentId?: string;
}

export const IncidentPanel: React.FC<IncidentPanelProps> = ({
  incidents,
  onSelectIncident,
  selectedIncidentId,
}) => {
  const [search, setSearch] = useState('');
  const [urgencyFilter, setUrgencyFilter] = useState<'all' | 'critical' | 'high' | 'medium'>('all');
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'in_progress' | 'bottleneck' | 'resolved'>('all');

  // Filtered and searched incidents
  const filteredIncidents = useMemo(() => {
    return incidents.filter((inc) => {
      // Search
      const matchesSearch =
        inc.incident_id.toLowerCase().includes(search.toLowerCase()) ||
        inc.zone.toLowerCase().includes(search.toLowerCase());

      // Urgency filter
      const matchesUrgency = urgencyFilter === 'all' || inc.reported_urgency === urgencyFilter;

      // Status filter
      let matchesStatus = true;
      if (statusFilter === 'pending') {
        matchesStatus = inc.lifecycle_status === 'pending_assignment' || inc.lifecycle_status === 'reported';
      } else if (statusFilter === 'in_progress') {
        matchesStatus = inc.lifecycle_status === 'assigned' || inc.lifecycle_status === 'in_transit' || inc.lifecycle_status === 'partially_served';
      } else if (statusFilter === 'bottleneck') {
        matchesStatus = inc.lifecycle_status === 'unmet_shelter_bottleneck';
      } else if (statusFilter === 'resolved') {
        matchesStatus = inc.lifecycle_status === 'fully_served';
      }

      return matchesSearch && matchesUrgency && matchesStatus;
    });
  }, [incidents, search, urgencyFilter, statusFilter]);

  // Bottleneck count
  const bottleneckCount = incidents.filter((i) => i.lifecycle_status === 'unmet_shelter_bottleneck').length;

  return (
    <div className="glass-panel" style={{ padding: '1rem', height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Panel Title & Controls */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div>
          <h2 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)' }}>
            Incident Triage & Evacuation Status
          </h2>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Showing {filteredIncidents.length} of {incidents.length} emergency requests
          </span>
        </div>

        {/* Search & Urgency input */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <div style={{ position: 'relative' }}>
            <Search size={14} style={{ position: 'absolute', left: '8px', top: '9px', color: 'var(--text-dim)' }} />
            <input
              type="text"
              placeholder="Search ID/Zone..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                padding: '0.35rem 0.65rem 0.35rem 1.75rem',
                fontSize: '0.775rem',
                borderRadius: '6px',
                border: '1px solid var(--border-subtle)',
                background: 'rgba(15, 23, 42, 0.8)',
                color: 'var(--text-main)',
                outline: 'none',
                width: '130px',
              }}
            />
          </div>
          <select
            value={urgencyFilter}
            onChange={(e) => setUrgencyFilter(e.target.value as any)}
            style={{
              padding: '0.35rem 0.5rem',
              fontSize: '0.75rem',
              borderRadius: '6px',
              border: '1px solid var(--border-subtle)',
              background: 'rgba(15, 23, 42, 0.8)',
              color: 'var(--text-muted)',
              outline: 'none',
              cursor: 'pointer',
            }}
          >
            <option value="all">All Urgency</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
          </select>
        </div>
      </div>


      {/* Filter Chips */}
      <div style={{ display: 'flex', gap: '0.35rem', marginBottom: '0.75rem', flexWrap: 'wrap' }}>
        <button
          onClick={() => setStatusFilter('all')}
          style={{
            fontSize: '0.725rem',
            padding: '0.2rem 0.55rem',
            borderRadius: '4px',
            border: 'none',
            cursor: 'pointer',
            background: statusFilter === 'all' ? 'var(--cyan-bright)' : 'rgba(30, 41, 59, 0.6)',
            color: statusFilter === 'all' ? '#000' : 'var(--text-muted)',
            fontWeight: 600,
          }}
        >
          All ({incidents.length})
        </button>
        <button
          onClick={() => setStatusFilter('pending')}
          style={{
            fontSize: '0.725rem',
            padding: '0.2rem 0.55rem',
            borderRadius: '4px',
            border: 'none',
            cursor: 'pointer',
            background: statusFilter === 'pending' ? 'var(--amber-warn)' : 'rgba(30, 41, 59, 0.6)',
            color: statusFilter === 'pending' ? '#000' : 'var(--text-muted)',
            fontWeight: 600,
          }}
        >
          Pending
        </button>
        <button
          onClick={() => setStatusFilter('in_progress')}
          style={{
            fontSize: '0.725rem',
            padding: '0.2rem 0.55rem',
            borderRadius: '4px',
            border: 'none',
            cursor: 'pointer',
            background: statusFilter === 'in_progress' ? 'var(--blue-bright)' : 'rgba(30, 41, 59, 0.6)',
            color: statusFilter === 'in_progress' ? '#000' : 'var(--text-muted)',
            fontWeight: 600,
          }}
        >
          In Progress
        </button>
        <button
          onClick={() => setStatusFilter('bottleneck')}
          style={{
            fontSize: '0.725rem',
            padding: '0.2rem 0.55rem',
            borderRadius: '4px',
            border: 'none',
            cursor: 'pointer',
            background: statusFilter === 'bottleneck' ? 'var(--rose-crit)' : 'rgba(30, 41, 59, 0.6)',
            color: statusFilter === 'bottleneck' ? '#fff' : bottleneckCount > 0 ? '#fda4af' : 'var(--text-muted)',
            fontWeight: 600,
          }}
        >
          Bottlenecks ({bottleneckCount})
        </button>
        <button
          onClick={() => setStatusFilter('resolved')}
          style={{
            fontSize: '0.725rem',
            padding: '0.2rem 0.55rem',
            borderRadius: '4px',
            border: 'none',
            cursor: 'pointer',
            background: statusFilter === 'resolved' ? 'var(--emerald-safe)' : 'rgba(30, 41, 59, 0.6)',
            color: statusFilter === 'resolved' ? '#000' : 'var(--text-muted)',
            fontWeight: 600,
          }}
        >
          Resolved
        </button>
      </div>

      {/* Bottleneck Alert Banner if capacity bottleneck exists */}
      {bottleneckCount > 0 && (
        <div
          style={{
            background: 'rgba(244, 63, 94, 0.12)',
            border: '1px solid rgba(244, 63, 94, 0.35)',
            borderRadius: '6px',
            padding: '0.5rem 0.75rem',
            marginBottom: '0.75rem',
            fontSize: '0.75rem',
            color: '#fda4af',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '0.5rem',
          }}
        >
          <AlertTriangle size={15} color="var(--rose-crit)" style={{ marginTop: '2px', flexShrink: 0 }} />
          <div>
            <strong>Shelter Capacity Bottleneck:</strong> {bottleneckCount} incidents cannot be evacuated because shelter capacity is full. JalRakshak AI does not fabricate rescues or overflow shelters.
          </div>
        </div>
      )}

      {/* Incidents Table */}
      <div style={{ flex: 1, overflowY: 'auto', border: '1px solid var(--border-subtle)', borderRadius: '8px' }}>
        <table className="command-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Zone</th>
              <th>Urgency</th>
              <th>Affected</th>
              <th>Awaiting</th>
              <th>Rescued</th>
              <th>Status</th>
              <th>Boat</th>
            </tr>
          </thead>
          <tbody>
            {filteredIncidents.length === 0 ? (
              <tr>
                <td colSpan={8} style={{ textAlign: 'center', padding: '1.5rem', color: 'var(--text-dim)' }}>
                  No incidents match the active filter criteria.
                </td>
              </tr>
            ) : (
              filteredIncidents.map((inc) => {
                const isSelected = selectedIncidentId === inc.incident_id;
                const awaiting =
                  inc.people_awaiting_pickup !== undefined
                    ? inc.people_awaiting_pickup
                    : Math.max(0, inc.people_affected - inc.people_rescued - inc.people_onboard);

                return (
                  <tr
                    key={inc.incident_id}
                    onClick={() => onSelectIncident(inc)}
                    style={{
                      cursor: 'pointer',
                      background: isSelected ? 'rgba(6, 182, 212, 0.12)' : undefined,
                    }}
                  >
                    <td className="mono" style={{ fontWeight: 700, color: 'var(--cyan-bright)' }}>
                      {inc.incident_id}
                    </td>
                    <td>{inc.zone}</td>
                    <td>
                      <span
                        className={`status-badge ${
                          inc.reported_urgency === 'critical'
                            ? 'status-badge-critical'
                            : inc.reported_urgency === 'high'
                            ? 'status-badge-high'
                            : 'status-badge-medium'
                        }`}
                      >
                        {inc.reported_urgency}
                      </span>
                    </td>
                    <td className="mono" style={{ fontWeight: 600 }}>
                      {inc.people_affected}
                    </td>
                    <td
                      className="mono"
                      style={{
                        fontWeight: 700,
                        color: awaiting > 0 ? 'var(--amber-warn)' : 'var(--text-dim)',
                      }}
                    >
                      {awaiting}
                    </td>
                    <td
                      className="mono"
                      style={{
                        fontWeight: 600,
                        color: inc.people_rescued > 0 ? 'var(--emerald-safe)' : 'var(--text-dim)',
                      }}
                    >
                      {inc.people_rescued}
                    </td>
                    <td>
                      <span
                        className={`status-badge ${
                          inc.lifecycle_status === 'fully_served'
                            ? 'status-badge-safe'
                            : inc.lifecycle_status === 'unmet_shelter_bottleneck'
                            ? 'status-badge-critical'
                            : inc.lifecycle_status === 'assigned' || inc.lifecycle_status === 'in_transit'
                            ? 'status-badge-cyan'
                            : 'status-badge-low'
                        }`}
                        style={{ fontSize: '0.675rem' }}
                      >
                        {inc.lifecycle_status === 'unmet_shelter_bottleneck'
                          ? 'Bottleneck'
                          : inc.lifecycle_status.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="mono" style={{ fontSize: '0.75rem', color: inc.assigned_boat_id ? 'var(--text-main)' : 'var(--text-dim)' }}>
                      {inc.assigned_boat_id || '—'}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
