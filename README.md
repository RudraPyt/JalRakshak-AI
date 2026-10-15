# JalRakshak AI — Adaptive Flood Rescue Coordination System
**Hackathon Problem Statement 27: Flood Rescue Dispatch — Where Boats, Shelters, and Roads Negotiate in Real Time**

🚀 **Live Frontend (Netlify):** [https://jalrakshak-ai-frontend.netlify.app/](https://jalrakshak-ai-frontend.netlify.app/)  
⚡ **Live Backend API (Render):** [https://jalrakshak-ai-backend.onrender.com/docs](https://jalrakshak-ai-backend.onrender.com/docs)  
🩺 **Health Endpoint:** [https://jalrakshak-ai-backend.onrender.com/health](https://jalrakshak-ai-backend.onrender.com/health)

---

## 1. System Overview

During flood emergencies, static response plans become obsolete within minutes as routes close, boats break down, shelters fill up, and emergency reports conflict. 

**JalRakshak AI** is an autonomous simulation and decision-support platform that coordinates rescue resources in real time. It features:
- **Dynamic Routing Graph:** NetworkX shortest-path planner respecting real-time edge closures, uncertainty penalties, and re-openings.
- **Dual Dispatch Strategies:**
  1. *Centralized Greedy Baseline:* Deterministic dispatcher optimizing urgency, waiting-time anti-starvation bonuses, and capacity constraints.
  2. *Decentralized Multi-Agent System (MAS):* Autonomous agents (Incident, Boat, Route, Shelter, Coordinator) negotiating assignments via the **Contract Net Protocol (CNP)**.
- **Deterministic 7-Step Simulation Loop:** Discrete time-stepped simulation advancing boat movement, passenger boarding, and shelter deliveries.
- **Explainable Decision Logging:** Auditable records documenting why every commitment, reroute, or rejection occurred.
- **After-Action Replay:** Deep-copy snapshot timeline enabling historical step-by-step playback.
- **10 Formal Safety Invariants:** Enforced and verified at every step (no closed-edge traversal, no boat double-booking, no shelter overcapacity, no false completions).

---

## 2. Quickstart & Installation (Windows PowerShell)

### Prerequisites
- Python 3.10+ (Tested on Python 3.14.2)
- Installed dependencies: `fastapi`, `uvicorn`, `networkx`, `pandas`, `pydantic`, `pytest`, `httpx`

### Install Dependencies
```powershell
python -m pip install fastapi uvicorn networkx pandas pydantic pytest httpx
```

### Launch the FastAPI Server
From the workspace root (`Y:\Projects\JalRakshak-AI`):
```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
Once started, access the interactive OpenAPI / Swagger UI at:
👉 **`http://127.0.0.1:8000/docs`**

---

## 3. Running Automated Tests

Run the complete test suite (60 unit, integration, invariant, and API tests):
```powershell
python -m pytest backend/tests/ -v
```

---

## 4. API Endpoints & PowerShell Usage Examples

### 4.1 System Health
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method GET
```

### 4.2 Reset Simulation with Strategy Selection
Reset to clean initial conditions with either `"centralized"` or `"multi_agent"`:
```powershell
# Reset using Decentralized Multi-Agent Strategy
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/simulation/reset" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"strategy": "multi_agent"}'
```

### 4.3 Advance Simulation Clock (Single Step)
Step forward by exactly 1 simulation minute:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/simulation/step" -Method POST
```

### 4.4 Inspect Current World State
Retrieve full world state, boat locations, shelter occupancy, and active commitments:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/simulation/state" -Method GET
```

### 4.5 Manually Inject an Environmental Event
Inject a bridge closure, boat failure, or shelter overflow:
```powershell
# Inject closure of LowBridge edge N2 at current minute
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/events/inject" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{
    "event_type": "road_closure",
    "target_id": "N2",
    "description": "Bridge deck submerged after flash flood"
  }'
```

### 4.6 Inspect Traceable Decision Logs
Filter decision records by action type (`COMMITTED`, `BID_SUBMITTED`, `INVALIDATED`, `REROUTED`, `SERVED`):
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/logs/decisions?limit=20" -Method GET
```

### 4.7 After-Action Replay
Retrieve recorded timeline and view a snapshot at a specific minute:
```powershell
# Get all recorded minutes
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/replay/timeline" -Method GET

# Inspect exact historical state at minute 5
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/replay/snapshot/5" -Method GET
```

### 4.8 Strategy Comparison (Centralized Baseline vs. MAS)
Run a side-by-side benchmark comparing metrics under identical scenarios:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/evaluation/compare" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"simulation_minutes": 15, "include_stretch_events": false}'
```

### 4.9 Run Simultaneous-Failure Stretch Challenge
Triggers bridge closure (`N2`), boat failure (`BOAT03`), and shelter overflow (`SH02`) concurrently at minute 5:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/evaluation/stretch-challenge" -Method POST
```

---

## 5. Repository Structure

```text
Y:\Projects\JalRakshak-AI\
├── boats.csv                    <-- 4 rescue boat resources
├── duplicate_test_labels.csv    <-- Ground-truth deduplication pairs
├── incidents.csv                <-- 12 mock emergency requests
├── road_network.csv             <-- 12 graph edges connecting 11 zones
├── scenario_events.csv          <-- Injected dynamic events
├── shelters.csv                 <-- 4 evacuation shelters
├── README.txt                   <-- Original synthetic dataset disclaimer
├── PROJECT_SPECIFICATION.md     <-- Complete problem statement & spec
├── README.md                    <-- This operational guide
│
└── backend/
    ├── app/
    │   ├── main.py              <-- FastAPI entrypoint
    │   ├── config.py            <-- Path settings & constants
    │   ├── api/                 <-- Endpoints, session manager, schemas
    │   │   ├── session.py       <-- Thread-safe simulation session & replay buffer
    │   │   ├── schemas.py       <-- Pydantic API schemas
    │   │   ├── routes_simulation.py
    │   │   ├── routes_events.py
    │   │   ├── routes_logs.py
    │   │   ├── routes_replay.py
    │   │   └── routes_evaluation.py
    │   ├── core/                <-- Simulation engine & algorithms
    │   │   ├── state.py         <-- Authoritative WorldState & 7-step loop
    │   │   ├── router.py        <-- NetworkX Dijkstra routing & closures
    │   │   ├── clock.py         <-- Discrete simulation clock
    │   │   ├── logger.py        <-- Explainable decision audit logger
    │   │   ├── invariants.py    <-- 10 Safety invariants checker
    │   │   ├── uncertainty.py   <-- Duplicate detector & conflict handler
    │   │   ├── metrics.py       <-- Evaluation metrics & Jain's fairness
    │   │   └── data_loader.py   <-- CSV validation & spatial mapper
    │   ├── models/              <-- Pydantic data schemas
    │   │   ├── enums.py, graph.py, incident.py, boat.py, shelter.py, event.py, assignment.py, decision_log.py, agent.py
    │   ├── agents/              <-- Multi-Agent System (CNP)
    │   │   ├── incident_agent.py, boat_agent.py, route_agent.py, shelter_agent.py, coordinator.py
    │   └── dispatchers/         <-- Dual dispatch strategies
    │       ├── base.py, centralized.py, multi_agent.py
    └── tests/                   <-- 60 Automated Pytest Tests
│
└── frontend/                    <-- Phase 6: React + TypeScript + Vite Dashboard
    ├── src/
    │   ├── components/          <-- Modular Command Center Components
    │   │   ├── Header.tsx       <-- Top controls, strategy switcher, clock & disclaimer
    │   │   ├── KPIBanner.tsx    <-- 6 Vital operational KPI cards & invariants
    │   │   ├── SimulationMap.tsx<-- Interactive SVG graph map of zones, routes, boats, pins
    │   │   ├── InspectorDrawer.tsx <-- Detail drawer for boats, incidents, shelters, edges
    │   │   ├── IncidentPanel.tsx<-- Triage table with filters, search, and bottleneck alerts
    │   │   ├── ResourcePanel.tsx<-- Shelter capacity progress bars & boat fleet status
    │   │   ├── DecisionInspector.tsx <-- Real Contract Net Protocol audit trail feed
    │   │   ├── EventControls.tsx<-- Dynamic scenario event injector & stretch trigger
    │   │   ├── ReplayScrubber.tsx <-- Historical snapshot timeline scrubber
    │   │   └── StrategyComparison.tsx <-- Recharts benchmark graphs & metrics table
    │   ├── services/api.ts      <-- Type-safe API client for FastAPI backend
    │   ├── types/index.ts       <-- TypeScript data models mirroring backend
    │   ├── index.css            <-- Glassmorphic tactical dark theme design system
    │   ├── App.tsx              <-- Root application view and state coordinator
    │   └── main.tsx
    ├── package.json
    └── vite.config.ts           <-- Proxy configuration to http://127.0.0.1:8000
```

---

## 6. Frontend Dashboard (Phase 6)

The frontend is a modern, responsive web application titled **"JalRakshak AI — Flood Rescue Command Center"**.

### Tech Stack
- **Framework:** React 19 + TypeScript + Vite
- **Data Visualization:** Recharts for comparative strategy evaluation charts
- **Mapping & Network Visualization:** Custom interactive SVG graph visualization tailored specifically for the 11-zone synthetic topology
- **Icons & Styling:** Lucide-React + Glassmorphic Tactical Dark Theme (`index.css`)

### Frontend Installation & Launch (Windows PowerShell)

```powershell
# Navigate to the frontend directory
cd Y:\Projects\JalRakshak-AI\frontend

# Install frontend dependencies (if not already installed)
npm install

# Start the Vite development server
npm run dev

# Or build for production
npm run build
```

Once running:
- **Frontend Dashboard URL:** 👉 **`http://localhost:5173/`**
- **Backend API Documentation:** 👉 **`http://127.0.0.1:8000/docs`**

---

## 7. Step-by-Step Demo Walkthrough: Simultaneous-Failure Stretch Challenge

Follow these steps in the Frontend Command Center or via PowerShell to demonstrate dynamic multi-agent resilience:

1. **Open the Dashboard:** Navigate to `http://localhost:5173/`. Observe that clock is at `T+0m`, strategy is `Centralized Baseline`, and all 6 KPI cards show initial conditions (115 awaiting, 26 initial shelter capacity free, 0 violations).
2. **Select Dispatch Strategy:** Click `"Decentralized MAS (CNP)"` in the top bar. Notice the purple theme badge and activation of the Contract Net Protocol dispatcher.
3. **Advance to Minute 4:** Click `"Step (+1m)"` four times (or toggle `"Auto"`). Observe boats `BOAT01`, `BOAT02`, `BOAT03`, and `BOAT04` deploying to urgent incidents, embarking passengers, and moving toward designated shelters.
4. **Trigger the Simultaneous Failure Challenge:**
   - Click the **"Scenario Events & Stress"** tab.
   - Click the red button: **"Trigger Simultaneous Stretch Challenge"**.
   - This executes 3 concurrent catastrophes at minute 5:
     1. Road Closure: Bridge `N2` (`LowBridge`) washed out by flood surge.
     2. Boat Breakdown: Heavy-capacity vessel `BOAT03` engine stalled by debris.
     3. Shelter Overflow: `SH02` (`CommunityHall`) overrun by unscheduled refugees.
5. **Inspect Dynamic Replanning:**
   - Step forward to minute 6 and 7.
   - On the **Simulation Map**, edge `N2` switches to dashed hazard crimson with a warning badge.
   - Boat `BOAT03` enters failed red status.
   - Check the **"Decision Inspector (CNP)"** tab: see real audit logs showing `INVALIDATED` commitments, local `PROPOSAL` re-announcements, rerouting around `LowBridge` via `EastColony`/`ClinicQuarter`, and shelter re-negotiation to `SH01` and `SH03`.
6. **Observe Truthful Bottleneck Handling:**
   - Notice that once available shelter capacity drops to 0, remaining requests are truthfully held as `UNMET_SHELTER_BOTTLENECK`. The system never fabricates false completions or exceeds authorized shelter occupancy.
7. **Scrub Replay History:**
   - Click the **"After-Action Replay"** tab. Use the slider to scrub backward to minute 0, then forward through minutes 1–7 to inspect exact recorded states without mutating the active simulation.
8. **View Objective Strategy Benchmarks:**
   - Click the **"Strategy Evaluation & Metrics"** tab. View the Recharts comparison charts and Jain's fairness index demonstrating Centralized Baseline vs. Decentralized Multi-Agent trade-offs.

---

## 8. Remaining Limitations and Known Defects

1. **Synthetic Coordinate Grid:** Coordinates $(x, y) \in [0.2, 3.2]$ represent an abstract synthetic disaster network from Hackathon Problem Statement 27, not real-world GPS coordinates (WGS84).
2. **Fixed Fleet Size:** The fleet consists of 4 simulated boats. During cascading disasters, boat availability is the primary pacing constraint.
3. **Shelter Capacity Deficit:** 115 affected citizens vs. 26 maximum shelter spaces (reducing to 20 during overflow events) makes a 100% evacuation rate mathematically impossible without external regional relief. JalRakshak AI truthfully highlights this bottleneck.

