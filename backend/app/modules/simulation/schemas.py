import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.core.permissions import LogLevel, SimulationStatus


# ── Simulation ───────────────────────────────────────────
class SimulationCreate(BaseModel):
    status: SimulationStatus = SimulationStatus.RUNNING


class SimulationUpdate(BaseModel):
    status: Optional[SimulationStatus] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class SimulationResponse(BaseModel):
    id: uuid.UUID
    production_line_id: uuid.UUID
    status: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Simulation Log ───────────────────────────────────────
class SimulationLogCreate(BaseModel):
    machine_id: Optional[uuid.UUID] = None
    level: LogLevel = LogLevel.INFO
    message: Optional[str] = None


class SimulationLogResponse(BaseModel):
    id: uuid.UUID
    simulation_id: uuid.UUID
    machine_id: Optional[uuid.UUID] = None
    level: Optional[str] = None
    message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Batch Simulation ─────────────────────────────────────

class MachineInput(BaseModel):
    """
    Mirrors the RawMachine dict consumed by SimulationEngine.run_from_dicts().

    - id              : unique identifier for this machine node
    - name            : human-readable label
    - process         : top-level process (e.g. "Spinning")
    - subprocess      : subprocess key  (e.g. "Rotor Spinning")
    - parameters      : Layer 3 operational params (maps to *Params dataclass)
    - input_attributes: Layer 2 overrides for root nodes (raw material props);
                        leave empty for mid-chain nodes whose inputs come
                        entirely from the upstream machine output.
    """
    id: uuid.UUID
    name: str
    process: str
    subprocess: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    input_attributes: dict[str, Any] = Field(default_factory=dict)


class ConnectionInput(BaseModel):
    """Directed edge between two machine nodes."""
    source_machine_id: uuid.UUID
    target_machine_id: uuid.UUID


class BatchSimulateRequest(BaseModel):
    """
    Batch simulation request body.

    The client sends the full production-line graph once, together with
    the number of steps to simulate.  The server runs the engine `steps`
    times and returns one SimulationFrame per step.

    Because the current engine is steady-state (not time-varying), each
    frame is an independent evaluation of the same graph.  Future
    extensions can thread state forward between steps.

    - production_line_id: optional — used only for logging / correlation
    - steps             : how many frames to generate (1 – 1 000)
    - machines          : ordered list of machine nodes
    - connections       : directed edges defining the production DAG
    """
    production_line_id: Optional[uuid.UUID] = None
    steps: int = Field(default=1, ge=1, le=1000,
                       description="Number of simulation steps to run (1 – 1 000)")
    machines: list[MachineInput]
    connections: list[ConnectionInput] = Field(default_factory=list)


class LinkState(BaseModel):
    """State of a single directed edge at one simulation step."""
    source_machine: str
    target_machine: str
    # Each entry in 'states' is the Layer 4 output dict of the source node.
    states: list[dict[str, Any]]


class SimulationFrame(BaseModel):
    """
    A single snapshot produced by one simulation step.

    Matches the structure returned by SimulationResult.to_dict() so the
    frontend can consume frames directly from the engine output.
    """
    step: int                                   # 0-indexed step number
    success: bool
    production_line_full_input: dict[str, Any]  # root machine Layer 2 inputs
    production_line_full_output: dict[str, Any] # leaf machine Layer 4 outputs
    links: list[LinkState]                      # per-edge Layer 4 state
    errors_warnings: list[str]


class BatchSimulateResponse(BaseModel):
    """
    Full response for a batch simulation run.

    - production_line_id : echoed back for client correlation
    - steps_requested    : the 'steps' value from the request
    - steps_completed    : may be < steps_requested if the engine errored early
    - frames             : time-series of simulation frames, one per step
    """
    production_line_id: Optional[uuid.UUID]
    steps_requested: int
    steps_completed: int
    frames: list[SimulationFrame]
