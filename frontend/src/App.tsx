import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { KPIBanner } from './components/KPIBanner';
import { SimulationMap } from './components/SimulationMap';
import { InspectorDrawer } from './components/InspectorDrawer';
import { IncidentPanel } from './components/IncidentPanel';
import { ResourcePanel } from './components/ResourcePanel';
import { DecisionInspector } from './components/DecisionInspector';
import { EventControls } from './components/EventControls';
import { ReplayScrubber } from './components/ReplayScrubber';
import { StrategyComparison } from './components/StrategyComparison';
import type {
  SimulationStateResponse,
  ReplaySnapshot,
  Incident,
  Boat,
  Shelter,
} from './types';
import { api } from './services/api';
import { AlertTriangle } from 'lucide-react';


export const App: React.FC = () => {
  const [worldState, setWorldState] = useState<SimulationStateResponse | null>(null);
  const [replaySnapshot, setReplaySnapshot] = useState<ReplaySnapshot | null>(null);
  const [isReplayActive, setIsReplayActive] = useState(false);

  const [activeTab, setActiveTab] = useState<'dashboard' | 'replay' | 'comparison' | 'events' | 'logs'>('dashboard');
  const [strategy, setStrategy] = useState<'centralized' | 'multi_agent'>('centralized');
  const [isRunning, setIsRunning] = useState(false);
  const [autoPlaySpeed, setAutoPlaySpeed] = useState(2000);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isConnected, setIsConnected] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Inspector Drawer Selection
  const [selectedEntity, setSelectedEntity] = useState<{
    type: 'boat' | 'incident' | 'shelter' | 'edge' | 'zone';
    data: any;
  } | null>(null);

  // Poll / Fetch authoritative state from backend
  const fetchState = async () => {
    try {
      const state = await api.getSimulationState();
      setWorldState(state);
      setStrategy(state.strategy);
      setIsConnected(true);
      setError(null);
    } catch (err: any) {
      setIsConnected(false);
      setError(err.message || 'Cannot connect to JalRakshak AI backend API.');
    }
  };

  // Initial load
  useEffect(() => {
    fetchState();
  }, []);

  // Step Simulation (+1 min)
  const handleStep = async () => {
    if (isProcessing) return;
    setIsProcessing(true);
    try {
      await api.stepSimulation();
      await fetchState();
    } catch (err: any) {
      setError(`Step failed: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Reset Simulation
  const handleReset = async () => {
    if (isProcessing) return;
    setIsProcessing(true);
    setIsRunning(false);
    try {
      const resetState = await api.resetSimulation(strategy);
      setWorldState(resetState);
      setSelectedEntity(null);
      if (isReplayActive) {
        setIsReplayActive(false);
        setReplaySnapshot(null);
      }
      setError(null);
    } catch (err: any) {
      setError(`Reset failed: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Strategy change
  const handleStrategyChange = async (newStrategy: 'centralized' | 'multi_agent') => {
    if (isProcessing || newStrategy === strategy) return;
    setIsProcessing(true);
    setIsRunning(false);
    try {
      setStrategy(newStrategy);
      const resetState = await api.resetSimulation(newStrategy);
      setWorldState(resetState);
      setSelectedEntity(null);
      setError(null);
    } catch (err: any) {
      setError(`Strategy switch failed: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Toggle Auto-play
  const handleTogglePlay = () => {
    setIsRunning((prev) => !prev);
  };

  // Auto-play interval loop
  useEffect(() => {
    if (!isRunning || isReplayActive) return;

    const interval = setInterval(async () => {
      if (isProcessing) return;
      setIsProcessing(true);
      try {
        await api.stepSimulation();
        await fetchState();
      } catch (err: any) {
        setIsRunning(false);
        setError(`Auto-simulation stopped due to error: ${err.message}`);
      } finally {
        setIsProcessing(false);
      }
    }, autoPlaySpeed);

    return () => clearInterval(interval);
  }, [isRunning, autoPlaySpeed, isProcessing, isReplayActive]);

  // Tab switch
  const handleTabChange = (tab: 'dashboard' | 'replay' | 'comparison' | 'events' | 'logs') => {
    setActiveTab(tab);
    if (tab === 'replay') {
      setIsReplayActive(true);
      setIsRunning(false);
    }
  };


  // Exit Replay mode
  const handleExitReplay = () => {
    setIsReplayActive(false);
    setReplaySnapshot(null);
    setActiveTab('dashboard');
    fetchState();
  };

  // Select entities from map or tables
  const handleSelectEntity = (type: 'boat' | 'incident' | 'shelter' | 'edge' | 'zone', data: any) => {
    setSelectedEntity({ type, data });
  };

  // Determine active view data (Live vs Replay)
  const activeMinute = isReplayActive && replaySnapshot ? replaySnapshot.minute : worldState?.minute ?? 0;
  const activeKpis = isReplayActive && replaySnapshot ? replaySnapshot.kpis : worldState?.kpis;
  const activeBoats = isReplayActive && replaySnapshot ? replaySnapshot.boats : worldState?.boats ?? [];
  const activeShelters = isReplayActive && replaySnapshot ? replaySnapshot.shelters : worldState?.shelters ?? [];
  const activeIncidents = isReplayActive && replaySnapshot ? replaySnapshot.incidents : worldState?.incidents ?? [];
  const activeEdges = isReplayActive && replaySnapshot ? replaySnapshot.edges : worldState?.edges ?? [];
  const activeZones = worldState?.zones ?? [];
  const activeAssignments = isReplayActive && replaySnapshot ? replaySnapshot.assignments : worldState?.active_assignments ?? [];

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Header & Simulation Controls */}
      <Header
        minute={activeMinute}
        isRunning={isRunning}
        strategy={strategy}
        activeTab={activeTab}
        isConnected={isConnected}
        autoPlaySpeed={autoPlaySpeed}
        onTabChange={handleTabChange}
        onStrategyChange={handleStrategyChange}
        onStep={handleStep}
        onTogglePlay={handleTogglePlay}
        onReset={handleReset}
        onSpeedChange={setAutoPlaySpeed}
        isProcessing={isProcessing}
        isReplayActive={isReplayActive}
        onExitReplay={handleExitReplay}
      />

      {/* Error alert toast */}
      {error && (
        <div style={{
          background: 'rgba(244, 63, 94, 0.9)',
          color: '#ffffff',
          padding: '0.6rem 1.25rem',
          fontSize: '0.8rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          zIndex: 100
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertTriangle size={16} />
            <span>{error}</span>
          </div>
          <button
            onClick={() => setError(null)}
            style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer', fontWeight: 'bold' }}
          >
            ✕
          </button>
        </div>
      )}

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: '1.25rem', maxWidth: '1680px', margin: '0 auto', width: '100%' }}>
        {/* KPI Banner always visible on live and replay */}
        {activeKpis && (
          <KPIBanner
            kpis={activeKpis}
            invariantsPassed={isReplayActive && replaySnapshot ? replaySnapshot.invariants_ok : true}
          />
        )}

        {/* TAB 1: COMMAND DASHBOARD */}
        {activeTab === 'dashboard' && (
          <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.35fr) minmax(360px, 1fr)', gap: '1.25rem' }}>
            {/* Left Column: Interactive Simulation Map & Inspector Drawer */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <SimulationMap
                zones={activeZones}
                edges={activeEdges}
                boats={activeBoats as Boat[]}
                shelters={activeShelters as Shelter[]}
                incidents={activeIncidents as Incident[]}
                activeAssignments={activeAssignments}
                selectedEntity={selectedEntity}
                onSelectEntity={handleSelectEntity}
              />

              {/* Inspector Drawer under map if an entity is selected */}
              {selectedEntity && (
                <InspectorDrawer
                  selection={selectedEntity}
                  onClose={() => setSelectedEntity(null)}
                />
              )}
            </div>

            {/* Right Column: Split Panels for Incidents & Resources */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', height: '620px' }}>
              <div style={{ flex: 1.1, minHeight: '300px' }}>
                <IncidentPanel
                  incidents={activeIncidents as Incident[]}
                  onSelectIncident={(inc) => handleSelectEntity('incident', inc)}
                  selectedIncidentId={selectedEntity?.type === 'incident' ? selectedEntity.data.incident_id : undefined}
                />
              </div>

              <div style={{ flex: 0.9, minHeight: '260px' }}>
                <ResourcePanel
                  boats={activeBoats as Boat[]}
                  shelters={activeShelters as Shelter[]}
                  onSelectBoat={(b) => handleSelectEntity('boat', b)}
                  onSelectShelter={(s) => handleSelectEntity('shelter', s)}
                  selectedBoatId={selectedEntity?.type === 'boat' ? selectedEntity.data.boat_id : undefined}
                  selectedShelterId={selectedEntity?.type === 'shelter' ? selectedEntity.data.shelter_id : undefined}
                />
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: SCENARIO EVENTS & STRETCH CHALLENGE */}
        {activeTab === 'events' && (
          <EventControls
            currentMinute={worldState?.minute ?? 0}
            edges={worldState?.edges ?? []}
            boats={worldState?.boats ?? []}
            shelters={worldState?.shelters ?? []}
            onEventApplied={fetchState}
          />
        )}

        {/* TAB 3: DECISION INSPECTOR (CNP LOGS) */}
        {activeTab === 'logs' && (
          <div style={{ height: '700px' }}>
            <DecisionInspector currentMinute={worldState?.minute ?? 0} />
          </div>
        )}

        {/* TAB 4: AFTER-ACTION REPLAY */}
        {activeTab === 'replay' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <ReplayScrubber
              currentLiveMinute={worldState?.minute ?? 0}
              onSnapshotLoaded={(snap) => setReplaySnapshot(snap)}
              onExitReplay={handleExitReplay}
            />

            {/* Replay State Visualization */}
            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.35fr) minmax(360px, 1fr)', gap: '1.25rem' }}>
              <SimulationMap
                zones={activeZones}
                edges={activeEdges}
                boats={activeBoats as Boat[]}
                shelters={activeShelters as Shelter[]}
                incidents={activeIncidents as Incident[]}
                activeAssignments={activeAssignments}
                selectedEntity={selectedEntity}
                onSelectEntity={handleSelectEntity}
              />

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', height: '620px' }}>
                <IncidentPanel
                  incidents={activeIncidents as Incident[]}
                  onSelectIncident={(inc) => handleSelectEntity('incident', inc)}
                  selectedIncidentId={selectedEntity?.type === 'incident' ? selectedEntity.data.incident_id : undefined}
                />
                {selectedEntity && (
                  <InspectorDrawer
                    selection={selectedEntity}
                    onClose={() => setSelectedEntity(null)}
                  />
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 5: STRATEGY EVALUATION & BENCHMARKS */}
        {activeTab === 'comparison' && (
          <StrategyComparison />
        )}
      </main>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid var(--border-subtle)',
        background: 'rgba(7, 11, 20, 0.85)',
        padding: '0.75rem 1.25rem',
        fontSize: '0.75rem',
        color: 'var(--text-dim)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.5rem',
      }}>
        <div>
          JalRakshak AI — Adaptive Flood Rescue Coordination System (Problem Statement 27)
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <span>Contract Net Protocol (CNP)</span>
          <span>Dijkstra Shortest Path</span>
          <span>10 Formal Safety Invariants</span>
          <span>FastAPI + React 19 + TypeScript</span>
        </div>
      </footer>
    </div>
  );
};

export default App;
