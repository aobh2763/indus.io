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

router = APIRouter(prefix="/projects", tags=["Projects"])


# ── Projects ─────────────────────────────────────────────
@router.get("/", response_model=list[ProjectResponse])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.get_all_projects(db, skip, limit)


@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_project(db, data, owner_id=current_user.id)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = service.get_project_by_id(db, project_id)
    if not project:
        raise NotFoundError("Project")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
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


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = service.soft_delete_project(db, project_id)
    if not project:
        raise NotFoundError("Project")


# ── Project Access ───────────────────────────────────────
@router.get("/{project_id}/access", response_model=list[ProjectAccessResponse], tags=["Project Access"])
def list_access(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.get_project_access_list(db, project_id)


@router.post("/{project_id}/access", response_model=ProjectAccessResponse, status_code=201, tags=["Project Access"])
def grant_access(
    project_id: str,
    data: ProjectAccessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_project_access(db, project_id, data)


@router.put("/access/{access_id}", response_model=ProjectAccessResponse, tags=["Project Access"])
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


@router.delete("/access/{access_id}", status_code=204, tags=["Project Access"])
def revoke_access(access_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    access = service.delete_project_access(db, access_id)
    if not access:
        raise NotFoundError("Access entry")
