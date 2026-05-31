import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import Integer, UniqueConstraint, select, func

from app.modules.simulation.models import Simulation, SimulationLog, SimulationStep
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


def save_simulation_frame(db: Session, sim: Simulation, frame_data: dict) -> SimulationLog:
    step = SimulationStep(
        simulation_id=sim.id,
        step=get_next_step(db, sim.id),
        frame_data=frame_data,)
    db.add(step)
    db.commit()
    db.refresh(step)
    return step


def get_next_step(db: Session, simulation_id: uuid.UUID) -> int:
    count = db.query(func.count(SimulationStep.id)) \
        .filter(SimulationStep.simulation_id == simulation_id) \
        .scalar()

    return count or 0


# ── Simulation Steps ──────────────────────────────────────
def get_steps_by_simulation(db: Session, sim_id: uuid.UUID):
    return db.query(SimulationStep).filter(SimulationStep.simulation_id == sim_id).all()


def get_simulation_step(db: Session, sim_id: uuid.UUID, step_number: int):
    return db.query(SimulationStep).filter(
        SimulationStep.simulation_id == sim_id,
        SimulationStep.step == step_number
    ).first()


def get_steps_from_to(db: Session, sim_id: uuid.UUID, from_step: int, to_step: int):
    return db.query(SimulationStep).filter(
        SimulationStep.simulation_id == sim_id,
        SimulationStep.step >= from_step,
        SimulationStep.step <= to_step
    ).all()


def get_steps_between(db: Session, sim_id: uuid.UUID, from_datetime: datetime, to_datetime: datetime):
    if from_datetime > to_datetime:
        raise ValueError("from_datetime must be less than or equal to to_datetime")
    
    return db.query(SimulationStep).filter(
        SimulationStep.simulation_id == sim_id,
        SimulationStep.created_at >= from_datetime,
        SimulationStep.created_at <= to_datetime
    ).all()