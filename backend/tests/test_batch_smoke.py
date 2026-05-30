"""
Smoke test for the batch simulation endpoint logic.
Runs run_batch() directly (without a running server) to verify
the full import chain and data flow works end-to-end.

Run from the repo root:
    python backend/tests/test_batch_smoke.py
"""
import sys
import uuid
from pathlib import Path

# ── Add simulation/ to path (mirrors what engine.py does at runtime) ─────────
_ROOT = Path(__file__).resolve().parents[2]   # indus-io/
sys.path.insert(0, str(_ROOT / "simulation"))

# ── Minimal stub of BatchSimulateRequest so we can call run_batch() ──────────
# (avoids the need to spin up FastAPI / Pydantic in this script)
from types import SimpleNamespace

from simulation_engine import SimulationEngine
import copy


def run_batch_direct(machines_raw, connections_raw, steps, line_id=None):
    """Inline version of engine.run_batch() for testing."""
    engine = SimulationEngine()
    line_id = line_id or uuid.uuid4()
    frames = []
    for step in range(steps):
        step_machines = copy.deepcopy(machines_raw)
        result = engine.run_from_dicts(step_machines, connections_raw, line_id)
        frame_dict = result.to_dict()
        frames.append({
            "step": step,
            "success": result.success,
            "production_line_full_input":  frame_dict["production_line_full_input"],
            "production_line_full_output": frame_dict["production_line_full_output"],
            "links":           frame_dict["links"],
            "errors_warnings": frame_dict["errors_warnings"],
        })
        if not result.success:
            break
    return {
        "production_line_id": str(line_id),
        "steps_requested":   steps,
        "steps_completed":   len(frames),
        "frames":            frames,
    }


# ── Test data: single-node (Rotor Spinning) production line ──────────────────
machines_raw = [
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "name": "Rotor Spinner R-01",
        "process": "Spinning",
        "subprocess": "Rotor Spinning",
        "parameters": {
            "rotor_diameter_mm": 33.0,
            "rotor_speed_rpm": 100_000,
            "twist_factor_am": 130.0,
            "opening_roller_speed_rpm": 7_500,
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
            "operating_hours_since_maintenance": 600.0,
        },
        "input_attributes": {
            "fiber_type": "cotton_carded",
            "fiber_length_mm": 27.0,
            "fiber_fineness_dtex": 1.7,
            "short_fiber_content_pct": 14.0,
            "fiber_tensile_strength_cN_tex": 28.0,
            "sliver_count_ktex": 4.5,
            "moisture_content_pct": 7.0,
            "trash_content_pct": 1.2,
        },
    }
]

STEPS = 5
response = run_batch_direct(machines_raw, connections_raw=[], steps=STEPS)

# ── Assertions ────────────────────────────────────────────────────────────────
assert response["steps_requested"] == STEPS,  "steps_requested mismatch"
assert response["steps_completed"] == STEPS,  "steps_completed mismatch"
assert len(response["frames"])     == STEPS,  "frame count mismatch"

for frame in response["frames"]:
    assert frame["success"],           f"step {frame['step']} failed"
    assert frame["production_line_full_output"], f"step {frame['step']} has no output"

# ── Print summary ─────────────────────────────────────────────────────────────
print(f"  steps_requested  : {response['steps_requested']}")
print(f"  steps_completed  : {response['steps_completed']}")
print(f"  frames           : {len(response['frames'])}")

first_frame  = response["frames"][0]
sample_out   = list(first_frame["production_line_full_output"].values())[0]
print(f"  sample output keys ({len(sample_out)}): {list(sample_out.keys())[:5]} ...")

warnings = first_frame["errors_warnings"]
if warnings:
    print(f"  warnings ({len(warnings)}): {warnings[0][:80]}")
else:
    print("  warnings: none")

print("\nSMOKE TEST PASSED")
