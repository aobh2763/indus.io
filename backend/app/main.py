from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.database import engine

# ── Import ALL models so SQLAlchemy registers them ───────
from app.modules.identity import models as _identity_models  # noqa: F401
from app.modules.project import models as _project_models  # noqa: F401
from app.modules.production import models as _production_models  # noqa: F401
from app.modules.simulation import models as _simulation_models  # noqa: F401
from app.modules.analytics import models as _analytics_models  # noqa: F401
from app.modules.telemetry import models as _telemetry_models  # noqa: F401
from app.modules.intelligence import models as _intelligence_models  # noqa: F401
from app.modules.monitoring import models as _monitoring_models  # noqa: F401

# ── Create all tables ────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── FastAPI app ──────────────────────────────────────────
app = FastAPI(
    title="indus.io Backend API",
    description="Backend for the Production Line Simulation Platform — "
                "Industrial simulation, real-time telemetry, AI-driven suggestions, and KPI analytics.",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Auth", "description": "Registration and login"},
        {"name": "Users", "description": "User management"},
        {"name": "Projects", "description": "Project workspaces"},
        {"name": "Project Access", "description": "Fine-grained project permissions"},
        {"name": "Production", "description": "Production lines"},
        {"name": "Machines", "description": "Machine nodes in the production graph"},
        {"name": "Connections", "description": "Edges between machines"},
        {"name": "Simulations", "description": "Simulation execution"},
        {"name": "Simulation Engine", "description": "Start / stop / complete simulations"},
        {"name": "Simulation Logs", "description": "Simulation event logs"},
        {"name": "Analytics", "description": "KPI definitions"},
        {"name": "KPI Values", "description": "KPI time-series data"},
        {"name": "Telemetry", "description": "Real-time sensor data"},
        {"name": "AI Agents", "description": "AI module management"},
        {"name": "Suggestions", "description": "AI-generated recommendations"},
        {"name": "Alerts", "description": "Anomaly and threshold alerts"},
    ],
)

# ── CORS ─────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount API router ─────────────────────────────────────
app.include_router(api_router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}