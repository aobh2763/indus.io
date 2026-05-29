"""
Reactive Dyeing Simulation Module
Process: Colouring > Reactive Dyeing (Exhaust / Pad-Batch / Continuous)

Layer 2 of this module (InputFabric) maps directly onto Layer 4 of the
plain_weaving.py module (FabricQualityOutput). Every field name and unit
is preserved so that the output of the weaving node plugs directly into
the input of the reactive dyeing node in the indus.io production network.

Reactive dyeing is the most important coloration method for cellulosic
fibres, accounting for ~20-30% of global dyestuff production (Mahapatra,
p. 194). The dye forms a covalent bond with the hydroxyl groups of
cellulose, delivering outstanding wash fastness (rating 4-5).

All parameter relationships derived from:
N. N. Mahapatra, "Textile Dyes", Chapter 13: Reactive Dyes,
Woodhead Publishing India / CRC Press, 2016.
ISBN 978-93-85059-60-5

Key references within Mahapatra Ch. 13:
  [13.2]  Components and formula of reactive dyes (S-F-T-X structure)
  [13.4]  Dyeing methods: M-brand, H-brand, VS, ME, HE dyes with
          respective temperatures and process conditions
  [13.5]  Functional group classification and fixation temperatures
  [13.8]  Dyeing cycle factors: pH, temperature, salt, alkali, time
  [13.12] Properties: wash fastness 4-5, light fastness ~6
  [13.18] Dyeing mechanism: exhaustion → fixation → wash-off
          "Conventional reactive dyes: only 70% fixed onto fibre"
  [13.19] Stripping conditions
  [13.24] Avitera SE: ~90% fixation, 50% water/energy savings vs conventional

Layer 5 functions model the physical cause-effect relationships linking
operational parameters (Layer 3) and input fabric (Layer 2) to dyed
fabric quality output metrics (Layer 4).
"""

import math
from dataclasses import dataclass


# ─────────────────────────────────────────────────────────────────────────────
# DATA CLASSES — Layer 2, 3, 4
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class InputFabric:
    """
    Layer 2 — Input fabric properties for Reactive Dyeing.

    All fields map 1-to-1 onto FabricQualityOutput (Layer 4) from
    plain_weaving.py. The structural fabric parameters determine dye
    penetration behaviour: high cover factors restrict dye access to
    interior threads; high fabric weight requires more dye and longer
    processing; high crimp values indicate compacted thread geometry
    that slows dye diffusion.
    """
    # From FabricQualityOutput — yarn geometry
    yarn_diameter_warp_mm: float       # Warp yarn diameter in mm (Peirce).
                                       # Thicker threads need more time for dye diffusion
                                       # to reach the fibre core.
    yarn_diameter_weft_mm: float       # Weft yarn diameter in mm.

    # From FabricQualityOutput — fabric cover
    warp_cover_factor: float           # Fractional warp cover (0–1).
                                       # High cover → tightly packed threads → restricted
                                       # dye liquor penetration into the fabric interior.
    weft_cover_factor: float           # Fractional weft cover (0–1).
    total_cover_factor: float          # Combined cover: f_w + f_e - f_w × f_e.
                                       # Approaching 1.0: dense fabric → high risk of
                                       # unlevel dyeing (outside dyed, inside pale).

    # From FabricQualityOutput — crimp state
    warp_crimp_pct: float              # Warp crimp % in fabric. High crimp → more yarn
                                       # per unit area → higher effective fibre mass to dye.
    weft_crimp_pct: float              # Weft crimp %.
    crimp_balance: str                 # "warp_dominant", "balanced", "weft_dominant".

    # From FabricQualityOutput — mechanical weaving outputs
    fell_displacement_mm: float        # Beat-up fell displacement (mm). Proxy for fabric
                                       # compactness — higher values → denser structure.
    beat_up_force_cN_per_cm: float     # Beat-up force per cm (cN/cm).
    fabric_areal_weight_g_m2: float    # Fabric weight in g/m² (GSM). Directly sets the
                                       # mass of substrate (goods) in the dye bath,
                                       # governing dye dosage calculations (% owf).
    weft_tension_at_fell_cN: float     # Weft tension at fell (cN). Highly tensioned yarns
                                       # may have residual stress that affects swelling.

    # From FabricQualityOutput — upstream risk flags
    warp_break_risk: str               # "low", "medium", "high" — weaving warp-break risk.
    weft_break_risk: str               # "low", "medium", "high" — weaving weft-break risk.
    cloth_defect_risk: str             # "low", "medium", "high" — weaving cloth defect risk.
                                       # Cloth defects (thick/thin places) cause uneven dye
                                       # uptake → shade variation in the dyed fabric.

    # From FabricQualityOutput — production context
    production_rate_m_per_min: float   # Upstream weaving rate (m/min).
    production_rate_m2_per_hour: float # Upstream weaving area rate (m²/h).


@dataclass
class ReactiveDyeingParams:
    """
    Layer 3 — Operational parameters specific to Reactive Dyeing.

    Based on exhaust (batch) dyeing process on a winch / jigger / jet
    dyeing machine unless otherwise noted.
    """
    # ── DYE CHEMISTRY ────────────────────────────────────────────────────────
    dye_type: str                    # Reactive dye brand/chemistry type:
                                     # "M_brand"   — dichlorotriazine (DCT), cold brand.
                                     #               Temp: 30–40°C, high reactivity.
                                     #               [Mahapatra 13.4, 13.6]
                                     # "VS"         — vinylsulphone (Remazol). Temp: 60°C.
                                     #               Moderate reactivity. [Mahapatra 13.9]
                                     # "ME"         — bifunctional MCT + VS. Temp: 60–65°C.
                                     #               High fixation. [Mahapatra 13.4]
                                     # "MCT"        — monochlorotriazine. Temp: 80°C.
                                     #               Low reactivity. [Mahapatra 13.9]
                                     # "H_brand"    — monochlorotriazine (hot brand).
                                     #               Temp: 80–95°C. [Mahapatra 13.6]
                                     # "HE"         — high-exhaustion, Temp: 80–90°C.
                                     #               [Mahapatra 13.4]
                                     # "bifunctional_trifunctional" — Avitera SE type.
                                     #               Fixation ~90%. [Mahapatra 13.24]

    dye_concentration_owf_pct: float # Dye concentration as % on weight of fabric (owf).
                                     # Light shade: 0.1–1.0%, medium: 1.0–3.0%,
                                     # dark: 3.0–8.0%. Governs salt requirement.
                                     # Mahapatra 13.8: electrolyte concentration is a
                                     # key cycle factor proportional to shade depth.

    # ── ELECTROLYTE (SALT) ───────────────────────────────────────────────────
    salt_concentration_g_L: float    # NaCl or Na2SO4 (Glauber's salt) in g/L.
                                     # Mahapatra 13.18: "electrolyte neutralizes
                                     # [negative surface charge], assists exhaustion."
                                     # Light shade: 20–30 g/L, dark shade: 60–80 g/L.
                                     # "Salt-controllable dyes" (Class B direct, p. 1572):
                                     # exhaustion controlled by incremental salt addition.

    # ── ALKALI (FIXATION AGENT) ───────────────────────────────────────────────
    alkali_type: str                 # Type of alkali added after exhaustion phase:
                                     # "NaHCO3"   — pH ~8.5 (high-reactivity dyes).
                                     #               Mahapatra 13.6: high reactivity uses
                                     #               medium alkali (NaHCO3).
                                     # "Na2CO3"   — pH ~10.5–11 (soda ash; most common).
                                     #               Moderate reactivity dyes. [13.6]
                                     # "NaOH"     — pH ~12–13 (strong alkali for low
                                     #               reactivity / H-brand). [13.6]
                                     # "Na2CO3+NaOH" — mixed alkali for VS dyes.
    alkali_concentration_g_L: float  # Alkali dose in g/L. Typical: NaHCO3 5–15 g/L,
                                     # Na2CO3 10–20 g/L, NaOH 5–10 g/L.

    # ── PROCESS TEMPERATURE ───────────────────────────────────────────────────
    dyeing_temperature_C: float      # Dyeing temperature in °C.
                                     # M_brand: 30–40°C, VS/ME: 60°C, MCT: 80°C,
                                     # H_brand: 80–95°C. (Mahapatra 13.5, 13.6)
                                     # Temperature governs both diffusion rate (positive)
                                     # and hydrolysis rate (negative — competing reaction).

    # ── PROCESS TIMES ────────────────────────────────────────────────────────
    exhaustion_time_min: float       # Time in minutes for exhaustion phase (with salt,
                                     # before alkali addition). Typical: 20–45 min.
    fixation_time_min: float         # Time in minutes for fixation phase (after alkali
                                     # addition). Typical: 30–60 min.
    wash_off_time_min: float         # Time in minutes for complete wash-off sequence
                                     # (hot wash + soap + cold wash). Typical: 30–60 min.
                                     # Mahapatra 13.18: "a good wash must be applied to
                                     # remove extra and unfixed dyes... necessary for
                                     # level dyeing and good wash-fastness."

    # ── LIQUOR RATIO ─────────────────────────────────────────────────────────
    liquor_ratio: float              # Machine liquor ratio (MLR) = volume of dye
                                     # liquor / weight of fabric (L/kg).
                                     # Winch/jigger: 1:15–1:30.
                                     # Jet/soft-flow: 1:6–1:12.
                                     # Lower MLR → higher exhaustion, less water,
                                     # less energy. Mahapatra Fig 13.7: Avitera SE
                                     # achieves 15–20 L/kg vs conventional 40.5 L/kg.

    # ── MACHINE TYPE ─────────────────────────────────────────────────────────
    machine_type: str                # "jigger", "winch", "jet", "soft_flow",
                                     # "pad_batch", "pad_steam".
                                     # Governs MLR range, fabric tension during dyeing,
                                     # and throughput rate.

    # ── WATER QUALITY ────────────────────────────────────────────────────────
    water_hardness_ppm: float        # Water hardness in ppm (mg/L CaCO3 equivalent).
                                     # Mahapatra 13.8: "quality of water" is a key
                                     # cycle factor. Hard water Ca²⁺/Mg²⁺ ions precipitate
                                     # dye anions → reduced exhaustion, dye spots.
                                     # Soft: <50 ppm, medium: 50–200, hard: >200 ppm.

    # ── PRETREATMENT STATE ───────────────────────────────────────────────────
    fabric_is_mercerized: bool       # Mercerization (NaOH swelling of cotton) increases
                                     # dye uptake and brilliance.
                                     # Mahapatra 13.1: "colour yield and brilliancy of
                                     # shades are enhanced significantly by mercerization."
    fabric_is_scoured: bool          # Scouring removes wax and size from grey fabric.
                                     # Mahapatra 13.1: "good pretreatment is a prerequisite."
                                     # Unsoured fabric → poor wetting → unlevel dyeing.

    # ── MACHINE CONDITION ────────────────────────────────────────────────────
    ambient_temperature_C: float      # Room temperature (°C). Affects heat-up curve.
    maintenance_interval_hours: float # Machine service interval in hours.
    operating_hours_since_maintenance: float  # Hours since last service.


@dataclass
class DyedFabricOutput:
    """
    Layer 4 — Predicted output quality metrics for Reactive Dyeing.
    """
    # ── DYE BATH EQUILIBRIUM ─────────────────────────────────────────────────
    dye_bath_pH: float                  # Estimated pH after alkali addition.
    exhaustion_pct: float               # % of initial dye absorbed by fabric:
                                        # E% = (initial_dye - remaining_bath_dye) /
                                        #       initial_dye × 100.
                                        # Mahapatra 13.4: high-reactivity dyes achieve
                                        # high exhaustion at 60°C.
    fixation_pct: float                 # % of applied dye covalently bonded to fibre:
                                        # Conventional reactive: 60–80%.
                                        # Bifunctional/trifunctional: up to ~90%.
                                        # Mahapatra 13.2 and 13.24.
    hydrolysis_pct: float               # % of dye hydrolysed (reacted with water, not
                                        # fibre). Hydrolysed dye cannot form covalent
                                        # bonds and must be washed off completely.
                                        # hydrolysis% = 100 - fixation_pct (of applied dye).
    unfixed_dye_on_fabric_pct: float    # % of applied dye physically adsorbed but NOT
                                        # covalently bonded. Must be removed in wash-off.
                                        # = exhaustion% - fixation% (approx.).

    # ── SHADE AND FASTNESS ───────────────────────────────────────────────────
    colour_yield_relative: float        # Relative colour yield (0–1.0).
                                        # Driven by fixation%, mercerization, and fabric
                                        # pretreatment quality.
    wash_fastness_rating: float         # ISO wash fastness rating (1–5). Reactive dyes:
                                        # "very good wash fastness with rating 4–5."
                                        # [Mahapatra 13.12] Decreases if unfixed dye
                                        # is not fully removed in wash-off.
    light_fastness_rating: float        # ISO light fastness rating (1–8). Reactive dyes:
                                        # "very good light fastness with rating about 6."
                                        # [Mahapatra 13.12]
    rubbing_fastness_dry: float         # ISO rubbing fastness — dry (1–5). Reactive: 3–4.
    rubbing_fastness_wet: float         # ISO rubbing fastness — wet (1–5). Reactive: 3–4.

    # ── LEVELNESS ────────────────────────────────────────────────────────────
    levelness_risk: str                 # "low", "medium", "high" — risk of shade
                                        # variation across the fabric width/length.
    dye_penetration_quality: str        # "full", "partial", "surface_only" — describes
                                        # depth of dye penetration through yarn cross-section.
                                        # Dense fabrics (high cover factor) at low MLR
                                        # and short exhaustion time → surface-only dyeing.

    # ── SUSTAINABILITY METRICS ───────────────────────────────────────────────
    water_consumption_L_per_kg: float   # Total process water in L/kg of fabric.
                                        # Conventional: ~40.5 L/kg; Best available
                                        # technology: ~15.2 L/kg. [Mahapatra Fig 13.7]
    salt_load_g_per_kg: float           # Total salt discharged per kg of fabric (g/kg).
                                        # Environmental concern: Mahapatra 13.23:
                                        # "Reducing salt consumption… in the effluent."
    total_process_time_min: float       # Total dyeing cycle time in minutes.
    energy_relative: float              # Relative energy index (1.0 = conventional).
                                        # Avitera SE: 0.26× conventional [Mahapatra Fig 13.7].

    # ── EFFLUENT ─────────────────────────────────────────────────────────────
    effluent_dye_load_pct: float        # % of applied dye discharged in effluent:
                                        # = 100 - fixation%. High-unfixed → high effluent
                                        # dye load → difficult wastewater treatment.

    # ── RISK FLAGS ───────────────────────────────────────────────────────────
    unlevel_dyeing_risk: str            # "low", "medium", "high".
    fabric_damage_risk: str             # "low", "medium", "high" — NaOH at high temp
                                        # can degrade cellulose (oxycellulose formation).
    warnings: list                      # Out-of-range parameter warnings.


# ─────────────────────────────────────────────────────────────────────────────
# LAYER 5 — SIMULATION FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def calculate_dye_bath_pH(alkali_type: str, alkali_concentration_g_L: float) -> float:
    """
    Estimates dye bath pH after alkali addition.

    Source: Mahapatra Section 13.6:
    - "High reactivity dyes: pH is maintained 10–11 by using NaHCO3."
    - "Lower/medium reactivity dyes: pH maintained 11–12 by using Na2CO3."
    - "Low reactivity: strong alkali NaOH used." (pH ~12–13)

    Section 13.9:
    - VS dyes: "pH is 11.5 using soda ash and caustic soda."
    - MCT dyes: "pH value of 10.5 for proper fixation on cellulosic fibres."

    pH determination:
    NaHCO3 buffer: intrinsic pH 8.3, rises with concentration to ~8.5–9.0.
    Na2CO3: buffered in the 10.5–11.5 range.
    Na2CO3 + NaOH mixture: 11.0–12.0.
    NaOH: pH driven by concentration → pH = 14 + log[OH-] mol/L.
    For NaOH (MW=40): [OH-] = conc_g_L / 40 mol/L.
    """
    alkali = alkali_type.lower().replace(" ", "").replace("+", "_plus_")

    if "nahco3" in alkali or "bicarbonate" in alkali:
        # NaHCO3: buffer centred at pH ~8.3–9.0
        base_pH = 8.3
        pH = base_pH + 0.05 * math.log(max(alkali_concentration_g_L, 0.1))
        return round(min(pH, 9.0), 1)

    elif "na2co3_plus_naoh" in alkali or ("na2co3" in alkali and "naoh" in alkali):
        # Mixed alkali: soda ash + caustic soda → pH 11.0–12.0
        base_pH = 11.0
        pH = base_pH + 0.15 * math.log(max(alkali_concentration_g_L, 0.1))
        return round(min(pH, 12.2), 1)

    elif "na2co3" in alkali or "soda_ash" in alkali or "sodaash" in alkali:
        # Na2CO3: pH 10.5–11.5
        base_pH = 10.4
        pH = base_pH + 0.10 * math.log(max(alkali_concentration_g_L, 0.1))
        return round(min(pH, 11.5), 1)

    else:
        # NaOH: strong base, pH from molar concentration
        # MW(NaOH) = 40 g/mol; [OH-] = conc/40 mol/L
        OH_molarity = alkali_concentration_g_L / 40.0
        if OH_molarity > 0:
            pH = 14.0 + math.log10(OH_molarity)
        else:
            pH = 12.0
        return round(min(14.0, max(12.0, pH)), 1)


def calculate_exhaustion(
    dye_type: str,
    dye_concentration_owf_pct: float,
    salt_concentration_g_L: float,
    dyeing_temperature_C: float,
    exhaustion_time_min: float,
    liquor_ratio: float,
    total_cover_factor: float,
    fabric_areal_weight_g_m2: float,
    fabric_is_scoured: bool,
    water_hardness_ppm: float
) -> float:
    """
    Predicts dye exhaustion % (fraction of dye absorbed by the fabric
    from the bath, before fixation).

    Source: Mahapatra Section 13.18:
    "When fibre is immersed in dye liquor, an electrolyte is added to
    assist the exhaustion of dye. Here NaCl is used as the electrolyte.
    This electrolyte neutralizes [the negative surface charge]. So when
    the textile material is introduced to dye liquor, the dye is
    exhausted on to the fibre."

    Mahapatra p. 1550-1580 (direct dye exhaustion principles, equally
    applicable to reactive pre-fixation phase):
    - "Influence of temperature on exhaustion": higher temperature → faster
      diffusion rate → faster exhaustion.
    - "Influence of liquor ratio on exhaustion": lower MLR → higher
      exhaustion (bath is more concentrated relative to goods).
    - Salt: "electrolyte neutralizes absorption" → increases driving force.
    - Dye concentration: higher %owf shade → proportionally more dye in
      bath → equilibrium shifts; exhaustion % slightly lower for dark shades
      because the dye bath remains more concentrated at equilibrium.

    Dye-type maximum exhaustion (E_max) at optimal conditions:
    - M_brand (DCT): E_max ~80% (high reactivity, fast exhaustion).
    - VS (vinylsulphone): E_max ~75%.
    - ME (bifunctional): E_max ~85%.
    - MCT: E_max ~70%.
    - H_brand: E_max ~72%.
    - HE: E_max ~85%.
    - bifunctional_trifunctional: E_max ~92% (Avitera SE).

    Physical model: first-order exhaustion kinetics calibrated to
    published process conditions:
        E(t) = E_max × (1 - exp(-k_e × t))
    where k_e depends on temperature, salt concentration, and liquor ratio.

    Water hardness: Ca²⁺ and Mg²⁺ ions form precipitates with dye anions
    → effective dye concentration reduced → lower exhaustion.
    Mahapatra 13.8: "quality of water" is explicitly listed as a key
    cycle factor in reactive dyeing.
    """
    # Maximum equilibrium exhaustion by dye type
    E_max_map = {
        "m_brand":                    80.0,
        "vs":                         75.0,
        "me":                         85.0,
        "mct":                        70.0,
        "h_brand":                    72.0,
        "he":                         85.0,
        "bifunctional_trifunctional": 92.0,
    }
    dtype = dye_type.lower().replace("-", "_").replace(" ", "_")
    E_max = E_max_map.get(dtype, 75.0)

    # Optimal temperature for each dye type (Mahapatra 13.5, 13.6)
    optimal_T_map = {
        "m_brand": 35.0, "vs": 60.0, "me": 62.0,
        "mct": 80.0, "h_brand": 88.0, "he": 85.0,
        "bifunctional_trifunctional": 60.0,
    }
    T_opt = optimal_T_map.get(dtype, 60.0)

    # Temperature factor: Arrhenius-type, peaks at optimal temperature
    # At T_opt: factor = 1.0; deviation penalised
    T_dev = abs(dyeing_temperature_C - T_opt) / max(T_opt, 1.0)
    T_factor = math.exp(-1.5 * T_dev ** 2)

    # Salt factor: salt drives exhaustion above a threshold
    # Light shade: 20 g/L sufficient; dark shade: 60–80 g/L.
    # Reference salt for optimal exhaustion: 50 g/L.
    salt_factor = 1.0 - math.exp(-salt_concentration_g_L / 40.0)

    # Liquor ratio (MLR) factor: lower MLR → higher exhaustion
    # Reference MLR: 1:15 (L/kg). E ∝ 1/(1 + k_LR × MLR)
    LR_factor = 15.0 / max(liquor_ratio, 5.0)
    LR_factor = min(1.3, LR_factor)  # cap benefit at very low MLR

    # Time factor: first-order kinetics
    # Rate constant k_e calibrated to achieve 90% of E_max by typical exhaustion_time
    k_e = 0.04 * T_factor  # s⁻¹-analogue; increases with temperature
    time_factor = 1.0 - math.exp(-k_e * exhaustion_time_min)

    # Shade depth penalty: heavier shades have lower exhaustion %
    # (more dye in bath; equilibrium % is lower)
    if dye_concentration_owf_pct > 3.0:
        shade_penalty = 0.93
    elif dye_concentration_owf_pct > 1.0:
        shade_penalty = 0.97
    else:
        shade_penalty = 1.00

    # Fabric cover factor: high cover → restricted dye bath penetration
    cover_penalty = 1.0 - 0.15 * max(0.0, total_cover_factor - 0.70)

    # Pretreatment: unsoured fabric → poor wetting → lower exhaustion
    pretreatment_factor = 1.0 if fabric_is_scoured else 0.82

    # Water hardness: Ca²⁺/Mg²⁺ precipitate dye anions → reduces effective
    # dye concentration and thus exhaustion
    if water_hardness_ppm > 200:
        hardness_factor = 0.88
    elif water_hardness_ppm > 100:
        hardness_factor = 0.94
    else:
        hardness_factor = 1.00

    E = (E_max * salt_factor * LR_factor * time_factor
         * shade_penalty * cover_penalty * pretreatment_factor * hardness_factor)
    return round(min(98.0, max(20.0, E)), 1)


def calculate_fixation(
    dye_type: str,
    dye_bath_pH: float,
    dyeing_temperature_C: float,
    fixation_time_min: float,
    exhaustion_pct: float,
    fabric_is_mercerized: bool
) -> float:
    """
    Predicts dye fixation % — the fraction of applied dye that forms
    covalent bonds with the cellulose fibre.

    Source: Mahapatra Section 13.2:
    "Conventional reactive dyes for cellulosic fibres suffer an obvious
    drawback in that only 70% of the dye is fixed onto the fibre; the
    remainder of the dye undergoes hydrolysis in the dye bath."

    Section 13.24 (Avitera SE):
    "In conventional dyes, 60–80 per cent of the dye applied to cotton
    during dyeing is fixed, but in AVITERA® SE, this is nearly 90 per cent."

    Physical mechanism (Mahapatra 13.18):
    "Fixation of dye means the reaction of reactive group of dye with
    terminal –OH or –NH2 group of fibre, forming a strong covalent bond.
    This is controlled by maintaining proper pH by adding alkali."

    Two competing reactions:
    (1) Dye + Cellulose-OH → Dye-O-Cellulose (fixation, desired)
    (2) Dye + H₂O → Dye-OH (hydrolysis, undesired)

    Both reactions are base-catalysed. At higher pH:
    - Rate of fixation increases (more cellulosate anions Cell-O⁻ available)
    - Rate of hydrolysis ALSO increases (more OH⁻ for nucleophilic attack)
    The net fixation % depends on the ratio k_fix / k_hydrolysis.

    Temperature:
    - Higher temperature → faster both reactions.
    - H-brand MCT dyes require high temperature for sufficient reactivity.
    - M-brand DCT dyes: high temperature increases hydrolysis faster than
      fixation → fix at 30–40°C.

    Maximum fixation by dye type (Mahapatra 13.2, 13.24, 13.4):
    - M_brand (DCT): 75% (fast reaction, some hydrolysis in bath)
    - VS: 75–80%
    - ME bifunctional: ~80% (two reactive groups, second fixes if first hydrolysed)
    - MCT: 70%
    - H_brand: 72%
    - HE: 80%
    - bifunctional_trifunctional: 90% (Avitera SE, three reactive groups) [13.24]

    Mercerisation bonus: Mahapatra 13.1: "colour yield and brilliancy of
    shades are enhanced significantly by mercerization." Mercerised cotton
    has an expanded lattice that allows better dye penetration and more
    hydroxyl groups accessible → fixation improves ~5–8%.

    Time factor: first-order fixation kinetics — fixation rate falls as
    reactive groups are consumed; modelled as:
        F(t) = F_max × (1 - exp(-k_f × t))
    """
    # Maximum fixation by dye type
    F_max_map = {
        "m_brand":                    75.0,
        "vs":                         78.0,
        "me":                         82.0,
        "mct":                        70.0,
        "h_brand":                    72.0,
        "he":                         80.0,
        "bifunctional_trifunctional": 90.0,  # Avitera SE [Mahapatra 13.24]
    }
    dtype = dye_type.lower().replace("-", "_").replace(" ", "_")
    F_max = F_max_map.get(dtype, 72.0)

    # Optimal pH ranges for each dye type [Mahapatra 13.6, 13.9]
    optimal_pH_map = {
        "m_brand": 8.5,                   # NaHCO3 → pH ~8.5
        "vs": 11.5,                        # Na2CO3+NaOH → pH 11.5
        "me": 11.0,
        "mct": 10.5,                       # Na2CO3 → pH ~10.5
        "h_brand": 11.0,
        "he": 11.0,
        "bifunctional_trifunctional": 10.5,
    }
    pH_opt = optimal_pH_map.get(dtype, 11.0)

    # pH factor: parabolic around optimum — too low → slow fixation;
    # too high → excess hydrolysis (OH⁻ competes with Cell-O⁻)
    pH_dev = abs(dye_bath_pH - pH_opt)
    if pH_dev <= 0.5:
        pH_factor = 1.00
    elif pH_dev <= 1.5:
        pH_factor = 1.0 - 0.12 * pH_dev
    else:
        pH_factor = max(0.55, 1.0 - 0.18 * pH_dev)

    # Temperature factor: activates fixation but also hydrolysis
    # Optimal fixation temperature matches dye-type design temperature
    T_opt_map = {"m_brand": 35.0, "vs": 60.0, "me": 62.0,
                 "mct": 80.0, "h_brand": 88.0, "he": 85.0,
                 "bifunctional_trifunctional": 58.0}
    T_opt = T_opt_map.get(dtype, 60.0)
    T_diff = dyeing_temperature_C - T_opt
    if abs(T_diff) <= 5:
        T_factor = 1.00
    elif T_diff > 5:
        # Over-temperature: excess hydrolysis; for MCT/H-brand this is less severe
        if dtype in ("mct", "h_brand"):
            T_factor = 1.0 - 0.005 * (T_diff - 5)
        else:
            T_factor = 1.0 - 0.015 * (T_diff - 5)
    else:
        # Under-temperature: insufficient activation
        T_factor = max(0.50, 1.0 + 0.020 * T_diff)

    # Time factor: fixation saturates after sufficient alkali time
    k_f = 0.04  # First-order rate constant (min⁻¹); calibrated to typical 45 min fix
    time_factor = 1.0 - math.exp(-k_f * fixation_time_min)

    # Exhaustion coupling: only exhausted dye can be fixed
    # Fixation% (of applied) = fixation of exhausted fraction
    exhaustion_coupling = min(1.0, exhaustion_pct / 85.0)

    # Mercerisation bonus [Mahapatra 13.1]
    mercer_factor = 1.07 if fabric_is_mercerized else 1.00

    F = F_max * pH_factor * T_factor * time_factor * exhaustion_coupling * mercer_factor
    return round(min(95.0, max(30.0, F)), 1)


def calculate_hydrolysis(fixation_pct: float) -> float:
    """
    Predicts total dye hydrolysis % (dye reacted with water, not fibre).

    Source: Mahapatra Section 13.2:
    "Only 70% of the dye is fixed onto the fibre; the remainder of the
    dye undergoes hydrolysis in the dye bath."

    Hydrolysis is the principal competing reaction in reactive dyeing:
        Dye-Cl + H₂O → Dye-OH + HCl  (haloheterocycle dyes)
        Dye-CH=CH₂ + H₂O → Dye-CH₂-CH₂-OH  (vinyl sulphone dyes)

    The hydrolysed dye CANNOT form covalent bonds with cellulose. It
    must be completely removed in the wash-off stage to achieve the
    stated wash fastness rating. Inefficient wash-off of hydrolysed dye
    leads to reduced wash fastness (bleeding in wash).

    Simple mass balance:
        hydrolysis% = 100 - fixation%  (of applied dye)
    This includes both bath hydrolysis (before exhaustion) and fibre-
    surface hydrolysis (after exhaustion but before covalent bond
    formation).
    """
    hydrolysis = 100.0 - fixation_pct
    return round(max(5.0, hydrolysis), 1)


def calculate_unfixed_dye_on_fabric(
    exhaustion_pct: float,
    fixation_pct: float
) -> float:
    """
    Predicts % of applied dye that is physically adsorbed on the fabric
    but NOT covalently bonded — must be removed in wash-off.

    Source: Mahapatra Section 13.18:
    "As the dyeing is completed, a good wash must be applied to the
    material to remove extra and unfixed dyes from material surface.
    This is necessary for level dyeing and good wash-fastness."

    The unfixed fraction on fabric ≈ exhaustion% - fixation%
    (simplified, ignoring re-desorption kinetics during wash-off).
    This quantity drives wash-off requirements: more unfixed dye →
    more wash baths needed → more water and energy.

    Mahapatra Fig 13.7 (Avitera SE comparison):
    - Conventional dyeing: 15–30% unfixed dye to wash off.
    - Avitera SE: 5% or less unfixed dye.
    "With 5 per cent or less unfixed dye to be removed instead of the
    usual 15–30 per cent, the washing-off process can be drastically
    curtailed."
    """
    unfixed = max(0.0, exhaustion_pct - fixation_pct)
    return round(min(60.0, unfixed), 1)


def calculate_wash_fastness(
    fixation_pct: float,
    wash_off_time_min: float,
    unfixed_dye_on_fabric_pct: float,
    dyeing_temperature_C: float
) -> float:
    """
    Predicts ISO wash fastness rating (1–5).

    Source: Mahapatra Section 13.12:
    "Textile materials dyed with reactive dyes have very good wash
    fastness with rating [4–5]. Reactive dye gives brighter shades and
    has moderate rubbing fastness."

    Wash fastness in reactive dyeing depends on:
    (1) Fixation% — covalently bonded dye cannot bleed; the higher the
        fixation, the better the fastness baseline.
    (2) Completeness of wash-off — if hydrolysed/unfixed dye remains on
        the fabric surface, it bleeds in the first wash, reducing the
        apparent fastness.
    (3) Dyeing temperature — excessively high temperature can cause
        partial dye degradation or incomplete covalent bond stability
        (especially for some sensitive chromophores).

    Rating scale:
    - 5.0: excellent (no staining in wash test; achievable with ≥80% fixation
      + thorough wash-off)
    - 4.0–4.5: very good (typical for well-processed reactive dyed cotton)
    - 3.0–3.5: acceptable (marginal wash-off or moderate fixation)
    - < 3.0: poor (unfixed dye bleeding, indicates process failure)

    Calibration to Mahapatra 13.12: target rating 4–5 for reactive dyes.
    """
    # Base rating from fixation %
    if fixation_pct >= 85:
        base = 4.8
    elif fixation_pct >= 75:
        base = 4.3
    elif fixation_pct >= 65:
        base = 3.8
    elif fixation_pct >= 55:
        base = 3.3
    else:
        base = 2.5

    # Wash-off penalty: inadequate wash-off leaves hydrolysed dye
    if wash_off_time_min < 20:
        washoff_penalty = 0.8  # severe — barely rinsed
    elif wash_off_time_min < 35:
        washoff_penalty = 0.92
    else:
        washoff_penalty = 1.00

    # Residual unfixed dye on fabric: each additional 5% → -0.15 rating
    residual_penalty = min(1.0, 1.0 - (unfixed_dye_on_fabric_pct / 5.0) * 0.08)
    residual_penalty = max(0.5, residual_penalty)

    # High temperature may degrade chromophore stability
    if dyeing_temperature_C > 95:
        temp_factor = 0.97
    else:
        temp_factor = 1.00

    rating = base * washoff_penalty * residual_penalty * temp_factor
    return round(min(5.0, max(1.0, rating)), 1)


def calculate_colour_yield(
    fixation_pct: float,
    fabric_is_mercerized: bool,
    fabric_is_scoured: bool,
    total_cover_factor: float,
    dye_penetration_quality: str
) -> float:
    """
    Predicts relative colour yield (0.0–1.0 scale).

    Source: Mahapatra Section 13.1:
    "The colour yield and brilliancy of shades are enhanced significantly
    by mercerization."
    Section 13.12: "Reactive dyes are water-soluble anionic dyes... good
    pretreatment of the material is a prerequisite."

    Colour yield reflects the amount of dye actually contributing to
    visible colour relative to the maximum possible for the dye application:
    - Fixation % is the primary driver (more covalent dye = more colour).
    - Mercerisation: NaOH swells cotton crystal structure → better dye
      diffusion and more accessible hydroxyl groups → deeper, brighter shades.
    - Scouring: removes natural wax and added size from grey fabric;
      unsoured fabric has poor wetting → dye sits on surface → poor yield.
    - Dye penetration depth: surface-only dyeing means much of the yarn
      cross-section is undyed → fabric appears paler in cross-section →
      lower effective colour yield.
    - Dense fabric (high total cover): reduced liquor penetration path
      length → less uniform dye distribution → marginally lower yield.
    """
    base_yield = fixation_pct / 100.0

    mercer_bonus = 0.10 if fabric_is_mercerized else 0.0
    scour_factor = 1.00 if fabric_is_scoured else 0.82
    pen_factor = {"full": 1.00, "partial": 0.87, "surface_only": 0.72}.get(
        dye_penetration_quality, 0.87
    )
    cover_penalty = max(0.85, 1.0 - 0.10 * max(0.0, total_cover_factor - 0.75))

    yield_val = (base_yield + mercer_bonus) * scour_factor * pen_factor * cover_penalty
    return round(min(1.0, max(0.0, yield_val)), 3)


def assess_dye_penetration_quality(
    total_cover_factor: float,
    dyeing_temperature_C: float,
    exhaustion_time_min: float,
    liquor_ratio: float,
    yarn_diameter_weft_mm: float
) -> str:
    """
    Qualitative assessment of dye penetration depth through yarn cross-section.

    Source: Mahapatra Section 13.8: fabric cover and pretreatment affect
    "dyeing temperature" and "dyeing time" as key cycle factors.

    Dye penetration into a yarn is governed by diffusion through the
    liquid-filled pores between fibres. Fick's law governs diffusion:
        J = -D × (dC/dr)
    where D (diffusivity) increases with temperature and time.

    For a yarn of diameter d, the diffusion front reaches the centre in
    a characteristic time proportional to d² / D. At insufficient time
    or low temperature, dye remains in the outer fibre layers → "ring dyeing"
    or surface-only penetration, which gives poor rub fastness and
    shade change on abrasion.

    Dense fabrics (high total cover factor) also slow bulk liquor
    penetration, reducing the effective dye concentration at the
    yarn surface and compounding the problem.

    Assessment thresholds calibrated to standard textile processing:
    """
    penetration_score = 0

    # Temperature: higher temperature → faster diffusion
    if dyeing_temperature_C >= 70:
        penetration_score += 3
    elif dyeing_temperature_C >= 50:
        penetration_score += 2
    else:
        penetration_score += 1  # cold-brand: lower temperature

    # Time: longer exhaustion time → more diffusion
    if exhaustion_time_min >= 45:
        penetration_score += 3
    elif exhaustion_time_min >= 25:
        penetration_score += 2
    else:
        penetration_score += 1

    # Liquor ratio: lower MLR → dye is more concentrated at fabric surface
    if liquor_ratio <= 10:
        penetration_score += 3
    elif liquor_ratio <= 20:
        penetration_score += 2
    else:
        penetration_score += 1

    # Yarn thickness: thicker yarns need more time / temperature
    if yarn_diameter_weft_mm > 0.30:
        penetration_score -= 2  # coarse yarn — harder to penetrate
    elif yarn_diameter_weft_mm > 0.22:
        penetration_score -= 1

    # Dense fabric: high cover restricts liquor flow
    if total_cover_factor > 0.85:
        penetration_score -= 2
    elif total_cover_factor > 0.75:
        penetration_score -= 1

    if penetration_score >= 7:
        return "full"
    elif penetration_score >= 4:
        return "partial"
    else:
        return "surface_only"


def assess_levelness_risk(
    dye_type: str,
    salt_concentration_g_L: float,
    dyeing_temperature_C: float,
    exhaustion_pct: float,
    total_cover_factor: float,
    cloth_defect_risk: str,
    fabric_is_scoured: bool
) -> str:
    """
    Qualitative assessment of unlevel (uneven) dyeing risk.

    Source: Mahapatra Sections 13.4, 13.8, 13.18.

    Levelness refers to the uniformity of dye uptake across the fabric.
    Reactive dyeing risks several forms of unlevel results:

    (1) Strike rate mismatch (too-fast exhaustion):
        If dye exhausts very rapidly (e.g. M-brand at slightly elevated
        temperature), the dye deposits unevenly before it can migrate
        to equilibrium. The faster the strike rate relative to the
        circulation rate of the machine, the more unlevel the result.
        Mahapatra 13.4 (H-brand): "less sensitive to Glauber salt, time
        and temperature… level dyeing results." Some dye classes require
        careful salt addition to control exhaustion rate.

    (2) Fabric structure variation (from upstream weaving):
        Cloth defects (thick/thin places, stitching) present different
        thread densities. Denser areas take up dye faster → barré stripes.
        Upstream cloth_defect_risk flag directly maps to levelness risk.

    (3) Pretreatment: unsoured fabric has wax patches → dye repulsion
        in those areas → pale spots or streaks.

    (4) High exhaustion% at very short time: rapid exhaustion that
        outpaces machine liquor circulation → contact dyeing at entry
        point darker than rest of fabric.
    """
    risk_score = 0

    # Fast-striking dyes at suboptimal conditions
    dtype = dye_type.lower().replace("-", "_").replace(" ", "_")
    if dtype == "m_brand" and dyeing_temperature_C > 45:
        risk_score += 2  # DCT over-temperature → too-fast strike
    if dtype in ("mct", "h_brand") and dyeing_temperature_C < 75:
        risk_score += 2  # Under-temperature → patchy fixation

    # Very high exhaustion at short time → possible contact dyeing
    if exhaustion_pct > 85 and salt_concentration_g_L > 70:
        risk_score += 1  # High salt + high exhaustion → rapid strike

    # Dense fabric: poor liquor penetration → centre of cloth paler
    if total_cover_factor > 0.85:
        risk_score += 2
    elif total_cover_factor > 0.75:
        risk_score += 1

    # Upstream weaving defect inheritance
    if cloth_defect_risk.lower() == "high":
        risk_score += 3
    elif cloth_defect_risk.lower() == "medium":
        risk_score += 1

    # Pretreatment: unsoured → wax patches → unlevel wetting
    if not fabric_is_scoured:
        risk_score += 3  # Major levelness risk

    # Low salt: insufficient electrolyte → poor dye substantivity → migrates unevenly
    if salt_concentration_g_L < 15:
        risk_score += 2

    if risk_score <= 2:
        return "low"
    elif risk_score <= 5:
        return "medium"
    else:
        return "high"


def assess_fabric_damage_risk(
    alkali_type: str,
    dye_bath_pH: float,
    dyeing_temperature_C: float,
    fixation_time_min: float,
    operating_hours_ratio: float
) -> str:
    """
    Qualitative assessment of fabric damage risk during reactive dyeing.

    Source: Mahapatra Section 13.18.

    Two key damage mechanisms in reactive dyeing of cotton:

    (1) Oxycellulose formation (alkali + oxygen + heat):
        At high pH (>12) with elevated temperature and dissolved oxygen,
        cellulose can be oxidised to oxycellulose — a degraded, brittle
        form that results in reduced tensile strength and premature
        fabric failure in use. Risk increases with:
        - pH > 12 (NaOH at high concentration)
        - Temperature > 60°C
        - Extended treatment time
        - Poor liquor circulation (stagnant zones → local alkali build-up)

    (2) Hydrolytic degradation:
        At pH > 13 and T > 95°C, the 1,4-glycosidic bonds in cellulose
        can be hydrolytically cleaved → loss of degree of polymerisation
        → reduced fabric strength. Less relevant for reactive dyeing
        (temperatures are below this threshold except for some H-brand
        processes), but relevant for poorly controlled NaOH additions.

    Machine condition: worn pump seals or heating elements can create
    local hot-spots or pH gradients that concentrate damage.
    """
    risk_score = 0

    # pH risk: alkaline damage to cellulose
    if dye_bath_pH >= 12.5:
        risk_score += 3  # severe alkaline conditions
    elif dye_bath_pH >= 12.0:
        risk_score += 2
    elif dye_bath_pH >= 11.5:
        risk_score += 1

    # Temperature × pH interaction: both together amplify damage
    if dyeing_temperature_C > 80 and dye_bath_pH >= 12.0:
        risk_score += 2  # synergistic cellulose attack
    elif dyeing_temperature_C > 70 and dye_bath_pH >= 11.5:
        risk_score += 1

    # Extended high-pH treatment time
    if fixation_time_min > 60 and dye_bath_pH >= 12.0:
        risk_score += 1

    # Alkali type: NaOH is more aggressive than Na2CO3
    if "naoh" in alkali_type.lower() and dye_bath_pH >= 12.0:
        risk_score += 1

    # Machine maintenance: worn circulation pumps → uneven pH distribution
    if operating_hours_ratio > 1.0:
        risk_score += 1

    if risk_score <= 1:
        return "low"
    elif risk_score <= 4:
        return "medium"
    else:
        return "high"


def calculate_sustainability_metrics(
    liquor_ratio: float,
    wash_off_time_min: float,
    dyeing_temperature_C: float,
    fixation_pct: float,
    salt_concentration_g_L: float,
    fabric_areal_weight_g_m2: float
) -> tuple:
    """
    Calculates water consumption, salt load, and relative energy index.

    Source: Mahapatra Section 13.24, Figure 13.7 (Avitera SE comparison):

    Conventional dyeing (1 kg cotton):
        Water: 40.5 L/kg
        Energy: 6.5 kg steam
        Time: 7 hours

    Best available technology (BaT) / Avitera SE:
        Water: 15.2 L/kg
        Energy: 1.7 kg steam
        Time: 4 hours

    Mahapatra 13.24: "AVITERA® SE can save more than 50 per cent of
    water, 70 per cent of energy and 50 per cent of time."
    "The washing-off process can be drastically curtailed — with 5% or
    less unfixed dye to remove instead of the usual 15–30%."
    Mahapatra 13.23: "Reducing salt consumption and/or unused dye in
    the effluent." Salt discharge per kg:
        salt_load (g/kg) = salt_concentration_g_L × liquor_ratio (L/kg)

    Water consumption:
        Dyeing bath: liquor_ratio (L/kg)
        Wash-off: proportional to wash_off_time_min and unfixed dye level
            (more unfixed → more wash baths needed)
        Total: dyeing_water + washoff_water

    Energy:
        Primarily from heating the dye bath and maintaining temperature.
        Higher temperature + longer time → more energy.
        Relative energy index normalised to conventional process (=1.0).

    Effluent dye load:
        = 100 - fixation_pct  (% of applied dye in effluent)
    """
    # Dyeing bath water: directly from MLR
    dyeing_water = liquor_ratio  # L/kg

    # Wash-off water: proportional to unfixed dye fraction
    # Each percentage point of unfixed dye requires approximately 0.3 L/kg
    # extra washing (empirical estimate based on standard 3-5 wash baths
    # for conventional vs 1-2 baths for high-fixation dyes).
    unfixed_fraction = max(0.0, 100.0 - fixation_pct) / 100.0
    washoff_water = 2.0 + unfixed_fraction * 15.0  # L/kg

    # Additional wash baths driven by wash-off time
    extra_wash = max(0.0, wash_off_time_min - 30.0) * 0.10  # extra L/kg
    washoff_water += extra_wash

    total_water = dyeing_water + washoff_water

    # Salt load (g/kg of fabric)
    salt_load = salt_concentration_g_L * liquor_ratio

    # Relative energy index (Conventional = 1.0)
    # Energy ≈ mass of water × ΔT × Cp
    # ΔT = (dyeing_temperature - 20) [baseline ambient = 20°C]
    # Cp(water) ≈ 4.18 J/(g·°C)
    # Also includes wash-off bath reheating
    delta_T = max(0.0, dyeing_temperature_C - 20.0)
    energy_heating = total_water * delta_T / 2000.0  # normalised
    energy_ref = 40.5 * (80.0 - 20.0) / 2000.0      # reference: 40.5 L/kg at 80°C
    energy_relative = energy_heating / max(energy_ref, 0.001)

    # Effluent dye load
    effluent_dye_load = round(max(5.0, 100.0 - fixation_pct), 1)

    return (round(total_water, 1),
            round(salt_load, 0),
            round(energy_relative, 2),
            effluent_dye_load)


# ─────────────────────────────────────────────────────────────────────────────
# MASTER SIMULATION FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def simulate_reactive_dyeing(
    fabric: InputFabric,
    params: ReactiveDyeingParams
) -> DyedFabricOutput:
    """
    Master simulation function for Reactive Dyeing.

    Takes Layer 2 (InputFabric — direct output from plain_weaving.py Layer 4)
    and Layer 3 (ReactiveDyeingParams — dyeing operational parameters),
    runs all sub-models, and returns Layer 4 (DyedFabricOutput).
    """
    warnings = []

    # ── PARAMETER VALIDATION ──────────────────────────────────────────────────

    dtype = params.dye_type.lower().replace("-", "_").replace(" ", "_")

    # Dye-type temperature compatibility [Mahapatra 13.5, 13.6]
    temp_limits = {
        "m_brand":  (25, 50),
        "vs":       (50, 70),
        "me":       (55, 70),
        "mct":      (70, 95),
        "h_brand":  (75, 98),
        "he":       (75, 95),
        "bifunctional_trifunctional": (50, 70),
    }
    t_range = temp_limits.get(dtype, (40, 95))
    if not (t_range[0] <= params.dyeing_temperature_C <= t_range[1]):
        warnings.append(
            f"Dyeing temperature ({params.dyeing_temperature_C}°C) is outside the "
            f"recommended range for {params.dye_type} dyes ({t_range[0]}–{t_range[1]}°C). "
            f"[Mahapatra 13.5, 13.6] Incorrect temperature leads to premature hydrolysis "
            "or insufficient fixation."
        )

    # Alkali–dye type mismatch [Mahapatra 13.6]
    alkali_lower = params.alkali_type.lower()
    if dtype == "m_brand" and "naoh" in alkali_lower and "na2co3" not in alkali_lower:
        warnings.append(
            f"Strong alkali (NaOH) is not recommended for {params.dye_type} dyes. "
            "High-reactivity M-brand dyes require a mild alkali (NaHCO3 or Na2CO3) "
            "to avoid excessive hydrolysis. [Mahapatra 13.6]"
        )
    if dtype == "h_brand" and "nahco3" in alkali_lower:
        warnings.append(
            f"NaHCO3 (pH ~8.5) is insufficient for H-brand (low-reactivity) dyes. "
            "A stronger alkali (Na2CO3 or NaOH) at higher temperature is required "
            "for proper covalent bond formation. [Mahapatra 13.6]"
        )

    # Pretreatment checks [Mahapatra 13.1]
    if not params.fabric_is_scoured:
        warnings.append(
            "Fabric has NOT been scoured. Mahapatra 13.1: 'Good pretreatment of the "
            "material is a prerequisite' for reactive dyeing. Unscoured fabric retains "
            "natural wax, size, and impurities that impede wetting and dye penetration, "
            "resulting in unlevel dyeing and poor colour yield."
        )

    # Salt concentration vs shade depth [Mahapatra 13.8]
    if params.dye_concentration_owf_pct > 3.0 and params.salt_concentration_g_L < 50:
        warnings.append(
            f"Dark shade ({params.dye_concentration_owf_pct}% owf) requires higher "
            f"salt concentration (≥50 g/L) for adequate exhaustion. "
            f"Current setting: {params.salt_concentration_g_L} g/L is likely insufficient. "
            "[Mahapatra 13.8: electrolyte concentration is a key cycle factor.]"
        )

    # Water hardness [Mahapatra 13.8]
    if params.water_hardness_ppm > 200:
        warnings.append(
            f"Water hardness ({params.water_hardness_ppm} ppm) is high. "
            "Ca²⁺ and Mg²⁺ ions precipitate dye anions from solution, reducing "
            "effective dye concentration and causing specky dyeing. "
            "Use softened water or add a chelating agent (e.g., 1 g/L sequestrant). "
            "[Mahapatra 13.8: 'quality of water' is a key cycle factor.]"
        )

    # Liquor ratio vs machine type
    lr_limits = {
        "jigger":      (3.0, 8.0),
        "winch":       (15.0, 30.0),
        "jet":         (6.0, 15.0),
        "soft_flow":   (4.0, 12.0),
        "pad_batch":   (0.5, 2.0),
        "pad_steam":   (0.5, 2.0),
    }
    mtype = params.machine_type.lower().replace("-", "_").replace(" ", "_")
    lr_range = lr_limits.get(mtype, (5.0, 30.0))
    if not (lr_range[0] <= params.liquor_ratio <= lr_range[1]):
        warnings.append(
            f"Liquor ratio {params.liquor_ratio}:1 is outside the typical range for "
            f"a {params.machine_type} ({lr_range[0]}–{lr_range[1]}:1). "
            "MLR directly affects exhaustion %, water consumption, and shade depth. "
            "[Mahapatra Fig. 13.7]"
        )

    # Dense fabric warning
    if fabric.total_cover_factor > 0.85:
        warnings.append(
            f"Fabric total cover factor ({fabric.total_cover_factor:.3f}) is very high. "
            "Dense fabrics severely restrict dye liquor penetration into the fabric interior, "
            "leading to ring-dyeing (surface-only) and potential shade variation through "
            "the fabric cross-section. Consider pad dyeing or increasing machine circulation time."
        )

    # Upstream risk inheritance
    if fabric.cloth_defect_risk == "high":
        warnings.append(
            "UPSTREAM: Weaving cloth defect risk was HIGH (thick/thin places, "
            "stitching, pick-spacing variation). These fabric irregularities result "
            "in density differences that cause shade variation in dyeing — denser zones "
            "absorb more dye and appear darker. Shade correction after dyeing is very difficult."
        )

    # Maintenance check
    maintenance_ratio = (params.operating_hours_since_maintenance
                         / max(params.maintenance_interval_hours, 1.0))
    if maintenance_ratio > 1.0:
        warnings.append(
            f"Dyeing machine maintenance is overdue "
            f"({params.operating_hours_since_maintenance:.0f} h / "
            f"{params.maintenance_interval_hours:.0f} h interval). "
            "Worn pump impellers, blocked jets, and faulty temperature probes lead to "
            "uneven liquor circulation and temperature gradients → unlevel dyeing."
        )

    # ── RUN SIMULATION MODELS ─────────────────────────────────────────────────

    dye_bath_pH = calculate_dye_bath_pH(
        params.alkali_type, params.alkali_concentration_g_L
    )

    exhaustion_pct = calculate_exhaustion(
        params.dye_type,
        params.dye_concentration_owf_pct,
        params.salt_concentration_g_L,
        params.dyeing_temperature_C,
        params.exhaustion_time_min,
        params.liquor_ratio,
        fabric.total_cover_factor,
        fabric.fabric_areal_weight_g_m2,
        params.fabric_is_scoured,
        params.water_hardness_ppm
    )

    fixation_pct = calculate_fixation(
        params.dye_type,
        dye_bath_pH,
        params.dyeing_temperature_C,
        params.fixation_time_min,
        exhaustion_pct,
        params.fabric_is_mercerized
    )

    hydrolysis_pct = calculate_hydrolysis(fixation_pct)

    unfixed_on_fabric = calculate_unfixed_dye_on_fabric(exhaustion_pct, fixation_pct)

    wash_fastness = calculate_wash_fastness(
        fixation_pct,
        params.wash_off_time_min,
        unfixed_on_fabric,
        params.dyeing_temperature_C
    )

    # Light fastness: reactive dyes ~6; slightly reduced by dark shades or
    # incomplete fixation (Mahapatra 13.12: "light fastness with rating about 6")
    light_fastness = 6.0 if fixation_pct >= 70 else max(4.0, 6.0 - (70.0 - fixation_pct) * 0.06)
    light_fastness = round(light_fastness, 1)

    # Rubbing fastness: dry ~4, wet ~3-4 (Mahapatra 13.12: "moderate rubbing fastness")
    rub_dry = round(min(4.5, 3.5 + (fixation_pct - 65.0) * 0.02), 1)
    rub_wet = round(min(4.0, rub_dry - 0.5), 1)

    penetration_quality = assess_dye_penetration_quality(
        fabric.total_cover_factor,
        params.dyeing_temperature_C,
        params.exhaustion_time_min,
        params.liquor_ratio,
        fabric.yarn_diameter_weft_mm
    )

    colour_yield = calculate_colour_yield(
        fixation_pct,
        params.fabric_is_mercerized,
        params.fabric_is_scoured,
        fabric.total_cover_factor,
        penetration_quality
    )

    levelness_risk = assess_levelness_risk(
        params.dye_type,
        params.salt_concentration_g_L,
        params.dyeing_temperature_C,
        exhaustion_pct,
        fabric.total_cover_factor,
        fabric.cloth_defect_risk,
        params.fabric_is_scoured
    )

    fabric_damage_risk = assess_fabric_damage_risk(
        params.alkali_type,
        dye_bath_pH,
        params.dyeing_temperature_C,
        params.fixation_time_min,
        maintenance_ratio
    )

    total_process_time = (params.exhaustion_time_min
                          + params.fixation_time_min
                          + params.wash_off_time_min)

    water_L_per_kg, salt_load, energy_rel, effluent_dye = calculate_sustainability_metrics(
        params.liquor_ratio,
        params.wash_off_time_min,
        params.dyeing_temperature_C,
        fixation_pct,
        params.salt_concentration_g_L,
        fabric.fabric_areal_weight_g_m2
    )

    # ── POST-SIMULATION WARNINGS ──────────────────────────────────────────────

    # Poor fixation warning
    if fixation_pct < 60:
        warnings.append(
            f"Fixation ({fixation_pct}%) is below the minimum acceptable threshold of 60%. "
            "Mahapatra 13.2: 'Only 70% of the dye is fixed onto the fibre' under conventional "
            "conditions. Values below 60% indicate a process error (wrong alkali, temperature, "
            "or time). Wash fastness will be unacceptably poor."
        )

    # High unfixed dye warning
    if unfixed_on_fabric > 20:
        warnings.append(
            f"Unfixed dye on fabric ({unfixed_on_fabric}%) is high. "
            "Mahapatra 13.24: 'With 5 per cent or less unfixed dye to remove, "
            "the washing-off process can be drastically curtailed.' "
            "Current level requires extensive multi-bath hot-wash + soaping to achieve "
            "acceptable wash fastness. Increase fixation or switch to a higher-fixation dye."
        )

    # Low wash fastness warning
    if wash_fastness < 3.5:
        warnings.append(
            f"Predicted wash fastness ({wash_fastness}) is below commercial minimum (3.5). "
            "Reactive dyes should deliver rating 4–5. [Mahapatra 13.12] "
            "Causes: inadequate fixation, insufficient wash-off, or residual unfixed dye. "
            "Review alkali pH, temperature, and wash-off sequence."
        )

    # Surface-only penetration
    if penetration_quality == "surface_only":
        warnings.append(
            "Dye penetration is SURFACE ONLY — the yarn core is undyed. "
            "This results in shade change on abrasion (e.g. pilling exposes pale fibre), "
            "poor rub fastness, and premature shade loss in laundering. "
            "Increase dyeing temperature, exhaustion time, or reduce MLR."
        )

    # Environmental: high salt discharge
    if salt_load > 800:
        warnings.append(
            f"Salt discharge ({salt_load:.0f} g/kg of fabric) is very high. "
            "Mahapatra 13.23: 'Reducing salt consumption… in the effluent' is a key "
            "future trend. High salt discharge increases ecological salinity in receiving "
            "water bodies. Consider low-salt or salt-free reactive dye systems."
        )

    # Very high effluent dye load
    if effluent_dye > 35:
        warnings.append(
            f"Effluent dye load ({effluent_dye}% of applied dye) is very high. "
            "Conventional reactive dyeing discharges 20–40% of applied dye in effluent. "
            "Mahapatra 13.22: 'The demand for Right-First Dyeing is increasing.' "
            "Consider bifunctional or trifunctional dyes with higher fixation."
        )

    return DyedFabricOutput(
        dye_bath_pH=dye_bath_pH,
        exhaustion_pct=exhaustion_pct,
        fixation_pct=fixation_pct,
        hydrolysis_pct=hydrolysis_pct,
        unfixed_dye_on_fabric_pct=unfixed_on_fabric,
        colour_yield_relative=colour_yield,
        wash_fastness_rating=wash_fastness,
        light_fastness_rating=light_fastness,
        rubbing_fastness_dry=max(1.0, rub_dry),
        rubbing_fastness_wet=max(1.0, rub_wet),
        levelness_risk=levelness_risk,
        dye_penetration_quality=penetration_quality,
        water_consumption_L_per_kg=water_L_per_kg,
        salt_load_g_per_kg=salt_load,
        total_process_time_min=total_process_time,
        energy_relative=energy_rel,
        effluent_dye_load_pct=effluent_dye,
        unlevel_dyeing_risk=levelness_risk,
        fabric_damage_risk=fabric_damage_risk,
        warnings=warnings
    )


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE USAGE — scenarios chained directly from plain_weaving.py outputs
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    print("=" * 65)
    print("REACTIVE DYEING SIMULATION — Exhaust Batch Process")
    print("Based on Mahapatra, 'Textile Dyes', Ch. 13, 2016")
    print("Layer 2 sourced directly from plain_weaving.py Layer 4")
    print("=" * 65)

    # ── SCENARIO 1: Medium shade on carded cotton plain cloth ────────────────
    # Input: plain_weaving.py Scenario 1 (Ne 20 carded cotton square cloth).
    # Dye: ME bifunctional reactive dye (Remazol type), 2% owf medium shade.
    # Validation: Mahapatra 13.2: fixation 60-80% conventional;
    #             Mahapatra 13.12: wash fastness 4-5 for reactive dyes.
    print("\n--- SCENARIO 1: 2% owf ME bifunctional reactive dye on "
          "carded cotton (Scenario 1 weave output) ---\n")

    fabric_1 = InputFabric(
        # Direct copy of plain_weaving.py Scenario 1 FabricQualityOutput:
        yarn_diameter_warp_mm=0.205,
        yarn_diameter_weft_mm=0.205,
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

    params_1 = ReactiveDyeingParams(
        dye_type="ME",
        dye_concentration_owf_pct=2.0,    # medium shade
        salt_concentration_g_L=50.0,       # appropriate for medium shade
        alkali_type="Na2CO3",
        alkali_concentration_g_L=15.0,
        dyeing_temperature_C=60.0,         # standard ME dye temperature [Mahapatra 13.4]
        exhaustion_time_min=40.0,
        fixation_time_min=45.0,
        wash_off_time_min=40.0,
        liquor_ratio=10.0,                 # jet machine
        machine_type="jet",
        water_hardness_ppm=80.0,
        fabric_is_mercerized=False,
        fabric_is_scoured=True,
        ambient_temperature_C=24.0,
        maintenance_interval_hours=2_000.0,
        operating_hours_since_maintenance=700.0
    )

    r1 = simulate_reactive_dyeing(fabric_1, params_1)

    print(f"  Dye bath pH:             {r1.dye_bath_pH}")
    print(f"  Exhaustion:              {r1.exhaustion_pct}%")
    print(f"  Fixation:                {r1.fixation_pct}%  "
          f"(Mahapatra ref: 60–80% conventional; ME bifunctional ~82%)")
    print(f"  Hydrolysis:              {r1.hydrolysis_pct}%")
    print(f"  Unfixed dye on fabric:   {r1.unfixed_dye_on_fabric_pct}%")
    print(f"  Colour yield:            {r1.colour_yield_relative:.3f}")
    print(f"  Dye penetration:         {r1.dye_penetration_quality}")
    print(f"  Wash fastness:           {r1.wash_fastness_rating}/5  "
          f"(Mahapatra ref: 4–5)")
    print(f"  Light fastness:          {r1.light_fastness_rating}/8  "
          f"(Mahapatra ref: ~6)")
    print(f"  Rub fastness dry/wet:    {r1.rubbing_fastness_dry}/{r1.rubbing_fastness_wet}")
    print(f"  Levelness risk:          {r1.levelness_risk.upper()}")
    print(f"  Fabric damage risk:      {r1.fabric_damage_risk.upper()}")
    print(f"  Water consumption:       {r1.water_consumption_L_per_kg} L/kg  "
          f"(Mahapatra conventional ref: 40.5 L/kg)")
    print(f"  Salt discharge:          {r1.salt_load_g_per_kg} g/kg")
    print(f"  Energy (relative):       {r1.energy_relative}× conventional")
    print(f"  Effluent dye load:       {r1.effluent_dye_load_pct}%")
    print(f"  Total process time:      {r1.total_process_time_min:.0f} min")
    if r1.warnings:
        print(f"\n  WARNINGS:")
        for w in r1.warnings:
            print(f"    ⚠ {w}")
    else:
        print("\n  No warnings — all parameters within recommended ranges.")

    # ── SCENARIO 2: Dark shade on mercerised PES/CO poplin ───────────────────
    # Input: plain_weaving.py Scenario 2 (Ne 30 PES/CO poplin).
    # Dye: Bifunctional/trifunctional dye (Avitera SE), 5% owf dark shade.
    # Expected: high fixation (~90%), low water and effluent load.
    print("\n--- SCENARIO 2: 5% owf trifunctional dye (Avitera SE) "
          "on mercerised PES/CO poplin ---\n")

    fabric_2 = InputFabric(
        yarn_diameter_warp_mm=0.165,
        yarn_diameter_weft_mm=0.191,
        warp_cover_factor=0.793,
        weft_cover_factor=0.420,
        total_cover_factor=0.880,
        warp_crimp_pct=12.8,
        weft_crimp_pct=2.4,
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

    params_2 = ReactiveDyeingParams(
        dye_type="bifunctional_trifunctional",  # Avitera SE [Mahapatra 13.24]
        dye_concentration_owf_pct=5.0,           # dark shade
        salt_concentration_g_L=65.0,             # high salt for dark shade
        alkali_type="Na2CO3",
        alkali_concentration_g_L=18.0,
        dyeing_temperature_C=60.0,               # Avitera SE: ≤60°C [Mahapatra 13.24]
        exhaustion_time_min=45.0,
        fixation_time_min=50.0,
        wash_off_time_min=25.0,                  # shorter wash-off for high-fix dye
        liquor_ratio=8.0,                        # low MLR soft-flow machine
        machine_type="soft_flow",
        water_hardness_ppm=40.0,                 # softened water
        fabric_is_mercerized=True,               # mercerised fabric [Mahapatra 13.1]
        fabric_is_scoured=True,
        ambient_temperature_C=22.0,
        maintenance_interval_hours=3_000.0,
        operating_hours_since_maintenance=250.0
    )

    r2 = simulate_reactive_dyeing(fabric_2, params_2)

    print(f"  Dye bath pH:             {r2.dye_bath_pH}")
    print(f"  Exhaustion:              {r2.exhaustion_pct}%")
    print(f"  Fixation:                {r2.fixation_pct}%  "
          f"(Mahapatra Avitera SE ref: ~90%)")
    print(f"  Hydrolysis:              {r2.hydrolysis_pct}%")
    print(f"  Unfixed dye on fabric:   {r2.unfixed_dye_on_fabric_pct}%  "
          f"(Mahapatra Avitera ref: ≤5%)")
    print(f"  Colour yield:            {r2.colour_yield_relative:.3f}")
    print(f"  Dye penetration:         {r2.dye_penetration_quality}")
    print(f"  Wash fastness:           {r2.wash_fastness_rating}/5")
    print(f"  Light fastness:          {r2.light_fastness_rating}/8")
    print(f"  Levelness risk:          {r2.levelness_risk.upper()}")
    print(f"  Fabric damage risk:      {r2.fabric_damage_risk.upper()}")
    print(f"  Water consumption:       {r2.water_consumption_L_per_kg} L/kg  "
          f"(Mahapatra Avitera ref: 15.2 L/kg)")
    print(f"  Salt discharge:          {r2.salt_load_g_per_kg} g/kg")
    print(f"  Energy (relative):       {r2.energy_relative}× conventional")
    print(f"  Effluent dye load:       {r2.effluent_dye_load_pct}%")
    print(f"  Total process time:      {r2.total_process_time_min:.0f} min")
    if r2.warnings:
        print(f"\n  WARNINGS:")
        for w in r2.warnings:
            print(f"    ⚠ {w}")
    else:
        print("\n  No warnings — all parameters within recommended ranges.")

    # ── SCENARIO 3: Stress test — wrong settings, upstream defects ───────────
    # Input: plain_weaving.py Scenario 3 (coarse weft-faced cloth, high defect risk).
    # Dye: H-brand (MCT) at wrong (too low) temperature, no scouring, hard water.
    print("\n--- SCENARIO 3: H-brand MCT dye on coarse weft-faced cloth "
          "— wrong temperature, unsoured, hard water (stress test) ---\n")

    fabric_3 = InputFabric(
        yarn_diameter_warp_mm=0.324,
        yarn_diameter_weft_mm=0.370,
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

    params_3 = ReactiveDyeingParams(
        dye_type="H_brand",                # MCT hot-brand dye
        dye_concentration_owf_pct=4.0,
        salt_concentration_g_L=45.0,       # insufficient for dark shade
        alkali_type="Na2CO3",
        alkali_concentration_g_L=15.0,
        dyeing_temperature_C=55.0,         # WRONG: H-brand requires 80–95°C
        exhaustion_time_min=20.0,          # too short
        fixation_time_min=25.0,            # too short
        wash_off_time_min=15.0,            # inadequate
        liquor_ratio=25.0,                 # high MLR winch
        machine_type="winch",
        water_hardness_ppm=280.0,          # hard water
        fabric_is_mercerized=False,
        fabric_is_scoured=False,           # NOT scoured — major issue
        ambient_temperature_C=27.0,
        maintenance_interval_hours=1_200.0,
        operating_hours_since_maintenance=1_180.0  # nearly overdue
    )

    r3 = simulate_reactive_dyeing(fabric_3, params_3)

    print(f"  Dye bath pH:             {r3.dye_bath_pH}")
    print(f"  Exhaustion:              {r3.exhaustion_pct}%")
    print(f"  Fixation:                {r3.fixation_pct}%")
    print(f"  Hydrolysis:              {r3.hydrolysis_pct}%")
    print(f"  Unfixed dye on fabric:   {r3.unfixed_dye_on_fabric_pct}%")
    print(f"  Colour yield:            {r3.colour_yield_relative:.3f}")
    print(f"  Dye penetration:         {r3.dye_penetration_quality}")
    print(f"  Wash fastness:           {r3.wash_fastness_rating}/5")
    print(f"  Light fastness:          {r3.light_fastness_rating}/8")
    print(f"  Levelness risk:          {r3.levelness_risk.upper()}")
    print(f"  Fabric damage risk:      {r3.fabric_damage_risk.upper()}")
    print(f"  Water consumption:       {r3.water_consumption_L_per_kg} L/kg")
    print(f"  Salt discharge:          {r3.salt_load_g_per_kg} g/kg")
    print(f"  Energy (relative):       {r3.energy_relative}× conventional")
    print(f"  Effluent dye load:       {r3.effluent_dye_load_pct}%")
    print(f"  Total process time:      {r3.total_process_time_min:.0f} min")
    if r3.warnings:
        print(f"\n  WARNINGS:")
        for w in r3.warnings:
            print(f"    ⚠ {w}")

    print("\n" + "=" * 65)
    print("Simulation complete.")
    print("=" * 65)
