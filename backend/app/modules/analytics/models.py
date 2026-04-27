import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class KPI(Base):
    __tablename__ = "kpis"

    production_line_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("production_lines.id", ondelete="CASCADE"), nullable=False
    )
    machine_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("machines.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    formula: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # ── Relationships ────────────────────────────────────
    production_line = relationship("ProductionLine", back_populates="kpis")
    values = relationship("KPIValue", back_populates="kpi", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="kpi")


class KPIValue(Base):
    __tablename__ = "kpi_values"

    kpi_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("kpis.id", ondelete="CASCADE"), nullable=False
    )
    simulation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("simulations.id", ondelete="SET NULL"), nullable=True
    )
    value: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()"
    )

    # ── Relationships ────────────────────────────────────
    kpi = relationship("KPI", back_populates="values")
    simulation = relationship("Simulation", back_populates="kpi_values")
