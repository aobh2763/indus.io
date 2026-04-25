import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.modules.simulation.models import Simulation, SimulationLog
from app.modules.simulation.schemas import (
    SimulationCreate,
    SimulationLogCreate,
    SimulationUpdate,
)


# ── Simulations ──────────────────────────────────────────
def get_simulations_by_line(db: Session, line_id: uuid.UUID):
    return db.query(Simulation).filter(
        Simulation.production_line_id == line_id, Simulation.deleted_at.is_(None)
    ).all()


def get_simulation_by_id(db: Session, sim_id: uuid.UUID) -> Optional[Simulation]:
    return db.query(Simulation).filter(
        Simulation.id == sim_id, Simulation.deleted_at.is_(None)
    ).first()


def create_simulation(db: Session, line_id: uuid.UUID, data: SimulationCreate) -> Simulation:
    sim = Simulation(
        production_line_id=line_id,
        status=data.status.value,
        start_time=datetime.now(timezone.utc),
    )
    db.add(sim)
    db.commit()
    db.refresh(sim)
    return sim


def update_simulation(db: Session, sim_id: uuid.UUID, data: SimulationUpdate) -> Optional[Simulation]:
    sim = get_simulation_by_id(db, sim_id)
    if not sim:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "status" and value is not None:
            setattr(sim, field, value.value if hasattr(value, "value") else value)
        else:
            setattr(sim, field, value)
    db.commit()
    db.refresh(sim)
    return sim


def soft_delete_simulation(db: Session, sim_id: uuid.UUID) -> Optional[Simulation]:
    sim = get_simulation_by_id(db, sim_id)
    if not sim:
        return None
    sim.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return sim


# ── Simulation Logs ──────────────────────────────────────
def get_logs_by_simulation(db: Session, sim_id: uuid.UUID):
    return db.query(SimulationLog).filter(SimulationLog.simulation_id == sim_id).all()


def create_log(db: Session, sim_id: uuid.UUID, data: SimulationLogCreate) -> SimulationLog:
    log = SimulationLog(
        simulation_id=sim_id,
        machine_id=data.machine_id,
        level=data.level.value,
        message=data.message,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
