import React, { useState, useEffect } from 'react';
import {
  History,
  Play,
  Pause,
  SkipBack,
  SkipForward,
} from 'lucide-react';
import type { ReplaySnapshot, ReplayTimelineResponse } from '../types';

import { api } from '../services/api';

interface ReplayScrubberProps {
  onSnapshotLoaded: (snapshot: ReplaySnapshot) => void;
  onExitReplay: () => void;
  currentLiveMinute: number;
}

export const ReplayScrubber: React.FC<ReplayScrubberProps> = ({
  onSnapshotLoaded,
  onExitReplay,
  currentLiveMinute,
}) => {
  const [timeline, setTimeline] = useState<ReplayTimelineResponse | null>(null);
  const [selectedMinute, setSelectedMinute] = useState<number>(0);
  const [snapshot, setSnapshot] = useState<ReplaySnapshot | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [loading, setLoading] = useState(false);

  // Fetch timeline on mount
  useEffect(() => {
    const fetchTimeline = async () => {
      try {
        const tl = await api.getReplayTimeline();
        setTimeline(tl);
        if (tl.recorded_minutes.length > 0) {
          const initMin = tl.recorded_minutes[0];
          setSelectedMinute(initMin);
          loadSnapshot(initMin);
        }
      } catch (err) {
        console.error('Failed to load replay timeline:', err);
      }
    };
    fetchTimeline();
  }, []);

  const loadSnapshot = async (minute: number) => {
    setLoading(true);
    try {
      const snap = await api.getReplaySnapshot(minute);
      setSnapshot(snap);
      onSnapshotLoaded(snap);
    } catch (err) {
      console.error(`Failed to load replay snapshot at minute ${minute}:`, err);
    } finally {
      setLoading(false);
    }
  };

  const handleSliderChange = (minute: number) => {
    setSelectedMinute(minute);
    loadSnapshot(minute);
  };

  const handleStepBack = () => {
    if (!timeline || timeline.recorded_minutes.length === 0) return;
    const curIdx = timeline.recorded_minutes.indexOf(selectedMinute);
    if (curIdx > 0) {
      const prevMin = timeline.recorded_minutes[curIdx - 1];
      handleSliderChange(prevMin);
    }
  };

  const handleStepForward = () => {
    if (!timeline || timeline.recorded_minutes.length === 0) return;
    const curIdx = timeline.recorded_minutes.indexOf(selectedMinute);
    if (curIdx < timeline.recorded_minutes.length - 1) {
      const nextMin = timeline.recorded_minutes[curIdx + 1];
      handleSliderChange(nextMin);
    } else {
      setIsPlaying(false);
    }
  };

  // Replay Auto-Playback loop
  useEffect(() => {
    if (!isPlaying) return;
    const interval = setInterval(() => {
      if (!timeline) return;
      const curIdx = timeline.recorded_minutes.indexOf(selectedMinute);
      if (curIdx < timeline.recorded_minutes.length - 1) {
        const nextMin = timeline.recorded_minutes[curIdx + 1];
        handleSliderChange(nextMin);
      } else {
        setIsPlaying(false);
      }
    }, 1200);

    return () => clearInterval(interval);
  }, [isPlaying, selectedMinute, timeline]);

  const maxRecorded = timeline?.recorded_minutes[timeline.recorded_minutes.length - 1] ?? 0;

  return (
    <div className="glass-panel" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {/* Top Replay Banner */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <History size={20} color="#fbbf24" />
          <div>
            <h2 style={{ fontSize: '1rem', fontWeight: 700, color: '#fef3c7' }}>
              After-Action Historical Replay & Decision Scrubbing
            </h2>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Step backward and forward through deep-copy world state snapshots recorded at every simulation minute.
            </p>
          </div>
        </div>

        <button className="btn btn-warning" onClick={onExitReplay}>
          Return to Live Simulation (T+{currentLiveMinute}m)
        </button>
      </div>

      {/* Scrub Bar & Controls */}
      <div className="glass-card" style={{ padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Inspecting Snapshot:
            </span>
            <span className="mono" style={{ fontSize: '1.2rem', fontWeight: 800, color: '#fbbf24' }}>
              Minute {selectedMinute}
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
              (Recorded total: {timeline?.total_snapshots || 0} states)
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <button
              className="btn btn-secondary"
              onClick={handleStepBack}
              disabled={loading || selectedMinute === 0}
              title="Step backward 1 snapshot"
            >
              <SkipBack size={15} />
            </button>
            <button
              className="btn btn-primary"
              onClick={() => setIsPlaying(!isPlaying)}
              title={isPlaying ? 'Pause replay playback' : 'Play historical snapshots sequentially'}
            >
              {isPlaying ? <Pause size={15} /> : <Play size={15} />}
              {isPlaying ? 'Pause' : 'Play Replay'}
            </button>
            <button
              className="btn btn-secondary"
              onClick={handleStepForward}
              disabled={loading || selectedMinute >= maxRecorded}
              title="Step forward 1 snapshot"
            >
              <SkipForward size={15} />
            </button>
          </div>
        </div>

        {/* Range Slider */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>0m</span>
          <input
            type="range"
            min="0"
            max={maxRecorded}
            step="1"
            value={selectedMinute}
            onChange={(e) => handleSliderChange(Number(e.target.value))}
            style={{
              flex: 1,
              accentColor: '#fbbf24',
              cursor: 'pointer',
              height: '6px',
            }}
          />
          <span className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>{maxRecorded}m</span>
        </div>
      </div>

      {/* Snapshot Summary Cards */}
      {snapshot && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '0.75rem' }}>
          <div className="glass-card" style={{ padding: '0.65rem 0.85rem' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Delivered at T+{selectedMinute}m</div>
            <div className="mono" style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--emerald-safe)' }}>
              {snapshot.kpis.total_delivered_people} pax
            </div>
          </div>
          <div className="glass-card" style={{ padding: '0.65rem 0.85rem' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Onboard Vessels</div>
            <div className="mono" style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--cyan-bright)' }}>
              {snapshot.kpis.total_onboard_people} pax
            </div>
          </div>
          <div className="glass-card" style={{ padding: '0.65rem 0.85rem' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Awaiting Stranded</div>
            <div className="mono" style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--amber-warn)' }}>
              {snapshot.kpis.total_awaiting_people} pax
            </div>
          </div>
          <div className="glass-card" style={{ padding: '0.65rem 0.85rem' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Shelter Free Space</div>
            <div className="mono" style={{ fontSize: '1.25rem', fontWeight: 800, color: snapshot.kpis.shelter_remaining_total === 0 ? 'var(--rose-crit)' : 'var(--text-main)' }}>
              {snapshot.kpis.shelter_remaining_total} spaces
            </div>
          </div>
          <div className="glass-card" style={{ padding: '0.65rem 0.85rem' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Invariants Ok</div>
            <div className="mono" style={{ fontSize: '1.25rem', fontWeight: 800, color: snapshot.invariants_ok ? 'var(--emerald-safe)' : 'var(--rose-crit)' }}>
              {snapshot.invariants_ok ? 'PASSED' : 'VIOLATION'}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
