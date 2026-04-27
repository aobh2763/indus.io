from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.exceptions import NotFoundError
from app.modules.identity.models import User
from app.modules.analytics import service
from app.modules.analytics.schemas import (
    KPICreate,
    KPIResponse,
    KPIUpdate,
    KPIValueCreate,
    KPIValueResponse,
)

router = APIRouter(tags=["Analytics"])


# ── KPIs ─────────────────────────────────────────────────
@router.get("/lines/{line_id}/kpis", response_model=list[KPIResponse])
def list_kpis(line_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.get_kpis_by_line(db, line_id)


@router.post("/lines/{line_id}/kpis", response_model=KPIResponse, status_code=201)
def create_kpi(
    line_id: str,
    data: KPICreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_kpi(db, line_id, data)


@router.get("/kpis/{kpi_id}", response_model=KPIResponse)
def get_kpi(kpi_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    kpi = service.get_kpi_by_id(db, kpi_id)
    if not kpi:
        raise NotFoundError("KPI")
    return kpi


@router.put("/kpis/{kpi_id}", response_model=KPIResponse)
def update_kpi(
    kpi_id: str,
    data: KPIUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kpi = service.update_kpi(db, kpi_id, data)
    if not kpi:
        raise NotFoundError("KPI")
    return kpi


@router.delete("/kpis/{kpi_id}", status_code=204)
def delete_kpi(kpi_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    kpi = service.soft_delete_kpi(db, kpi_id)
    if not kpi:
        raise NotFoundError("KPI")


# ── KPI Values ───────────────────────────────────────────
@router.get("/kpis/{kpi_id}/values", response_model=list[KPIValueResponse], tags=["KPI Values"])
def list_values(kpi_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.get_values_by_kpi(db, kpi_id)


@router.post("/kpis/{kpi_id}/values", response_model=KPIValueResponse, status_code=201, tags=["KPI Values"])
def create_value(
    kpi_id: str,
    data: KPIValueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_kpi_value(db, kpi_id, data)
