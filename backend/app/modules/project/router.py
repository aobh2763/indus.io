from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.exceptions import NotFoundError
from app.modules.identity.models import User
from app.modules.project import service
from app.modules.project.schemas import (
    ProjectAccessCreate,
    ProjectAccessResponse,
    ProjectAccessUpdate,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)

projects_router = APIRouter(prefix="/projects", tags=["Projects"])
access_router = APIRouter(prefix="/projects", tags=["Project Access"])


# ── Projects ─────────────────────────────────────────────
@projects_router.get("/", response_model=list[ProjectResponse])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.get_all_projects(db, skip, limit)


@projects_router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_project(db, data, user_id=current_user.id)


@projects_router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = service.get_project_by_id(db, project_id)
    if not project:
        raise NotFoundError("Project")
    return project


@projects_router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = service.update_project(db, project_id, data)
    if not project:
        raise NotFoundError("Project")
    return project


@projects_router.delete("/{project_id}", status_code=204)
def delete_project(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = service.soft_delete_project(db, project_id)
    if not project:
        raise NotFoundError("Project")


# ── Project Access ───────────────────────────────────────
@access_router.get("/{project_id}/access", response_model=list[ProjectAccessResponse])
def list_access(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.get_project_access_list(db, project_id)


@access_router.post("/{project_id}/access", response_model=ProjectAccessResponse, status_code=201)
def grant_access(
    project_id: str,
    data: ProjectAccessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_project_access(db, project_id, data)


@access_router.put("/access/{access_id}", response_model=ProjectAccessResponse)
def update_access(
    access_id: str,
    data: ProjectAccessUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    access = service.update_project_access(db, access_id, data)
    if not access:
        raise NotFoundError("Access entry")
    return access


@access_router.delete("/access/{access_id}", status_code=204)
def revoke_access(access_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    access = service.delete_project_access(db, access_id)
    if not access:
        raise NotFoundError("Access entry")
