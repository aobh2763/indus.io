from fastapi import APIRouter

from app.modules.identity.router import router as identity_router
from app.modules.project.router import router as project_router
from app.modules.production.router import router as production_router
from app.modules.simulation.router import router as simulation_router
from app.modules.analytics.router import router as analytics_router
from app.modules.telemetry.router import router as telemetry_router
from app.modules.intelligence.router import router as intelligence_router
from app.modules.monitoring.router import router as monitoring_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(identity_router)
api_router.include_router(project_router)
api_router.include_router(production_router)
api_router.include_router(simulation_router)
api_router.include_router(analytics_router)
api_router.include_router(telemetry_router)
api_router.include_router(intelligence_router)
api_router.include_router(monitoring_router)
