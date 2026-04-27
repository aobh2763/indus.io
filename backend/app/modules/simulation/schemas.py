import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.core.permissions import LogLevel, SimulationStatus


# ── Simulation ───────────────────────────────────────────
class SimulationCreate(BaseModel):
    status: SimulationStatus = SimulationStatus.RUNNING


class SimulationUpdate(BaseModel):
    status: Optional[SimulationStatus] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class SimulationResponse(BaseModel):
    id: uuid.UUID
    production_line_id: uuid.UUID
    status: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Simulation Log ───────────────────────────────────────
class SimulationLogCreate(BaseModel):
    machine_id: Optional[uuid.UUID] = None
    level: LogLevel = LogLevel.INFO
    message: Optional[str] = None


class SimulationLogResponse(BaseModel):
    id: uuid.UUID
    simulation_id: uuid.UUID
    machine_id: Optional[uuid.UUID] = None
    level: Optional[str] = None
    message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
