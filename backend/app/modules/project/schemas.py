import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.core.permissions import AccessLevel, AccessStatus, Visibility


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
    current_user_access_level: Optional[str] = None
    current_user_can_clone: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Project Access ───────────────────────────────────────
class ProjectAccessCreate(BaseModel):
    user_id: Optional[uuid.UUID] = None
    email: Optional[EmailStr] = None
    access_level: AccessLevel = AccessLevel.VIEWER
    can_clone: bool = False

    @model_validator(mode="after")
    def require_user_reference(self):
        if not self.user_id and not self.email:
            raise ValueError("Provide user_id or email")
        return self


class ProjectAccessUpdate(BaseModel):
    access_level: Optional[AccessLevel] = None
    can_clone: Optional[bool] = None


class ProjectAccessResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    project_name: Optional[str] = None
    user_id: uuid.UUID
    invited_by_user_id: Optional[uuid.UUID] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    access_level: str
    can_clone: bool
    status: str = AccessStatus.ACCEPTED.value
    accepted_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectNotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    actor_user_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    access_id: Optional[uuid.UUID] = None
    type: str
    title: str
    message: str
    read_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
