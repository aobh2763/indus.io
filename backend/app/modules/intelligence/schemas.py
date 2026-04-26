import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── AI Agent ─────────────────────────────────────────────
class AIAgentCreate(BaseModel):
    name: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)
    version: Optional[str] = None


class AIAgentUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    version: Optional[str] = None


class AIAgentResponse(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    version: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Suggestion ───────────────────────────────────────────
class SuggestionCreate(BaseModel):
    ai_agent_id: Optional[uuid.UUID] = None
    machine_id: Optional[uuid.UUID] = None
    type: Optional[str] = None
    description: Optional[str] = None
    payload: Optional[dict] = None
    confidence: Optional[float] = None


class SuggestionUpdate(BaseModel):
    applied: Optional[bool] = None


class SuggestionResponse(BaseModel):
    id: uuid.UUID
    ai_agent_id: Optional[uuid.UUID] = None
    production_line_id: uuid.UUID
    machine_id: Optional[uuid.UUID] = None
    type: Optional[str] = None
    description: Optional[str] = None
    payload: Optional[dict] = None
    confidence: Optional[float] = None
    applied: bool
    created_at: datetime

    model_config = {"from_attributes": True}
