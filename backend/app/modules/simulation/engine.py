"""
Simulation Engine — placeholder for future simulation execution logic.

This module will contain the actual simulation orchestration:
  - Graph traversal of the production line (machines + connections)
  - Step-by-step execution of machine processing
  - KPI calculation during simulation
  - Real-time log generation
  - Alert triggering on threshold breaches

For now, it exposes helper functions that the simulation service
and future WebSocket handlers can call.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.modules.simulation.models import Simulation
from app.core.permissions import SimulationStatus


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
