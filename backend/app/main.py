"""Main FastAPI application for JalRakshak AI.

Adaptive Flood Rescue Coordination System — Official Problem Statement 27.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.schemas import HealthResponse
from .api.routes_simulation import router as simulation_router
from .api.routes_events import router as events_router
from .api.routes_logs import router as logs_router
from .api.routes_replay import router as replay_router
from .api.routes_evaluation import router as evaluation_router


app = FastAPI(
    title="JalRakshak AI — Adaptive Flood Rescue Coordination System",
    description=(
        "Autonomous simulation and decision-support API for Problem Statement 27: "
        "Dynamic replanning over a changing road/water graph, multi-agent negotiation (CNP), "
        "uncertainty handling, capacity invariants, and after-action replay."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for local Vite frontend and web development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(simulation_router)
app.include_router(events_router)
app.include_router(logs_router)
app.include_router(replay_router)
app.include_router(evaluation_router)


@app.get("/health", response_model=HealthResponse, tags=["System Health"])
def health_check():
    """System health check endpoint verifying backend availability."""
    return HealthResponse(
        status="ok",
        version="0.1.0",
        service="JalRakshak AI — Adaptive Flood Rescue Coordination API",
    )


@app.get("/", tags=["System Health"])
def root():
    """Root endpoint providing system identity and interactive documentation link."""
    return {
        "project": "JalRakshak AI",
        "description": "Adaptive Flood Rescue Coordination System (Hackathon Problem Statement 27)",
        "version": "0.1.0",
        "docs_url": "/docs",
        "health_url": "/health",
        "simulation_endpoints": {
            "state": "GET /api/simulation/state",
            "step": "POST /api/simulation/step",
            "reset": "POST /api/simulation/reset",
            "events": "GET /api/events",
            "inject_event": "POST /api/events/inject",
            "decision_logs": "GET /api/logs/decisions",
            "replay_timeline": "GET /api/replay/timeline",
            "evaluation_compare": "POST /api/evaluation/compare",
            "stretch_challenge": "POST /api/evaluation/stretch-challenge",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
