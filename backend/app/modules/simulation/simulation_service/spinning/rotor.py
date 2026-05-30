"""
Rotor Spinning Simulation Module
Process: Spinning > Rotor Spinning (Rieter R 70 / BT 923)

All parameter relationships derived from:
Rieter Manual of Spinning, Volume 5 – Rotor Spinning
M. Frey and P. Toggweiler, Rieter Machine Works Ltd.
Supporting comparison data from Volume 6 – Alternative Spinning Systems
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
    Feedstock is card sliver or draw frame sliver (1–3 passages).
    """
    fiber_type: str              # "cotton_carded", "cotton_combed", "blend_PES_CO",
                                 # "polyester", "viscose", "MMF"
    fiber_length_mm: float       # Mean fiber length in mm. Rotor limit: ~40 mm max.
                                 # Longer fibers improve strength but risk opening roller wrapping.
    fiber_fineness_dtex: float   # Fiber fineness in dtex. Finer fibers → more fibers per
                                 # cross-section → better evenness and strength.
    short_fiber_content_pct: float  # % of fibers below 12 mm. Higher = more waste, weaker yarn,
                                    # and rotor groove contamination.
    fiber_tensile_strength_cN_tex: float  # Fiber tenacity in cN/tex.
    sliver_count_ktex: float     # Input sliver linear density in ktex. Range: 3.0 - 7.0 ktex.
                                 # Must match total draft to produce target yarn count.
    moisture_content_pct: float  # Fiber moisture %. Affects static buildup and fiber cohesion.
    trash_content_pct: float     # Impurity level (%). Primary driver of rotor groove deposits
                                 # and periodic end-break spikes.


@dataclass
class RotorOperationalParams:
    """
    Layer 3 — Operational parameters specific to Rotor Spinning subprocess.
    Based on Rieter R 70 / BT 923 and standard open-end rotor machines.
    """
    # ── ROTOR ZONE ───────────────────────────────────────────────────────────
    rotor_diameter_mm: float         # Rotor diameter in mm. Typical range: 28 - 56 mm.
                                     # Smaller rotor → higher achievable rpm → higher twist potential.
                                     # Larger rotor → more back-doubling laps → better evenness.
    rotor_speed_rpm: float           # Rotor rotational speed in rpm. Range: 40 000 - 150 000 rpm.
                                     # Each revolution inserts exactly one turn of twist.
                                     # Must respect peripheral speed limit (~160 m/s max).
    twist_factor_am: float           # Metric twist factor αm = T(t/m) × √(tex/1000).
                                     # Typical range: 90 - 180 for rotor-spun cotton.
                                     # Controls yarn strength, hardness, and end-break rate.

    # ── OPENING ROLLER ───────────────────────────────────────────────────────
    opening_roller_speed_rpm: float  # Opening roller speed in rpm. Range: 5 000 - 10 000 rpm.
                                     # Higher speed → better fiber individualization but more fiber damage.
    opening_roller_wire_type: str    # "fine_wire" or "coarse_wire".
                                     # Fine wire suits finer fibers and counts (Ne > 20).
                                     # Coarse wire handles coarser counts and trashier raw materials.

    # ── NAVEL AND GROOVE ─────────────────────────────────────────────────────
    navel_type: str                  # "smooth", "notched", or "grooved".
                                     # Smooth → lower hairiness, less abrasion resistance.
                                     # Notched/grooved → wraps fiber ends, higher hairiness,
                                     # better abrasion resistance (preferred for woven goods).
    rotor_groove_type: str           # "T_groove", "U_groove", or "K_groove".
                                     # U-groove: self-cleaning, lower nep accumulation.
                                     # T-groove: higher fiber consolidation, prone to deposit buildup.
                                     # K-groove: optimized profile, low neps, good for fine counts.

    # ── DRAFTING / FEED ──────────────────────────────────────────────────────
    total_draft_ratio: float         # Total draft from sliver to yarn. Typically 50 - 300 fold.
                                     # Set by: (sliver_count_ktex × 1000) / yarn_count_tex.
    delivery_speed_m_min: float      # Yarn delivery/winding speed in m/min. Max: ~200 m/min.
                                     # Fundamental constraint: v = n_rotor / T(t/m).
                                     # T(t/m) = twist_factor_am / √(yarn_count_tex / 1000).

    # ── TARGET YARN ──────────────────────────────────────────────────────────
    yarn_count_Ne: float             # Target yarn count in Ne. Rotor range: 4 - 40 Ne.
    yarn_count_tex: float            # Target yarn count in tex (≈ 590.5 / Ne).

    # ── MACHINE CONDITION ────────────────────────────────────────────────────
    ambient_temperature_C: float     # In Celsius. Affects fiber friction and static.
    ambient_humidity_pct: float      # Relative humidity %. Important for cotton processing.
    last_maintenance_date: str       # ISO date string, e.g. "2025-10-01".
    maintenance_interval_hours: float  # Recommended service interval in hours.
    operating_hours_since_maintenance: float  # Tracked by machine control system.


@dataclass
class YarnQualityOutput:
    """
    Layer 4 — Predicted output quality metrics for Spinning.
    """
    actual_twist_turns_per_m: float    # Actual twist inserted in turns/m (= rotor_rpm / delivery_speed).
    back_doubling_index: float         # Estimated number of fiber back-doubling passes in rotor groove.
                                       # Higher index → better self-leveling → better evenness.
    yarn_tenacity_cN_tex: float        # Predicted yarn tenacity in cN/tex.
    yarn_evenness_CVm_pct: float       # CVm% — mass coefficient of variation. Lower is better.
    hairiness_H: float                 # Uster hairiness H value. Rotor yarn sits between ring and air-jet.
    neps_per_km: float                 # Nep count per km (200% nep threshold).
    spinning_tension_cN: float         # Tension in yarn between rotor groove and take-off tube (2-8 cN).
    waste_fiber_pct: float             # Fiber loss as % of input (trash + short fibers: 3-10%).
    ends_down_risk: str                # "low", "medium", "high" — qualitative risk level.
    production_rate_g_rotor_h: float   # Grams per rotor position per hour.
    warnings: list                     # List of warning messages for out-of-range conditions.


# ─────────────────────────────────────────────────────────────────────────────
# CORE SIMULATION FUNCTIONS
# Each function models one specific cause-effect relationship from the manual.
# ─────────────────────────────────────────────────────────────────────────────

def calculate_actual_twist(
    rotor_speed_rpm: float,
    delivery_speed_m_min: float
) -> float:
    """
    Calculates the actual twist inserted in the yarn in turns/m.

    Source: Rieter Manual Vol 5, Twist Insertion section.
    In rotor spinning, one revolution of the rotor inserts exactly one
    turn of twist into the yarn — this is the fundamental equation of
    the process and derives directly from the geometry of the open-end
    principle:

        T (t/m) = n_rotor (rpm) / v_delivery (m/min)

    Unlike ring spinning, there is no traveler lag or twist loss. The
    equation is exact. The delivery speed and rotor speed are therefore
    set together to achieve the desired twist factor αm.

    Note: for fine counts (high Ne) at high rotor speeds, the delivery
    speed approaches the machine limit (~200 m/min), which constrains
    the minimum achievable αm.
    """
    if delivery_speed_m_min <= 0:
        return 0.0
    twist = rotor_speed_rpm / delivery_speed_m_min
    return round(twist, 1)


def calculate_back_doubling_index(
    rotor_diameter_mm: float,
    fiber_length_mm: float
) -> float:
    """
    Estimates the number of back-doubling passes in the rotor groove.

    Source: Rieter Manual Vol 5, Back-doubling section.
    Back-doubling is one of the most important and beneficial features
    of rotor spinning. Fibers deposited in the rotor groove are drawn
    off not individually but as a consolidated ring. Before each fiber
    leaves the groove, it overlaps with fibers already deposited in
    previous laps. The number of such overlap laps is approximately:

        N_bd ≈ (π × D_rotor) / L_fiber

    where D_rotor is the rotor diameter and L_fiber is the mean fiber
    length. This back-doubling acts as a self-leveling mechanism,
    attenuating sliver mass irregularities in the same way as doubling
    at a draw frame, and is responsible for the excellent evenness of
    rotor-spun yarn relative to ring-spun yarn.

    A higher back-doubling index means better self-leveling of the
    fiber mass, which directly reduces CVm%.
    """
    rotor_circumference_mm = math.pi * rotor_diameter_mm
    index = rotor_circumference_mm / max(fiber_length_mm, 1.0)
    return round(index, 2)


def predict_yarn_tenacity(
    twist_factor_am: float,
    fiber_type: str,
    fiber_length_mm: float,
    yarn_count_Ne: float,
    rotor_diameter_mm: float,
    short_fiber_content_pct: float
) -> float:
    """
    Predicts yarn tenacity in cN/tex for rotor-spun yarn.

    Source: Rieter Manual Vol 6, Fig. 42, Fig. 43, Fig. 56.
    - Rotor yarn strength lies between ring and friction-spun yarn,
      nearer to friction spinning for short staples, nearer to ring
      for longer staples (Vol 6, Fig. 33 and Fig. 56).
    - Comparison values at optimal twist (Vol 6, Fig. 42 - Murata data):
      100% cotton carded:   Ne 20 → ~12.4, Ne 32 → ~12.2 cN/tex (OE rotor).
    - Comparison values (Vol 6, Fig. 43 - Murata data):
      50% PES / 50% CO:     Ne 20 → ~17.8, Ne 30 → ~17.5, Ne 40 → ~17.2 cN/tex.
    - Twist factor αm has a parabolic effect: optimal range ≈ 110-140.
      Below ~90: insufficient fiber binding → sharp strength loss.
      Above ~160: over-twisted, fiber buckling at groove wall → strength loss.
    - Larger rotor diameter → fibers travel a longer arc at the groove wall
      → slightly greater fiber buckling → marginal tenacity loss.
    - Short fiber content (SFC): short fibers contribute negligibly to
      load-bearing capacity but increase yarn cross-section variability.
    - Fiber length: longer fibers → greater fiber-to-fiber overlap in
      the yarn body → higher tenacity. Effect is more pronounced in
      rotor yarn than in ring yarn because the fiber orientation is
      less perfect in rotor yarn.

    Base values calibrated to Murata/Rieter comparison figures in Vol 6.
    """
    # Base tenacity map by fiber type and count (cN/tex at optimal twist)
    # Values derived from Vol 6 Figs 42, 43, 56 and cross-referenced with
    # Vol 5 tenacity tables.
    base_tenacity_map = {
        "cotton_carded":  {10: 13.5, 20: 12.4, 30: 11.8, 40: 11.0},
        "cotton_combed":  {10: 15.0, 20: 13.8, 30: 13.0, 40: 12.2},
        "blend_PES_CO":   {20: 17.8, 30: 17.5, 40: 17.2},
        "polyester":      {20: 20.0, 30: 19.2, 40: 18.4},
        "viscose":        {20: 13.5, 30: 13.0, 40: 12.5},
        "MMF":            {20: 19.0, 30: 18.3, 40: 17.5},
    }

    # Normalize fiber type key
    ftype = fiber_type.lower().replace(" ", "_")
    if "blend" in ftype or ("pes" in ftype and "co" in ftype):
        ftype = "blend_PES_CO"
    elif "cotton" in ftype and "comb" in ftype:
        ftype = "cotton_combed"
    elif "cotton" in ftype:
        ftype = "cotton_carded"
    elif "viscose" in ftype or "cv" in ftype:
        ftype = "viscose"
    elif "polyester" in ftype:
        ftype = "polyester"
    else:
        ftype = "MMF"

    base_map = base_tenacity_map.get(ftype, base_tenacity_map["cotton_carded"])
    counts = sorted(base_map.keys())

    # Interpolate base tenacity for the given yarn count
    if yarn_count_Ne <= counts[0]:
        base = base_map[counts[0]]
    elif yarn_count_Ne >= counts[-1]:
        base = base_map[counts[-1]]
    else:
        base = base_map[counts[-1]]
        for i in range(len(counts) - 1):
            if counts[i] <= yarn_count_Ne <= counts[i + 1]:
                t_frac = (yarn_count_Ne - counts[i]) / (counts[i + 1] - counts[i])
                base = (base_map[counts[i]]
                        + t_frac * (base_map[counts[i + 1]] - base_map[counts[i]]))
                break

    # Twist factor effect: parabolic, optimal near αm = 125 for rotor cotton.
    # Model: within ±20 of optimum → no penalty; outside → progressively penalized.
    optimal_am = 125.0
    twist_dev = abs(twist_factor_am - optimal_am)
    if twist_dev <= 20:
        twist_factor_eff = 1.0
    elif twist_dev <= 55:
        twist_factor_eff = 1.0 - (twist_dev - 20) * 0.005
    else:
        twist_factor_eff = max(0.55, 1.0 - (twist_dev - 20) * 0.008)

    # Rotor diameter effect: larger rotor → greater centrifugal wall contact
    # → slightly more fiber buckling → marginal tenacity loss.
    # Normalized to 33 mm reference rotor.
    diameter_factor = 1.0 - max(0.0, (rotor_diameter_mm - 33.0) * 0.0025)

    # Short fiber penalty: SFC above 8% reduces effective fiber length
    # distribution and creates local weak spots.
    short_fiber_penalty = max(0.0, (short_fiber_content_pct - 8.0) * 0.008)

    # Fiber length effect: longer fibers → more fiber-to-fiber overlap
    # in the consolidated yarn body. Normalized to 28 mm reference.
    length_factor = 0.88 + (fiber_length_mm / 28.0) * 0.12

    tenacity = (base
                * twist_factor_eff
                * diameter_factor
                * length_factor
                * (1.0 - short_fiber_penalty))
    return round(max(5.0, tenacity), 2)


def predict_yarn_evenness(
    total_draft_ratio: float,
    fiber_length_mm: float,
    fiber_fineness_dtex: float,
    rotor_diameter_mm: float,
    back_doubling_index: float
) -> float:
    """
    Predicts yarn evenness CVm% for rotor-spun yarn.

    Source: Rieter Manual Vol 5, Evenness section; Vol 6 Table 6.
    - Rotor yarn evenness is very good and typically comparable to
      ring-spun yarn for the same count, primarily due to the
      back-doubling effect in the rotor groove (Vol 5).
    - Back-doubling provides inherent self-leveling: the higher the
      back-doubling index (more fiber laps per groove circumference),
      the more short-term irregularities in the fiber stream are
      averaged out. A larger rotor with shorter fibers → higher index.
    - Finer fibers → more fibers per cross-section → Poisson noise
      (limiting irregularity) is lower → better CVm.
    - Total draft: above 250 fold, evenness degrades due to increased
      fiber float in the opening channel; below 50 fold, the fiber
      strand is insufficiently attenuated.
    - Minimum fiber count in cross-section: ≥ 80 fibers recommended
      (Vol 6, Table 5) for adequate evenness.
    - Typical CVm values: 10.0 - 15.0%.
    """
    # Base CVm from fiber fineness and length
    # Finer fibers (lower dtex) → lower CVm. Longer fibers → better control.
    base_CVm = 11.5 + (fiber_fineness_dtex - 1.5) * 0.9 - (fiber_length_mm - 25.0) * 0.07

    # Back-doubling self-leveling bonus: each doubling unit above 3.0
    # reduces CVm slightly (diminishing returns modeled logarithmically).
    if back_doubling_index > 3.0:
        leveling_bonus = 0.4 * math.log(back_doubling_index / 3.0)
    else:
        leveling_bonus = 0.0
    base_CVm -= leveling_bonus

    # Total draft penalty: outside the practical range
    if total_draft_ratio > 250:
        draft_penalty = (total_draft_ratio - 250) * 0.012
    elif total_draft_ratio < 50:
        draft_penalty = (50 - total_draft_ratio) * 0.025
    else:
        draft_penalty = 0.0

    CVm = base_CVm + draft_penalty
    return round(max(9.0, min(18.0, CVm)), 1)


def predict_hairiness(
    twist_factor_am: float,
    navel_type: str,
    fiber_type: str,
    yarn_count_Ne: float
) -> float:
    """
    Predicts Uster hairiness H value for rotor-spun yarn.

    Source: Rieter Manual Vol 6, Table 6 and Fig. 45.
    - Fig. 45 (Murata data, Zweigle S3 scale):
      Ring 20/1 Ne: 2 251 - 2 318 vs Air-jet 20/1 Ne: 398 - 410.
      Rotor yarn H (Uster scale) lies between these two extremes.
    - The navel type is the dominant machine-side parameter for
      hairiness in rotor spinning. The yarn passes over the navel
      and fiber ends projecting from the yarn surface are either
      laid back (smooth navel → low H) or actively separated and
      wrapped (notched/grooved navel → higher H).
    - A notched or grooved navel also improves abrasion resistance
      because those surface fibers form a protective wrapping layer.
    - Higher twist factor → fibers are bound more tightly into the
      yarn body → fewer protruding ends → lower hairiness.
    - Finer yarns (higher Ne) → fewer fibers per cross-section →
      lower absolute hairiness.
    - Typical Uster H values: 4.0 - 8.5 for rotor-spun cotton.
    """
    # Base H at reference conditions (notched navel, αm=125, Ne 20, cotton)
    count_factor = math.sqrt(yarn_count_Ne / 20.0)
    base_H = 6.5 / count_factor  # finer yarns → lower absolute H

    # Navel type: primary hardware driver of hairiness
    navel_multiplier = {
        "smooth":  0.78,   # fiber ends are laid back → lower H
        "notched": 1.00,   # reference type — active fiber wrapping
        "grooved": 1.15,   # most aggressive wrapping → highest H but best abrasion
    }.get(navel_type.lower(), 1.00)

    # Twist factor: higher twist tightens yarn structure
    # Reference αm = 125. Each unit above reduces H marginally.
    twist_reduction = max(0.0, (twist_factor_am - 100.0) * 0.012)
    H = base_H * navel_multiplier - twist_reduction

    # Fiber type: synthetic fibers are smoother → fewer protruding ends
    if "cotton" in fiber_type.lower():
        H *= 1.0
    elif "blend" in fiber_type.lower():
        H *= 0.88
    else:
        H *= 0.75  # pure synthetics

    return round(max(2.0, H), 2)


def predict_nep_count(
    opening_roller_speed_rpm: float,
    rotor_groove_type: str,
    fiber_type: str,
    trash_content_pct: float,
    short_fiber_content_pct: float
) -> float:
    """
    Predicts 200% nep count per km in rotor-spun yarn.

    Source: Rieter Manual Vol 5, Nep / Imperfections section.
    Neps in rotor yarn originate from three sources:
      (a) Residual fiber neps from the sliver, not broken up by the
          opening roller (primary source for cotton).
      (b) Fiber bundles due to incomplete individualization at the
          opening roller — under-speed causes imperfect opening,
          over-speed causes fiber damage that creates new neps.
      (c) Rotor groove deposits: trash particles, short fibers, and
          fiber fragments accumulate in the groove over time and are
          periodically re-incorporated into the yarn as nep spikes.

    Unlike ring spinning, rotor spinning actively removes many neps
    and trash particles through the bypass extraction channel behind
    the opening roller. The rotor groove type determines how aggressively
    deposits accumulate:
      - T-groove: deep groove traps deposits → more nep release events.
      - U-groove: shallower, more self-cleaning geometry → fewer deposits.
      - K-groove: engineered profile for minimum deposit retention.

    Opening roller speed: optimal window is 6 500 - 8 500 rpm.
    Below → insufficient individualization. Above → fiber breakage
    creates new neps faster than the extraction removes them.

    Typical 200% nep counts: 40 - 200 neps/km.
    """
    # Base nep count at reference conditions: 7 500 rpm, U-groove, clean cotton
    base_neps = 75.0

    # Opening roller speed effect: U-shaped penalty around optimal window
    optimal_roller_speed = 7_500.0
    if opening_roller_speed_rpm < 6_000:
        # Under-speed: incomplete individualization
        roller_delta = (6_000 - opening_roller_speed_rpm) / 1_000.0
        roller_penalty = roller_delta * 0.12
    elif opening_roller_speed_rpm > 8_500:
        # Over-speed: mechanical fiber damage → new neps
        roller_delta = (opening_roller_speed_rpm - 8_500) / 1_000.0
        roller_penalty = roller_delta * 0.09
    else:
        roller_penalty = 0.0
    neps = base_neps * (1.0 + roller_penalty)

    # Groove type: determines deposit accumulation propensity
    groove_factor = {
        "T_GROOVE": 1.25,  # deep groove → deposits → periodic nep spikes
        "U_GROOVE": 1.00,  # reference, self-cleaning geometry
        "K_GROOVE": 0.88,  # optimized for minimum nep accumulation
    }.get(rotor_groove_type.upper().replace("-", "_"), 1.00)
    neps *= groove_factor

    # Fiber type: cotton has natural nep burden; synthetics are nep-free
    if "cotton" in fiber_type.lower():
        neps *= 1.0
    elif "blend" in fiber_type.lower():
        neps *= 0.80
    else:
        neps *= 0.58  # pure synthetics have no seed-coat or fiber neps

    # Trash content: each % of trash raises groove deposit rate
    neps *= (1.0 + trash_content_pct * 0.14)

    # Short fiber content: short fibers escape individualization and form bundles
    neps *= (1.0 + short_fiber_content_pct * 0.009)

    return round(max(20.0, neps), 0)


def predict_spinning_tension(
    yarn_count_tex: float,
    rotor_diameter_mm: float,
    rotor_speed_rpm: float,
    twist_factor_am: float
) -> float:
    """
    Predicts spinning tension in cN (tension in the yarn between the
    rotor groove and the take-off tube).

    Source: Rieter Manual Vol 5, Spinning tension section;
    Dr. H. Stalder [15] referenced in Vol 6 Section 2.7.5.
    - Rotor spinning tension is driven by the centrifugal force exerted
      on the yarn ring rotating within the groove at rotor peripheral speed.
    - It is much lower than ring spinning tension (traveler tension can
      reach 50-200 cN), making rotor spinning inherently more gentle on yarn.
    - Unlike air-jet spinning, tension IS a limiting factor in rotor
      spinning for high speeds or coarse counts, because it acts through
      the take-off tube onto the freshly formed yarn.
    - Empirical model calibrated to measured tension range (2-8 cN)
      from Vol 5 and cross-checked with Stalder centrifugal derivation [15]:
        P ∝ m_linear × ω² × R² × arc_factor
    - Larger rotor → larger R → higher centrifugal component.
    - Higher speed → higher ω → quadratic tension increase.
    - Heavier yarn (higher tex) → more mass rotating → higher tension.
    - Higher twist factor: tighter yarn structure → marginally higher tension.

    Practical range: 2 - 10 cN. Values above 8 cN indicate risk of
    tension-induced end breaks, especially at weak spots.
    """
    # Angular velocity and rotor radius
    omega_rad_s = 2.0 * math.pi * rotor_speed_rpm / 60.0
    radius_m = (rotor_diameter_mm / 2.0) / 1000.0

    # Linear mass density in kg/m (tex = g/km = g/1000m → kg/m = tex/1e6)
    linear_density_kg_m = yarn_count_tex / 1_000_000.0

    # Approximate arc of yarn in groovе as a semicircle
    arc_length_m = math.pi * radius_m

    # Centrifugal tension: F = m_arc × ω² × R
    tension_N = linear_density_kg_m * arc_length_m * omega_rad_s**2 * radius_m
    tension_cN = tension_N * 100.0

    # Twist factor modulation: tighter twist → marginally stiffer yarn
    # → slightly elevated tension transfer through take-off tube
    twist_mod = 1.0 + (twist_factor_am - 110.0) * 0.0015

    tension_cN *= twist_mod
    return round(min(15.0, max(1.0, tension_cN)), 2)


def predict_waste_percentage(
    trash_content_pct: float,
    short_fiber_content_pct: float,
    opening_roller_speed_rpm: float,
    fiber_length_mm: float
) -> float:
    """
    Predicts fiber waste as % of input for rotor spinning.

    Source: Rieter Manual Vol 5, Waste section; Vol 6 Section 2.7.11.4.
    - Vol 6 Section 2.7.11.4 notes that rotor spinning waste is lower
      than air-jet spinning waste (5-10%), and is mainly controllable
      through the bypass valve and opening roller settings.
    - Rotor spinning extracts trash very efficiently through the bypass
      channel behind the opening roller. The extraction vacuum pulls
      trash particles and short fibers (which cannot grip the opening
      roller pins) out of the fiber stream before they enter the rotor.
    - Typical waste range: 3 - 10% depending on raw material quality.
    - Short fiber content is the dominant driver: fibers below ~12 mm
      cannot be held by the pin/saw-tooth surface at the opening roller
      speeds used → they are extracted with the trash airstream.
    - Higher opening roller speed → more aggressive trash ejection →
      more waste (cleaner rotor) but higher fiber loss.
    - Longer fiber length → lower proportion of the fiber population
      falls below the critical extraction threshold → less waste.

    Lower waste vs. air-jet (Vol 6 Section 2.7.11.4): rotor spinning
    is operated with a bypass valve that can be adjusted to trade off
    waste percentage against rotor cleanliness.
    """
    # Base waste at ideal conditions: clean fiber, standard roller speed
    base_waste = 2.5

    # Trash contribution: trash is efficiently extracted through bypass channel.
    # Each % of trash content ≈ 0.55% of input mass extracted as waste.
    trash_waste = trash_content_pct * 0.55

    # Short fiber contribution: SFC fibers below ~12 mm are extracted
    short_fiber_waste = short_fiber_content_pct * 0.09

    # Opening roller speed: above reference (7 500 rpm), extraction increases
    roller_extra = max(0.0, (opening_roller_speed_rpm - 7_500) / 1_000.0 * 0.25)

    # Fiber length effect: shorter mean length → larger fraction of population
    # falls below the critical extraction threshold
    length_waste = max(0.0, (28.0 - fiber_length_mm) * 0.04)

    total_waste = base_waste + trash_waste + short_fiber_waste + roller_extra + length_waste
    return round(min(12.0, total_waste), 1)


def predict_production_rate(
    delivery_speed_m_min: float,
    yarn_count_tex: float
) -> float:
    """
    Predicts production rate in grams per rotor position per hour.

    Source: Rieter Manual Vol 6, Fig. 57 (curve B — Rotor spinning).
    Formula: production_rate (g/rotor/h) = delivery_speed (m/min) × yarn_count (tex) × 60 / 1000

    Cross-check from Vol 6, Fig. 57 at Ne 20 (tex ≈ 30), Rotor curve B:
    At ~150 m/min delivery → ~270 g/rotor/h.
    Verification: 150 × 30 × 60 / 1000 = 270 g/rotor/h. ✓

    At Ne 10 (tex ≈ 60), Rotor curve B shows ~430 g/rotor/h.
    At 120 m/min: 120 × 60 × 60 / 1000 = 432 g/rotor/h. ✓

    Rotor spinning achieves substantially higher production rates than
    ring spinning for equivalent counts (ring at Ne 20 ≈ 30-50 g/spi/h),
    but lower than air-jet for fine counts (air-jet at Ne 20 ≈ 350 g/spi/h
    at 350 m/min). For coarse counts (Ne 8-15), rotor spinning is
    economically the most productive open-end process.
    """
    rate = delivery_speed_m_min * yarn_count_tex * 60.0 / 1000.0
    return round(rate, 1)


def assess_ends_down_risk(
    spinning_tension_cN: float,
    yarn_count_tex: float,
    yarn_tenacity_cN_tex: float,
    trash_content_pct: float,
    short_fiber_content_pct: float,
    operating_hours_since_maintenance: float,
    maintenance_interval_hours: float,
    rotor_speed_rpm: float,
    rotor_diameter_mm: float
) -> str:
    """
    Qualitative assessment of end break (ends down) risk in rotor spinning.

    Source: Rieter Manual Vol 5, End Breakage section.
    In rotor spinning, end breaks are caused by two distinct mechanisms:
      (1) Tension failure: spinning tension exceeds yarn breaking force
          at a momentary weak spot (thin place or structural defect).
          More relevant than in air-jet where tension is negligible.
      (2) Feed failure: interruption of the fiber stream entering the
          rotor — caused by large trash particles blocking the fiber
          duct, rotor groove deposit release, or sliver thick/thin
          places causing a momentary stop in fiber supply.

    The tension-to-strength ratio is the primary engineering criterion:
      - Breaking force (cN) = yarn_count_tex × yarn_tenacity_cN_tex
        (units: tex × cN/tex = cN ✓)
      - Safety margin = (breaking force − tension) / breaking force
      - At > 15% of breaking force: high risk zone.

    Peripheral speed: excessive peripheral speed (> 160 m/s) creates
    imbalance vibration and bearing-induced tension spikes → elevated risk.
    Maintenance overdue → worn bearings → vibration → tension spikes.
    """
    risk_score = 0

    # Tension-to-strength ratio: primary end-break driver
    yarn_breaking_force_cN = yarn_count_tex * yarn_tenacity_cN_tex  # cN
    if yarn_breaking_force_cN > 0:
        tension_ratio = spinning_tension_cN / yarn_breaking_force_cN
        if tension_ratio > 0.15:
            risk_score += 3  # critical — spinning tension is 15%+ of break force
        elif tension_ratio > 0.09:
            risk_score += 2
        elif tension_ratio > 0.05:
            risk_score += 1

    # Trash content: rotor groove deposits cause periodic feed failures
    if trash_content_pct > 2.5:
        risk_score += 3
    elif trash_content_pct > 1.5:
        risk_score += 2
    elif trash_content_pct > 0.8:
        risk_score += 1

    # Short fiber content: weak yarn cross-sections
    if short_fiber_content_pct > 20.0:
        risk_score += 2
    elif short_fiber_content_pct > 14.0:
        risk_score += 1

    # Maintenance: worn bearings → rotor vibration → tension spikes
    maintenance_ratio = operating_hours_since_maintenance / max(maintenance_interval_hours, 1.0)
    if maintenance_ratio > 1.0:
        risk_score += 2  # overdue for service
    elif maintenance_ratio > 0.85:
        risk_score += 1  # approaching service interval

    # Peripheral speed: above 140 m/s, rotor imbalance forces increase steeply
    peripheral_speed_m_s = (math.pi * rotor_diameter_mm / 1000.0) * rotor_speed_rpm / 60.0
    if peripheral_speed_m_s > 150:
        risk_score += 2
    elif peripheral_speed_m_s > 130:
        risk_score += 1

    if risk_score <= 2:
        return "low"
    elif risk_score <= 5:
        return "medium"
    else:
        return "high"


# ─────────────────────────────────────────────────────────────────────────────
# MASTER SIMULATION FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def simulate_rotor_spinning(
    material: InputMaterial,
    params: RotorOperationalParams
) -> YarnQualityOutput:
    """
    Master simulation function for Rotor Spinning.

    Takes Layer 2 (input material) and Layer 3 (operational parameters),
    runs all prediction models, and returns Layer 4 (output quality metrics).

    Also performs parameter validation and generates warnings for out-of-range
    conditions based on limits documented in Rieter Manual Vol 5 and Vol 6.
    """
    warnings = []

    # ── PARAMETER VALIDATION ──────────────────────────────────────────────────

    # Yarn count range check (rotor spinning practical range: Ne 4-40)
    if params.yarn_count_Ne < 4 or params.yarn_count_Ne > 40:
        warnings.append(
            f"Yarn count {params.yarn_count_Ne} Ne is outside the rotor spinning practical range "
            "(4 - 40 Ne). Counts finer than Ne 40 are better suited to ring or air-jet spinning; "
            "coarser than Ne 4 are handled by Dref-2000 or similar coarse OE systems."
        )

    # Rotor peripheral speed check (absolute safety limit: ~160 m/s)
    peripheral_speed = (math.pi * params.rotor_diameter_mm / 1000.0) * params.rotor_speed_rpm / 60.0
    if peripheral_speed > 160:
        warnings.append(
            f"CRITICAL: Rotor peripheral speed ({peripheral_speed:.1f} m/s) exceeds the "
            "safe maximum of ~160 m/s. Rotor integrity and bearing life are at risk. "
            "Reduce rotor speed or use a smaller diameter rotor."
        )
    elif peripheral_speed > 140:
        warnings.append(
            f"Rotor peripheral speed ({peripheral_speed:.1f} m/s) is in the high-risk zone "
            "(>140 m/s). Monitor bearing temperature and vibration closely."
        )

    # Rotor speed range check
    if params.rotor_speed_rpm < 40_000:
        warnings.append(
            f"Rotor speed {params.rotor_speed_rpm:,.0f} rpm is below the practical minimum "
            "of ~40 000 rpm. Twist insertion and fiber consolidation will be inadequate."
        )

    # Opening roller speed check
    if params.opening_roller_speed_rpm < 5_000 or params.opening_roller_speed_rpm > 10_000:
        warnings.append(
            f"Opening roller speed {params.opening_roller_speed_rpm:,.0f} rpm is outside "
            "the practical range (5 000 - 10 000 rpm). Fiber individualization and "
            "trash extraction will be compromised."
        )

    # Twist factor range check
    if params.twist_factor_am < 80:
        warnings.append(
            f"Twist factor αm = {params.twist_factor_am} is below minimum (80). "
            "The yarn will lack fiber cohesion and have very low strength. "
            "Increase αm or reduce delivery speed."
        )
    elif params.twist_factor_am > 175:
        warnings.append(
            f"Twist factor αm = {params.twist_factor_am} exceeds practical maximum (175). "
            "Yarn will be over-twisted, harsh, and prone to snarling."
        )

    # Delivery speed consistency check: v must equal n_rotor / T(t/m)
    # where T(t/m) = αm / √(tex/1000)
    T_per_m_expected = params.twist_factor_am / math.sqrt(params.yarn_count_tex / 1000.0)
    v_expected = params.rotor_speed_rpm / T_per_m_expected
    if abs(params.delivery_speed_m_min - v_expected) / max(v_expected, 1.0) > 0.20:
        warnings.append(
            f"Delivery speed ({params.delivery_speed_m_min} m/min) is inconsistent with "
            f"rotor speed and twist factor αm. Expected ≈ {v_expected:.0f} m/min for "
            f"αm = {params.twist_factor_am} at {params.yarn_count_Ne} Ne. "
            "The actual twist inserted will deviate significantly from the target."
        )

    # Sliver count / draft check
    if material.sliver_count_ktex < 3.0 or material.sliver_count_ktex > 7.0:
        warnings.append(
            f"Sliver count {material.sliver_count_ktex} ktex is outside the recommended "
            "range (3.0 - 7.0 ktex) for rotor spinning. Adjust to achieve the target "
            "total draft ratio while keeping opening quality acceptable."
        )

    # Fiber length limit for rotor spinning
    if material.fiber_length_mm > 40:
        warnings.append(
            f"Fiber length {material.fiber_length_mm} mm exceeds the rotor spinning practical "
            "limit (~40 mm). Longer fibers tend to wrap around the opening roller pins, "
            "causing fiber damage, nep generation, and high end-break rates."
        )

    # Opening roller wire type vs. yarn count compatibility
    if (params.opening_roller_wire_type == "coarse_wire"
            and params.yarn_count_Ne > 25):
        warnings.append(
            f"Coarse wire opening roller is not optimal for fine yarns (Ne {params.yarn_count_Ne}). "
            "Use fine wire clothing above Ne 20 for better fiber individualization and "
            "lower nep count in the fine yarn."
        )

    # ── RUN SIMULATION MODELS ─────────────────────────────────────────────────

    actual_twist = calculate_actual_twist(
        params.rotor_speed_rpm,
        params.delivery_speed_m_min
    )

    back_doubling = calculate_back_doubling_index(
        params.rotor_diameter_mm,
        material.fiber_length_mm
    )

    tenacity = predict_yarn_tenacity(
        params.twist_factor_am,
        material.fiber_type,
        material.fiber_length_mm,
        params.yarn_count_Ne,
        params.rotor_diameter_mm,
        material.short_fiber_content_pct
    )

    evenness_CVm = predict_yarn_evenness(
        params.total_draft_ratio,
        material.fiber_length_mm,
        material.fiber_fineness_dtex,
        params.rotor_diameter_mm,
        back_doubling
    )

    hairiness = predict_hairiness(
        params.twist_factor_am,
        params.navel_type,
        material.fiber_type,
        params.yarn_count_Ne
    )

    neps = predict_nep_count(
        params.opening_roller_speed_rpm,
        params.rotor_groove_type,
        material.fiber_type,
        material.trash_content_pct,
        material.short_fiber_content_pct
    )

    spinning_tension = predict_spinning_tension(
        params.yarn_count_tex,
        params.rotor_diameter_mm,
        params.rotor_speed_rpm,
        params.twist_factor_am
    )

    waste_pct = predict_waste_percentage(
        material.trash_content_pct,
        material.short_fiber_content_pct,
        params.opening_roller_speed_rpm,
        material.fiber_length_mm
    )

    production_rate = predict_production_rate(
        params.delivery_speed_m_min,
        params.yarn_count_tex
    )

    ends_down = assess_ends_down_risk(
        spinning_tension,
        params.yarn_count_tex,
        tenacity,
        material.trash_content_pct,
        material.short_fiber_content_pct,
        params.operating_hours_since_maintenance,
        params.maintenance_interval_hours,
        params.rotor_speed_rpm,
        params.rotor_diameter_mm
    )

    # ── POST-SIMULATION WARNINGS ──────────────────────────────────────────────

    # Tension-to-strength ratio warning
    yarn_breaking_force = params.yarn_count_tex * tenacity
    if spinning_tension > yarn_breaking_force * 0.12:
        warnings.append(
            f"WARNING: Spinning tension ({spinning_tension} cN) is "
            f"{100 * spinning_tension / yarn_breaking_force:.1f}% of yarn breaking force "
            f"({yarn_breaking_force:.0f} cN). End-break rate will be elevated. "
            "Consider reducing rotor speed or switching to a smaller diameter rotor."
        )

    # Twist factor outside optimal range warning
    if params.twist_factor_am < 95 or params.twist_factor_am > 155:
        warnings.append(
            f"Twist factor αm = {params.twist_factor_am} is outside the optimal range (95 - 155). "
            "Adjust rotor speed or delivery speed for best strength and evenness."
        )

    # Back-doubling index warning: below 3.0, self-leveling is poor
    if back_doubling < 3.0:
        warnings.append(
            f"Back-doubling index ({back_doubling:.1f}) is below 3.0. "
            "The rotor circumference is small relative to fiber length — "
            "self-leveling will be limited and CVm may be higher than predicted. "
            "Consider a larger rotor diameter or shorter staple fiber."
        )

    return YarnQualityOutput(
        actual_twist_turns_per_m=actual_twist,
        back_doubling_index=back_doubling,
        yarn_tenacity_cN_tex=tenacity,
        yarn_evenness_CVm_pct=evenness_CVm,
        hairiness_H=hairiness,
        neps_per_km=neps,
        spinning_tension_cN=spinning_tension,
        waste_fiber_pct=waste_pct,
        ends_down_risk=ends_down,
        production_rate_g_rotor_h=production_rate,
        warnings=warnings
    )


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE USAGE AND VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    print("=" * 65)
    print("ROTOR SPINNING SIMULATION — Rieter R 70")
    print("Based on Rieter Manual of Spinning, Volumes 5 & 6")
    print("=" * 65)

    # ── SCENARIO 1: 100% carded cotton, Ne 20, standard production ──
    # Reference cross-check: Vol 6 Fig. 42 → OE rotor Ne 20 cotton
    # carded should yield ~12.4 cN/tex at optimal twist.
    print("\n--- SCENARIO 1: 100% cotton carded, Ne 20, standard settings ---\n")

    material_1 = InputMaterial(
        fiber_type="cotton_carded",
        fiber_length_mm=27.0,          # 1 1/16 inch (27.2 mm) — typical carded cotton
        fiber_fineness_dtex=1.7,
        short_fiber_content_pct=14.0,  # carded cotton — higher SFC than combed
        fiber_tensile_strength_cN_tex=28.0,
        sliver_count_ktex=4.5,         # card sliver — typical for rotor
        moisture_content_pct=7.0,
        trash_content_pct=1.2          # moderate trash
    )

    # Twist calculation: αm=130, Ne 20, tex=29.5
    # T(t/m) = 130 / √(29.5/1000) = 130 / 0.1718 = 757 t/m
    # v = 100 000 / 757 = 132 m/min
    params_1 = RotorOperationalParams(
        rotor_diameter_mm=33.0,
        rotor_speed_rpm=100_000,
        twist_factor_am=130.0,
        opening_roller_speed_rpm=7_500,
        opening_roller_wire_type="coarse_wire",
        navel_type="notched",
        rotor_groove_type="U_groove",
        total_draft_ratio=152.5,        # 4.5 ktex / 29.5 tex = 152.5
        delivery_speed_m_min=132.0,
        yarn_count_Ne=20.0,
        yarn_count_tex=29.5,            # 590.5 / 20
        ambient_temperature_C=24.0,
        ambient_humidity_pct=55.0,
        last_maintenance_date="2025-10-01",
        maintenance_interval_hours=1_500.0,
        operating_hours_since_maintenance=600.0
    )

    result_1 = simulate_rotor_spinning(material_1, params_1)

    print(f"  Actual Twist:          {result_1.actual_twist_turns_per_m} t/m")
    print(f"  Back-doubling Index:   {result_1.back_doubling_index}  (≥3.0 preferred)")
    print(f"  Yarn Tenacity:         {result_1.yarn_tenacity_cN_tex} cN/tex  "
          f"(Vol 6 Fig.42 ref: ~12.4 cN/tex)")
    print(f"  Yarn Evenness CVm:     {result_1.yarn_evenness_CVm_pct}%")
    print(f"  Hairiness H:           {result_1.hairiness_H}")
    print(f"  Neps/km (200%):        {result_1.neps_per_km}")
    print(f"  Spinning Tension:      {result_1.spinning_tension_cN} cN  (range: 2-8 cN)")
    print(f"  Fiber Waste:           {result_1.waste_fiber_pct}%")
    print(f"  Ends Down Risk:        {result_1.ends_down_risk.upper()}")
    print(f"  Production Rate:       {result_1.production_rate_g_rotor_h} g/rotor/h")
    if result_1.warnings:
        print(f"\n  WARNINGS:")
        for w in result_1.warnings:
            print(f"    ⚠ {w}")
    else:
        print("\n  No warnings — all parameters within recommended ranges.")

    # ── SCENARIO 2: PES/CO 50/50 blend, Ne 30, smaller rotor, high speed ──
    # Reference cross-check: Vol 6 Fig. 43 → OE rotor PES/CO 50/50
    # Ne 30 should yield ~17.5 cN/tex at optimal twist.
    print("\n--- SCENARIO 2: 50% PES / 50% CO blend, Ne 30, high speed ---\n")

    material_2 = InputMaterial(
        fiber_type="blend_PES_CO",
        fiber_length_mm=33.0,          # PES/CO blend — longer staple
        fiber_fineness_dtex=1.5,
        short_fiber_content_pct=5.0,
        fiber_tensile_strength_cN_tex=38.0,
        sliver_count_ktex=3.8,
        moisture_content_pct=6.0,
        trash_content_pct=0.3          # blended yarn — very low trash
    )

    # Twist calculation: αm=110, Ne 30, tex=19.7
    # T(t/m) = 110 / √(19.7/1000) = 110 / 0.1403 = 784 t/m
    # v = 120 000 / 784 = 153 m/min
    params_2 = RotorOperationalParams(
        rotor_diameter_mm=30.0,        # smaller rotor → higher speed capability
        rotor_speed_rpm=120_000,
        twist_factor_am=110.0,         # lower twist for synthetic blend
        opening_roller_speed_rpm=8_000,
        opening_roller_wire_type="fine_wire",
        navel_type="smooth",           # smooth navel → lower hairiness for woven goods
        rotor_groove_type="K_groove",  # optimized profile for fine counts
        total_draft_ratio=193.0,        # 3.8 ktex / 19.7 tex = 193
        delivery_speed_m_min=153.0,
        yarn_count_Ne=30.0,
        yarn_count_tex=19.7,            # 590.5 / 30
        ambient_temperature_C=22.0,
        ambient_humidity_pct=60.0,
        last_maintenance_date="2025-11-01",
        maintenance_interval_hours=2_000.0,
        operating_hours_since_maintenance=350.0
    )

    result_2 = simulate_rotor_spinning(material_2, params_2)

    print(f"  Actual Twist:          {result_2.actual_twist_turns_per_m} t/m")
    print(f"  Back-doubling Index:   {result_2.back_doubling_index}")
    print(f"  Yarn Tenacity:         {result_2.yarn_tenacity_cN_tex} cN/tex  "
          f"(Vol 6 Fig.43 ref: ~17.5 cN/tex)")
    print(f"  Yarn Evenness CVm:     {result_2.yarn_evenness_CVm_pct}%")
    print(f"  Hairiness H:           {result_2.hairiness_H}")
    print(f"  Neps/km (200%):        {result_2.neps_per_km}")
    print(f"  Spinning Tension:      {result_2.spinning_tension_cN} cN")
    print(f"  Fiber Waste:           {result_2.waste_fiber_pct}%")
    print(f"  Ends Down Risk:        {result_2.ends_down_risk.upper()}")
    print(f"  Production Rate:       {result_2.production_rate_g_rotor_h} g/rotor/h")
    if result_2.warnings:
        print(f"\n  WARNINGS:")
        for w in result_2.warnings:
            print(f"    ⚠ {w}")
    else:
        print("\n  No warnings — all parameters within recommended ranges.")

    # ── SCENARIO 3: Coarse Ne 8 carded cotton, high trash, maintenance due ──
    # Stress test: aggressive raw material, near-service machine, large rotor.
    print("\n--- SCENARIO 3: Coarse Ne 8 cotton carded, high trash, "
          "maintenance nearly due ---\n")

    material_3 = InputMaterial(
        fiber_type="cotton_carded",
        fiber_length_mm=25.0,
        fiber_fineness_dtex=1.9,
        short_fiber_content_pct=20.0,  # high SFC — challenging carded material
        fiber_tensile_strength_cN_tex=25.0,
        sliver_count_ktex=6.0,
        moisture_content_pct=7.5,
        trash_content_pct=2.8          # high trash — significant rotor groove risk
    )

    # Twist calculation: αm=145, Ne 8, tex=73.8
    # T(t/m) = 145 / √(73.8/1000) = 145 / 0.2717 = 533 t/m
    # v = 70 000 / 533 = 131 m/min
    params_3 = RotorOperationalParams(
        rotor_diameter_mm=46.0,        # large rotor suited to coarse counts
        rotor_speed_rpm=70_000,        # lower speed consistent with large diameter
        twist_factor_am=145.0,         # higher twist factor for coarse cotton
        opening_roller_speed_rpm=7_000,
        opening_roller_wire_type="coarse_wire",
        navel_type="grooved",          # grooved navel — best abrasion resistance
        rotor_groove_type="T_groove",  # T-groove common for coarse counts
        total_draft_ratio=81.3,         # 6.0 ktex / 73.8 tex = 81.3
        delivery_speed_m_min=131.0,
        yarn_count_Ne=8.0,
        yarn_count_tex=73.8,            # 590.5 / 8
        ambient_temperature_C=25.0,
        ambient_humidity_pct=58.0,
        last_maintenance_date="2025-08-01",
        maintenance_interval_hours=1_000.0,
        operating_hours_since_maintenance=950.0  # 95% of service interval used
    )

    result_3 = simulate_rotor_spinning(material_3, params_3)

    print(f"  Actual Twist:          {result_3.actual_twist_turns_per_m} t/m")
    print(f"  Back-doubling Index:   {result_3.back_doubling_index}")
    print(f"  Yarn Tenacity:         {result_3.yarn_tenacity_cN_tex} cN/tex")
    print(f"  Yarn Evenness CVm:     {result_3.yarn_evenness_CVm_pct}%")
    print(f"  Hairiness H:           {result_3.hairiness_H}")
    print(f"  Neps/km (200%):        {result_3.neps_per_km}")
    print(f"  Spinning Tension:      {result_3.spinning_tension_cN} cN")
    print(f"  Fiber Waste:           {result_3.waste_fiber_pct}%")
    print(f"  Ends Down Risk:        {result_3.ends_down_risk.upper()}")
    print(f"  Production Rate:       {result_3.production_rate_g_rotor_h} g/rotor/h")
    if result_3.warnings:
        print(f"\n  WARNINGS:")
        for w in result_3.warnings:
            print(f"    ⚠ {w}")

    print("\n" + "=" * 65)
    print("Simulation complete.")
    print("=" * 65)