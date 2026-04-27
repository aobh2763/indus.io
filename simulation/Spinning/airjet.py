"""
Airjet Spinning Simulation Module
Process: Spinning > Airjet Spinning (Rieter J 10 / Murata MVS)

All parameter relationships derived from:
Rieter Manual of Spinning, Volume 6 - Alternative Spinning Systems
Dr. Herbert Stalder, Rieter Machine Works Ltd., 2016

Layer 5: Interdependency and behavior simulation functions.
These functions take operational parameters (Layer 3) and input
material properties (Layer 2) as inputs, and predict output
quality metrics (Layer 4).
"""

import math
from dataclasses import dataclass
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# DATA CLASSES — represent Layer 2, 3, and 4 structures
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class InputMaterial:
    """
    Layer 2 — Input material properties for Spinning.
    Feedstock is always draw frame sliver (3 passages recommended).
    """
    fiber_type: str              # "cotton", "polyester", "blend_PES_CO", "viscose", "MMF"
    fiber_length_mm: float       # Mean fiber length in mm. Critical for draft zone settings.
    fiber_fineness_dtex: float   # Fiber fineness in dtex. Finer fibers improve most quality metrics.
    short_fiber_content_pct: float  # % of fibers below 12mm. Higher = more waste and lower strength.
    fiber_tensile_strength_cN_tex: float  # Fiber tenacity in cN/tex.
    sliver_count_ktex: float     # Input sliver linear density in ktex. Range: 2.0 - 4.5 ktex.
    moisture_content_pct: float  # Fiber moisture %. Affects static and drafting behavior.
    trash_content_pct: float     # Impurity level. Acts as a disturbing factor in nozzle zone.


@dataclass
class AirjetOperationalParams:
    """
    Layer 3 — Operational parameters specific to Airjet Spinning subprocess.
    Based on Rieter J 10 and Murata MVS specifications from the manual.
    """
    # DRAFTING ZONE (4-cylinder drafting system)
    total_draft_ratio: float         # Overall draft. Range: 43 - 200 (mechanical max 317 for J 10).
    pre_draft_ratio: float           # Pre-draft zone ratio. Range: 1.57 - 2.10.
    break_draft_ratio: float         # Break draft zone ratio. Range: 1.2 - 2.4.
    main_draft_ratio: float          # Main draft zone (apron zone). Recommended: 30 - 60 fold.
    draft_zone_distance_A_mm: float  # Distance A in drafting unit (adjustable per fiber length).
    draft_zone_distance_B_mm: float  # Distance B in drafting unit (adjustable per fiber length).

    # NOZZLE / TWISTING ZONE
    air_pressure_bar: float          # Compressed air pressure. Range: 4.0 - 6.0 bar.
                                     # Higher pressure → higher wrapping twist.
    distance_L_mm: float             # Distance from front roller nip to spindle entry.
                                     # Should be slightly shorter than mean fiber length.
                                     # Longer L → more wrapping fibers separated.

    # WINDING / DELIVERY ZONE
    delivery_speed_m_min: float      # Yarn delivery/spinning speed. Range: up to 450 m/min.
                                     # Higher speed → lower wrapping twist.
    spinning_draft: float            # Ratio of take-up roller speed to drafting delivery speed.
                                     # Usually slightly below 1.0. Lower = more wrapping fibers.
    package_diameter_mm: float       # Target package diameter. Max 300 mm.

    # TARGET YARN
    yarn_count_Ne: float             # Target yarn count in Ne. Range: 20 - 50 (J 10).
    yarn_count_tex: float            # Target yarn count in tex (= 590.5 / Ne approximately).

    # MACHINE CONDITION
    ambient_temperature_C: float     # In Celsius. Affects fiber behavior.
    ambient_humidity_pct: float      # Relative humidity %. Important for cotton processing.
    last_maintenance_date: str       # ISO date string, e.g. "2025-10-01".
    maintenance_interval_hours: float  # Recommended service interval in hours.
    operating_hours_since_maintenance: float  # Tracked by machine control system.


@dataclass
class YarnQualityOutput:
    """
    Layer 4 — Predicted output quality metrics for Spinning.
    """
    wrapping_twist_am: float           # Wrapping twist multiplier (αm). Optimal range: 140 - 160 am.
    wrapping_fiber_pct: float          # % of total yarn mass that are wrapping/surface fibers.
                                       # Good threshold: >= 15%. Fine yarns reach up to 30%.
    yarn_tenacity_cN_tex: float        # Predicted yarn tenacity in cN/tex.
    yarn_evenness_CVm_pct: float       # CVm% — mass coefficient of variation. Lower is better.
    hairiness_H: float                 # Uster hairiness H value. Airjet typically much lower than ring.
    neps_per_km: float                 # Nep count per km (200% nep threshold).
    spinning_tension_cN: float         # Tension in yarn between nozzle and take-up rollers (5-15 cN).
    waste_fiber_pct: float             # Fiber loss as % of input (short fibers lost: 5-10%).
    ends_down_risk: str                # "low", "medium", "high" — qualitative risk level.
    production_rate_g_spi_h: float     # Grams per spinning position per hour.
    warnings: list                     # List of warning messages for out-of-range conditions.


# ─────────────────────────────────────────────────────────────────────────────
# CORE SIMULATION FUNCTIONS
# Each function models one specific cause-effect relationship from the manual.
# ─────────────────────────────────────────────────────────────────────────────

def predict_wrapping_twist(
    delivery_speed_m_min: float,
    air_pressure_bar: float,
    yarn_count_tex: float
) -> float:
    """
    Predicts wrapping twist multiplier (αm) as a function of spinning speed
    and air pressure.

    Source: Rieter Manual Vol 6, Fig. 39 and Fig. 40.
    - Fig. 39: For cotton 20 tex, twist drops from ~450 am at 50 m/min
               to ~150 am at 400 m/min. Approximately inverse relationship.
    - Fig. 40: Twist increases from ~130 am at 4.5 bar to ~190 am at 5.5 bar.
               Approximately linear with pressure.

    Model: twist_am = base_twist * pressure_factor / speed_factor
    Calibrated to match manual figures for cotton 20 tex.
    """
    # Base twist at reference conditions (250 m/min, 5.0 bar, 20 tex)
    # From Fig 39: approximately 200 am at 250 m/min for 20 tex cotton
    base_twist = 200.0

    # Speed effect: inverse relationship (Fig. 39)
    # At 50 m/min → ~450 am, at 400 m/min → ~150 am
    # Modeled as: twist ∝ 1 / sqrt(speed), normalized to reference speed of 250
    speed_factor = math.sqrt(delivery_speed_m_min / 250.0)

    # Pressure effect: approximately linear (Fig. 40)
    # At 4.5 bar → ~130 am, at 5.5 bar → ~190 am (delta ~60 per 1 bar)
    # Reference: 5.0 bar → ~160 am
    pressure_factor = 1.0 + (air_pressure_bar - 5.0) * 0.3

    # Yarn count effect: finer yarns retain more wrapping twist
    # Coarser yarns have lower relative twist due to geometry
    count_factor = math.sqrt(20.0 / yarn_count_tex)  # normalized to 20 tex

    wrapping_twist = base_twist * pressure_factor * count_factor / speed_factor

    return round(wrapping_twist, 1)


def predict_wrapping_fiber_percentage(
    yarn_count_tex: float,
    spinning_draft: float,
    distance_L_mm: float,
    fiber_length_mm: float
) -> float:
    """
    Predicts the percentage of wrapping (surface) fibers in the yarn.

    Source: Rieter Manual Vol 6, Section 2.7.8.
    - Fine count yarns (low tex) reach up to 30% wrapping fibers.
    - Coarse yarns drop to 15% or below.
    - Lower spinning draft → more wrapping fibers.
    - Longer distance L → more fiber ends separated → more wrapping fibers.
    - L should be slightly shorter than mean fiber length for optimal separation.

    Critical threshold: below 15% → yarn axis distorts, strength drops sharply.
    """
    # Base wrapping % from yarn count (fine=30%, coarse=15%)
    # Linear interpolation: at 10 tex → 30%, at 50 tex → 15%
    base_pct = max(15.0, 30.0 - (yarn_count_tex - 10.0) * (15.0 / 40.0))

    # Draft effect: lower spinning draft → more wrapping fibers
    # Spinning draft is ratio of take-up to delivery speed (usually ~0.97-1.0)
    # Deviation below 1.0 increases wrapping fiber count
    draft_bonus = max(0.0, (1.0 - spinning_draft) * 20.0)

    # Distance L effect: L relative to fiber length
    # Optimal L is slightly shorter than fiber length
    # If L is much shorter, fewer fibers are separated
    # If L equals fiber length, separation is maximized
    l_ratio = distance_L_mm / fiber_length_mm
    l_factor = min(1.0, l_ratio)  # capped at 1.0 (no benefit from L > fiber length)
    l_bonus = (l_factor - 0.7) * 10.0  # bonus relative to baseline L ratio of 0.7

    total_pct = base_pct + draft_bonus + l_bonus
    return round(min(30.0, max(10.0, total_pct)), 1)


def predict_yarn_tenacity(
    wrapping_twist_am: float,
    wrapping_fiber_pct: float,
    fiber_type: str,
    fiber_length_mm: float,
    yarn_count_Ne: float
) -> float:
    """
    Predicts yarn tenacity in cN/tex.

    Source: Rieter Manual Vol 6, Fig. 41, 42, 43, and Section 2.7.9.1.
    - Optimal wrapping twist is 140-160 am. Strength drops above or below this range.
    - The strength/twist curve mirrors that of ring-spun yarn.
    - For PES/CO 67/33% blends: Ne 20 → ~19.3, Ne 30 → ~19.24, Ne 40 → ~17.2 cN/tex (airjet).
    - For 100% cotton carded: Ne 20 → ~13.2, Ne 32 → ~12.2 cN/tex (airjet).
    - Airjet yarn strength sits between ring and rotor, nearer rotor for short staple,
      nearer ring for longer staple.
    - Below 15% wrapping fibers: significant strength loss due to corkscrew distortion.

    Reference tenacity values by fiber type and count (from Fig. 42, 43):
    """
    # Base tenacity by fiber type and yarn count (from manual figures)
    # Values in cN/tex at optimal wrapping twist (140-160 am)
    base_tenacity_map = {
        "cotton_carded": {20: 13.2, 30: 12.4, 40: 11.5},
        "cotton_combed": {20: 15.4, 30: 14.1, 40: 12.2},
        "blend_PES_CO":  {20: 19.3, 30: 19.24, 40: 17.2},
        "polyester":     {20: 21.0, 30: 20.0,  40: 18.5},
        "viscose":       {20: 14.0, 30: 13.0,  40: 12.0},
        "MMF":           {20: 20.5, 30: 19.5,  40: 18.0},
    }

    # Normalize fiber type key
    ftype = fiber_type.lower().replace(" ", "_")
    if "blend" in ftype or "pes" in ftype:
        ftype = "blend_PES_CO"
    elif "cotton" in ftype and "comb" in ftype:
        ftype = "cotton_combed"
    elif "cotton" in ftype:
        ftype = "cotton_carded"
    elif "viscose" in ftype or "cv" in ftype:
        ftype = "viscose"
    elif "polyester" in ftype or "pes" in ftype:
        ftype = "polyester"
    else:
        ftype = "MMF"

    base_map = base_tenacity_map.get(ftype, base_tenacity_map["cotton_carded"])

    # Interpolate base tenacity for the given yarn count
    counts = sorted(base_map.keys())
    if yarn_count_Ne <= counts[0]:
        base = base_map[counts[0]]
    elif yarn_count_Ne >= counts[-1]:
        base = base_map[counts[-1]]
    else:
        for i in range(len(counts) - 1):
            if counts[i] <= yarn_count_Ne <= counts[i + 1]:
                t = (yarn_count_Ne - counts[i]) / (counts[i + 1] - counts[i])
                base = base_map[counts[i]] + t * (base_map[counts[i + 1]] - base_map[counts[i]])
                break

    # Twist effect: parabolic — optimal at 150 am, drops on either side (Fig. 41)
    # At 100 am: -30%, at 200 am: -10%, at 300 am: -40% relative to peak
    twist_deviation = abs(wrapping_twist_am - 150.0)
    if twist_deviation <= 30:
        twist_factor = 1.0  # within optimal zone
    elif twist_deviation <= 80:
        twist_factor = 1.0 - (twist_deviation - 30) * 0.004  # gentle drop
    else:
        twist_factor = max(0.5, 1.0 - (twist_deviation - 30) * 0.006)

    # Wrapping fiber % effect: below 15% causes significant strength loss
    if wrapping_fiber_pct < 15.0:
        wrap_penalty = (15.0 - wrapping_fiber_pct) * 0.04  # 4% loss per % point below threshold
    else:
        wrap_penalty = 0.0

    # Fiber length effect: longer fibers → better strength (Fig. 33)
    # Normalized to 30 mm (PES/CO typical length)
    length_factor = 0.85 + (fiber_length_mm / 30.0) * 0.15

    tenacity = base * twist_factor * length_factor * (1.0 - wrap_penalty) # type: ignore
    return round(max(5.0, tenacity), 2)


def predict_hairiness(
    wrapping_twist_am: float,
    delivery_speed_m_min: float,
    fiber_type: str,
    yarn_count_Ne: float
) -> float:
    """
    Predicts Uster hairiness H value.

    Source: Rieter Manual Vol 6, Fig. 45 and Fig. 46.
    - Fig. 45: Airjet 20/1 Ne carded cotton → H ≈ 398-410 (vs ring ≈ 2251-2318 Zweigle S3).
    - Fig. 46: H decreases as wrapping twist increases.
               At 140 am: H ≈ 6.7, at 220 am: H ≈ 4.0, at 280 am: H ≈ 3.0 (cotton 37 tex).
    - Airjet hairiness is considerably lower than ring-spun yarn.
    - Core fibers hidden inside yarn do not contribute to hairiness.

    Model uses Uster H value (not Zweigle S3).
    """
    # Base H at reference conditions (150 am, 20 Ne cotton)
    # From Fig. 46 at 150 am for cotton 37 tex: H ≈ 5.5
    # Fine yarns (20 Ne) have lower absolute hairiness
    count_factor = math.sqrt(yarn_count_Ne / 20.0)  # finer yarns → lower H
    base_H = 5.5 / count_factor

    # Twist effect: higher twist → lower hairiness (Fig. 46)
    # At 140 am: H ≈ 6.7, at 280 am: H ≈ 3.0 (for 37 tex cotton)
    # Approximately: H decreases 0.027 per unit of αm above 140
    twist_reduction = max(0.0, (wrapping_twist_am - 140.0) * 0.022)
    H = base_H - twist_reduction

    # Speed effect: higher speed → slightly higher hairiness (secondary effect)
    speed_factor = 1.0 + (delivery_speed_m_min - 300.0) * 0.0003
    H *= speed_factor

    # Fiber type adjustment: synthetics tend to have lower hairiness
    if "cotton" in fiber_type.lower():
        H *= 1.0
    elif "blend" in fiber_type.lower():
        H *= 0.85
    else:
        H *= 0.75  # pure synthetics

    return round(max(1.5, H), 2)


def predict_nep_count(
    delivery_speed_m_min: float,
    wrapping_twist_am: float,
    fiber_type: str,
    trash_content_pct: float
) -> float:
    """
    Predicts 200% nep count per km.

    Source: Rieter Manual Vol 6, Fig. 44 and Section 2.7.9.3.
    - Fig. 44: Nep count increases drastically as spinning speed decreases
               (i.e., as wrapping twist increases).
    - At 530 m/min: ~50 neps/km. At 320 m/min: ~300 neps/km (cotton 20 tex).
    - Some wrapping fibers or bundles can be counted as neps.
    - Nep count is similar to ring-spun yarn when wrapping twist is not excessive.

    Model: neps increase sharply below ~380 m/min (inverse speed relationship).
    """
    # Base nep count at reference speed (450 m/min)
    base_neps = 80.0

    # Speed effect (Fig. 44): approximately hyperbolic
    # neps ∝ 1 / (speed - threshold)
    threshold_speed = 280.0  # below this, neps increase very sharply
    if delivery_speed_m_min <= threshold_speed:
        neps = base_neps * 5.0  # very high — out of practical range
    else:
        speed_ratio = 450.0 / delivery_speed_m_min
        neps = base_neps * (speed_ratio ** 2.5)

    # High wrapping twist amplifies nep count (wrapping bundles counted as neps)
    if wrapping_twist_am > 200:
        twist_penalty = (wrapping_twist_am - 200) * 0.5
        neps += twist_penalty

    # Fiber type: cotton has more neps than synthetics
    if "cotton" in fiber_type.lower():
        neps *= 1.0
    elif "blend" in fiber_type.lower():
        neps *= 0.8
    else:
        neps *= 0.6

    # Trash content amplifies neps
    neps *= (1.0 + trash_content_pct * 0.1)

    return round(max(20.0, neps), 0)


def predict_spinning_tension(
    yarn_count_tex: float,
    wrapping_fiber_pct: float,
    delivery_speed_m_min: float,
    air_pressure_bar: float
) -> float:
    """
    Predicts spinning tension in cN (tension between nozzle and take-up rollers).

    Source: Rieter Manual Vol 6, Section 2.7.5 and Fig. 38.
    Formula derived from manual:
        Pspinn = 0.5 * T_yarn * W * ωf² * R² * e^(μβ) * sin(β)

    Simplified for simulation:
    - Tension range: 5 - 15 cN (much lower than ring spinning).
    - Higher air pressure → higher fiber rotation speed → higher tension.
    - Unlike ring spinning, end breaks are rarely due to weak yarn spots;
      they are caused by feed irregularities.

    We use a simplified empirical model calibrated to the manual's stated range.
    """
    # Angular velocity proxy: proportional to air pressure
    # At 5 bar and 450 m/min: tension ≈ 8-10 cN (midrange)
    base_tension = 8.0

    # Pressure effect: higher pressure → faster fiber rotation → higher tension
    pressure_factor = 1.0 + (air_pressure_bar - 5.0) * 0.3

    # Yarn count effect: heavier yarn → slightly higher tension
    count_factor = math.sqrt(yarn_count_tex / 20.0)

    # Wrapping fiber % effect: more wrapping fibers → slightly higher tension
    wrap_factor = 1.0 + (wrapping_fiber_pct - 20.0) * 0.01

    tension = base_tension * pressure_factor * count_factor * wrap_factor
    return round(min(15.0, max(5.0, tension)), 2)


def predict_waste_percentage(
    short_fiber_content_pct: float,
    distance_L_mm: float,
    fiber_length_mm: float
) -> float:
    """
    Predicts fiber waste as % of input.

    Source: Rieter Manual Vol 6, Section 2.7.2.
    - Fiber loss in Airjet is relatively high: 5 to 10%.
    - Short fibers are preferentially lost (they bypass the spindle entirely).
    - Higher short fiber content → higher waste.
    - Longer distance L → more fibers extracted → slightly more waste.
    """
    base_waste = 5.0  # minimum waste at ideal conditions

    # Short fiber contribution: each % of short fiber adds ~0.15% to waste
    short_fiber_waste = short_fiber_content_pct * 0.15

    # Distance L contribution: L close to fiber length → more extraction
    l_ratio = min(1.0, distance_L_mm / fiber_length_mm)
    l_waste = l_ratio * 2.0  # up to 2% extra from L setting

    total_waste = base_waste + short_fiber_waste + l_waste
    return round(min(12.0, total_waste), 1)


def predict_evenness(
    total_draft_ratio: float,
    main_draft_ratio: float,
    sliver_count_ktex: float,
    fiber_length_mm: float,
    fiber_fineness_dtex: float
) -> float:
    """
    Predicts yarn evenness CVm%.

    Source: Rieter Manual Vol 6, Section 2.7.4 and 2.7.9.2.
    - Airjet achieves evenness comparable to ring-spun yarn.
    - The drafting unit is the main element influencing evenness.
    - Main draft should be 30-60 fold for optimal results.
    - Total draft should not exceed ~200 for good evenness (technology limit).
    - Finer input slivers (lower ktex) are needed for fine yarn counts.

    Model: base CVm from fiber properties, penalized for drafting extremes.
    """
    # Base CVm from fiber properties
    # Finer fibers → better evenness (more fibers per cross-section)
    # Longer fibers → better drafting control
    base_CVm = 12.0 + (fiber_fineness_dtex - 1.5) * 1.0 - (fiber_length_mm - 25.0) * 0.1

    # Draft ratio penalty: outside 30-60 main draft zone
    if main_draft_ratio < 30:
        draft_penalty = (30 - main_draft_ratio) * 0.05
    elif main_draft_ratio > 60:
        draft_penalty = (main_draft_ratio - 60) * 0.1
    else:
        draft_penalty = 0.0

    # Total draft penalty: above 200 fold
    if total_draft_ratio > 200:
        total_draft_penalty = (total_draft_ratio - 200) * 0.02
    else:
        total_draft_penalty = 0.0

    CVm = base_CVm + draft_penalty + total_draft_penalty
    return round(max(8.0, min(20.0, CVm)), 1)


def predict_production_rate(
    delivery_speed_m_min: float,
    yarn_count_tex: float
) -> float:
    """
    Predicts production rate in grams per spinning position per hour.

    Source: Rieter Manual Vol 6, Fig. 57.
    Formula: production_rate (g/spi/h) = delivery_speed (m/min) * yarn_count (tex) * 60 / 1000

    From manual Fig. 57 at Ne 30 (≈20 tex), Airjet at ~350 m/min → ~400 g/spi/h.
    This matches: 350 * 20 * 60 / 1000 = 420 g/spi/h. Consistent.
    """
    rate = delivery_speed_m_min * yarn_count_tex * 60.0 / 1000.0
    return round(rate, 1)


def assess_ends_down_risk(
    wrapping_fiber_pct: float,
    spinning_tension_cN: float,
    short_fiber_content_pct: float,
    trash_content_pct: float,
    operating_hours_since_maintenance: float,
    maintenance_interval_hours: float
) -> str:
    """
    Qualitative assessment of end break (ends down) risk.

    Source: Rieter Manual Vol 6, Section 2.7.5.
    - Unlike ring spinning, ends down in Airjet are mostly due to feed irregularities,
      not weak yarn spots (tension is too low to cause breaks at weak spots).
    - Risk factors: low wrapping fiber %, high trash, high short fiber content,
      maintenance overdue, and nozzle blockage.
    """
    risk_score = 0

    if wrapping_fiber_pct < 15.0:
        risk_score += 3  # critical — yarn structure compromised
    elif wrapping_fiber_pct < 18.0:
        risk_score += 1

    if short_fiber_content_pct > 15.0:
        risk_score += 2
    elif short_fiber_content_pct > 10.0:
        risk_score += 1

    if trash_content_pct > 2.0:
        risk_score += 2
    elif trash_content_pct > 1.0:
        risk_score += 1

    maintenance_ratio = operating_hours_since_maintenance / maintenance_interval_hours
    if maintenance_ratio > 1.0:
        risk_score += 2
    elif maintenance_ratio > 0.85:
        risk_score += 1

    if risk_score <= 1:
        return "low"
    elif risk_score <= 3:
        return "medium"
    else:
        return "high"


# ─────────────────────────────────────────────────────────────────────────────
# MASTER SIMULATION FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def simulate_airjet_spinning(
    material: InputMaterial,
    params: AirjetOperationalParams
) -> YarnQualityOutput:
    """
    Master simulation function for Airjet Spinning.

    Takes Layer 2 (input material) and Layer 3 (operational parameters),
    runs all prediction models, and returns Layer 4 (output quality metrics).

    Also performs parameter validation and generates warnings for out-of-range
    conditions based on limits documented in the Rieter manual.
    """
    warnings = []

    # ── PARAMETER VALIDATION ──────────────────────────────────────────────────

    # Yarn count range (J 10: Ne 20-50)
    if params.yarn_count_Ne < 20 or params.yarn_count_Ne > 50:
        warnings.append(
            f"Yarn count {params.yarn_count_Ne} Ne is outside J 10 recommended range (20-50 Ne)."
        )

    # Fiber length check
    if material.fiber_length_mm < 25.4:  # 1 inch minimum for cotton
        warnings.append(
            f"Fiber length {material.fiber_length_mm} mm is below minimum for cotton (25.4 mm / 1 inch). "
            "Cotton must be combed for counts finer than this."
        )

    # Sliver count check
    if material.sliver_count_ktex < 2.0 or material.sliver_count_ktex > 4.5:
        warnings.append(
            f"Sliver count {material.sliver_count_ktex} ktex is outside recommended range (2.0 - 4.5 ktex)."
        )

    # Total draft check (technology limit: 200 fold for J 10)
    if params.total_draft_ratio > 200:
        warnings.append(
            f"Total draft {params.total_draft_ratio} exceeds recommended technology limit of 200 fold. "
            "Evenness and strength will be degraded."
        )

    # Main draft zone check (recommended 30-60 fold)
    if params.main_draft_ratio < 30 or params.main_draft_ratio > 60:
        warnings.append(
            f"Main draft ratio {params.main_draft_ratio} is outside the optimal range (30-60 fold). "
            "Adjust for better evenness."
        )

    # Air pressure check (practical range: 4.0 - 6.0 bar)
    if params.air_pressure_bar < 4.0 or params.air_pressure_bar > 6.0:
        warnings.append(
            f"Air pressure {params.air_pressure_bar} bar is outside practical range (4.0 - 6.0 bar)."
        )

    # Delivery speed check (J 10 max: 450 m/min)
    if params.delivery_speed_m_min > 450:
        warnings.append(
            f"Delivery speed {params.delivery_speed_m_min} m/min exceeds J 10 maximum (450 m/min)."
        )

    # Distance L check: should be slightly shorter than fiber length
    if params.distance_L_mm >= material.fiber_length_mm:
        warnings.append(
            f"Distance L ({params.distance_L_mm} mm) should be shorter than fiber length "
            f"({material.fiber_length_mm} mm) to ensure proper fiber end separation."
        )

    # Cotton purity check: 100% cotton needs combing above certain counts
    if "cotton" in material.fiber_type.lower() and "blend" not in material.fiber_type.lower():
        if params.yarn_count_Ne > 30 and "comb" not in material.fiber_type.lower():
            warnings.append(
                f"Spinning 100% cotton at Ne {params.yarn_count_Ne} requires combed cotton. "
                "Carded cotton will give insufficient strength (50-70% of ring-spun yarn)."
            )

    # ── RUN SIMULATION MODELS ─────────────────────────────────────────────────

    wrapping_twist = predict_wrapping_twist(
        params.delivery_speed_m_min,
        params.air_pressure_bar,
        params.yarn_count_tex
    )

    wrapping_fiber_pct = predict_wrapping_fiber_percentage(
        params.yarn_count_tex,
        params.spinning_draft,
        params.distance_L_mm,
        material.fiber_length_mm
    )

    tenacity = predict_yarn_tenacity(
        wrapping_twist,
        wrapping_fiber_pct,
        material.fiber_type,
        material.fiber_length_mm,
        params.yarn_count_Ne
    )

    hairiness = predict_hairiness(
        wrapping_twist,
        params.delivery_speed_m_min,
        material.fiber_type,
        params.yarn_count_Ne
    )

    neps = predict_nep_count(
        params.delivery_speed_m_min,
        wrapping_twist,
        material.fiber_type,
        material.trash_content_pct
    )

    spinning_tension = predict_spinning_tension(
        params.yarn_count_tex,
        wrapping_fiber_pct,
        params.delivery_speed_m_min,
        params.air_pressure_bar
    )

    waste_pct = predict_waste_percentage(
        material.short_fiber_content_pct,
        params.distance_L_mm,
        material.fiber_length_mm
    )

    evenness_CVm = predict_evenness(
        params.total_draft_ratio,
        params.main_draft_ratio,
        material.sliver_count_ktex,
        material.fiber_length_mm,
        material.fiber_fineness_dtex
    )

    production_rate = predict_production_rate(
        params.delivery_speed_m_min,
        params.yarn_count_tex
    )

    ends_down = assess_ends_down_risk(
        wrapping_fiber_pct,
        spinning_tension,
        material.short_fiber_content_pct,
        material.trash_content_pct,
        params.operating_hours_since_maintenance,
        params.maintenance_interval_hours
    )

    # Warn if wrapping fiber % is below critical threshold
    if wrapping_fiber_pct < 15.0:
        warnings.append(
            f"CRITICAL: Wrapping fiber % ({wrapping_fiber_pct}%) is below 15% threshold. "
            "Yarn axis will distort and strength will be significantly reduced."
        )

    # Warn if wrapping twist is outside optimal zone
    if wrapping_twist < 140 or wrapping_twist > 160:
        warnings.append(
            f"Wrapping twist ({wrapping_twist} am) is outside optimal range (140-160 am). "
            "Adjust air pressure or delivery speed for best strength."
        )

    return YarnQualityOutput(
        wrapping_twist_am=wrapping_twist,
        wrapping_fiber_pct=wrapping_fiber_pct,
        yarn_tenacity_cN_tex=tenacity,
        yarn_evenness_CVm_pct=evenness_CVm,
        hairiness_H=hairiness,
        neps_per_km=neps,
        spinning_tension_cN=spinning_tension,
        waste_fiber_pct=waste_pct,
        ends_down_risk=ends_down,
        production_rate_g_spi_h=production_rate,
        warnings=warnings
    )


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE USAGE AND VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    print("=" * 65)
    print("AIRJET SPINNING SIMULATION — Rieter J 10")
    print("Based on Rieter Manual of Spinning, Volume 6")
    print("=" * 65)

    # ── SCENARIO 1: Cotton/Polyester blend, typical production conditions ──
    print("\n--- SCENARIO 1: PES/CO 50/50 blend, Ne 30, optimal settings ---\n")

    material_1 = InputMaterial(
        fiber_type="blend_PES_CO",
        fiber_length_mm=33.0,       # 33 mm — typical PES/CO blend
        fiber_fineness_dtex=1.5,
        short_fiber_content_pct=8.0,
        fiber_tensile_strength_cN_tex=35.0,
        sliver_count_ktex=3.0,      # 3 ktex — within recommended range
        moisture_content_pct=6.5,
        trash_content_pct=0.5
    )

    params_1 = AirjetOperationalParams(
        total_draft_ratio=150.0,
        pre_draft_ratio=1.8,
        break_draft_ratio=1.5,
        main_draft_ratio=45.0,      # within optimal 30-60 range
        draft_zone_distance_A_mm=44.5,
        draft_zone_distance_B_mm=49.0,
        air_pressure_bar=5.0,       # reference pressure
        distance_L_mm=30.0,         # slightly shorter than fiber length (33mm)
        delivery_speed_m_min=350.0,
        spinning_draft=0.97,
        package_diameter_mm=250.0,
        yarn_count_Ne=30.0,
        yarn_count_tex=19.7,        # 590.5 / 30
        ambient_temperature_C=22.0,
        ambient_humidity_pct=60.0,
        last_maintenance_date="2025-09-01",
        maintenance_interval_hours=2000.0,
        operating_hours_since_maintenance=800.0
    )

    result_1 = simulate_airjet_spinning(material_1, params_1)

    print(f"  Wrapping Twist:        {result_1.wrapping_twist_am} am  (optimal: 140-160 am)")
    print(f"  Wrapping Fiber %:      {result_1.wrapping_fiber_pct}%  (threshold: ≥15%)")
    print(f"  Yarn Tenacity:         {result_1.yarn_tenacity_cN_tex} cN/tex")
    print(f"  Yarn Evenness CVm:     {result_1.yarn_evenness_CVm_pct}%")
    print(f"  Hairiness H:           {result_1.hairiness_H}")
    print(f"  Neps/km (200%):        {result_1.neps_per_km}")
    print(f"  Spinning Tension:      {result_1.spinning_tension_cN} cN  (range: 5-15 cN)")
    print(f"  Fiber Waste:           {result_1.waste_fiber_pct}%")
    print(f"  Ends Down Risk:        {result_1.ends_down_risk.upper()}")
    print(f"  Production Rate:       {result_1.production_rate_g_spi_h} g/spi/h")
    if result_1.warnings:
        print(f"\n  WARNINGS:")
        for w in result_1.warnings:
            print(f"    ⚠ {w}")
    else:
        print("\n  No warnings — all parameters within recommended ranges.")

    # ── SCENARIO 2: High speed, low pressure — exploring twist trade-off ──
    print("\n--- SCENARIO 2: Same material, high speed (430 m/min), lower pressure ---\n")

    params_2 = AirjetOperationalParams(
        total_draft_ratio=150.0,
        pre_draft_ratio=1.8,
        break_draft_ratio=1.5,
        main_draft_ratio=45.0,
        draft_zone_distance_A_mm=44.5,
        draft_zone_distance_B_mm=49.0,
        air_pressure_bar=4.5,       # reduced pressure
        distance_L_mm=30.0,
        delivery_speed_m_min=430.0, # near maximum speed
        spinning_draft=0.97,
        package_diameter_mm=250.0,
        yarn_count_Ne=30.0,
        yarn_count_tex=19.7,
        ambient_temperature_C=22.0,
        ambient_humidity_pct=60.0,
        last_maintenance_date="2025-09-01",
        maintenance_interval_hours=2000.0,
        operating_hours_since_maintenance=800.0
    )

    result_2 = simulate_airjet_spinning(material_1, params_2)

    print(f"  Wrapping Twist:        {result_2.wrapping_twist_am} am")
    print(f"  Wrapping Fiber %:      {result_2.wrapping_fiber_pct}%")
    print(f"  Yarn Tenacity:         {result_2.yarn_tenacity_cN_tex} cN/tex")
    print(f"  Hairiness H:           {result_2.hairiness_H}")
    print(f"  Neps/km (200%):        {result_2.neps_per_km}")
    print(f"  Ends Down Risk:        {result_2.ends_down_risk.upper()}")
    print(f"  Production Rate:       {result_2.production_rate_g_spi_h} g/spi/h")
    if result_2.warnings:
        print(f"\n  WARNINGS:")
        for w in result_2.warnings:
            print(f"    ⚠ {w}")

    # ── SCENARIO 3: 100% carded cotton — known limitation of airjet ──
    print("\n--- SCENARIO 3: 100% carded cotton Ne 20 — known Airjet limitation ---\n")

    material_3 = InputMaterial(
        fiber_type="cotton_carded",
        fiber_length_mm=27.0,       # 1 1/16 inch carded cotton
        fiber_fineness_dtex=1.7,
        short_fiber_content_pct=18.0,  # carded cotton has higher short fiber content
        fiber_tensile_strength_cN_tex=28.0,
        sliver_count_ktex=3.5,
        moisture_content_pct=7.0,
        trash_content_pct=1.8       # carded cotton has more trash
    )

    params_3 = AirjetOperationalParams(
        total_draft_ratio=120.0,
        pre_draft_ratio=1.7,
        break_draft_ratio=1.4,
        main_draft_ratio=40.0,
        draft_zone_distance_A_mm=44.5,
        draft_zone_distance_B_mm=49.0,
        air_pressure_bar=5.5,       # high pressure to compensate short fibers
        distance_L_mm=24.0,         # shorter than fiber length to avoid too much waste
        delivery_speed_m_min=350.0,
        spinning_draft=0.97,
        package_diameter_mm=250.0,
        yarn_count_Ne=20.0,
        yarn_count_tex=29.5,        # 590.5 / 20
        ambient_temperature_C=22.0,
        ambient_humidity_pct=60.0,
        last_maintenance_date="2025-09-01",
        maintenance_interval_hours=2000.0,
        operating_hours_since_maintenance=800.0
    )

    result_3 = simulate_airjet_spinning(material_3, params_3)

    print(f"  Wrapping Twist:        {result_3.wrapping_twist_am} am")
    print(f"  Wrapping Fiber %:      {result_3.wrapping_fiber_pct}%")
    print(f"  Yarn Tenacity:         {result_3.yarn_tenacity_cN_tex} cN/tex")
    print(f"  Neps/km (200%):        {result_3.neps_per_km}")
    print(f"  Fiber Waste:           {result_3.waste_fiber_pct}%")
    print(f"  Ends Down Risk:        {result_3.ends_down_risk.upper()}")
    print(f"  Production Rate:       {result_3.production_rate_g_spi_h} g/spi/h")
    if result_3.warnings:
        print(f"\n  WARNINGS:")
        for w in result_3.warnings:
            print(f"    ⚠ {w}")

    print("\n" + "=" * 65)
    print("Simulation complete.")
    print("=" * 65)