from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.database import get_db
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut
from app.services import project as service

router = APIRouter(prefix="/projects", 
                   tags=["Projects"])

@router.get("/", response_model=list[ProjectOut])
def get_all(db: Session = Depends(get_db)):
    return service.get_all(db)

@router.get("/{project_id}", response_model=ProjectOut)
def get_one(project_id: UUID, db: Session = Depends(get_db)):
    project = service.get_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/", response_model=ProjectOut, status_code=201)
def create(data: ProjectCreate, db: Session = Depends(get_db)):
    return service.create(db, data)

@router.put("/{project_id}", response_model=ProjectOut)
def update(project_id: UUID, data: ProjectUpdate, db: Session = Depends(get_db)):
    project = service.update(db, project_id, data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/{project_id}", status_code=204)
def delete(project_id: UUID, db: Session = Depends(get_db)):
    service.delete(db, project_id)