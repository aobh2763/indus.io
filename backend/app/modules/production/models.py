import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProductionLine(Base):
    __tablename__ = "production_lines"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str | None] = mapped_column(String(20), nullable=True)  # DRAFT / RUNNING / ARCHIVED

    # ── Relationships ────────────────────────────────────
    project = relationship("Project", back_populates="production_lines")
    machines = relationship("Machine", back_populates="production_line", cascade="all, delete-orphan")
    connections = relationship("Connection", back_populates="production_line", cascade="all, delete-orphan")
    simulations = relationship("Simulation", back_populates="production_line", cascade="all, delete-orphan")
    kpis = relationship("KPI", back_populates="production_line", cascade="all, delete-orphan")
    suggestions = relationship("Suggestion", back_populates="production_line", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="production_line", cascade="all, delete-orphan")


class Machine(Base):
    __tablename__ = "machines"

    production_line_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("production_lines.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    process: Mapped[str | None] = mapped_column(Text, nullable=True)
    subprocess: Mapped[str | None] = mapped_column(Text, nullable=True)
    manufacturer: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    year_introduced: Mapped[int | None] = mapped_column(nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    position_x: Mapped[float] = mapped_column(Float, default=0.0)
    position_y: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Keeping parameters and is_configured as they are useful for simulation logic
    parameters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_configured: Mapped[bool] = mapped_column(Boolean, default=False)

    # ── Relationships ────────────────────────────────────
    production_line = relationship("ProductionLine", back_populates="machines")
    sensor_data = relationship("SensorData", back_populates="machine", cascade="all, delete-orphan")
    attribute_values = relationship("MachineAttributeValue", back_populates="machine", cascade="all, delete-orphan")


class Connection(Base):
    __tablename__ = "connections"

    production_line_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("production_lines.id", ondelete="CASCADE"), nullable=False
    )
    source_machine_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("machines.id", ondelete="CASCADE"), nullable=False
    )
    target_machine_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("machines.id", ondelete="CASCADE"), nullable=False
    )
    weight: Mapped[float] = mapped_column(Float, default=1.0)

    # ── Relationships ────────────────────────────────────
    production_line = relationship("ProductionLine", back_populates="connections")
    source_machine = relationship("Machine", foreign_keys=[source_machine_id], backref="outgoing_connections")
    target_machine = relationship("Machine", foreign_keys=[target_machine_id], backref="incoming_connections")


class AttributeDefinition(Base):
    __tablename__ = "attribute_definitions"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # INPUT / PARAMETER / OUTPUT

    # ── Relationships ────────────────────────────────────
    values = relationship("MachineAttributeValue", back_populates="attribute", cascade="all, delete-orphan")


class MachineAttributeValue(Base):
    __tablename__ = "machine_attribute_values"

    machine_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("machines.id", ondelete="CASCADE"), nullable=False
    )
    attribute_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("attribute_definitions.id", ondelete="CASCADE"), nullable=False
    )
    value: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()"
    )

    # ── Relationships ────────────────────────────────────
    machine = relationship("Machine", back_populates="attribute_values")
    attribute = relationship("AttributeDefinition", back_populates="values")
