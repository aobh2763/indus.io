import uuid

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Project(Base):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    visibility: Mapped[str] = mapped_column(String(20), nullable=False)  # PUBLIC / PRIVATE

    # ── Relationships ────────────────────────────────────
    access_entries = relationship("ProjectAccess", back_populates="project", cascade="all, delete-orphan")
    production_lines = relationship("ProductionLine", back_populates="project", cascade="all, delete-orphan")


class ProjectAccess(Base):
    __tablename__ = "project_access"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_user"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    access_level: Mapped[str] = mapped_column(String(20), nullable=False)  # OWNER / SUPERVISOR / COLLABORATOR / VIEWER
    can_clone: Mapped[bool] = mapped_column(Boolean, default=False)

    # ── Relationships ────────────────────────────────────
    project = relationship("Project", back_populates="access_entries")
    user = relationship("User", backref="project_accesses", lazy="selectin")
