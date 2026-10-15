import React from 'react';
import {
  Activity,
  Play,
  Pause,
  RotateCcw,
  SkipForward,
  Wifi,
  WifiOff,
  Sliders,
  History,
  BarChart3,
  AlertTriangle,
  Radio,
} from 'lucide-react';

interface HeaderProps {
  minute: number;
  isRunning: boolean;
  strategy: 'centralized' | 'multi_agent';
  activeTab: 'dashboard' | 'replay' | 'comparison' | 'events' | 'logs';
  isConnected: boolean;
  autoPlaySpeed: number;
  onTabChange: (tab: 'dashboard' | 'replay' | 'comparison' | 'events' | 'logs') => void;
  onStrategyChange: (strategy: 'centralized' | 'multi_agent') => void;
  onStep: () => void;
  onTogglePlay: () => void;
  onReset: () => void;
  onSpeedChange: (speed: number) => void;
  isProcessing: boolean;
  isReplayActive?: boolean;
  onExitReplay?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  minute,
  isRunning,
  strategy,
  activeTab,
  isConnected,
  autoPlaySpeed,
  onTabChange,
  onStrategyChange,
  onStep,
  onTogglePlay,
  onReset,
  onSpeedChange,
  isProcessing,
  isReplayActive,
  onExitReplay,
}) => {
  return (
    <header className="glass-panel" style={{ borderRadius: 0, borderTop: 'none', borderLeft: 'none', borderRight: 'none' }}>
      {/* Synthetic Simulation Disclaimer Banner */}
      <div className="disclaimer-banner">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertTriangle size={15} color="#f59e0b" />
          <span>
            <strong>SYNTHETIC SIMULATION ENVIRONMENT:</strong> All zones, routes, coordinates, and incidents are generated for testing multi-agent decision support. Not for live emergency dispatch.
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.725rem' }}>
          <span style={{ color: isConnected ? '#34d399' : '#f87171', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            {isConnected ? <Wifi size={13} /> : <WifiOff size={13} />}
            {isConnected ? 'Backend Connected' : 'Disconnected (Retrying...)'}
          </span>
        </div>
      </div>

      {/* Main Command Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem 1.25rem', gap: '1rem', flexWrap: 'wrap' }}>
        {/* Brand & Mission Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div style={{
            width: '38px',
            height: '38px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #0284c7 0%, #06b6d4 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 15px rgba(6, 182, 212, 0.4)'
          }}>
            <Radio size={22} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <h1 style={{ fontSize: '1.05rem', fontWeight: 800, letterSpacing: '-0.02em', color: '#f8fafc' }}>
                JalRakshak AI
              </h1>
              <span style={{ fontSize: '0.7rem', color: 'var(--cyan-bright)', background: 'rgba(6, 182, 212, 0.12)', padding: '0.1rem 0.4rem', borderRadius: '4px', border: '1px solid var(--border-cyan)', fontWeight: 600 }}>
                PROBLEM 27
              </span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Flood Rescue Command Center
            </p>
          </div>
        </div>

        {/* Replay Notice if in Replay Mode */}
        {isReplayActive && (
          <div style={{
            background: 'rgba(245, 158, 11, 0.2)',
            border: '1px solid rgba(245, 158, 11, 0.5)',
            padding: '0.35rem 0.8rem',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '0.6rem'
          }}>
            <History size={16} color="#fbbf24" />
            <span style={{ fontSize: '0.8rem', color: '#fef3c7', fontWeight: 600 }}>
              HISTORICAL REPLAY MODE
            </span>
            <button
              className="btn btn-warning"
              style={{ padding: '0.2rem 0.5rem', fontSize: '0.725rem' }}
              onClick={onExitReplay}
            >
              Exit to Live
            </button>
          </div>
        )}

        {/* Simulation Clock & Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          {/* Clock Pill */}
          <div className="glass-card" style={{ padding: '0.35rem 0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem', borderColor: 'var(--border-cyan)' }}>
            <Activity size={16} color="var(--cyan-bright)" className={isRunning ? 'pulsing-ring' : ''} />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>SIM TIME</span>
            <span className="mono" style={{ fontSize: '1.1rem', fontWeight: 700, color: '#38bdf8' }}>
              T + {minute} <span style={{ fontSize: '0.75rem', fontWeight: 400, color: 'var(--text-muted)' }}>min</span>
            </span>
          </div>

          {/* Strategy Selector */}
          <div style={{ display: 'flex', background: 'rgba(15, 23, 42, 0.9)', padding: '0.2rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <button
              onClick={() => onStrategyChange('centralized')}
              disabled={isProcessing}
              style={{
                padding: '0.35rem 0.65rem',
                fontSize: '0.75rem',
                fontWeight: 600,
                borderRadius: '6px',
                border: 'none',
                cursor: 'pointer',
                background: strategy === 'centralized' ? '#0284c7' : 'transparent',
                color: strategy === 'centralized' ? '#ffffff' : 'var(--text-muted)',
                transition: 'all 0.15s ease'
              }}
            >
              Centralized Baseline
            </button>
            <button
              onClick={() => onStrategyChange('multi_agent')}
              disabled={isProcessing}
              style={{
                padding: '0.35rem 0.65rem',
                fontSize: '0.75rem',
                fontWeight: 600,
                borderRadius: '6px',
                border: 'none',
                cursor: 'pointer',
                background: strategy === 'multi_agent' ? 'linear-gradient(135deg, #7c3aed, #a855f7)' : 'transparent',
                color: strategy === 'multi_agent' ? '#ffffff' : 'var(--text-muted)',
                transition: 'all 0.15s ease'
              }}
            >
              Decentralized MAS (CNP)
            </button>
          </div>

          {/* Execution Controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <button
              className={`btn ${isRunning ? 'btn-warning' : 'btn-primary'}`}
              onClick={onTogglePlay}
              disabled={isProcessing || isReplayActive}
              title={isRunning ? 'Pause simulation loop' : 'Run simulation automatically'}
            >
              {isRunning ? <Pause size={15} /> : <Play size={15} />}
              {isRunning ? 'Pause' : 'Auto'}
            </button>

            <button
              className="btn btn-secondary"
              onClick={onStep}
              disabled={isProcessing || isRunning || isReplayActive}
              title="Advance simulation by exactly 1 minute"
            >
              <SkipForward size={15} />
              Step (+1m)
            </button>

            <button
              className="btn btn-danger"
              onClick={onReset}
              disabled={isProcessing}
              title="Reset simulation to initial state (minute 0)"
            >
              <RotateCcw size={15} />
              Reset
            </button>

            {/* Speed toggle for auto-play */}
            <select
              value={autoPlaySpeed}
              onChange={(e) => onSpeedChange(Number(e.target.value))}
              className="glass-card"
              style={{
                padding: '0.4rem 0.5rem',
                fontSize: '0.75rem',
                color: 'var(--text-muted)',
                borderRadius: '6px',
                outline: 'none',
                cursor: 'pointer'
              }}
            >
              <option value={2000}>2.0s / min</option>
              <option value={1000}>1.0s / min</option>
              <option value={500}>0.5s / min (Fast)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <nav style={{ display: 'flex', borderTop: '1px solid var(--border-subtle)', background: 'rgba(10, 15, 29, 0.6)', padding: '0 1.25rem', gap: '0.5rem' }}>
        {[
          { id: 'dashboard', label: 'Command Dashboard', icon: Activity },
          { id: 'events', label: 'Scenario Events & Stress', icon: Sliders },
          { id: 'logs', label: 'Decision Inspector (CNP)', icon: Radio },
          { id: 'replay', label: 'After-Action Replay', icon: History },
          { id: 'comparison', label: 'Strategy Evaluation & Metrics', icon: BarChart3 },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id as any)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.45rem',
                padding: '0.65rem 0.95rem',
                fontSize: '0.825rem',
                fontWeight: isActive ? 600 : 500,
                color: isActive ? 'var(--cyan-bright)' : 'var(--text-muted)',
                border: 'none',
                borderBottom: isActive ? '2px solid var(--cyan-bright)' : '2px solid transparent',
                background: 'transparent',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              <Icon size={15} />
              {tab.label}
            </button>
          );
        })}
      </nav>
    </header>
  );
};
