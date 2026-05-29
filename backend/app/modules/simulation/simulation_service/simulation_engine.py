"""
simulation_engine.py
────────────────────
Orchestrates a full indus.io production-line simulation by traversing the
machine graph stored in the database schema and dispatching each node to the
correct simulation module.

Architecture overview
─────────────────────
                    DB schema objects
                    ─────────────────
  ProductionLine ──► machines (nodes) + connections (directed edges)
        │
        │   each Machine carries:
        │     • process       – top-level process name  (e.g. "Spinning")
        │     • subprocess    – specific subprocess     (e.g. "Rotor Spinning")
        │     • parameters    – JSONB dict of Layer 3 values
        │     • MachineAttributeValue rows of type INPUT  (Layer 2 values)
        │     • MachineAttributeValue rows of type OUTPUT (Layer 4 results)
        │
        ▼
  SimulationEngine.run(production_line_id)
        │
        ├─ 1. Build directed acyclic graph (DAG) from Connection rows
        ├─ 2. Topological sort → execution order
        ├─ 3. For each machine (in order):
        │       a. Collect Layer 2  – from upstream machine's Layer 4 output
        │                             (bridge function) OR from DB INPUT rows
        │       b. Collect Layer 3  – from machine.parameters JSONB
        │       c. Dispatch         – REGISTRY[(process, subprocess)](L2, L3)
        │       d. Persist Layer 4  – write OUTPUT AttributeValue rows to DB
        └─ 4. Return SimulationResult with all per-machine outputs + warnings

Layer 4 → Layer 2 bridges
──────────────────────────
Each pair of connected process types has a dedicated bridge function that
converts the upstream machine's output dataclass into the downstream machine's
input dataclass — preserving every field name and unit as defined in the
individual simulation modules.

Supported subprocess keys (process → subprocess)
─────────────────────────────────────────────────
  Spinning    → Rotor Spinning          (rotor.py)
  Spinning    → Air-jet Spinning        (airjet.py)
  Weaving     → Plain Weaving           (plain_weaving.py)
  Knitting    → Weft Knitting           (weft_knitting.py)
  Colouring   → Reactive Dyeing         (reactive_dyeing.py)
  Colouring   → Vat Dyeing              (vat_dyeing.py)
"""

from __future__ import annotations

# Make the standalone `simulation/` package importable when running from
# the `backend/` folder (mirrors the shim used by the FastAPI bridge).
import sys
from pathlib import Path
_SIM_PKG_DIR = Path(__file__).resolve().parents[5] / "simulation"
if str(_SIM_PKG_DIR) not in sys.path:
    sys.path.insert(0, str(_SIM_PKG_DIR))

# Import simulation modules with resilient fallbacks. Prefer relative imports
# when the module is used as a package (`app.modules.simulation.simulation_service`),
# then try the repository-level `simulation.*` package, then bare names.
try:
    from .printing.screen_printing import simulate_screen_printing
    from .printing.rotary_printing import simulate_rotary_printing
    from .knitting.warp_knitting import simulate_warp_knitting
    from .weaving.dobby import simulate_dobby_weaving
except Exception:
    try:
        from simulation.printing.screen_printing import simulate_screen_printing
        from simulation.printing.rotary_printing import simulate_rotary_printing
        from simulation.knitting.warp_knitting import simulate_warp_knitting
        from simulation.weaving.dobby import simulate_dobby_weaving
    except Exception:
        from printing.screen_printing import simulate_screen_printing
        from printing.rotary_printing import simulate_rotary_printing
        from knitting.warp_knitting import simulate_warp_knitting
        from weaving.dobby import simulate_dobby_weaving

import dataclasses
import uuid
from collections import defaultdict, deque
from dataclasses import asdict
from typing import Any, Callable

# ── Import simulation modules ────────────────────────────────────────────────
# Each module exposes: one simulate_*() function + its dataclasses.
# Adjust the import paths to match your project layout.
try:
    from .spinning.rotor import (
        InputMaterial as RotorInputMaterial,
        RotorOperationalParams,
        YarnQualityOutput,
        simulate_rotor_spinning,
    )
except Exception:
    try:
        from simulation.spinning.rotor import (
            InputMaterial as RotorInputMaterial,
            RotorOperationalParams,
            YarnQualityOutput,
            simulate_rotor_spinning,
        )
    except Exception:
        from spinning.rotor import (
            InputMaterial as RotorInputMaterial,
            RotorOperationalParams,
            YarnQualityOutput,
            simulate_rotor_spinning,
        )
try:
    from .spinning.airjet import (
        InputMaterial as AirjetInputMaterial,
        AirjetOperationalParams,
        YarnQualityOutput as AirjetYarnQualityOutput,
        simulate_airjet_spinning,
    )
except Exception:
    try:
        from simulation.spinning.airjet import (
            InputMaterial as AirjetInputMaterial,
            AirjetOperationalParams,
            YarnQualityOutput as AirjetYarnQualityOutput,
            simulate_airjet_spinning,
        )
    except Exception:
        from spinning.airjet import (
            InputMaterial as AirjetInputMaterial,
            AirjetOperationalParams,
            YarnQualityOutput as AirjetYarnQualityOutput,
            simulate_airjet_spinning,
        )
try:
    from .weaving.plain import (
        InputYarns,
        PlainWeavingParams,
        FabricQualityOutput,
        simulate_plain_weaving,
    )
except Exception:
    try:
        from simulation.weaving.plain import (
            InputYarns,
            PlainWeavingParams,
            FabricQualityOutput,
            simulate_plain_weaving,
        )
    except Exception:
        from weaving.plain import (
            InputYarns,
            PlainWeavingParams,
            FabricQualityOutput,
            simulate_plain_weaving,
        )
try:
    from .knitting.weft_knitting import (
        InputFabric as KnittingInputFabric,
        WeftKnittingParams,
        KnittedFabricOutput,
        simulate_weft_knitting,
    )
except Exception:
    try:
        from simulation.knitting.weft_knitting import (
            InputFabric as KnittingInputFabric,
            WeftKnittingParams,
            KnittedFabricOutput,
            simulate_weft_knitting,
        )
    except Exception:
        from knitting.weft_knitting import (
            InputFabric as KnittingInputFabric,
            WeftKnittingParams,
            KnittedFabricOutput,
            simulate_weft_knitting,
        )
try:
    from .coloring.reactive_dyeing import (
        InputFabric as ReactiveDyeingInputFabric,
        ReactiveDyeingParams,
        DyedFabricOutput as ReactiveDyedFabricOutput,
        simulate_reactive_dyeing,
    )
except Exception:
    try:
        from simulation.coloring.reactive_dyeing import (
            InputFabric as ReactiveDyeingInputFabric,
            ReactiveDyeingParams,
            DyedFabricOutput as ReactiveDyedFabricOutput,
            simulate_reactive_dyeing,
        )
    except Exception:
        from coloring.reactive_dyeing import (
            InputFabric as ReactiveDyeingInputFabric,
            ReactiveDyeingParams,
            DyedFabricOutput as ReactiveDyedFabricOutput,
            simulate_reactive_dyeing,
        )


# ─────────────────────────────────────────────────────────────────────────────
# TYPE ALIASES
# ─────────────────────────────────────────────────────────────────────────────

# A "raw machine record" mirrors the DB Machine row + its related rows.
# In a real FastAPI app this would be a SQLAlchemy model instance; here we
# use plain dicts so the engine is DB-library-agnostic and fully testable.
RawMachine = dict[str, Any]
RawConnection = dict[str, Any]   # {source_machine_id, target_machine_id}

# A simulation output is any dataclass instance produced by a simulate_*() fn.
SimOutput = Any


# ────────────────────────────────────────────────────────────────────────────
# RESULT DATACLASS
# ─────────────────────────────────────────────────────────────────────────────

@dataclasses.dataclass
class MachineSimResult:
    """Holds the complete simulation result for a single machine node."""
    machine_id: uuid.UUID
    machine_name: str
    process: str
    subprocess: str
    # Layer 2 dict (input to this node)
    layer2_input: dict[str, Any]
    # Layer 3 dict (operational params for this node)
    layer3_params: dict[str, Any]
    # Layer 4 dataclass instance (simulation output)
    layer4_output: SimOutput
    # Serialised Layer 4 as a flat dict — ready for DB persistence
    layer4_dict: dict[str, Any]
    # Any validation warnings raised by the simulation function
    warnings: list[str]


@dataclasses.dataclass
class SimulationResult:
    """Top-level result returned by SimulationEngine.run()."""
    production_line_id: uuid.UUID
    execution_order: list[uuid.UUID]          # Machine IDs in topo-sort order
    machine_results: dict[uuid.UUID, MachineSimResult]
    global_warnings: list[str]
    success: bool
    connections: list[dict] = dataclasses.field(default_factory=list) # {source_machine_id, target_machine_id}

    def to_dict(self) -> dict:
        """
        Serialises the simulation result to a plain dict.

        Returns a structure with four keys:
          production_line_full_input  – Layer 2 inputs of root machines
          production_line_full_output – Layer 4 outputs of leaf machines
          links                       – per-edge Layer 4 state (as {source, target, states})
          errors_warnings             – all global warnings + per-machine warnings
        """
        # Calculate in-degree and out-degree
        in_degree = {mid: 0 for mid in self.execution_order}
        out_degree = {mid: 0 for mid in self.execution_order}
        for conn in self.connections:
            src = conn["source_machine_id"]
            tgt = conn["target_machine_id"]
            if tgt in in_degree: in_degree[tgt] += 1
            if src in out_degree: out_degree[src] += 1

        # Root machines (in-degree 0) — their layer2_input is the full line input
        root_machines = [mid for mid in self.execution_order if in_degree.get(mid, 0) == 0]
        # Leaf machines (out-degree 0) — their layer4_dict is the full line output
        leaf_machines = [mid for mid in self.execution_order if out_degree.get(mid, 0) == 0]

        full_input = {
            str(mid): self.machine_results[mid].layer2_input
            for mid in root_machines if mid in self.machine_results
        }

        full_output = {
            str(mid): self.machine_results[mid].layer4_dict
            for mid in leaf_machines if mid in self.machine_results
        }

        # Build links array with 'states' over tick t (length 1 for steady-state)
        links = []
        for conn in self.connections:
            src = conn["source_machine_id"]
            tgt = conn["target_machine_id"]
            if src in self.machine_results:
                state_at_t = self.machine_results[src].layer4_dict
                links.append({
                    "source_machine": str(src),
                    "target_machine": str(tgt),
                    "states": [state_at_t],  # array of states, t=0
                })

        # Collect all errors and warnings
        errors_warnings = list(self.global_warnings)
        for mres in self.machine_results.values():
            errors_warnings.extend(mres.warnings)

        return {
            "production_line_full_input":  full_input,
            "links":                       links,
            "production_line_full_output": full_output,
            "errors_warnings":             errors_warnings,
        }

    def save_to_json(self, filepath: str) -> None:
        import json
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)


# ─────────────────────────────────────────────────────────────────────────────
# DISPATCH REGISTRY
# ─────────────────────────────────────────────────────────────────────────────
# Maps (process.lower(), subprocess.lower()) → simulation function.
# Add new entries here whenever a new simulation module is written.

_REGISTRY: dict[tuple[str, str], Callable] = {
    ("spinning", "rotor spinning"):       simulate_rotor_spinning,
    ("spinning", "air-jet spinning"):     simulate_airjet_spinning,
    ("spinning", "airjet spinning"):      simulate_airjet_spinning,
    ("weaving",  "plain weaving"):        simulate_plain_weaving,
    ("weaving", "dobby weaving"):         simulate_dobby_weaving,
    ("knitting", "warp knitting"):        simulate_warp_knitting,
    ("knitting", "weft knitting"):        simulate_weft_knitting,
    ("colouring","reactive dyeing"):      simulate_reactive_dyeing,
    # ("colouring","vat dyeing"):           simulate_vat_dyeing,
    # aliases
    ("dyeing",   "reactive dyeing"):      simulate_reactive_dyeing,
    # ("dyeing",   "vat dyeing"):           simulate_vat_dyeing,
    ("printing", "rotary printing"):      simulate_rotary_printing,
    ("printing", "screen printing"):      simulate_screen_printing
}


def _lookup(process: str, subprocess: str) -> Callable:
    key = (process.strip().lower(), subprocess.strip().lower())
    fn = _REGISTRY.get(key)
    if fn is None:
        supported = ", ".join(f"({p}/{s})" for p, s in _REGISTRY)
        raise ValueError(
            f"No simulation module registered for process='{process}' / "
            f"subprocess='{subprocess}'. Supported: {supported}"
        )
    return fn


# ─────────────────────────────────────────────────────────────────────────────
# LAYER 2 BUILDERS
# ─────────────────────────────────────────────────────────────────────────────
# Each function converts:
#   - upstream_output: the Layer 4 dataclass from the immediately upstream node
#   - override_dict:   any INPUT-type AttributeValue rows stored in the DB
#                      (user-supplied overrides take precedence over derived values)
# into the correct Layer 2 input dataclass for the downstream node.

def _build_rotor_input(override_dict: dict) -> RotorInputMaterial:
    """
    Layer 2 for Rotor Spinning.
    No upstream node (spinning is the first process) — all values come from
    the machine's INPUT AttributeValue rows (raw material properties).
    """
    return RotorInputMaterial(
        fiber_type=override_dict.get("fiber_type", "cotton_carded"),
        fiber_length_mm=float(override_dict.get("fiber_length_mm", 27.0)),
        fiber_fineness_dtex=float(override_dict.get("fiber_fineness_dtex", 1.7)),
        short_fiber_content_pct=float(override_dict.get("short_fiber_content_pct", 14.0)),
        fiber_tensile_strength_cN_tex=float(override_dict.get("fiber_tensile_strength_cN_tex", 28.0)),
        sliver_count_ktex=float(override_dict.get("sliver_count_ktex", 4.5)),
        moisture_content_pct=float(override_dict.get("moisture_content_pct", 7.0)),
        trash_content_pct=float(override_dict.get("trash_content_pct", 1.2)),
    )


def _build_airjet_input(override_dict: dict) -> AirjetInputMaterial:
    """Layer 2 for Air-jet Spinning — also a first-process node."""
    return AirjetInputMaterial(
        fiber_type=override_dict.get("fiber_type", "cotton_combed"),
        fiber_length_mm=float(override_dict.get("fiber_length_mm", 30.0)),
        fiber_fineness_dtex=float(override_dict.get("fiber_fineness_dtex", 1.5)),
        short_fiber_content_pct=float(override_dict.get("short_fiber_content_pct", 6.0)),
        fiber_tensile_strength_cN_tex=float(override_dict.get("fiber_tensile_strength_cN_tex", 32.0)),
        sliver_count_ktex=float(override_dict.get("sliver_count_ktex", 3.0)),
        moisture_content_pct=float(override_dict.get("moisture_content_pct", 6.5)),
        trash_content_pct=float(override_dict.get("trash_content_pct", 0.3)),
    )


def _spinning_output_to_weaving_input(
    yarn_output: YarnQualityOutput,
    spinning_params: RotorOperationalParams | AirjetOperationalParams,
    override_dict: dict,
) -> InputYarns:
    """
    Bridge: Spinning Layer 4 (YarnQualityOutput) → Weaving Layer 2 (InputYarns).

    The warp and weft yarns fed to the loom come from spinning nodes.
    In the simplest single-yarn production line, both warp and weft are
    identical yarns from the same upstream machine.  A production line
    with two spinning nodes connected to one weaving node will call this
    bridge twice — once for warp, once for weft — and merge the results.

    Fields mapped (spinning L4 → weaving L2):
      yarn_tenacity_cN_tex    → warp/weft_yarn_tenacity_cN_tex
      yarn_evenness_CVm_pct   → warp/weft_yarn_CVm_pct
      hairiness_H             → warp/weft_yarn_hairiness_H
      actual_twist_turns_per_m→ warp/weft_yarn_twist_t_per_m
      yarn_count_tex/Ne from spinning L3 params
    """
    tex = float(spinning_params.yarn_count_tex)
    Ne  = float(spinning_params.yarn_count_Ne)
    ytype = spinning_params.yarn_count_tex  # will grab fiber_type below

    # fiber_type lives in the spinning L2 (InputMaterial), not L4.
    # The override_dict may carry it from the DB INPUT rows.
    fiber_type = override_dict.get("fiber_type", "cotton_carded")

    return InputYarns(
        warp_yarn_count_tex=override_dict.get("warp_yarn_count_tex", tex),
        warp_yarn_count_Ne=override_dict.get("warp_yarn_count_Ne", Ne),
        warp_yarn_tenacity_cN_tex=override_dict.get(
            "warp_yarn_tenacity_cN_tex", yarn_output.yarn_tenacity_cN_tex),
        warp_yarn_CVm_pct=override_dict.get(
            "warp_yarn_CVm_pct", yarn_output.yarn_evenness_CVm_pct),
        warp_yarn_hairiness_H=override_dict.get(
            "warp_yarn_hairiness_H", yarn_output.hairiness_H),
        warp_yarn_twist_t_per_m=override_dict.get(
            "warp_yarn_twist_t_per_m", yarn_output.actual_twist_turns_per_m),
        warp_yarn_type=override_dict.get("warp_yarn_type", fiber_type),
        # Weft defaults to same yarn unless overridden
        weft_yarn_count_tex=override_dict.get("weft_yarn_count_tex", tex),
        weft_yarn_count_Ne=override_dict.get("weft_yarn_count_Ne", Ne),
        weft_yarn_tenacity_cN_tex=override_dict.get(
            "weft_yarn_tenacity_cN_tex", yarn_output.yarn_tenacity_cN_tex),
        weft_yarn_CVm_pct=override_dict.get(
            "weft_yarn_CVm_pct", yarn_output.yarn_evenness_CVm_pct),
        weft_yarn_hairiness_H=override_dict.get(
            "weft_yarn_hairiness_H", yarn_output.hairiness_H),
        weft_yarn_twist_t_per_m=override_dict.get(
            "weft_yarn_twist_t_per_m", yarn_output.actual_twist_turns_per_m),
        weft_yarn_type=override_dict.get("weft_yarn_type", fiber_type),
    )


def _weaving_output_to_knitting_input(
    fabric_output: FabricQualityOutput,
    override_dict: dict,
) -> KnittingInputFabric:
    """
    Bridge: Weaving Layer 4 (FabricQualityOutput) → Knitting Layer 2 (InputFabric).

    Every field in InputFabric maps 1-to-1 onto FabricQualityOutput.
    The override_dict allows the Production Manager to overwrite individual
    values via the DB INPUT AttributeValue rows without re-running weaving.
    """
    d = asdict(fabric_output)
    d.update(override_dict)           # DB overrides win
    return KnittingInputFabric(**{
        k: d[k] for k in KnittingInputFabric.__dataclass_fields__
    })


def _weaving_output_to_reactive_input(
    fabric_output: FabricQualityOutput,
    override_dict: dict,
) -> ReactiveDyeingInputFabric:
    """
    Bridge: Weaving Layer 4 (FabricQualityOutput) → Reactive Dyeing Layer 2.
    """
    d = asdict(fabric_output)
    d.update(override_dict)
    return ReactiveDyeingInputFabric(**{
        k: d[k] for k in ReactiveDyeingInputFabric.__dataclass_fields__
    })


# def _weaving_output_to_vat_input(
#     fabric_output: FabricQualityOutput,
#     override_dict: dict,
# ) -> VatDyeingInputFabric:
#     """
#     Bridge: Weaving Layer 4 (FabricQualityOutput) → Vat Dyeing Layer 2.
#     """
#     d = asdict(fabric_output)
#     d.update(override_dict)
#     return VatDyeingInputFabric(**{
#         k: d[k] for k in VatDyeingInputFabric.__dataclass_fields__
#     })


# ─────────────────────────────────────────────────────────────────────────────
# LAYER 3 BUILDER — deserialise JSONB parameters → typed dataclass
# ─────────────────────────────────────────────────────────────────────────────

def _build_layer3(process: str, subprocess: str, params_dict: dict) -> Any:
    """
    Deserialises the machine.parameters JSONB column into the correct
    Layer 3 dataclass for the given (process, subprocess).

    The JSONB dict is expected to contain exactly the field names defined
    in the corresponding *Params dataclass.  Missing keys fall back to the
    dataclass field defaults, if any.

    For fields with no default and no value in the JSONB, a KeyError is
    raised with a descriptive message so the Production Manager knows which
    parameter needs to be configured on the canvas.
    """
    p = process.strip().lower()
    s = subprocess.strip().lower()

    def _safe(cls, data: dict):
        """Build cls from data dict, raising a helpful error on missing keys."""
        fields = cls.__dataclass_fields__
        kwargs = {}
        missing = []
        for name, field in fields.items():
            if name in data:
                kwargs[name] = data[name]
            elif field.default is not dataclasses.MISSING:
                kwargs[name] = field.default
            elif field.default_factory is not dataclasses.MISSING:  # type: ignore[attr-defined]
                kwargs[name] = field.default_factory()
            else:
                missing.append(name)
        if missing:
            raise ValueError(
                f"Machine ({process}/{subprocess}) is missing required "
                f"Layer 3 parameters: {missing}. "
                "Please configure these on the production canvas."
            )
        return cls(**kwargs)

    if p == "spinning" and "rotor" in s:
        return _safe(RotorOperationalParams, params_dict)
    if p == "spinning" and ("air" in s or "jet" in s):
        return _safe(AirjetOperationalParams, params_dict)
    if p == "weaving" and "plain" in s:
        return _safe(PlainWeavingParams, params_dict)
    if p == "knitting" and "weft" in s:
        return _safe(WeftKnittingParams, params_dict)
    if p in ("colouring", "dyeing") and "reactive" in s:
        return _safe(ReactiveDyeingParams, params_dict)
    # if p in ("colouring", "dyeing") and "vat" in s:
    #     return _safe(VatDyeingParams, params_dict)

    raise ValueError(
        f"No Layer 3 dataclass mapped for process='{process}' / "
        f"subprocess='{subprocess}'."
    )


# ─────────────────────────────────────────────────────────────────────────────
# DAG UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def _build_adjacency(
    machines: list[RawMachine],
    connections: list[RawConnection],
) -> tuple[dict[uuid.UUID, list[uuid.UUID]],   # children  (src → [dst])
           dict[uuid.UUID, list[uuid.UUID]],   # parents   (dst → [src])
           dict[uuid.UUID, int]]:              # in-degree
    """Builds forward adjacency, reverse adjacency, and in-degree maps."""
    children:  dict[uuid.UUID, list[uuid.UUID]] = defaultdict(list)
    parents:   dict[uuid.UUID, list[uuid.UUID]] = defaultdict(list)
    in_degree: dict[uuid.UUID, int]             = {m["id"]: 0 for m in machines}

    for conn in connections:
        src = conn["source_machine_id"]
        dst = conn["target_machine_id"]
        children[src].append(dst)
        parents[dst].append(src)
        in_degree[dst] = in_degree.get(dst, 0) + 1

    return children, parents, in_degree


def _topological_sort(
    machines: list[RawMachine],
    connections: list[RawConnection],
) -> list[uuid.UUID]:
    """
    Returns machine IDs in topological (execution) order using Kahn's algorithm.
    Raises ValueError if a cycle is detected (invalid production line graph).
    """
    children, parents, in_degree = _build_adjacency(machines, connections)

    queue: deque[uuid.UUID] = deque(
        mid for mid, deg in in_degree.items() if deg == 0
    )
    order: list[uuid.UUID] = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for child in children[node]:
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)

    if len(order) != len(machines):
        cycle_nodes = [m["name"] for m in machines if m["id"] not in order]
        raise ValueError(
            f"Production line graph contains a cycle involving: {cycle_nodes}. "
            "Cycles are not allowed — each machine must receive its input from "
            "a strictly upstream predecessor."
        )

    return order


# ─────────────────────────────────────────────────────────────────────────────
# OUTPUT → INPUT BRIDGE DISPATCHER
# ─────────────────────────────────────────────────────────────────────────────

def _bridge(
    upstream_output: SimOutput,
    upstream_machine: RawMachine,
    downstream_machine: RawMachine,
    downstream_override: dict,
) -> Any:
    """
    Routes the upstream machine's Layer 4 output to the correct Layer 2
    builder for the downstream machine.

    upstream_output  — the dataclass instance returned by the upstream
                       simulate_*() call.
    upstream_machine — the raw machine dict (carries process/subprocess).
    downstream_machine — the machine that will receive the input.
    downstream_override — INPUT-type AttributeValue rows for the downstream
                          machine (user-supplied DB overrides).

    Returns the appropriate Layer 2 dataclass instance.
    """
    up_proc  = upstream_machine.get("process", "").lower()
    up_sub   = upstream_machine.get("subprocess", "").lower()
    dn_proc  = downstream_machine.get("process", "").lower()
    dn_sub   = downstream_machine.get("subprocess", "").lower()

    # ── Spinning → Weaving ───────────────────────────────────────────────────
    if "spinning" in up_proc and "weaving" in dn_proc:
        # Retrieve the Layer 3 params that were used for the spinning node
        # so we can pass yarn_count_tex / yarn_count_Ne to the bridge.
        spinning_params = upstream_machine.get("_layer3_instance")
        if spinning_params is None:
            raise RuntimeError(
                f"Upstream spinning node '{upstream_machine['name']}' has not "
                "been simulated yet. Check topological order."
            )
        return _spinning_output_to_weaving_input(
            upstream_output, spinning_params, downstream_override
        )

    # ── Weaving → Knitting ───────────────────────────────────────────────────
    if "weaving" in up_proc and "knitting" in dn_proc:
        return _weaving_output_to_knitting_input(upstream_output, downstream_override)

    # ── Weaving → Reactive Dyeing ────────────────────────────────────────────
    if "weaving" in up_proc and "reactive" in dn_sub:
        return _weaving_output_to_reactive_input(upstream_output, downstream_override)

    # ── Weaving → Vat Dyeing ─────────────────────────────────────────────────
    # if "weaving" in up_proc and "vat" in dn_sub:
    #     return _weaving_output_to_vat_input(upstream_output, downstream_override)

    raise NotImplementedError(
        f"No bridge implemented for connection "
        f"'{upstream_machine['process']}/{upstream_machine['subprocess']}' → "
        f"'{downstream_machine['process']}/{downstream_machine['subprocess']}'. "
        "Add a bridge function in simulation_engine.py."
    )


# ─────────────────────────────────────────────────────────────────────────────
# DB PERSISTENCE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _flatten_output(output: SimOutput) -> dict[str, Any]:
    """
    Converts any Layer 4 dataclass to a flat dict suitable for writing to
    the machine_attribute_values table.

    Lists (e.g. warnings) are converted to a single joined string so they
    fit in a Float-typed AttributeValue.  If your schema has a Text column
    for warnings you can store them as-is.
    """
    raw = asdict(output)
    flat = {}
    for k, v in raw.items():
        if isinstance(v, list):
            # Warnings list → joined string (store separately if needed)
            flat[k] = "; ".join(str(i) for i in v) if v else ""
        elif isinstance(v, bool):
            flat[k] = 1.0 if v else 0.0
        elif isinstance(v, str):
            flat[k] = v    # caller handles non-Float columns
        else:
            flat[k] = float(v) if v is not None else None
    return flat


def persist_layer4_to_db(
    session,                     # SQLAlchemy Session
    machine_id: uuid.UUID,
    flat_output: dict[str, Any],
    attribute_cache: dict[str, Any],  # name → AttributeDefinition ORM object
) -> None:
    """
    Writes Layer 4 results back to machine_attribute_values.

    For each key in flat_output:
      1. Look up (or create) the AttributeDefinition row with type='OUTPUT'.
      2. Upsert a MachineAttributeValue row for this machine.

    attribute_cache is a dict you pre-populate with existing AttributeDefinition
    rows so we don't hit the DB for every field on every machine.

    This function is intentionally kept ORM-library-agnostic in signature;
    fill in the body with your actual SQLAlchemy / async session calls.
    """
    from app.db.models import AttributeDefinition, MachineAttributeValue  # noqa: F401
    from datetime import datetime, timezone

    for attr_name, value in flat_output.items():
        if value is None:
            continue

        # 1. Resolve or create AttributeDefinition
        attr_def = attribute_cache.get(attr_name)
        if attr_def is None:
            attr_def = (
                session.query(AttributeDefinition)
                .filter_by(name=attr_name, type="OUTPUT")
                .first()
            )
            if attr_def is None:
                attr_def = AttributeDefinition(
                    id=uuid.uuid4(),
                    name=attr_name,
                    type="OUTPUT",
                    unit=None,   # unit metadata can be added separately
                )
                session.add(attr_def)
                session.flush()
            attribute_cache[attr_name] = attr_def

        # 2. Upsert MachineAttributeValue
        # For Float fields only; string fields need a Text column (see note above).
        if not isinstance(value, str):
            mav = (
                session.query(MachineAttributeValue)
                .filter_by(machine_id=machine_id, attribute_id=attr_def.id)
                .first()
            )
            if mav is None:
                mav = MachineAttributeValue(
                    id=uuid.uuid4(),
                    machine_id=machine_id,
                    attribute_id=attr_def.id,
                    value=float(value),
                    timestamp=datetime.now(timezone.utc),
                )
                session.add(mav)
            else:
                mav.value = float(value)
                mav.timestamp = datetime.now(timezone.utc)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class SimulationEngine:
    """
    Orchestrates the simulation of an entire production line.

    Usage (dict-based, no DB):
        machines    = [{"id": ..., "process": "Spinning", "subprocess": "Rotor Spinning",
                         "parameters": {...}, "input_attributes": {...}}, ...]
        connections = [{"source_machine_id": ..., "target_machine_id": ...}, ...]
        result = SimulationEngine().run_from_dicts(machines, connections, line_id)

    Usage (SQLAlchemy):
        with Session() as session:
            result = SimulationEngine().run_from_db(session, production_line_id)
    """

    # ── dict-based entry point ───────────────────────────────────────────────

    def run_from_dicts(
        self,
        machines: list[RawMachine],
        connections: list[RawConnection],
        production_line_id: uuid.UUID | None = None,
    ) -> SimulationResult:
        """
        Runs a full production-line simulation from plain Python dicts.

        Each machine dict must contain:
          id              uuid.UUID
          name            str
          process         str   (e.g. "Spinning")
          subprocess      str   (e.g. "Rotor Spinning")
          parameters      dict  (Layer 3 — maps to *Params dataclass fields)
          input_attributes dict  (Layer 2 overrides — maps to *InputMaterial fields;
                                  may be empty for mid-chain nodes)
        """
        line_id = production_line_id or uuid.uuid4()
        machine_map: dict[uuid.UUID, RawMachine] = {m["id"]: m for m in machines}

        # ── Step 1: topological sort ─────────────────────────────────────────
        try:
            exec_order = _topological_sort(machines, connections)
        except ValueError as exc:
            return SimulationResult(
                production_line_id=line_id,
                execution_order=[],
                machine_results={},
                global_warnings=[str(exc)],
                success=False,
            )

        # Build parent map: dst → list of src
        # the destination should have only one source
        _, parents, _ = _build_adjacency(machines, connections)

        machine_results: dict[uuid.UUID, MachineSimResult] = {}
        global_warnings: list[str] = []

        # ── Step 2: execute each node in order ───────────────────────────────
        for mid in exec_order:
            machine = machine_map[mid]
            process    = machine.get("process",    "")
            subprocess = machine.get("subprocess", "")
            params_raw = machine.get("parameters", {}) or {}
            input_attr = machine.get("input_attributes", {}) or {}

            try:
                # ── Layer 3: deserialise parameters JSONB → typed dataclass ──
                layer3 = _build_layer3(process, subprocess, params_raw)
                # Stash on the machine dict so downstream bridges can read it
                machine["_layer3_instance"] = layer3

                # ── Layer 2: build input dataclass ───────────────────────────
                upstream_ids = parents.get(mid, [])

                if not upstream_ids:
                    # Root node (no upstream) — Layer 2 comes entirely from
                    # the machine's INPUT AttributeValue rows.
                    layer2 = self._build_root_layer2(process, subprocess, input_attr)

                elif len(upstream_ids) == 1:
                    # Single upstream — bridge its Layer 4 output
                    up_id = upstream_ids[0]
                    up_result = machine_results[up_id]
                    layer2 = _bridge(
                        up_result.layer4_output,
                        machine_map[up_id],
                        machine,
                        input_attr,
                    )

                else:
                    # Multiple upstream nodes (e.g. two spinning machines → one
                    # weaving machine for warp + weft from different processes).
                    layer2 = self._build_multi_upstream_layer2(
                        process, subprocess,
                        upstream_ids, machine_map, machine_results,
                        input_attr,
                    )

                # ── Dispatch: run simulation ──────────────────────────────────
                simulate_fn = _lookup(process, subprocess)
                layer4_output = simulate_fn(layer2, layer3)

                # ── Serialise Layer 4 for DB persistence ─────────────────────
                layer4_dict = _flatten_output(layer4_output)
                warnings = getattr(layer4_output, "warnings", [])

                machine_results[mid] = MachineSimResult(
                    machine_id=mid,
                    machine_name=machine.get("name", str(mid)),
                    process=process,
                    subprocess=subprocess,
                    layer2_input=asdict(layer2),
                    layer3_params=asdict(layer3),
                    layer4_output=layer4_output,
                    layer4_dict=layer4_dict,
                    warnings=warnings,
                )

                if warnings:
                    global_warnings.append(
                        f"[{machine['name']}] {len(warnings)} warning(s): "
                        + "; ".join(warnings[:3])
                        + ("..." if len(warnings) > 3 else "")
                    )

            except Exception as exc:
                global_warnings.append(
                    f"[{machine.get('name', mid)}] SIMULATION ERROR: {exc}"
                )
                # Mark this node as failed so downstream nodes can degrade gracefully
                machine["_simulation_failed"] = True

        success = not any("SIMULATION ERROR" in w for w in global_warnings)

        return SimulationResult(
            production_line_id=line_id,
            execution_order=exec_order,
            machine_results=machine_results,
            global_warnings=global_warnings,
            success=success,
            connections=connections,
        )

    # ── SQLAlchemy entry point ───────────────────────────────────────────────

    def run_from_db(self, session, production_line_id: uuid.UUID) -> SimulationResult:
        """
        Loads the production line from the DB, runs the simulation, and writes
        Layer 4 outputs back to machine_attribute_values.

        Requires SQLAlchemy models as defined in the schema provided:
          ProductionLine, Machine, Connection, AttributeDefinition,
          MachineAttributeValue.
        """
        # pyrefly: ignore [missing-import]
        from app.db.models import (  # noqa: F401
            ProductionLine,
            Machine,
            Connection,
            AttributeDefinition,
            MachineAttributeValue,
        )

        # ── Load the production line ─────────────────────────────────────────
        line = session.get(ProductionLine, production_line_id)
        if line is None:
            raise ValueError(f"ProductionLine {production_line_id} not found.")

        # ── Serialise ORM objects → plain dicts for the engine ───────────────
        def _load_input_attrs(machine_orm) -> dict:
            """Loads INPUT-type AttributeValue rows as a flat name→value dict."""
            result = {}
            for mav in machine_orm.attribute_values:
                if mav.attribute.type == "INPUT":
                    result[mav.attribute.name] = mav.value
            return result

        machines_raw: list[RawMachine] = [
            {
                "id":                m.id,
                "name":              m.name,
                "process":           m.process or "",
                "subprocess":        m.subprocess or "",
                "parameters":        m.parameters or {},
                "input_attributes":  _load_input_attrs(m),
            }
            for m in line.machines
        ]

        connections_raw: list[RawConnection] = [
            {
                "source_machine_id": c.source_machine_id,
                "target_machine_id": c.target_machine_id,
            }
            for c in line.connections
        ]

        # ── Run simulation ────────────────────────────────────────────────────
        result = self.run_from_dicts(machines_raw, connections_raw, production_line_id)

        # ── Persist Layer 4 outputs to DB ─────────────────────────────────────
        attr_cache: dict[str, Any] = {}
        for mid, mres in result.machine_results.items():
            persist_layer4_to_db(session, mid, mres.layer4_dict, attr_cache)

        session.commit()
        return result

    # ── Internal helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _build_root_layer2(process: str, subprocess: str, input_attr: dict) -> Any:
        """
        Builds Layer 2 for a root node (no upstream machine).
        Root nodes are spinning machines; their raw material properties
        come from the user-supplied INPUT AttributeValue rows.
        """
        p = process.lower()
        s = subprocess.lower()
        if "spinning" in p and "rotor" in s:
            return _build_rotor_input(input_attr)
        if "spinning" in p and ("air" in s or "jet" in s):
            return _build_airjet_input(input_attr)
        raise ValueError(
            f"Machine '{process}/{subprocess}' has no upstream connection "
            "and no root Layer 2 builder is registered for it. "
            "Only spinning machines may be root nodes."
        )

    @staticmethod
    def _build_multi_upstream_layer2(
        process: str,
        subprocess: str,
        upstream_ids: list[uuid.UUID],
        machine_map: dict[uuid.UUID, RawMachine],
        machine_results: dict[uuid.UUID, MachineSimResult],
        override_dict: dict,
    ) -> Any:
        """
        Handles the case where a downstream machine has more than one upstream
        node — most commonly a weaving machine fed by separate warp and weft
        spinning machines.

        Convention: the Production Manager labels each spinning machine with
          input_attributes["role"] = "warp" or "weft"
        If no role is set, the first upstream node is warp, the second is weft.
        """
        if "weaving" not in process.lower():
            raise NotImplementedError(
                f"Multi-upstream Layer 2 build is only implemented for Weaving. "
                f"Got: {process}/{subprocess}"
            )

        warp_output = warp_machine = None
        weft_output = weft_machine = None

        for up_id in upstream_ids:
            up_machine = machine_map[up_id]
            up_result  = machine_results[up_id]
            role = up_machine.get("input_attributes", {}).get("role", "")
            if role == "weft" or warp_output is not None:
                weft_output  = up_result.layer4_output
                weft_machine = up_machine
            else:
                warp_output  = up_result.layer4_output
                warp_machine = up_machine

        if warp_output is None or weft_output is None:
            raise ValueError(
                "Weaving node has multiple upstream nodes but could not "
                "assign both a warp and a weft source."
            )

        # Build warp InputYarns from warp spinning node
        warp_input = _spinning_output_to_weaving_input(
            warp_output,
            warp_machine["_layer3_instance"],
            {k: v for k, v in override_dict.items() if "warp" in k},
        )

        # Build weft InputYarns from weft spinning node
        weft_input = _spinning_output_to_weaving_input(
            weft_output,
            weft_machine["_layer3_instance"],
            {k: v for k, v in override_dict.items() if "weft" in k},
        )

        # Merge: warp fields from warp_input, weft fields from weft_input
        return InputYarns(
            warp_yarn_count_tex=warp_input.warp_yarn_count_tex,
            warp_yarn_count_Ne=warp_input.warp_yarn_count_Ne,
            warp_yarn_tenacity_cN_tex=warp_input.warp_yarn_tenacity_cN_tex,
            warp_yarn_CVm_pct=warp_input.warp_yarn_CVm_pct,
            warp_yarn_hairiness_H=warp_input.warp_yarn_hairiness_H,
            warp_yarn_twist_t_per_m=warp_input.warp_yarn_twist_t_per_m,
            warp_yarn_type=warp_input.warp_yarn_type,
            weft_yarn_count_tex=weft_input.warp_yarn_count_tex,   # weft machine's "warp" slot
            weft_yarn_count_Ne=weft_input.warp_yarn_count_Ne,
            weft_yarn_tenacity_cN_tex=weft_input.warp_yarn_tenacity_cN_tex,
            weft_yarn_CVm_pct=weft_input.warp_yarn_CVm_pct,
            weft_yarn_hairiness_H=weft_input.warp_yarn_hairiness_H,
            weft_yarn_twist_t_per_m=weft_input.warp_yarn_twist_t_per_m,
            weft_yarn_type=weft_input.warp_yarn_type,
        )


# ─────────────────────────────────────────────────────────────────────────────
# DEMO — runs without a database using plain dicts
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import pprint

    # ── Build a 3-node chain: Rotor Spinning → Plain Weaving → Reactive Dyeing

    m_spinning = {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "name": "Rotor Spinner R-01",
        "process": "Spinning",
        "subprocess": "Rotor Spinning",
        "parameters": {
            # Layer 3 — RotorOperationalParams fields
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
            # Layer 2 — RotorInputMaterial fields (raw material properties)
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

    m_weaving = {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000002"),
        "name": "Plain Loom W-01",
        "process": "Weaving",
        "subprocess": "Plain Weaving",
        "parameters": {
            # Layer 3 — PlainWeavingParams fields
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
            "operating_hours_since_maintenance": 800.0,
        },
        "input_attributes": {},   # fully derived from upstream spinning node
    }

    m_dyeing = {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000003"),
        "name": "Jet Dyeing Machine D-01",
        "process": "Colouring",
        "subprocess": "Reactive Dyeing",
        "parameters": {
            # Layer 3 — ReactiveDyeingParams fields
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
            "operating_hours_since_maintenance": 700.0,
        },
        "input_attributes": {},   # fully derived from upstream weaving node
    }

    machines = [m_spinning, m_weaving, m_dyeing]

    connections = [
        {"source_machine_id": m_spinning["id"], "target_machine_id": m_weaving["id"]},
        {"source_machine_id": m_weaving["id"],  "target_machine_id": m_dyeing["id"]},
    ]

    engine = SimulationEngine()
    result = engine.run_from_dicts(machines, connections)

    print("=" * 65)
    print("FULL PRODUCTION LINE SIMULATION")
    print(f"  Line ID : {result.production_line_id}")
    print(f"  Success : {result.success}")
    print(f"  Order   : {[str(i)[-4:] for i in result.execution_order]}")
    print("=" * 65)

    for mid in result.execution_order:
        if mid not in result.machine_results:
            continue
        mres = result.machine_results[mid]
        print(f"\n> {mres.machine_name}  [{mres.process} / {mres.subprocess}]")
        # Print a representative subset of Layer 4 outputs
        out = mres.layer4_dict
        for key in list(out.keys())[:8]:
            print(f"    {key:45s} = {out[key]}")
        if mres.warnings:
            print(f"    WARNINGS ({len(mres.warnings)}): {mres.warnings[0][:80]}")

    if result.global_warnings:
        print("\nGLOBAL WARNINGS:")
        for w in result.global_warnings:
            print(f"  ! {w}")

    print("\n" + "=" * 65)
    
    # Save the output format as requested by the user
    output_filepath = "simulation_output.json"
    result.save_to_json(output_filepath)
    print(f"\nSaved full simulation state to {output_filepath}")
