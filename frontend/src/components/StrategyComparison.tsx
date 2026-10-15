import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import {
  RotateCw,
  Scale,
  Info,
} from 'lucide-react';
import type { ComparisonReport } from '../types';

import { api } from '../services/api';

export const StrategyComparison: React.FC = () => {
  const [report, setReport] = useState<ComparisonReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [evalMinutes, setEvalMinutes] = useState(15);
  const [includeStretch, setIncludeStretch] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runEvaluation = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.compareStrategies(evalMinutes, includeStretch);
      setReport(data);
    } catch (err: any) {
      setError(err.message || 'Failed to execute comparative evaluation benchmark.');
    } finally {
      setLoading(false);
    }
  };

  // Run on initial mount
  useEffect(() => {
    runEvaluation();
  }, []);

  // Format data for Recharts People & Requests comparison
  const peopleComparisonData = report
    ? [
      {
        metric: 'Delivered (pax)',
        'Centralized Baseline': report.centralized.total_delivered_people,
        'Decentralized MAS': report.multi_agent.total_delivered_people,
      },
      {
        metric: 'Onboard (in transit)',
        'Centralized Baseline': report.centralized.total_onboard_people,
        'Decentralized MAS': report.multi_agent.total_onboard_people,
      },
      {
        metric: 'Unmet Bottleneck',
        'Centralized Baseline': report.centralized.unmet_requests_count,
        'Decentralized MAS': report.multi_agent.unmet_requests_count,
      },
    ]
    : [];

  // Format data for Efficiency & Fairness
  const efficiencyData = report
    ? [
      {
        metric: 'MTTS (min)',
        'Centralized Baseline': Number(report.centralized.mean_time_to_service_min.toFixed(1)),
        'Decentralized MAS': Number(report.multi_agent.mean_time_to_service_min.toFixed(1)),
      },
      {
        metric: 'Idle Ratio (%)',
        'Centralized Baseline': Number(report.centralized.fleet_idle_ratio_pct.toFixed(1)),
        'Decentralized MAS': Number(report.multi_agent.fleet_idle_ratio_pct.toFixed(1)),
      },
      {
        metric: 'Fairness (x100)',
        'Centralized Baseline': Number((report.centralized.neighbourhood_fairness_jains_index * 100).toFixed(1)),
        'Decentralized MAS': Number((report.multi_agent.neighbourhood_fairness_jains_index * 100).toFixed(1)),
      },
      {
        metric: 'Recovery (min)',
        'Centralized Baseline': report.centralized.failure_recovery_time_min,
        'Decentralized MAS': report.multi_agent.failure_recovery_time_min,
      },
    ]
    : [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Benchmark Controls Card */}
      <div className="glass-panel" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Scale size={20} color="var(--cyan-bright)" />
              <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)' }}>
                Strategy Benchmark: Centralized Baseline vs Decentralized MAS
              </h2>
            </div>
            <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>
              Side-by-side deterministic simulation comparison executing both dispatch architectures over identical disaster conditions.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Horizon:</label>
              <select
                value={evalMinutes}
                onChange={(e) => setEvalMinutes(Number(e.target.value))}
                style={{
                  padding: '0.35rem 0.65rem',
                  fontSize: '0.75rem',
                  borderRadius: '6px',
                  background: 'var(--bg-input)',
                  border: '1px solid var(--border-subtle)',
                  color: 'var(--text-main)',
                  outline: 'none',
                }}
              >
                <option value={10}>10 Minutes</option>
                <option value={15}>15 Minutes (Standard)</option>
                <option value={20}>20 Minutes</option>
                <option value={30}>30 Minutes</option>
              </select>
            </div>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', color: 'var(--text-main)', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={includeStretch}
                onChange={(e) => setIncludeStretch(e.target.checked)}
                style={{ accentColor: 'var(--cyan-bright)' }}
              />
              Include Simultaneous Stretch Failures
            </label>

            <button
              className="btn btn-primary"
              onClick={runEvaluation}
              disabled={loading}
              style={{ padding: '0.45rem 0.85rem' }}
            >
              <RotateCw size={14} className={loading ? 'animate-spin' : ''} />
              {loading ? 'Evaluating...' : 'Run Benchmark'}
            </button>
          </div>
        </div>

        {error && (
          <div style={{ marginTop: '1rem', padding: '0.65rem', borderRadius: '6px', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid var(--rose-crit)', color: '#fda4af', fontSize: '0.8rem' }}>
            {error}
          </div>
        )}
      </div>

      {/* Honest Architecture Narrative Banner */}
      <div
        className="glass-card"
        style={{
          borderLeft: '4px solid var(--purple-agent)',
          padding: '0.85rem 1.25rem',
          fontSize: '0.8rem',
          color: 'var(--text-muted)',
          lineHeight: '1.5',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#d8b4fe', fontWeight: 600, marginBottom: '0.25rem' }}>
          <Info size={15} /> Objective Analytical Framing
        </div>
        Neither dispatch strategy is globally superior in all metrics. The <strong>Centralized Baseline</strong> computes faster global greedy matches with zero negotiation overhead when the network is static. However, the <strong>Decentralized Multi-Agent System (CNP)</strong> exhibits dynamic resilience during multi-point cascading disruptions (e.g., bridge collapses and boat stalls), allowing local agents to renegotiate commitments autonomously without single-point failure bottlenecks.
      </div>

      {report && (
        <>
          {/* Recharts Visual Comparison Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '1.25rem' }}>
            {/* Chart 1: Rescued & Operational Volume */}
            <div className="glass-panel" style={{ padding: '1.25rem' }}>
              <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.85rem' }}>
                Evacuation Volume: Delivered vs Onboard vs Unmet
              </h3>
              <div style={{ width: '100%', height: 260 }}>
                <ResponsiveContainer>
                  <BarChart data={peopleComparisonData} margin={{ top: 10, right: 20, left: -10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
                    <XAxis dataKey="metric" stroke="var(--text-muted)" fontSize={11} />
                    <YAxis stroke="var(--text-muted)" fontSize={11} />
                    <Tooltip
                      contentStyle={{
                        background: 'var(--bg-elevated)',
                        border: '1px solid var(--border-strong)',
                        borderRadius: '8px',
                        fontSize: '0.75rem',
                        color: 'var(--text-main)',
                      }}
                    />
                    <Legend wrapperStyle={{ fontSize: '0.75rem', paddingTop: '8px' }} />
                    <Bar dataKey="Centralized Baseline" fill="#0284c7" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="Decentralized MAS" fill="#a855f7" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Chart 2: Operational Efficiency & Recovery */}
            <div className="glass-panel" style={{ padding: '1.25rem' }}>
              <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.85rem' }}>
                Operational Metrics: MTTS, Idle Ratio, Fairness, Recovery
              </h3>
              <div style={{ width: '100%', height: 260 }}>
                <ResponsiveContainer>
                  <BarChart data={efficiencyData} margin={{ top: 10, right: 20, left: -10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
                    <XAxis dataKey="metric" stroke="var(--text-muted)" fontSize={11} />
                    <YAxis stroke="var(--text-muted)" fontSize={11} />
                    <Tooltip
                      contentStyle={{
                        background: 'var(--bg-elevated)',
                        border: '1px solid var(--border-strong)',
                        borderRadius: '8px',
                        fontSize: '0.75rem',
                        color: 'var(--text-main)',
                      }}
                    />
                    <Legend wrapperStyle={{ fontSize: '0.75rem', paddingTop: '8px' }} />
                    <Bar dataKey="Centralized Baseline" fill="#0284c7" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="Decentralized MAS" fill="#a855f7" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Metric Breakdown Table */}
          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.75rem' }}>
              Comprehensive Performance Benchmark Table
            </h3>
            <div style={{ overflowX: 'auto' }}>
              <table className="command-table">
                <thead>
                  <tr>
                    <th>Metric</th>
                    <th>Centralized Baseline</th>
                    <th>Decentralized MAS (CNP)</th>
                    <th>Operational Significance</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style={{ fontWeight: 600 }}>People Delivered Safe</td>
                    <td className="mono" style={{ color: 'var(--emerald-safe)', fontWeight: 700 }}>
                      {report.centralized.total_delivered_people} pax ({report.centralized.delivery_rate_pct.toFixed(1)}%)
                    </td>
                    <td className="mono" style={{ color: 'var(--emerald-safe)', fontWeight: 700 }}>
                      {report.multi_agent.total_delivered_people} pax ({report.multi_agent.delivery_rate_pct.toFixed(1)}%)
                    </td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Evacuated to open shelters within time limit</td>
                  </tr>
                  <tr>
                    <td style={{ fontWeight: 600 }}>People In Transit (Onboard)</td>
                    <td className="mono" style={{ color: 'var(--cyan-bright)' }}>{report.centralized.total_onboard_people} pax</td>
                    <td className="mono" style={{ color: 'var(--cyan-bright)' }}>{report.multi_agent.total_onboard_people} pax</td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Currently aboard boats moving toward shelters</td>
                  </tr>
                  <tr>
                    <td style={{ fontWeight: 600 }}>Unmet Requests</td>
                    <td className="mono" style={{ color: 'var(--rose-crit)' }}>
                      {report.centralized.unmet_requests_count} ({report.centralized.unmet_requests_pct.toFixed(1)}%)
                    </td>
                    <td className="mono" style={{ color: 'var(--rose-crit)' }}>
                      {report.multi_agent.unmet_requests_count} ({report.multi_agent.unmet_requests_pct.toFixed(1)}%)
                    </td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Requests held due to shelter capacity bottleneck</td>
                  </tr>
                  <tr>
                    <td style={{ fontWeight: 600 }}>Mean Time to Service (MTTS)</td>
                    <td className="mono">{report.centralized.mean_time_to_service_min.toFixed(2)} min</td>
                    <td className="mono">{report.multi_agent.mean_time_to_service_min.toFixed(2)} min</td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Average response latency from report to rescue</td>
                  </tr>
                  <tr>
                    <td style={{ fontWeight: 600 }}>Fleet Idle Ratio</td>
                    <td className="mono">{report.centralized.fleet_idle_ratio_pct.toFixed(1)}%</td>
                    <td className="mono">{report.multi_agent.fleet_idle_ratio_pct.toFixed(1)}%</td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Percentage of time boats are without assignments</td>
                  </tr>
                  <tr>
                    <td style={{ fontWeight: 600 }}>Neighbourhood Fairness (Jain's Index)</td>
                    <td className="mono">{(report.centralized.neighbourhood_fairness_jains_index * 100).toFixed(1)}%</td>
                    <td className="mono">{(report.multi_agent.neighbourhood_fairness_jains_index * 100).toFixed(1)}%</td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Even distribution of rescue services across zones</td>
                  </tr>
                  <tr>
                    <td style={{ fontWeight: 600 }}>Failure Recovery Time</td>
                    <td className="mono">{report.centralized.failure_recovery_time_min} min</td>
                    <td className="mono">{report.multi_agent.failure_recovery_time_min} min</td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Time required to reroute/replan after route/boat outages</td>
                  </tr>
                  <tr>
                    <td style={{ fontWeight: 600 }}>Safety Invariant Violations</td>
                    <td className="mono" style={{ color: report.centralized.route_violations_detected === 0 ? 'var(--emerald-safe)' : 'var(--rose-crit)' }}>
                      {report.centralized.route_violations_detected} violations
                    </td>
                    <td className="mono" style={{ color: report.multi_agent.route_violations_detected === 0 ? 'var(--emerald-safe)' : 'var(--rose-crit)' }}>
                      {report.multi_agent.route_violations_detected} violations
                    </td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Formal capacity and closed-route violations</td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Observations List */}
            {report.summary_observations && report.summary_observations.length > 0 && (
              <div style={{ marginTop: '1rem', background: 'var(--bg-card)', padding: '0.85rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.4rem' }}>
                  System Observations & Findings:
                </div>
                <ul style={{ paddingLeft: '1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                  {report.summary_observations.map((obs, idx) => (
                    <li key={idx}>{obs}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};
