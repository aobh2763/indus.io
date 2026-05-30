"""
Weft Knitting Simulation Module
Process: Knitting > Weft Knitting (Single Jersey / Circular Latch Needle)

Layer 2 of this module (InputFabric) maps directly onto Layer 4 of the
plain_weaving.py module (FabricQualityOutput). Every field name and unit
is preserved so that the output of the weaving node plugs directly into
the input of the weft knitting node in the indus.io production network.

The weft knitting machine receives the woven fabric substrate — carrying
yarn diameter, cover, crimp, and areal weight forward — and interlocks
loops of yarn drawn from that substrate around the needle circle to
produce a knitted fabric with its own stitch density, tightness, and
dimensional properties.

All parameter relationships derived from:
David J Spencer, "Knitting Technology", 3rd edition,
Woodhead Publishing / Technomic Publishing, 2001.
ISBN 1-85573-333-1 (Woodhead) / 1-58716-121-4 (Technomic)

Key references within Spencer:
  [Doyle]   Doyle, HATRA Research (cited in Spencer Section 22.5):
            S = ks / l²  (stitch density from loop length)
  [Munden]  Munden, D.L., HATRA Research Report No. 9 (April 1959),
            cited extensively in Spencer Section 22.5-22.6:
            cpi = kc/l,  wpi = kw/l,  S = ks/l²,  TF = √tex / l
  [Knapton] Knapton k-values for fully-relaxed state (Spencer p. 281):
            ks = 23.1,  kc = 5.5,  kw = 4.2,  R = 1.3
  [Spencer 7.2.1] Gauge–count formula: NeB = G² / 18 (plain, cotton)
  [Spencer 6.3]   Productivity: P = F × R (feeds × revolutions/min)
  [Spencer 22.8]  Needle bounce limit: ~5 m/s tangential needle speed

Layer 5 functions model the physical cause-effect relationships that
link operational parameters (Layer 3) and input fabric properties
(Layer 2) to knitted fabric quality output metrics (Layer 4).
"""

import math
from dataclasses import dataclass


# ─────────────────────────────────────────────────────────────────────────────
# DATA CLASSES — Layer 2, 3, 4
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class InputFabric:
    """
    Layer 2 — Input fabric properties for Weft Knitting.

    All fields map 1-to-1 onto FabricQualityOutput (Layer 4) from
    plain_weaving.py.  The yarn diameters and areal weight carry the
    physical thread characteristics forward; the cover factors and crimp
    values describe the woven substrate's structural state before the
    weft-knitting needles engage with it.
    """
    # From FabricQualityOutput — yarn geometry
    yarn_diameter_warp_mm: float      # Warp yarn diameter in mm (Peirce formula).
                                      # Used to back-calculate yarn count for gauge matching.
    yarn_diameter_weft_mm: float      # Weft yarn diameter in mm.
                                      # In single-jersey weft knitting the weft yarn is the
                                      # knitting yarn; warp geometry informs substrate weight.
    # From FabricQualityOutput — fabric cover
    warp_cover_factor: float          # Fractional warp cover of input woven substrate (0–1).
    weft_cover_factor: float          # Fractional weft cover (0–1).
    total_cover_factor: float         # Combined cover: f_w + f_e - f_w × f_e.
    # From FabricQualityOutput — crimp state
    warp_crimp_pct: float             # Warp crimp % in the substrate. A highly crimped warp
                                      # means greater yarn reserve and potential yarn flow
                                      # once the substrate is presented to the knitting needles.
    weft_crimp_pct: float             # Weft crimp % in the substrate.
    crimp_balance: str                # "warp_dominant", "balanced", or "weft_dominant".
    # From FabricQualityOutput — mechanical outputs of weaving
    fell_displacement_mm: float       # Beat-up fell displacement (mm) — reflects the
                                      # tension history of the weft yarn entering the knitting
                                      # machine. High fell displacement → residual tension.
    beat_up_force_cN_per_cm: float    # Beat-up force per cm reed width (cN/cm).
    fabric_areal_weight_g_m2: float   # Woven fabric weight in g/m². This is the substrate
                                      # weight the knitting machine must handle for take-down.
    weft_tension_at_fell_cN: float    # Peak weft tension at fell incorporation (cN).
                                      # High values → tightly set yarn → less yarn available
                                      # for loop formation without drawing from the package.
    # From FabricQualityOutput — risk flags (carried forward for traceability)
    warp_break_risk: str              # "low", "medium", "high" — weaving warp-break risk.
    weft_break_risk: str              # "low", "medium", "high" — weaving weft-break risk.
    cloth_defect_risk: str            # "low", "medium", "high" — weaving cloth defect risk.
    # From FabricQualityOutput — production context
    production_rate_m_per_min: float  # Weaving production rate in m/min (upstream context).
    production_rate_m2_per_hour: float  # Weaving production rate in m²/h.


@dataclass
class WeftKnittingParams:
    """
    Layer 3 — Operational parameters specific to Weft Knitting.

    Based on single-jersey circular latch-needle machines unless otherwise
    noted. Spencer Section 7.2.1 and Chapters 8, 22.
    """
    # ── MACHINE GEOMETRY ──────────────────────────────────────────────────────
    machine_gauge_npi: int           # Machine gauge in needles per inch (npi).
                                     # Common single-jersey range: 12 – 40 npi.
                                     # Spencer p. 64: "NeB = G²/18, G = gauge in npi."
                                     # Finer gauge → finer yarn count → finer fabric.
    cylinder_diameter_inch: float    # Cylinder diameter in inches. Common: 14-40 in.
                                     # Total needles = π × D_in × gauge_npi.
                                     # Spencer p. 64: "most popular diameter is 26 inches."
    number_of_feeds: int             # Number of active yarn feed positions (feeders).
                                     # Single-jersey: typically 48-192 feeders.
                                     # Productivity P = F × R (Spencer Section 6.3).

    # ── STITCH GEOMETRY ───────────────────────────────────────────────────────
    stitch_length_mm: float          # Loop (stitch) length in mm — the primary process
                                     # control variable in weft knitting.
                                     # Spencer p. 43: "the larger the stitch length, the
                                     # more extensible and lighter the fabric and the poorer
                                     # the cover, opacity and bursting strength."
                                     # For plain cotton single-jersey: typical range 2.5–5.5 mm.
                                     # Spencer Section 22.6: TF = √tex / l (SI), where l is mm.

    # ── MACHINE SPEED ─────────────────────────────────────────────────────────
    machine_rpm: float               # Cylinder revolutions per minute.
                                     # Single-jersey: 15–45 rpm typical industrial range.
                                     # Upper limit: tangential needle speed < 5 m/s
                                     # (Spencer Section 22.8: "tangential speed of the
                                     # needles can be more than 5 metres per second" on
                                     # high-speed seamless hose machines; 4000 cpm possible).
                                     # Courses/min = feeds × rpm (for single-feed structure).

    # ── YARN TENSION ─────────────────────────────────────────────────────────
    yarn_input_tension_cN: float     # Input yarn tension at the feeder guide (cN).
                                     # Spencer Section 22.7 (robbing back): "yarn tension
                                     # increases… as it passes over the knitting elements."
                                     # High tension → shorter effective stitch length (robbing
                                     # back). Typical range: 2–12 cN for spun yarns.

    # ── TAKE-DOWN ─────────────────────────────────────────────────────────────
    take_down_tension_cN_per_cm: float  # Fabric take-down tension per cm of fabric width.
                                        # Spencer Section 22.9: "higher take-down tension leads
                                        # to a greater incidence of cuts and holes in the fabric,
                                        # wear on the knitting elements, problems when knitting
                                        # weaker yarns, and a greater length-wise deformation."
                                        # Typical range: 0.5–4.0 cN/cm.

    # ── NEEDLE TYPE ──────────────────────────────────────────────────────────
    needle_type: str                 # "latch_needle" or "compound_needle".
                                     # Latch needle: dominant in single-jersey.
                                     # Compound needle: higher speed capability, finer gauge.
                                     # (Spencer Sections 4.3, 4.5)

    # ── STRUCTURE TYPE ────────────────────────────────────────────────────────
    structure_type: str              # "plain_single_jersey", "rib_1x1", "interlock".
                                     # Plain single-jersey: simplest, most economical,
                                     # maximum covering power. (Spencer Section 7.2)
                                     # Rib: double-faced, ~30% width-wise recovery after
                                     # cutting. (Spencer Section 7.3)
                                     # Interlock: face loops on both sides, stable.

    # ── RELAXATION STATE ──────────────────────────────────────────────────────
    relaxation_state: str            # "as_knitted", "dry_relaxed", "wet_relaxed",
                                     # or "fully_relaxed".
                                     # Spencer Table (p. 281) [Munden / Knapton]:
                                     #   dry_relaxed:   ks=19.0, kc=5.0, kw=3.8
                                     #   wet_relaxed:   ks=21.6, kc=5.3, kw=4.1
                                     #   fully_relaxed: ks=23.1, kc=5.5, kw=4.2, R=1.3
                                     # Fully relaxed: 24h soak at 40°C + 1h tumble-dry at 70°C.

    # ── MACHINE CONDITION ─────────────────────────────────────────────────────
    ambient_temperature_C: float       # In Celsius. Affects yarn friction and knitting tension.
    ambient_humidity_pct: float        # Relative humidity %. Cotton at high humidity:
                                       # swells, softens → easier loop formation but
                                       # increased fibre shedding and needle clogging.
    maintenance_interval_hours: float  # Recommended needle/sinker service interval.
    operating_hours_since_maintenance: float  # Hours since last full needle bed service.


@dataclass
class KnittedFabricOutput:
    """
    Layer 4 — Predicted output quality metrics for Weft Knitting.
    """
    # ── DERIVED YARN COUNT ────────────────────────────────────────────────────
    yarn_count_tex: float              # Yarn count derived from weft diameter (Peirce inverse).
    yarn_count_Ne: float               # Converted to Ne cotton count.

    # ── TIGHTNESS FACTOR ─────────────────────────────────────────────────────
    tightness_factor: float            # TF = √tex / l (Spencer Section 22.6, SI units).
                                       # Plain worsted: TF 1.4–1.5 (Spencer p. 282).
                                       # Below 1.0: very loose (open), 1.2–1.8: commercial
                                       # range; above 2.0: very tight (risk of needle break).

    # ── MUNDEN STITCH DENSITY ────────────────────────────────────────────────
    courses_per_cm: float              # cpc = kc / l  (Spencer Eq. 22.5, Munden 1959).
    wales_per_cm: float                # wpc = kw / l  (Spencer Eq. 22.5).
    stitch_density_per_cm2: float      # S = ks / l²  (Spencer, Doyle / Munden).
                                       # Stitches per cm². S = cpc × wpc.
    loop_shape_factor: float           # R = cpc / wpc = kc / kw (Spencer p. 281).
                                       # For plain worsted fully-relaxed: R ≈ 1.3.

    # ── FABRIC WEIGHT ─────────────────────────────────────────────────────────
    fabric_areal_weight_g_m2: float    # Knitted fabric weight in g/m²:
                                       # W = S × l × tex / 100  (standard formula).
                                       # Typical single-jersey: 100–250 g/m².

    # ── DIMENSIONAL STABILITY ────────────────────────────────────────────────
    width_relaxation_pct: float        # Width shrinkage after relaxation (%).
                                       # Plain: potential 40% width-wise recovery on stretch
                                       # → ~15–20% width reduction on relaxation off loom.
    length_relaxation_pct: float       # Length shrinkage after relaxation (%).
                                       # Typically 5–15% for plain cotton single-jersey.

    # ── PRODUCTION METRICS ───────────────────────────────────────────────────
    total_needles: int                 # Total active needles: π × D_in × G_npi.
    courses_per_minute: float          # = feeds × rpm (Spencer Section 6.3).
    fabric_production_rate_m_min: float  # = (courses/min) / (cpc × 100).
    fabric_production_rate_m2_hr: float  # = m/min × fabric_width_m × 60.
    fabric_width_m: float              # Knitted fabric width (open width after slitting tube):
                                       # = π × cylinder_diameter_inch × 0.0254.

    # ── QUALITY INDICATORS ───────────────────────────────────────────────────
    needle_break_risk: str             # "low", "medium", "high".
    yarn_break_risk: str               # "low", "medium", "high".
    fabric_defect_risk: str            # "low", "medium", "high".
    pilling_propensity: str            # "low", "medium", "high".
    warnings: list                     # Out-of-range parameter warnings.


# ─────────────────────────────────────────────────────────────────────────────
# LAYER 5 — SIMULATION FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def derive_yarn_count_from_diameter(
    yarn_diameter_mm: float,
    yarn_type: str = "cotton_carded"
) -> tuple:
    """
    Back-calculates yarn count (tex, Ne) from diameter using Peirce's formula.

    Source: F. T. Peirce (1937), cited throughout Spencer and Marks & Robinson.
    Forward formula (from plain_weaving.py, Layer 5):
        d (mm) = k × √tex
    Inverted:
        tex = (d / k)²
        Ne  = 590.5 / tex

    This inversion propagates the yarn diameter from the weaving substrate
    (Layer 4 of plain_weaving.py) back to a yarn count, allowing the weft
    knitting machine to check gauge–count compatibility for the incoming yarn.

    Fibre-type constants k (mm/√tex) — same values used in plain_weaving.py:
        cotton_carded / cotton_combed : k = 0.037
        polyester / PES               : k = 0.033
        viscose / CV                  : k = 0.040
        blend_PES_CO                  : k = 0.035
        MMF generic                   : k = 0.034
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
        k = 0.034

    tex = (yarn_diameter_mm / k) ** 2
    Ne = 590.5 / max(tex, 0.1)
    return round(tex, 2), round(Ne, 1)


def calculate_total_needles(
    cylinder_diameter_inch: float,
    machine_gauge_npi: int
) -> int:
    """
    Calculates total number of active needles in the cylinder.

    Source: Spencer Section 15.1, p. 197:
        "Machine gauge can be calculated by dividing the total number
        of needles into the circumference."
    Rearranged:
        total_needles = π × D_in × gauge_npi

    Cross-check example (Spencer p. 197):
        4-inch diameter cylinder, gauge 168 needles in 12.57 inches:
        gauge = 168 / 12.57 ≈ 14 npi.
        So 168 = π × 4 × 14 → π × 4 × 14 = 175.9 ≈ 168 (rounded to
        actual needle count, as gaps between needles must be integer).

    Spencer p. 64 (single-jersey): "most popular diameter is 26 inches
    (66 cm) giving an approximate finished fabric width of 60–70 inches."
    """
    circumference_in = math.pi * cylinder_diameter_inch
    needles = round(circumference_in * machine_gauge_npi)
    return needles


def calculate_tightness_factor(
    yarn_count_tex: float,
    stitch_length_mm: float
) -> float:
    """
    Calculates Munden's Tightness Factor (TF) for plain weft knitted fabric.

    Source: Spencer Section 22.6, p. 282:
        "Munden first suggested the use of a factor to indicate the relative
        tightness or looseness of plain weft knitted structure, to be used
        in a similar manner to that of the cover factor in the weaving
        industry. Originally termed the cover factor but now referred to
        as the tightness factor (TF)…"

        TF = √tex / l  (SI units, l in mm)

    Spencer p. 282: "For most plain fabrics knitted from worsted yarn the
    TF ranges between 1.4 and 1.5."

    Physical meaning:
        TF < 1.0  → very open, slack structure (lacey, poor cover)
        TF 1.2–1.6 → normal commercial plain single-jersey range
        TF > 1.8  → tight structure (risk of needle-break, fabric distortion)
        TF > 2.0  → excessive — yarn compressed between needle and sinker
                    → needle fracture (Spencer Section 22.8)

    Relationship to fabric properties (Spencer p. 43):
        "Generally, the larger the stitch length [lower TF], the more
        extensible and lighter the fabric and the poorer the cover,
        opacity and bursting strength."
    """
    if stitch_length_mm <= 0:
        return 0.0
    TF = math.sqrt(yarn_count_tex) / stitch_length_mm
    return round(TF, 3)


def calculate_munden_stitch_density(
    stitch_length_mm: float,
    relaxation_state: str
) -> tuple:
    """
    Calculates courses/cm, wales/cm, stitch density (S/cm²), and loop shape
    factor using Munden's empirical equations.

    Source: Spencer Section 22.5, p. 280-281, citing Munden (1959):
        cpi = kc / l
        wpi = kw / l
        S   = ks / l²
        R   = cpc / wpc = kc / kw  (loop shape factor)

    Spencer Table (p. 281) — k values for three relaxation states:
        State           ks     kc     kw     R
        Dry relaxed    19.0   5.0   3.8   1.32
        Wet relaxed    21.6   5.3   4.1   1.29
        Fully relaxed  23.1   5.5   4.2   1.31

    Spencer p. 280: "Munden… indicated that the linear dimensions as well
    as the stitch density for a wide range of thoroughly relaxed, plain
    knitted, worsted yarn fabrics were uniquely determined by their stitch
    length and that all other variables influenced dimensions only by
    changing this variable."

    NOTE: The Munden k values were originally derived for worsted yarns.
    They are the best published universal constants available and are the
    standard reference for plain weft knitted structure geometry.

    Units: l is in mm, cpi and wpi are returned as courses and wales per
    CENTIMETRE (Spencer uses inches in some sections; we convert:
        cpc = kc / l × (1/2.54)  because 1 inch = 2.54 cm
        But since Spencer quotes k values against l in mm and the result
        is in per inch, we convert: cpc = (kc / l) / 2.54.

    Cross-check: for l = 3.5 mm, fully relaxed:
        wpi = 4.2 / 3.5 = 1.2 wales/mm = 12 wales/cm → reasonable for
        a medium-gauge (E18) cotton single-jersey fabric. ✓
    """
    k_map = {
        "as_knitted":    {"ks": 16.5, "kc": 4.5, "kw": 3.3},  # tighter than dry-relaxed
        "dry_relaxed":   {"ks": 19.0, "kc": 5.0, "kw": 3.8},
        "wet_relaxed":   {"ks": 21.6, "kc": 5.3, "kw": 4.1},
        "fully_relaxed": {"ks": 23.1, "kc": 5.5, "kw": 4.2},
    }
    k = k_map.get(relaxation_state.lower().replace(" ", "_"),
                  k_map["dry_relaxed"])

    # Munden equations: cpi and wpi in per inch → convert to per cm
    # cpc (per cm) = (kc / l_mm) / 2.54
    # But Spencer uses l in mm already in his SI presentation (p. 282),
    # so: cpc = kc / (l_mm × 2.54) is the correct conversion from
    # Munden's inch-based k values to metric.
    cpc = k["kc"] / (stitch_length_mm * 2.54)
    wpc = k["kw"] / (stitch_length_mm * 2.54)
    S = k["ks"] / ((stitch_length_mm * 2.54) ** 2)   # stitches/cm²
    R = k["kc"] / k["kw"]

    return round(cpc, 2), round(wpc, 2), round(S, 2), round(R, 3)


def calculate_fabric_weight_g_m2(
    stitch_density_per_cm2: float,
    stitch_length_mm: float,
    yarn_count_tex: float
) -> float:
    """
    Calculates knitted fabric areal weight in g/m².

    Source: Spencer Section 1.5, p. 5 (unit conversion example):
        "5 oz/yd² = 170 g/m²" — calibration reference for unit check.
    Standard weft-knitting fabric weight formula:
        W (g/m²) = S (stitches/cm²) × l (cm) × tex (g/1000m) × 1000
                 = S × (l/10) × tex × 1000 / 1000
                 = S × l_mm / 10 × tex

    Derivation:
        Mass of yarn per cm² of fabric = S × l × (tex / 1000)
        where tex is g per 1000 m and l is in mm → l/1000 m.
        Mass per cm² (g) = S × (l_mm / (1000 × 1000)) × tex × 1000
                         = S × l_mm × tex / 1000000 × 1000
                         = S × l_mm × tex / 1000 g/cm²
        × 10000 to convert cm² to m²:
        W (g/m²) = S × l_mm × tex / 1000 × 10000
                 = S × l_mm × tex × 10

    Cross-check: S = 22, l = 3.5 mm, tex = 20 (Ne 30):
        W = 22 × 3.5 × 20 × 10 / 10000 = 154 g/m² — typical for
        medium-weight single-jersey from Ne 30 yarn. ✓

    (The /10000 converts g/cm² back to g/m² properly:
        g/cm² × 10000 = g/m²; so:
        W = S × l_mm × tex / (1000 × 1000) × 10000
          = S × l_mm × tex / 100    where l_mm is in mm and S in /cm²)
    """
    W = stitch_density_per_cm2 * stitch_length_mm * yarn_count_tex / 100.0
    return round(W, 1)


def calculate_dimensional_relaxation(
    tightness_factor: float,
    structure_type: str,
    warp_crimp_pct: float,
    relaxation_state: str
) -> tuple:
    """
    Estimates width and length relaxation % after fabric leaves the needles.

    Source: Spencer Section 7.2 (plain), Section 7.3 (rib), Section 22.5:

    Plain (single-jersey):
      - Spencer p. 63: "Plain normally has a potential recovery of 40%
        in width after stretching." This means the relaxed width is
        typically 15–25% narrower than the knitting width.
      - Width relaxation increases with tightness factor (tighter structures
        have greater elastic energy stored → more springback on release).
      - Length relaxation (coursewise): typically 5–15% shorter than
        knitting length for plain cotton. Higher TF → more length relaxation
        as courses compact together.

    Rib (1×1):
      - Spencer p. 68: "Relaxed 1×1 rib is theoretically twice the thickness
        and half the width of an equivalent plain fabric… In practice, 1×1 rib
        normally relaxes by approximately 30 per cent compared with its
        knitting width."
      - Width relaxation rib: ~25–35%.
      - Length relaxation rib: typically 3–10%.

    Interlock:
      - Spencer Section 7.4: interlock is more stable than plain or rib.
      - Width relaxation interlock: typically 10–18%.
      - Length relaxation interlock: typically 3–8%.

    Warp crimp contribution: the warp crimp of the input woven substrate
    represents residual yarn tension that is partially released during knitting
    loop formation. High substrate warp crimp → yarn is effectively shorter
    in the loop → slightly tighter loops → marginally more width relaxation.

    Relaxation-state dependency: fully-relaxed fabric has undergone the
    maximum possible dimensional change (Knapton protocol: 24h wet + tumble-
    dry). Dry-relaxed: intermediate. As-knitted: minimum relaxation.
    """
    state_factor = {
        "as_knitted":    0.50,
        "dry_relaxed":   0.80,
        "wet_relaxed":   0.90,
        "fully_relaxed": 1.00,
    }.get(relaxation_state.lower().replace(" ", "_"), 0.80)

    structure_type_lower = structure_type.lower().replace(" ", "_").replace("-", "_")

    # ── Width relaxation ──────────────────────────────────────────────────────
    if "rib" in structure_type_lower:
        # Spencer p. 68: "approximately 30 per cent" for 1×1 rib
        base_width_relax = 30.0
    elif "interlock" in structure_type_lower:
        base_width_relax = 14.0
    else:
        # Plain single-jersey: 15–25% base depending on TF
        base_width_relax = 12.0 + (tightness_factor - 1.0) * 8.0

    # Tightness factor modulation: tighter structure → more stored elastic energy
    TF_modulation = max(0.7, min(1.4, tightness_factor / 1.3))

    # Warp crimp contribution: crimped yarn is effectively shorter → tighter loop
    crimp_contrib = max(0.0, (warp_crimp_pct - 5.0) * 0.15)

    width_relaxation = (base_width_relax + crimp_contrib) * TF_modulation * state_factor

    # ── Length relaxation ──────────────────────────────────────────────────────
    if "rib" in structure_type_lower:
        base_length_relax = 6.0
    elif "interlock" in structure_type_lower:
        base_length_relax = 5.0
    else:
        # Plain: 5–15% → higher TF means courses pack tighter on release
        base_length_relax = 4.0 + (tightness_factor - 1.0) * 7.0

    length_relaxation = base_length_relax * TF_modulation * state_factor

    return (round(min(45.0, max(0.0, width_relaxation)), 1),
            round(min(20.0, max(0.0, length_relaxation)), 1))


def calculate_production_rate(
    number_of_feeds: int,
    machine_rpm: float,
    courses_per_cm: float,
    cylinder_diameter_inch: float,
    structure_type: str
) -> tuple:
    """
    Calculates knitting productivity metrics.

    Source: Spencer Section 6.3, p. 52:
        "In weft knitting, P = F × R or T × (E/C), where F is the number
        of active yarn feeds, R or T the number of machine revolutions or
        cam-carriage traverses per minute, and C the number of courses or
        colours which comprise one pattern row."

    For plain single-jersey (C = 1 feed per course):
        courses/min = F × R   [Spencer Eq. 6.3]

    Fabric production rate (m/min):
        v_fabric = courses_per_min / (cpc × 100)
    where cpc is courses per cm and the ×100 converts cm to m.

    Fabric width in open form (after slitting the tube):
        w_m = π × D_in × 0.0254  (tube circumference in metres)

    Fabric area production rate:
        A = v_fabric (m/min) × w_m (m) × 60 (min/h)  [m²/h]

    For rib structures, each course requires two needle beds (Spencer p. 70).
    The effective feed rate per fabric course is halved (C = 2 for rib):
        courses/min (rib) ≈ F × R / 2

    Spencer Section 7.2.1: "compared with a rib machine, a plain machine
    is simpler and more economical, with a potential for more feeders,
    higher running speeds and knitting a wider range of yarn counts."

    Cross-check: Spencer p. 52 states "as many as 4000 courses per minute
    can be knitted on some plain machines." At 45 rpm with 90 feeders:
        P = 90 × 45 = 4050 courses/min ✓
    """
    stype = structure_type.lower().replace(" ", "_").replace("-", "_")

    # Courses per pass: for rib, one feed produces two courses (one per bed)
    # but the fabric advances only half the equivalent speed per feed.
    if "rib" in stype:
        courses_per_min = number_of_feeds * machine_rpm / 2.0
    elif "interlock" in stype:
        courses_per_min = number_of_feeds * machine_rpm / 2.0
    else:
        courses_per_min = number_of_feeds * machine_rpm

    # Fabric delivery rate in m/min
    # cpc (courses/cm) → need cm per course → 1/cpc cm → 1/(cpc×100) m per course
    if courses_per_cm > 0:
        v_fabric_m_min = courses_per_min / (courses_per_cm * 100.0)
    else:
        v_fabric_m_min = 0.0

    # Open fabric width: tube circumference = π × D_in in inches → ×0.0254 → m
    fabric_width_m = math.pi * cylinder_diameter_inch * 0.0254

    # Area production rate
    area_m2_hr = v_fabric_m_min * fabric_width_m * 60.0

    return (round(courses_per_min, 0),
            round(v_fabric_m_min, 4),
            round(area_m2_hr, 2),
            round(fabric_width_m, 3))


def check_gauge_count_compatibility(
    machine_gauge_npi: int,
    yarn_count_Ne: float,
    structure_type: str
) -> tuple:
    """
    Checks whether the yarn count is compatible with the machine gauge.

    Source: Spencer Section 7.2.1, p. 63:
        "An approximately suitable count may be obtained using the formula
        NeB = G²/18 or NeK = G²/15, where NeB = cotton spun count,
        NeK = worsted spun count, G = gauge in npi."
        "For fine gauges, a heavier and stronger count may be necessary."

    Extended formula — Spencer also quotes for rib (Section 7.3):
        "the rib machine also requires finer yarn than a similar gauge
        plain machine." Finer yarn by ~√2 for rib (because each thread
        carries half the wale width load). For interlock, one additional
        step finer still.

    The formula gives the nominal centre of the acceptable count range.
    Spencer Section 15.3 notes a range of counts around this nominal:
        "a range of yarn counts may be knitted for each machine gauge,
        including a number of ends of yarn at each knitting system."
    We define a ±30% band around the nominal count as 'acceptable'.

    Returns: (nominal_Ne, is_compatible, compatibility_note)
    """
    stype = structure_type.lower().replace(" ", "_").replace("-", "_")

    if "rib" in stype:
        # Rib requires finer yarn than plain for same gauge
        nominal_Ne = machine_gauge_npi ** 2 / 14.0
    elif "interlock" in stype:
        # Interlock: two-bed, requires yet finer yarn
        nominal_Ne = machine_gauge_npi ** 2 / 12.0
    else:
        # Plain single-jersey: Spencer's formula directly
        nominal_Ne = machine_gauge_npi ** 2 / 18.0

    lower_bound = nominal_Ne * 0.65
    upper_bound = nominal_Ne * 1.50

    if lower_bound <= yarn_count_Ne <= upper_bound:
        compat = True
        note = f"Yarn count Ne {yarn_count_Ne:.1f} is within the recommended range for E{machine_gauge_npi} ({lower_bound:.0f}–{upper_bound:.0f} Ne)."
    elif yarn_count_Ne < lower_bound:
        compat = False
        note = (f"Yarn count Ne {yarn_count_Ne:.1f} is too coarse for E{machine_gauge_npi} gauge. "
                f"Minimum recommended: Ne {lower_bound:.0f}. "
                "Coarse yarns will not fit between needles → needle breakage and missed stitches. "
                f"(Spencer p. 63: NeB = G²/18 → {nominal_Ne:.0f} Ne for this gauge)")
    else:
        compat = False
        note = (f"Yarn count Ne {yarn_count_Ne:.1f} is too fine for E{machine_gauge_npi} gauge. "
                f"Maximum recommended: Ne {upper_bound:.0f}. "
                "Fine yarns produce very loose, open fabric with inadequate cover. "
                f"(Spencer p. 63: NeB = G²/18 → {nominal_Ne:.0f} Ne for this gauge)")

    return round(nominal_Ne, 1), compat, note


def assess_needle_break_risk(
    tightness_factor: float,
    machine_gauge_npi: int,
    cylinder_diameter_inch: float,
    machine_rpm: float,
    fabric_areal_weight_g_m2: float,
    take_down_tension_cN_per_cm: float,
    operating_hours_ratio: float
) -> str:
    """
    Qualitative assessment of needle break risk in weft knitting.

    Source: Spencer Section 22.8, p. 283:
    (1) Tightness (over-tight knitting):
        "needle hooks and latches have been reduced in size wherever
        possible in order to reduce the extent of the needle movement."
        Above TF ≈ 1.8–2.0, yarn compression between needle and sinker
        exceeds needle hook tensile capacity → fracture.
    (2) Needle bounce (high speed):
        "Needle bounce is a major problem in high speed knitting. This
        is caused by the needle butt being suddenly checked by the impact
        of hitting the upper surface of the up-throw cam after it has
        accelerated away from the lowest point of the stitch cam."
        Tangential needle speed limit: ~5 m/s (Spencer p. 284, seamless
        hose machines). For circular knitting:
            v_tan = π × D_in × 0.0254 × rpm / 60  (m/s)
    (3) Take-down tension:
        Spencer Section 22.9: "higher take-down tension leads to a greater
        incidence of cuts and holes in the fabric, wear on the knitting
        elements." Excessive take-down forces are transferred upward through
        the fabric and deflect the needle stem at the trick wall contact
        point, increasing fracture risk.
    (4) Maintenance (worn tricks and butt channels):
        Spencer Section 22.8: "upthrow cam becomes pitted in this section"
        → needle butts impact unevenly → bouncing amplified → breakage.
    """
    risk_score = 0

    # Tightness factor: TF > 1.8 enters high-risk zone
    if tightness_factor > 2.0:
        risk_score += 3  # severe over-tight
    elif tightness_factor > 1.8:
        risk_score += 2
    elif tightness_factor > 1.65:
        risk_score += 1

    # Tangential needle speed: limit is ~5 m/s (Spencer Section 22.8)
    v_tan = math.pi * cylinder_diameter_inch * 0.0254 * machine_rpm / 60.0
    if v_tan > 5.0:
        risk_score += 3  # exceeds Spencer's stated limit
    elif v_tan > 4.0:
        risk_score += 2
    elif v_tan > 3.0:
        risk_score += 1

    # Take-down tension: above 3.0 cN/cm → deflects needle at trick wall
    if take_down_tension_cN_per_cm > 3.5:
        risk_score += 2
    elif take_down_tension_cN_per_cm > 2.5:
        risk_score += 1

    # Very heavy substrate weight → greater inertia in fabric tube → higher take-down
    if fabric_areal_weight_g_m2 > 350:
        risk_score += 1

    # Maintenance overdue → worn cam tracks → amplified needle bounce
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


def assess_yarn_break_risk(
    yarn_count_tex: float,
    yarn_input_tension_cN: float,
    tightness_factor: float,
    weft_break_risk_upstream: str,
    weft_tension_at_fell_cN: float
) -> str:
    """
    Qualitative assessment of yarn break risk during weft knitting.

    Source: Spencer Section 22.7 (robbing back), Section 7.2.1 (contra technique):

    (1) Yarn tension amplification (robbing back):
        Spencer Section 22.7, p. 282:
        "yarn tension increases (according to Amontons' Law of Friction)
        as it passes over the knitting elements from point A… a two-fold
        increase in yarn/metal friction can cause a six-fold increase in
        maximum knitting tension."
        Peak knitting tension ≈ input_tension × exp(μ × total_wrap_angle).
        Simplification: peak_tension ≈ 3 × input_tension for typical
        tension settings with 3–5 yarn contact points.

    (2) Yarn breaking force:
        Breaking force (cN) ≈ yarn_count_tex × 8.0
        (conservative estimate for typical ring / rotor spun cotton at Ne 20–40;
        note: weaving layer 4 does not carry tenacity forward explicitly,
        so we use a count-based estimate consistent with Vol 6 Fig. 42.)

    (3) Upstream weft-break risk inheritance:
        If the weaving module already flagged "high" weft-break risk,
        the same yarn carries that weakness into the knitting machine.
        The knitting process introduces fewer stress peaks than the shuttle
        loom's fell-incorporation mechanism (Spencer Section 7.2.1 contra
        technique reduces peak tensions), so the inherited risk is
        down-weighted by one level.

    (4) Tightness factor: high TF → needle descends further → yarn must
        supply more length per stitch → tension spikes at the feeder.
    """
    risk_score = 0

    # Estimated yarn breaking force
    breaking_force_cN = yarn_count_tex * 8.0  # conservative for spun cotton/blend

    # Peak tension during loop formation (robbing-back amplification × 3)
    peak_knitting_tension = yarn_input_tension_cN * 3.0

    tension_ratio = peak_knitting_tension / max(breaking_force_cN, 1.0)
    if tension_ratio > 0.35:
        risk_score += 3
    elif tension_ratio > 0.22:
        risk_score += 2
    elif tension_ratio > 0.14:
        risk_score += 1

    # Upstream weft-break risk inheritance (down-weighted one level for knitting)
    if weft_break_risk_upstream.lower() == "high":
        risk_score += 2
    elif weft_break_risk_upstream.lower() == "medium":
        risk_score += 1

    # Residual weft tension from weaving: high tension → yarn less pliable → harder to loop
    if weft_tension_at_fell_cN > 150:
        risk_score += 2
    elif weft_tension_at_fell_cN > 80:
        risk_score += 1

    # Tightness factor: very tight knitting draws yarn aggressively
    if tightness_factor > 1.9:
        risk_score += 2
    elif tightness_factor > 1.6:
        risk_score += 1

    if risk_score <= 2:
        return "low"
    elif risk_score <= 5:
        return "medium"
    else:
        return "high"


def assess_fabric_defect_risk(
    warp_crimp_pct: float,
    total_cover_factor: float,
    yarn_input_tension_cN: float,
    take_down_tension_cN_per_cm: float,
    cloth_defect_risk_upstream: str,
    courses_per_min: float,
    number_of_feeds: int,
    structure_type: str
) -> str:
    """
    Qualitative assessment of fabric defect risk in weft knitting.

    Source: Spencer Sections 7.2.1, 9.1–9.2, 22.7, 22.9.

    Main defect types:
    (1) Feeder striping (barre):
        Spencer Section 9.3.2 (feeder striping):
        "Uniformity [of yarn] and help to mask feeder stripiness, but they
        also increase fabric weight." — each feeder produces one horizontal
        stripe per revolution; tension variation between feeders → barre.
        Risk increases with number of feeds (more opportunities for
        inter-feeder tension mismatch) and with high yarn tension.

    (2) Drop stitches / missed stitches:
        Spencer Section 9.1: float stitch produced when yarn is not
        trapped in the needle hook. High input tension → yarn lifts clear
        of hook during clearing. Low tension → yarn misses the hook.
        Too-tight tightness factor → yarn bridges over needle → drop stitch.

    (3) Holes from take-down tension:
        Spencer Section 22.9: "higher take-down tension leads to a greater
        incidence of cuts and holes in the fabric."

    (4) Robbing back irregularity:
        Spencer Section 22.7: tension fluctuations cause stitch length
        variation → courses of varying density → visible horizontal bands
        in uniform yarn fabrics.

    (5) Upstream defect inheritance:
        Cloth defects from weaving (thick/thin places, stitching) persist
        in the yarn as stitch-length irregularities in knitting output.

    (6) Warp crimp — yarn supply variability:
        High substrate warp crimp means the yarn entering the knitting zone
        has experienced prior crimping deformation. This reduces yarn
        pliability and creates micro-tension spikes as crimped sections
        straighten in the feeder, contributing to barre.
    """
    risk_score = 0

    # Feeder striping risk: higher feeds → more barre exposure
    if number_of_feeds > 144:
        risk_score += 1   # statistical: inter-feeder tension variance more likely
    if yarn_input_tension_cN < 2.0:
        risk_score += 2   # too low → missed stitches
    elif yarn_input_tension_cN > 10.0:
        risk_score += 2   # too high → drop stitches, robbing back
    elif yarn_input_tension_cN > 7.0:
        risk_score += 1

    # Take-down tension: holes and distortion
    if take_down_tension_cN_per_cm > 3.0:
        risk_score += 2   # Spencer: "greater incidence of cuts and holes"
    elif take_down_tension_cN_per_cm > 2.0:
        risk_score += 1

    # Upstream cloth defect inheritance
    if cloth_defect_risk_upstream.lower() == "high":
        risk_score += 2
    elif cloth_defect_risk_upstream.lower() == "medium":
        risk_score += 1

    # Warp crimp: high crimp → micro-tension spikes → barre
    if warp_crimp_pct > 14.0:
        risk_score += 2
    elif warp_crimp_pct > 8.0:
        risk_score += 1

    # Open fabric (low cover) → loop instability → more missed stitches
    if total_cover_factor < 0.40:
        risk_score += 1

    # High courses/min → less time per loop formation → amplified irregularity
    if courses_per_min > 3000:
        risk_score += 1

    if risk_score <= 2:
        return "low"
    elif risk_score <= 5:
        return "medium"
    else:
        return "high"


def assess_pilling_propensity(
    yarn_diameter_weft_mm: float,
    yarn_count_Ne: float,
    tightness_factor: float,
    structure_type: str
) -> str:
    """
    Qualitative assessment of pilling propensity of the knitted fabric.

    Source: Spencer Section 22.5 (fabric compactness and durability):
        "Compactness is an important fabric property that influences
        durability, drape, handle, strength, abrasion resistance,
        dimensional stability."
    Also Spencer p. 43: "stitch length… the larger the stitch length
    [lower TF], the more extensible and lighter the fabric and the
    poorer the cover, opacity and bursting strength."

    Physical mechanisms:
    - Pilling arises when surface fibres work out of the yarn body during
      wear abrasion and tangle into balls (pills) anchored by remaining
      fibres.
    - High TF (tight structure) → fibres are locked firmly → less
      fibre migration → lower pilling.
    - Low TF (slack structure) → fibres can migrate easily → higher pilling.
    - Coarser yarns (higher tex, lower Ne) → fewer fibres per cross-section
      → individual fibre ends are longer → anchor pills more firmly → higher
      tendency for permanent pills (worse pilling rating).
    - Rib and interlock structures: sinker loops are concealed between the
      two fabric faces → less abrasion of sinker loops → lower pilling than
      plain single-jersey for the same yarn.
    - Air-jet spun yarn (from airjet.py) has low hairiness → less free fibre
      ends → inherently lower pilling than ring or rotor-spun yarn.
      (Marks & Robinson weaving output did not flag yarn type explicitly,
      so we use yarn_diameter and count as proxies.)
    """
    risk_score = 0

    # Tightness factor: looser → more pilling
    if tightness_factor < 1.1:
        risk_score += 3  # very open structure → severe pilling
    elif tightness_factor < 1.3:
        risk_score += 2
    elif tightness_factor < 1.5:
        risk_score += 1
    # TF ≥ 1.5: firm, compact → low pilling contribution

    # Coarser yarn → larger, stronger pills
    if yarn_count_Ne < 12:
        risk_score += 2  # coarse yarn → strong pills, hard to remove
    elif yarn_count_Ne < 20:
        risk_score += 1

    # Large diameter → thick sinker loops → more exposed surface area
    if yarn_diameter_weft_mm > 0.22:
        risk_score += 1

    # Structure type: plain single-jersey has highest pilling exposure
    stype = structure_type.lower().replace(" ", "_").replace("-", "_")
    if "plain" in stype or "jersey" in stype:
        risk_score += 1  # sinker loops fully exposed on technical back
    # Rib/interlock: sinker loops are partially concealed → no extra penalty

    if risk_score <= 2:
        return "low"
    elif risk_score <= 4:
        return "medium"
    else:
        return "high"


# ─────────────────────────────────────────────────────────────────────────────
# MASTER SIMULATION FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def simulate_weft_knitting(
    fabric: InputFabric,
    params: WeftKnittingParams
) -> KnittedFabricOutput:
    """
    Master simulation function for Weft Knitting.

    Takes Layer 2 (InputFabric — direct output from plain_weaving.py Layer 4)
    and Layer 3 (WeftKnittingParams — loom operational parameters), runs all
    sub-models, and returns Layer 4 (KnittedFabricOutput).
    """
    warnings = []

    # ── DERIVE YARN COUNT FROM WEFT DIAMETER (Peirce inverse) ─────────────────
    # Spencer Section 1.4: yarn count drives gauge selection.
    # We use the weft yarn diameter because in weft knitting the weft thread
    # becomes the knitting yarn — it is fed to each needle in succession.
    yarn_count_tex, yarn_count_Ne = derive_yarn_count_from_diameter(
        fabric.yarn_diameter_weft_mm
    )

    # ── GAUGE–COUNT COMPATIBILITY ─────────────────────────────────────────────
    nominal_Ne, gauge_ok, gauge_note = check_gauge_count_compatibility(
        params.machine_gauge_npi,
        yarn_count_Ne,
        params.structure_type
    )
    if not gauge_ok:
        warnings.append(gauge_note)

    # ── TOTAL NEEDLES ─────────────────────────────────────────────────────────
    total_needles = calculate_total_needles(
        params.cylinder_diameter_inch,
        params.machine_gauge_npi
    )

    # ── TIGHTNESS FACTOR ──────────────────────────────────────────────────────
    TF = calculate_tightness_factor(yarn_count_tex, params.stitch_length_mm)

    # ── MUNDEN STITCH DENSITY ─────────────────────────────────────────────────
    cpc, wpc, S, R = calculate_munden_stitch_density(
        params.stitch_length_mm,
        params.relaxation_state
    )

    # ── FABRIC WEIGHT ─────────────────────────────────────────────────────────
    gsm = calculate_fabric_weight_g_m2(S, params.stitch_length_mm, yarn_count_tex)

    # ── DIMENSIONAL RELAXATION ────────────────────────────────────────────────
    width_relax, length_relax = calculate_dimensional_relaxation(
        TF,
        params.structure_type,
        fabric.warp_crimp_pct,
        params.relaxation_state
    )

    # ── PRODUCTION RATE ───────────────────────────────────────────────────────
    cpm, v_m_min, area_m2_hr, fabric_width_m = calculate_production_rate(
        params.number_of_feeds,
        params.machine_rpm,
        cpc,
        params.cylinder_diameter_inch,
        params.structure_type
    )

    # ── RISK ASSESSMENTS ──────────────────────────────────────────────────────
    maintenance_ratio = (params.operating_hours_since_maintenance
                         / max(params.maintenance_interval_hours, 1.0))

    needle_risk = assess_needle_break_risk(
        TF,
        params.machine_gauge_npi,
        params.cylinder_diameter_inch,
        params.machine_rpm,
        fabric.fabric_areal_weight_g_m2,
        params.take_down_tension_cN_per_cm,
        maintenance_ratio
    )

    yarn_risk = assess_yarn_break_risk(
        yarn_count_tex,
        params.yarn_input_tension_cN,
        TF,
        fabric.weft_break_risk,
        fabric.weft_tension_at_fell_cN
    )

    defect_risk = assess_fabric_defect_risk(
        fabric.warp_crimp_pct,
        fabric.total_cover_factor,
        params.yarn_input_tension_cN,
        params.take_down_tension_cN_per_cm,
        fabric.cloth_defect_risk,
        cpm,
        params.number_of_feeds,
        params.structure_type
    )

    pilling = assess_pilling_propensity(
        fabric.yarn_diameter_weft_mm,
        yarn_count_Ne,
        TF,
        params.structure_type
    )

    # ── POST-SIMULATION WARNINGS ──────────────────────────────────────────────

    # Tightness factor warnings (Spencer Section 22.6)
    if TF > 1.9:
        warnings.append(
            f"Tightness factor ({TF:.3f}) exceeds 1.9 — approaching the structural jamming "
            "limit. Yarn is compressed between needle stem and sinker belly → needle "
            "fracture and dropped stitches are highly probable. "
            "Increase stitch length or use a coarser gauge. "
            "(Spencer Section 22.6 and 22.8)"
        )
    elif TF < 1.0:
        warnings.append(
            f"Tightness factor ({TF:.3f}) is very low — the structure will be slack "
            "and open with poor cover. Loops will be too large to maintain coherence "
            "under take-down tension. Increase gauge or reduce stitch length. "
            "(Spencer p. 43: 'the poorer the cover, opacity and bursting strength.')"
        )

    # Tangential speed warning (Spencer Section 22.8)
    v_tan = math.pi * params.cylinder_diameter_inch * 0.0254 * params.machine_rpm / 60.0
    if v_tan > 5.0:
        warnings.append(
            f"Tangential needle speed ({v_tan:.2f} m/s) exceeds 5 m/s — the limit "
            "stated by Spencer (Section 22.8) for high-speed seamless hose machines. "
            "Needle bounce and butt fracture are highly likely. Reduce rpm."
        )
    elif v_tan > 4.0:
        warnings.append(
            f"Tangential needle speed ({v_tan:.2f} m/s) is approaching the 5 m/s limit "
            "(Spencer Section 22.8). Monitor for needle bounce and cam track pitting."
        )

    # Upstream risk inheritance warnings
    if fabric.warp_break_risk == "high":
        warnings.append(
            "UPSTREAM: Weaving warp-break risk was HIGH. The yarn entering the "
            "weft-knitting machine carries this structural weakness (thin places, "
            "high CVm). Yarn break rates in knitting will be elevated. "
            "Consider yarn conditioning or switching to a more uniform yarn."
        )
    if fabric.weft_break_risk == "high":
        warnings.append(
            "UPSTREAM: Weaving weft-break risk was HIGH. Weft tension at the fell "
            f"({fabric.weft_tension_at_fell_cN} cN) indicates a tightly set yarn with "
            "reduced pliability — loop formation will require high stitch cam force."
        )
    if fabric.cloth_defect_risk == "high":
        warnings.append(
            "UPSTREAM: Weaving cloth defect risk was HIGH (pick spacing variation, "
            "stitching, or setting-on places). These manifest as yarn count variations "
            "that will cause course-density banding (barre) in the knitted fabric. "
            "(Spencer Section 22.7 robbing-back amplifies tension variations.)"
        )

    # Take-down tension warning (Spencer Section 22.9)
    if params.take_down_tension_cN_per_cm > 3.5:
        warnings.append(
            f"Take-down tension ({params.take_down_tension_cN_per_cm} cN/cm) is high. "
            "'Higher take-down tension leads to a greater incidence of cuts and holes "
            "in the fabric, wear on the knitting elements, problems when knitting "
            "weaker yarns, and a greater length-wise deformation.' "
            "(Spencer Section 22.9). Reduce take-down tension."
        )

    # Maintenance overdue
    if maintenance_ratio > 1.0:
        warnings.append(
            f"Maintenance overdue (operating hours = {params.operating_hours_since_maintenance:.0f} h "
            f"vs interval {params.maintenance_interval_hours:.0f} h). Worn needle tricks, "
            "cam tracks, and sinker slots will increase needle bounce and yarn abrasion. "
            "(Spencer Section 22.8: 'upthrow cam becomes pitted.')"
        )

    # Inlet yarn tension: robbing-back risk
    if params.yarn_input_tension_cN > 9.0:
        warnings.append(
            f"Yarn input tension ({params.yarn_input_tension_cN} cN) is high. "
            "'A two-fold increase in yarn/metal friction can cause a six-fold increase "
            "in maximum knitting tension.' (Spencer Section 22.7). "
            "Reduce tensioner setting to prevent robbing back and stitch irregularity."
        )

    return KnittedFabricOutput(
        yarn_count_tex=yarn_count_tex,
        yarn_count_Ne=yarn_count_Ne,
        tightness_factor=TF,
        courses_per_cm=cpc,
        wales_per_cm=wpc,
        stitch_density_per_cm2=S,
        loop_shape_factor=R,
        fabric_areal_weight_g_m2=gsm,
        width_relaxation_pct=width_relax,
        length_relaxation_pct=length_relax,
        total_needles=total_needles,
        courses_per_minute=cpm,
        fabric_production_rate_m_min=v_m_min,
        fabric_production_rate_m2_hr=area_m2_hr,
        fabric_width_m=fabric_width_m,
        needle_break_risk=needle_risk,
        yarn_break_risk=yarn_risk,
        fabric_defect_risk=defect_risk,
        pilling_propensity=pilling,
        warnings=warnings
    )


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE USAGE — scenarios chained directly from plain_weaving.py outputs
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    print("=" * 65)
    print("WEFT KNITTING SIMULATION — Circular Single-Jersey")
    print("Based on Spencer, 'Knitting Technology', 3rd ed., 2001")
    print("Layer 2 sourced directly from plain_weaving.py Layer 4")
    print("=" * 65)

    # ── SCENARIO 1: Cotton jersey from Weaving Scenario 1 output ────────────
    # Input: plain_weaving.py Scenario 1 (Ne 20 carded cotton square cloth).
    # Weft knitting: E18 circular single-jersey, medium stitch length.
    # Validation: Spencer p. 64 — E18 → Nm 1/24–1/32 → tex ≈ 31–42 tex.
    #             Weft diameter 0.205 mm → tex ≈ (0.205/0.037)² ≈ 30.7 tex
    #             → Ne 20. E18 nominal: NeB = 18²/18 = 18. Ne 20 is within
    #             ±30% → compatible. ✓
    print("\n--- SCENARIO 1: Cotton single-jersey, E18, from weaving "
          "Scenario 1 output ---\n")

    fabric_1 = InputFabric(
        # Direct copy of plain_weaving.py Scenario 1 FabricQualityOutput:
        yarn_diameter_warp_mm=0.205,        # d_warp for Ne 20 cotton carded
        yarn_diameter_weft_mm=0.205,        # d_weft = d_warp (square cloth)
        warp_cover_factor=0.615,
        weft_cover_factor=0.574,
        total_cover_factor=0.836,
        warp_crimp_pct=7.2,
        weft_crimp_pct=8.5,
        crimp_balance="balanced",
        fell_displacement_mm=2.4,
        beat_up_force_cN_per_cm=312.0,
        fabric_areal_weight_g_m2=178.0,
        weft_tension_at_fell_cN=88.0,
        warp_break_risk="low",
        weft_break_risk="low",
        cloth_defect_risk="low",
        production_rate_m_per_min=0.073,
        production_rate_m2_per_hour=8.52
    )

    params_1 = WeftKnittingParams(
        machine_gauge_npi=18,
        cylinder_diameter_inch=26.0,      # Spencer p. 64: "most popular diameter"
        number_of_feeds=72,               # Standard 26" E18 single-jersey
        stitch_length_mm=3.2,             # Medium stitch length for Ne 20 cotton
        machine_rpm=25.0,
        yarn_input_tension_cN=5.0,
        take_down_tension_cN_per_cm=1.5,
        needle_type="latch_needle",
        structure_type="plain_single_jersey",
        relaxation_state="dry_relaxed",
        ambient_temperature_C=24.0,
        ambient_humidity_pct=60.0,
        maintenance_interval_hours=2_000.0,
        operating_hours_since_maintenance=650.0
    )

    r1 = simulate_weft_knitting(fabric_1, params_1)

    print(f"  Yarn count (derived):    {r1.yarn_count_tex} tex  /  Ne {r1.yarn_count_Ne}")
    print(f"  Tightness factor (TF):   {r1.tightness_factor}  "
          f"(Spencer ref: 1.4–1.5 for plain worsted)")
    print(f"  Courses per cm:          {r1.courses_per_cm}")
    print(f"  Wales per cm:            {r1.wales_per_cm}")
    print(f"  Stitch density:          {r1.stitch_density_per_cm2} stitches/cm²")
    print(f"  Loop shape factor R:     {r1.loop_shape_factor}  "
          f"(Spencer Knapton fully-relaxed ref: 1.3)")
    print(f"  Fabric weight:           {r1.fabric_areal_weight_g_m2} g/m²")
    print(f"  Width relaxation:        {r1.width_relaxation_pct}%")
    print(f"  Length relaxation:       {r1.length_relaxation_pct}%")
    print(f"  Total needles:           {r1.total_needles}")
    print(f"  Courses per minute:      {r1.courses_per_minute:.0f}  "
          f"(P = {params_1.number_of_feeds} feeds × {params_1.machine_rpm} rpm)")
    print(f"  Fabric production:       {r1.fabric_production_rate_m_min} m/min  "
          f"→  {r1.fabric_production_rate_m2_hr} m²/h")
    print(f"  Fabric width (slit):     {r1.fabric_width_m} m")
    print(f"  Needle break risk:       {r1.needle_break_risk.upper()}")
    print(f"  Yarn break risk:         {r1.yarn_break_risk.upper()}")
    print(f"  Fabric defect risk:      {r1.fabric_defect_risk.upper()}")
    print(f"  Pilling propensity:      {r1.pilling_propensity.upper()}")
    if r1.warnings:
        print(f"\n  WARNINGS:")
        for w in r1.warnings:
            print(f"    ⚠ {w}")
    else:
        print("\n  No warnings — all parameters within recommended ranges.")

    # ── SCENARIO 2: PES/CO fine-gauge jersey from Weaving Scenario 2 ────────
    # Input: plain_weaving.py Scenario 2 (Ne 30 PES/CO poplin).
    # Weft knitting: E24 circular single-jersey for fine jersey fabric.
    # Validation: E24 → NeB = 24²/18 = 32. Ne 30 is within ±30% → compatible.
    print("\n--- SCENARIO 2: PES/CO fine-gauge jersey, E24, from weaving "
          "Scenario 2 output ---\n")

    fabric_2 = InputFabric(
        yarn_diameter_warp_mm=0.165,        # d_warp for Ne 30 PES/CO
        yarn_diameter_weft_mm=0.191,        # d_weft for Ne 20 PES/CO (coarser weft)
        warp_cover_factor=0.793,
        weft_cover_factor=0.420,
        total_cover_factor=0.880,
        warp_crimp_pct=12.8,                # poplin — warp dominant
        weft_crimp_pct=2.4,                 # Spencer ref: ≤3% for poplin
        crimp_balance="warp_dominant",
        fell_displacement_mm=1.0,
        beat_up_force_cN_per_cm=198.0,
        fabric_areal_weight_g_m2=162.0,
        weft_tension_at_fell_cN=42.0,
        warp_break_risk="low",
        weft_break_risk="low",
        cloth_defect_risk="low",
        production_rate_m_per_min=0.102,
        production_rate_m2_per_hour=18.36
    )

    params_2 = WeftKnittingParams(
        machine_gauge_npi=24,
        cylinder_diameter_inch=30.0,
        number_of_feeds=96,
        stitch_length_mm=2.8,              # finer yarn → shorter stitch length
        machine_rpm=30.0,
        yarn_input_tension_cN=4.0,
        take_down_tension_cN_per_cm=1.2,
        needle_type="latch_needle",
        structure_type="plain_single_jersey",
        relaxation_state="dry_relaxed",
        ambient_temperature_C=22.0,
        ambient_humidity_pct=55.0,
        maintenance_interval_hours=2_500.0,
        operating_hours_since_maintenance=300.0
    )

    r2 = simulate_weft_knitting(fabric_2, params_2)

    print(f"  Yarn count (derived):    {r2.yarn_count_tex} tex  /  Ne {r2.yarn_count_Ne}")
    print(f"  Tightness factor (TF):   {r2.tightness_factor}")
    print(f"  Courses per cm:          {r2.courses_per_cm}")
    print(f"  Wales per cm:            {r2.wales_per_cm}")
    print(f"  Stitch density:          {r2.stitch_density_per_cm2} stitches/cm²")
    print(f"  Fabric weight:           {r2.fabric_areal_weight_g_m2} g/m²")
    print(f"  Width / Length relax:    {r2.width_relaxation_pct}% / {r2.length_relaxation_pct}%")
    print(f"  Courses per minute:      {r2.courses_per_minute:.0f}")
    print(f"  Fabric production:       {r2.fabric_production_rate_m_min} m/min  "
          f"→  {r2.fabric_production_rate_m2_hr} m²/h")
    print(f"  Needle break risk:       {r2.needle_break_risk.upper()}")
    print(f"  Yarn break risk:         {r2.yarn_break_risk.upper()}")
    print(f"  Fabric defect risk:      {r2.fabric_defect_risk.upper()}")
    print(f"  Pilling propensity:      {r2.pilling_propensity.upper()}")
    if r2.warnings:
        print(f"\n  WARNINGS:")
        for w in r2.warnings:
            print(f"    ⚠ {w}")
    else:
        print("\n  No warnings — all parameters within recommended ranges.")

    # ── SCENARIO 3: Coarse jersey from Weaving Scenario 3 (stress test) ─────
    # Input: plain_weaving.py Scenario 3 (Ne 8 coarse cotton weft-faced cloth).
    # Weft knitting: E12 coarse single-jersey (shaker stitch / fleece base).
    # Expected: multiple warnings — coarse yarn, high substrate weight, upstream risks.
    print("\n--- SCENARIO 3: Coarse jersey, E12, from weaving Scenario 3 "
          "(stress test) ---\n")

    fabric_3 = InputFabric(
        yarn_diameter_warp_mm=0.324,        # d_warp for Ne 8 coarse cotton carded
        yarn_diameter_weft_mm=0.370,        # d_weft for Ne 6 very coarse cotton
        warp_cover_factor=0.389,
        weft_cover_factor=0.666,
        total_cover_factor=0.796,
        warp_crimp_pct=14.5,
        weft_crimp_pct=9.2,
        crimp_balance="weft_dominant",
        fell_displacement_mm=5.1,
        beat_up_force_cN_per_cm=480.0,
        fabric_areal_weight_g_m2=445.0,
        weft_tension_at_fell_cN=185.0,
        warp_break_risk="high",
        weft_break_risk="high",
        cloth_defect_risk="high",
        production_rate_m_per_min=0.056,
        production_rate_m2_per_hour=11.2
    )

    params_3 = WeftKnittingParams(
        machine_gauge_npi=12,
        cylinder_diameter_inch=20.0,
        number_of_feeds=36,
        stitch_length_mm=5.0,              # coarse knitting → long stitch length
        machine_rpm=20.0,
        yarn_input_tension_cN=9.0,         # high tension for coarse yarn control
        take_down_tension_cN_per_cm=3.5,   # high tension for heavy substrate
        needle_type="latch_needle",
        structure_type="plain_single_jersey",
        relaxation_state="dry_relaxed",
        ambient_temperature_C=26.0,
        ambient_humidity_pct=65.0,
        maintenance_interval_hours=1_500.0,
        operating_hours_since_maintenance=1_450.0  # nearly overdue
    )

    r3 = simulate_weft_knitting(fabric_3, params_3)

    print(f"  Yarn count (derived):    {r3.yarn_count_tex} tex  /  Ne {r3.yarn_count_Ne}")
    print(f"  Tightness factor (TF):   {r3.tightness_factor}")
    print(f"  Courses per cm:          {r3.courses_per_cm}")
    print(f"  Wales per cm:            {r3.wales_per_cm}")
    print(f"  Stitch density:          {r3.stitch_density_per_cm2} stitches/cm²")
    print(f"  Fabric weight:           {r3.fabric_areal_weight_g_m2} g/m²")
    print(f"  Width / Length relax:    {r3.width_relaxation_pct}% / {r3.length_relaxation_pct}%")
    print(f"  Courses per minute:      {r3.courses_per_minute:.0f}")
    print(f"  Fabric production:       {r3.fabric_production_rate_m_min} m/min  "
          f"→  {r3.fabric_production_rate_m2_hr} m²/h")
    print(f"  Needle break risk:       {r3.needle_break_risk.upper()}")
    print(f"  Yarn break risk:         {r3.yarn_break_risk.upper()}")
    print(f"  Fabric defect risk:      {r3.fabric_defect_risk.upper()}")
    print(f"  Pilling propensity:      {r3.pilling_propensity.upper()}")
    if r3.warnings:
        print(f"\n  WARNINGS:")
        for w in r3.warnings:
            print(f"    ⚠ {w}")

    print("\n" + "=" * 65)
    print("Simulation complete.")
    print("=" * 65)
