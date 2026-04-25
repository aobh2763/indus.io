import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.modules.production.models import (
    AttributeDefinition,
    Connection,
    Machine,
    MachineAttributeValue,
    ProductionLine,
)
from app.db.graph import (
    sync_machine_to_graph,
    delete_machine_from_graph,
    sync_connection_to_graph,
    delete_connection_from_graph
)
from app.modules.production.schemas import (
    AttributeDefinitionCreate,
    ConnectionCreate,
    ConnectionUpdate,
    MachineAttributeValueCreate,
    MachineCreate,
    MachineUpdate,
    ProductionLineCreate,
    ProductionLineUpdate,
)


# ── Production Lines ─────────────────────────────────────
def get_lines_by_project(db: Session, project_id: uuid.UUID):
    return db.query(ProductionLine).filter(
        ProductionLine.project_id == project_id, ProductionLine.deleted_at.is_(None)
    ).all()


def get_line_by_id(db: Session, line_id: uuid.UUID) -> Optional[ProductionLine]:
    return db.query(ProductionLine).filter(
        ProductionLine.id == line_id, ProductionLine.deleted_at.is_(None)
    ).first()


def create_line(db: Session, project_id: uuid.UUID, data: ProductionLineCreate) -> ProductionLine:
    line = ProductionLine(
        project_id=project_id,
        name=data.name,
        status=data.status.value if data.status else None,
    )
    db.add(line)
    db.commit()
    db.refresh(line)
    return line


def update_line(db: Session, line_id: uuid.UUID, data: ProductionLineUpdate) -> Optional[ProductionLine]:
    line = get_line_by_id(db, line_id)
    if not line:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "status" and value is not None:
            setattr(line, field, value.value if hasattr(value, "value") else value)
        else:
            setattr(line, field, value)
    db.commit()
    db.refresh(line)
    return line


def soft_delete_line(db: Session, line_id: uuid.UUID) -> Optional[ProductionLine]:
    line = get_line_by_id(db, line_id)
    if not line:
        return None
    line.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return line


# ── Machines ─────────────────────────────────────────────
def get_machines_by_line(db: Session, line_id: uuid.UUID):
    return db.query(Machine).filter(
        Machine.production_line_id == line_id, Machine.deleted_at.is_(None)
    ).all()


def get_machine_by_id(db: Session, machine_id: uuid.UUID) -> Optional[Machine]:
    return db.query(Machine).filter(
        Machine.id == machine_id, Machine.deleted_at.is_(None)
    ).first()


def create_machine(db: Session, line_id: uuid.UUID, data: MachineCreate) -> Machine:
    machine = Machine(
        production_line_id=line_id,
        name=data.name,
        process=data.process,
        subprocess=data.subprocess,
        manufacturer=data.manufacturer,
        model_reference=data.model_reference,
        year_introduced=data.year_introduced,
        description=data.description,
        icon=data.icon,
        position_x=data.position_x,
        position_y=data.position_y,
        parameters=data.parameters,
        is_configured=data.is_configured,
    )
    db.add(machine)
    db.commit()
    db.refresh(machine)
    
    # Sync to Graph
    sync_machine_to_graph(db, machine.id, machine.name, {
        "process": machine.process,
        "manufacturer": machine.manufacturer
    })
    
    return machine


def update_machine(db: Session, machine_id: uuid.UUID, data: MachineUpdate) -> Optional[Machine]:
    machine = get_machine_by_id(db, machine_id)
    if not machine:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(machine, field, value)
    db.commit()
    db.refresh(machine)
    return machine


def soft_delete_machine(db: Session, machine_id: uuid.UUID) -> Optional[Machine]:
    machine = get_machine_by_id(db, machine_id)
    if not machine:
        return None
    machine.deleted_at = datetime.now(timezone.utc)
    db.commit()
    
    # Remove from Graph
    delete_machine_from_graph(db, machine.id)
    
    return machine


# ── Connections ──────────────────────────────────────────
def get_connections_by_line(db: Session, line_id: uuid.UUID):
    return db.query(Connection).filter(
        Connection.production_line_id == line_id, Connection.deleted_at.is_(None)
    ).all()


def get_connection_by_id(db: Session, conn_id: uuid.UUID) -> Optional[Connection]:
    return db.query(Connection).filter(
        Connection.id == conn_id, Connection.deleted_at.is_(None)
    ).first()


def create_connection(db: Session, line_id: uuid.UUID, data: ConnectionCreate) -> Connection:
    conn = Connection(
        production_line_id=line_id,
        source_machine_id=data.source_machine_id,
        target_machine_id=data.target_machine_id,
        weight=data.weight,
    )
    db.add(conn)
    db.commit()
    db.refresh(conn)
    
    # Sync to Graph
    sync_connection_to_graph(db, conn.source_machine_id, conn.target_machine_id, conn.weight)
    
    return conn


def update_connection(db: Session, conn_id: uuid.UUID, data: ConnectionUpdate) -> Optional[Connection]:
    conn = get_connection_by_id(db, conn_id)
    if not conn:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(conn, field, value)
    db.commit()
    db.refresh(conn)
    return conn


def soft_delete_connection(db: Session, conn_id: uuid.UUID) -> Optional[Connection]:
    conn = get_connection_by_id(db, conn_id)
    if not conn:
        return None
    conn.deleted_at = datetime.now(timezone.utc)
    db.commit()
    
    # Remove from Graph
    delete_connection_from_graph(db, conn.source_machine_id, conn.target_machine_id)
    
    return conn


# ── Attribute Definitions ────────────────────────────────
def create_attribute_definition(db: Session, data: AttributeDefinitionCreate) -> AttributeDefinition:
    attr = AttributeDefinition(
        name=data.name,
        unit=data.unit,
        type=data.type,
    )
    db.add(attr)
    db.commit()
    db.refresh(attr)
    return attr


def get_attribute_definitions(db: Session):
    return db.query(AttributeDefinition).all()


# ── Machine Attribute Values ─────────────────────────────
def add_machine_attribute_value(db: Session, machine_id: uuid.UUID, data: MachineAttributeValueCreate) -> MachineAttributeValue:
    val = MachineAttributeValue(
        machine_id=machine_id,
        attribute_id=data.attribute_id,
        value=data.value,
    )
    db.add(val)
    db.commit()
    db.refresh(val)
    return val


def get_attribute_values_by_machine(db: Session, machine_id: uuid.UUID):
    return db.query(MachineAttributeValue).filter(MachineAttributeValue.machine_id == machine_id).all()
