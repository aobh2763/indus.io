import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Simulation(Base):
    __tablename__ = "simulations"

    production_line_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("production_lines.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str | None] = mapped_column(String(20), nullable=True)  # RUNNING / STOPPED / COMPLETED
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Relationships ────────────────────────────────────
    production_line = relationship("ProductionLine", back_populates="simulations")
    logs = relationship("SimulationLog", back_populates="simulation", cascade="all, delete-orphan")
    kpi_values = relationship("KPIValue", back_populates="simulation")
    alerts = relationship("Alert", back_populates="simulation")


class SimulationLog(Base):
    __tablename__ = "simulation_logs"

    # Override: simulation_logs don't need updated_at / deleted_at from Base
    # but we keep them for consistency — they simply won't be used

    simulation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False
    )
    machine_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("machines.id", ondelete="SET NULL"), nullable=True
    )
    level: Mapped[str | None] = mapped_column(String(20), nullable=True)  # INFO / WARNING / ERROR
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Relationships ────────────────────────────────────
    simulation = relationship("Simulation", back_populates="logs")
    machine = relationship("Machine")
