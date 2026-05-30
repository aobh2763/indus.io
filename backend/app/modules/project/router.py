from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.permissions import AccessLevel, AccessStatus, GlobalRole
from app.modules.identity.models import User
from app.modules.project.models import ProjectAccess
from app.modules.project import service
from app.modules.project.schemas import (
    ProjectAccessCreate,
    ProjectAccessResponse,
    ProjectAccessUpdate,
    ProjectNotificationResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)

projects_router = APIRouter(prefix="/projects", tags=["Projects"])
access_router = APIRouter(prefix="/projects", tags=["Project Access"])


def ensure_project_access_manager(db: Session, project_id: str, current_user: User):
    if current_user.role == GlobalRole.ADMIN.value:
        return

    owner_access = (
        db.query(ProjectAccess)
        .filter(
            ProjectAccess.project_id == project_id,
            ProjectAccess.user_id == current_user.id,
            ProjectAccess.access_level == AccessLevel.OWNER.value,
            ProjectAccess.status == AccessStatus.ACCEPTED.value,
            ProjectAccess.deleted_at.is_(None),
        )
        .first()
    )
    if not owner_access:
        raise ForbiddenError("Only project owners can manage contributor access")


def ensure_project_clone_allowed(db: Session, project_id: str, current_user: User):
    if current_user.role == GlobalRole.ADMIN.value:
        return

    access = (
        db.query(ProjectAccess)
        .filter(
            ProjectAccess.project_id == project_id,
            ProjectAccess.user_id == current_user.id,
            ProjectAccess.status == AccessStatus.ACCEPTED.value,
            ProjectAccess.deleted_at.is_(None),
        )
        .first()
    )
    if not access or (access.access_level != AccessLevel.OWNER.value and not access.can_clone):
        raise ForbiddenError("You are not allowed to clone this project")


def ensure_project_visible(db: Session, project_id: str, current_user: User):
    if current_user.role == GlobalRole.ADMIN.value:
        return
    project = service.get_project_by_id(db, project_id, user=current_user)
    if project and project.visibility == "PUBLIC":
        return
    accepted_access = (
        db.query(ProjectAccess)
        .filter(
            ProjectAccess.project_id == project_id,
            ProjectAccess.user_id == current_user.id,
            ProjectAccess.status == AccessStatus.ACCEPTED.value,
            ProjectAccess.deleted_at.is_(None),
        )
        .first()
    )
    if not accepted_access:
        raise ForbiddenError("You do not have access to this project")


# ── Projects ─────────────────────────────────────────────
@projects_router.get("/", response_model=list[ProjectResponse])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.get_all_projects(db, skip, limit, user=current_user)


@projects_router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_project(db, data, user_id=current_user.id)


@projects_router.post("/{project_id}/clone", response_model=ProjectResponse, status_code=201)
def clone_project(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_project_clone_allowed(db, project_id, current_user)
    return service.clone_project(db, project_id, user_id=current_user.id)


@projects_router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = service.get_project_by_id(db, project_id, user=current_user)
    if not project:
        raise NotFoundError("Project")
    ensure_project_visible(db, project_id, current_user)
    return project


@projects_router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_project_access_manager(db, project_id, current_user)
    project = service.update_project(db, project_id, data)
    if not project:
        raise NotFoundError("Project")
    return project


@projects_router.delete("/{project_id}", status_code=204)
def delete_project(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_project_access_manager(db, project_id, current_user)
    project = service.soft_delete_project(db, project_id)
    if not project:
        raise NotFoundError("Project")


# ── Project Access ───────────────────────────────────────
@access_router.get("/{project_id}/access", response_model=list[ProjectAccessResponse])
def list_access(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_project_access_manager(db, project_id, current_user)
    return service.get_project_access_list(db, project_id)


@access_router.post("/{project_id}/access", response_model=ProjectAccessResponse, status_code=201)
def grant_access(
    project_id: str,
    data: ProjectAccessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_project_access_manager(db, project_id, current_user)
    return service.create_project_access(db, project_id, data, invited_by_user_id=current_user.id)


@access_router.put("/access/{access_id}", response_model=ProjectAccessResponse)
def update_access(
    access_id: str,
    data: ProjectAccessUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    access_entry = db.query(ProjectAccess).filter(ProjectAccess.id == access_id, ProjectAccess.deleted_at.is_(None)).first()
    if not access_entry:
        raise NotFoundError("Access entry")
    ensure_project_access_manager(db, str(access_entry.project_id), current_user)
    access = service.update_project_access(db, access_id, data)
    if not access:
        raise NotFoundError("Access entry")
    return access


@access_router.delete("/access/{access_id}", status_code=204)
def revoke_access(access_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    access_entry = db.query(ProjectAccess).filter(ProjectAccess.id == access_id, ProjectAccess.deleted_at.is_(None)).first()
    if not access_entry:
        raise NotFoundError("Access entry")
    ensure_project_access_manager(db, str(access_entry.project_id), current_user)
    access = service.delete_project_access(db, access_id)
    if not access:
        raise NotFoundError("Access entry")


@access_router.get("/me/invitations", response_model=list[ProjectAccessResponse])
def list_my_invitations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.get_current_user_invitations(db, current_user.id)


@access_router.post("/access/{access_id}/accept", response_model=ProjectAccessResponse)
def accept_access_invitation(access_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    access = service.accept_project_access(db, access_id, current_user.id)
    if not access:
        raise NotFoundError("Access invitation")
    return access


@access_router.post("/access/{access_id}/decline", status_code=204)
def decline_access_invitation(access_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    access = service.decline_project_access(db, access_id, current_user.id)
    if not access:
        raise NotFoundError("Access invitation")


@access_router.get("/notifications", response_model=list[ProjectNotificationResponse])
def list_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.get_notifications(db, current_user.id)


@access_router.post("/notifications/{notification_id}/read", response_model=ProjectNotificationResponse)
def mark_notification_read(notification_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notification = service.mark_notification_read(db, notification_id, current_user.id)
    if not notification:
        raise NotFoundError("Notification")
    return notification
