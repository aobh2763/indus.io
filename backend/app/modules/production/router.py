from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.permissions import AccessLevel, AccessStatus, GlobalRole, Visibility
from app.modules.identity.models import User
from app.modules.project.models import Project, ProjectAccess
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

router = APIRouter()


def _project_access(db: Session, project_id: str, current_user: User) -> ProjectAccess | None:
    return (
        db.query(ProjectAccess)
        .filter(
            ProjectAccess.project_id == project_id,
            ProjectAccess.user_id == current_user.id,
            ProjectAccess.status == AccessStatus.ACCEPTED.value,
            ProjectAccess.deleted_at.is_(None),
        )
        .first()
    )


def ensure_project_read(db: Session, project_id: str, current_user: User):
    if current_user.role == GlobalRole.ADMIN.value:
        return
    project = db.query(Project).filter(Project.id == project_id, Project.deleted_at.is_(None)).first()
    if project and project.visibility == Visibility.PUBLIC.value:
        return
    if not _project_access(db, project_id, current_user):
        raise ForbiddenError("You do not have access to this project")


def ensure_project_write(db: Session, project_id: str, current_user: User, require_clone: bool = False):
    if current_user.role == GlobalRole.ADMIN.value:
        return
    access = _project_access(db, project_id, current_user)
    if not access:
        raise ForbiddenError("You do not have access to this project")
    if require_clone and access.access_level != AccessLevel.OWNER.value and not access.can_clone:
        raise ForbiddenError("You are not allowed to clone or create production lines for this project")
    if access.access_level not in [AccessLevel.OWNER.value, AccessLevel.COLLABORATOR.value]:
        raise ForbiddenError("You are not allowed to modify this project")


def ensure_line_read(db: Session, line_id: str, current_user: User):
    line = service.get_line_by_id(db, line_id)
    if not line:
        raise NotFoundError("Production line")
    ensure_project_read(db, str(line.project_id), current_user)
    return line


def ensure_line_write(db: Session, line_id: str, current_user: User):
    line = service.get_line_by_id(db, line_id)
    if not line:
        raise NotFoundError("Production line")
    ensure_project_write(db, str(line.project_id), current_user)
    return line


# ── Production Lines ─────────────────────────────────────
@router.get("/projects/{project_id}/lines", response_model=list[ProductionLineResponse], tags=["Production Lines"])
def list_lines(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_project_read(db, project_id, current_user)
    return service.get_lines_by_project(db, project_id)


@router.post("/projects/{project_id}/lines", response_model=ProductionLineResponse, status_code=201, tags=["Production Lines"])
def create_line(
    project_id: str,
    data: ProductionLineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_project_write(db, project_id, current_user)
    return service.create_line(db, project_id, data)


@router.get("/lines/{line_id}", response_model=ProductionLineResponse, tags=["Production Lines"])
def get_line(line_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ensure_line_read(db, line_id, current_user)


@router.put("/lines/{line_id}", response_model=ProductionLineResponse, tags=["Production Lines"])
def update_line(
    line_id: str,
    data: ProductionLineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_line_write(db, line_id, current_user)
    line = service.update_line(db, line_id, data)
    if not line:
        raise NotFoundError("Production line")
    return line


@router.delete("/lines/{line_id}", status_code=204, tags=["Production Lines"])
def delete_line(line_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_line_write(db, line_id, current_user)
    line = service.soft_delete_line(db, line_id)
    if not line:
        raise NotFoundError("Production line")


# ── Machines ─────────────────────────────────────────────
@router.get("/lines/{line_id}/machines", response_model=list[MachineResponse], tags=["Machines"])
def list_machines(line_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_line_read(db, line_id, current_user)
    return service.get_machines_by_line(db, line_id)


@router.post("/lines/{line_id}/machines", response_model=MachineResponse, status_code=201, tags=["Machines"])
def create_machine(
    line_id: str,
    data: MachineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_line_write(db, line_id, current_user)
    return service.create_machine(db, line_id, data)


@router.get("/machines/{machine_id}", response_model=MachineResponse, tags=["Machines"])
def get_machine(machine_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    machine = service.get_machine_by_id(db, machine_id)
    if not machine:
        raise NotFoundError("Machine")
    ensure_line_read(db, str(machine.production_line_id), current_user)
    return machine


@router.put("/machines/{machine_id}", response_model=MachineResponse, tags=["Machines"])
def update_machine(
    machine_id: str,
    data: MachineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = service.get_machine_by_id(db, machine_id)
    if not existing:
        raise NotFoundError("Machine")
    ensure_line_write(db, str(existing.production_line_id), current_user)
    machine = service.update_machine(db, machine_id, data)
    return machine


@router.delete("/machines/{machine_id}", status_code=204, tags=["Machines"])
def delete_machine(machine_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    machine = service.get_machine_by_id(db, machine_id)
    if not machine:
        raise NotFoundError("Machine")
    ensure_line_write(db, str(machine.production_line_id), current_user)
    machine = service.soft_delete_machine(db, machine_id)
    if not machine:
        raise NotFoundError("Machine")


# ── Connections ──────────────────────────────────────────
@router.get("/lines/{line_id}/connections", response_model=list[ConnectionResponse], tags=["Connections"])
def list_connections(line_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_line_read(db, line_id, current_user)
    return service.get_connections_by_line(db, line_id)


@router.post("/lines/{line_id}/connections", response_model=ConnectionResponse, status_code=201, tags=["Connections"])
def create_connection(
    line_id: str,
    data: ConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_line_write(db, line_id, current_user)
    return service.create_connection(db, line_id, data)


@router.get("/connections/{connection_id}", response_model=ConnectionResponse, tags=["Connections"])
def get_connection(connection_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conn = service.get_connection_by_id(db, connection_id)
    if not conn:
        raise NotFoundError("Connection")
    ensure_line_read(db, str(conn.production_line_id), current_user)
    return conn


@router.put("/connections/{connection_id}", response_model=ConnectionResponse, tags=["Connections"])
def update_connection(
    connection_id: str,
    data: ConnectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = service.get_connection_by_id(db, connection_id)
    if not existing:
        raise NotFoundError("Connection")
    ensure_line_write(db, str(existing.production_line_id), current_user)
    conn = service.update_connection(db, connection_id, data)
    return conn


@router.delete("/connections/{connection_id}", status_code=204, tags=["Connections"])
def delete_connection(connection_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conn = service.get_connection_by_id(db, connection_id)
    if not conn:
        raise NotFoundError("Connection")
    ensure_line_write(db, str(conn.production_line_id), current_user)
    conn = service.soft_delete_connection(db, connection_id)
    if not conn:
        raise NotFoundError("Connection")
