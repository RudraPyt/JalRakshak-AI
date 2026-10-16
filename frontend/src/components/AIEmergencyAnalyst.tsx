import React, { useState } from 'react';
import {
  Sparkles,
  AlertTriangle,
  RefreshCw,
  Clock,
  Shield,
  LifeBuoy,
  Home,
  AlertOctagon,
  CheckCircle,
  FileText,
  ChevronDown,
  ChevronUp,
  Cpu,
  Info,
  Layers,
} from 'lucide-react';
import type { SituationReportResponse } from '../types';
import { api } from '../services/api';

interface AIEmergencyAnalystProps {
  currentMinute: number;
  activeStrategy: string;
  onRefreshSimulationState?: () => void;
  // Optional external report control
  compact?: boolean;
}

export const AIEmergencyAnalyst: React.FC<AIEmergencyAnalystProps> = ({
  currentMinute,
  activeStrategy,
  onRefreshSimulationState,
  compact = false,
}) => {
  const [report, setReport] = useState<SituationReportResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(!compact);
  const [selectedFocus, setSelectedFocus] = useState<string>('all');

  const handleGenerateReport = async () => {
    if (isLoading) return;
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.getSituationReport({
        focus_area: selectedFocus === 'all' ? undefined : selectedFocus,
      });
      setReport(response);
      setIsExpanded(true);
      if (onRefreshSimulationState) {
        onRefreshSimulationState();
      }
    } catch (err: any) {
      const message = err.message || 'Failed to generate situation report from Gemini API.';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const isStale = report && report.simulation_minute !== currentMinute;

  return (
    <div
      className="glass-panel"
      style={{
        border: '1px solid var(--border-cyan)',
        background: 'linear-gradient(180deg, rgba(6, 182, 212, 0.05) 0%, var(--bg-card) 100%)',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Top Banner & Trigger Area */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0.85rem 1.25rem',
          flexWrap: 'wrap',
          gap: '0.75rem',
          borderBottom: isExpanded ? '1px solid var(--border-subtle)' : 'none',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 15px rgba(6, 182, 212, 0.35)',
            }}
          >
            <Sparkles size={20} color="#ffffff" className={isLoading ? 'pulsing-ring' : ''} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
              <h2 style={{ fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
                AI Emergency Situation Analyst
              </h2>
              <span
                style={{
                  fontSize: '0.65rem',
                  fontWeight: 700,
                  letterSpacing: '0.05em',
                  textTransform: 'uppercase',
                  padding: '0.15rem 0.5rem',
                  borderRadius: '12px',
                  background: 'rgba(6, 182, 212, 0.15)',
                  color: 'var(--cyan-bright)',
                  border: '1px solid var(--border-cyan)',
                }}
              >
                Google Gemini 2.5
              </span>
              {report && (
                <span
                  style={{
                    fontSize: '0.65rem',
                    padding: '0.15rem 0.5rem',
                    borderRadius: '12px',
                    background: isStale ? 'rgba(245, 158, 11, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                    color: isStale ? 'var(--amber-warn)' : 'var(--emerald-safe)',
                    border: `1px solid ${isStale ? 'rgba(245, 158, 11, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.3rem',
                  }}
                >
                  <Clock size={11} />
                  Snapshot: T+{report.simulation_minute}m {isStale ? `(Live: T+${currentMinute}m)` : '(Current)'}
                </span>
              )}
            </div>
            <p style={{ fontSize: '0.725rem', color: 'var(--text-muted)', margin: 0, marginTop: '0.15rem' }}>
              Engine: <strong style={{ color: 'var(--text-main)' }}>{activeStrategy === 'multi_agent' ? 'Decentralized MAS (CNP)' : 'Centralized Baseline'}</strong> · Multi-criteria assessment, bottleneck identification, and advisory
            </p>
          </div>
        </div>

        {/* Controls & Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
          {/* Optional Focus Area Filter */}
          <select
            value={selectedFocus}
            onChange={(e) => setSelectedFocus(e.target.value)}
            disabled={isLoading}
            style={{
              padding: '0.4rem 0.6rem',
              fontSize: '0.75rem',
              borderRadius: '6px',
              background: 'var(--bg-elevated)',
              color: 'var(--text-main)',
              border: '1px solid var(--border-subtle)',
              cursor: 'pointer',
              outline: 'none',
            }}
          >
            <option value="all">Comprehensive Analysis</option>
            <option value="evacuation">Focus: Incident Evacuation</option>
            <option value="fleet_shelter">Focus: Fleet & Shelter Capacity</option>
            <option value="road_bottlenecks">Focus: Route & Network Bottlenecks</option>
          </select>

          {/* Primary Action Button */}
          <button
            id="btn-generate-ai-report"
            className="btn btn-primary"
            onClick={handleGenerateReport}
            disabled={isLoading}
            style={{
              padding: '0.45rem 1rem',
              fontSize: '0.8rem',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              background: isLoading
                ? 'var(--bg-elevated)'
                : 'linear-gradient(135deg, #0284c7 0%, #06b6d4 100%)',
              boxShadow: isLoading ? 'none' : '0 0 15px rgba(6, 182, 212, 0.4)',
              cursor: isLoading ? 'not-allowed' : 'pointer',
            }}
          >
            <RefreshCw size={14} className={isLoading ? 'pulsing-ring' : ''} />
            <span>
              {isLoading
                ? 'Analyzing Simulation State...'
                : report
                ? isStale
                  ? `Re-analyze at T+${currentMinute}m`
                  : 'Refresh AI Report'
                : 'Generate AI Situation Report'}
            </span>
          </button>

          {/* Toggle Expand/Collapse */}
          {report && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                padding: '0.4rem',
                display: 'flex',
                alignItems: 'center',
              }}
              title={isExpanded ? 'Collapse report panel' : 'Expand report panel'}
            >
              {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
            </button>
          )}
        </div>
      </div>

      {/* Loading Bar Indicator */}
      {isLoading && (
        <div style={{ padding: '2rem 1.5rem', textAlign: 'center' }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.75rem',
              background: 'var(--bg-elevated)',
              padding: '0.8rem 1.5rem',
              borderRadius: '24px',
              border: '1px solid var(--border-cyan)',
              boxShadow: '0 0 25px rgba(6, 182, 212, 0.2)',
            }}
          >
            <Cpu size={20} color="var(--cyan-bright)" className="pulsing-ring" />
            <div style={{ textAlign: 'left' }}>
              <div style={{ fontSize: '0.825rem', fontWeight: 700, color: 'var(--text-main)' }}>
                Gemini AI is analyzing snapshot at Minute T+{currentMinute}...
              </div>
              <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
                Evaluating capacity margins, road network blockages, active incidents, and invariants.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error Card */}
      {error && !isLoading && (
        <div
          style={{
            margin: '1rem 1.25rem',
            padding: '1rem',
            borderRadius: '8px',
            background: 'rgba(244, 63, 94, 0.1)',
            border: '1px solid rgba(244, 63, 94, 0.35)',
            color: 'var(--text-main)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
            <AlertTriangle size={20} color="var(--rose-crit)" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div style={{ flex: 1 }}>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--rose-crit)', margin: '0 0 0.25rem 0' }}>
                Situation Report Generation Error
              </h4>
              <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)', margin: '0 0 0.5rem 0' }}>
                {error}
              </p>
              {error.includes('GEMINI_API_KEY') && (
                <div
                  style={{
                    background: 'var(--bg-elevated)',
                    padding: '0.6rem 0.8rem',
                    borderRadius: '6px',
                    fontSize: '0.725rem',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  <span style={{ fontWeight: 600, color: 'var(--amber-warn)' }}>Configuration Guide:</span>
                  <p style={{ margin: '0.25rem 0 0 0', color: 'var(--text-dim)' }}>
                    Add your Gemini API key to backend environment variables or <code className="mono">backend/.env</code>:
                  </p>
                  <code
                    className="mono"
                    style={{
                      display: 'block',
                      background: 'rgba(0,0,0,0.3)',
                      padding: '0.3rem 0.5rem',
                      borderRadius: '4px',
                      marginTop: '0.25rem',
                      color: 'var(--cyan-bright)',
                    }}
                  >
                    GEMINI_API_KEY="your-gemini-api-key"
                  </code>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Empty State Prompt (Before First Generation) */}
      {!report && !isLoading && !error && (
        <div
          style={{
            padding: '1.75rem 1.25rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <FileText size={22} color="var(--text-dim)" />
            <div>
              <div style={{ fontSize: '0.825rem', fontWeight: 600, color: 'var(--text-main)' }}>
                No active situation report generated for Minute T+{currentMinute}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Click <strong>"Generate AI Situation Report"</strong> to evaluate current disaster dynamics, bottlenecks, and recommended human actions.
              </div>
            </div>
          </div>
          <button
            className="btn btn-primary"
            onClick={handleGenerateReport}
            style={{
              padding: '0.45rem 1rem',
              fontSize: '0.8rem',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
            }}
          >
            <Sparkles size={14} />
            Generate Now
          </button>
        </div>
      )}

      {/* Generated Report Content Panel */}
      {report && isExpanded && !isLoading && (
        <div style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Advisory Disclaimer Notice */}
          <div
            style={{
              background: 'rgba(245, 158, 11, 0.08)',
              border: '1px solid rgba(245, 158, 11, 0.3)',
              borderRadius: '8px',
              padding: '0.75rem 1rem',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '0.65rem',
            }}
          >
            <Shield size={18} color="var(--amber-warn)" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div style={{ fontSize: '0.75rem', lineHeight: '1.4' }}>
              <strong style={{ color: 'var(--amber-warn)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Simulation Advisory Only:
              </strong>{' '}
              <span style={{ color: 'var(--text-muted)' }}>{report.advisory_disclaimer}</span>
            </div>
          </div>

          {/* SECTION 1: SITUATION OVERVIEW */}
          <div
            className="glass-card"
            style={{
              padding: '1rem 1.25rem',
              borderLeft: '4px solid var(--cyan-bright)',
              background: 'var(--bg-elevated)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <ActivityIcon size={16} color="var(--cyan-bright)" />
                <h3 style={{ fontSize: '0.875rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.04em', margin: 0, color: 'var(--text-main)' }}>
                  1. Situation Overview
                </h3>
              </div>
              <span className="mono" style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>
                T+{report.simulation_minute}m · {new Date(report.generated_at_utc).toLocaleTimeString()}
              </span>
            </div>
            <p style={{ fontSize: '0.825rem', lineHeight: 1.5, color: 'var(--text-main)', margin: 0 }}>
              {report.situation_overview}
            </p>
          </div>

          {/* TWO COLUMN GRID: CRITICAL INCIDENTS & RESOURCE STATUS */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1rem' }}>
            {/* SECTION 2: CRITICAL INCIDENTS */}
            <div className="glass-card" style={{ padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                  <AlertOctagon size={16} color="var(--rose-crit)" />
                  <h4 style={{ fontSize: '0.825rem', fontWeight: 700, margin: 0, color: 'var(--text-main)', textTransform: 'uppercase' }}>
                    2. Critical Incidents
                  </h4>
                </div>
                <span style={{ fontSize: '0.7rem', color: 'var(--rose-crit)', fontWeight: 600 }}>
                  {report.critical_incidents.length} Flagged
                </span>
              </div>

              {report.critical_incidents.length === 0 ? (
                <div style={{ fontSize: '0.775rem', color: 'var(--text-muted)', padding: '0.5rem 0' }}>
                  No high-criticality incidents requiring immediate triage in this snapshot.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                  {report.critical_incidents.map((inc) => (
                    <div
                      key={inc.incident_id}
                      style={{
                        background: 'var(--bg-secondary)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: '6px',
                        padding: '0.65rem 0.8rem',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                          <span className="mono" style={{ fontWeight: 700, fontSize: '0.8rem', color: 'var(--cyan-bright)' }}>
                            {inc.incident_id}
                          </span>
                          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{inc.location}</span>
                        </div>
                        <span
                          style={{
                            fontSize: '0.65rem',
                            fontWeight: 700,
                            padding: '0.1rem 0.4rem',
                            borderRadius: '4px',
                            background:
                              inc.urgency.toUpperCase() === 'CRITICAL'
                                ? 'rgba(244, 63, 94, 0.2)'
                                : 'rgba(245, 158, 11, 0.2)',
                            color:
                              inc.urgency.toUpperCase() === 'CRITICAL'
                                ? 'var(--rose-crit)'
                                : 'var(--amber-warn)',
                            border: `1px solid ${
                              inc.urgency.toUpperCase() === 'CRITICAL'
                                ? 'rgba(244, 63, 94, 0.4)'
                                : 'rgba(245, 158, 11, 0.4)'
                            }`,
                          }}
                        >
                          {inc.urgency}
                        </span>
                      </div>
                      <div style={{ display: 'flex', gap: '1rem', fontSize: '0.725rem', marginBottom: '0.3rem' }}>
                        <span>
                          Affected: <strong style={{ color: 'var(--text-main)' }}>{inc.affected_population}</strong>
                        </span>
                        <span>
                          Stranded / Awaiting:{' '}
                          <strong style={{ color: 'var(--rose-crit)' }}>{inc.waiting_population}</strong>
                        </span>
                      </div>
                      <p style={{ fontSize: '0.725rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>
                        {inc.reason}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* SECTION 3: RESOURCE STATUS */}
            <div className="glass-card" style={{ padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                  <LifeBuoy size={16} color="var(--blue-bright)" />
                  <h4 style={{ fontSize: '0.825rem', fontWeight: 700, margin: 0, color: 'var(--text-main)', textTransform: 'uppercase' }}>
                    3. Fleet & Shelter Resources
                  </h4>
                </div>
                <span style={{ fontSize: '0.7rem', color: 'var(--blue-bright)', fontWeight: 600 }}>
                  {report.resource_status.available_boats} / {report.resource_status.total_boats} Boats Available
                </span>
              </div>

              {/* Resource Metrics Strip */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem' }}>
                <div style={{ background: 'var(--bg-secondary)', padding: '0.5rem', borderRadius: '6px', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Available Boats</div>
                  <div className="mono" style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--emerald-safe)' }}>
                    {report.resource_status.available_boats}
                  </div>
                </div>
                <div style={{ background: 'var(--bg-secondary)', padding: '0.5rem', borderRadius: '6px', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Dispatched</div>
                  <div className="mono" style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--cyan-bright)' }}>
                    {report.resource_status.dispatched_boats}
                  </div>
                </div>
                <div style={{ background: 'var(--bg-secondary)', padding: '0.5rem', borderRadius: '6px', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Failed/Maint</div>
                  <div className="mono" style={{ fontSize: '1.1rem', fontWeight: 800, color: report.resource_status.failed_boats > 0 ? 'var(--rose-crit)' : 'var(--text-dim)' }}>
                    {report.resource_status.failed_boats}
                  </div>
                </div>
              </div>

              {/* Shelter Capacity Progress Bar */}
              <div style={{ background: 'var(--bg-secondary)', padding: '0.65rem', borderRadius: '6px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.725rem', marginBottom: '0.35rem' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                    <Home size={12} color="var(--indigo-bright)" /> Shelter Occupancy
                  </span>
                  <span className="mono" style={{ fontWeight: 600 }}>
                    {report.resource_status.shelter_current_occupancy} / {report.resource_status.total_shelter_capacity} ({report.resource_status.shelter_remaining_capacity} free)
                  </span>
                </div>
                <div style={{ width: '100%', height: '8px', background: 'var(--bg-card)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div
                    style={{
                      height: '100%',
                      width: `${Math.min(
                        100,
                        (report.resource_status.shelter_current_occupancy / Math.max(1, report.resource_status.total_shelter_capacity)) * 100
                      )}%`,
                      background: 'linear-gradient(90deg, #06b6d4, #10b981)',
                      borderRadius: '4px',
                    }}
                  />
                </div>
              </div>

              <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                <strong>Capacity Assessment:</strong> {report.resource_status.shortages_and_notes}
              </div>
            </div>
          </div>

          {/* TWO COLUMN GRID: BOTTLENECKS/RISKS & RECOMMENDED ACTIONS */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1rem' }}>
            {/* SECTION 4: BOTTLENECKS AND RISKS */}
            <div className="glass-card" style={{ padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                  <AlertTriangle size={16} color="var(--amber-warn)" />
                  <h4 style={{ fontSize: '0.825rem', fontWeight: 700, margin: 0, color: 'var(--text-main)', textTransform: 'uppercase' }}>
                    4. Bottlenecks & Operational Risks
                  </h4>
                </div>
                <span style={{ fontSize: '0.7rem', color: 'var(--amber-warn)', fontWeight: 600 }}>
                  {report.bottlenecks_and_risks.length} Detected
                </span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                {report.bottlenecks_and_risks.map((risk, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: 'var(--bg-secondary)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: '6px',
                      padding: '0.65rem 0.8rem',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-main)' }}>
                        {risk.category}
                      </span>
                      <span
                        style={{
                          fontSize: '0.625rem',
                          fontWeight: 700,
                          textTransform: 'uppercase',
                          padding: '0.1rem 0.4rem',
                          borderRadius: '4px',
                          background:
                            risk.severity === 'critical'
                              ? 'rgba(244, 63, 94, 0.2)'
                              : risk.severity === 'high'
                              ? 'rgba(245, 158, 11, 0.2)'
                              : 'rgba(56, 189, 248, 0.2)',
                          color:
                            risk.severity === 'critical'
                              ? 'var(--rose-crit)'
                              : risk.severity === 'high'
                              ? 'var(--amber-warn)'
                              : 'var(--blue-bright)',
                        }}
                      >
                        {risk.severity}
                      </span>
                    </div>
                    <p style={{ fontSize: '0.725rem', color: 'var(--text-muted)', margin: '0 0 0.35rem 0', lineHeight: 1.4 }}>
                      {risk.description}
                    </p>
                    <div style={{ fontSize: '0.675rem', color: 'var(--text-dim)', background: 'rgba(0,0,0,0.15)', padding: '0.25rem 0.45rem', borderRadius: '4px' }}>
                      <strong>Evidence:</strong> {risk.evidence}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* SECTION 5: RECOMMENDED ACTIONS (HUMAN REVIEW ONLY) */}
            <div className="glass-card" style={{ padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem', border: '1px solid var(--border-cyan)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                  <CheckCircle size={16} color="var(--emerald-safe)" />
                  <h4 style={{ fontSize: '0.825rem', fontWeight: 700, margin: 0, color: 'var(--text-main)', textTransform: 'uppercase' }}>
                    5. Recommended Practical Actions
                  </h4>
                </div>
                <span
                  style={{
                    fontSize: '0.65rem',
                    padding: '0.1rem 0.45rem',
                    borderRadius: '4px',
                    background: 'rgba(16, 185, 129, 0.15)',
                    color: 'var(--emerald-safe)',
                    fontWeight: 700,
                  }}
                >
                  Human Review Only
                </span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                {report.recommended_actions.map((act) => (
                  <div
                    key={act.action_id}
                    style={{
                      background: 'var(--bg-secondary)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: '6px',
                      padding: '0.65rem 0.8rem',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                        <span className="mono" style={{ fontWeight: 800, fontSize: '0.75rem', color: 'var(--emerald-safe)' }}>
                          {act.action_id}
                        </span>
                        <strong style={{ fontSize: '0.775rem', color: 'var(--text-main)' }}>{act.title}</strong>
                      </div>
                      {act.target_entity && (
                        <span className="mono" style={{ fontSize: '0.65rem', background: 'var(--bg-elevated)', padding: '0.1rem 0.4rem', borderRadius: '4px', color: 'var(--cyan-bright)' }}>
                          {act.target_entity}
                        </span>
                      )}
                    </div>
                    <p style={{ fontSize: '0.725rem', color: 'var(--text-muted)', margin: '0 0 0.35rem 0', lineHeight: 1.4 }}>
                      {act.rationale}
                    </p>
                    <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)', fontStyle: 'italic' }}>
                      ℹ️ {act.advisory_note}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* LOWER STRIP: STRATEGY PERFORMANCE & DATA LIMITATIONS */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1rem' }}>
            {/* SECTION 6: STRATEGY PERFORMANCE */}
            <div className="glass-card" style={{ padding: '0.85rem 1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.5rem' }}>
                <Layers size={15} color="var(--purple-agent)" />
                <h5 style={{ fontSize: '0.775rem', fontWeight: 700, margin: 0, textTransform: 'uppercase', color: 'var(--text-main)' }}>
                  6. Strategy Performance Assessment
                </h5>
              </div>
              <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)', lineHeight: 1.45 }}>
                <p style={{ margin: '0 0 0.4rem 0' }}>{report.strategy_performance.summary}</p>
                <div style={{ fontSize: '0.675rem', color: 'var(--text-dim)' }}>
                  Active Engine:{' '}
                  <strong style={{ color: 'var(--text-main)' }}>
                    {report.strategy_performance.current_strategy === 'multi_agent'
                      ? 'Decentralized MAS (CNP)'
                      : 'Centralized Greedy Baseline'}
                  </strong>
                  {' · '}
                  Comparative Benchmark:{' '}
                  <span style={{ color: report.strategy_performance.measurements_available ? 'var(--emerald-safe)' : 'var(--amber-warn)' }}>
                    {report.strategy_performance.measurements_available ? 'Evaluated' : 'Not Run in Session'}
                  </span>
                </div>
              </div>
            </div>

            {/* SECTION 7: DATA LIMITATIONS */}
            <div className="glass-card" style={{ padding: '0.85rem 1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.5rem' }}>
                <Info size={15} color="var(--blue-bright)" />
                <h5 style={{ fontSize: '0.775rem', fontWeight: 700, margin: 0, textTransform: 'uppercase', color: 'var(--text-main)' }}>
                  7. Data Limitations & Scope
                </h5>
              </div>
              <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.725rem', color: 'var(--text-muted)', lineHeight: 1.45 }}>
                {report.data_limitations.limitations.map((lim, idx) => (
                  <li key={idx} style={{ marginBottom: '0.2rem' }}>
                    {lim}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Inline helper icon component for Activity
function ActivityIcon(props: { size: number; color: string }) {
  return (
    <svg
      width={props.size}
      height={props.size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={props.color}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
    </svg>
  );
}

export default AIEmergencyAnalyst;
