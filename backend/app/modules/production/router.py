from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.exceptions import NotFoundError
from app.modules.identity.models import User
from app.modules.production import service
from app.modules.production.schemas import (
    ConnectionCreate,
    ConnectionResponse,
    ConnectionUpdate,
    MachineCreate,
    MachineResponse,
    MachineUpdate,
    ProductionLineCreate,
    ProductionLineResponse,
    ProductionLineUpdate,
)

router = APIRouter(tags=["Production"])


# ── Production Lines ─────────────────────────────────────
@router.get("/projects/{project_id}/lines", response_model=list[ProductionLineResponse])
def list_lines(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.get_lines_by_project(db, project_id)


@router.post("/projects/{project_id}/lines", response_model=ProductionLineResponse, status_code=201)
def create_line(
    project_id: str,
    data: ProductionLineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_line(db, project_id, data)


@router.get("/lines/{line_id}", response_model=ProductionLineResponse)
def get_line(line_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    line = service.get_line_by_id(db, line_id)
    if not line:
        raise NotFoundError("Production line")
    return line


@router.put("/lines/{line_id}", response_model=ProductionLineResponse)
def update_line(
    line_id: str,
    data: ProductionLineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    line = service.update_line(db, line_id, data)
    if not line:
        raise NotFoundError("Production line")
    return line


@router.delete("/lines/{line_id}", status_code=204)
def delete_line(line_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    line = service.soft_delete_line(db, line_id)
    if not line:
        raise NotFoundError("Production line")


# ── Machines ─────────────────────────────────────────────
@router.get("/lines/{line_id}/machines", response_model=list[MachineResponse], tags=["Machines"])
def list_machines(line_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.get_machines_by_line(db, line_id)


@router.post("/lines/{line_id}/machines", response_model=MachineResponse, status_code=201, tags=["Machines"])
def create_machine(
    line_id: str,
    data: MachineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_machine(db, line_id, data)


@router.get("/machines/{machine_id}", response_model=MachineResponse, tags=["Machines"])
def get_machine(machine_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    machine = service.get_machine_by_id(db, machine_id)
    if not machine:
        raise NotFoundError("Machine")
    return machine


@router.put("/machines/{machine_id}", response_model=MachineResponse, tags=["Machines"])
def update_machine(
    machine_id: str,
    data: MachineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    machine = service.update_machine(db, machine_id, data)
    if not machine:
        raise NotFoundError("Machine")
    return machine


@router.delete("/machines/{machine_id}", status_code=204, tags=["Machines"])
def delete_machine(machine_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    machine = service.soft_delete_machine(db, machine_id)
    if not machine:
        raise NotFoundError("Machine")


# ── Connections ──────────────────────────────────────────
@router.get("/lines/{line_id}/connections", response_model=list[ConnectionResponse], tags=["Connections"])
def list_connections(line_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.get_connections_by_line(db, line_id)


@router.post("/lines/{line_id}/connections", response_model=ConnectionResponse, status_code=201, tags=["Connections"])
def create_connection(
    line_id: str,
    data: ConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_connection(db, line_id, data)


@router.get("/connections/{connection_id}", response_model=ConnectionResponse, tags=["Connections"])
def get_connection(connection_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conn = service.get_connection_by_id(db, connection_id)
    if not conn:
        raise NotFoundError("Connection")
    return conn


@router.put("/connections/{connection_id}", response_model=ConnectionResponse, tags=["Connections"])
def update_connection(
    connection_id: str,
    data: ConnectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conn = service.update_connection(db, connection_id, data)
    if not conn:
        raise NotFoundError("Connection")
    return conn


@router.delete("/connections/{connection_id}", status_code=204, tags=["Connections"])
def delete_connection(connection_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conn = service.soft_delete_connection(db, connection_id)
    if not conn:
        raise NotFoundError("Connection")
