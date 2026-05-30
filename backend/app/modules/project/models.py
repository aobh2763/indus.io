import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
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
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACCEPTED")  # PENDING / ACCEPTED / DECLINED
    invited_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Relationships ────────────────────────────────────
    project = relationship("Project", back_populates="access_entries")
    user = relationship("User", foreign_keys=[user_id], backref="project_accesses", lazy="selectin")
    invited_by = relationship("User", foreign_keys=[invited_by_user_id])

    @property
    def user_name(self) -> str | None:
        return self.user.name if self.user else None

    @property
    def user_email(self) -> str | None:
        return self.user.email if self.user else None

    @property
    def project_name(self) -> str | None:
        return self.project.name if self.project else None


class ProjectNotification(Base):
    __tablename__ = "project_notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True
    )
    access_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("project_access.id", ondelete="SET NULL"), nullable=True
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("User", foreign_keys=[user_id])
    actor = relationship("User", foreign_keys=[actor_user_id])
    project = relationship("Project")
    access = relationship("ProjectAccess")
