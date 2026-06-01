from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.dependencies import get_db
from app.modules.project.models import Project
from app.modules.production.models import ProductionLine, Machine
from app.modules.monitoring.models import Alert

router = APIRouter(prefix="/system", tags=["System"])

@router.get("/stats")
def get_system_stats(db: Session = Depends(get_db)):
    project_count = db.query(func.count(Project.id)).scalar()
    line_count = db.query(func.count(ProductionLine.id)).scalar()
    machine_count = db.query(func.count(Machine.id)).scalar()
    alert_count = db.query(func.count(Alert.id)).filter(Alert.status == "OPEN").scalar()

    return {
        "projects": project_count or 0,
        "lines": line_count or 0,
        "machines": machine_count or 0,
        "open_alerts": alert_count or 0,
    }
