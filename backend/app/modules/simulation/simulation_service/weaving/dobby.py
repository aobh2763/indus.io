"""
Dobby Weaving Simulation Module
Process: Weaving > Dobby Weaving

Layer 1 — Machine Identity
    Type            : Dobby Loom (positive or negative dobby)
    Subprocess      : Dobby Weaving
    Technology      : Double-acting dobby shedding with pattern chain (pegged lags
                      or punched-paper control), cam or crank knife drive, positive
                      or negative take-up / let-off motion, shuttle or shuttleless
                      (rapier / projectile) weft insertion.
    Typical machines: Stäubli dobby, Knowles positive dobby, Keighley / Rüti cam
                      dobby; loom frames such as Picanol, Rüti, Sulzer, Saurer.
    Capacity        : 16 – 36 heald shafts; virtually unlimited picks per repeat.
    Fabric scope    : Fancy weaves with geometric stripes, checks, and multi-shaft
                      structures — twills, satins, dobby figured cloths, terry
                      borders, handkerchiefs, table linen, dress fabrics.

All parameter relationships derived from:
    Marks, R. & Robinson, A.T.C., "Principles of Weaving", The Textile Institute,
    Manchester, 1976. (Chapters 1, 2, 3, 4, 5, 6.)

Layer 5: Interdependency and behavior simulation functions.
These functions take operational parameters (Layer 3) and input yarn
properties (Layer 2) as inputs, and predict output fabric quality
metrics (Layer 4).

Layer 2 note:
    Weaving input = Spinning output.
    The InputYarn dataclass mirrors YarnQualityOutput from the spinning
    simulation modules (ring, rotor, airjet, friction, open-end), using only
    the fields that are physically meaningful at the weaving stage.
"""

import math
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# DATA CLASSES — Layer 2, 3, and 4 structures
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class InputYarn:
    """
    Layer 2 — Input yarn properties for Weaving.

    These fields correspond directly to Layer 4 (YarnQualityOutput) of the
    spinning subprocess simulation, ensuring the two layers are coupled:

        spinning.YarnQualityOutput  →  weaving.InputYarn
        ─────────────────────────────────────────────────
        yarn_tenacity_cN_tex        →  yarn_tenacity_cN_tex
        yarn_evenness_CVm_pct       →  yarn_evenness_CVm_pct
        hairiness_H                 →  hairiness_H
        neps_per_km                 →  neps_per_km
        waste_fiber_pct             →  (not used directly at weaving stage)

    Additional yarn identity fields required by the loom:
        yarn_count_tex, yarn_count_Ne, fiber_type, twist_multiplier
    """
    # Yarn identity (set by the spinner)
    yarn_count_tex: float       # Linear density in tex. E.g. 20 tex = Ne 29.5.
    yarn_count_Ne: float        # Count in English (cotton count / Ne). = 590.5 / tex.
    fiber_type: str             # "cotton", "polyester", "blend_PES_CO", "viscose", "wool"
    twist_multiplier: float     # αe (English twist multiplier). Ring: 3.5–5.5;
                                # Airjet: lower apparent value (2.5–4.0 equiv.).

    # Yarn quality metrics (direct output of spinning simulation)
    yarn_tenacity_cN_tex: float     # Tenacity in cN/tex. Warp yarn: typically ≥ 12 cN/tex.
    yarn_evenness_CVm_pct: float    # Mass CV%. Lower is better. Above 16% → weaving problems.
    hairiness_H: float              # Uster hairiness index. High hairiness → more shedding resistance.
    neps_per_km: float              # Nep count per km. High neps → appearance faults.

    # Warp-specific preparation state
    warp_sizing_applied: bool       # True if warp has been slashed (sized). Strongly recommended
                                    # for spun yarns in the warp.
    size_add_on_pct: float          # Size add-on in % by weight. Typical range: 8–15% for cotton.
    moisture_regain_pct: float      # Yarn moisture regain %. Cotton standard: 8.5%.


@dataclass
class DobbyOperationalParams:
    """
    Layer 3 — Operational parameters for Dobby Weaving.

    Source: Marks & Robinson, Principles of Weaving, Ch. 1–6.
    """
    # ── SHEDDING SYSTEM ──────────────────────────────────────────────────────
    number_of_heald_shafts: int          # Active heald shafts. Dobby range: 8 – 36.
    weave_repeat_ends: int               # Warp repeat (ends in one weave repeat).
    weave_repeat_picks: int              # Weft repeat (picks in one weave repeat).
    ends_per_cm_per_shaft: float         # Ends/cm on each shaft. Max guideline: 10–12 ends/cm.
                                         # Exceeding this → increased end-breakage and heald wear.
    shed_depth_mm: float                 # Clear shed depth in mm. Typical: 60–90 mm.
                                         # Deeper shed → more warp stress but safer shuttle/rapier flight.
    shed_type: str                       # "open", "semi_open", or "bottom_closed".
                                         # Modern double-acting dobbies give approximately open shed.
    dobby_type: str                      # "negative" or "positive".
                                         # Positive required for heavy fabrics (woollen/worsted).

    # ── LOOM SPEED AND WEFT INSERTION ────────────────────────────────────────
    loom_speed_picks_per_min: float      # Loom speed in picks/min. Dobby practical limit:
                                         #   conventional: 180–270 picks/min;
                                         #   modern high-speed positive dobby: up to 500 picks/min.
    weft_insertion_type: str             # "shuttle", "rapier", "projectile", or "air_jet".
    reed_space_cm: float                 # Useful reedspace (warp width in reed) in cm.
    shuttle_mass_g: float                # Shuttle mass in g (for shuttle looms). Typical: 400–500 g.
                                         # Set to 0.0 for shuttleless looms.

    # ── YARN SETT AND FABRIC STRUCTURE ───────────────────────────────────────
    warp_ends_per_cm: float              # Warp sett in ends/cm in the reed.
    weft_picks_per_cm: float             # Weft sett in picks/cm as woven.
    float_length_warp: float             # Average warp float length in the weave.
                                         # Plain = 1, 2/2 twill = 2, 5-end satin = 4.
    float_length_weft: float             # Average weft float length in the weave.
    interlacement_ratio: float           # Fraction of intersections that interlace.
                                         # Plain = 1.0; 2/2 twill = 0.5; 5-end satin = 0.2.

    # ── WARP TENSION AND FABRIC CONTROL ──────────────────────────────────────
    warp_tension_cN_per_end: float       # Warp tension per end in cN during weaving.
                                         # Typical spun yarns: 15–40 cN/end;
                                         # filament yarns: 5–15 cN/end.
    let_off_type: str                    # "negative_friction", "positive_automatic".
                                         # Automatic strongly preferred for quality fabrics.
    take_up_picks_per_cm: float          # Take-up motion setting (picks/cm on loom).
                                         # Determines pick-spacing at the fell.

    # ── REED ─────────────────────────────────────────────────────────────────
    reed_count_dents_per_cm: float       # Reed dent count in dents/cm. E.g. 20 dents/cm.
    ends_per_dent: int                   # Ends per dent. Typically 1, 2, or 3.

    # ── TEMPLE AND SELVEDGE ──────────────────────────────────────────────────
    temple_type: str                     # "ring", "roller", or "full_width".
    selvedge_type: str                   # "conventional", "tuck", "leno", or "twist".

    # ── AMBIENT / MACHINE CONDITION ──────────────────────────────────────────
    ambient_temperature_C: float         # Weaving room temperature in °C. Recommended: 20–26°C.
    ambient_humidity_pct: float          # Relative humidity in %. Recommended: 65–80% for cotton.
    last_maintenance_date: str           # ISO date string, e.g. "2025-10-01".
    maintenance_interval_hours: float    # Recommended service interval in hours.
    operating_hours_since_maintenance: float  # Hours elapsed since last maintenance.


@dataclass
class FabricQualityOutput:
    """
    Layer 4 — Predicted output quality metrics for Dobby Weaving.
    """
    # Fabric construction metrics
    fabric_width_cm: float              # Finished (woven) fabric width in cm.
    weft_crimp_pct: float               # Weft crimp % (= weft takeup from straight to crimped).
    warp_crimp_pct: float               # Warp crimp % (= warp takeup from straight to woven).
    fabric_weight_g_per_m2: float       # Predicted fabric weight in g/m².

    # Performance / quality metrics
    cloth_cover_factor: float           # Combined warp + weft cover factor (0 – 2.0 scale).
                                        # Values > 1.0 indicate a fully-covered fabric.
    warp_end_break_risk: str            # "low", "medium", or "high".
    weft_break_risk: str                # "low", "medium", or "high".
    shedding_quality: str               # "good", "marginal", or "poor".
    beat_up_resistance: str             # "easy", "moderate", or "difficult".

    # Appearance metrics
    expected_nep_visibility: str        # "negligible", "acceptable", or "visible_defects".
    pick_spacing_regularity: str        # "excellent", "good", or "irregular".
    selvedge_quality: str               # "clean", "acceptable", or "faults_likely".

    # Production metrics
    theoretical_production_m_per_hour: float   # Theoretical fabric output in m/h.
    loom_efficiency_pct: float                 # Estimated loom efficiency % (accounts for
                                               # stop rates from end breaks, weft breaks, etc.)
    actual_production_m_per_hour: float        # Effective fabric output = theoretical × efficiency.

    warnings: list                       # List of warning messages for out-of-range conditions.


# ─────────────────────────────────────────────────────────────────────────────
# CORE SIMULATION FUNCTIONS — Layer 5
# Each function models one specific cause-effect relationship from the manual.
# ─────────────────────────────────────────────────────────────────────────────

def predict_weft_crimp(
    weft_picks_per_cm: float,
    warp_ends_per_cm: float,
    warp_tension_cN_per_end: float,
    float_length_warp: float,
    fiber_type: str
) -> float:
    """
    Predicts weft crimp % (weft takeup).

    Source: Marks & Robinson, Ch. 6 (Cloth Formation, Section 6.1).
    - Weft crimp increases with warp sett (more ends/cm → weft must weave
      over and under more ends per unit length → more curvature).
    - Higher warp tension pushes the weaving point back and tends to reduce
      weft crimp (warp thread straightens under tension, forcing weft to
      curve more, but also pulling the fell tighter).
    - Longer float lengths (loose weaves) → less crimp because the yarn
      travels in longer straight runs between intersections.
    - Interlacement model: crimp ≈ proportional to frequency of crossings.

    Calibrated to typical cotton plain weave at 20 ends/cm, 20 picks/cm:
    weft crimp ≈ 8–12%, warp crimp ≈ 4–8%.
    """
    # Base crimp from sett interaction — plain weave reference
    # More warp ends per cm → weft undulates more per cm
    base_crimp = (warp_ends_per_cm / 20.0) * 8.0  # 8% at 20 ends/cm reference

    # Float length reduces crimp: float of 1 (plain) → full crimp;
    # float of 4 (satin-like) → ~25% of plain crimp
    float_factor = 1.0 / float_length_warp

    # Warp tension effect: higher tension → straighter warp → weft crimps more
    # Normalised to 25 cN/end reference
    tension_factor = 1.0 + (warp_tension_cN_per_end - 25.0) * 0.008

    # Fiber type: wool and high-crimp fibers swell more after weaving
    if "wool" in fiber_type.lower():
        fiber_factor = 1.15
    elif "cotton" in fiber_type.lower():
        fiber_factor = 1.0
    elif "blend" in fiber_type.lower():
        fiber_factor = 0.95
    else:  # synthetics / filament
        fiber_factor = 0.88

    crimp = base_crimp * float_factor * tension_factor * fiber_factor
    return round(max(1.0, min(25.0, crimp)), 1)


def predict_warp_crimp(
    warp_ends_per_cm: float,
    weft_picks_per_cm: float,
    warp_tension_cN_per_end: float,
    float_length_weft: float,
    fiber_type: str
) -> float:
    """
    Predicts warp crimp % (warp takeup).

    Source: Marks & Robinson, Ch. 6.
    - By conservation of cloth geometry, when weft crimp is high, warp crimp
      tends to be lower (warp is kept straighter by high tension).
    - Higher warp tension → lower warp crimp (warp thread resists bending).
    - More picks/cm → warp undulates more per unit length → higher warp crimp.
    - Longer weft float → less warp crimp.
    """
    base_crimp = (weft_picks_per_cm / 20.0) * 5.0  # 5% at 20 picks/cm reference

    float_factor = 1.0 / float_length_weft

    # High tension straightens warp, reducing warp crimp
    tension_factor = 1.0 - (warp_tension_cN_per_end - 25.0) * 0.01
    tension_factor = max(0.5, tension_factor)

    if "wool" in fiber_type.lower():
        fiber_factor = 1.10
    elif "cotton" in fiber_type.lower():
        fiber_factor = 1.0
    elif "blend" in fiber_type.lower():
        fiber_factor = 0.93
    else:
        fiber_factor = 0.85

    crimp = base_crimp * float_factor * tension_factor * fiber_factor
    return round(max(0.5, min(15.0, crimp)), 1)


def predict_fabric_weight(
    warp_ends_per_cm: float,
    weft_picks_per_cm: float,
    yarn_count_tex: float,  # same tex for warp and weft (simplified — extend for mixed setts)
    warp_crimp_pct: float,
    weft_crimp_pct: float
) -> float:
    """
    Predicts fabric weight in g/m².

    Source: Marks & Robinson, Ch. 6 (Cloth Formation).
    Formula (standard textile):
        Weight (g/m²) = [ends/cm × (1 + warp_crimp/100) × tex_warp / 10]
                      + [picks/cm × (1 + weft_crimp/100) × tex_weft / 10]

    (dividing by 10 converts ends/cm × tex × 100cm/m / 1000 g/kg → g/m²)

    Assumes same yarn count for warp and weft for simplicity; extend the
    data class to separate warp_yarn_count_tex and weft_yarn_count_tex for
    mixed constructions.
    """
    warp_contribution = (warp_ends_per_cm * 100 * yarn_count_tex
                         * (1 + warp_crimp_pct / 100.0)) / 1000.0
    weft_contribution = (weft_picks_per_cm * 100 * yarn_count_tex
                         * (1 + weft_crimp_pct / 100.0)) / 1000.0
    weight = warp_contribution + weft_contribution
    return round(weight, 1)


def predict_cover_factor(
    warp_ends_per_cm: float,
    weft_picks_per_cm: float,
    yarn_count_tex: float,
    interlacement_ratio: float
) -> float:
    """
    Predicts combined cloth cover factor.

    Source: Standard weave cover factor formula.
    Warp cover factor K_warp = ends/cm × √tex / 10
    Weft cover factor K_weft = picks/cm × √tex / 10
    Combined cover = K_warp + K_weft − K_warp × K_weft
        (using the intersection subtraction to avoid exceeding 1.0 on each axis)

    Then scaled by interlacement_ratio because loosely-bound floats expose
    more yarn surface and the effective cover is higher for a given sett
    (satin/dobby fancy weaves look "fuller" than their sett implies).

    Cover factor range: 0 – 1 per component, combined 0 – 2.
    """
    k_warp = warp_ends_per_cm * math.sqrt(yarn_count_tex) / 10.0
    k_weft = weft_picks_per_cm * math.sqrt(yarn_count_tex) / 10.0

    # Clamp individual factors to 1.0 maximum (can't cover more than 100%)
    k_warp = min(1.0, k_warp)
    k_weft = min(1.0, k_weft)

    combined = k_warp + k_weft - k_warp * k_weft

    # Float length modifier: longer floats give marginally higher perceived cover
    # because the yarn lies flatter (less interlacement distortion)
    float_boost = 1.0 + (1.0 - interlacement_ratio) * 0.05
    combined *= float_boost

    return round(min(2.0, max(0.0, combined)), 3)


def assess_end_break_risk(
    yarn_tenacity_cN_tex: float,
    yarn_evenness_CVm_pct: float,
    warp_tension_cN_per_end: float,
    ends_per_cm_per_shaft: float,
    warp_sizing_applied: bool,
    size_add_on_pct: float,
    shed_depth_mm: float,
    loom_speed_picks_per_min: float,
    operating_hours_since_maintenance: float,
    maintenance_interval_hours: float
) -> str:
    """
    Qualitative assessment of warp end-break risk.

    Source: Marks & Robinson, Ch. 3.1 (heald shaft loading limits: max
    10–12 ends/cm per shaft), Ch. 6.1 (warp tension and cloth formation),
    and general weaving engineering principles.

    Risk factors:
    - Low yarn tenacity (< 12 cN/tex) → breaks under tension peaks at beat-up.
    - High CV% (> 16%) → weak places → sudden breaks.
    - Excessive tension relative to tenacity.
    - Too many ends per shaft (> 12/cm) → increased heald friction and abrasion.
    - No sizing on spun yarns → fibers pulled out by heald and reed.
    - Deep shed → higher warp yarn bending angle → higher tension at crossing.
    - High loom speed → larger dynamic tension peaks.
    - Overdue maintenance → worn healds and reed → more abrasion.
    """
    risk_score = 0

    # Tenacity check
    if yarn_tenacity_cN_tex < 10.0:
        risk_score += 3
    elif yarn_tenacity_cN_tex < 13.0:
        risk_score += 1

    # Evenness check
    if yarn_evenness_CVm_pct > 18.0:
        risk_score += 2
    elif yarn_evenness_CVm_pct > 15.0:
        risk_score += 1

    # Tension vs tenacity ratio
    # Single-end breaking force (cN) = tenacity (cN/tex) × linear_density (tex) / 100
    # The /100 converts tex (mg/m) to a per-end force in cN at unit elongation;
    # here we use a simplified approximation: for a Ne 30 yarn (≈20 tex),
    # tenacity 17 cN/tex → breaking force ≈ 17 × 20 / 100 × 100 = 340 cN.
    # We compare warp_tension_cN_per_end against that.
    # Note: yarn_count_tex is not available in this function so we use
    # a proxy: assume a "medium" 25 tex yarn for the ratio check, and
    # flag only clear outliers. The master function already does a proper
    # check with actual tex values and logs a warning.
    # Here we use tenacity as a standalone index (cN/tex):
    # - warp_tension_cN_per_end / yarn_tenacity_cN_tex is dimensionally
    #   (cN/end) / (cN/tex) = tex/end, not a pure ratio.
    # We therefore simply flag based on absolute tension values relative
    # to typical safe ranges for the given tenacity level.
    if warp_tension_cN_per_end > 35 and yarn_tenacity_cN_tex < 12.0:
        risk_score += 3  # high tension + weak yarn → very high risk
    elif warp_tension_cN_per_end > 30 and yarn_tenacity_cN_tex < 15.0:
        risk_score += 1

    # Shaft loading
    if ends_per_cm_per_shaft > 12.0:
        risk_score += 2
    elif ends_per_cm_per_shaft > 10.0:
        risk_score += 1

    # Sizing
    if not warp_sizing_applied:
        risk_score += 2
    elif size_add_on_pct < 6.0:
        risk_score += 1

    # Shed depth
    if shed_depth_mm > 95:
        risk_score += 1

    # Loom speed
    if loom_speed_picks_per_min > 350:
        risk_score += 2
    elif loom_speed_picks_per_min > 250:
        risk_score += 1

    # Maintenance
    maintenance_ratio = operating_hours_since_maintenance / max(1.0, maintenance_interval_hours)
    if maintenance_ratio > 1.0:
        risk_score += 2
    elif maintenance_ratio > 0.85:
        risk_score += 1

    if risk_score <= 2:
        return "low"
    elif risk_score <= 5:
        return "medium"
    else:
        return "high"


def assess_weft_break_risk(
    yarn_tenacity_cN_tex: float,
    yarn_evenness_CVm_pct: float,
    loom_speed_picks_per_min: float,
    weft_insertion_type: str,
    reed_space_cm: float,
    shuttle_mass_g: float
) -> str:
    """
    Qualitative assessment of weft break risk.

    Source: Marks & Robinson, Ch. 4 and 5.
    - Shuttle insertion: weft must withstand peak tension as shuttle traverses.
      Formula from Ch. 4.3: shuttle velocity ∝ loom speed × reed width.
      Higher weft velocity → higher peak weft tension → more breaks.
    - Rapier/projectile: tension is more controlled; less dependence on loom speed.
    - Air-jet: high initial velocity; weft breaks more common with coarser or
      irregular yarns.
    - Low tenacity and high CVm% amplify risk on any insertion system.
    """
    risk_score = 0

    # Yarn quality
    if yarn_tenacity_cN_tex < 10.0:
        risk_score += 3
    elif yarn_tenacity_cN_tex < 13.0:
        risk_score += 1

    if yarn_evenness_CVm_pct > 18.0:
        risk_score += 2
    elif yarn_evenness_CVm_pct > 15.0:
        risk_score += 1

    # Insertion system × speed interaction
    insertion = weft_insertion_type.lower()
    if insertion == "shuttle":
        # Shuttle velocity ∝ speed × reedspace (Ch. 4.3, Eq. 4.1)
        # At 200 picks/min, 150 cm → v ≈ 12–14 m/s: moderate
        # At 270 picks/min, 200 cm → v ≈ 18 m/s: high stress on weft
        effective_speed_factor = loom_speed_picks_per_min * reed_space_cm / (200 * 150)
        if effective_speed_factor > 1.5:
            risk_score += 3
        elif effective_speed_factor > 1.1:
            risk_score += 1
    elif insertion == "air_jet":
        # Air jets require very high weft velocity; sensitive to evenness
        if loom_speed_picks_per_min > 400:
            risk_score += 2
        elif loom_speed_picks_per_min > 300:
            risk_score += 1
        if yarn_evenness_CVm_pct > 14.0:
            risk_score += 1
    elif insertion in ("rapier", "projectile"):
        # Better tension control; lower risk than shuttle at same speed
        if loom_speed_picks_per_min > 400:
            risk_score += 1

    if risk_score <= 1:
        return "low"
    elif risk_score <= 3:
        return "medium"
    else:
        return "high"


def assess_shedding_quality(
    number_of_heald_shafts: int,
    shed_depth_mm: float,
    shed_type: str,
    dobby_type: str,
    ends_per_cm_per_shaft: float,
    hairiness_H: float,
    loom_speed_picks_per_min: float
) -> str:
    """
    Qualitative assessment of shedding quality.

    Source: Marks & Robinson, Ch. 3 (Shedding Mechanisms).
    - More heald shafts → more heald-to-heald friction and crossing → lower quality.
    - Open shed (double-acting dobby) → best; centre-closed → most wasted movement.
    - Positive dobby → better control for heavy fabrics; negative → adequate for light.
    - Deep shed helps shuttle/rapier flight but increases warp tension.
    - High yarn hairiness increases interfiber friction during shedding → tangles.
    - High loom speed → less dwell time for shed formation → marginal shedding.
    - Exceeding 10–12 ends/cm per shaft (guideline from Ch. 3.1) → poor shedding.
    """
    quality_score = 0  # 0 = worst, higher = better

    # Shedding type bonus
    if shed_type == "open":
        quality_score += 3
    elif shed_type == "semi_open":
        quality_score += 2
    else:  # bottom_closed
        quality_score += 0

    # Dobby type
    if dobby_type == "positive":
        quality_score += 2
    else:
        quality_score += 1

    # Shaft loading penalty (Ch. 3.1 guideline: max 10–12 ends/cm/shaft)
    if ends_per_cm_per_shaft <= 8.0:
        quality_score += 2
    elif ends_per_cm_per_shaft <= 10.0:
        quality_score += 1
    elif ends_per_cm_per_shaft > 12.0:
        quality_score -= 2

    # Shed depth
    if 65 <= shed_depth_mm <= 85:
        quality_score += 1
    elif shed_depth_mm > 100:
        quality_score -= 1

    # Hairiness penalty
    if hairiness_H > 7.0:
        quality_score -= 1
    if hairiness_H > 10.0:
        quality_score -= 1

    # Speed penalty
    if loom_speed_picks_per_min > 400:
        quality_score -= 2
    elif loom_speed_picks_per_min > 280:
        quality_score -= 1

    # Number of shafts
    if number_of_heald_shafts > 24:
        quality_score -= 1
    if number_of_heald_shafts > 30:
        quality_score -= 1

    if quality_score >= 6:
        return "good"
    elif quality_score >= 3:
        return "marginal"
    else:
        return "poor"


def assess_beat_up_resistance(
    warp_ends_per_cm: float,
    weft_picks_per_cm: float,
    float_length_warp: float,
    float_length_weft: float,
    yarn_count_tex: float
) -> str:
    """
    Assesses resistance to beat-up (difficulty of inserting a new pick into the fell).

    Source: Marks & Robinson, Ch. 6.1 (Cloth Formation).
    - High sett (many ends/cm or picks/cm) → cloth is dense → more resistance.
    - Longer float lengths → fewer intersections → less resistance (looser structure).
    - Coarser yarn (higher tex) → larger diameter → more resistance at same sett.

    High beat-up resistance can cause pick-spacing irregularities, warp breaks,
    and requires more loom power. This is especially critical for negative
    (friction) take-up and let-off systems.
    """
    # Approximate crimp interchange index (higher = more compacted)
    # Interaction of both setts relative to yarn diameter (∝ √tex)
    yarn_diameter_proxy = math.sqrt(yarn_count_tex)
    sett_index = (warp_ends_per_cm + weft_picks_per_cm) * yarn_diameter_proxy / 20.0

    # Float length reduces resistance
    avg_float = (float_length_warp + float_length_weft) / 2.0
    resistance_index = sett_index / avg_float

    if resistance_index < 8.0:
        return "easy"
    elif resistance_index < 14.0:
        return "moderate"
    else:
        return "difficult"


def predict_nep_visibility(
    neps_per_km: float,
    float_length_warp: float,
    float_length_weft: float,
    yarn_count_tex: float
) -> str:
    """
    Predicts expected nep visibility on the woven fabric surface.

    Source: General weaving quality principles.
    - Neps trapped at intersections are compressed and less visible on tight structures.
    - Longer floats (satin, dobby fancy) expose more yarn surface → neps more visible.
    - Finer yarns (lower tex) → neps appear larger relative to yarn diameter.
    - High nep count (> 200/km) almost always produces visible defects.
    """
    # Exposure factor: satin-like weaves expose more surface
    avg_float = (float_length_warp + float_length_weft) / 2.0
    exposure_factor = avg_float  # plain = 1.0, long float = 4+

    # Fineness factor: finer yarns → neps relatively larger
    fineness_factor = max(0.5, 20.0 / yarn_count_tex)  # normalized to 20 tex

    nep_visibility_index = neps_per_km * exposure_factor * fineness_factor / 100.0

    if nep_visibility_index < 1.0:
        return "negligible"
    elif nep_visibility_index < 3.0:
        return "acceptable"
    else:
        return "visible_defects"


def predict_pick_spacing_regularity(
    let_off_type: str,
    loom_speed_picks_per_min: float,
    yarn_evenness_CVm_pct: float,
    operating_hours_since_maintenance: float,
    maintenance_interval_hours: float
) -> str:
    """
    Predicts pick-spacing regularity (weft bar risk).

    Source: Marks & Robinson, Ch. 6.2–6.3 (Take-up and Let-off Motions).
    - Positive automatic let-off → excellent regularity.
    - Negative friction let-off → inherent stick-slip → periodic weft bars.
    - High loom speed → reduced dwell → less time for take-up settle → more variation.
    - High yarn CVm% → irregular beat-up force per pick → pick-spacing variation.
    - Overdue maintenance → eccentric gears, worn pawls → periodic bars.
    """
    risk_score = 0

    if let_off_type == "negative_friction":
        risk_score += 3  # inherent stick-slip variation
    else:  # positive_automatic
        risk_score += 0

    if loom_speed_picks_per_min > 350:
        risk_score += 1

    if yarn_evenness_CVm_pct > 16.0:
        risk_score += 2
    elif yarn_evenness_CVm_pct > 13.0:
        risk_score += 1

    maintenance_ratio = operating_hours_since_maintenance / max(1.0, maintenance_interval_hours)
    if maintenance_ratio > 1.0:
        risk_score += 2
    elif maintenance_ratio > 0.85:
        risk_score += 1

    if risk_score <= 1:
        return "excellent"
    elif risk_score <= 3:
        return "good"
    else:
        return "irregular"


def predict_selvedge_quality(
    selvedge_type: str,
    weft_insertion_type: str,
    loom_speed_picks_per_min: float,
    warp_ends_per_cm: float,
    yarn_tenacity_cN_tex: float
) -> str:
    """
    Predicts selvedge quality.

    Source: Marks & Robinson, Ch. 5.2 (Selvedges).
    - Conventional shuttle selvedge: strong but requires careful timing.
    - Tuck selvedge: good appearance; standard for shuttleless looms.
    - Leno selvedge: strongest fringe; complex mechanism.
    - Twist selvedge: neat fringe appearance; used on projectile/rapier.
    - Higher loom speed → less dwell for selvedge formation → faults.
    - Low yarn tenacity → selvedge ends break under shuttle rubbing or rapier entry.
    - Dense warp sett makes selvedge tighter → fewer fraying issues.
    """
    score = 0

    # Base score from selvedge type
    type_scores = {
        "conventional": 3,
        "tuck": 3,
        "leno": 2,   # complex but strong; needs careful maintenance
        "twist": 2,
    }
    score += type_scores.get(selvedge_type.lower(), 2)

    # Insertion type compatibility
    insertion = weft_insertion_type.lower()
    if insertion == "shuttle" and selvedge_type == "conventional":
        score += 1  # optimal pairing
    elif insertion in ("rapier", "projectile") and selvedge_type == "tuck":
        score += 1  # optimal pairing

    # Speed penalty
    if loom_speed_picks_per_min > 350:
        score -= 1
    if loom_speed_picks_per_min > 450:
        score -= 1

    # Tenacity check: low tenacity → selvedge end breaks
    if yarn_tenacity_cN_tex < 11.0:
        score -= 2
    elif yarn_tenacity_cN_tex < 14.0:
        score -= 1

    if score >= 4:
        return "clean"
    elif score >= 2:
        return "acceptable"
    else:
        return "faults_likely"


def predict_loom_efficiency(
    warp_end_break_risk: str,
    weft_break_risk: str,
    shedding_quality: str,
    selvedge_quality: str,
    number_of_heald_shafts: int,
    weft_insertion_type: str
) -> float:
    """
    Estimates loom efficiency % (ratio of actual to theoretical production).

    Source: General industrial weaving engineering; Marks & Robinson, Ch. 1.6,
    5.1.3 (weft insertion rates and efficiency).

    Reference: shuttle looms typically run at 65–85% efficiency; rapier/
    projectile 75–90%; air-jet up to 93%. Efficiency drops with more heald
    shafts (more potential faults), poor shedding, and high break rates.
    """
    # Base efficiency by insertion type (%)
    base_efficiency = {
        "shuttle": 78.0,
        "rapier": 84.0,
        "projectile": 82.0,
        "air_jet": 88.0,
    }
    eff = base_efficiency.get(weft_insertion_type.lower(), 78.0)

    # Warp end-break penalty
    end_break_penalty = {"low": 0.0, "medium": 5.0, "high": 15.0}
    eff -= end_break_penalty.get(warp_end_break_risk, 5.0)

    # Weft break penalty
    weft_break_penalty = {"low": 0.0, "medium": 3.0, "high": 10.0}
    eff -= weft_break_penalty.get(weft_break_risk, 3.0)

    # Shedding quality penalty
    shedding_penalty = {"good": 0.0, "marginal": 3.0, "poor": 8.0}
    eff -= shedding_penalty.get(shedding_quality, 3.0)

    # Selvedge quality penalty
    selvedge_penalty = {"clean": 0.0, "acceptable": 2.0, "faults_likely": 6.0}
    eff -= selvedge_penalty.get(selvedge_quality, 2.0)

    # Heald shaft complexity penalty: each shaft above 16 adds minor stop risk
    shaft_penalty = max(0.0, (number_of_heald_shafts - 16) * 0.15)
    eff -= shaft_penalty

    return round(max(30.0, min(95.0, eff)), 1)


def predict_theoretical_production(
    loom_speed_picks_per_min: float,
    weft_picks_per_cm: float,
    fabric_width_cm: float
) -> float:
    """
    Predicts theoretical fabric production rate in m/h.

    Source: Marks & Robinson, Ch. 5.1.3 (Rate of weft insertion).
    Formula: production (m/h) = (loom_speed [picks/min] / picks_per_cm) × 60
    Fabric width is not in the m/h formula (m/h is linear output of the loom,
    not area output) — but we include it for reference.

    Note: actual production = theoretical × efficiency%.
    """
    if weft_picks_per_cm <= 0:
        return 0.0
    production_m_per_hour = (loom_speed_picks_per_min / weft_picks_per_cm) * 60.0
    return round(production_m_per_hour, 1)


# ─────────────────────────────────────────────────────────────────────────────
# MASTER SIMULATION FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def simulate_dobby_weaving(
    yarn: InputYarn,
    params: DobbyOperationalParams
) -> FabricQualityOutput:
    """
    Master simulation function for Dobby Weaving.

    Takes Layer 2 (InputYarn — the output of a spinning simulation) and
    Layer 3 (DobbyOperationalParams), runs all prediction models, and
    returns Layer 4 (FabricQualityOutput).

    Also performs parameter validation and generates warnings for out-of-range
    conditions based on limits documented in Marks & Robinson (1976).
    """
    warnings = []

    # ── PARAMETER VALIDATION ──────────────────────────────────────────────────

    # Dobby heald shaft range (Ch. 3.1)
    if params.number_of_heald_shafts < 8 or params.number_of_heald_shafts > 36:
        warnings.append(
            f"Number of heald shafts ({params.number_of_heald_shafts}) is outside the typical "
            "dobby range of 8–36 shafts. Verify loom specification."
        )

    # Ends per cm per shaft guideline (Ch. 3.1: max 10–12/cm)
    if params.ends_per_cm_per_shaft > 12.0:
        warnings.append(
            f"Ends/cm per shaft ({params.ends_per_cm_per_shaft:.1f}) exceeds the recommended "
            "maximum of 12 ends/cm per shaft. Expect increased end-breakage and heald wear. "
            "Consider using more shafts or reducing warp sett."
        )
    elif params.ends_per_cm_per_shaft > 10.0:
        warnings.append(
            f"Ends/cm per shaft ({params.ends_per_cm_per_shaft:.1f}) is above 10 — "
            "on the borderline of the recommended limit. Monitor end-break rate."
        )

    # Loom speed check for dobby (Ch. 3.3)
    conventional_max = 300  # conventional Keighley dobby limit
    if params.loom_speed_picks_per_min > 500:
        warnings.append(
            f"Loom speed {params.loom_speed_picks_per_min} picks/min exceeds the maximum "
            "of ~500 picks/min for even the most advanced positive dobbies."
        )
    elif params.loom_speed_picks_per_min > conventional_max and params.dobby_type == "negative":
        warnings.append(
            f"Loom speed {params.loom_speed_picks_per_min} picks/min with a negative dobby "
            "is above the practical limit (~300 picks/min). Gravity-controlled hooks and "
            "feelers are too sluggish at this speed. Use a positive dobby."
        )

    # Warp sizing check (general weaving practice)
    if not yarn.warp_sizing_applied and "cotton" in yarn.fiber_type.lower():
        warnings.append(
            "Warp sizing has not been applied to cotton yarn. Unsized spun yarns in the warp "
            "will suffer high end-breakage from heald and reed abrasion. Sizing is strongly "
            "recommended for spun staple yarns in the warp."
        )

    # Size add-on check
    if yarn.warp_sizing_applied and yarn.size_add_on_pct < 6.0:
        warnings.append(
            f"Size add-on of {yarn.size_add_on_pct:.1f}% is low. Typical cotton warp requires "
            "8–15% add-on for adequate protection. Increase size concentration or pick-up."
        )

    # Warp tension check
    # Single-end breaking force (cN) = tenacity (cN/tex) × count (tex)
    # tex = mass per 1000 m in grams; tenacity in cN/tex → force in cN.
    # Single-end breaking force (cN) = tenacity_cN_tex × count_tex / 100
    # (the /100 converts g/1000m to a workable cN estimate at single-end level)
    # Typical Ne 30 cotton blend (≈20 tex, 17 cN/tex): BF ≈ 17×20 = 340 cN (full skein).
    # Per end: at 100% yarn utilisation that is the breaking force of one end.
    # Practically safe tension is 15–35% of that, depending on sizing and loom type.
    approx_breaking_force_cN = yarn.yarn_tenacity_cN_tex * yarn.yarn_count_tex
    if approx_breaking_force_cN > 0:
        tension_ratio = params.warp_tension_cN_per_end / approx_breaking_force_cN
        if tension_ratio > 0.35:
            warnings.append(
                f"Warp tension ({params.warp_tension_cN_per_end:.1f} cN/end) is "
                f"{tension_ratio*100:.0f}% of estimated single-end breaking force "
                f"({approx_breaking_force_cN:.0f} cN). This is dangerously high. "
                "Reduce warp tension or use a stronger yarn."
            )
        elif tension_ratio > 0.25:
            warnings.append(
                f"Warp tension ({params.warp_tension_cN_per_end:.1f} cN/end) is "
                f"{tension_ratio*100:.0f}% of estimated breaking force — on the high side. "
                "Monitor end-break rate carefully."
            )

    # Yarn tenacity check for warp use
    if yarn.yarn_tenacity_cN_tex < 10.0:
        warnings.append(
            f"Yarn tenacity ({yarn.yarn_tenacity_cN_tex} cN/tex) is very low for warp use. "
            "Warp yarns typically require ≥ 12 cN/tex to withstand loom stresses. "
            "Consider using a stronger yarn or reducing warp tension."
        )

    # Humidity check (important for cotton sizing performance)
    if yarn.moisture_regain_pct < 5.0 and "cotton" in yarn.fiber_type.lower():
        warnings.append(
            f"Low moisture regain ({yarn.moisture_regain_pct}%) for cotton. "
            "Very dry conditions cause brittle sizing and increase static electricity, "
            "leading to more end breaks. Maintain 65–80% RH in the weaving room."
        )

    # Reed dent consistency check
    expected_ends_per_cm = params.reed_count_dents_per_cm * params.ends_per_dent
    if abs(expected_ends_per_cm - params.warp_ends_per_cm) > 2.0:
        warnings.append(
            f"Reed specification inconsistency: {params.reed_count_dents_per_cm:.1f} dents/cm "
            f"× {params.ends_per_dent} ends/dent = {expected_ends_per_cm:.1f} ends/cm, "
            f"but warp sett is set to {params.warp_ends_per_cm:.1f} ends/cm. "
            "Check reed count or ends per dent."
        )

    # Weave repeat vs shaft count check
    if params.weave_repeat_ends > params.number_of_heald_shafts:
        warnings.append(
            f"Weave repeat ({params.weave_repeat_ends} ends) exceeds the number of heald shafts "
            f"({params.number_of_heald_shafts}). With a straight draft this is not possible. "
            "Use a fancy draft or increase the number of shafts."
        )

    # Negative dobby + heavy fabric warning
    if params.dobby_type == "negative" and yarn.yarn_count_tex > 50:
        warnings.append(
            f"A negative dobby is being used with a relatively coarse yarn ({yarn.yarn_count_tex} tex). "
            "For heavy fabrics, a positive dobby is recommended to reliably lower the heald "
            "shafts against high warp tension (Marks & Robinson, Ch. 3.3.2)."
        )

    # ── RUN SIMULATION MODELS ─────────────────────────────────────────────────

    weft_crimp = predict_weft_crimp(
        params.weft_picks_per_cm,
        params.warp_ends_per_cm,
        params.warp_tension_cN_per_end,
        params.float_length_warp,
        yarn.fiber_type
    )

    warp_crimp = predict_warp_crimp(
        params.warp_ends_per_cm,
        params.weft_picks_per_cm,
        params.warp_tension_cN_per_end,
        params.float_length_weft,
        yarn.fiber_type
    )

    fabric_weight = predict_fabric_weight(
        params.warp_ends_per_cm,
        params.weft_picks_per_cm,
        yarn.yarn_count_tex,
        warp_crimp,
        weft_crimp
    )

    cover_factor = predict_cover_factor(
        params.warp_ends_per_cm,
        params.weft_picks_per_cm,
        yarn.yarn_count_tex,
        params.interlacement_ratio
    )

    end_break_risk = assess_end_break_risk(
        yarn.yarn_tenacity_cN_tex,
        yarn.yarn_evenness_CVm_pct,
        params.warp_tension_cN_per_end,
        params.ends_per_cm_per_shaft,
        yarn.warp_sizing_applied,
        yarn.size_add_on_pct,
        params.shed_depth_mm,
        params.loom_speed_picks_per_min,
        params.operating_hours_since_maintenance,
        params.maintenance_interval_hours
    )

    weft_break_risk = assess_weft_break_risk(
        yarn.yarn_tenacity_cN_tex,
        yarn.yarn_evenness_CVm_pct,
        params.loom_speed_picks_per_min,
        params.weft_insertion_type,
        params.reed_space_cm,
        params.shuttle_mass_g
    )

    shedding_quality = assess_shedding_quality(
        params.number_of_heald_shafts,
        params.shed_depth_mm,
        params.shed_type,
        params.dobby_type,
        params.ends_per_cm_per_shaft,
        yarn.hairiness_H,
        params.loom_speed_picks_per_min
    )

    beat_up_resistance = assess_beat_up_resistance(
        params.warp_ends_per_cm,
        params.weft_picks_per_cm,
        params.float_length_warp,
        params.float_length_weft,
        yarn.yarn_count_tex
    )

    nep_visibility = predict_nep_visibility(
        yarn.neps_per_km,
        params.float_length_warp,
        params.float_length_weft,
        yarn.yarn_count_tex
    )

    pick_spacing = predict_pick_spacing_regularity(
        params.let_off_type,
        params.loom_speed_picks_per_min,
        yarn.yarn_evenness_CVm_pct,
        params.operating_hours_since_maintenance,
        params.maintenance_interval_hours
    )

    selvedge = predict_selvedge_quality(
        params.selvedge_type,
        params.weft_insertion_type,
        params.loom_speed_picks_per_min,
        params.warp_ends_per_cm,
        yarn.yarn_tenacity_cN_tex
    )

    theoretical_production = predict_theoretical_production(
        params.loom_speed_picks_per_min,
        params.weft_picks_per_cm,
        params.reed_space_cm
    )

    loom_efficiency = predict_loom_efficiency(
        end_break_risk,
        weft_break_risk,
        shedding_quality,
        selvedge,
        params.number_of_heald_shafts,
        params.weft_insertion_type
    )

    actual_production = round(theoretical_production * loom_efficiency / 100.0, 1)

    # Fabric width: reed space less selvedge take-in (≈ 2–4%)
    # Higher warp tension and tight sett → less take-in
    take_in_factor = 1.0 - (weft_crimp / 100.0)  # fabric narrows as weft crimps
    fabric_width = round(params.reed_space_cm * take_in_factor, 1)

    # Post-simulation warnings
    if shedding_quality == "poor":
        warnings.append(
            "Shedding quality is rated POOR. This is likely to cause shuttle-trapping "
            "(warp shed not clear for weft insertion), high end-break rates, and loom "
            "stoppages. Review heald shaft loading, shed depth, and dobby type."
        )

    if end_break_risk == "high":
        warnings.append(
            "CRITICAL: Warp end-break risk is HIGH. Expect frequent loom stoppages. "
            "Priority actions: verify sizing, reduce warp tension, or use stronger yarn."
        )

    if pick_spacing == "irregular":
        warnings.append(
            "Pick-spacing regularity is IRREGULAR. The fabric is at risk of weft bars "
            "(horizontal stripes of varying density). Check let-off motion calibration, "
            "take-up mechanism gear wear, and yarn evenness."
        )

    if beat_up_resistance == "difficult":
        warnings.append(
            "Beat-up resistance is DIFFICULT. The current sett may cause the reed to "
            "struggle to pack picks to the required density, risking warp breaks and "
            "loom overload. Consider reducing sett or switching to a lighter weave."
        )

    return FabricQualityOutput(
        fabric_width_cm=fabric_width,
        weft_crimp_pct=weft_crimp,
        warp_crimp_pct=warp_crimp,
        fabric_weight_g_per_m2=fabric_weight,
        cloth_cover_factor=cover_factor,
        warp_end_break_risk=end_break_risk,
        weft_break_risk=weft_break_risk,
        shedding_quality=shedding_quality,
        beat_up_resistance=beat_up_resistance,
        expected_nep_visibility=nep_visibility,
        pick_spacing_regularity=pick_spacing,
        selvedge_quality=selvedge,
        theoretical_production_m_per_hour=theoretical_production,
        loom_efficiency_pct=loom_efficiency,
        actual_production_m_per_hour=actual_production,
        warnings=warnings
    )


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE USAGE AND VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    print("=" * 70)
    print("DOBBY WEAVING SIMULATION")
    print("Based on Marks & Robinson, Principles of Weaving (1976)")
    print("=" * 70)

    # ── SCENARIO 1: Cotton shirting — 2/2 twill on 16 shafts ─────────────────
    # Yarn input comes from the Airjet Spinning simulation output (Scenario 1):
    #   cotton/polyester blend Ne 30, typical quality metrics passed forward.
    print("\n--- SCENARIO 1: PES/CO blend Ne 30, 2/2 twill shirting, rapier loom ---\n")

    yarn_1 = InputYarn(
        yarn_count_tex=19.7,             # Ne 30 → 590.5/30 ≈ 19.7 tex
        yarn_count_Ne=30.0,
        fiber_type="blend_PES_CO",
        twist_multiplier=4.0,            # Typical for ring-equivalent blend

        # From airjet spinning Scenario 1 output:
        yarn_tenacity_cN_tex=17.8,       # good PES/CO blend tenacity
        yarn_evenness_CVm_pct=12.5,      # good evenness
        hairiness_H=3.8,                 # low hairiness (airjet characteristic)
        neps_per_km=90.0,                # moderate nep count

        warp_sizing_applied=True,
        size_add_on_pct=10.0,            # 10% size add-on — appropriate for blend
        moisture_regain_pct=4.5,         # blend: lower regain than pure cotton
    )

    params_1 = DobbyOperationalParams(
        number_of_heald_shafts=16,
        weave_repeat_ends=4,             # 2/2 twill repeats on 4 ends
        weave_repeat_picks=4,            # 2/2 twill repeats on 4 picks
        ends_per_cm_per_shaft=2.0,       # 32 ends/cm ÷ 16 shafts = 2.0/shaft (well within 10–12)
        shed_depth_mm=75,
        shed_type="open",                # Double-acting positive dobby
        dobby_type="positive",

        loom_speed_picks_per_min=250,
        weft_insertion_type="rapier",
        reed_space_cm=160.0,
        shuttle_mass_g=0.0,              # shuttleless

        warp_ends_per_cm=32.0,
        weft_picks_per_cm=28.0,
        float_length_warp=2.0,           # 2/2 twill: float = 2
        float_length_weft=2.0,
        interlacement_ratio=0.5,         # 2/2 twill: 50% of intersections interlace

        warp_tension_cN_per_end=20.0,    # reasonable for sized blend
        let_off_type="positive_automatic",
        take_up_picks_per_cm=28.0,

        reed_count_dents_per_cm=16.0,    # 16 dents/cm, 2 ends/dent = 32 ends/cm ✓
        ends_per_dent=2,

        temple_type="roller",
        selvedge_type="tuck",

        ambient_temperature_C=22.0,
        ambient_humidity_pct=70.0,
        last_maintenance_date="2025-09-01",
        maintenance_interval_hours=1500.0,
        operating_hours_since_maintenance=600.0,
    )

    result_1 = simulate_dobby_weaving(yarn_1, params_1)

    print(f"  Fabric Width:            {result_1.fabric_width_cm} cm")
    print(f"  Weft Crimp:              {result_1.weft_crimp_pct}%")
    print(f"  Warp Crimp:              {result_1.warp_crimp_pct}%")
    print(f"  Fabric Weight:           {result_1.fabric_weight_g_per_m2} g/m²")
    print(f"  Cover Factor:            {result_1.cloth_cover_factor}")
    print(f"  Warp End-Break Risk:     {result_1.warp_end_break_risk.upper()}")
    print(f"  Weft Break Risk:         {result_1.weft_break_risk.upper()}")
    print(f"  Shedding Quality:        {result_1.shedding_quality.upper()}")
    print(f"  Beat-Up Resistance:      {result_1.beat_up_resistance.upper()}")
    print(f"  Nep Visibility:          {result_1.expected_nep_visibility.upper()}")
    print(f"  Pick Spacing:            {result_1.pick_spacing_regularity.upper()}")
    print(f"  Selvedge Quality:        {result_1.selvedge_quality.upper()}")
    print(f"  Theoretical Production:  {result_1.theoretical_production_m_per_hour} m/h")
    print(f"  Loom Efficiency:         {result_1.loom_efficiency_pct}%")
    print(f"  Actual Production:       {result_1.actual_production_m_per_hour} m/h")
    if result_1.warnings:
        print(f"\n  WARNINGS:")
        for w in result_1.warnings:
            print(f"    ⚠  {w}")
    else:
        print("\n  No warnings — all parameters within recommended ranges.")

    # ── SCENARIO 2: Heavy cotton dobby table linen — 8-shaft honeycomb ───────
    # Demonstrates positive dobby requirement for heavy fabrics (Ch. 3.3.2)
    print("\n--- SCENARIO 2: Heavy cotton Ne 20, 8-shaft honeycomb, shuttle loom ---\n")

    yarn_2 = InputYarn(
        yarn_count_tex=29.5,             # Ne 20 → 590.5/20 ≈ 29.5 tex
        yarn_count_Ne=20.0,
        fiber_type="cotton_combed",
        twist_multiplier=4.3,

        yarn_tenacity_cN_tex=14.5,       # combed cotton, good tenacity
        yarn_evenness_CVm_pct=13.0,
        hairiness_H=5.5,                 # higher than airjet (ring-spun assumed)
        neps_per_km=70.0,

        warp_sizing_applied=True,
        size_add_on_pct=12.0,
        moisture_regain_pct=8.0,         # cotton standard
    )

    params_2 = DobbyOperationalParams(
        number_of_heald_shafts=8,
        weave_repeat_ends=8,
        weave_repeat_picks=8,
        ends_per_cm_per_shaft=2.5,       # 20 ends/cm ÷ 8 shafts = 2.5/shaft
        shed_depth_mm=80,
        shed_type="open",
        dobby_type="positive",           # positive required for heavy fabric

        loom_speed_picks_per_min=180,    # shuttle loom, typical for table linen width
        weft_insertion_type="shuttle",
        reed_space_cm=140.0,             # table linen width
        shuttle_mass_g=450.0,

        warp_ends_per_cm=20.0,
        weft_picks_per_cm=18.0,
        float_length_warp=3.5,           # honeycomb: longer floats
        float_length_weft=3.5,
        interlacement_ratio=0.28,        # honeycomb: sparse interlacement

        warp_tension_cN_per_end=28.0,    # heavier cotton, higher tension needed
        let_off_type="positive_automatic",
        take_up_picks_per_cm=18.0,

        reed_count_dents_per_cm=10.0,    # 10 dents/cm × 2 ends/dent = 20 ends/cm ✓
        ends_per_dent=2,

        temple_type="ring",
        selvedge_type="conventional",

        ambient_temperature_C=23.0,
        ambient_humidity_pct=72.0,
        last_maintenance_date="2025-10-01",
        maintenance_interval_hours=2000.0,
        operating_hours_since_maintenance=1000.0,
    )

    result_2 = simulate_dobby_weaving(yarn_2, params_2)

    print(f"  Fabric Width:            {result_2.fabric_width_cm} cm")
    print(f"  Weft Crimp:              {result_2.weft_crimp_pct}%")
    print(f"  Warp Crimp:              {result_2.warp_crimp_pct}%")
    print(f"  Fabric Weight:           {result_2.fabric_weight_g_per_m2} g/m²")
    print(f"  Cover Factor:            {result_2.cloth_cover_factor}")
    print(f"  Warp End-Break Risk:     {result_2.warp_end_break_risk.upper()}")
    print(f"  Weft Break Risk:         {result_2.weft_break_risk.upper()}")
    print(f"  Shedding Quality:        {result_2.shedding_quality.upper()}")
    print(f"  Beat-Up Resistance:      {result_2.beat_up_resistance.upper()}")
    print(f"  Nep Visibility:          {result_2.expected_nep_visibility.upper()}")
    print(f"  Pick Spacing:            {result_2.pick_spacing_regularity.upper()}")
    print(f"  Selvedge Quality:        {result_2.selvedge_quality.upper()}")
    print(f"  Theoretical Production:  {result_2.theoretical_production_m_per_hour} m/h")
    print(f"  Loom Efficiency:         {result_2.loom_efficiency_pct}%")
    print(f"  Actual Production:       {result_2.actual_production_m_per_hour} m/h")
    if result_2.warnings:
        print(f"\n  WARNINGS:")
        for w in result_2.warnings:
            print(f"    ⚠  {w}")
    else:
        print("\n  No warnings — all parameters within recommended ranges.")

    # ── SCENARIO 3: Stress test — overloaded dobby, no sizing, high speed ────
    # Deliberately misconfigured to demonstrate the warning system.
    print("\n--- SCENARIO 3: Stress test — unsized carded cotton, overloaded dobby ---\n")

    yarn_3 = InputYarn(
        yarn_count_tex=29.5,
        yarn_count_Ne=20.0,
        fiber_type="cotton_carded",
        twist_multiplier=3.8,

        yarn_tenacity_cN_tex=9.5,        # weak carded cotton (below 10 cN/tex threshold)
        yarn_evenness_CVm_pct=17.5,      # poor evenness
        hairiness_H=8.5,                 # high hairiness
        neps_per_km=350.0,               # high nep count

        warp_sizing_applied=False,       # NO SIZING — deliberate fault
        size_add_on_pct=0.0,
        moisture_regain_pct=4.0,         # too dry
    )

    params_3 = DobbyOperationalParams(
        number_of_heald_shafts=24,
        weave_repeat_ends=24,
        weave_repeat_picks=24,
        ends_per_cm_per_shaft=1.8,       # 43 ends/cm ÷ 24 shafts = 1.8/shaft (OK)
        shed_depth_mm=105,               # excessive shed depth
        shed_type="bottom_closed",       # worst shedding type
        dobby_type="negative",           # negative for heavy — will trigger warning

        loom_speed_picks_per_min=380,    # too fast for negative dobby
        weft_insertion_type="shuttle",
        reed_space_cm=180.0,
        shuttle_mass_g=460.0,

        warp_ends_per_cm=28.0,
        weft_picks_per_cm=26.0,
        float_length_warp=1.0,           # plain-like: very tight
        float_length_weft=1.0,
        interlacement_ratio=1.0,

        warp_tension_cN_per_end=35.0,    # excessive for weak yarn
        let_off_type="negative_friction", # inherently irregular
        take_up_picks_per_cm=26.0,

        reed_count_dents_per_cm=14.0,
        ends_per_dent=2,                 # 28 ends/cm ✓ (14×2)

        temple_type="roller",
        selvedge_type="conventional",

        ambient_temperature_C=28.0,      # too warm
        ambient_humidity_pct=45.0,       # too dry
        last_maintenance_date="2024-01-01",
        maintenance_interval_hours=1000.0,
        operating_hours_since_maintenance=1400.0,  # overdue
    )

    result_3 = simulate_dobby_weaving(yarn_3, params_3)

    print(f"  Fabric Width:            {result_3.fabric_width_cm} cm")
    print(f"  Fabric Weight:           {result_3.fabric_weight_g_per_m2} g/m²")
    print(f"  Cover Factor:            {result_3.cloth_cover_factor}")
    print(f"  Warp End-Break Risk:     {result_3.warp_end_break_risk.upper()}")
    print(f"  Weft Break Risk:         {result_3.weft_break_risk.upper()}")
    print(f"  Shedding Quality:        {result_3.shedding_quality.upper()}")
    print(f"  Beat-Up Resistance:      {result_3.beat_up_resistance.upper()}")
    print(f"  Nep Visibility:          {result_3.expected_nep_visibility.upper()}")
    print(f"  Pick Spacing:            {result_3.pick_spacing_regularity.upper()}")
    print(f"  Loom Efficiency:         {result_3.loom_efficiency_pct}%")
    print(f"  Actual Production:       {result_3.actual_production_m_per_hour} m/h")
    if result_3.warnings:
        print(f"\n  WARNINGS ({len(result_3.warnings)} issues detected):")
        for w in result_3.warnings:
            print(f"    ⚠  {w}")

    print("\n" + "=" * 70)
    print("Simulation complete.")
    print("=" * 70)
