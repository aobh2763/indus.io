from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.exceptions import NotFoundError
from app.modules.identity.models import User
from app.modules.simulation import service
from app.modules.simulation.engine import start_simulation, stop_simulation, complete_simulation
from app.modules.simulation.schemas import (
    SimulationCreate,
    SimulationLogCreate,
    SimulationLogResponse,
    SimulationResponse,
    SimulationUpdate,
)

router = APIRouter(tags=["Simulations"])


# ── Simulations ──────────────────────────────────────────
@router.get("/lines/{line_id}/simulations", response_model=list[SimulationResponse])
def list_simulations(line_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.get_simulations_by_line(db, line_id)


@router.post("/lines/{line_id}/simulations", response_model=SimulationResponse, status_code=201)
def create_simulation(
    line_id: str,
    data: SimulationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_simulation(db, line_id, data)


@router.get("/simulations/{simulation_id}", response_model=SimulationResponse)
def get_simulation(simulation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sim = service.get_simulation_by_id(db, simulation_id)
    if not sim:
        raise NotFoundError("Simulation")
    return sim


@router.put("/simulations/{simulation_id}", response_model=SimulationResponse)
def update_simulation(
    simulation_id: str,
    data: SimulationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sim = service.update_simulation(db, simulation_id, data)
    if not sim:
        raise NotFoundError("Simulation")
    return sim


@router.delete("/simulations/{simulation_id}", status_code=204)
def delete_simulation(simulation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sim = service.soft_delete_simulation(db, simulation_id)
    if not sim:
        raise NotFoundError("Simulation")


# ── Engine actions ───────────────────────────────────────
@router.post("/simulations/{simulation_id}/start", response_model=SimulationResponse, tags=["Simulation Engine"])
def start(simulation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sim = service.get_simulation_by_id(db, simulation_id)
    if not sim:
        raise NotFoundError("Simulation")
    return start_simulation(db, sim)


@router.post("/simulations/{simulation_id}/stop", response_model=SimulationResponse, tags=["Simulation Engine"])
def stop(simulation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sim = service.get_simulation_by_id(db, simulation_id)
    if not sim:
        raise NotFoundError("Simulation")
    return stop_simulation(db, sim)


@router.post("/simulations/{simulation_id}/complete", response_model=SimulationResponse, tags=["Simulation Engine"])
def complete(simulation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sim = service.get_simulation_by_id(db, simulation_id)
    if not sim:
        raise NotFoundError("Simulation")
    return complete_simulation(db, sim)


# ── Simulation Logs ──────────────────────────────────────
@router.get("/simulations/{simulation_id}/logs", response_model=list[SimulationLogResponse], tags=["Simulation Logs"])
def list_logs(simulation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.get_logs_by_simulation(db, simulation_id)


@router.post("/simulations/{simulation_id}/logs", response_model=SimulationLogResponse, status_code=201, tags=["Simulation Logs"])
def create_log(
    simulation_id: str,
    data: SimulationLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_log(db, simulation_id, data)
