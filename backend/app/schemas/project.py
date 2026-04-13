from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from app.models.project import Visibility

class ProjectCreate(BaseModel):
    name: str
    project_manager: UUID
    visibility: Visibility = Visibility.PRIVATE
    production_lines: Optional[List[str]] = []
    shift_supervisor_ids: List[UUID] = [] 
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Project Alpha",
                "project_manager": "123e4567-e89b-12d3-a456-426614174000",
                "visibility": "public",
                "production_lines": "Line A",
                "shift_supervisor_ids": [
                    "123e4567-e89b-12d3-a456-426614174001",
                    "123e4567-e89b-12d3-a456-426614174002"
                ]
            }
        }}
    
class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    visibility: Optional[Visibility] = None
    production_lines: Optional[List[str]] = []
    shift_supervisor_ids: Optional[List[UUID]] = None
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Project Alpha",
                "visibility": "public",
                "production_lines": "Line A",
                "shift_supervisor_ids": [
                    "123e4567-e89b-12d3-a456-426614174001",
                    "123e4567-e89b-12d3-a456-426614174002"
                ]
            }
        }}

class ProjectOut(BaseModel):
    project_id: UUID
    name: str
    project_manager: UUID
    visibility: Visibility
    production_lines: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True