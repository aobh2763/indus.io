import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.core.permissions import AccessLevel, Visibility


# ── Project ──────────────────────────────────────────────
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    visibility: Visibility = Visibility.PRIVATE


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[Visibility] = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    visibility: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Project Access ───────────────────────────────────────
class ProjectAccessCreate(BaseModel):
    user_id: uuid.UUID
    access_level: AccessLevel = AccessLevel.VIEWER
    can_clone: bool = False


class ProjectAccessUpdate(BaseModel):
    access_level: Optional[AccessLevel] = None
    can_clone: Optional[bool] = None


class ProjectAccessResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    user_id: uuid.UUID
    access_level: str
    can_clone: bool
    created_at: datetime

    model_config = {"from_attributes": True}
