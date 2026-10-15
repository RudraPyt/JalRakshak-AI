import React from 'react';
import {
  Users,
  Anchor,
  ShieldCheck,
  ShieldAlert,
  Home,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import type { SimulationKPIs } from '../types';


interface KPIBannerProps {
  kpis: SimulationKPIs;
  invariantsPassed?: boolean;
  invariantViolations?: string[];
}

export const KPIBanner: React.FC<KPIBannerProps> = ({
  kpis,
  invariantsPassed = true,
  invariantViolations = [],
}) => {
  const delivered = kpis.total_delivered_people ?? kpis.people_rescued_to_shelters ?? 0;
  const affected = kpis.total_affected_people ?? kpis.total_people_affected ?? 115;
  const onboard = kpis.total_onboard_people ?? kpis.people_onboard_boats ?? 0;
  const awaiting = kpis.total_awaiting_people ?? kpis.people_awaiting_pickup ?? 0;
  const activeBoats = kpis.active_boats_count ?? kpis.boats_active ?? 0;
  const totalBoats = kpis.total_boats_count ?? 4;
  const shelterRemaining = kpis.shelter_remaining_total ?? kpis.shelter_remaining_capacity ?? 0;
  const shelterCapacity = kpis.shelter_capacity_total ?? kpis.shelter_total_capacity ?? 110;
  const shelterOccupancy = kpis.shelter_occupancy_total ?? kpis.shelter_current_occupancy ?? 0;
  const unmetIncidents = kpis.unmet_incidents_count ?? kpis.incidents_unserved ?? 0;
  const deliveryPct = kpis.delivery_rate_pct ?? (affected > 0 ? (delivered / affected) * 100 : 0);

  const isShelterBottleneck = shelterRemaining === 0;
  const isShelterLow = shelterRemaining > 0 && shelterRemaining <= 5;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.85rem', marginBottom: '1.25rem' }}>
      {/* 1. Delivered People */}
      <div className="glass-panel" style={{ padding: '0.85rem 1rem', position: 'relative', overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
          <span style={{ fontSize: '0.725rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Delivered Safe
          </span>
          <CheckCircle2 size={16} color="var(--emerald-safe)" />
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.4rem' }}>
          <span className="mono" style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--emerald-safe)' }}>
            {delivered}
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            / {affected} ({deliveryPct.toFixed(1)}%)
          </span>
        </div>
        <div style={{ marginTop: '0.4rem', height: '4px', background: 'rgba(255,255,255,0.06)', borderRadius: '2px', overflow: 'hidden' }}>
          <div
            style={{
              height: '100%',
              width: `${Math.min(100, deliveryPct)}%`,
              background: 'var(--emerald-safe)',
              borderRadius: '2px',
              transition: 'width 0.3s ease'
            }}
          />
        </div>
      </div>

      {/* 2. Onboard In-Transit */}
      <div className="glass-panel" style={{ padding: '0.85rem 1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
          <span style={{ fontSize: '0.725rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            People Onboard
          </span>
          <Users size={16} color="var(--cyan-bright)" />
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.4rem' }}>
          <span className="mono" style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--cyan-bright)' }}>
            {onboard}
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            in boat transit
          </span>
        </div>
        <div style={{ fontSize: '0.725rem', color: 'var(--text-dim)', marginTop: '0.35rem' }}>
          En route to designated shelters
        </div>
      </div>

      {/* 3. Awaiting Rescue */}
      <div className="glass-panel" style={{ padding: '0.85rem 1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
          <span style={{ fontSize: '0.725rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Awaiting Pickup
          </span>
          <AlertCircle size={16} color={awaiting > 0 ? 'var(--amber-warn)' : 'var(--text-dim)'} />
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.4rem' }}>
          <span className="mono" style={{ fontSize: '1.65rem', fontWeight: 800, color: awaiting > 0 ? 'var(--amber-warn)' : 'var(--text-muted)' }}>
            {awaiting}
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            stranded citizens
          </span>
        </div>
        <div style={{ fontSize: '0.725rem', color: 'var(--text-dim)', marginTop: '0.35rem' }}>
          {unmetIncidents} incidents awaiting service
        </div>
      </div>

      {/* 4. Active Fleet */}
      <div className="glass-panel" style={{ padding: '0.85rem 1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
          <span style={{ fontSize: '0.725rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Active Boat Fleet
          </span>
          <Anchor size={16} color="var(--blue-bright)" />
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.4rem' }}>
          <span className="mono" style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--blue-bright)' }}>
            {activeBoats}
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            / {totalBoats} operational
          </span>
        </div>
        <div style={{ fontSize: '0.725rem', color: 'var(--text-dim)', marginTop: '0.35rem' }}>
          {totalBoats - activeBoats} idle or maintaining
        </div>
      </div>

      {/* 5. Shelter Capacity & Bottleneck Warning */}
      <div className="glass-panel" style={{
        padding: '0.85rem 1rem',
        border: isShelterBottleneck ? '1px solid rgba(244, 63, 94, 0.4)' : isShelterLow ? '1px solid rgba(245, 158, 11, 0.4)' : '1px solid var(--border-subtle)',
        background: isShelterBottleneck ? 'rgba(244, 63, 94, 0.08)' : undefined
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
          <span style={{ fontSize: '0.725rem', fontWeight: 600, color: isShelterBottleneck ? '#fca5a5' : 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Shelter Capacity Free
          </span>
          <Home size={16} color={isShelterBottleneck ? 'var(--rose-crit)' : isShelterLow ? 'var(--amber-warn)' : 'var(--emerald-safe)'} />
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.4rem' }}>
          <span className="mono" style={{
            fontSize: '1.65rem',
            fontWeight: 800,
            color: isShelterBottleneck ? 'var(--rose-crit)' : isShelterLow ? 'var(--amber-warn)' : 'var(--text-main)'
          }}>
            {shelterRemaining}
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            / {shelterCapacity} total spaces
          </span>
        </div>
        <div style={{ fontSize: '0.725rem', color: isShelterBottleneck ? '#fca5a5' : 'var(--text-dim)', marginTop: '0.35rem', fontWeight: isShelterBottleneck ? 600 : 400 }}>
          {isShelterBottleneck ? '⚠️ CAPACITY EXHAUSTED (Bottleneck)' : `${shelterOccupancy} currently occupied/reserved`}
        </div>
      </div>


      {/* 6. Invariant Safety Status */}
      <div className="glass-panel" style={{
        padding: '0.85rem 1rem',
        border: !invariantsPassed || invariantViolations.length > 0 ? '1px solid var(--rose-crit)' : '1px solid var(--border-subtle)',
        background: !invariantsPassed || invariantViolations.length > 0 ? 'rgba(244, 63, 94, 0.1)' : undefined
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
          <span style={{ fontSize: '0.725rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Safety Invariants
          </span>
          {!invariantsPassed || invariantViolations.length > 0 ? (
            <ShieldAlert size={16} color="var(--rose-crit)" />
          ) : (
            <ShieldCheck size={16} color="var(--emerald-safe)" />
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.4rem' }}>
          <span className="mono" style={{
            fontSize: '1.25rem',
            fontWeight: 800,
            color: !invariantsPassed || invariantViolations.length > 0 ? 'var(--rose-crit)' : 'var(--emerald-safe)'
          }}>
            {!invariantsPassed || invariantViolations.length > 0 ? 'VIOLATION' : '10 / 10 PASSED'}
          </span>
        </div>
        <div style={{ fontSize: '0.725rem', color: !invariantsPassed ? '#fda4af' : 'var(--text-dim)', marginTop: '0.35rem' }}>
          {!invariantsPassed ? `${invariantViolations.length} constraint failures` : 'Capacity & flow laws hold'}
        </div>
      </div>
    </div>
  );
};
