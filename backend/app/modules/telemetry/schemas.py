import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SensorDataCreate(BaseModel):
    type: str = Field(..., min_length=1)
    value: float
    source: Optional[str] = None
    quality_score: Optional[float] = None


class SensorDataResponse(BaseModel):
    id: uuid.UUID
    machine_id: uuid.UUID
    type: str
    value: float
    source: Optional[str] = None
    quality_score: Optional[float] = None
    timestamp: datetime

    model_config = {"from_attributes": True}
