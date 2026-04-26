from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.modules.identity.models import User
from app.modules.telemetry import service
from app.modules.telemetry.schemas import SensorDataCreate, SensorDataResponse

router = APIRouter(tags=["Telemetry"])


@router.get("/machines/{machine_id}/sensor-data", response_model=list[SensorDataResponse])
def list_sensor_data(
    machine_id: str,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.get_sensor_data_by_machine(db, machine_id, limit)


@router.post("/machines/{machine_id}/sensor-data", response_model=SensorDataResponse, status_code=201)
def create_sensor_data(
    machine_id: str,
    data: SensorDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_sensor_data(db, machine_id, data)


@router.post("/machines/{machine_id}/sensor-data/bulk", response_model=list[SensorDataResponse], status_code=201)
def bulk_create_sensor_data(
    machine_id: str,
    data_list: list[SensorDataCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.bulk_create_sensor_data(db, machine_id, data_list)
