import uuid

from sqlalchemy.orm import Session

from app.modules.telemetry.models import SensorData
from app.modules.telemetry.schemas import SensorDataCreate


def get_sensor_data_by_machine(db: Session, machine_id: uuid.UUID, limit: int = 100):
    return (
        db.query(SensorData)
        .filter(SensorData.machine_id == machine_id)
        .order_by(SensorData.timestamp.desc())
        .limit(limit)
        .all()
    )


def create_sensor_data(db: Session, machine_id: uuid.UUID, data: SensorDataCreate) -> SensorData:
    sd = SensorData(
        machine_id=machine_id,
        type=data.type,
        value=data.value,
        source=data.source,
        quality_score=data.quality_score,
    )
    db.add(sd)
    db.commit()
    db.refresh(sd)
    return sd


def bulk_create_sensor_data(db: Session, machine_id: uuid.UUID, data_list: list[SensorDataCreate]) -> list[SensorData]:
    records = [
        SensorData(
            machine_id=machine_id,
            type=d.type,
            value=d.value,
            source=d.source,
            quality_score=d.quality_score,
        )
        for d in data_list
    ]
    db.add_all(records)
    db.commit()
    for r in records:
        db.refresh(r)
    return records
