import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── KPI ──────────────────────────────────────────────────
class KPICreate(BaseModel):
    name: str = Field(..., min_length=1)
    machine_id: Optional[uuid.UUID] = None
    formula: Optional[str] = None
    target_value: Optional[float] = None
    unit: Optional[str] = None


class KPIUpdate(BaseModel):
    name: Optional[str] = None
    formula: Optional[str] = None
    target_value: Optional[float] = None
    unit: Optional[str] = None


class KPIResponse(BaseModel):
    id: uuid.UUID
    production_line_id: uuid.UUID
    machine_id: Optional[uuid.UUID] = None
    name: str
    formula: Optional[str] = None
    target_value: Optional[float] = None
    unit: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── KPI Value ────────────────────────────────────────────
class KPIValueCreate(BaseModel):
    simulation_id: Optional[uuid.UUID] = None
    value: float


class KPIValueResponse(BaseModel):
    id: uuid.UUID
    kpi_id: uuid.UUID
    simulation_id: Optional[uuid.UUID] = None
    value: float
    timestamp: datetime

    model_config = {"from_attributes": True}
