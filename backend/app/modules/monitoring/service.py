import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.modules.monitoring.models import Alert
from app.modules.monitoring.schemas import AlertCreate, AlertUpdate


def get_all_alerts(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(Alert)
        .filter(Alert.deleted_at.is_(None))
        .order_by(Alert.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_alerts_by_line(db: Session, line_id: uuid.UUID):
    return db.query(Alert).filter(
        Alert.production_line_id == line_id, Alert.deleted_at.is_(None)
    ).order_by(Alert.created_at.desc()).all()


def get_alert_by_id(db: Session, alert_id: uuid.UUID) -> Optional[Alert]:
    return db.query(Alert).filter(Alert.id == alert_id, Alert.deleted_at.is_(None)).first()


def create_alert(db: Session, data: AlertCreate) -> Alert:
    alert = Alert(
        production_line_id=data.production_line_id,
        machine_id=data.machine_id,
        kpi_id=data.kpi_id,
        simulation_id=data.simulation_id,
        type=data.type,
        severity=data.severity.value,
        message=data.message,
        status=data.status.value,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def update_alert(db: Session, alert_id: uuid.UUID, data: AlertUpdate) -> Optional[Alert]:
    alert = get_alert_by_id(db, alert_id)
    if not alert:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        if field in ("status", "severity") and value is not None:
            setattr(alert, field, value.value if hasattr(value, "value") else value)
        else:
            setattr(alert, field, value)
    db.commit()
    db.refresh(alert)
    return alert


def acknowledge_alert(db: Session, alert_id: uuid.UUID) -> Optional[Alert]:
    alert = get_alert_by_id(db, alert_id)
    if not alert:
        return None
    alert.acknowledged = True
    db.commit()
    db.refresh(alert)
    return alert


def resolve_alert(db: Session, alert_id: uuid.UUID) -> Optional[Alert]:
    alert = get_alert_by_id(db, alert_id)
    if not alert:
        return None
    alert.status = "RESOLVED"
    alert.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    return alert
