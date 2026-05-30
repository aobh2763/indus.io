import uuid
from copy import deepcopy
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.modules.project.models import Project, ProjectAccess, ProjectNotification
from app.modules.production.models import Connection, Machine, ProductionLine
from app.modules.project.schemas import (
    ProjectAccessCreate,
    ProjectAccessUpdate,
    ProjectCreate,
    ProjectUpdate,
)
from app.core.permissions import AccessLevel, AccessStatus, GlobalRole, Visibility
from app.modules.identity import service as identity_service


def attach_current_user_access(db: Session, project: Project, user) -> Project:
    if not user:
        project.current_user_access_level = None
        project.current_user_can_clone = False
        return project
    if user.role == GlobalRole.ADMIN.value:
        project.current_user_access_level = AccessLevel.OWNER.value
        project.current_user_can_clone = True
        return project
    access = (
        db.query(ProjectAccess)
        .filter(
            ProjectAccess.project_id == project.id,
            ProjectAccess.user_id == user.id,
            ProjectAccess.status == AccessStatus.ACCEPTED.value,
            ProjectAccess.deleted_at.is_(None),
        )
        .first()
    )
    project.current_user_access_level = access.access_level if access else None
    project.current_user_can_clone = bool(access.can_clone) if access else False
    return project


# ── Project CRUD ─────────────────────────────────────────
def get_all_projects(db: Session, skip: int = 0, limit: int = 100, user=None):
    query = db.query(Project).filter(Project.deleted_at.is_(None))
    if user and user.role != GlobalRole.ADMIN.value:
        query = (
            query.outerjoin(ProjectAccess, ProjectAccess.project_id == Project.id)
            .filter(
                (Project.visibility == Visibility.PUBLIC.value)
                | (
                    (ProjectAccess.user_id == user.id)
                    & (ProjectAccess.status == AccessStatus.ACCEPTED.value)
                    & (ProjectAccess.deleted_at.is_(None))
                )
            )
            .distinct()
        )
    projects = query.offset(skip).limit(limit).all()
    return [attach_current_user_access(db, project, user) for project in projects]


def get_project_by_id(db: Session, project_id: uuid.UUID, user=None) -> Optional[Project]:
    project = db.query(Project).filter(Project.id == project_id, Project.deleted_at.is_(None)).first()
    return attach_current_user_access(db, project, user) if project else None


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
        status=AccessStatus.ACCEPTED.value,
        accepted_at=datetime.now(timezone.utc),
    )
    db.add(access)
    
    db.commit()
    db.refresh(project)
    project.current_user_access_level = AccessLevel.OWNER.value
    project.current_user_can_clone = True
    return project


def clone_project(db: Session, project_id: uuid.UUID, user_id: uuid.UUID) -> Project:
    source = get_project_by_id(db, project_id)
    if not source:
        raise NotFoundError("Project")

    clone = Project(
        name=f"{source.name} Copy",
        description=source.description,
        visibility=source.visibility,
    )
    db.add(clone)
    db.flush()

    owner_access = ProjectAccess(
        project_id=clone.id,
        user_id=user_id,
        access_level=AccessLevel.OWNER.value,
        can_clone=True,
        status=AccessStatus.ACCEPTED.value,
        accepted_at=datetime.now(timezone.utc),
    )
    db.add(owner_access)

    source_lines = (
        db.query(ProductionLine)
        .filter(ProductionLine.project_id == source.id, ProductionLine.deleted_at.is_(None))
        .all()
    )
    for source_line in source_lines:
        cloned_line = ProductionLine(
            project_id=clone.id,
            name=source_line.name,
            status=source_line.status,
        )
        db.add(cloned_line)
        db.flush()

        machine_id_map: dict[uuid.UUID, uuid.UUID] = {}
        source_machines = (
            db.query(Machine)
            .filter(Machine.production_line_id == source_line.id, Machine.deleted_at.is_(None))
            .all()
        )
        for source_machine in source_machines:
            cloned_machine = Machine(
                production_line_id=cloned_line.id,
                name=source_machine.name,
                process=source_machine.process,
                subprocess=source_machine.subprocess,
                manufacturer=source_machine.manufacturer,
                model_reference=source_machine.model_reference,
                year_introduced=source_machine.year_introduced,
                description=source_machine.description,
                icon=source_machine.icon,
                position_x=source_machine.position_x,
                position_y=source_machine.position_y,
                parameters=deepcopy(source_machine.parameters),
                is_configured=source_machine.is_configured,
            )
            db.add(cloned_machine)
            db.flush()
            machine_id_map[source_machine.id] = cloned_machine.id

        source_connections = (
            db.query(Connection)
            .filter(Connection.production_line_id == source_line.id, Connection.deleted_at.is_(None))
            .all()
        )
        for source_connection in source_connections:
            source_id = machine_id_map.get(source_connection.source_machine_id)
            target_id = machine_id_map.get(source_connection.target_machine_id)
            if not source_id or not target_id:
                continue
            db.add(
                Connection(
                    production_line_id=cloned_line.id,
                    source_machine_id=source_id,
                    target_machine_id=target_id,
                    weight=source_connection.weight,
                )
            )

    db.commit()
    db.refresh(clone)
    clone.current_user_access_level = AccessLevel.OWNER.value
    clone.current_user_can_clone = True
    return clone


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


def _notify(
    db: Session,
    *,
    user_id: uuid.UUID,
    actor_user_id: uuid.UUID | None,
    project_id: uuid.UUID | None,
    access_id: uuid.UUID | None,
    type: str,
    title: str,
    message: str,
) -> ProjectNotification:
    notification = ProjectNotification(
        user_id=user_id,
        actor_user_id=actor_user_id,
        project_id=project_id,
        access_id=access_id,
        type=type,
        title=title,
        message=message,
    )
    db.add(notification)
    return notification


def create_project_access(
    db: Session,
    project_id: uuid.UUID,
    data: ProjectAccessCreate,
    invited_by_user_id: uuid.UUID | None = None,
) -> ProjectAccess:
    project = get_project_by_id(db, project_id)
    if not project:
        raise NotFoundError("Project")

    user = (
        identity_service.get_user_by_id(db, data.user_id)
        if data.user_id
        else identity_service.get_user_by_email(db, str(data.email).lower())
    )
    if not user:
        raise NotFoundError("User")

    existing = (
        db.query(ProjectAccess)
        .filter(ProjectAccess.project_id == project_id, ProjectAccess.user_id == user.id)
        .first()
    )

    if existing and existing.deleted_at is None:
        raise AlreadyExistsError("Project access")

    if existing:
        existing.access_level = data.access_level.value
        existing.can_clone = data.can_clone
        existing.status = AccessStatus.PENDING.value
        existing.invited_by_user_id = invited_by_user_id
        existing.accepted_at = None
        existing.deleted_at = None
        db.flush()
        _notify(
            db,
            user_id=user.id,
            actor_user_id=invited_by_user_id,
            project_id=project_id,
            access_id=existing.id,
            type="PROJECT_INVITATION",
            title="Project invitation",
            message=f"You were invited to {project.name} as {data.access_level.value}.",
        )
        db.commit()
        db.refresh(existing)
        return existing

    access = ProjectAccess(
        project_id=project_id,
        user_id=user.id,
        access_level=data.access_level.value,
        can_clone=data.can_clone,
        status=AccessStatus.PENDING.value,
        invited_by_user_id=invited_by_user_id,
    )
    db.add(access)
    db.flush()
    _notify(
        db,
        user_id=user.id,
        actor_user_id=invited_by_user_id,
        project_id=project_id,
        access_id=access.id,
        type="PROJECT_INVITATION",
        title="Project invitation",
        message=f"You were invited to {project.name} as {data.access_level.value}.",
    )
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


def accept_project_access(db: Session, access_id: uuid.UUID, user_id: uuid.UUID) -> Optional[ProjectAccess]:
    access = (
        db.query(ProjectAccess)
        .filter(
            ProjectAccess.id == access_id,
            ProjectAccess.user_id == user_id,
            ProjectAccess.deleted_at.is_(None),
        )
        .first()
    )
    if not access:
        return None
    access.status = AccessStatus.ACCEPTED.value
    access.accepted_at = datetime.now(timezone.utc)
    db.query(ProjectNotification).filter(
        ProjectNotification.access_id == access.id,
        ProjectNotification.user_id == user_id,
        ProjectNotification.type == "PROJECT_INVITATION",
        ProjectNotification.read_at.is_(None),
    ).update({"read_at": datetime.now(timezone.utc)}, synchronize_session=False)
    project = get_project_by_id(db, access.project_id)
    if access.invited_by_user_id and project:
        _notify(
            db,
            user_id=access.invited_by_user_id,
            actor_user_id=user_id,
            project_id=access.project_id,
            access_id=access.id,
            type="PROJECT_INVITATION_ACCEPTED",
            title="Invitation accepted",
            message=f"{access.user_email or 'A user'} accepted the invitation to {project.name}.",
        )
    db.commit()
    db.refresh(access)
    return access


def decline_project_access(db: Session, access_id: uuid.UUID, user_id: uuid.UUID) -> Optional[ProjectAccess]:
    access = (
        db.query(ProjectAccess)
        .filter(
            ProjectAccess.id == access_id,
            ProjectAccess.user_id == user_id,
            ProjectAccess.deleted_at.is_(None),
        )
        .first()
    )
    if not access:
        return None
    access.status = AccessStatus.DECLINED.value
    access.deleted_at = datetime.now(timezone.utc)
    db.query(ProjectNotification).filter(
        ProjectNotification.access_id == access.id,
        ProjectNotification.user_id == user_id,
        ProjectNotification.type == "PROJECT_INVITATION",
        ProjectNotification.read_at.is_(None),
    ).update({"read_at": datetime.now(timezone.utc)}, synchronize_session=False)
    project = get_project_by_id(db, access.project_id)
    if access.invited_by_user_id and project:
        _notify(
            db,
            user_id=access.invited_by_user_id,
            actor_user_id=user_id,
            project_id=access.project_id,
            access_id=access.id,
            type="PROJECT_INVITATION_DECLINED",
            title="Invitation declined",
            message=f"{access.user_email or 'A user'} declined the invitation to {project.name}.",
        )
    db.commit()
    return access


def get_current_user_invitations(db: Session, user_id: uuid.UUID):
    return (
        db.query(ProjectAccess)
        .filter(
            ProjectAccess.user_id == user_id,
            ProjectAccess.status == AccessStatus.PENDING.value,
            ProjectAccess.deleted_at.is_(None),
        )
        .all()
    )


def get_notifications(db: Session, user_id: uuid.UUID, limit: int = 50):
    return (
        db.query(ProjectNotification)
        .filter(ProjectNotification.user_id == user_id, ProjectNotification.deleted_at.is_(None))
        .order_by(ProjectNotification.created_at.desc())
        .limit(limit)
        .all()
    )


def mark_notification_read(db: Session, notification_id: uuid.UUID, user_id: uuid.UUID) -> Optional[ProjectNotification]:
    notification = (
        db.query(ProjectNotification)
        .filter(
            ProjectNotification.id == notification_id,
            ProjectNotification.user_id == user_id,
            ProjectNotification.deleted_at.is_(None),
        )
        .first()
    )
    if not notification:
        return None
    notification.read_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(notification)
    return notification
