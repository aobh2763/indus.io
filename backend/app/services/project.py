from sqlalchemy.orm import Session
from uuid import UUID
from app.models.project import Project, ProjectShiftSupervisor
from app.schemas.project import ProjectCreate, ProjectUpdate

def get_all(db: Session):

    return db.query(Project).all()

def get_by_id(db: Session, project_id: UUID):
    return db.query(Project).filter(Project.project_id == project_id).first()

def create(db: Session, data: ProjectCreate):
    project = Project(
        name=data.name,
        project_manager=data.project_manager,
        visibility=data.visibility,
        production_lines=data.production_lines,
    )
    db.add(project)
    db.flush()
    for uid in data.shift_supervisor_ids:
        db.add(ProjectShiftSupervisor(project_id=project.project_id, user_id=uid))

    db.commit()
    db.refresh(project)
    return project

def update(db: Session, project_id: UUID, data: ProjectUpdate):
    project = get_by_id(db, project_id)
    if not project:
        return None

    if data.name is not None:project.name = data.name
    if data.visibility is not None:project.visibility = data.visibility
    if data.production_lines is not None:project.production_lines = data.production_lines

    if data.shift_supervisor_ids is not None:
        db.query(ProjectShiftSupervisor).filter_by(project_id=project_id).delete()
        for uid in data.shift_supervisor_ids:
            db.add(ProjectShiftSupervisor(project_id=project_id, user_id=uid))

    db.commit()
    db.refresh(project)
    return project

def delete(db: Session, project_id: UUID):
    project = get_by_id(db, project_id)
    if project:
        db.delete(project)
        db.commit()
    return project