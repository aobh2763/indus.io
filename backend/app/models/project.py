from datetime import datetime
import enum
from typing import List
import uuid
from sqlalchemy import Column, ForeignKey, String, Enum as SAEnum, DateTime
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship
from app.db.database import Base

class Visibility(enum.Enum):
    PRIVATE="private"
    PUBLIC="public"



class Project(Base):
    __tablename__ = "project"
    project_id= Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column (String)
    project_manager =Column (UUID(as_uuid=True))
    visibility= Column(SAEnum(Visibility), default=Visibility.PRIVATE)  
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    production_lines= Column(ARRAY(String))
    shift_supervisors= relationship("ProjectShiftSupervisor", backref="project")


class ProjectShiftSupervisor(Base):
    __tablename__ = "project_shift_supervisor"
    project_id = Column(UUID(as_uuid=True), ForeignKey("project.project_id"), primary_key=True)
    user_id    = Column(UUID(as_uuid=True), primary_key=True)
