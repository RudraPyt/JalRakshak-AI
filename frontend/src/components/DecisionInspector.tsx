import React, { useState, useEffect } from 'react';
import {
  Radio,
  Search,
  RefreshCw,
} from 'lucide-react';
import type { DecisionLogEntry, ActionType } from '../types';
import { api } from '../services/api';


interface DecisionInspectorProps {
  currentMinute: number;
}

export const DecisionInspector: React.FC<DecisionInspectorProps> = ({ currentMinute }) => {
  const [logs, setLogs] = useState<DecisionLogEntry[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [actionFilter, setActionFilter] = useState<string>('');
  const [entityFilter, setEntityFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await api.getDecisionLogs({
        action_type: actionFilter ? actionFilter : undefined,
        entity_id: entityFilter ? entityFilter : undefined,
        limit: 100,
        offset: 0,
      });
      setLogs(res.logs);
      setTotalCount(res.total_count);
    } catch (err) {
      console.error('Failed to load decision logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [currentMinute, actionFilter, entityFilter]);

  // Filter logs by text search
  const displayedLogs = logs.filter((log) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      log.entity_id.toLowerCase().includes(q) ||
      log.rule_applied.toLowerCase().includes(q) ||
      log.explanation.toLowerCase().includes(q) ||
      (log.target_id && log.target_id.toLowerCase().includes(q))
    );
  });

  const getActionBadge = (action: ActionType) => {
    switch (action) {
      case 'PROPOSAL':
        return <span className="status-badge status-badge-purple">Task Announcement</span>;
      case 'BID_SUBMITTED':
        return <span className="status-badge status-badge-cyan">Boat Bid</span>;
      case 'BID_ACCEPTED':
      case 'COMMITTED':
        return <span className="status-badge status-badge-safe">Award / Commitment</span>;
      case 'BID_REJECTED':
        return <span className="status-badge status-badge-critical">Bid Rejected</span>;
      case 'INVALIDATED':
      case 'FAILED':
        return <span className="status-badge status-badge-critical">Invalidated</span>;
      case 'REROUTED':
      case 'REASSIGNED':
        return <span className="status-badge status-badge-high">Rerouted / Replanned</span>;
      case 'PASSENGERS_LOADED':
        return <span className="status-badge status-badge-cyan">Loaded Pax</span>;
      case 'PASSENGERS_DELIVERED':
      case 'SERVED':
        return <span className="status-badge status-badge-safe">Delivered Safe</span>;
      default:
        return <span className="status-badge status-badge-low">{action}</span>;
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '1.25rem', height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header & Description */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Radio size={18} color="var(--purple-agent)" />
            <h2 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>
              Live Multi-Agent Negotiation & Decision Inspector
            </h2>
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Authoritative Contract Net Protocol audit trail from backend execution ({totalCount} entries recorded). Zero hardcoded mock data.
          </p>

        </div>

        <button
          className="btn btn-secondary"
          onClick={fetchLogs}
          disabled={loading}
          style={{ padding: '0.35rem 0.65rem' }}
        >
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          Refresh Feed
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.85rem', flexWrap: 'wrap' }}>
        {/* Search */}
        <div style={{ position: 'relative', flex: 1, minWidth: '180px' }}>
          <Search size={14} style={{ position: 'absolute', left: '8px', top: '9px', color: 'var(--text-dim)' }} />
          <input
            type="text"
            placeholder="Search decisions, rules, entities..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '0.4rem 0.65rem 0.4rem 1.75rem',
              fontSize: '0.775rem',
              borderRadius: '6px',
              border: '1px solid var(--border-subtle)',
              background: 'var(--bg-input)',
              color: 'var(--text-main)',
              outline: 'none',
            }}
          />
        </div>

        {/* Action Type Filter */}
        <select
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value)}
          style={{
            padding: '0.4rem 0.65rem',
            fontSize: '0.75rem',
            borderRadius: '6px',
            border: '1px solid var(--border-subtle)',
            background: 'var(--bg-input)',
            color: 'var(--text-muted)',
            outline: 'none',
            cursor: 'pointer',
          }}
        >
          <option value="">All Action Types</option>
          <option value="PROPOSAL">Task Proposals / Announcements</option>
          <option value="BID_SUBMITTED">Boat Bids</option>
          <option value="COMMITTED">Awards / Commitments</option>
          <option value="BID_REJECTED">Bid Rejections</option>
          <option value="INVALIDATED">Invalidations</option>
          <option value="REROUTED">Reroutes / Replanning</option>
          <option value="PASSENGERS_DELIVERED">Deliveries</option>
        </select>

        {/* Entity Filter */}
        <input
          type="text"
          placeholder="Filter Entity (e.g. BOAT01)"
          value={entityFilter}
          onChange={(e) => setEntityFilter(e.target.value)}
          style={{
            padding: '0.4rem 0.65rem',
            fontSize: '0.75rem',
            borderRadius: '6px',
            border: '1px solid var(--border-subtle)',
            background: 'var(--bg-input)',
            color: 'var(--text-main)',
            outline: 'none',
            width: '150px',
          }}
        />
      </div>

      {/* Decision Log Timeline */}
      <div style={{ flex: 1, overflowY: 'auto', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '0.5rem', background: 'var(--bg-secondary)' }}>
        {displayedLogs.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--text-dim)', fontSize: '0.85rem' }}>
            {loading ? 'Fetching live decision audit logs...' : 'No decision logs recorded yet for current filter.'}
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {displayedLogs.map((log) => {
              const isInvalidation = log.action_type === 'INVALIDATED' || log.action_type === 'FAILED';
              const isCommitment = log.action_type === 'COMMITTED' || log.action_type === 'BID_ACCEPTED';
              const isDelivery = log.action_type === 'PASSENGERS_DELIVERED';

              return (
                <div
                  key={log.entry_id}
                  className="glass-card"
                  style={{
                    padding: '0.75rem',
                    borderLeft: isInvalidation
                      ? '3px solid var(--rose-crit)'
                      : isCommitment
                      ? '3px solid var(--cyan-bright)'
                      : isDelivery
                      ? '3px solid var(--emerald-safe)'
                      : '3px solid var(--border-subtle)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.35rem', flexWrap: 'wrap', gap: '0.4rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-dim)', background: 'rgba(255,255,255,0.05)', padding: '0.1rem 0.35rem', borderRadius: '4px' }}>
                        T+{log.timestamp_min}m
                      </span>
                      {getActionBadge(log.action_type)}
                      <span className="mono" style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--text-main)' }}>
                        {log.entity_id} {log.target_id ? `→ ${log.target_id}` : ''}
                      </span>
                    </div>

                    <span className="mono" style={{ fontSize: '0.725rem', color: 'var(--text-dim)' }}>
                      Rule: {log.rule_applied}
                    </span>
                  </div>

                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                    {log.explanation}
                  </p>

                  {(log.previous_state || log.new_state) && (
                    <div style={{ marginTop: '0.35rem', fontSize: '0.725rem', color: 'var(--text-dim)', display: 'flex', gap: '0.5rem' }}>
                      {log.previous_state && <span>Prev: <code>{log.previous_state}</code></span>}
                      {log.new_state && <span>New: <code style={{ color: 'var(--cyan-bright)' }}>{log.new_state}</code></span>}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
