import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.modules.analytics.models import KPI, KPIValue
from app.modules.analytics.schemas import KPICreate, KPIUpdate, KPIValueCreate


# ── KPIs ─────────────────────────────────────────────────
def get_kpis_by_line(db: Session, line_id: uuid.UUID):
    return db.query(KPI).filter(KPI.production_line_id == line_id, KPI.deleted_at.is_(None)).all()


def get_kpi_by_id(db: Session, kpi_id: uuid.UUID) -> Optional[KPI]:
    return db.query(KPI).filter(KPI.id == kpi_id, KPI.deleted_at.is_(None)).first()


def create_kpi(db: Session, line_id: uuid.UUID, data: KPICreate) -> KPI:
    kpi = KPI(
        production_line_id=line_id,
        machine_id=data.machine_id,
        name=data.name,
        formula=data.formula,
        target_value=data.target_value,
        unit=data.unit,
    )
    db.add(kpi)
    db.commit()
    db.refresh(kpi)
    return kpi


def update_kpi(db: Session, kpi_id: uuid.UUID, data: KPIUpdate) -> Optional[KPI]:
    kpi = get_kpi_by_id(db, kpi_id)
    if not kpi:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(kpi, field, value)
    db.commit()
    db.refresh(kpi)
    return kpi


def soft_delete_kpi(db: Session, kpi_id: uuid.UUID) -> Optional[KPI]:
    kpi = get_kpi_by_id(db, kpi_id)
    if not kpi:
        return None
    kpi.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return kpi


# ── KPI Values ───────────────────────────────────────────
def get_values_by_kpi(db: Session, kpi_id: uuid.UUID):
    return db.query(KPIValue).filter(KPIValue.kpi_id == kpi_id).order_by(KPIValue.timestamp.desc()).all()


def create_kpi_value(db: Session, kpi_id: uuid.UUID, data: KPIValueCreate) -> KPIValue:
    kv = KPIValue(
        kpi_id=kpi_id,
        simulation_id=data.simulation_id,
        value=data.value,
    )
    db.add(kv)
    db.commit()
    db.refresh(kv)
    return kv
