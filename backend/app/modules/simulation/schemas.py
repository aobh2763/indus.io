import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, ConfigDict

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
    

class SimulationStepSchema(BaseModel):
    simulation_id: uuid.UUID
    step: int
    frame_data: dict

    model_config = {
        "from_attributes": True
    }

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
    
    model_config = ConfigDict(
        json_schema_extra= {
                    "example": {
        "production_line_id": "00000000-0000-0000-0000-000000000000",
        "steps": 1,
        "machines": [
            {
            "id": "00000000-0000-0000-0000-000000000001",
            "name": "Rotor Spinner R-01",
            "process": "Spinning",
            "subprocess": "Rotor Spinning",
            "parameters": {
                "rotor_diameter_mm": 33.0,
                "rotor_speed_rpm": 100000,
                "twist_factor_am": 130.0,
                "opening_roller_speed_rpm": 7500,
                "opening_roller_wire_type": "coarse_wire",
                "navel_type": "notched",
                "rotor_groove_type": "U_groove",
                "total_draft_ratio": 152.5,
                "delivery_speed_m_min": 132.0,
                "yarn_count_Ne": 20.0,
                "yarn_count_tex": 29.5,
                "ambient_temperature_C": 24.0,
                "ambient_humidity_pct": 55.0,
                "last_maintenance_date": "2025-10-01",
                "maintenance_interval_hours": 1500.0,
                "operating_hours_since_maintenance": 600.0
            },
            "input_attributes": {
                "fiber_type": "cotton_carded",
                "fiber_length_mm": 27.0,
                "fiber_fineness_dtex": 1.7,
                "short_fiber_content_pct": 14.0,
                "fiber_tensile_strength_cN_tex": 28.0,
                "sliver_count_ktex": 4.5,
                "moisture_content_pct": 7.0,
                "trash_content_pct": 1.2
            }
            },
            {
            "id": "00000000-0000-0000-0000-000000000002",
            "name": "Plain Loom W-01",
            "process": "Weaving",
            "subprocess": "Plain Weaving",
            "parameters": {
                "ends_per_cm": 30.0,
                "picks_per_cm": 28.0,
                "reed_width_cm": 160.0,
                "loom_speed_picks_per_min": 220,
                "loom_type": "shuttle",
                "warp_tension_cN_per_end": 12.0,
                "let_off_type": "positive",
                "take_up_type": "positive",
                "shed_depth_cm": 9.5,
                "heald_shaft_count": 2,
                "temple_type": "pin_temple",
                "ambient_temperature_C": 24.0,
                "ambient_humidity_pct": 60.0,
                "maintenance_interval_hours": 2000.0,
                "operating_hours_since_maintenance": 800.0
            },
            "input_attributes": {}
            },
            {
            "id": "00000000-0000-0000-0000-000000000003",
            "name": "Jet Dyeing Machine D-01",
            "process": "Colouring",
            "subprocess": "Reactive Dyeing",
            "parameters": {
                "dye_type": "ME",
                "dye_concentration_owf_pct": 2.0,
                "salt_concentration_g_L": 50.0,
                "alkali_type": "Na2CO3",
                "alkali_concentration_g_L": 15.0,
                "dyeing_temperature_C": 60.0,
                "exhaustion_time_min": 40.0,
                "fixation_time_min": 45.0,
                "wash_off_time_min": 40.0,
                "liquor_ratio": 10.0,
                "machine_type": "jet",
                "water_hardness_ppm": 80.0,
                "fabric_is_mercerized": False,
                "fabric_is_scoured": True,
                "ambient_temperature_C": 24.0,
                "maintenance_interval_hours": 2000.0,
                "operating_hours_since_maintenance": 700.0
            },
            "input_attributes": {}
            }
        ],
        "connections": [
            {
            "source_machine_id": "00000000-0000-0000-0000-000000000001",
            "target_machine_id": "00000000-0000-0000-0000-000000000002"
            },
            {
            "source_machine_id": "00000000-0000-0000-0000-000000000002",
            "target_machine_id": "00000000-0000-0000-0000-000000000003"
            }
        ]
    }})


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
