import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.core.permissions import ProductionLineStatus


# ── Production Line ──────────────────────────────────────
class ProductionLineCreate(BaseModel):
    name: str = Field(..., min_length=1)
    status: ProductionLineStatus = ProductionLineStatus.DRAFT


class ProductionLineUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[ProductionLineStatus] = None


class ProductionLineResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    status: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Machine ──────────────────────────────────────────────
class MachineCreate(BaseModel):
    name: str = Field(..., min_length=1)
    process: Optional[str] = None
    subprocess: Optional[str] = None
    manufacturer: Optional[str] = None
    model_reference: Optional[str] = None
    year_introduced: Optional[int] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    position_x: float = 0.0
    position_y: float = 0.0
    parameters: Optional[dict[str, Any]] = None
    is_configured: bool = False


class MachineUpdate(BaseModel):
    name: Optional[str] = None
    process: Optional[str] = None
    subprocess: Optional[str] = None
    manufacturer: Optional[str] = None
    model_reference: Optional[str] = None
    year_introduced: Optional[int] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    parameters: Optional[dict[str, Any]] = None
    is_configured: Optional[bool] = None


class MachineResponse(BaseModel):
    id: uuid.UUID
    production_line_id: uuid.UUID
    name: str
    process: Optional[str] = None
    subprocess: Optional[str] = None
    manufacturer: Optional[str] = None
    model_reference: Optional[str] = None
    year_introduced: Optional[int] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    position_x: float
    position_y: float
    parameters: Optional[dict[str, Any]] = None
    is_configured: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Connection ───────────────────────────────────────────
class ConnectionCreate(BaseModel):
    source_machine_id: uuid.UUID
    target_machine_id: uuid.UUID
    weight: float = 1.0


class ConnectionUpdate(BaseModel):
    weight: Optional[float] = None


class ConnectionResponse(BaseModel):
    id: uuid.UUID
    production_line_id: uuid.UUID
    source_machine_id: uuid.UUID
    target_machine_id: uuid.UUID
    weight: float
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Attribute Definition ─────────────────────────────────
class AttributeDefinitionCreate(BaseModel):
    name: str = Field(..., min_length=1)
    unit: Optional[str] = None
    type: str = Field(..., pattern="^(INPUT|PARAMETER|OUTPUT)$")


class AttributeDefinitionResponse(BaseModel):
    id: uuid.UUID
    name: str
    unit: Optional[str] = None
    type: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Machine Attribute Value ──────────────────────────────
class MachineAttributeValueCreate(BaseModel):
    attribute_id: uuid.UUID
    value: float


class MachineAttributeValueResponse(BaseModel):
    id: uuid.UUID
    machine_id: uuid.UUID
    attribute_id: uuid.UUID
    value: float
    timestamp: datetime

    model_config = {"from_attributes": True}
