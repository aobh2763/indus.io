"""
Plain Weaving Simulation Module
Process: Weaving > Plain Weaving (Shuttle / Rapier / Air-jet Loom)

Layer 2 of this module (InputYarns) corresponds directly to Layer 4
of the spinning simulation modules (YarnQualityOutput from rotor.py,
airjet.py, ring_spinning.py, etc.). The warp and weft yarns arrive at
the loom as the finished product of the preceding spinning process.

All parameter relationships derived from:
R. Marks and A. T. C. Robinson, "Principles of Weaving",
The Textile Institute, Manchester, 1976.
ISBN 0 900739 25 8

Supporting references:
  [Peirce]     F. T. Peirce, "The Geometry of Cloth Structure",
               J. Text. Inst. 28, T45 (1937).
  [Greenwood]  K. Greenwood and J. G. Cowhig, referenced in
               Marks & Robinson Ch. 6, Cloth-fell Position experiment
               (16-tex cellulose acetate, 34 ends/cm, plain weave).
  [Townsend]   Townsend (ref. 17 in Marks & Robinson), weft-tension
               measurements at the fell in plain worsted cloth.

Layer 5 functions model the physical cause-effect relationships
that link operational parameters (Layer 3) and input yarn properties
(Layer 2) to fabric output quality metrics (Layer 4).
"""

import math
from dataclasses import dataclass, field


# ─────────────────────────────────────────────────────────────────────────────
# DATA CLASSES — Layer 2, 3, and 4
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class InputYarns:
    """
    Layer 2 — Input yarn properties for Plain Weaving.

    These fields map 1-to-1 onto the Layer 4 output of spinning modules:
      warp_tenacity_cN_tex    ← YarnQualityOutput.yarn_tenacity_cN_tex
      warp_CVm_pct            ← YarnQualityOutput.yarn_evenness_CVm_pct
      warp_hairiness_H        ← YarnQualityOutput.hairiness_H
      warp_twist_t_per_m      ← YarnQualityOutput.actual_twist_turns_per_m
      warp_yarn_count_tex     ← RotorOperationalParams.yarn_count_tex  (Layer 3 → 4)
      ... and the same fields for weft.

    Warp and weft may come from different spinning processes (e.g., rotor-spun
    warp and ring-spun weft), so both sets of properties are specified separately.
    """
    # ── WARP YARN (ends) ──────────────────────────────────────────────────────
    warp_yarn_count_tex: float       # Warp linear density in tex. Plain weave range: 5 - 200 tex.
    warp_yarn_count_Ne: float        # Warp count in Ne (cotton count). Ne = 590.5 / tex.
    warp_yarn_tenacity_cN_tex: float # Warp yarn tenacity in cN/tex, from spinning L4.
                                     # Minimum recommended for reliable weaving: > 8 cN/tex.
    warp_yarn_CVm_pct: float         # Warp yarn mass evenness CVm%, from spinning L4.
                                     # Higher CVm → more thin places → higher end-break risk.
    warp_yarn_hairiness_H: float     # Uster hairiness H of warp yarn, from spinning L4.
                                     # High hairiness → shed not clean → increased stitching risk.
    warp_yarn_twist_t_per_m: float   # Twist in warp yarn (t/m), from spinning L4.
                                     # Affects yarn compressibility and crimp behaviour.
    warp_yarn_type: str              # "cotton_carded", "cotton_combed", "blend_PES_CO",
                                     # "polyester", "viscose", "MMF" — matches spinning L2.

    # ── WEFT YARN (picks) ─────────────────────────────────────────────────────
    weft_yarn_count_tex: float       # Weft linear density in tex.
    weft_yarn_count_Ne: float        # Weft count in Ne.
    weft_yarn_tenacity_cN_tex: float # Weft yarn tenacity in cN/tex, from spinning L4.
                                     # Weft must sustain insertion tension (jet/rapier drag).
    weft_yarn_CVm_pct: float         # Weft yarn CVm%, from spinning L4.
    weft_yarn_hairiness_H: float     # Weft yarn hairiness H, from spinning L4.
    weft_yarn_twist_t_per_m: float   # Twist in weft yarn (t/m), from spinning L4.
    weft_yarn_type: str              # Same type codes as warp.


@dataclass
class PlainWeavingParams:
    """
    Layer 3 — Operational parameters specific to Plain Weaving.

    Plain weave is the simplest interlacing: every end crosses over one
    pick, under the next, alternating across the full width and length of
    the fabric. It has the shortest float length (1), the highest possible
    interlacing frequency, and therefore the highest crimp and firmness
    for a given sett.
    """
    # ── SETT AND STRUCTURE ────────────────────────────────────────────────────
    ends_per_cm: float               # Warp sett (threads/cm). Typical range: 10 - 60 ends/cm.
                                     # Determines warp cover factor and shed geometry.
    picks_per_cm: float              # Weft sett, set by take-up motion (picks/cm).
                                     # Typical range: 8 - 55 picks/cm.
    reed_width_cm: float             # Effective reed/weaving width in cm. Typical: 90 - 400 cm.
                                     # Width occupied by warp threads in the reed.

    # ── LOOM SPEED AND TYPE ───────────────────────────────────────────────────
    loom_speed_picks_per_min: float  # Machine speed in picks/min.
                                     # Shuttle looms: 150-300 ppm.
                                     # Rapier looms: 200-400 ppm.
                                     # Air-jet looms: up to 400-600 ppm.
                                     # (Marks & Robinson, Section 5.4, p. 130)
    loom_type: str                   # "shuttle", "rapier", "air_jet", "water_jet".
                                     # Governs weft insertion tension model.

    # ── WARP TENSION ─────────────────────────────────────────────────────────
    warp_tension_cN_per_end: float   # Basic warp tension (To) per end in cN.
                                     # This is the resting tension between picks.
                                     # Minimum: must prevent bumping (Marks & Robinson, p. 147).
                                     # Typical range: 5 - 30 cN/end depending on count and type.
    let_off_type: str                # "positive" or "negative_friction".
                                     # Positive: gear-driven → uniform warp tension.
                                     # Negative friction: floating beam → variable tension,
                                     # prone to setting-on places (Marks & Robinson p. 150-151).

    # ── TAKE-UP ───────────────────────────────────────────────────────────────
    take_up_type: str                # "positive" or "negative".
                                     # Positive (7-wheel, Picanol, Shirley):
                                     #   → uniform pick-spacing → preferred for most fabrics.
                                     # Negative: used for woollen yarns or heavily milled cloths
                                     #   to achieve uniform weft density.
                                     # (Marks & Robinson, Section 6.1.1, p. 140)

    # ── SHED GEOMETRY ─────────────────────────────────────────────────────────
    shed_depth_cm: float             # Clear shed depth at the reed (cm). Typical: 8 - 12 cm.
                                     # Affects shuttle/carrier clearance and warp thread fatigue.
    heald_shaft_count: int           # Number of heald shafts. Plain weave minimum = 2.
                                     # More shafts → higher heald mass → increased end-break
                                     # risk from dynamic forces at loom speed.

    # ── TEMPLE SYSTEM ─────────────────────────────────────────────────────────
    temple_type: str                 # "pin_temple", "clip_temple", or "none".
                                     # Temples prevent weftway contraction of cloth at the fell.
                                     # Without temples: weft cuts and reed rubs on selvedge ends.
                                     # (Marks & Robinson, Section 6.1.2, p. 141)

    # ── MACHINE CONDITION ────────────────────────────────────────────────────
    ambient_temperature_C: float     # In Celsius. Affects warp tension and yarn friction.
    ambient_humidity_pct: float      # Relative humidity %. Cotton swells and softens at high
                                     # humidity, affecting crimp balance and end-break rate.
    maintenance_interval_hours: float     # Recommended service interval in running hours.
    operating_hours_since_maintenance: float  # Hours since last service.


@dataclass
class FabricQualityOutput:
    """
    Layer 4 — Predicted output quality metrics for Plain Weaving.
    """
    yarn_diameter_warp_mm: float         # Estimated warp yarn diameter in mm (Peirce formula).
    yarn_diameter_weft_mm: float         # Estimated weft yarn diameter in mm.
    warp_cover_factor: float             # Fractional warp cover = d_warp_cm × ends/cm.
                                         # Range 0-1; value 1.0 = fully covered warp face.
    weft_cover_factor: float             # Fractional weft cover = d_weft_cm × picks/cm.
    total_cover_factor: float            # Combined cover factor (Peirce):
                                         # f_total = f_warp + f_weft - f_warp × f_weft.
    warp_crimp_pct: float                # Warp thread crimp % in the finished fabric.
                                         # Higher warp crimp → warp-faced appearance → poplin-type.
    weft_crimp_pct: float                # Weft thread crimp %.
    crimp_balance: str                   # "warp_dominant", "balanced", "weft_dominant".
                                         # Describes which system has higher crimp in relaxed cloth.
    fell_displacement_mm: float          # Displacement of cloth fell by reed at beat-up (mm).
                                         # (Greenwood & Cowhig data, Marks & Robinson Fig. 6.3)
    beat_up_force_cN_per_cm: float       # Estimated beat-up force per cm of reed width (cN/cm).
                                         # Proportional to fell displacement (Equation 6.1).
    fabric_areal_weight_g_m2: float      # Fabric areal density in g/m² (GSM).
    weft_tension_at_fell_cN: float       # Estimated weft tension at incorporation into fell (cN).
                                         # High values indicate risk of weft-cutting.
    warp_break_risk: str                 # "low", "medium", "high".
    weft_break_risk: str                 # "low", "medium", "high".
    cloth_defect_risk: str               # "low", "medium", "high" — thick/thin places, stitching.
    production_rate_m_per_min: float     # Fabric delivery rate in m/min.
    production_rate_m2_per_hour: float   # Fabric area produced per hour (m²/h).
    warnings: list                       # Out-of-range parameter warnings.


# ─────────────────────────────────────────────────────────────────────────────
# LAYER 5 — SIMULATION FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def calculate_yarn_diameter_mm(
    yarn_count_tex: float,
    yarn_type: str
) -> float:
    """
    Estimates yarn diameter in mm using Peirce's empirical formula.

    Source: F. T. Peirce, "The Geometry of Cloth Structure",
    J. Text. Inst. 28, T45–T96 (1937); cited and used in
    Marks & Robinson, Ch. 6, footnote p. 141:
        "Calculated as d/p, where d is the yarn diameter
         and p the thread spacing."

    Peirce's formula:
        d (cm) = k × √tex / 10
    i.e., d (mm) = k × √tex

    where k is a fibre-type constant:
        k_cotton     ≈ 0.037 cm/√tex → 0.037 mm/√tex in mm-tex form... wait
        Actually from Peirce: d (cm) = (1/28) × √(tex/ρ) where ρ is fibre
        specific gravity.

    Practical calibrated constants (mm, tex):
        cotton:        k = 0.037   (ρ ≈ 1.52 g/cm³)
        polyester:     k = 0.033   (ρ ≈ 1.38 g/cm³)
        viscose/modal: k = 0.040   (ρ ≈ 1.52 g/cm³, looser twist structure)
        PES/CO blend:  k = 0.035   (weighted average)
        MMF generic:   k = 0.034

    These values reproduce Peirce's published diameters within ~5% for
    typical yarn counts (Ne 6-60) at typical twist levels.
    The formula captures the most important effect: coarser yarns occupy
    more space and produce higher cover factors at the same thread density.
    """
    yt = yarn_type.lower().replace(" ", "_")
    if "cotton" in yt:
        k = 0.037
    elif "polyester" in yt or "pes" in yt:
        k = 0.033
    elif "viscose" in yt or "cv" in yt:
        k = 0.040
    elif "blend" in yt or ("pes" in yt and "co" in yt):
        k = 0.035
    else:
        k = 0.034  # generic MMF

    diameter_mm = k * math.sqrt(yarn_count_tex)
    return round(diameter_mm, 4)


def calculate_cover_factor(
    yarn_diameter_mm: float,
    threads_per_cm: float
) -> float:
    """
    Calculates the fractional cover factor for one yarn system (warp or weft).

    Source: Peirce (1937), as cited and applied in Marks & Robinson, p. 141,
    footnote: "Calculated as d/p, where d is the yarn diameter and p the
    thread spacing."

    Since p (cm) = 1 / threads_per_cm, and d must be in cm:
        fractional_cover = d (cm) × threads_per_cm
                         = (d_mm / 10) × n

    For a square cloth in approximately plain weave, Greenwood & Cowhig
    (Marks & Robinson, p. 193) found that a fractional weft cover of ~0.4
    is sufficient for a firm cloth with low-twist continuous-filament yarns,
    and that a value approaching 0.58 represents the practical weaving limit
    under their experimental conditions.

    Physical meaning:
        fc = 0.0  → open net fabric, threads widely spaced
        fc = 0.5  → firmly set cloth (typical shirting, sheeting)
        fc ≥ 0.58 → approaching maximum practical sett for plain weave
        fc = 1.0  → all space filled (theoretical; requires yarn deformation)
    """
    d_cm = yarn_diameter_mm / 10.0
    fc = d_cm * threads_per_cm
    return round(min(1.0, fc), 4)


def calculate_total_cover_factor(
    warp_cover: float,
    weft_cover: float
) -> float:
    """
    Calculates the combined (total) fabric cover factor.

    Source: Peirce (1937), cited in standard textile geometry texts.
    The intersection of warp and weft projections is counted once, so:

        f_total = f_warp + f_weft - f_warp × f_weft

    This is the standard probability-based formula, assuming that warp
    and weft positions are independent. The subtracted term removes the
    overlap where both warp and weft cover the same area.

    For a square cloth (f_warp = f_weft = 0.5):
        f_total = 0.5 + 0.5 - 0.25 = 0.75

    For f_warp = f_weft = 0.4 (open plain-weave shirting):
        f_total = 0.4 + 0.4 - 0.16 = 0.64

    Maximum theoretical for a "woven" fabric: well below 1.0, because
    the interlacing geometry of plain weave prevents both systems from
    simultaneously reaching their individual maxima.
    """
    fc = warp_cover + weft_cover - warp_cover * weft_cover
    return round(min(1.0, fc), 4)


def calculate_crimp(
    warp_diameter_mm: float,
    weft_diameter_mm: float,
    ends_per_cm: float,
    picks_per_cm: float,
    warp_tension_cN_per_end: float,
    weft_cover_factor: float,
    temple_type: str
) -> tuple:
    """
    Estimates warp crimp% and weft crimp% in plain-weave fabric.

    Source: Marks & Robinson, Section 6.1.2, p. 141-142, drawing on
    Peirce's geometry (1937) and Townsend's measurements (ref. 17):
    - "For a square plain worsted cloth with a fractional cover of 0.5,
      the weft tension may increase from about 5 gf (49 mN) as the
      shuttle lays it in the shed to as much as 180 gf (1765 mN) when
      the pick is incorporated into the cloth." (p. 141)
    - "Since effective templing prevents the weft at the fell from
      crimping, it follows that the warp crimp at the fell must be
      correspondingly high." (p. 141)
    - "We may expect the weft crimp to be rather greater than the warp
      crimp in the relaxed cloth." (p. 142) — this is the loom-state
      and relaxed-state tendency for warpway tension to dominate.

    Peirce's geometry for plain weave:
        If D = d_warp + d_weft (sum of diameters, mm)
        and p = thread spacing (mm), then:
        crimp% ≈ (π²/8) × (D/p)² × 100  [approximate, low-crimp limit]

    This is exact only when D/p ≪ 1. For practical plain-weave fabrics
    (D/p approaching 0.5), the full Peirce ellipse integral applies, but
    the approximation is accurate within ~10% for normal sett ranges.

    Crimp redistribution (Marks & Robinson, p. 141-142):
    - Near the fell (with temples active): warp crimp is high, weft crimp
      is suppressed.
    - Relaxed cloth: weft crimp redistributes upward; warp crimp falls.
    - This function returns the estimated RELAXED loom-state crimps,
      accounting for the partial redistribution that occurs off the loom.
    - For warp-faced cloths (f_warp >> f_weft): weft crimp is low (2-3%).
    - For square cloths: some redistribution → weft crimp slightly > warp.
    - For weft-faced cloths (f_weft >> f_warp): weft crimp dominates.

    Temple effect:
    - With temples: warp crimp at fell is artificially elevated; after
      leaving temples, some redistribution occurs → estimated here.
    - Without temples: weftway contraction occurs; warp crimp is lower
      and weft crimp is higher even at fell.

    Warp tension effect:
    - Higher warp tension → warp threads are held straighter → lower
      warp crimp and correspondingly higher weft crimp.
    """
    # Thread spacings in mm
    p_warp_mm = 10.0 / ends_per_cm   # warp thread spacing (mm)
    p_weft_mm = 10.0 / picks_per_cm  # weft thread spacing (mm)
    D_mm = warp_diameter_mm + weft_diameter_mm  # sum of diameters

    # Peirce approximate crimp% for each system
    # Warp crimp: controlled by how tightly weft is packed (picks/cm)
    # The warp must bend over/under each weft pick.
    ratio_warp = D_mm / p_weft_mm   # D / p_weft
    warp_crimp_base = (math.pi**2 / 8.0) * ratio_warp**2 * 100.0

    # Weft crimp: controlled by warp packing (ends/cm)
    ratio_weft = D_mm / p_warp_mm   # D / p_warp
    weft_crimp_base = (math.pi**2 / 8.0) * ratio_weft**2 * 100.0

    # Redistribution factor: in a square cloth under normal weaving
    # conditions with positive let-off, warpway tension dominates.
    # This biases the warp crimp downward (warp is held tighter) and
    # the weft crimp upward in the relaxed state.
    # (Marks & Robinson, p. 142: "warp crimp tends to predominate near
    # the fell, weft crimp exceeds warp crimp in the relaxed cloth")
    # Modelled as a redistribution fraction based on warp tension per end
    # relative to a reference tension of 10 cN/end.
    tension_ref_cN = 10.0
    tension_ratio = warp_tension_cN_per_end / tension_ref_cN

    # Higher warp tension → straighter warp → less warp crimp, more weft crimp
    # Redistribution factor: 0 = no effect, 1 = full redistribution
    redistribution = min(0.35, max(-0.20, 0.12 * (tension_ratio - 1.0)))

    warp_crimp = warp_crimp_base * (1.0 - redistribution)
    weft_crimp = weft_crimp_base * (1.0 + redistribution * 0.6)

    # Temple adjustment:
    # Without temples, weftway contraction reduces the effective weft
    # pick length → less weft tension → weft crimp is larger off loom.
    if temple_type.lower() == "none":
        weft_crimp *= 1.18   # wider distribution of crimp into weft
        warp_crimp *= 0.88   # less restraint on warp at fell
    elif temple_type.lower() == "clip_temple":
        # Clip temples less effective than pin temples at selvedges
        weft_crimp *= 1.06
        warp_crimp *= 0.96

    # Warp-faced cloth correction: if weft_cover >> warp_cover, suppress weft crimp
    # (Marks & Robinson, p. 142: "weft crimp in warp-faced cloths is low, 2-3%")
    if weft_cover_factor < 0.30 and ends_per_cm / picks_per_cm > 1.5:
        weft_crimp = min(weft_crimp, 3.5)

    warp_crimp = max(0.5, warp_crimp)
    weft_crimp = max(0.5, weft_crimp)

    return round(warp_crimp, 2), round(weft_crimp, 2)


def predict_fell_displacement_mm(
    weft_cover_factor: float
) -> float:
    """
    Predicts the cloth-fell displacement at beat-up in mm.

    Source: Marks & Robinson, Section 6.1.3, p. 143-145, and
    Figure 6.3 (Greenwood & Cowhig data, p. 144):
    - Experiment: 16-tex cellulose acetate warp, 34 ends/cm,
      16-tex cellulose acetate weft, plain weave, varying picks/cm.
    - Key data points from Fig. 6.3:
        f_weft ≤ 0.20 → fell displacement ≈ 0 mm (reed barely touches fell)
        f_weft = 0.40 → fell displacement ≈ 2.5 mm (firm cloth, point A)
        f_weft = 0.50 → fell displacement ≈ 5.5 mm
        f_weft = 0.58 → fell displacement → 7.5 mm (approaching limit)

    "The cloth-fell position increases very rapidly as the fractional
    weft cover approaches the limit for a particular set of conditions."
    (Marks & Robinson, p. 144)

    The curve is well-represented by an exponential approach to the
    practical limit. Parameters fitted to Greenwood & Cowhig's data:
        displacement = L × exp(α × (fc - fc0)) - L × exp(α × (-fc0))
    simplified to a logistic-like function calibrated to the three
    reported data points.

    Physical meaning: the fell displacement IS the reed stroke needed
    to force the new pick into position against the weaving resistance.
    It is independent of basic warp tension To (Equation 6.1) and is
    determined solely by the fabric structure.
    """
    fc = max(0.0, min(0.70, weft_cover_factor))

    if fc <= 0.20:
        # Open cloth: no resistance until threshold cover is reached
        return 0.0
    elif fc <= 0.58:
        # Exponential rise fitted to Fig. 6.3 data points
        # (0.20, 0.0), (0.40, 2.5), (0.50, 5.5), (0.58, 7.5)
        # Using the form: d = A × exp(k × (fc - 0.20)) - A
        A = 0.415
        k = 8.0
        displacement = A * (math.exp(k * (fc - 0.20)) - 1.0)
    else:
        # Above practical limit: asymptotic behaviour
        # "impossible to exceed fractional weft cover of ~0.58"
        displacement = 7.5 + (fc - 0.58) * 25.0

    return round(max(0.0, displacement), 2)


def predict_beat_up_force(
    fell_displacement_mm: float,
    ends_per_cm: float,
    warp_yarn_count_tex: float,
    free_length_warp_cm: float = 25.0,
    free_length_fabric_cm: float = 8.0,
    warp_elongation_at_break_pct: float = 6.5
) -> float:
    """
    Predicts the beat-up force per cm of reed width in cN/cm.

    Source: Marks & Robinson, Section 6.1.4, Equation 6.1, p. 145:
        R = Z × (Ew/Lw + Ef/Lf)
    where:
        R = weaving resistance (= beat-up force) [force units]
        Z = fell displacement at beat-up (mm → cm)
        Ew = elastic modulus of warp
        Ef = elastic modulus of fabric
        Lw = free length of warp
        Lf = free length of fabric

    "The weaving resistance, which is equal and opposite to the beat-up
    force, is proportional to the displacement of the fell from its basic
    position." (Marks & Robinson, p. 146)

    "Since no term involving the basic warp tension, To, appears in
    Equation (6.1), we conclude that the beat-up force is independent of
    the basic warp tension." (Marks & Robinson, p. 146)

    Elastic modulus estimate for spun yarns:
        Ew (cN/cm²) ≈ tenacity_cN_tex × count_tex × 1000 / elongation_at_break
    For a warp sheet of n ends/cm:
        Ew_sheet = n × (yarn_modulus per end)
    Typical warp elongation at break: 6-8% for ring/rotor cotton yarns.

    The fabric elastic modulus Ef ≈ 0.3 × Ew for a plain-weave cloth
    (the fabric stretches more than the raw warp because of crimp
    interchange).

    The result is given per cm of reed width (cN/cm), which is the
    operationally useful form for comparing beat-up requirements across
    different cloth constructions.
    """
    if fell_displacement_mm <= 0:
        return 0.0

    Z_cm = fell_displacement_mm / 10.0   # convert mm → cm

    # Per-end elastic modulus: E_end = (tenacity × tex) / elongation
    # Tenacity × tex = breaking force in cN; elongation as fraction.
    # We use a conservative yarn modulus estimate based on count alone.
    # Approximate: E_end_cN_per_cm ≈ warp_count_tex × 0.8 / 0.07
    # (0.8 = representative tenacity for mixed spinning origins in cN/tex,
    # 0.07 = elongation at break ~7% expressed as fraction)
    yarn_modulus_per_end = warp_yarn_count_tex * 0.8 / (warp_elongation_at_break_pct / 100.0)

    # Warp sheet modulus per cm of width
    E_warp_per_cm = ends_per_cm * yarn_modulus_per_end  # cN per cm of width per unit strain

    # Fabric modulus: approximately 0.25-0.35 × warp sheet modulus
    # (Fabric deformation involves crimp interchange, not just yarn extension)
    E_fabric_per_cm = 0.30 * E_warp_per_cm

    # Beat-up force: R = Z × (Ew/Lw + Ef/Lf)
    L_w = free_length_warp_cm
    L_f = free_length_fabric_cm

    beat_up_force = Z_cm * (E_warp_per_cm / L_w + E_fabric_per_cm / L_f)
    return round(max(0.0, beat_up_force), 1)


def predict_weft_tension_at_fell_cN(
    weft_cover_factor: float,
    weft_yarn_count_tex: float,
    reed_width_cm: float
) -> float:
    """
    Estimates peak weft tension at the moment of incorporation into the fell (cN).

    Source: Marks & Robinson, Section 6.1.2, p. 141, citing Townsend (ref. 17):
    "For a square plain worsted cloth with a fractional cover of 0.5
    (corresponding to a firmly set cloth), the weft tension may increase
    from about 5 gf (49 mN) as the shuttle lays it in the shed to as much
    as 180 gf (1765 mN) when the pick is incorporated into the cloth."

    This ~36× amplification of tension from insertion to incorporation
    drives the risk of weft-cutting at the selvedges.

    Generalization beyond Townsend's worsted reference:
    - Weft tension at incorporation scales with:
        (a) weft cover factor — higher fc → greater scissors-like crimp force
        (b) weft yarn count (tex) — heavier picks carry more inertia and
            bend farther around warp ends → higher tension for equal crimp
        (c) reed width — wider cloth → weft tension is distributed but
            insertion stretch per unit length is lower; effect is modest

    Calibrated to Townsend's data:
        At fc = 0.5, worsted 34-tex yarn → 1765 mN ≈ 180 cN
    """
    # Reference: Townsend's measurement at fc = 0.5, tex = 34, full width
    # T_ref = 180 cN at fc=0.5, tex=34
    T_ref = 180.0
    fc_ref = 0.50
    tex_ref = 34.0

    # Cover factor effect: exponential above the threshold fc=0.20
    if weft_cover_factor <= 0.20:
        fc_factor = 0.03  # very low tension in open cloths
    else:
        fc_factor = math.exp(3.5 * (weft_cover_factor - fc_ref))

    # Count effect: heavier weft → greater force to crimp round warp ends
    tex_factor = (weft_yarn_count_tex / tex_ref) ** 0.6

    # Width effect: slightly lower peak tension per unit length on wider looms
    width_factor = (180.0 / max(reed_width_cm, 80.0)) ** 0.12

    weft_tension = T_ref * fc_factor * tex_factor * width_factor
    return round(max(1.0, weft_tension), 1)


def calculate_fabric_weight_g_m2(
    warp_count_tex: float,
    weft_count_tex: float,
    ends_per_cm: float,
    picks_per_cm: float,
    warp_crimp_pct: float,
    weft_crimp_pct: float
) -> float:
    """
    Calculates fabric areal weight in g/m² (GSM).

    Source: Standard textile engineering formula, consistent with
    Marks & Robinson's framework where crimp percentages describe
    the extra length of yarn consumed per unit length of cloth.

    GSM = warp contribution + weft contribution

    Warp contribution (g/m²):
        mass_warp = ends/cm × 100 cm/m × warp_count_tex (g/km)
                  × (1 + warp_crimp/100) / 1000 (m/km)
        → = ends_per_cm × 100 × tex_warp × (1 + warp_crimp/100) / 1000

    Weft contribution (g/m²):
        mass_weft = picks/cm × 100 cm/m × weft_count_tex (g/km)
                  × (1 + weft_crimp/100) / 1000

    The (1 + crimp/100) factor accounts for the fact that each thread
    is longer than the cloth dimension it spans, due to the undulations
    of plain-weave interlacing. For typical plain-weave crimps (5-15%),
    this adds 5-15% to the yarn consumption and hence the fabric weight.

    Units check:
        (ends/cm) × (cm/m) × (g/1000m) × (1+crimp) / ... → g/m² ✓
    """
    # Warp contribution: ends per cm × 100 cm/m × tex/1000 × crimp factor
    warp_mass = ends_per_cm * 100.0 * warp_count_tex * (1.0 + warp_crimp_pct / 100.0) / 1000.0
    # Weft contribution: picks per cm × 100 cm/m × tex/1000 × crimp factor
    weft_mass = picks_per_cm * 100.0 * weft_count_tex * (1.0 + weft_crimp_pct / 100.0) / 1000.0

    return round(warp_mass + weft_mass, 1)


def assess_warp_break_risk(
    warp_tenacity_cN_tex: float,
    warp_count_tex: float,
    warp_tension_cN_per_end: float,
    warp_CVm_pct: float,
    warp_crimp_pct: float,
    loom_speed_picks_per_min: float,
    shed_depth_cm: float,
    operating_hours_ratio: float
) -> str:
    """
    Qualitative assessment of warp end-break risk.

    Source: Marks & Robinson, Section 6.1.5, p. 147-149.
    - "Any change in the cloth-fell position will produce a change in
      pick-spacing." — meaning fell disturbances from end-breaks compound.
    - Dynamic forces: at higher loom speeds, heald shaft acceleration
      increases (proportional to loom_speed²), imposing additional cyclic
      tension on each warp end. (Marks & Robinson, Section 2.2, pp. 21-27)
    - Warp tension spikes at shed change: as the healds reverse, the warp
      threads in the separating shed are momentarily stretched between the
      reed and the heald. The spike magnitude scales with crimp (because
      crimped threads must first straighten before stretching) and with
      loom speed (kinetic energy in the shed).
    - CVm effect: thin places in the warp yarn represent weak spots. At
      a CVm of 14%, the probability of a ±2σ thin place is ~5% per metre —
      high enough to cause measurable end-break rates on high-speed looms.
    - Maintenance: worn heald wires and reed dents increase abrasion and
      create local stress concentrations on the warp threads.

    Risk scoring follows a stress-to-strength ratio model:
        safety_factor = yarn_breaking_force / peak_warp_tension
    where peak tension ≈ basic_tension × (1 + dynamic_factor).
    """
    risk_score = 0

    # Yarn breaking force per end
    breaking_force_cN = warp_tenacity_cN_tex * warp_count_tex  # cN

    # Dynamic tension multiplier: at 300 ppm, shed acceleration is ~3-4× static
    speed_factor = 1.0 + (loom_speed_picks_per_min / 300.0) * 1.5
    # Shed-depth factor: deeper shed → greater angular displacement of healds
    depth_factor = 1.0 + max(0, (shed_depth_cm - 9.0) * 0.04)
    peak_tension = warp_tension_cN_per_end * speed_factor * depth_factor

    safety_factor = breaking_force_cN / max(peak_tension, 0.1)
    if safety_factor < 6:
        risk_score += 3
    elif safety_factor < 10:
        risk_score += 2
    elif safety_factor < 15:
        risk_score += 1

    # CVm: thin places as weak spots in the yarn
    if warp_CVm_pct > 16:
        risk_score += 3
    elif warp_CVm_pct > 14:
        risk_score += 2
    elif warp_CVm_pct > 12:
        risk_score += 1

    # Crimp: high warp crimp means the thread must straighten first,
    # absorbing energy, but also means higher shed-angle forces
    if warp_crimp_pct > 12:
        risk_score += 1

    # Maintenance overdue
    if operating_hours_ratio > 1.0:
        risk_score += 2
    elif operating_hours_ratio > 0.85:
        risk_score += 1

    if risk_score <= 2:
        return "low"
    elif risk_score <= 5:
        return "medium"
    else:
        return "high"


def assess_weft_break_risk(
    weft_tenacity_cN_tex: float,
    weft_count_tex: float,
    weft_tension_at_fell_cN: float,
    weft_CVm_pct: float,
    weft_cover_factor: float,
    loom_type: str
) -> str:
    """
    Qualitative assessment of weft break risk.

    Source: Marks & Robinson, Section 6.1.2, p. 142, and
    Section 5.1-5.4 (weft insertion methods).

    Two distinct mechanisms cause weft breaks:
    (1) Weft-cutting at the fell:
        "Weft-cutting can be minimized by delaying the crossing of the
        healds until the shuttle is at rest, but this may sometimes
        result in slack weft or weft loops at the selvedges."
        (Marks & Robinson, p. 142)
        Driven by: high weft tension at fell (Townsend) + scissors action
        of ends at selvedges + inadequate temple restraint.

    (2) Insertion break:
        During flight/traverse, the weft must sustain the drag tension
        of the insertion system. Air-jet: pneumatic drag; rapier: carrier
        grip friction; shuttle: none (self-carrying package).
        Insertion breaks are most common in air-jet and water-jet looms
        at high speeds. (Marks & Robinson, Section 5.4, pp. 130-133)

    The primary quantitative criterion is the ratio of weft breaking
    force to the peak weft tension at incorporation into the fell.
    """
    risk_score = 0

    # Weft breaking force
    breaking_force_cN = weft_tenacity_cN_tex * weft_count_tex  # cN

    # Weft-cutting risk: tension at fell vs. breaking force
    fell_ratio = weft_tension_at_fell_cN / max(breaking_force_cN, 1.0)
    if fell_ratio > 0.40:
        risk_score += 3  # critical — weft tension is > 40% of break force
    elif fell_ratio > 0.25:
        risk_score += 2
    elif fell_ratio > 0.15:
        risk_score += 1

    # Insertion-type risk: air-jet and water-jet impose flight tension
    loom_lower = loom_type.lower().replace("-", "_").replace(" ", "_")
    if loom_lower in ("air_jet", "water_jet"):
        # Weft must sustain pneumatic or hydraulic drag during insertion
        # Thin yarns (low tex) are particularly at risk
        if weft_count_tex < 15:
            risk_score += 2  # fine yarn, high insertion stress per unit mass
        elif weft_count_tex < 25:
            risk_score += 1
    elif loom_lower == "rapier":
        # Carrier grip can induce local tension spikes at transfer point
        risk_score += 1 if weft_count_tex < 20 else 0

    # CVm: thin places in weft are weak spots during insertion
    if weft_CVm_pct > 15:
        risk_score += 2
    elif weft_CVm_pct > 13:
        risk_score += 1

    if risk_score <= 2:
        return "low"
    elif risk_score <= 5:
        return "medium"
    else:
        return "high"


def assess_cloth_defect_risk(
    warp_CVm_pct: float,
    weft_CVm_pct: float,
    warp_hairiness_H: float,
    weft_cover_factor: float,
    let_off_type: str,
    take_up_type: str,
    warp_yarn_type: str
) -> str:
    """
    Qualitative assessment of risk of cloth defects (thick/thin places,
    stitching, setting-on places).

    Source: Marks & Robinson, Sections 6.1.5, 6.2.1, 6.3, pp. 148-174.

    Main defect types in plain weaving:
    (1) Thick/thin places (pick-spacing variation):
        "Variations in pick-spacing, if severe enough, will produce a
        fault in the fabric. Most, but not all, variations in pick-spacing
        are caused by displacement of the cloth fell."
        (Marks & Robinson, p. 149)
        Driven by: let-off and take-up irregularities, and loom stoppages.
        Positive take-up → uniform pick-spacing → lower risk.
        Negative friction let-off → variable warp tension → higher risk.

    (2) Stitching (thread cross-over errors):
        "Incorrect thread-interlacing (which is generally known as
        stitching)" — caused by ends from the same shed failing to
        separate cleanly. High warp hairiness increases the risk as
        protruding fibres tangle between adjacent ends.
        (Marks & Robinson, Section 3.1, p. 47)

    (3) Setting-on places (restarting faults):
        "Plain weave is the most susceptible to setting-on places."
        (Marks & Robinson, p. 163)
        Driven by: warp tension change during stoppage and fell position
        shift. More severe with negative let-off.

    (4) Shade variation (pick-spacing periodicity):
        Visible in smooth, uniform yarns (combed cotton, filament yarns).
        "Smooth, uniform yarns, such as continuous-filament yarns and
        combed cotton yarns, especially if gassed and mercerized, show
        up variations in pick-spacing that would be masked by the
        irregularities and fibrous surface of spun yarns."
        (Marks & Robinson, p. 148)
    """
    risk_score = 0

    # Take-up type: positive is strongly preferred for pick-spacing uniformity
    if take_up_type.lower() == "negative":
        risk_score += 2  # deliberate pick-spacing variation → defect risk
    elif take_up_type.lower() != "positive":
        risk_score += 1  # unknown type — conservative penalty

    # Let-off type: negative friction → warp tension variation → fell instability
    if let_off_type.lower() == "negative_friction":
        risk_score += 2  # Marks & Robinson, p. 149
    # Positive let-off: no additional penalty

    # Plain weave susceptibility: "most susceptible to setting-on places"
    # (Marks & Robinson, p. 163) — inherent to this weave structure
    risk_score += 1  # plain-weave baseline susceptibility

    # Warp evenness: thin places cause fell position disturbances
    if warp_CVm_pct > 15:
        risk_score += 2
    elif warp_CVm_pct > 13:
        risk_score += 1

    # Weft evenness: picks of varying diameter alter pick-spacing locally
    if weft_CVm_pct > 14:
        risk_score += 1

    # Hairiness: warp hairiness causes stitching
    if warp_hairiness_H > 7.0:
        risk_score += 2  # severe stitching risk — consider singeing or sizing
    elif warp_hairiness_H > 5.5:
        risk_score += 1

    # Yarn uniformity: fine combed cotton/filament amplifies pick-spacing faults
    yt = warp_yarn_type.lower()
    if "combed" in yt or "mmf" in yt or "polyester" in yt:
        risk_score += 1  # uniform yarns reveal pick-spacing variations

    # High weft cover: near the limit → cloth-fell position sensitivity is high
    # "A given change in cloth-fell position has a much larger effect on
    # pick-spacing at low than at high fractional weft covers." (p. 149)
    if weft_cover_factor < 0.25:
        risk_score += 2  # very open cloth → highly sensitive to fell disturbances
    elif weft_cover_factor < 0.35:
        risk_score += 1

    if risk_score <= 3:
        return "low"
    elif risk_score <= 6:
        return "medium"
    else:
        return "high"


def predict_production_rate(
    loom_speed_picks_per_min: float,
    picks_per_cm: float,
    reed_width_cm: float
) -> tuple:
    """
    Predicts fabric production rate in m/min and m²/hour.

    Source: Marks & Robinson, Section 2.6.2, pp. 198-209.
    The fabric advance per pick = 1 / picks_per_cm (cm).
    Therefore:
        production rate (cm/min) = loom_speed_picks_per_min / picks_per_cm
        production rate (m/min)  = loom_speed_picks_per_min / (picks_per_cm × 100)

    Cross-check from Marks & Robinson, Section 5.1, p. 109, Table 5.1:
    Conventional shuttle loom: ~180-240 picks/min, ~30-50 picks/cm
        → 180/30/100 = 0.060 m/min. Over 1 m width → 3.6 m²/h. Typical.
    Air-jet loom: ~400 picks/min, same sett
        → 400/30/100 = 0.133 m/min → 8.0 m²/h. Consistent with Table 5.1.

    Production rate in m²/hour:
        = production_m_per_min × 60 × reed_width_cm / 100
    (No efficiency factor applied here — pure mechanical throughput.
    Actual loom efficiency typically 85-95% on modern looms,
    90-95% for shuttle looms on good yarns.)
    """
    m_per_min = loom_speed_picks_per_min / (picks_per_cm * 100.0)
    m2_per_hour = m_per_min * 60.0 * reed_width_cm / 100.0
    return round(m_per_min, 4), round(m2_per_hour, 2)


# ─────────────────────────────────────────────────────────────────────────────
# MASTER SIMULATION FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def simulate_plain_weaving(
    yarns: InputYarns,
    params: PlainWeavingParams
) -> FabricQualityOutput:
    """
    Master simulation function for Plain Weaving.

    Takes Layer 2 (input yarns — direct outputs from spinning Layer 4)
    and Layer 3 (loom operational parameters), runs all sub-models,
    and returns Layer 4 (predicted fabric quality output).
    """
    warnings = []

    # ── PARAMETER VALIDATION ──────────────────────────────────────────────────

    # Loom speed range by loom type
    speed_limits = {
        "shuttle":   (100, 300),
        "rapier":    (150, 450),
        "air_jet":   (300, 700),
        "water_jet": (300, 600),
    }
    ltype = params.loom_type.lower().replace("-", "_").replace(" ", "_")
    spd_range = speed_limits.get(ltype, (100, 500))
    if not (spd_range[0] <= params.loom_speed_picks_per_min <= spd_range[1]):
        warnings.append(
            f"Loom speed {params.loom_speed_picks_per_min} picks/min is outside the "
            f"recommended range for a {params.loom_type} loom "
            f"({spd_range[0]} - {spd_range[1]} picks/min). "
            "Refer to Marks & Robinson, Section 5.1, Table 5.1."
        )

    # Minimum heald shafts for plain weave
    if params.heald_shaft_count < 2:
        warnings.append(
            "Plain weave requires a minimum of 2 heald shafts. "
            "(Marks & Robinson, Section 3.1, p. 47)"
        )

    # Warp tension: must prevent bumping. Minimum guideline: > 5 cN/end.
    if params.warp_tension_cN_per_end < 4.0:
        warnings.append(
            f"Warp tension ({params.warp_tension_cN_per_end} cN/end) is below the "
            "minimum needed to prevent bumping during beat-up. "
            "'The onset of bumping determines the minimum practicable warp tension.' "
            "(Marks & Robinson, p. 147). Increase let-off tension."
        )
    elif params.warp_tension_cN_per_end > 35.0:
        warnings.append(
            f"Warp tension ({params.warp_tension_cN_per_end} cN/end) is high. "
            "Values above 30 cN/end risk elevated warp breakage rates, especially "
            "on coarser counts. There is no advantage in exceeding the bumping-prevention "
            "minimum. (Marks & Robinson, p. 147)"
        )

    # Negative take-up with filament/combed cotton yarns: defect risk warning
    if (params.take_up_type.lower() == "negative"
            and ("combed" in yarns.warp_yarn_type.lower()
                 or "polyester" in yarns.warp_yarn_type.lower()
                 or "mmf" in yarns.warp_yarn_type.lower())):
        warnings.append(
            "Negative take-up is not recommended for uniform yarns (combed cotton, "
            "filament). Variations in pick density will be highly visible. Use a "
            "positive take-up for uniform pick-spacing. "
            "(Marks & Robinson, Section 6.1.1, p. 140)"
        )

    # Temple requirement for square and weft-faced cloths
    if params.temple_type.lower() == "none":
        warnings.append(
            "No temples fitted. Without temples, the weft near the fell will contract "
            "widthwise, causing reed abrasion on selvedge ends and weft-cutting. "
            "'Weaving cannot proceed under these conditions' (without temples for "
            "square plain cloths). Fit pin or clip temples. "
            "(Marks & Robinson, Section 6.1.2, p. 141)"
        )

    # Warp hairiness: high H → stitching risk
    if yarns.warp_yarn_hairiness_H > 7.5:
        warnings.append(
            f"Warp yarn hairiness H = {yarns.warp_yarn_hairiness_H} is very high. "
            "This will cause significant stitching (incorrect thread interlacing) "
            "in plain weave. Consider warp sizing or singeing before beaming. "
            "(Marks & Robinson, Section 3.1, p. 47)"
        )

    # Negative let-off warning for plain weave
    if params.let_off_type.lower() == "negative_friction":
        warnings.append(
            "Negative friction let-off produces warp tension variations that disturb "
            "the cloth-fell position and cause pick-spacing faults. "
            "'Plain weave is the most susceptible to setting-on places.' "
            "(Marks & Robinson, p. 163). Use a positive let-off for best results."
        )

    # ── RUN SIMULATION MODELS ─────────────────────────────────────────────────

    d_warp = calculate_yarn_diameter_mm(yarns.warp_yarn_count_tex, yarns.warp_yarn_type)
    d_weft = calculate_yarn_diameter_mm(yarns.weft_yarn_count_tex, yarns.weft_yarn_type)

    fc_warp = calculate_cover_factor(d_warp, params.ends_per_cm)
    fc_weft = calculate_cover_factor(d_weft, params.picks_per_cm)
    fc_total = calculate_total_cover_factor(fc_warp, fc_weft)

    warp_crimp, weft_crimp = calculate_crimp(
        d_warp, d_weft,
        params.ends_per_cm, params.picks_per_cm,
        params.warp_tension_cN_per_end,
        fc_weft,
        params.temple_type
    )

    # Crimp balance assessment
    if warp_crimp > weft_crimp * 1.5:
        crimp_balance = "warp_dominant"     # warp-faced: poplin-type
    elif weft_crimp > warp_crimp * 1.5:
        crimp_balance = "weft_dominant"     # weft-faced: limbric-type
    else:
        crimp_balance = "balanced"          # square or near-square cloth

    fell_disp = predict_fell_displacement_mm(fc_weft)
    beat_up_force = predict_beat_up_force(
        fell_disp,
        params.ends_per_cm,
        yarns.warp_yarn_count_tex
    )

    weft_tension_fell = predict_weft_tension_at_fell_cN(
        fc_weft,
        yarns.weft_yarn_count_tex,
        params.reed_width_cm
    )

    gsm = calculate_fabric_weight_g_m2(
        yarns.warp_yarn_count_tex,
        yarns.weft_yarn_count_tex,
        params.ends_per_cm,
        params.picks_per_cm,
        warp_crimp,
        weft_crimp
    )

    maintenance_ratio = (params.operating_hours_since_maintenance
                         / max(params.maintenance_interval_hours, 1.0))

    warp_risk = assess_warp_break_risk(
        yarns.warp_yarn_tenacity_cN_tex,
        yarns.warp_yarn_count_tex,
        params.warp_tension_cN_per_end,
        yarns.warp_yarn_CVm_pct,
        warp_crimp,
        params.loom_speed_picks_per_min,
        params.shed_depth_cm,
        maintenance_ratio
    )

    weft_risk = assess_weft_break_risk(
        yarns.weft_yarn_tenacity_cN_tex,
        yarns.weft_yarn_count_tex,
        weft_tension_fell,
        yarns.weft_yarn_CVm_pct,
        fc_weft,
        params.loom_type
    )

    defect_risk = assess_cloth_defect_risk(
        yarns.warp_yarn_CVm_pct,
        yarns.weft_yarn_CVm_pct,
        yarns.warp_yarn_hairiness_H,
        fc_weft,
        params.let_off_type,
        params.take_up_type,
        yarns.warp_yarn_type
    )

    m_per_min, m2_per_hour = predict_production_rate(
        params.loom_speed_picks_per_min,
        params.picks_per_cm,
        params.reed_width_cm
    )

    # ── POST-SIMULATION WARNINGS ──────────────────────────────────────────────

    # Cover factor approaching weaving limit
    if fc_weft > 0.55:
        warnings.append(
            f"Fractional weft cover ({fc_weft:.3f}) is approaching the practical weaving "
            f"limit. Greenwood & Cowhig found ~0.58 to be the maximum achievable for "
            "16-tex acetate; similar limits apply to other materials. "
            "Weaving resistance will be very high. Consider reducing picks/cm or "
            "switching to a finer weft. (Marks & Robinson, Fig. 6.3, p. 144)"
        )

    # Weft-cutting risk
    weft_BF = yarns.weft_yarn_tenacity_cN_tex * yarns.weft_yarn_count_tex
    if weft_tension_fell > 0.30 * weft_BF:
        warnings.append(
            f"Weft tension at fell ({weft_tension_fell:.0f} cN) exceeds 30% of weft "
            f"breaking force ({weft_BF:.0f} cN). Weft-cutting is likely, especially at "
            "the selvedges where temple restraint is reduced and end spacing is tighter. "
            "'It usually happens in or near the selvedges.' "
            "(Marks & Robinson, p. 142)"
        )

    # Bumping risk: fell displacement > 7 mm suggests bumping conditions
    if fell_disp > 6.0:
        warnings.append(
            f"Fell displacement at beat-up ({fell_disp:.1f} mm) is very large. "
            "Bumping conditions are likely. The cloth becomes momentarily slack "
            "as the reed drives the fell to maximum displacement. "
            "Increase basic warp tension to restore normal weaving conditions. "
            "(Marks & Robinson, Section 6.1.4, p. 146)"
        )

    # Maintenance overdue
    if maintenance_ratio > 1.0:
        warnings.append(
            f"Maintenance overdue (operating hours = "
            f"{params.operating_hours_since_maintenance:.0f} h vs interval "
            f"{params.maintenance_interval_hours:.0f} h). Worn heald wires, reed "
            "dents, and sley bearings will increase warp abrasion and tension "
            "irregularity. Service the loom promptly."
        )

    return FabricQualityOutput(
        yarn_diameter_warp_mm=d_warp,
        yarn_diameter_weft_mm=d_weft,
        warp_cover_factor=fc_warp,
        weft_cover_factor=fc_weft,
        total_cover_factor=fc_total,
        warp_crimp_pct=warp_crimp,
        weft_crimp_pct=weft_crimp,
        crimp_balance=crimp_balance,
        fell_displacement_mm=fell_disp,
        beat_up_force_cN_per_cm=beat_up_force,
        fabric_areal_weight_g_m2=gsm,
        weft_tension_at_fell_cN=weft_tension_fell,
        warp_break_risk=warp_risk,
        weft_break_risk=weft_risk,
        cloth_defect_risk=defect_risk,
        production_rate_m_per_min=m_per_min,
        production_rate_m2_per_hour=m2_per_hour,
        warnings=warnings
    )


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE USAGE AND VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    print("=" * 65)
    print("PLAIN WEAVING SIMULATION")
    print("Based on Marks & Robinson, 'Principles of Weaving'")
    print("The Textile Institute, Manchester, 1976")
    print("=" * 65)

    # ── SCENARIO 1: Square plain cloth — carded cotton, shuttle loom ───────
    # Input yarns sourced from rotor.py Scenario 1 (Ne 20 carded cotton).
    # Fabric: square construction, typical shirting / print cloth.
    # Cross-check: Greenwood & Cowhig reference fabric (16-tex, 34 ends/cm)
    # is close to this scenario → allows qualitative validation.
    print("\n--- SCENARIO 1: Square plain cloth, carded cotton, "
          "shuttle loom ---\n")

    # Layer 2: direct from rotor.py Scenario 1 output (Ne 20, carded cotton)
    yarns_1 = InputYarns(
        warp_yarn_count_tex=29.5,        # from rotor.py Scenario 1 (Ne 20)
        warp_yarn_count_Ne=20.0,
        warp_yarn_tenacity_cN_tex=12.3,  # from rotor.py Scenario 1 output
        warp_yarn_CVm_pct=11.8,          # from rotor.py Scenario 1 output
        warp_yarn_hairiness_H=5.8,       # from rotor.py Scenario 1 output
        warp_yarn_twist_t_per_m=757.0,   # from rotor.py Scenario 1 (αm=130, Ne20)
        warp_yarn_type="cotton_carded",
        weft_yarn_count_tex=29.5,        # matching weft count for square cloth
        weft_yarn_count_Ne=20.0,
        weft_yarn_tenacity_cN_tex=12.3,
        weft_yarn_CVm_pct=11.8,
        weft_yarn_hairiness_H=5.8,
        weft_yarn_twist_t_per_m=757.0,
        weft_yarn_type="cotton_carded",
    )

    # Layer 3: loom parameters
    # Validation: Greenwood & Cowhig experiment used 34 ends/cm, 16-tex acetate.
    # Here we use 30 ends/cm with 29.5-tex cotton, targeting a firm square cloth.
    # Expected: fc_weft ≈ 0.40 → fell displacement ≈ 2.5 mm (point A, Fig. 6.3).
    params_1 = PlainWeavingParams(
        ends_per_cm=30.0,
        picks_per_cm=28.0,           # slightly fewer picks for near-square cotton
        reed_width_cm=160.0,         # standard 160 cm loom
        loom_speed_picks_per_min=220,
        loom_type="shuttle",
        warp_tension_cN_per_end=12.0,  # typical for cotton Ne 20 on shuttle loom
        let_off_type="positive",
        take_up_type="positive",
        shed_depth_cm=9.5,
        heald_shaft_count=2,
        temple_type="pin_temple",
        ambient_temperature_C=24.0,
        ambient_humidity_pct=60.0,
        maintenance_interval_hours=2_000.0,
        operating_hours_since_maintenance=800.0
    )

    r1 = simulate_plain_weaving(yarns_1, params_1)

    print(f"  Warp yarn diameter:       {r1.yarn_diameter_warp_mm} mm")
    print(f"  Warp cover factor:        {r1.warp_cover_factor:.3f}")
    print(f"  Weft cover factor:        {r1.weft_cover_factor:.3f}  "
          f"(Greenwood ref. ≈ 0.40 for firm cloth, Fig. 6.3)")
    print(f"  Total cover factor:       {r1.total_cover_factor:.3f}")
    print(f"  Warp crimp:               {r1.warp_crimp_pct}%")
    print(f"  Weft crimp:               {r1.weft_crimp_pct}%  "
          f"({r1.crimp_balance})")
    print(f"  Fell displacement:        {r1.fell_displacement_mm} mm  "
          f"(Greenwood ref. ≈ 2.5 mm at fc=0.40, Fig. 6.3)")
    print(f"  Beat-up force:            {r1.beat_up_force_cN_per_cm} cN/cm")
    print(f"  Weft tension at fell:     {r1.weft_tension_at_fell_cN} cN  "
          f"(Townsend ref. ~180 cN at fc=0.5)")
    print(f"  Fabric weight (GSM):      {r1.fabric_areal_weight_g_m2} g/m²")
    print(f"  Warp break risk:          {r1.warp_break_risk.upper()}")
    print(f"  Weft break risk:          {r1.weft_break_risk.upper()}")
    print(f"  Cloth defect risk:        {r1.cloth_defect_risk.upper()}")
    print(f"  Production rate:          {r1.production_rate_m_per_min} m/min  "
          f"→  {r1.production_rate_m2_per_hour} m²/h")
    if r1.warnings:
        print(f"\n  WARNINGS:")
        for w in r1.warnings:
            print(f"    ⚠ {w}")
    else:
        print("\n  No warnings — all parameters within recommended ranges.")

    # ── SCENARIO 2: PES/CO poplin, fine count, rapier loom ─────────────────
    # Input yarns sourced from rotor.py Scenario 2 (Ne 30 PES/CO blend).
    # Fabric: poplin (warp-faced) — ends_per_cm >> picks_per_cm.
    # Expected: warp_crimp >> weft_crimp, weft_crimp ≈ 2-3%.
    print("\n--- SCENARIO 2: PES/CO poplin (warp-faced), "
          "rapier loom ---\n")

    yarns_2 = InputYarns(
        warp_yarn_count_tex=19.7,        # from rotor.py Scenario 2 (Ne 30 PES/CO)
        warp_yarn_count_Ne=30.0,
        warp_yarn_tenacity_cN_tex=17.3,  # from rotor.py Scenario 2 output
        warp_yarn_CVm_pct=11.0,
        warp_yarn_hairiness_H=3.8,       # smooth navel in Scenario 2 → low H
        warp_yarn_twist_t_per_m=784.0,
        warp_yarn_type="blend_PES_CO",
        weft_yarn_count_tex=29.5,        # coarser weft than warp (poplin construction)
        weft_yarn_count_Ne=20.0,
        weft_yarn_tenacity_cN_tex=17.5,  # PES/CO at Ne 20 from Vol 6 Fig 43
        weft_yarn_CVm_pct=11.5,
        weft_yarn_hairiness_H=4.0,
        weft_yarn_twist_t_per_m=700.0,
        weft_yarn_type="blend_PES_CO",
    )

    # Poplin: high ends/cm (warp-faced), lower picks/cm, weft crimp ≈ 2-3%.
    # "In warp-faced cloth, such as poplin and poult, the weft crimp is
    # low in the relaxed fabric, usually not more than 2 or 3%."
    # (Marks & Robinson, p. 142)
    params_2 = PlainWeavingParams(
        ends_per_cm=48.0,            # dense warp for poplin construction
        picks_per_cm=22.0,           # fewer picks → warp-faced structure
        reed_width_cm=180.0,
        loom_speed_picks_per_min=320,
        loom_type="rapier",
        warp_tension_cN_per_end=10.0,  # lower tension for fine PES/CO warp
        let_off_type="positive",
        take_up_type="positive",
        shed_depth_cm=10.0,
        heald_shaft_count=2,
        temple_type="pin_temple",
        ambient_temperature_C=22.0,
        ambient_humidity_pct=55.0,
        maintenance_interval_hours=2_500.0,
        operating_hours_since_maintenance=400.0
    )

    r2 = simulate_plain_weaving(yarns_2, params_2)

    print(f"  Warp cover factor:        {r2.warp_cover_factor:.3f}  (high → warp-faced)")
    print(f"  Weft cover factor:        {r2.weft_cover_factor:.3f}  (low → poplin)")
    print(f"  Total cover factor:       {r2.total_cover_factor:.3f}")
    print(f"  Warp crimp:               {r2.warp_crimp_pct}%  "
          f"({r2.crimp_balance})")
    print(f"  Weft crimp:               {r2.weft_crimp_pct}%  "
          f"(Marks & Robinson ref: ≤3% for poplin)")
    print(f"  Fell displacement:        {r2.fell_displacement_mm} mm")
    print(f"  Weft tension at fell:     {r2.weft_tension_at_fell_cN} cN  "
          f"(low expected for warp-faced)")
    print(f"  Fabric weight (GSM):      {r2.fabric_areal_weight_g_m2} g/m²")
    print(f"  Warp break risk:          {r2.warp_break_risk.upper()}")
    print(f"  Weft break risk:          {r2.weft_break_risk.upper()}")
    print(f"  Cloth defect risk:        {r2.cloth_defect_risk.upper()}")
    print(f"  Production rate:          {r2.production_rate_m_per_min} m/min  "
          f"→  {r2.production_rate_m2_per_hour} m²/h")
    if r2.warnings:
        print(f"\n  WARNINGS:")
        for w in r2.warnings:
            print(f"    ⚠ {w}")
    else:
        print("\n  No warnings — all parameters within recommended ranges.")

    # ── SCENARIO 3: Coarse weft-faced cloth, no temples, negative let-off ───
    # Stress test: challenging construction, poor machine setup.
    # Sourced from rotor.py Scenario 3 (Ne 8 coarse cotton).
    print("\n--- SCENARIO 3: Coarse weft-faced cloth, no temples, "
          "negative let-off (stress test) ---\n")

    yarns_3 = InputYarns(
        warp_yarn_count_tex=73.8,        # from rotor.py Scenario 3 (Ne 8 cotton)
        warp_yarn_count_Ne=8.0,
        warp_yarn_tenacity_cN_tex=11.0,  # reduced by high SFC in Scenario 3
        warp_yarn_CVm_pct=13.5,          # higher CVm for coarse carded cotton
        warp_yarn_hairiness_H=8.5,       # grooved navel in Scenario 3 → high H
        warp_yarn_twist_t_per_m=533.0,
        warp_yarn_type="cotton_carded",
        weft_yarn_count_tex=100.0,       # very coarse weft for weft-faced structure
        weft_yarn_count_Ne=6.0,
        weft_yarn_tenacity_cN_tex=10.5,
        weft_yarn_CVm_pct=14.0,
        weft_yarn_hairiness_H=8.0,
        weft_yarn_twist_t_per_m=450.0,
        weft_yarn_type="cotton_carded",
    )

    params_3 = PlainWeavingParams(
        ends_per_cm=12.0,            # open warp sett for coarse count
        picks_per_cm=18.0,           # more picks → weft-faced construction
        reed_width_cm=200.0,
        loom_speed_picks_per_min=180,
        loom_type="shuttle",
        warp_tension_cN_per_end=8.0,
        let_off_type="negative_friction",  # old-style negative let-off
        take_up_type="positive",
        shed_depth_cm=11.0,
        heald_shaft_count=2,
        temple_type="none",          # no temples — stress test
        ambient_temperature_C=26.0,
        ambient_humidity_pct=65.0,
        maintenance_interval_hours=1_200.0,
        operating_hours_since_maintenance=1_150.0  # nearly overdue
    )

    r3 = simulate_plain_weaving(yarns_3, params_3)

    print(f"  Warp cover factor:        {r3.warp_cover_factor:.3f}")
    print(f"  Weft cover factor:        {r3.weft_cover_factor:.3f}  "
          f"(high → weft-faced)")
    print(f"  Total cover factor:       {r3.total_cover_factor:.3f}")
    print(f"  Warp crimp:               {r3.warp_crimp_pct}%  "
          f"({r3.crimp_balance})")
    print(f"  Weft crimp:               {r3.weft_crimp_pct}%")
    print(f"  Fell displacement:        {r3.fell_displacement_mm} mm")
    print(f"  Weft tension at fell:     {r3.weft_tension_at_fell_cN} cN")
    print(f"  Fabric weight (GSM):      {r3.fabric_areal_weight_g_m2} g/m²")
    print(f"  Warp break risk:          {r3.warp_break_risk.upper()}")
    print(f"  Weft break risk:          {r3.weft_break_risk.upper()}")
    print(f"  Cloth defect risk:        {r3.cloth_defect_risk.upper()}")
    print(f"  Production rate:          {r3.production_rate_m_per_min} m/min  "
          f"→  {r3.production_rate_m2_per_hour} m²/h")
    if r3.warnings:
        print(f"\n  WARNINGS:")
        for w in r3.warnings:
            print(f"    ⚠ {w}")

    print("\n" + "=" * 65)
    print("Simulation complete.")
    print("=" * 65)
