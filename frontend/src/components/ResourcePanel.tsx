import React from 'react';
import {
  Anchor,
  Home,
} from 'lucide-react';
import type { Boat, Shelter } from '../types';


interface ResourcePanelProps {
  boats: Boat[];
  shelters: Shelter[];
  onSelectBoat: (boat: Boat) => void;
  onSelectShelter: (shelter: Shelter) => void;
  selectedBoatId?: string;
  selectedShelterId?: string;
}

export const ResourcePanel: React.FC<ResourcePanelProps> = ({
  boats,
  shelters,
  onSelectBoat,
  onSelectShelter,
  selectedBoatId,
  selectedShelterId,
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', height: '100%' }}>
      {/* 1. SHELTERS SECTION */}
      <div className="glass-panel" style={{ padding: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
            <Home size={16} color="var(--emerald-safe)" />
            <h2 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)' }}>
              Evacuation Shelters & Capacities
            </h2>
          </div>
          <span style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
            Strict Safety Capacity Enforced
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.65rem' }}>
          {shelters.map((shelter) => {
            const isSelected = selectedShelterId === shelter.shelter_id;
            const remaining = Math.max(0, shelter.capacity_people - shelter.current_occupancy - shelter.reserved_capacity);
            const isFull = remaining === 0 || shelter.status === 'full';
            const occPct = (shelter.current_occupancy / shelter.capacity_people) * 100;
            const resPct = (shelter.reserved_capacity / shelter.capacity_people) * 100;

            return (
              <div
                key={shelter.shelter_id}
                onClick={() => onSelectShelter(shelter)}
                className="glass-card"
                style={{
                  padding: '0.75rem',
                  cursor: 'pointer',
                  borderColor: isSelected ? 'var(--cyan-bright)' : isFull ? 'rgba(244, 63, 94, 0.4)' : undefined,
                  background: isSelected ? 'rgba(6, 182, 212, 0.1)' : undefined,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '0.25rem' }}>
                  <span className="mono" style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--text-main)' }}>
                    {shelter.shelter_id} — {shelter.name}
                  </span>
                  <span
                    className={`status-badge ${isFull ? 'status-badge-critical' : 'status-badge-safe'}`}
                    style={{ fontSize: '0.65rem' }}
                  >
                    {isFull ? 'FULL' : 'OPEN'}
                  </span>
                </div>

                <div style={{ fontSize: '0.725rem', color: 'var(--text-dim)', marginBottom: '0.4rem' }}>
                  Zone: {shelter.zone_id}
                </div>

                {/* Multi-segment capacity progress bar */}
                <div style={{ height: '7px', background: 'rgba(255,255,255,0.06)', borderRadius: '4px', overflow: 'hidden', display: 'flex', marginBottom: '0.35rem' }}>
                  <div style={{ width: `${occPct}%`, background: 'var(--cyan-bright)', transition: 'width 0.3s ease' }} title={`Occupied: ${shelter.current_occupancy}`} />
                  <div style={{ width: `${resPct}%`, background: 'var(--amber-warn)', transition: 'width 0.3s ease' }} title={`Reserved: ${shelter.reserved_capacity}`} />
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.725rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>
                    Occ: <strong style={{ color: '#fff' }}>{shelter.current_occupancy}</strong> | Res: <strong style={{ color: '#fff' }}>{shelter.reserved_capacity}</strong>
                  </span>
                  <span style={{ color: isFull ? 'var(--rose-crit)' : 'var(--emerald-safe)', fontWeight: 700 }}>
                    {remaining} free / {shelter.capacity_people}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 2. BOAT FLEET SECTION */}
      <div className="glass-panel" style={{ padding: '1rem', flex: 1, display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
            <Anchor size={16} color="var(--cyan-bright)" />
            <h2 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)' }}>
              Rescue Boat Fleet
            </h2>
          </div>
          <span style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
            {boats.filter((b) => b.status === 'in_transit' || b.status === 'servicing').length} Actively Deployed
          </span>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', border: '1px solid var(--border-subtle)', borderRadius: '8px' }}>
          <table className="command-table">
            <thead>
              <tr>
                <th>Boat</th>
                <th>Status</th>
                <th>Zone</th>
                <th>Load</th>
                <th>Assigned Incident</th>
                <th>Target Shelter</th>
                <th>Speed</th>
              </tr>
            </thead>
            <tbody>
              {boats.map((b) => {
                const isSelected = selectedBoatId === b.boat_id;
                const isFailed = b.status === 'failed';

                return (
                  <tr
                    key={b.boat_id}
                    onClick={() => onSelectBoat(b)}
                    style={{
                      cursor: 'pointer',
                      background: isSelected ? 'rgba(6, 182, 212, 0.12)' : isFailed ? 'rgba(244, 63, 94, 0.08)' : undefined,
                    }}
                  >
                    <td className="mono" style={{ fontWeight: 700, color: isFailed ? 'var(--rose-crit)' : 'var(--cyan-bright)' }}>
                      {b.boat_id}
                    </td>
                    <td>
                      <span
                        className={`status-badge ${
                          b.status === 'available'
                            ? 'status-badge-safe'
                            : b.status === 'failed'
                            ? 'status-badge-critical'
                            : 'status-badge-cyan'
                        }`}
                        style={{ fontSize: '0.675rem' }}
                      >
                        {b.status}
                      </span>
                    </td>
                    <td className="mono">{b.current_zone}</td>
                    <td className="mono" style={{ fontWeight: 600 }}>
                      <span style={{ color: b.onboard_people > 0 ? 'var(--cyan-bright)' : 'inherit' }}>
                        {b.onboard_people}
                      </span>{' '}
                      / {b.capacity_people}
                    </td>
                    <td className="mono" style={{ fontSize: '0.75rem' }}>
                      {b.assigned_incident_id || '—'}
                    </td>
                    <td className="mono" style={{ fontSize: '0.75rem' }}>
                      {b.target_shelter_id || '—'}
                    </td>
                    <td className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {b.speed_units_per_min}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
