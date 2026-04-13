from datetime import datetime
from enum import Enum
from app.db.database import Base
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

class User(Base):
    __tablename__= "users"
    user_id = Column(UUID(as_uuid=True), primary_key=True)
    name= Column(String, nullable=False)
    email= Column(String, unique=True, nullable=False)
    password= Column(String, nullable=False)
    created_at = Column(datetime)
    updated_at = Column(datetime)
