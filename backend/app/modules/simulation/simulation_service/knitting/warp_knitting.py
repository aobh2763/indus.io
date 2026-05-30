"""
Warp Knitting Simulation Module
Process: Knitting > Warp Knitting

Layer 1 — Machine Identity
    Type            : Single-needle-bar warp knitting machine
    Subprocess      : Warp Knitting
    Technology      : Compound-needle or latch-needle warp knitting. Guide bars
                      perform compound swinging-and-shogging movements to lap warp
                      threads as overlaps and underlaps around the needles. Pattern
                      control via profiled chain links, pattern wheels, or modern
                      electronic linear-motor (Karl Mayer EL) direct-drive systems.
                      Positive or negative warp let-off from flanged beams. Fabric
                      drawn-off by take-down rollers.
    Machine classes : Tricot (fine-gauge, high-speed; 28–44 npi; simple 2-bar
                      plain structures; lingerie, apparel); Raschel (coarse-gauge,
                      open-work, multi-bar; 1–32 npi; lace, nets, technical textiles).
                      Also Simplex, Crochet (galloon), and multi-bar lace variants.
    Speed range     : Tricot: 1 500–3 300 courses/min (compound needle, Karl Mayer
                      HKS 2-3 E). Raschel: 400–2 200 courses/min depending on gauge
                      and structure. Double-needle-bar raschel: 250–500 cpm per bar.
    Gauge range     : E 1 (coarsest raschel) to E 44 (finest tricot).
    Fabric scope    : Locknit, sharkskin, queenscord, satin, velour (tricot);
                      power net, sandfly net, pillar-inlay, lace, geotextile
                      structures, spacer fabrics (raschel).

All parameter relationships derived from:
    Spencer, D.J., "Knitting Technology", 3rd edition, Woodhead Publishing,
    Cambridge, 2001. (Chapters 22–27 on warp knitting principles, machine
    classes, structures, fabric geometry, and production science.)

Layer 5: Interdependency and behaviour simulation functions.
These functions take the input woven fabric (Layer 2) and machine operational
parameters (Layer 3) as inputs, and predict output knitted fabric quality
metrics (Layer 4).

Layer 2 note:
    Knitting input = Weaving output.
    The InputWovenFabric dataclass mirrors FabricQualityOutput from the weaving
    simulation modules (plain, twill, satin, jacquard, dobby), using the fields
    that are physically meaningful at the knitting stage. In the textile pipeline,
    woven fabric can serve as a substrate for warp knitting when the warp knitting
    process is used for technical or composite applications (weft-insertion
    geotextiles, stitch-bonded composites, spacer fabrics where a woven base is
    integrated). For standard apparel warp knitting, the relevant fields are the
    yarn-level properties carried through from weaving: fabric weight, cover factor,
    and key quality indicators that define the incoming textile substrate.

        weaving.FabricQualityOutput  →  warp_knitting.InputWovenFabric
        ────────────────────────────────────────────────────────────────
        fabric_width_cm              →  fabric_width_cm
        fabric_weight_g_per_m2       →  fabric_weight_g_per_m2
        cloth_cover_factor           →  cloth_cover_factor
        warp_end_break_risk          →  warp_yarn_quality_risk
        weft_break_risk              →  weft_yarn_quality_risk
        expected_nep_visibility      →  substrate_nep_visibility
        pick_spacing_regularity      →  substrate_regularity
        selvedge_quality             →  substrate_selvedge_quality
        weft_crimp_pct               →  weft_crimp_pct
        warp_crimp_pct               →  warp_crimp_pct
        loom_efficiency_pct          →  upstream_process_efficiency_pct
        actual_production_m_per_hour →  upstream_feed_rate_m_per_hour

    Additional fields required by the warp knitting machine:
        yarn_count_dtex, fiber_type, yarn_tenacity_cN_tex,
        yarn_evenness_CVm_pct, yarn_hairiness_H
"""

import math
from dataclasses import dataclass
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# DATA CLASSES — Layers 2, 3, and 4
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class InputWovenFabric:
    """
    Layer 2 — Input woven fabric / yarn properties for Warp Knitting.

    These fields correspond directly to Layer 4 (FabricQualityOutput) of the
    weaving subprocess simulations, ensuring the two layers are coupled:

        weaving.FabricQualityOutput  →  warp_knitting.InputWovenFabric
    """
    # ── FABRIC GEOMETRY (from weaving Layer 4) ─────────────────────────────
    fabric_width_cm: float              # Input fabric width in cm.
    fabric_weight_g_per_m2: float       # Woven fabric weight in g/m². Informs
                                        # the knitting machine's take-down load.
    cloth_cover_factor: float           # Combined warp+weft cover factor (0–2.0).
                                        # Used to judge substrate density/openness
                                        # for stitch-bonding or weft-insertion work.
    weft_crimp_pct: float               # Weft crimp from weaving stage.
    warp_crimp_pct: float               # Warp crimp from weaving stage.

    # ── SUBSTRATE QUALITY (from weaving Layer 4) ───────────────────────────
    warp_yarn_quality_risk: str         # Mirrors warp_end_break_risk: "low" / "medium" / "high".
                                        # Reflects yarn tenacity and evenness at the warp stage.
    weft_yarn_quality_risk: str         # Mirrors weft_break_risk: "low" / "medium" / "high".
    substrate_nep_visibility: str       # Mirrors expected_nep_visibility:
                                        # "negligible" / "acceptable" / "visible_defects".
    substrate_regularity: str           # Mirrors pick_spacing_regularity:
                                        # "excellent" / "good" / "irregular".
    substrate_selvedge_quality: str     # Mirrors selvedge_quality:
                                        # "clean" / "acceptable" / "faults_likely".

    # ── UPSTREAM PROCESS PERFORMANCE ───────────────────────────────────────
    upstream_process_efficiency_pct: float   # Loom efficiency % from weaving — informs
                                             # overall pipeline OEE calculation.
    upstream_feed_rate_m_per_hour: float     # Weaving actual output in m/h — used for
                                             # line-balancing between loom and knitter.

    # ── YARN PROPERTIES (carried through from spinning via weaving) ─────────
    # These are the yarn-level properties that the warp knitting machine
    # directly depends on, regardless of whether the yarn was previously woven.
    yarn_count_dtex: float              # Yarn linear density in dtex (= tex × 10).
                                        # Tricot fine fabrics: 20–78 dtex (nylon/polyester).
                                        # Raschel coarse: 80–6 000 dtex.
    fiber_type: str                     # "nylon", "polyester", "elastane",
                                        # "cotton", "viscose", "aramid", "glass", "blend_PES_CO"
    yarn_tenacity_cN_tex: float         # Yarn tenacity in cN/tex. Filaments: 35–65 cN/tex.
                                        # Spun cotton: 12–18 cN/tex.
    yarn_evenness_CVm_pct: float        # Mass CV%. Filament: < 1%; Spun: 10–16%.
                                        # High CVm% → course irregularity (barre).
    yarn_hairiness_H: float             # Uster hairiness (H). Filament: < 1.0;
                                        # Spun: 4–10. High hairiness → guide-eye wear,
                                        # thread entanglement, guide blockage.


@dataclass
class WarpKnittingOperationalParams:
    """
    Layer 3 — Operational parameters for Warp Knitting.

    Source: Spencer, D.J., Knitting Technology, 3rd ed. (2001), Ch. 23–27.
    """
    # ── MACHINE CLASS AND GAUGE ──────────────────────────────────────────────
    machine_class: str              # "tricot" or "raschel".
                                    # Tricot: fine-gauge, compound needle, high-speed,
                                    #   short yarn path, fabric drawn at ~90° to needle bar.
                                    # Raschel: wide gauge range, latch or compound needle,
                                    #   fabric drawn almost parallel to needle bar (~120–160°),
                                    #   strong take-down tension, suited to open structures.
    gauge_E: int                    # Machine gauge in needles per inch (npi).
                                    # Tricot: E 20–E 44 (typical E 28 or E 32).
                                    # Raschel: E 1–E 32.
    needle_type: str                # "compound" or "latch".
                                    # Compound needles achieve 3 300 cpm without metal fatigue.
                                    # Latch needles are limited and have shorter life.
    knitting_width_cm: float        # Active needle-bar knitting width in cm.
                                    # Tricot: up to 660 cm (260 inches). Raschel: varies.

    # ── GUIDE BARS AND LAPPING ────────────────────────────────────────────────
    number_of_guide_bars: int       # Number of active guide bars.
                                    # Standard tricot: 2. Multi-bar raschel: up to 78.
                                    # Spencer Ch. 23: minimum 2 for commercial structures.
    threading_density: str          # "full" (1 thread per guide) or "half" (every other guide)
                                    # or "pattern" (partly-threaded for nets/openwork).
    underlap_span_needles: int      # Number of needle spaces covered by the underlap of the
                                    # main (front) guide bar. Defines structure family:
                                    #   1 = tricot (1×1), 2 = cord (2×1), 3 = satin (3×1),
                                    #   4 = velvet (4×1), 6–8 = velour/pile.
                                    # Spencer Ch. 25: each +1 space → heavier, more opaque fabric.
    lapping_type: str               # Structure produced by the guide bar pattern.
                                    # "locknit", "reverse_locknit", "sharkskin", "queenscord",
                                    # "tricot", "satin", "atlas", "pillar_inlay", "net",
                                    # "velour", "power_net"
    overlap_direction: str          # "closed_lap" or "open_lap".
                                    # Open-lap pillar stitches can unrove from end knitted last.
                                    # Closed-lap pillar stitches are used on crochet machines.
    pattern_control: str            # "chain_links", "pattern_wheels", or "electronic".
                                    # Electronic (Karl Mayer EL linear motor): +30% speed,
                                    # 12-needle shog possible in E 28 (Spencer Ch. 23.8).

    # ── MACHINE SPEED AND LET-OFF ─────────────────────────────────────────────
    machine_speed_cpm: float        # Knitting speed in courses per minute (cpm).
                                    # Compound-needle tricot max: 3 300 cpm (HKS 2-3 E).
                                    # Raschel (single-needle bar): 400–2 200 cpm.
                                    # Raschel E 40 finest: 1 900–2 200 cpm.
                                    # Double-needle-bar raschel: 250–500 cpm per bar.
    let_off_type: str               # "positive_automatic" or "negative_friction".
                                    # Karl Mayer computer-controlled positive let-off:
                                    # maintains uniform run-in from beam to needles.
                                    # Negative: belt-brake; susceptible to tension spikes.
    run_in_ratio_front_back: float  # Run-in ratio (front bar : back bar).
                                    # Locknit: 3:4; Sharkskin: 5:3; Queenscord: 9:4 (Spencer p.321).
                                    # Governs how much yarn is fed to each bar per course.
    warp_tension_cN_per_end: float  # Warp tension per end in cN during knitting.
                                    # Filament (nylon/polyester): 3–12 cN/end.
                                    # Spun cotton/staple: 8–20 cN/end.
    take_down_tension_cN_per_cm: float  # Fabric take-down tension in cN/cm width.
                                        # Tricot: low (~8–20 cN/cm, gentle fabric angle).
                                        # Raschel: high (~30–80 cN/cm, steep fabric angle).
                                        # High take-down tension essential for open-work.

    # ── STITCH AND LOOP GEOMETRY ─────────────────────────────────────────────
    stitch_length_mm: float         # Loop/stitch length in mm.
                                    # Fine tricot (22 dtex polyester, E 44): ~0.8–1.2 mm.
                                    # Standard locknit (40 den nylon, E 28): ~1.4–2.0 mm.
                                    # Coarse raschel: 2.5–5.0 mm.
                                    # Spencer Ch. 22: stitch length is the fundamental unit;
                                    # all fabric dimensions and weight depend on it.
    sinker_depth_mm: float          # Sinker loop depth (knock-over / hold-down position) in mm.
                                    # Tricot: fixed sinker bellies hold loops gently.
                                    # Raschel: sinkers withdraw; needle trick-plate acts
                                    # as knock-over surface.
    shed_swing_angle_deg: float     # Guide bar swing arc (degrees of cam-shaft revolution).
                                    # Standard: ~120–150°. Reduces as speed increases.

    # ── AMBIENT AND MAINTENANCE ───────────────────────────────────────────────
    ambient_temperature_C: float    # Room temperature in °C. Synthetic filaments:
                                    # sensitive to humidity for static control.
    ambient_humidity_pct: float     # Relative humidity %. Synthetic warp: 50–65%.
                                    # Cotton/viscose: 65–75%.
    last_maintenance_date: str      # ISO date string, e.g. "2025-10-01".
    maintenance_interval_hours: float   # Recommended service interval in hours.
                                        # Guide-bar chain links, needle bar, sinker bars,
                                        # tension rails, beam shafts.
    operating_hours_since_maintenance: float  # Hours since last full service.


@dataclass
class WarpKnittedFabricOutput:
    """
    Layer 4 — Predicted output quality metrics for Warp Knitting.
    """
    # Fabric structure metrics
    fabric_width_finished_cm: float         # Estimated finished fabric width after take-off.
    courses_per_cm: float                   # Wale-direction density (courses/cm).
    wales_per_cm: float                     # Course-direction density (wales/cm).
    stitch_density_per_cm2: float           # Total loop density = cpc × wpc.
    fabric_weight_g_per_m2: float           # Predicted knitted fabric weight in g/m².
    tightness_factor: float                 # TF = √dtex / stitch_length_mm.
                                            # Spencer Ch. 22: TF 1.4–1.5 for plain weft knit;
                                            # warp knit typically 1.0–1.6 depending on structure.

    # Structural quality metrics
    loop_formation_quality: str             # "good", "marginal", or "poor".
    yarn_tension_balance: str               # "balanced", "tight_front", "tight_back", or "unbalanced".
    underlap_regularity: str                # "uniform", "minor_variation", or "irregular".
    fabric_stability: str                   # "stable", "moderate", or "unstable".
                                            # Single guide bar = unstable (Spencer Ch. 23).

    # Appearance metrics
    surface_nep_visibility: str             # "negligible", "acceptable", or "visible_defects".
    barre_risk: str                         # "low", "moderate", or "high".
                                            # Barre = horizontal streaks from course-length variation.
    selvedge_security: str                  # "secure", "borderline", or "at_risk".
                                            # Raschels need extra selvedge threads (Spencer Ch. 24.3.2).

    # Structure-specific quality
    cover_adequacy: str                     # "excellent", "acceptable", or "insufficient".
    extensibility_rating: str               # "high", "moderate", or "low".
                                            # Locknit: high; Queenscord: low (Spencer Ch. 25).
    fabric_curling_tendency: str            # "none", "mild", or "significant".
                                            # Locknit tends to curl toward face at top/bottom.

    # Production metrics
    theoretical_production_m_per_hour: float    # Theoretical fabric output in m/h.
    machine_efficiency_pct: float               # Estimated machine efficiency % (accounting
                                                # for yarn breaks, guide blockages, etc.)
    actual_production_m_per_hour: float         # Effective output = theoretical × efficiency.

    warnings: list                          # List of warning messages for out-of-range conditions.


# ─────────────────────────────────────────────────────────────────────────────
# CORE SIMULATION FUNCTIONS — Layer 5
# Each function models one specific cause-effect relationship from the manual.
# ─────────────────────────────────────────────────────────────────────────────

def predict_courses_per_cm(
    stitch_length_mm: float,
    yarn_count_dtex: float,
    fiber_type: str,
    let_off_type: str
) -> float:
    """
    Predicts courses per cm (cpc) in the finished fabric.

    Source: Spencer, Knitting Technology, Ch. 22.5 (Knitted Fabric Geometry).
    Munden's law: cpc = kc / l, where l is stitch length and kc is a
    structure/fibre-dependent constant (kc ≈ 5.0–5.5 for plain weft knit).
    For warp knit, the relationship is analogous but influenced by:
    - Stitch length (primary determinant, Spencer Ch. 22.1).
    - Yarn diameter (finer yarns pack more courses per cm at the same l).
    - Let-off type: positive let-off maintains constant l → uniform cpc.
      Negative let-off introduces tension spikes → cpc variation (barre).
    - Fibre type: thermoplastic filaments (nylon, polyester) heat-set tightly,
      giving more stable cpc after relaxation than spun staple yarns.

    Calibrated: locknit on 40 den nylon (≈ 44 dtex), E 28, stitch length 1.6 mm
    → ~37 courses/inch ≈ 14.6 cpc finished (Spencer Ch. 25.3).
    """
    if stitch_length_mm <= 0:
        return 0.0

    # Base kc (analogous to Munden's kc for warp knit structures)
    kc = 14.5  # calibrated to locknit / tricot reference

    # Fibre factor: thermoplastics relax tightly; cellulosics swell more
    if "nylon" in fiber_type.lower() or "polyester" in fiber_type.lower():
        fiber_factor = 1.0
    elif "elastane" in fiber_type.lower():
        fiber_factor = 1.15   # elastic yarn contracts, packing more courses
    elif "viscose" in fiber_type.lower() or "cotton" in fiber_type.lower():
        fiber_factor = 0.92   # greater swell reduces packing
    elif "aramid" in fiber_type.lower() or "glass" in fiber_type.lower():
        fiber_factor = 0.95
    else:
        fiber_factor = 0.97

    # Let-off penalty: negative let-off causes periodic run-in variations
    let_off_factor = 1.0 if let_off_type == "positive_automatic" else 0.96

    cpc = (kc / stitch_length_mm) * fiber_factor * let_off_factor
    return round(max(1.0, cpc), 2)


def predict_wales_per_cm(
    gauge_E: int,
    stitch_length_mm: float,
    fabric_width_cm: float,
    knitting_width_cm: float,
    underlap_span_needles: int
) -> float:
    """
    Predicts wales per cm (wpc) in the finished fabric.

    Source: Spencer, Knitting Technology, Ch. 22.5, Ch. 25.
    Wales/cm at the machine = gauge_E × (needles per cm) = gauge_E / 2.54.
    After relaxation, fabric contracts in width (shrinkage):
    - Locknit (28 gauge, 40 den nylon): finishes at 37+ wales/inch ≈ 14.6 wpc
      from a 168-inch machine knitting width → finished width 92–100 inches
      (Spencer Ch. 25.3). Width shrinkage ≈ 20–30% for locknit;
      Queenscord: 1–6% only (very rigid).
    - Longer underlaps → more horizontal underlap floats → greater width
      extensibility → more width shrinkage during relaxation.
    - Finer gauge (more needles/cm) → more wales/cm at same shrinkage.
    """
    if knitting_width_cm <= 0:
        return 0.0

    # Needles per cm = gauge in needles per inch / 2.54 cm/inch
    needles_per_cm = gauge_E / 2.54

    # Width shrinkage during relaxation (Spencer Ch. 25):
    # Longer underlap → higher extensibility → more width shrinkage
    # 1×1 tricot: ~10%; locknit (2×1): ~20–30%; satin (3×1): ~30–35%.
    shrinkage_map = {1: 0.10, 2: 0.25, 3: 0.32, 4: 0.35, 6: 0.42, 8: 0.50}
    base_shrinkage = shrinkage_map.get(underlap_span_needles,
                                       min(0.50, 0.10 + underlap_span_needles * 0.06))

    # Finished width after shrinkage
    finished_width_cm = knitting_width_cm * (1.0 - base_shrinkage)

    # Total wales = needles across finished width
    total_wales = needles_per_cm * knitting_width_cm
    wpc = total_wales / finished_width_cm

    return round(max(1.0, wpc), 2)


def predict_fabric_weight(
    yarn_count_dtex: float,
    stitch_length_mm: float,
    courses_per_cm: float,
    wales_per_cm: float,
    number_of_guide_bars: int,
    threading_density: str
) -> float:
    """
    Predicts warp knitted fabric weight in g/m².

    Source: Spencer, Knitting Technology, Ch. 25.3 (Locknit examples).
    Spencer gives: 28-gauge locknit from 40 den nylon (≈ 44 dtex) → ~82 g/m².
    From 70 den nylon → ~152 g/m².
    General formula (analogous to weft knit):
        weight (g/m²) = stitch_density × stitch_length × linear_density
                      × number_of_yarn_systems
    where stitch_density = cpc × wpc (loops/cm²),
    stitch_length is in cm (l_cm = l_mm / 10),
    linear_density is in g/cm (dtex / 1 000 000 g/cm),
    and there are (number_of_guide_bars × threading_factor) yarn systems.

    Simplified to:
        weight = cpc × wpc × (l_mm/10) × (dtex/1e6) × 1e4 × bars × threading
    where × 1e4 converts g/cm² to g/m².
    """
    threading_factor = 1.0 if threading_density == "full" else 0.5

    stitch_density = courses_per_cm * wales_per_cm          # loops/cm²
    l_cm = stitch_length_mm / 10.0                          # cm
    linear_density_g_per_cm = yarn_count_dtex / 1_000_000   # g/cm

    weight_g_per_cm2 = (stitch_density * l_cm * linear_density_g_per_cm
                        * number_of_guide_bars * threading_factor)
    weight_g_per_m2 = weight_g_per_cm2 * 10_000

    return round(max(5.0, weight_g_per_m2), 1)


def predict_tightness_factor(
    yarn_count_dtex: float,
    stitch_length_mm: float
) -> float:
    """
    Calculates Tightness Factor (TF) for the warp knitted structure.

    Source: Spencer, Knitting Technology, Ch. 22.6 (Tightness Factor).
    Munden's Tightness Factor (originally termed 'cover factor'):
        TF = √tex / l    (SI units, l in mm, tex = dtex/10)
    or equivalently:
        TF = √dtex / (l × √10)

    Spencer Ch. 22.6: for plain weft knit from worsted yarn,
    TF ranges 1.4–1.5 for typical commercial structures.
    Warp knit structures vary:
    - Tight locknit (E 28, 40 den, l ≈ 1.4 mm): TF ≈ 1.5
    - Open structures (larger l, finer yarn): TF < 1.0
    - Very tight / pile structures (short l, heavy yarn): TF > 2.0
    Low TF → open, light, extensible fabric.
    High TF → dense, heavy, stable fabric.
    """
    if stitch_length_mm <= 0:
        return 0.0
    tex = yarn_count_dtex / 10.0
    tf = math.sqrt(tex) / stitch_length_mm
    return round(tf, 3)


def assess_loop_formation_quality(
    machine_speed_cpm: float,
    machine_class: str,
    needle_type: str,
    yarn_tenacity_cN_tex: float,
    yarn_evenness_CVm_pct: float,
    warp_tension_cN_per_end: float,
    yarn_count_dtex: float,
    gauge_E: int,
    operating_hours_since_maintenance: float,
    maintenance_interval_hours: float
) -> str:
    """
    Assesses loop formation quality at the needle head.

    Source: Spencer, Knitting Technology, Ch. 22.8 (Needle bounce and
    high-speed knitting), Ch. 24.2.1 (Knitting cycle of bearded needle
    tricot), Ch. 24.3.3 (Raschel knitting action).

    Key factors:
    - Compound needles (Ch. 24.4): short, simple action; achieve 3 300 cpm
      without metal fatigue or loop distortion; superior to latch or bearded.
    - Latch needles: longer latches needed on raschel to avoid overlap landing
      below open latch; limited speed due to latch bounce.
    - High machine speed → less dwell time for overlap wrap → missed overlaps.
    - Low yarn tenacity → breakage during needle head pass.
    - High CVm% → weak places → inconsistent loop formation.
    - High warp tension relative to yarn strength → tension spikes at overlap.
    - Overdue maintenance → worn needle hooks, bent guide holes → poor lapping.
    """
    risk = 0

    # Needle type × speed compatibility
    speed_limit = {"compound": 3300, "latch": 2200, "bearded": 1500}
    limit = speed_limit.get(needle_type.lower(), 2000)
    if machine_speed_cpm > limit:
        risk += 3
    elif machine_speed_cpm > limit * 0.85:
        risk += 1

    # Yarn strength check
    if yarn_tenacity_cN_tex < 10.0:
        risk += 3
    elif yarn_tenacity_cN_tex < 14.0:
        risk += 1

    # Evenness check (CVm%)
    if yarn_evenness_CVm_pct > 14.0:
        risk += 2
    elif yarn_evenness_CVm_pct > 10.0:
        risk += 1

    # Warp tension vs yarn strength (approximate safe ratio)
    # Single-end break force estimate: tenacity (cN/tex) × count (tex)
    tex = yarn_count_dtex / 10.0
    break_force_cN = yarn_tenacity_cN_tex * tex
    if break_force_cN > 0:
        tension_ratio = warp_tension_cN_per_end / break_force_cN
        if tension_ratio > 0.30:
            risk += 2
        elif tension_ratio > 0.20:
            risk += 1

    # Maintenance
    maint_ratio = operating_hours_since_maintenance / max(1.0, maintenance_interval_hours)
    if maint_ratio > 1.0:
        risk += 2
    elif maint_ratio > 0.85:
        risk += 1

    if risk <= 2:
        return "good"
    elif risk <= 5:
        return "marginal"
    else:
        return "poor"


def assess_yarn_tension_balance(
    run_in_ratio_front_back: float,
    let_off_type: str,
    warp_tension_cN_per_end: float,
    yarn_tenacity_cN_tex: float,
    yarn_count_dtex: float,
    number_of_guide_bars: int
) -> str:
    """
    Assesses balance of yarn tension between guide bars.

    Source: Spencer, Knitting Technology, Ch. 25 (Rules governing two-bar
    structures, p. 313–314) and Ch. 22.3 (Warp let-off).
    - Front bar dominates both face and back of fabric (Spencer Ch. 25.1 rule 1).
    - Each guide bar has independent run-in from its own beam and let-off.
    - Run-in ratio between bars defines the structure (locknit = 3:4, etc.).
    - Positive let-off → each bar maintains its set run-in accurately.
    - Negative let-off → tension spikes → unequal run-in → one bar dominates.
    - Very high front-bar tension → loop inclination and unbalanced fabric.
    - More than 2 bars with negative let-off → compounding tension imbalance.
    """
    score = 0

    # Let-off type
    if let_off_type == "positive_automatic":
        score += 3
    else:
        score += 0  # negative: inherent imbalance

    # Run-in ratio extremes: balanced structures have ratios near 1:1 or
    # well-defined standard ratios (locknit 3:4 = 0.75; sharkskin 5:3 = 1.67)
    if 0.5 <= run_in_ratio_front_back <= 2.0:
        score += 2
    elif 0.3 <= run_in_ratio_front_back <= 3.0:
        score += 1
    else:
        score += 0  # extreme ratio → likely imbalance

    # Warp tension vs yarn strength
    tex = yarn_count_dtex / 10.0
    break_force_cN = yarn_tenacity_cN_tex * tex
    if break_force_cN > 0:
        if warp_tension_cN_per_end / break_force_cN < 0.20:
            score += 2
        elif warp_tension_cN_per_end / break_force_cN < 0.30:
            score += 1

    # More bars → more complex balance requirement
    if number_of_guide_bars > 4:
        score -= 1
    if number_of_guide_bars > 12:
        score -= 1

    if score >= 6:
        return "balanced"
    elif score >= 4:
        return "tight_front"  # front bar dominance (normal for locknit)
    elif score >= 2:
        return "tight_back"
    else:
        return "unbalanced"


def assess_underlap_regularity(
    pattern_control: str,
    machine_speed_cpm: float,
    let_off_type: str,
    operating_hours_since_maintenance: float,
    maintenance_interval_hours: float,
    yarn_evenness_CVm_pct: float
) -> str:
    """
    Assesses underlap regularity (uniformity of the floats on the technical back).

    Source: Spencer, Knitting Technology, Ch. 23.6 (Pattern mechanism),
    Ch. 23.8 (Electronic guide bar control system).
    - Chain links: can produce late/early-timed shog if links not accurately
      ground (Spencer Ch. 23.7). Too sharp a gradient → early timing;
      too gradual → late timing → irregular underlaps.
    - Pattern wheels: accurate and smooth at high speeds; economical for long runs.
    - Electronic (Karl Mayer EL): 1/100 mm increments; 30% higher speeds than
      chain links; eliminated timing-related shog irregularity.
    - High speed → less time for shogging mechanism to settle → more variation.
    - High yarn CVm% → variable knitting tension → irregular underlap length.
    - Overdue maintenance → worn chain links, stiff guide-bar bearings.
    """
    score = 0

    if pattern_control == "electronic":
        score += 4
    elif pattern_control == "pattern_wheels":
        score += 3
    else:  # chain_links
        score += 1

    if let_off_type == "positive_automatic":
        score += 2

    if machine_speed_cpm <= 1500:
        score += 2
    elif machine_speed_cpm <= 2500:
        score += 1

    if yarn_evenness_CVm_pct < 8.0:
        score += 1

    maint_ratio = operating_hours_since_maintenance / max(1.0, maintenance_interval_hours)
    if maint_ratio < 0.5:
        score += 1
    elif maint_ratio > 1.0:
        score -= 2

    if score >= 7:
        return "uniform"
    elif score >= 4:
        return "minor_variation"
    else:
        return "irregular"


def assess_fabric_stability(
    number_of_guide_bars: int,
    underlap_span_needles: int,
    lapping_type: str,
    threading_density: str,
    overlap_direction: str
) -> str:
    """
    Assesses structural stability of the warp knitted fabric.

    Source: Spencer, Knitting Technology, Ch. 23.12 (Direction of lapping)
    and Ch. 23 general principles.
    - Single guide bar → always unstable: loop inclination from unbalanced
      underlap tension (Spencer Ch. 23.12 cohesive single bar structures).
    - Two bars underlapping in opposition → balanced tension at needle head
      → upright loops → stable structure (Spencer Ch. 23.12 rule 2).
    - Longer underlap (satin, velvet) → floats lie more horizontally → less
      stable than tight tricot/locknit structures.
    - Partly-threaded bars → open-work → net pillars → dimensionally unstable
      unless well-designed (Spencer Ch. 26).
    - Open lap vs closed lap: closed lap → cannot unrove → more secure.
    """
    score = 0

    if number_of_guide_bars == 1:
        return "unstable"  # Spencer Ch. 23: always unstable

    if number_of_guide_bars >= 2:
        score += 3  # two bars underlapping in opposition → balanced

    # Underlap length: shorter → more stable
    if underlap_span_needles <= 2:
        score += 2
    elif underlap_span_needles <= 4:
        score += 1
    else:
        score -= 1   # long floats reduce stability

    # Lapping type stability
    stable_types = {"locknit", "queenscord", "tricot", "sharkskin", "pillar_inlay"}
    if lapping_type.lower() in stable_types:
        score += 2

    # Threading density: full = maximum cohesion
    if threading_density == "full":
        score += 1
    elif threading_density == "pattern":
        score -= 1  # open-work areas reduce stability

    # Closed lap: cannot unrove → secures structure
    if overlap_direction == "closed_lap":
        score += 1

    if score >= 7:
        return "stable"
    elif score >= 4:
        return "moderate"
    else:
        return "unstable"


def assess_barre_risk(
    let_off_type: str,
    yarn_evenness_CVm_pct: float,
    machine_speed_cpm: float,
    operating_hours_since_maintenance: float,
    maintenance_interval_hours: float,
    fiber_type: str
) -> str:
    """
    Assesses risk of barre (horizontal streaks) in the knitted fabric.

    Source: Spencer, Knitting Technology, Ch. 22.1–22.2 (Loop length control).
    Spencer Ch. 22.2: course-length variation between feeds, or within the
    same feed from one machine revolution to the next, causes horizontal
    barriness. This is especially visible with continuous filament yarns.
    Causes:
    - Negative let-off: tension spikes → run-in variation → barre.
    - High yarn CVm%: mass variation → variable knitting tension → barre.
    - High machine speed: less time for yarn tension to equilibrate.
    - Worn machine elements: eccentric beam shafts, stiff tension rails.
    - Continuous filament yarns: barre more visible than with spun yarns
      because filaments reflect light in uniform sheets.
    """
    risk = 0

    if let_off_type == "negative_friction":
        risk += 3  # inherent periodic tension variation

    if yarn_evenness_CVm_pct > 10.0:
        risk += 2
    elif yarn_evenness_CVm_pct > 5.0:
        risk += 1

    if machine_speed_cpm > 2500:
        risk += 1

    maint_ratio = operating_hours_since_maintenance / max(1.0, maintenance_interval_hours)
    if maint_ratio > 1.0:
        risk += 2
    elif maint_ratio > 0.85:
        risk += 1

    # Filament yarns: barre more visible than spun
    if any(f in fiber_type.lower() for f in ("nylon", "polyester", "elastane")):
        risk += 1

    if risk <= 2:
        return "low"
    elif risk <= 4:
        return "moderate"
    else:
        return "high"


def assess_surface_nep_visibility(
    substrate_nep_visibility: str,
    yarn_count_dtex: float,
    underlap_span_needles: int,
    fiber_type: str
) -> str:
    """
    Assesses nep visibility on the knitted fabric surface.

    Source: Spencer, Knitting Technology, Ch. 25 (plain tricot structures).
    - Warp knitting loops press neps into intersections; long underlaps float
      neps onto the technical back surface where they are more visible.
    - Finer yarns (lower dtex) → neps appear proportionally larger.
    - Spun-yarn neps from the weaving stage persist into knitting;
      filament yarns have no neps.
    - Longer underlap floats expose more yarn surface → more nep visibility.
    """
    # Base from weaving substrate
    base_map = {"negligible": 0, "acceptable": 1, "visible_defects": 3}
    base = base_map.get(substrate_nep_visibility.lower(), 1)

    # Filament fibers have no neps
    if any(f in fiber_type.lower() for f in ("nylon", "polyester", "elastane",
                                              "glass", "aramid")):
        return "negligible"

    # Spun/staple fiber nep assessment
    float_penalty = max(0, underlap_span_needles - 2)  # longer floats expose neps
    fine_penalty = 1 if yarn_count_dtex < 50 else 0    # fine yarns → neps relatively larger

    total = base + float_penalty + fine_penalty

    if total <= 1:
        return "negligible"
    elif total <= 3:
        return "acceptable"
    else:
        return "visible_defects"


def assess_selvedge_security(
    machine_class: str,
    threading_density: str,
    lapping_type: str,
    take_down_tension_cN_per_cm: float,
    yarn_tenacity_cN_tex: float,
    substrate_selvedge_quality: str
) -> str:
    """
    Assesses selvedge security of the warp knitted fabric.

    Source: Spencer, Knitting Technology, Ch. 24.3.2 (Raschel description):
    'Additional warp threads may be supplied at the selvedges to ensure that
    these needles knit fabric overlaps, otherwise a progressive press-off
    of loops may occur.' (Spencer p. 303).
    Tricot: sinkers hold selvedge loops between overlaps; generally secure.
    Raschel: high take-down tension and steep fabric angle can stress selvedges.
    Open/net structures: selvedge needles may receive only one overlapped thread
    and are vulnerable.
    Partly-threaded bars with net lapping may need dedicated selvedge bars.
    """
    score = 0

    # Machine class
    if machine_class.lower() == "tricot":
        score += 3  # gentle sinker action, fabric drawn nearly horizontally
    else:
        score += 1  # raschel: high take-down tension stresses selvedge

    # Threading: full sett = every needle lapped = secure selvedge
    if threading_density == "full":
        score += 2
    elif threading_density == "half":
        score += 1
    else:  # pattern/partly-threaded → some needles may miss
        score += 0

    # Lapping type: pillar stitch / locknit provides continuous selvedge overlap
    stable_types = {"locknit", "sharkskin", "queenscord", "tricot", "pillar_inlay"}
    if lapping_type.lower() in stable_types:
        score += 1
    elif lapping_type.lower() in {"net", "power_net"}:
        score -= 1

    # Take-down tension: high tension risks pulling selvedge loops
    if take_down_tension_cN_per_cm > 60:
        score -= 2
    elif take_down_tension_cN_per_cm > 40:
        score -= 1

    # Yarn tenacity
    if yarn_tenacity_cN_tex < 10.0:
        score -= 2
    elif yarn_tenacity_cN_tex < 15.0:
        score -= 1

    # Carry forward selvedge quality from substrate (weaving stage)
    selvedge_map = {"clean": 1, "acceptable": 0, "faults_likely": -1}
    score += selvedge_map.get(substrate_selvedge_quality.lower(), 0)

    if score >= 5:
        return "secure"
    elif score >= 2:
        return "borderline"
    else:
        return "at_risk"


def assess_cover_adequacy(
    tightness_factor: float,
    lapping_type: str,
    threading_density: str,
    number_of_guide_bars: int
) -> str:
    """
    Assesses fabric cover adequacy (opacity vs open-work as intended).

    Source: Spencer, Knitting Technology, Ch. 25 (two-bar structures).
    Spencer Ch. 25.2: two-bar tricot has poor cover.
    Locknit (Ch. 25.3): longer front-bar underlaps improve cover and opacity.
    Sharkskin (Ch. 25.5): even greater rigidity and heavier cover.
    Open structures (nets, power net): cover adequacy judged differently —
    'adequate' means the open holes are the intended design.
    TF governs cover in the same way as for weft knit structures.
    """
    # Open-work structures are intentionally low-cover — judge as "excellent" by design
    open_types = {"net", "power_net", "pillar_inlay"}
    if lapping_type.lower() in open_types and threading_density in ("half", "pattern"):
        return "excellent"  # intentional openwork

    # Closed / dense structures
    if tightness_factor >= 1.5:
        base = "excellent"
    elif tightness_factor >= 1.2:
        base = "acceptable"
    else:
        base = "insufficient"

    # Locknit: front-bar longer underlaps improve cover (Spencer Ch. 25.3)
    if lapping_type.lower() in {"locknit", "sharkskin", "queenscord"}:
        if base == "acceptable":
            base = "excellent"

    # More guide bars → more yarn → more cover
    if number_of_guide_bars >= 4 and base == "acceptable":
        base = "excellent"

    return base


def assess_extensibility(
    lapping_type: str,
    underlap_span_needles: int,
    yarn_count_dtex: float,
    fiber_type: str
) -> str:
    """
    Assesses fabric extensibility rating.

    Source: Spencer, Knitting Technology, Ch. 25 (two-bar plain tricot
    structures).
    Spencer Ch. 25.3 (Locknit): 'The longer underlaps of the front bar on
    the back of the fabric improve extensibility.' 'Elasticity makes it
    particularly suitable for lingerie.'
    Spencer Ch. 25.6 (Queenscord): 'Even greater rigidity...shrinkage of
    only 1–6 per cent.'
    General rule: longer underlap → more horizontal float → more extensibility
    in the wale direction.
    Elastane-containing structures: dramatically higher extensibility.
    Power net: 75–85% length extension, 65–75% width extension (Spencer Ch. 28.10).
    """
    # Elastane-based structures
    if "elastane" in fiber_type.lower():
        return "high"

    # Power net (Ch. 28.10): very high extensibility
    if lapping_type.lower() == "power_net":
        return "high"

    # Standard lapping type extensibility
    high_ext = {"locknit", "satin", "velour", "atlas"}
    low_ext = {"queenscord", "pillar_inlay", "sharkskin"}

    if lapping_type.lower() in high_ext or underlap_span_needles >= 3:
        return "high"
    elif lapping_type.lower() in low_ext or underlap_span_needles == 1:
        return "low"
    else:
        return "moderate"


def assess_fabric_curling(
    lapping_type: str,
    number_of_guide_bars: int,
    overlap_direction: str
) -> str:
    """
    Assesses tendency for the fabric to curl at its edges.

    Source: Spencer, Knitting Technology, Ch. 25.3 (Locknit):
    'Its tendency to curl towards the face at the top and bottom, and towards
    the back at the sides, can be reduced by heat setting.'
    Curling arises from unbalanced loop tension at the fabric edges.
    - Single guide bar structures: most prone (Spencer Ch. 23.12).
    - Two-bar structures underlapping in opposition: balanced → less curl.
    - Queenscord: pillar stitch ties in back-bar underlaps → very stable.
    - Closed lap: eliminates the unravel-direction imbalance.
    """
    if number_of_guide_bars == 1:
        return "significant"

    low_curl = {"queenscord", "sharkskin", "pillar_inlay", "net", "power_net"}
    mid_curl = {"locknit", "satin", "atlas", "velour"}

    if lapping_type.lower() in low_curl:
        return "none"
    elif lapping_type.lower() in mid_curl:
        return "mild"

    # Closed lap: reduces open-edge imbalance
    if overlap_direction == "closed_lap":
        return "mild"

    return "mild"


def predict_machine_efficiency(
    loop_formation_quality: str,
    underlap_regularity: str,
    selvedge_security: str,
    barre_risk: str,
    machine_class: str,
    number_of_guide_bars: int,
    operating_hours_since_maintenance: float,
    maintenance_interval_hours: float
) -> float:
    """
    Estimates machine efficiency % for production planning.

    Source: Spencer, Knitting Technology, Ch. 30.11 (Circular warp knitting):
    '...at 80 per cent efficiency, approximately 100 metres of fabric will be
    knitted per hour.'
    Reference efficiencies: tricot machines typically run at 85–92% on simple
    structures; raschel on complex multi-bar lace: 60–75%.
    Losses from: yarn breaks (end breaks stop machine), guide-bar blockages,
    beam depletion, pattern chain/wheel changes, maintenance stops.
    """
    # Base efficiency by machine class and guide bar count
    if machine_class.lower() == "tricot":
        base_eff = 90.0  # simple 2-bar structures, high-speed, low stop rate
    else:
        if number_of_guide_bars <= 4:
            base_eff = 83.0
        elif number_of_guide_bars <= 12:
            base_eff = 75.0
        else:
            base_eff = 65.0  # multi-bar raschel lace: many bars → more stops

    # Loop formation quality penalty
    loop_penalty = {"good": 0.0, "marginal": 5.0, "poor": 15.0}
    base_eff -= loop_penalty.get(loop_formation_quality, 5.0)

    # Underlap regularity (affects fabric stops for quality faults)
    underlap_penalty = {"uniform": 0.0, "minor_variation": 2.0, "irregular": 7.0}
    base_eff -= underlap_penalty.get(underlap_regularity, 2.0)

    # Selvedge security
    selvedge_penalty = {"secure": 0.0, "borderline": 3.0, "at_risk": 8.0}
    base_eff -= selvedge_penalty.get(selvedge_security, 3.0)

    # Barre risk (stops for quality inspection and creel changes)
    barre_penalty = {"low": 0.0, "moderate": 2.0, "high": 6.0}
    base_eff -= barre_penalty.get(barre_risk, 2.0)

    # Maintenance overdue penalty
    maint_ratio = operating_hours_since_maintenance / max(1.0, maintenance_interval_hours)
    if maint_ratio > 1.0:
        base_eff -= 5.0
    elif maint_ratio > 0.85:
        base_eff -= 2.0

    return round(max(30.0, min(95.0, base_eff)), 1)


def predict_theoretical_production(
    machine_speed_cpm: float,
    courses_per_cm: float,
    fabric_width_finished_cm: float
) -> float:
    """
    Predicts theoretical fabric production rate in m/h (linear metres).

    Source: Spencer, Knitting Technology, Ch. 22.1 (loop length and fabric
    dimensions) and Ch. 30.11 (circular warp knitting production reference).
    Formula (analogous to weaving): production (m/h) = (cpm / cpc) × 60 / 100
    where cpm = courses per minute, cpc = courses per cm.
    (Dividing by 100 converts cm to m.)
    """
    if courses_per_cm <= 0:
        return 0.0
    production_m_per_hour = (machine_speed_cpm / courses_per_cm) * 60.0 / 100.0
    return round(production_m_per_hour, 1)


# ─────────────────────────────────────────────────────────────────────────────
# MASTER SIMULATION FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def simulate_warp_knitting(
    fabric_in: InputWovenFabric,
    params: WarpKnittingOperationalParams
) -> WarpKnittedFabricOutput:
    """
    Master simulation function for Warp Knitting.

    Takes Layer 2 (InputWovenFabric — the output of a weaving simulation) and
    Layer 3 (WarpKnittingOperationalParams), runs all prediction models, and
    returns Layer 4 (WarpKnittedFabricOutput).

    Also performs parameter validation and generates warnings for out-of-range
    conditions based on limits documented in Spencer (2001).
    """
    warnings = []

    # ── PARAMETER VALIDATION ─────────────────────────────────────────────────

    # Machine speed vs needle type (Spencer Ch. 24.4, Ch. 22.8)
    speed_limits = {"compound": 3300, "latch": 2200, "bearded": 1500}
    limit = speed_limits.get(params.needle_type.lower(), 2000)
    if params.machine_speed_cpm > limit:
        warnings.append(
            f"Machine speed ({params.machine_speed_cpm} cpm) exceeds the practical "
            f"maximum for {params.needle_type} needles ({limit} cpm). "
            "Needle fatigue, metal-fatigue fractures, and loop distortion are likely. "
            "Reduce speed or upgrade to compound needles (Spencer Ch. 24.4)."
        )

    # Gauge vs yarn count compatibility
    # Fine gauge (high E) requires fine yarn; coarse gauge allows heavy yarn
    tex = fabric_in.yarn_count_dtex / 10.0
    yarn_diameter_proxy = math.sqrt(tex) * 0.04  # mm (approximate)
    needle_pitch_mm = 25.4 / params.gauge_E      # mm between needles
    if yarn_diameter_proxy > needle_pitch_mm * 0.6:
        warnings.append(
            f"Yarn count ({fabric_in.yarn_count_dtex:.0f} dtex, diameter ≈ "
            f"{yarn_diameter_proxy:.2f} mm) may be too coarse for E {params.gauge_E} "
            f"gauge (needle pitch {needle_pitch_mm:.2f} mm). Risk of guide-eye blockage, "
            "overlap congestion, and needle deflection. Use finer yarn or coarser gauge."
        )

    # Guide bar count vs machine class (Spencer Ch. 24.2 and 24.3)
    if params.machine_class.lower() == "tricot" and params.number_of_guide_bars > 4:
        warnings.append(
            f"Tricot machines conventionally accommodate up to 4 guide bars "
            f"(Spencer Ch. 24.2). Specified {params.number_of_guide_bars} bars. "
            "Consider using a multi-bar raschel instead."
        )

    # Single guide bar warning (Spencer Ch. 23.12)
    if params.number_of_guide_bars == 1:
        warnings.append(
            "A single guide bar produces an inherently unstable structure with "
            "loop inclination, low strength, poor covering power, and limited "
            "patterning potential (Spencer Ch. 23.12). Two guide bars are the "
            "commercial minimum for most structures."
        )

    # Underlap span vs machine class (Spencer Ch. 23.10)
    if params.underlap_span_needles > 1 and params.machine_class.lower() == "raschel":
        pass  # raschel handles long underlaps well
    if params.underlap_span_needles > 8:
        warnings.append(
            f"Underlap span of {params.underlap_span_needles} needle spaces is very long. "
            "Floats of this length may catch on adjacent elements, cause yarn snagging, "
            "and produce a highly unstable structure unless specifically designed "
            "(e.g., velvet with 6×1 or 8×1 lap, Spencer Ch. 25.9)."
        )

    # Warp tension check
    if params.warp_tension_cN_per_end > 0 and fabric_in.yarn_tenacity_cN_tex > 0:
        tex_val = fabric_in.yarn_count_dtex / 10.0
        break_force = fabric_in.yarn_tenacity_cN_tex * tex_val
        tension_ratio = params.warp_tension_cN_per_end / max(1.0, break_force)
        if tension_ratio > 0.30:
            warnings.append(
                f"Warp tension ({params.warp_tension_cN_per_end:.1f} cN/end) is "
                f"{tension_ratio*100:.0f}% of estimated single-end breaking force "
                f"({break_force:.1f} cN). High risk of end breaks during knitting. "
                "Reduce let-off tension or use a stronger yarn."
            )

    # Take-down tension vs machine class
    if params.machine_class.lower() == "tricot" and params.take_down_tension_cN_per_cm > 30:
        warnings.append(
            f"Take-down tension of {params.take_down_tension_cN_per_cm:.0f} cN/cm is "
            "high for a tricot machine. Tricot fabric is drawn at nearly 90° to the "
            "needle bar with a gentle, low tension to protect the fine fabric "
            "(Spencer Ch. 24.2). Reduce take-down tension."
        )
    elif params.machine_class.lower() == "raschel" and params.take_down_tension_cN_per_cm < 20:
        warnings.append(
            f"Take-down tension of {params.take_down_tension_cN_per_cm:.0f} cN/cm is "
            "low for a raschel machine. Raschel fabric requires high take-down tension "
            "(120–160° draw angle) to hold open structures down and ensure clean "
            "knock-over (Spencer Ch. 24.3.2). Increase take-down tension."
        )

    # Humidity for synthetic filament yarns
    if any(f in fabric_in.fiber_type.lower() for f in ("nylon", "polyester")):
        if params.ambient_humidity_pct > 70:
            warnings.append(
                f"Ambient humidity of {params.ambient_humidity_pct:.0f}% is above the "
                "recommended range (50–65%) for synthetic filament warp knitting. "
                "High humidity can cause guide-bar friction variations and promote "
                "static in nylon. Use de-humidification."
            )
        elif params.ambient_humidity_pct < 40:
            warnings.append(
                f"Ambient humidity of {params.ambient_humidity_pct:.0f}% is too low. "
                "Static electricity in synthetic filaments will cause thread entanglement, "
                "guide-eye blockage, and erratic lapping. Target 50–65% RH."
            )

    # Substrate quality warnings carried forward from weaving
    if fabric_in.warp_yarn_quality_risk == "high":
        warnings.append(
            "Input fabric: warp yarn quality risk from weaving stage is HIGH. "
            "The same weak yarns will increase end-break frequency at the warp "
            "knitting machine. Consider re-warping with higher-quality yarn."
        )
    if fabric_in.substrate_regularity == "irregular":
        warnings.append(
            "Input fabric: pick-spacing was IRREGULAR in the weaving stage. "
            "This indicates yarn count or tension irregularities that will "
            "produce barre and course-density variation in the knitted structure."
        )

    # Negative let-off warning for high-speed tricot
    if (params.let_off_type == "negative_friction"
            and params.machine_speed_cpm > 1500):
        warnings.append(
            f"Negative friction let-off at {params.machine_speed_cpm} cpm will "
            "produce significant warp tension spikes, leading to barre, uneven "
            "run-in between bars, and increased end-break rate. Positive automatic "
            "let-off is essential for high-speed warp knitting "
            "(Spencer Ch. 22.3)."
        )

    # Maintenance overdue
    maint_ratio = (params.operating_hours_since_maintenance
                   / max(1.0, params.maintenance_interval_hours))
    if maint_ratio > 1.0:
        warnings.append(
            f"Machine is overdue for maintenance (operating {params.operating_hours_since_maintenance:.0f} h "
            f"since last service; interval is {params.maintenance_interval_hours:.0f} h). "
            "Worn needle hooks, bent guide holes, stiff beam bearings, and degraded "
            "chain links will reduce fabric quality and increase stop rate."
        )

    # ── RUN SIMULATION MODELS ────────────────────────────────────────────────

    courses_per_cm = predict_courses_per_cm(
        params.stitch_length_mm,
        fabric_in.yarn_count_dtex,
        fabric_in.fiber_type,
        params.let_off_type
    )

    wales_per_cm = predict_wales_per_cm(
        params.gauge_E,
        params.stitch_length_mm,
        fabric_in.fabric_width_cm,
        params.knitting_width_cm,
        params.underlap_span_needles
    )

    stitch_density = round(courses_per_cm * wales_per_cm, 1)

    fabric_weight = predict_fabric_weight(
        fabric_in.yarn_count_dtex,
        params.stitch_length_mm,
        courses_per_cm,
        wales_per_cm,
        params.number_of_guide_bars,
        params.threading_density
    )

    tf = predict_tightness_factor(
        fabric_in.yarn_count_dtex,
        params.stitch_length_mm
    )

    loop_quality = assess_loop_formation_quality(
        params.machine_speed_cpm,
        params.machine_class,
        params.needle_type,
        fabric_in.yarn_tenacity_cN_tex,
        fabric_in.yarn_evenness_CVm_pct,
        params.warp_tension_cN_per_end,
        fabric_in.yarn_count_dtex,
        params.gauge_E,
        params.operating_hours_since_maintenance,
        params.maintenance_interval_hours
    )

    tension_balance = assess_yarn_tension_balance(
        params.run_in_ratio_front_back,
        params.let_off_type,
        params.warp_tension_cN_per_end,
        fabric_in.yarn_tenacity_cN_tex,
        fabric_in.yarn_count_dtex,
        params.number_of_guide_bars
    )

    underlap_reg = assess_underlap_regularity(
        params.pattern_control,
        params.machine_speed_cpm,
        params.let_off_type,
        params.operating_hours_since_maintenance,
        params.maintenance_interval_hours,
        fabric_in.yarn_evenness_CVm_pct
    )

    stability = assess_fabric_stability(
        params.number_of_guide_bars,
        params.underlap_span_needles,
        params.lapping_type,
        params.threading_density,
        params.overlap_direction
    )

    nep_visibility = assess_surface_nep_visibility(
        fabric_in.substrate_nep_visibility,
        fabric_in.yarn_count_dtex,
        params.underlap_span_needles,
        fabric_in.fiber_type
    )

    barre = assess_barre_risk(
        params.let_off_type,
        fabric_in.yarn_evenness_CVm_pct,
        params.machine_speed_cpm,
        params.operating_hours_since_maintenance,
        params.maintenance_interval_hours,
        fabric_in.fiber_type
    )

    selvedge = assess_selvedge_security(
        params.machine_class,
        params.threading_density,
        params.lapping_type,
        params.take_down_tension_cN_per_cm,
        fabric_in.yarn_tenacity_cN_tex,
        fabric_in.substrate_selvedge_quality
    )

    cover = assess_cover_adequacy(
        tf,
        params.lapping_type,
        params.threading_density,
        params.number_of_guide_bars
    )

    extensibility = assess_extensibility(
        params.lapping_type,
        params.underlap_span_needles,
        fabric_in.yarn_count_dtex,
        fabric_in.fiber_type
    )

    curling = assess_fabric_curling(
        params.lapping_type,
        params.number_of_guide_bars,
        params.overlap_direction
    )

    # Finished fabric width (based on knitting width minus shrinkage)
    shrinkage_map = {1: 0.10, 2: 0.25, 3: 0.32, 4: 0.35, 6: 0.42, 8: 0.50}
    shrink = shrinkage_map.get(params.underlap_span_needles,
                               min(0.50, 0.10 + params.underlap_span_needles * 0.06))
    fabric_width_finished = round(params.knitting_width_cm * (1.0 - shrink), 1)

    theoretical_production = predict_theoretical_production(
        params.machine_speed_cpm,
        courses_per_cm,
        fabric_width_finished
    )

    machine_efficiency = predict_machine_efficiency(
        loop_quality,
        underlap_reg,
        selvedge,
        barre,
        params.machine_class,
        params.number_of_guide_bars,
        params.operating_hours_since_maintenance,
        params.maintenance_interval_hours
    )

    actual_production = round(theoretical_production * machine_efficiency / 100.0, 1)

    # Post-simulation warnings
    if loop_quality == "poor":
        warnings.append(
            "CRITICAL: Loop formation quality is POOR. The machine will experience "
            "frequent end breaks, missed overlaps, and loop-on-needle errors. "
            "Reduce machine speed, check needle condition, and verify warp tension."
        )

    if stability == "unstable":
        warnings.append(
            "Fabric stability is UNSTABLE. The current structure will have poor "
            "dimensional stability, loop inclination, and inadequate cohesion. "
            "Ensure at least two guide bars underlapping in opposition "
            "(Spencer Ch. 23.12)."
        )

    if barre == "high":
        warnings.append(
            "Barre risk is HIGH. Horizontal streaks are very likely in the fabric. "
            "Switch to positive automatic let-off, improve yarn count consistency, "
            "and service the warp beam tension rails."
        )

    if selvedge == "at_risk":
        warnings.append(
            "Selvedge security is AT RISK. Progressive loop press-off at selvedge "
            "needles is likely. Add dedicated selvedge guide bars or increase "
            "selvedge thread density (Spencer Ch. 24.3.2)."
        )

    if tf > 2.0:
        warnings.append(
            f"Tightness Factor ({tf:.2f}) is very high. The fabric will be very dense, "
            "stiff, and difficult to form on the needle bar. Consider increasing "
            "stitch length or using finer yarn to reduce TF below 1.8."
        )
    elif tf < 0.8:
        warnings.append(
            f"Tightness Factor ({tf:.2f}) is very low. The fabric will be very open, "
            "flimsy, and dimensionally unstable. Reduce stitch length or increase "
            "yarn count to improve fabric integrity."
        )

    return WarpKnittedFabricOutput(
        fabric_width_finished_cm=fabric_width_finished,
        courses_per_cm=courses_per_cm,
        wales_per_cm=wales_per_cm,
        stitch_density_per_cm2=stitch_density,
        fabric_weight_g_per_m2=fabric_weight,
        tightness_factor=tf,
        loop_formation_quality=loop_quality,
        yarn_tension_balance=tension_balance,
        underlap_regularity=underlap_reg,
        fabric_stability=stability,
        surface_nep_visibility=nep_visibility,
        barre_risk=barre,
        selvedge_security=selvedge,
        cover_adequacy=cover,
        extensibility_rating=extensibility,
        fabric_curling_tendency=curling,
        theoretical_production_m_per_hour=theoretical_production,
        machine_efficiency_pct=machine_efficiency,
        actual_production_m_per_hour=actual_production,
        warnings=warnings
    )


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE USAGE AND VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    print("=" * 72)
    print("WARP KNITTING SIMULATION")
    print("Based on Spencer, D.J., Knitting Technology, 3rd ed. (2001)")
    print("=" * 72)

    # ── SCENARIO 1: Locknit lingerie on a compound-needle tricot machine ─────
    # Input fabric: PES/CO blend from dobby weaving Scenario 1 output.
    # This is typical of fabric entering a warp-knitting line where a woven
    # substrate (e.g. woven lining) is being replaced by a knitted structure.
    # Here the locknit is knitted directly from yarn (warp-beam feed);
    # the InputWovenFabric carries the yarn-quality fingerprint from upstream.
    print("\n--- SCENARIO 1: Nylon locknit lingerie on E 28 tricot machine ---\n")

    fabric_1 = InputWovenFabric(
        # Fabric geometry carried forward from weaving simulation output
        fabric_width_cm=160.0,
        fabric_weight_g_per_m2=120.0,
        cloth_cover_factor=0.95,
        weft_crimp_pct=7.5,
        warp_crimp_pct=4.2,
        # Substrate quality metrics (from weaving Layer 4)
        warp_yarn_quality_risk="low",
        weft_yarn_quality_risk="low",
        substrate_nep_visibility="negligible",    # nylon filament: no neps
        substrate_regularity="excellent",
        substrate_selvedge_quality="clean",
        # Upstream process performance
        upstream_process_efficiency_pct=84.0,
        upstream_feed_rate_m_per_hour=535.0,
        # Yarn properties (carried through from spinning via weaving)
        yarn_count_dtex=44.0,           # 40 denier nylon ≈ 44 dtex (Spencer Ch. 25.3)
        fiber_type="nylon",
        yarn_tenacity_cN_tex=42.0,      # nylon filament: high tenacity
        yarn_evenness_CVm_pct=0.8,      # filament: excellent evenness
        yarn_hairiness_H=0.2,           # filament: minimal hairiness
    )

    params_1 = WarpKnittingOperationalParams(
        machine_class="tricot",
        gauge_E=28,                         # E 28: standard for lingerie (Spencer Ch. 24.2)
        needle_type="compound",             # Compound needle: max speed, minimal fatigue
        knitting_width_cm=426.7,            # 168 inches — standard tricot width (Spencer Ch. 25.3)
        number_of_guide_bars=2,             # Standard 2-bar locknit
        threading_density="full",
        underlap_span_needles=2,            # Locknit: 2×1 front bar underlap
        lapping_type="locknit",             # Most popular warp-knit structure (70–80% of output)
        overlap_direction="closed_lap",
        pattern_control="electronic",       # Karl Mayer EL linear motor
        machine_speed_cpm=2800,             # High-speed compound needle tricot
        let_off_type="positive_automatic",  # Karl Mayer computer-controlled let-off
        run_in_ratio_front_back=0.75,       # Locknit: 3:4 ratio (Spencer p. 321)
        warp_tension_cN_per_end=6.0,        # Filament: low tension (3–12 cN/end typical)
        take_down_tension_cN_per_cm=15.0,   # Tricot: gentle take-down
        stitch_length_mm=1.6,               # Standard locknit, 40 den nylon (Spencer Ch. 25.3)
        sinker_depth_mm=3.2,
        shed_swing_angle_deg=130.0,
        ambient_temperature_C=22.0,
        ambient_humidity_pct=58.0,          # Synthetic: 50–65% RH
        last_maintenance_date="2025-10-01",
        maintenance_interval_hours=2000.0,
        operating_hours_since_maintenance=400.0,
    )

    result_1 = simulate_warp_knitting(fabric_1, params_1)

    print(f"  Finished Fabric Width:        {result_1.fabric_width_finished_cm} cm")
    print(f"  Courses per cm:               {result_1.courses_per_cm}")
    print(f"  Wales per cm:                 {result_1.wales_per_cm}")
    print(f"  Stitch Density:               {result_1.stitch_density_per_cm2} loops/cm²")
    print(f"  Fabric Weight:                {result_1.fabric_weight_g_per_m2} g/m²")
    print(f"  Tightness Factor:             {result_1.tightness_factor}")
    print(f"  Loop Formation Quality:       {result_1.loop_formation_quality.upper()}")
    print(f"  Yarn Tension Balance:         {result_1.yarn_tension_balance.upper()}")
    print(f"  Underlap Regularity:          {result_1.underlap_regularity.upper()}")
    print(f"  Fabric Stability:             {result_1.fabric_stability.upper()}")
    print(f"  Surface Nep Visibility:       {result_1.surface_nep_visibility.upper()}")
    print(f"  Barre Risk:                   {result_1.barre_risk.upper()}")
    print(f"  Selvedge Security:            {result_1.selvedge_security.upper()}")
    print(f"  Cover Adequacy:               {result_1.cover_adequacy.upper()}")
    print(f"  Extensibility:                {result_1.extensibility_rating.upper()}")
    print(f"  Fabric Curling:               {result_1.fabric_curling_tendency.upper()}")
    print(f"  Theoretical Production:       {result_1.theoretical_production_m_per_hour} m/h")
    print(f"  Machine Efficiency:           {result_1.machine_efficiency_pct}%")
    print(f"  Actual Production:            {result_1.actual_production_m_per_hour} m/h")
    if result_1.warnings:
        print(f"\n  WARNINGS:")
        for w in result_1.warnings:
            print(f"    ⚠  {w}")
    else:
        print("\n  No warnings — all parameters within recommended ranges.")

    # ── SCENARIO 2: Raschel power net for foundation wear ────────────────────
    # Spencer Ch. 28.10: power net — four half-sett bars, nylon + elastane.
    # Demonstrates the raschel machine's suitability for open elastic structures.
    print("\n--- SCENARIO 2: Raschel power net — nylon + elastane, E 18 ---\n")

    fabric_2 = InputWovenFabric(
        fabric_width_cm=200.0,
        fabric_weight_g_per_m2=90.0,
        cloth_cover_factor=0.60,           # lighter woven substrate or open structure
        weft_crimp_pct=5.0,
        warp_crimp_pct=3.0,
        warp_yarn_quality_risk="low",
        weft_yarn_quality_risk="low",
        substrate_nep_visibility="negligible",
        substrate_regularity="good",
        substrate_selvedge_quality="acceptable",
        upstream_process_efficiency_pct=78.0,
        upstream_feed_rate_m_per_hour=320.0,
        # Yarn properties: fine nylon for ground, elastane for inlay
        yarn_count_dtex=44.0,              # 40 den nylon for ground guide bars
        fiber_type="nylon",
        yarn_tenacity_cN_tex=42.0,
        yarn_evenness_CVm_pct=0.9,
        yarn_hairiness_H=0.15,
    )

    params_2 = WarpKnittingOperationalParams(
        machine_class="raschel",
        gauge_E=18,                         # E 18 raschel (Spencer Ch. 28.10)
        needle_type="compound",
        knitting_width_cm=430.0,
        number_of_guide_bars=4,             # Power net: 4 guide bars (2 nylon + 2 elastane)
        threading_density="half",           # Half-sett threaded: one thread every other guide
        underlap_span_needles=2,            # Ground bars: 2×1 underlap
        lapping_type="power_net",           # Spencer Ch. 28.10
        overlap_direction="closed_lap",
        pattern_control="electronic",
        machine_speed_cpm=1400,             # Raschel: moderate speed with elastane
        let_off_type="positive_automatic",  # Essential for elastane tension control
        run_in_ratio_front_back=1.0,        # Front/back nylon bars run at same rate
        warp_tension_cN_per_end=5.0,        # Low tension for elastane compatibility
        take_down_tension_cN_per_cm=50.0,   # Raschel: strong take-down for open structure
        stitch_length_mm=2.0,
        sinker_depth_mm=4.0,
        shed_swing_angle_deg=140.0,
        ambient_temperature_C=23.0,
        ambient_humidity_pct=55.0,
        last_maintenance_date="2025-09-15",
        maintenance_interval_hours=1500.0,
        operating_hours_since_maintenance=500.0,
    )

    result_2 = simulate_warp_knitting(fabric_2, params_2)

    print(f"  Finished Fabric Width:        {result_2.fabric_width_finished_cm} cm")
    print(f"  Fabric Weight:                {result_2.fabric_weight_g_per_m2} g/m²")
    print(f"  Tightness Factor:             {result_2.tightness_factor}")
    print(f"  Stitch Density:               {result_2.stitch_density_per_cm2} loops/cm²")
    print(f"  Loop Formation Quality:       {result_2.loop_formation_quality.upper()}")
    print(f"  Fabric Stability:             {result_2.fabric_stability.upper()}")
    print(f"  Cover Adequacy:               {result_2.cover_adequacy.upper()}")
    print(f"  Extensibility:                {result_2.extensibility_rating.upper()}")
    print(f"  Barre Risk:                   {result_2.barre_risk.upper()}")
    print(f"  Selvedge Security:            {result_2.selvedge_security.upper()}")
    print(f"  Machine Efficiency:           {result_2.machine_efficiency_pct}%")
    print(f"  Actual Production:            {result_2.actual_production_m_per_hour} m/h")
    if result_2.warnings:
        print(f"\n  WARNINGS:")
        for w in result_2.warnings:
            print(f"    ⚠  {w}")
    else:
        print("\n  No warnings — all parameters within recommended ranges.")

    # ── SCENARIO 3: Stress test — many faults deliberately introduced ─────────
    # Single guide bar, latch needles running too fast, negative let-off,
    # coarse yarn on fine gauge, overdue maintenance. Demonstrates full warning system.
    print("\n--- SCENARIO 3: Stress test — single-bar, overloaded, maintenance overdue ---\n")

    fabric_3 = InputWovenFabric(
        fabric_width_cm=150.0,
        fabric_weight_g_per_m2=180.0,
        cloth_cover_factor=1.2,
        weft_crimp_pct=9.0,
        warp_crimp_pct=5.5,
        warp_yarn_quality_risk="high",      # Weak warp yarns from weaving
        weft_yarn_quality_risk="medium",
        substrate_nep_visibility="visible_defects",
        substrate_regularity="irregular",   # Pick-spacing was irregular upstream
        substrate_selvedge_quality="faults_likely",
        upstream_process_efficiency_pct=55.0,
        upstream_feed_rate_m_per_hour=180.0,
        yarn_count_dtex=300.0,              # Coarse yarn — cotton equivalent ~Nm 33
        fiber_type="cotton",
        yarn_tenacity_cN_tex=11.0,          # Low tenacity (carded cotton)
        yarn_evenness_CVm_pct=16.5,         # Poor evenness
        yarn_hairiness_H=7.5,               # High hairiness
    )

    params_3 = WarpKnittingOperationalParams(
        machine_class="tricot",
        gauge_E=28,                         # Fine gauge — mismatched to coarse yarn
        needle_type="latch",                # Latch needles — lower speed limit
        knitting_width_cm=213.0,
        number_of_guide_bars=1,             # Single bar — inherently unstable
        threading_density="full",
        underlap_span_needles=4,            # Velvet-type long underlap
        lapping_type="velour",
        overlap_direction="open_lap",
        pattern_control="chain_links",      # Older chain-link control
        machine_speed_cpm=2600,             # Exceeds latch-needle limit (2200 cpm)
        let_off_type="negative_friction",   # Inherently irregular tension
        run_in_ratio_front_back=2.5,        # Extreme ratio
        warp_tension_cN_per_end=35.0,       # Very high for this yarn
        take_down_tension_cN_per_cm=8.0,    # Too low for raschel/open structure
        stitch_length_mm=2.2,
        sinker_depth_mm=3.5,
        shed_swing_angle_deg=150.0,
        ambient_temperature_C=30.0,
        ambient_humidity_pct=85.0,          # Too humid for synthetic / high for cotton
        last_maintenance_date="2023-01-01",
        maintenance_interval_hours=1000.0,
        operating_hours_since_maintenance=1800.0,   # Severely overdue
    )

    result_3 = simulate_warp_knitting(fabric_3, params_3)

    print(f"  Fabric Weight:                {result_3.fabric_weight_g_per_m2} g/m²")
    print(f"  Tightness Factor:             {result_3.tightness_factor}")
    print(f"  Loop Formation Quality:       {result_3.loop_formation_quality.upper()}")
    print(f"  Fabric Stability:             {result_3.fabric_stability.upper()}")
    print(f"  Barre Risk:                   {result_3.barre_risk.upper()}")
    print(f"  Selvedge Security:            {result_3.selvedge_security.upper()}")
    print(f"  Underlap Regularity:          {result_3.underlap_regularity.upper()}")
    print(f"  Machine Efficiency:           {result_3.machine_efficiency_pct}%")
    print(f"  Actual Production:            {result_3.actual_production_m_per_hour} m/h")
    if result_3.warnings:
        print(f"\n  WARNINGS ({len(result_3.warnings)} issues detected):")
        for w in result_3.warnings:
            print(f"    ⚠  {w}")

    print("\n" + "=" * 72)
    print("Simulation complete.")
    print("=" * 72)
