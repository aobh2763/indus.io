from datetime import datetime

from app.modules.production.models import Connection, Machine
from app.modules.simulation.models import SimulationStep
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.exceptions import NotFoundError
from app.modules.identity.models import User
from app.modules.simulation import service
from app.modules.simulation.engine import (
    start_simulation,
    stop_simulation,
    complete_simulation,
    run_batch,
)
from app.modules.simulation.schemas import (
    BatchSimulateRequest,
    BatchSimulateResponse,
    ConnectionInput,
    MachineInput,
    SimulationCreate,
    SimulationLogCreate,
    SimulationLogResponse,
    SimulationResponse,
    SimulationStepSchema,
    SimulationUpdate,
)

router = APIRouter()


# ── Simulations ──────────────────────────────────────────
@router.get("/lines/{line_id}/simulations", response_model=list[SimulationResponse], tags=["Simulations"])
def list_simulations(line_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.get_simulations_by_line(db, line_id)


@router.post("/lines/{line_id}/simulations", response_model=SimulationResponse, status_code=201, tags=["Simulations"])
def create_simulation(
    line_id: str,
    data: SimulationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_simulation(db, line_id, data)


@router.get("/simulations/{simulation_id}", response_model=SimulationResponse, tags=["Simulations"])
def get_simulation(simulation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sim = service.get_simulation_by_id(db, simulation_id)
    if not sim:
        raise NotFoundError("Simulation")
    return sim


@router.put("/simulations/{simulation_id}", response_model=SimulationResponse, tags=["Simulations"])
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


@router.delete("/simulations/{simulation_id}", status_code=204, tags=["Simulations"])
def delete_simulation(simulation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sim = service.soft_delete_simulation(db, simulation_id)
    if not sim:
        raise NotFoundError("Simulation")

def map_machine_to_machine_input(machine: Machine) -> MachineInput:
    return MachineInput(
        id=machine.id,
        name=machine.name,
        process=machine.process,
        subprocess=machine.subprocess,
        parameters=machine.parameters or {},
        input_attributes={attr.attribute_name: attr.value for attr in machine.attribute_values},
    )

def map_connection_to_connection_input(connection: Connection) -> ConnectionInput:
    return ConnectionInput(
        source_machine_id=connection.source_machine_id,
        target_machine_id=connection.target_machine_id,
    )

# ── Engine actions ───────────────────────────────────────
@router.post("/simulations/{simulation_id}/start", response_model=SimulationResponse, tags=["Simulation Engine"])
def start(simulation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sim = service.get_simulation_by_id(db, simulation_id)
    if not sim:
        raise NotFoundError("Simulation")
    return start_simulation(db, sim)

@router.post("/simulations/{simulation_id}/step", response_model=SimulationResponse, tags=["Simulation Engine"])
def step(simulation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sim = service.get_simulation_by_id(db, simulation_id)
    if not sim:
        raise NotFoundError("Simulation")
    
    if sim.status != "RUNNING":
        raise HTTPException(status_code=400, detail="Simulation must be RUNNING to step.")
    
    seen = set()
    unique_connections = []
    for c in sim.production_line.connections:
        key = (c.source_machine_id, c.target_machine_id)
        if key not in seen:
            seen.add(key)
            unique_connections.append(c)

    request = BatchSimulateRequest(
        production_line_id=sim.production_line_id,
        machines=[map_machine_to_machine_input(m) for m in sim.production_line.machines if m.deleted_at is None],
        connections=[map_connection_to_connection_input(c) for c in unique_connections if c.deleted_at is None],
        steps=1,
    )
    
    bach_result = run_batch(request)
    service.save_simulation_frame(db, sim, bach_result["frames"][0])
    
    print("Batch result for step:", bach_result)
    
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


@router.get("/simulations/{simulation_id}/steps", response_model=list[SimulationStepSchema], tags=["Simulation Engine"])
def get_steps(simulation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sim = service.get_simulation_by_id(db, simulation_id)
    if not sim:
        raise NotFoundError("Simulation")
    return service.get_steps_by_simulation(db, sim.id)


@router.get("/simulations/{simulation_id}/steps/{step_number}", response_model=SimulationStepSchema, tags=["Simulation Engine"])
def get_step(simulation_id: str, step_number: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sim = service.get_simulation_by_id(db, simulation_id)
    if not sim:
        raise NotFoundError("Simulation")
    step = service.get_simulation_step(db, sim.id, step_number)
    if not step:
        raise NotFoundError("Simulation Step")
    return step


@router.get("/simulations/{simulation_id}/steps/{from_step}/{to_step}", response_model=list[SimulationStepSchema], tags=["Simulation Engine"])
def get_steps_from_to(simulation_id: str, from_step: int, to_step: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sim = service.get_simulation_by_id(db, simulation_id)
    if not sim:
        raise NotFoundError("Simulation")
    return service.get_steps_from_to(db, sim.id, from_step, to_step)


@router.get("/simulations/{simulation_id}/steps/time/{from_datetime}/{to_datetime}", response_model=list[SimulationStepSchema], tags=["Simulation Engine"])
def get_steps_between(simulation_id: str, from_datetime: datetime, to_datetime: datetime, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sim = service.get_simulation_by_id(db, simulation_id)
    if not sim:
        raise NotFoundError("Simulation")
    return service.get_steps_between(db, sim.id, from_datetime, to_datetime)

# ── Batch Simulation ────────────────────────────────────────────────
@router.post(
    "/simulations/batch",
    response_model=BatchSimulateResponse,
    tags=["Simulation Engine"],
    summary="Run a batch simulation",
    description=(
        "Accepts the full production-line graph (machines + connections) and a "
        "number of steps.  Runs the SimulationEngine `steps` times and returns "
        "one `SimulationFrame` per step.  No Simulation DB record is created or "
        "modified — this endpoint is stateless and designed for interactive use "
        "from the canvas."
    ),
)
def batch_simulate(
    data: BatchSimulateRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Stateless batch simulation endpoint.

    The client sends the complete production-line graph once and specifies how
    many steps to run.  The server returns a time-series of frames that can be
    used to animate the production line or generate a dashboard report.
    """
    try:
        result = run_batch(data)
    except (ValueError, NotImplementedError) as exc:
        # Surface graph-configuration errors (missing bridges, cycles, etc.)
        # as 422 Unprocessable Entity so the frontend can display them.
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Simulation error: {exc}") from exc

    return result


# ── Simulation Logs ──────────────────────────────────────────────────
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
