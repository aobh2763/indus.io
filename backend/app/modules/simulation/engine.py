"""
Simulation Engine — bridges the FastAPI layer to the simulation package.

This module exposes:
  - start_simulation / stop_simulation / complete_simulation
      Lightweight helpers that update the Simulation DB row status.

  - run_batch()
      Runs the SimulationEngine N times and returns a BatchSimulateResponse.
      Each iteration is an independent steady-state evaluation of the
      production-line graph supplied in the request body.
"""

import sys
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.modules.simulation.models import Simulation
from app.core.permissions import SimulationStatus

# ── Make the standalone simulation/ package importable ───────────────────
# The simulation/ directory sits one level above the backend/ root, so it is
# not on sys.path by default.  We resolve it dynamically so that no manual
# PYTHONPATH configuration is required on any machine.
_SIM_PKG_DIR = Path(__file__).resolve().parents[4] / "simulation"
if str(_SIM_PKG_DIR) not in sys.path:
    sys.path.insert(0, str(_SIM_PKG_DIR))

from simulation_engine import SimulationEngine  # noqa: E402  (path-injection above)


# ── Status helpers ─────────────────────────────────────────────────

def start_simulation(db: Session, simulation: Simulation) -> Simulation:
    """Mark a simulation as RUNNING and record start_time."""
    simulation.status = SimulationStatus.RUNNING.value
    simulation.start_time = datetime.now(timezone.utc)
    db.commit()
    db.refresh(simulation)
    return simulation


def stop_simulation(db: Session, simulation: Simulation) -> Simulation:
    """Mark a simulation as STOPPED and record end_time."""
    simulation.status = SimulationStatus.STOPPED.value
    simulation.end_time = datetime.now(timezone.utc)
    db.commit()
    db.refresh(simulation)
    return simulation


def complete_simulation(db: Session, simulation: Simulation) -> Simulation:
    """Mark a simulation as COMPLETED and record end_time."""
    simulation.status = SimulationStatus.COMPLETED.value
    simulation.end_time = datetime.now(timezone.utc)
    db.commit()
    db.refresh(simulation)
    return simulation


# ── Batch runner ────────────────────────────────────────────────

def run_batch(request) -> dict:
    """
    Execute the SimulationEngine `request.steps` times and aggregate the
    results into a BatchSimulateResponse-compatible dict.

    Each step is a fully independent evaluation of the same graph.
    Because the current engine models steady-state processes (no time-
    varying feedback between steps), every frame is identical for a fixed
    graph.  The architecture is deliberately forward-compatible: when the
    engine gains time-varying models, the loop below will automatically
    feed the previous frame’s state into the next iteration.

    Parameters
    ----------
    request : BatchSimulateRequest
        The validated Pydantic request object from the router.

    Returns
    -------
    dict
        A dict matching BatchSimulateResponse’s field layout.
    """
    engine = SimulationEngine()

    # Convert Pydantic models → plain dicts expected by the engine.
    machines_raw = [
        {
            "id":               m.id,
            "name":             m.name,
            "process":          m.process,
            "subprocess":       m.subprocess,
            "parameters":       m.parameters,
            "input_attributes": m.input_attributes,
        }
        for m in request.machines
    ]

    connections_raw = [
        {
            "source_machine_id": c.source_machine_id,
            "target_machine_id": c.target_machine_id,
        }
        for c in request.connections
    ]

    line_id = request.production_line_id or uuid.uuid4()

    frames = []
    for step in range(request.steps):
        # Deep-copy machines_raw so _layer3_instance mutations from the
        # previous step do not bleed into the next iteration.
        import copy
        step_machines = copy.deepcopy(machines_raw)

        result = engine.run_from_dicts(step_machines, connections_raw, line_id)
        frame_dict = result.to_dict()  # uses the already-defined to_dict()

        frames.append({
            "step": step,
            "success": result.success,
            "production_line_full_input":  frame_dict["production_line_full_input"],
            "production_line_full_output": frame_dict["production_line_full_output"],
            "links":           frame_dict["links"],
            "errors_warnings": frame_dict["errors_warnings"],
        })

        # Bail out early if the engine reports a hard failure on any step.
        if not result.success:
            break

    return {
        "production_line_id": line_id,
        "steps_requested":   request.steps,
        "steps_completed":   len(frames),
        "frames":            frames,
    }
