import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.core.permissions import AlertSeverity, AlertStatus


class AlertCreate(BaseModel):
    production_line_id: uuid.UUID
    machine_id: Optional[uuid.UUID] = None
    kpi_id: Optional[uuid.UUID] = None
    simulation_id: Optional[uuid.UUID] = None
    type: str = Field(..., min_length=1)
    severity: AlertSeverity
    message: str = Field(..., min_length=1)
    status: AlertStatus = AlertStatus.OPEN


class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    acknowledged: Optional[bool] = None
    resolved_at: Optional[datetime] = None


class AlertResponse(BaseModel):
    id: uuid.UUID
    production_line_id: uuid.UUID
    machine_id: Optional[uuid.UUID] = None
    kpi_id: Optional[uuid.UUID] = None
    simulation_id: Optional[uuid.UUID] = None
    type: str
    severity: str
    message: str
    status: str
    acknowledged: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
