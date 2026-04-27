import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.modules.project.models import Project, ProjectAccess
from app.modules.project.schemas import (
    ProjectAccessCreate,
    ProjectAccessUpdate,
    ProjectCreate,
    ProjectUpdate,
)
from app.core.permissions import AccessLevel


# ── Project CRUD ─────────────────────────────────────────
def get_all_projects(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(Project)
        .filter(Project.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_project_by_id(db: Session, project_id: uuid.UUID) -> Optional[Project]:
    return db.query(Project).filter(Project.id == project_id, Project.deleted_at.is_(None)).first()


def create_project(db: Session, data: ProjectCreate, user_id: uuid.UUID) -> Project:
    # 1. Create the project record
    project = Project(
        name=data.name,
        description=data.description,
        visibility=data.visibility.value,
    )
    db.add(project)
    db.flush()  # To get the project.id before committing

    # 2. Automatically grant OWNER access to the creator
    access = ProjectAccess(
        project_id=project.id,
        user_id=user_id,
        access_level=AccessLevel.OWNER.value,
        can_clone=True,
    )
    db.add(access)
    
    db.commit()
    db.refresh(project)
    return project


def update_project(db: Session, project_id: uuid.UUID, data: ProjectUpdate) -> Optional[Project]:
    project = get_project_by_id(db, project_id)
    if not project:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "visibility" and value is not None:
            setattr(project, field, value.value if hasattr(value, "value") else value)
        else:
            setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


def soft_delete_project(db: Session, project_id: uuid.UUID) -> Optional[Project]:
    project = get_project_by_id(db, project_id)
    if not project:
        return None
    project.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return project


# ── Project Access CRUD ──────────────────────────────────
def get_project_access_list(db: Session, project_id: uuid.UUID):
    return (
        db.query(ProjectAccess)
        .filter(ProjectAccess.project_id == project_id, ProjectAccess.deleted_at.is_(None))
        .all()
    )


def create_project_access(db: Session, project_id: uuid.UUID, data: ProjectAccessCreate) -> ProjectAccess:
    access = ProjectAccess(
        project_id=project_id,
        user_id=data.user_id,
        access_level=data.access_level.value,
        can_clone=data.can_clone,
    )
    db.add(access)
    db.commit()
    db.refresh(access)
    return access


def update_project_access(db: Session, access_id: uuid.UUID, data: ProjectAccessUpdate) -> Optional[ProjectAccess]:
    access = db.query(ProjectAccess).filter(ProjectAccess.id == access_id, ProjectAccess.deleted_at.is_(None)).first()
    if not access:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "access_level" and value is not None:
            setattr(access, field, value.value if hasattr(value, "value") else value)
        else:
            setattr(access, field, value)
    db.commit()
    db.refresh(access)
    return access


def delete_project_access(db: Session, access_id: uuid.UUID) -> Optional[ProjectAccess]:
    access = db.query(ProjectAccess).filter(ProjectAccess.id == access_id, ProjectAccess.deleted_at.is_(None)).first()
    if not access:
        return None
    access.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return access
