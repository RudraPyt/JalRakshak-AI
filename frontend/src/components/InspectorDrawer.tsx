import React from 'react';
import {
  X,
  Anchor,
  AlertCircle,
  Home,
  Navigation,
  MapPin,
  ShieldAlert,
  Info,
} from 'lucide-react';


interface InspectorDrawerProps {
  selection: {
    type: 'boat' | 'incident' | 'shelter' | 'edge' | 'zone';
    data: any;
  } | null;
  onClose: () => void;
}

export const InspectorDrawer: React.FC<InspectorDrawerProps> = ({ selection, onClose }) => {
  if (!selection) return null;

  const { type, data } = selection;

  return (
    <div
      className="glass-panel"
      style={{
        padding: '1.25rem',
        borderLeft: '2px solid var(--cyan-bright)',
        background: 'rgba(15, 23, 42, 0.95)',
        boxShadow: 'var(--shadow-lg)',
        position: 'relative',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          {type === 'boat' && <Anchor size={20} color="var(--cyan-bright)" />}
          {type === 'incident' && <AlertCircle size={20} color="var(--rose-crit)" />}
          {type === 'shelter' && <Home size={20} color="var(--emerald-safe)" />}
          {type === 'edge' && <Navigation size={20} color="var(--blue-bright)" />}
          {type === 'zone' && <MapPin size={20} color="var(--purple-agent)" />}

          <div>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              {type} Entity Detail
            </span>
            <h3 className="mono" style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)' }}>
              {data.boat_id || data.incident_id || data.shelter_id || data.edge_id || data.zone_id}
            </h3>
          </div>
        </div>

        <button
          onClick={onClose}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer',
            padding: '0.35rem',
            borderRadius: '4px',
          }}
          title="Close Inspector"
        >
          <X size={18} />
        </button>
      </div>

      {/* Body content based on entity type */}
      {type === 'boat' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: 'var(--text-muted)' }}>Status:</span>
            <span className={`status-badge ${data.status === 'available' ? 'status-badge-safe' : data.status === 'failed' ? 'status-badge-critical' : 'status-badge-cyan'}`}>
              {data.status}
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Current Zone:</span>
            <span className="mono" style={{ fontWeight: 600 }}>{data.current_zone}</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Passenger Load:</span>
            <span className="mono" style={{ fontWeight: 600, color: data.onboard_people > 0 ? 'var(--cyan-bright)' : 'inherit' }}>
              {data.onboard_people} / {data.capacity_people} pax
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Speed Rating:</span>
            <span className="mono">{data.speed_units_per_min} units/min</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Assigned Incident:</span>
            <span className="mono">{data.assigned_incident_id || 'None (Idle)'}</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Destination Shelter:</span>
            <span className="mono">{data.target_shelter_id || 'None'}</span>
          </div>

          {data.planned_route_zones && data.planned_route_zones.length > 0 && (
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.65rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>
                Planned Route Waypoints:
              </span>
              <div className="mono" style={{ fontSize: '0.8rem', color: 'var(--cyan-bright)' }}>
                {data.planned_route_zones.join(' → ')}
              </div>
            </div>
          )}

          {data.status === 'failed' && (
            <div style={{ background: 'rgba(244, 63, 94, 0.15)', padding: '0.65rem', borderRadius: '8px', border: '1px solid var(--rose-crit)', color: '#fda4af' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontWeight: 600, marginBottom: '0.25rem' }}>
                <ShieldAlert size={14} /> Mechanical Failure
              </div>
              <div>{data.failure_reason || 'Propulsion failure in flooded debris'}</div>
              {data.failed_until_minute && (
                <div style={{ fontSize: '0.75rem', marginTop: '0.25rem' }}>
                  Expected recovery at minute: {data.failed_until_minute}
                </div>
              )}
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-dim)', borderTop: '1px solid var(--border-subtle)', paddingTop: '0.5rem' }}>
            <span>Idle Time: {data.total_idle_minutes} min</span>
            <span>Service Time: {data.total_service_minutes} min</span>
          </div>
        </div>
      )}

      {type === 'incident' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: 'var(--text-muted)' }}>Urgency:</span>
            <span className={`status-badge ${data.reported_urgency === 'critical' ? 'status-badge-critical' : data.reported_urgency === 'high' ? 'status-badge-high' : 'status-badge-medium'}`}>
              {data.reported_urgency}
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Lifecycle Status:</span>
            <span className={`status-badge ${data.lifecycle_status === 'fully_served' ? 'status-badge-safe' : data.lifecycle_status === 'unmet_shelter_bottleneck' ? 'status-badge-critical' : 'status-badge-low'}`}>
              {data.lifecycle_status.replace(/_/g, ' ')}
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Zone Location:</span>
            <span className="mono" style={{ fontWeight: 600 }}>{data.zone}</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Affected Headcount:</span>
            <span className="mono" style={{ fontWeight: 700, color: '#f8fafc' }}>{data.people_affected} people</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Awaiting Pickup:</span>
            <span className="mono" style={{ fontWeight: 700, color: 'var(--amber-warn)' }}>
              {data.people_awaiting_pickup !== undefined ? data.people_awaiting_pickup : Math.max(0, data.people_affected - data.people_rescued - data.people_onboard)} people
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Rescued & Delivered:</span>
            <span className="mono" style={{ fontWeight: 600, color: 'var(--emerald-safe)' }}>{data.people_rescued} people</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Assigned Boat:</span>
            <span className="mono">{data.assigned_boat_id || 'None'}</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Target Shelter:</span>
            <span className="mono">{data.assigned_shelter_id || 'None'}</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Verification Status:</span>
            <span style={{ color: data.verification_status === 'verified' ? 'var(--emerald-safe)' : 'var(--text-muted)', fontWeight: 500 }}>
              {data.verification_status} ({Math.round(data.source_confidence * 100)}% conf)
            </span>
          </div>

          {data.status_explanation && (
            <div style={{ background: 'rgba(15, 23, 42, 0.7)', padding: '0.65rem', borderRadius: '8px', border: '1px solid var(--border-subtle)', color: 'var(--text-muted)', fontSize: '0.775rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--cyan-bright)', marginBottom: '0.2rem' }}>
                <Info size={13} /> Status Explanation
              </div>
              {data.status_explanation}
            </div>
          )}

          {data.lifecycle_status === 'unmet_shelter_bottleneck' && (
            <div style={{ background: 'rgba(244, 63, 94, 0.12)', padding: '0.65rem', borderRadius: '8px', border: '1px solid rgba(244, 63, 94, 0.4)', color: '#fda4af', fontSize: '0.775rem' }}>
              <strong>Shelter Bottleneck:</strong> This incident cannot be safely dispatched because all network shelters have reached maximum authorized occupancy. The system truthfully holds dispatch until spaces free up.
            </div>
          )}
        </div>
      )}

      {type === 'shelter' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: 'var(--text-muted)' }}>Facility Name:</span>
            <span style={{ fontWeight: 600 }}>{data.name}</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Anchor Zone:</span>
            <span className="mono" style={{ fontWeight: 600 }}>{data.zone_id}</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: 'var(--text-muted)' }}>Operating Status:</span>
            <span className={`status-badge ${data.status === 'open' ? 'status-badge-safe' : 'status-badge-critical'}`}>
              {data.status}
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Total Authorized Capacity:</span>
            <span className="mono" style={{ fontWeight: 700 }}>{data.capacity_people} spaces</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Physically Sheltered:</span>
            <span className="mono" style={{ fontWeight: 600, color: 'var(--cyan-bright)' }}>{data.current_occupancy} people</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Reserved by In-Transit Boats:</span>
            <span className="mono" style={{ fontWeight: 600, color: 'var(--amber-warn)' }}>{data.reserved_capacity} spaces</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Remaining Free Capacity:</span>
            <span className="mono" style={{
              fontWeight: 800,
              fontSize: '1rem',
              color: Math.max(0, data.capacity_people - data.current_occupancy - data.reserved_capacity) === 0 ? 'var(--rose-crit)' : 'var(--emerald-safe)'
            }}>
              {Math.max(0, data.capacity_people - data.current_occupancy - data.reserved_capacity)} spaces
            </span>
          </div>

          {/* Progress bar visual */}
          <div style={{ marginTop: '0.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.725rem', color: 'var(--text-dim)', marginBottom: '0.25rem' }}>
              <span>Occupied ({data.current_occupancy})</span>
              <span>Reserved ({data.reserved_capacity})</span>
              <span>Free</span>
            </div>
            <div style={{ height: '8px', background: 'rgba(255,255,255,0.08)', borderRadius: '4px', overflow: 'hidden', display: 'flex' }}>
              <div style={{ width: `${(data.current_occupancy / data.capacity_people) * 100}%`, background: 'var(--cyan-bright)' }} />
              <div style={{ width: `${(data.reserved_capacity / data.capacity_people) * 100}%`, background: 'var(--amber-warn)' }} />
            </div>
          </div>
        </div>
      )}

      {type === 'edge' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: 'var(--text-muted)' }}>Route Status:</span>
            <span className={`status-badge ${data.status === 'open' ? 'status-badge-safe' : 'status-badge-critical'}`}>
              {data.status}
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Endpoints:</span>
            <span className="mono" style={{ fontWeight: 600 }}>{data.from_zone} ↔ {data.to_zone}</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Distance:</span>
            <span className="mono">{data.distance_units} units</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Traversal Time:</span>
            <span className="mono">{data.travel_time_min} minutes</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Route Uncertainty:</span>
            <span className="mono">{(data.uncertainty * 100).toFixed(0)}%</span>
          </div>

          {data.status === 'closed' && (
            <div style={{ background: 'rgba(244, 63, 94, 0.15)', padding: '0.65rem', borderRadius: '8px', border: '1px solid var(--rose-crit)', color: '#fda4af' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontWeight: 600, marginBottom: '0.25rem' }}>
                <ShieldAlert size={14} /> Edge Closed to Navigation
              </div>
              <div>{data.closure_reason || 'Severe flooding or debris blockage'}</div>
            </div>
          )}
        </div>
      )}

      {type === 'zone' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Sector ID:</span>
            <span className="mono" style={{ fontWeight: 700 }}>{data.zone_id}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Coordinates:</span>
            <span className="mono">({data.x}, {data.y})</span>
          </div>
          <div style={{ color: 'var(--text-dim)', fontSize: '0.75rem', marginTop: '0.25rem' }}>
            {data.description || 'Synthetic graph operational sector'}
          </div>
        </div>
      )}
    </div>
  );
};
