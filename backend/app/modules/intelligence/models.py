import uuid

from sqlalchemy import Boolean, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AIAgent(Base):
    __tablename__ = "ai_agents"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # ── Relationships ────────────────────────────────────
    suggestions = relationship("Suggestion", back_populates="ai_agent")


class Suggestion(Base):
    __tablename__ = "suggestions"

    ai_agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_agents.id", ondelete="SET NULL"), nullable=True
    )
    production_line_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("production_lines.id", ondelete="CASCADE"), nullable=False
    )
    machine_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("machines.id", ondelete="SET NULL"), nullable=True
    )
    type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # Store suggested parameter changes
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    applied: Mapped[bool] = mapped_column(Boolean, default=False)

    # ── Relationships ────────────────────────────────────
    ai_agent = relationship("AIAgent", back_populates="suggestions")
    production_line = relationship("ProductionLine", back_populates="suggestions")
    machine = relationship("Machine")
