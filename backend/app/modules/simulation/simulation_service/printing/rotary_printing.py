"""
Rotary Screen Printing Simulation Module
Process: Printing > Rotary Screen Printing

Layer 1 — Machine Identity
    Type            : Rotary Screen Printing Machine
    Subprocess      : Rotary Screen Printing
    Technology      : Continuous rotation of seamless cylindrical nickel screens
                      (electroformed lacquer or galvano type) while in contact
                      with the fabric. Print paste is pumped into the inside of
                      the rotating screen and forced out through open design areas
                      by a stationary squeegee (flexible stainless-steel blade,
                      magnetic rod, or Stork Airflow system). Fabric is held by
                      thermoplastic adhesive on an endless driven blanket. All
                      screens rotate simultaneously, enabling continuous, fully
                      uninterrupted fabric movement at high speed.
    Machine makers  : Stork (Netherlands), Johannes Zimmer (Austria), Reggiani
                      (Italy), MBK (Germany).
    Speed range     : Typically 30–70 m/min (1 800–4 200 m/h) depending on
                      design, fabric and dryer capacity. Miles Ch. 2.4: 'it is
                      quite possible to run the machine faster than this, the
                      limitations often being the length and efficiency of the
                      cloth and blanket dryers.'
    Screen types    : Lacquer (electroformed nickel, hexagonal holes, wall
                      0.08–0.10 mm, open area 9–13% inside measure, max 100 mesh
                      = 40 threads/cm); Galvano (solid nickel walls, stronger,
                      wall 0.35–0.40 mm for carpets, max 80 mesh reliably).
                      Stork PentaScreens (125–255 mesh, open area 7–16%) and
                      NovaScreens (135–195 mesh, open area 18–24%) for finer
                      definition.
    Squeegee types  : Flexible stainless-steel blade; magnetic rod (Zimmer —
                      rod + screen both move → higher paste volume than blade);
                      Stork Airflow (air-sack pressed blade → uniform pressure
                      across width). Magnetic rod gives higher minimum paste
                      volume than blade (Miles Ch. 2.4.1).
    Circumferences  : Standard: 640 mm. Others: 518, 537, 668, 688, 725, 801,
                      819, 914, 1018 mm (Miles Ch. 2.4.4). Full design repeat
                      must equal screen circumference or a whole-number fraction.
    Screen drive    : Both ends driven to avoid twisting and buckling. Short
                      blanket (screens close together) improves registration
                      vs flat-screen machines. Independent speed control per
                      screen (Stork/Zimmer) eliminates drag-induced misfit.
    Colorant scope  : Pigment (>50% of all textile prints), reactive dyes on
                      cellulosics, disperse dyes on polyester, acid dyes on
                      nylon/wool, vat dyes, azoic colorants, discharge pastes.

All parameter relationships derived from:
    Miles, L.W.C. (Ed.), "Textile Printing", Revised 2nd Edition, Society of
    Dyers and Colourists, Bradford, 2003.
    Chapters 1 (Engraved Roller), 2 (Screen Printing, especially 2.4 Rotary),
    7 (Print Paste Properties and Rheology), 8 (Fixation and Aftertreatment).

Layer 5: Interdependency and behaviour simulation functions.
These functions take the dyed fabric input (Layer 2) and machine / paste
operational parameters (Layer 3), and predict printed fabric quality metrics
(Layer 4).

Layer 2 note:
    Printing input = Colouring (dyeing) output.
    The InputDyedFabric dataclass mirrors DyedFabricOutput from the reactive
    dyeing simulation (and analogous dyeing subprocess modules), using the
    fields that are physically meaningful at the printing stage.

        dyeing.DyedFabricOutput          →  rotary_printing.InputDyedFabric
        ─────────────────────────────────────────────────────────────────────
        dye_bath_pH                      →  substrate_pH
        exhaustion_pct                   →  dye_exhaustion_pct
        fixation_pct                     →  dye_fixation_pct
        hydrolysis_pct                   →  unfixed_hydrolysed_dye_pct
        unfixed_dye_on_fabric_pct        →  residual_unfixed_dye_pct
        colour_yield_relative            →  ground_colour_yield
        wash_fastness_rating             →  ground_wash_fastness
        light_fastness_rating            →  ground_light_fastness
        levelness_risk                   →  ground_levelness_risk
        dye_penetration_quality          →  ground_dye_penetration
        water_consumption_L_per_kg       →  upstream_water_L_per_kg
        salt_load_g_per_kg               →  upstream_salt_g_per_kg
        fabric_damage_risk               →  substrate_damage_risk

    Additional fields carried through from spinning/weaving/dyeing:
        fiber_type, fabric_weight_g_per_m2, fabric_cover_factor,
        fabric_width_cm, fabric_surface_texture
"""

import math
from dataclasses import dataclass


# ─────────────────────────────────────────────────────────────────────────────
# DATA CLASSES — Layers 2, 3, and 4
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class InputDyedFabric:
    """
    Layer 2 — Input dyed fabric properties for Rotary Screen Printing.

    Mirrors DyedFabricOutput from the reactive dyeing subprocess (and
    analogous colouring subprocesses). Field mapping documented in module
    docstring above.
    """
    # ── SUBSTRATE IDENTITY ─────────────────────────────────────────────────
    fiber_type: str                     # "cotton", "polyester", "nylon",
                                        # "blend_PES_CO", "viscose", "wool",
                                        # "silk", "acrylic"
    fabric_weight_g_per_m2: float       # Fabric weight in g/m². Heavier
                                        # fabrics absorb more paste; require
                                        # longer steamer dwell.
    fabric_cover_factor: float          # Combined warp+weft cover factor (0–2).
                                        # Dense fabrics restrict paste penetration;
                                        # also affect blanket adhesion.
    fabric_width_cm: float              # Fabric width in cm. Must not exceed
                                        # screen (knitting) width.
    fabric_surface_texture: str         # "smooth", "textured", or "pile".
                                        # Pile fabrics absorb far more paste and
                                        # require coarser screens and higher
                                        # squeegee pressure (Miles Ch. 2.8.3).

    # ── DYE BATH / DYEING EQUILIBRIUM (from dyeing Layer 4) ───────────────
    substrate_pH: float                 # Fabric pH after dyeing and washing.
                                        # Residual alkali interferes with
                                        # discharge printing; acid conditions
                                        # accelerate binder crosslinking.
    dye_exhaustion_pct: float           # % of dye taken up by fabric in dyeing.
    dye_fixation_pct: float             # % of dye covalently / permanently fixed.
    unfixed_hydrolysed_dye_pct: float   # % hydrolysed reactive dye remaining —
                                        # reduces discharge crispness (Miles Ch. 6.2).
    residual_unfixed_dye_pct: float     # % of physically adsorbed unfixed dye —
                                        # bleeds into white areas during steaming
                                        # (Miles Ch. 8.5.3).

    # ── SHADE AND FASTNESS (from dyeing Layer 4) ──────────────────────────
    ground_colour_yield: float          # Relative ground colour yield (0–1).
    ground_wash_fastness: float         # ISO wash fastness of dyed ground (1–5).
    ground_light_fastness: float        # ISO light fastness of dyed ground (1–8).
    ground_levelness_risk: str          # "low" / "medium" / "high".
    ground_dye_penetration: str         # "full" / "partial" / "surface_only".

    # ── SUSTAINABILITY METRICS (from dyeing Layer 4) ──────────────────────
    upstream_water_L_per_kg: float      # Water used in dyeing stage (L/kg).
    upstream_salt_g_per_kg: float       # Salt discharged in dyeing (g/kg).

    # ── RISK FLAGS (from dyeing Layer 4) ──────────────────────────────────
    substrate_damage_risk: str          # "low" / "medium" / "high".
                                        # High damage → fabric tears at blanket
                                        # adhesive (Miles Ch. 2.3.1).


@dataclass
class RotaryPrintingOperationalParams:
    """
    Layer 3 — Operational parameters for Rotary Screen Printing.

    Source: Miles, Textile Printing, Ch. 1, 2, 7, 8.
    """
    # ── MACHINE SPEED AND WIDTH ───────────────────────────────────────────
    printing_speed_m_per_hour: float    # Fabric speed in m/h.
                                        # Typical: 1800–4200 m/h (30–70 m/min).
                                        # Miles Ch. 2.4: limitations from dryer
                                        # length and efficiency.
    screen_working_width_cm: float      # Active screen printing width in cm.
                                        # Fabric width must be ≤ this value.
    number_of_screens: int              # One screen per colour (Miles Ch. 2.4).
                                        # Rotary: up to 20+ screens possible.

    # ── SCREEN SPECIFICATION ──────────────────────────────────────────────
    screen_type: str                    # "lacquer_rotary" or "galvano_rotary"
                                        # or "penta_screen" or "nova_screen".
    screen_mesh_holes_per_inch: int     # Mesh count (holes per linear inch).
                                        # Lacquer/galvano: standard 60 (blotch)
                                        # or 80 (outlines/synthetics). Miles Ch. 2.7.3.
                                        # PentaScreen: 125–255 mesh.
                                        # NovaScreen: 135–195 mesh.
    screen_open_area_pct: float         # % open area (inside measure for rotary).
                                        # Lacquer 60-mesh: ~11%; 80-mesh: ~11%;
                                        # NovaScreen 135: 24%; PentaScreen 125: 15%.
                                        # Miles Table 2.2 and Ch. 2.7.3.
    screen_wall_thickness_mm: float     # Nickel wall thickness in mm.
                                        # Lacquer textile: 0.08–0.10 mm.
                                        # Galvano textile: 0.10–0.15 mm.
                                        # Galvano carpet: 0.35–0.40 mm.
    screen_circumference_mm: float      # Screen circumference in mm.
                                        # Standard: 640 mm. Others: 518, 537,
                                        # 668, 688, 725, 801, 819, 914, 1018 mm.
                                        # Miles Ch. 2.4.4.
    design_repeat_length_cm: float      # Length of one full design repeat in cm.
                                        # Must be screen_circumference/N where N
                                        # is a positive integer (whole fit rule).
                                        # Miles Ch. 2.5.4.

    # ── SQUEEGEE SPECIFICATION ────────────────────────────────────────────
    squeegee_type: str                  # "steel_blade": standard for most fabrics.
                                        # "magnetic_rod": higher paste volume;
                                        #   both surfaces moving → more pressure.
                                        # "airflow_rod": air sack → uniform pressure.
                                        # Miles Ch. 2.4.1.
    squeegee_blade_length_mm: float     # Effective blade length in mm. Should
                                        # span full fabric width.
    squeegee_pressure_setting: str      # "low", "medium", "high".
                                        # Controls paste volume applied; higher
                                        # pressure → more paste through open pores.
    squeegee_blade_curvature: str       # "shallow" (small angle, high pressure
                                        #   wedge), "standard", or "steep"
                                        #   (large angle, low paste volume).

    # ── BLANKET AND DRIVE ─────────────────────────────────────────────────
    blanket_type: str                   # "neoprene_rubber", "laminated_neoprene",
                                        # or "low_extensibility_synthetic".
                                        # Low extensibility required for rotary to
                                        # avoid sideways slip (Miles Ch. 2.4.3).
    adhesive_type: str                  # "thermoplastic" (heated plate, most common
                                        # on rotary), "water_based", "semi_permanent".
                                        # Miles Ch. 2.4: 'provision for thermoplastic
                                        # adhesive is common on rotary machines.'
    independent_screen_speed_control: bool  # True if each screen has independent
                                        # motor drive (Stork/Zimmer). Compensates
                                        # for fabric drag and eliminates drag-
                                        # induced pattern misfit (Miles Ch. 2.4.3).
    laser_registration: bool            # True if laser-based screen alignment
                                        # system (MBK laser) is fitted.
                                        # Eliminates manual registration waste
                                        # (Miles Ch. 2.4.2).

    # ── PASTE SUPPLY ──────────────────────────────────────────────────────
    paste_pump_type: str                # "peristaltic", "gear", or "screw".
                                        # Paste is pumped into screen from side
                                        # container through flexible pipe (Ch. 2.4).
    level_control_type: str             # "sensor_automatic" or "manual".
                                        # Sensor actuates pump when paste level
                                        # falls below preset height (Ch. 2.4).
    paste_distribution_quality: str     # "uniform" or "variable".
                                        # Holes in internal pipe larger at far end
                                        # to compensate pump-head drop (Ch. 2.4).

    # ── PRINT PASTE FORMULATION ───────────────────────────────────────────
    colorant_type: str                  # "pigment", "reactive_dye",
                                        # "disperse_dye", "acid_dye", "vat_dye",
                                        # "azoic", or "discharge".
    paste_colorant_conc_g_per_kg: float # Colorant in g/kg paste.
    thickener_type: str                 # "alginate": required for reactive dyes;
                                        # "starch_ether": high colour yield;
                                        # "guar_locust_bean": natural gum;
                                        # "emulsion_o_in_w": no stiff film;
                                        # "synthetic_polyacrylic": 1% use, high
                                        #   shear-thinning, best for rotary at
                                        #   high speed (Miles Ch. 7.6, 7.7.3);
                                        # "crystal_gum": sharp marks;
                                        # "half_emulsion".
    thickener_concentration_pct: float  # % thickener stock in paste.
    paste_viscosity_Pa_s: float         # Viscosity at working shear (Pa·s).
                                        # Pseudoplastic (shear-thinning) is
                                        # essential for screen printing (Ch. 7.7.3).
                                        # At rotary squeegee shear: 0.1–2.0 Pa·s.
                                        # At rest (below yield value): higher.
    paste_yield_value: str              # "short_flow" (yield value present) or
                                        # "long_flow" (Newtonian/near-Newtonian).
                                        # Short flow → sharper marks (Ch. 7.7.3).
                                        # Long flow → better blotch levelling.
    binder_concentration_pct: float     # % binder in paste (pigment prints).
                                        # Minimum 7% (Miles Recipe 5.1). 0.0 for
                                        # dye-based pastes.
    urea_concentration_g_per_kg: float  # Urea (g/kg paste).
                                        # Reactive/HT steam: 100–200 g/kg (Ch. 8.3.6).
                                        # Disperse/polyester: 0–50 g/kg (Ch. 5.4.3).
    alkali_type: str                    # "sodium_bicarbonate", "sodium_carbonate",
                                        # "caustic_soda", "ammonium_sulphate",
                                        # "none", or "diammonium_phosphate".
    alkali_concentration_g_per_kg: float  # Alkali in g/kg paste.
    design_coverage_pct: float          # % of fabric area printed. High coverage
                                        # (blotch) demands dryer efficiency.
                                        # Miles Ch. 2.4: dryer must handle
                                        # continuous high-paste output.

    # ── FIXATION PARAMETERS ───────────────────────────────────────────────
    fixation_method: str                # "baking_hot_air": pigment (140–160°C).
                                        # "saturated_steam": reactive at 100°C,
                                        #   10 min; festoon steamer capacity
                                        #   800 m at 80 m/min (Ch. 8.3.2).
                                        # "high_temp_steam": reactive 150°C 1 min,
                                        #   disperse 180°C 1 min (Ch. 8.3.6).
                                        # "pressure_steam": disperse 120°C 30 min.
                                        # "none_pigment_curing".
    fixation_temperature_C: float       # Fixation temperature in °C.
    fixation_time_min: float            # Fixation duration in minutes.
    steamer_type: str                   # "festoon" (most common for rotary,
                                        #   800 m capacity, 80 m/min),
                                        # "roller_ager" (compact, ≤120 m/min),
                                        # "star_batch" (batch, 500 m), or
                                        # "roller_baker" (pigment baking oven).
    dryer_capacity: str                 # "high", "adequate", or "low".
                                        # The primary production-rate limiter at
                                        # high speed or high coverage (Ch. 2.4).

    # ── WASH-OFF ──────────────────────────────────────────────────────────
    wash_off_applied: bool              # True for dye prints; False for pigment.
    wash_off_temperature_C: float       # Wash-off temperature in °C.
                                        # 90°C clears reactive in 90 s vs >4 min
                                        # at 60°C (Miles Fig. 8.12, Table 8.2).
    wash_off_stages: int                # Number of wash boxes (standard 8-box range
                                        # at 30 m/min gives 120 s hot dwell,
                                        # Miles Table 8.2).
    counterflow_washing: bool           # True if counterflow principle used.
                                        # Maximises removal efficiency per litre
                                        # of water used (Miles Ch. 8.6, Eqn 8.2).

    # ── AMBIENT AND MAINTENANCE ───────────────────────────────────────────
    ambient_temperature_C: float        # Room temperature in °C.
    ambient_humidity_pct: float         # Relative humidity in %. Critical for
                                        # paste stability in open rotary screens.
    last_maintenance_date: str          # ISO date string e.g. "2025-10-01".
    maintenance_interval_hours: float   # Machine service interval in hours.
                                        # Rotary machines are expensive; minimum
                                        # downtime is critical (Miles Ch. 2.4.5).
    operating_hours_since_maintenance: float  # Hours since last full service.


@dataclass
class RotaryPrintedFabricOutput:
    """
    Layer 4 — Predicted output quality metrics for Rotary Screen Printing.
    """
    # ── PASTE APPLICATION METRICS ─────────────────────────────────────────
    paste_volume_applied_g_per_m2: float    # Estimated paste volume applied (g/m²
                                            # of printed area). Rotary applies ~15 g/m²
                                            # on paper (Miles Table 2.3); more on fabric.
    paste_penetration_depth: str            # "full", "partial", or "surface_only".
    colour_yield_pct: float                 # % of theoretical maximum colour yield.

    # ── PRINT DEFINITION ─────────────────────────────────────────────────
    sharpness_of_mark: str                  # "excellent", "good", "acceptable", "poor".
    saw_tooth_risk: str                     # "negligible", "minor", "significant".
                                            # Boundary serration from screen mesh
                                            # array (Miles Ch. 2.7.2).
    registration_accuracy: str             # "excellent", "good", or "poor".
                                            # Rotary: driven screens, short blanket,
                                            # laser alignment → excellent potential.

    # ── ROTARY-SPECIFIC PRINT FAULTS ─────────────────────────────────────
    stripe_fault_risk: str                  # "low", "medium", "high".
                                            # Longitudinal stripe from uneven blade
                                            # pressure across width (Miles Ch. 2.4.1).
    colour_crushing_risk: str              # "low", "medium", "high".
                                            # Subsequent screen compressing wet colour.
    paste_level_instability_risk: str       # "low", "medium", "high".
                                            # Fluctuating paste level inside screen
                                            # → variable colour depth (Ch. 2.4).
    screen_creasing_risk: str               # "low", "medium", "high".
                                            # Thin-walled lacquer screens (0.08 mm)
                                            # can crease under excessive tension or
                                            # incorrect end-ring fitting (Ch. 2.4.2).
    repeat_fitting_quality: str             # "excellent", "good", or "poor".
                                            # Relates to whole-number fit of repeat
                                            # into screen circumference (Ch. 2.5.4).

    # ── FASTNESS METRICS ─────────────────────────────────────────────────
    print_wash_fastness: float              # ISO wash fastness (1–5).
    print_light_fastness: float             # ISO light fastness (1–8).
    print_rub_fastness_dry: float           # ISO dry rubbing fastness (1–5).
    print_rub_fastness_wet: float           # ISO wet rubbing fastness (1–5).
    colour_yield_relative: float            # Relative colour yield (0–1).

    # ── FIXATION QUALITY ─────────────────────────────────────────────────
    estimated_fixation_pct: float           # % of applied colorant fixed.
    unfixed_dye_staining_risk: str          # "low", "medium", "high".
    binder_crosslink_quality: str           # "good", "adequate", "poor" (pigment).

    # ── SUSTAINABILITY METRICS ────────────────────────────────────────────
    total_water_L_per_kg: float             # Dyeing + printing wash-off water (L/kg).
    total_effluent_dye_load_pct: float      # % of applied colorant discharged.
    energy_index: float                     # Relative energy (1.0 = conventional).

    # ── PRODUCTION METRICS ────────────────────────────────────────────────
    effective_production_m_per_hour: float  # Actual throughput m/h.
    machine_efficiency_pct: float           # % uptime including all downtime causes.

    warnings: list                          # Out-of-range parameter warnings.


# ─────────────────────────────────────────────────────────────────────────────
# CORE SIMULATION FUNCTIONS — Layer 5
# Each function models one specific cause-effect relationship from the manual.
# ─────────────────────────────────────────────────────────────────────────────

def predict_paste_volume_applied(
    screen_open_area_pct: float,
    screen_mesh_holes_per_inch: int,
    squeegee_type: str,
    squeegee_pressure_setting: str,
    squeegee_blade_curvature: str,
    fabric_surface_texture: str,
    fabric_weight_g_per_m2: float,
    paste_viscosity_Pa_s: float,
    printing_speed_m_per_hour: float
) -> float:
    """
    Predicts print paste volume applied in g/m² of printed area.

    Source: Miles, Textile Printing, Ch. 2.8.2 (Flow through screen pores:
    Poiseuille equation Q ∝ r³ or r²), Ch. 2.8.3 (Uptake of paste by fabric),
    Ch. 2.4.1 (Squeegee systems), Ch. 7.7.5 (Paste flow in screen printing).

    Key relationships:
    - Q ∝ pore_radius³ (Poiseuille; Miles Eqn 2.1). Pore radius ∝ 1/mesh.
      Halving the mesh count (coarser screen) roughly octuple the paste volume.
    - Screen open area has a direct proportional effect (Ch. 2.8.2): more
      open area → more paste.
    - Magnetic rod squeegee: both surfaces moving → higher minimum paste than
      stationary blade (Miles Ch. 2.4.1, Ferber & Hilden reference p. 33).
    - Squeegee blade curvature / angle: shallower angle → higher hydrodynamic
      pressure wedge → more paste; reducing squeegee angle increases volume
      by up to 5× (Miles Ch. 7.7.5, Dowds' equation V = K·B^0.4·cos A).
    - Higher printing speed → shorter dwell time under squeegee → less paste
      transferred (Ch. 7.7.5 regression analysis).
    - Viscosity effect: hydrodynamic pressure ∝ η in the wedge term but
      also opposes flow through pores; net effect approximately neutral for
      shear-thinning pastes (Miles Ch. 2.8.2).
    - Pile fabrics absorb substantially more paste than smooth (Ch. 2.8.3).
    - Rotary reference: ~15 g/m² on smooth paper (Miles Table 2.3); on fabric
      typically 25–120 g/m² depending on fabric type and mesh.
    """
    # --- Pore radius contribution (Poiseuille) ---
    # Pore radius ∝ 1 / mesh; reference at 60 mesh, 11% open area → 40 g/m²
    mesh_factor = (60.0 / max(1, screen_mesh_holes_per_inch)) ** 1.5  # Q ∝ r²–r³

    # Open area: direct proportional effect (Ch. 2.8.2)
    open_area_factor = screen_open_area_pct / 11.0  # normalised to 60-mesh lacquer

    base_volume = 40.0 * mesh_factor * open_area_factor

    # --- Squeegee type factor (Ch. 2.4.1) ---
    squeegee_factors = {
        "magnetic_rod": 1.40,    # both surfaces moving → highest paste volume
        "airflow_rod":  1.20,    # air-sack uniform pressure; more than standard blade
        "steel_blade":  1.00,    # stationary blade reference
    }
    sq_factor = squeegee_factors.get(squeegee_type.lower(), 1.00)

    # --- Squeegee pressure factor ---
    pressure_factors = {"low": 0.80, "medium": 1.00, "high": 1.25}
    p_factor = pressure_factors.get(squeegee_pressure_setting.lower(), 1.00)

    # --- Blade curvature / angle factor (Dowds' cosA term, Miles Ch. 7.7.5) ---
    curvature_factors = {
        "shallow": 1.30,   # small angle → large hydrodynamic pressure wedge
        "standard": 1.00,
        "steep":    0.78,  # large angle → less paste
    }
    c_factor = curvature_factors.get(squeegee_blade_curvature.lower(), 1.00)

    # --- Speed factor: higher speed → less dwell → less paste (Ch. 7.7.5) ---
    # Reference speed 2400 m/h (40 m/min). Volume ∝ (speed)^-0.3 empirically.
    speed_factor = (2400.0 / max(600.0, printing_speed_m_per_hour)) ** 0.3

    # --- Fabric texture absorption factor (Ch. 2.8.3) ---
    texture_factors = {
        "smooth": 1.00,
        "textured": 1.45,
        "pile": 2.20,     # pile absorbs very large paste volumes
    }
    t_factor = texture_factors.get(fabric_surface_texture.lower(), 1.00)

    # --- Fabric weight factor ---
    w_factor = (fabric_weight_g_per_m2 / 150.0) ** 0.35

    volume = (base_volume * sq_factor * p_factor * c_factor
              * speed_factor * t_factor * w_factor)
    return round(max(8.0, min(500.0, volume)), 1)


def predict_paste_penetration(
    paste_volume_g_per_m2: float,
    paste_viscosity_Pa_s: float,
    paste_yield_value: str,
    fabric_cover_factor: float,
    fabric_surface_texture: str,
    printing_speed_m_per_hour: float
) -> str:
    """
    Predicts paste penetration depth through fabric.

    Source: Miles, Textile Printing, Ch. 2.8.3 (Uptake of paste by fabric).
    'Penetration occurs through the thickness of the fabric, mainly due to the
    pressure and kinetic energy with which the paste leaves the pores, but
    sideways spread due to surface tension forces is restricted by the higher
    viscosity of pseudoplastic pastes under low shear conditions.' (Ch. 2.8.3)

    Washburn equation: penetration distance ∝ √(r·γ·t/η).
    At 60 m/min and 5 mm pressure zone: time ≈ 5 ms; paste of 0.1 Pa·s moves
    0.12 mm into 15 µm capillaries (Miles Ch. 7.7.5 worked example).

    Short-flow pastes (yield value present): resist capillary spread → reduced
    penetration but sharper marks (Ch. 7.7.3).
    Dense fabrics: fewer or smaller inter-fibre capillaries → less penetration.
    High speed: shorter contact time → less penetration.
    """
    # Penetration index (higher = deeper)
    # Volume / viscosity gives penetration driving force; limited by fabric density
    penetration_index = (paste_volume_g_per_m2 / max(0.1, paste_viscosity_Pa_s)) \
                        / max(0.5, fabric_cover_factor)

    # Speed: at high speed contact time is shorter → less penetration
    # Reference 2400 m/h; each 1000 m/h above reduces penetration
    speed_penalty = max(0.5, 1.0 - (printing_speed_m_per_hour - 2400) / 15000)
    penetration_index *= speed_penalty

    # Short-flow yield-value pastes: restrict capillary spread (Ch. 7.7.3)
    if paste_yield_value == "short_flow":
        penetration_index *= 0.65

    # Pile fabric: paste absorbed into pile, limited base penetration
    if fabric_surface_texture == "pile":
        penetration_index *= 0.40
    elif fabric_surface_texture == "textured":
        penetration_index *= 0.75

    if penetration_index >= 30.0:
        return "full"
    elif penetration_index >= 10.0:
        return "partial"
    else:
        return "surface_only"


def predict_sharpness_of_mark(
    paste_viscosity_Pa_s: float,
    paste_yield_value: str,
    screen_mesh_holes_per_inch: int,
    thickener_type: str,
    fabric_surface_texture: str,
    printing_speed_m_per_hour: float,
    design_coverage_pct: float
) -> str:
    """
    Predicts sharpness of the printed mark (edge definition).

    Source: Miles, Textile Printing, Ch. 7.7.5, Ch. 2.7.2.
    'Sharpness of the printed mark is improved by printing at high speed.
    This is clearly because less paste is transferred in the shorter contact
    time.' (Ch. 7.7.5)
    Higher speed also reduces lateral capillary spread time.
    Short-flow (yield-value) pastes resist capillary spread under low shear
    after squeegee → sharper marks (Ch. 7.7.3).
    Synthetic polyacrylic thickeners: very high shear-thinning → flows easily
    under squeegee, then gels immediately → sharp marks (Ch. 7.6).
    Fine mesh screens allow lower paste volume and finer outlines (Ch. 2.7.2).
    Smooth fabrics give sharper outlines than pile or textured (Ch. 2.8.3).
    Blotch (high coverage) designs: paste spreading at boundary reduces
    sharpness compared to fine isolated motifs.
    """
    score = 0

    # Paste viscosity and flow character
    if paste_viscosity_Pa_s >= 1.5:
        score += 2
    elif paste_viscosity_Pa_s >= 0.8:
        score += 1

    if paste_yield_value == "short_flow":
        score += 3  # strong resistance to spread after squeegee

    # Screen mesh: finer → smaller pores → less paste spread (Ch. 2.7.2)
    if screen_mesh_holes_per_inch >= 125:     # PentaScreen / NovaScreen
        score += 4
    elif screen_mesh_holes_per_inch >= 80:
        score += 3
    elif screen_mesh_holes_per_inch >= 60:
        score += 2
    else:
        score += 1  # coarse mesh → significant saw-tooth and spread

    # Thickener type (Ch. 7.6, 7.7.3)
    sharp_thickeners = {"synthetic_polyacrylic", "crystal_gum", "half_emulsion",
                        "emulsion_o_in_w"}
    if thickener_type.lower() in sharp_thickeners:
        score += 2
    elif thickener_type.lower() in {"starch_ether", "guar_locust_bean"}:
        score += 1

    # Printing speed (Ch. 7.7.5): higher speed → sharper mark
    if printing_speed_m_per_hour >= 3600:
        score += 3
    elif printing_speed_m_per_hour >= 2400:
        score += 2
    elif printing_speed_m_per_hour >= 1800:
        score += 1

    # Fabric surface
    if fabric_surface_texture == "smooth":
        score += 2
    elif fabric_surface_texture == "textured":
        score += 1

    # Design coverage: blotch designs → boundary spreading more likely
    if design_coverage_pct < 30:
        score += 2
    elif design_coverage_pct < 60:
        score += 1

    if score >= 14:
        return "excellent"
    elif score >= 9:
        return "good"
    elif score >= 5:
        return "acceptable"
    else:
        return "poor"


def predict_saw_tooth_risk(
    screen_mesh_holes_per_inch: int,
    design_coverage_pct: float
) -> str:
    """
    Predicts saw-tooth effect risk at design boundaries.

    Source: Miles, Textile Printing, Ch. 2.7.2.
    'In many screen-printed fabrics the edges of the printed areas appear
    serrated... This is known as the "saw-tooth effect"... an almost
    inevitable consequence of the design area consisting of a regular array
    of threads and spaces.' (Ch. 2.7.2)
    Rotary screen pores are hexagonal (not square mesh): saw-tooth pattern
    differs from flat-screen but is still present at coarse mesh counts.
    Finer mesh screens (PentaScreens: 0.12 mm minimum line width vs
    0.24 mm for standard) dramatically reduce saw-tooth (Ch. 2.7.3).
    """
    if screen_mesh_holes_per_inch >= 125:
        base = "negligible"   # PentaScreen / NovaScreen quality
    elif screen_mesh_holes_per_inch >= 80:
        base = "minor"
    else:
        base = "significant"  # standard 60-mesh coarser

    # Blotch designs show more saw-tooth at boundaries
    if design_coverage_pct > 60 and base == "minor":
        return "significant"
    return base


def predict_stripe_fault_risk(
    squeegee_type: str,
    squeegee_pressure_setting: str,
    screen_working_width_cm: float,
    fabric_width_cm: float,
    paste_viscosity_Pa_s: float,
    operating_hours_since_maintenance: float,
    maintenance_interval_hours: float
) -> str:
    """
    Predicts longitudinal stripe fault risk from uneven squeegee pressure.

    Source: Miles, Textile Printing, Ch. 2.4.1.
    'If the squeegee pressure is uneven, the volume of print paste applied
    across the width will vary, resulting in an unlevel appearance in the final
    print. This problem is most serious when printing wide fabrics.' (Ch. 2.4.1)
    Reggiani system: phosphor-bronze blade pressed by inflated air sack →
    even pressure across full width.
    Magnetic rods: pressure dependent on field strength settings; large rods
    can distort the screen (Ch. 2.4.1).
    Very wide screens (>200 cm) magnify blade deflection at centre → stripe.
    Worn bearings → blade tilts → one end bears more than the other.
    High viscosity pastes: resist blade, amplifying pressure non-uniformity.
    """
    risk = 0

    # Squeegee type: airflow rod has most uniform pressure (air sack)
    if squeegee_type.lower() == "airflow_rod":
        risk += 0
    elif squeegee_type.lower() == "steel_blade":
        risk += 1
    elif squeegee_type.lower() == "magnetic_rod":
        risk += 2  # field setting errors → stripe; large rods distort screen

    # Wide fabrics amplify blade deflection
    width_ratio = fabric_width_cm / max(1.0, screen_working_width_cm)
    if width_ratio > 0.9:
        risk += 2   # fabric almost as wide as screen → edge pressure issues
    elif width_ratio > 0.75:
        risk += 1

    # Absolute width
    if screen_working_width_cm > 250:
        risk += 2
    elif screen_working_width_cm > 180:
        risk += 1

    # High pressure setting amplifies non-uniformity
    if squeegee_pressure_setting == "high":
        risk += 1

    # High viscosity: resists blade, amplifies pressure imbalance
    if paste_viscosity_Pa_s > 3.0:
        risk += 1

    # Maintenance (worn bearings → blade tilt)
    maint_ratio = operating_hours_since_maintenance / max(1.0, maintenance_interval_hours)
    if maint_ratio > 1.0:
        risk += 2
    elif maint_ratio > 0.85:
        risk += 1

    if risk <= 2:
        return "low"
    elif risk <= 4:
        return "medium"
    else:
        return "high"


def predict_colour_crushing_risk(
    number_of_screens: int,
    printing_speed_m_per_hour: float,
    colorant_type: str
) -> str:
    """
    Predicts colour crushing risk (wet colour compressed by following screen).

    Source: Miles, Textile Printing, Ch. 2.3.5 (flat-screen discussion,
    directly applicable to rotary), Ch. 2.4 (rotary screens very close together).
    'The cylindrical screens can be much closer together than is possible with
    flat screens.' (Miles Ch. 2.4)
    In rotary machines the screens are adjacent, so every subsequent screen
    passes over previously deposited wet colour. Higher number of screens and
    higher speeds both increase crushing.
    Pigment pastes: more sensitive to crushing than dye-thickener pastes.
    At high speeds less inter-colour drying occurs before next screen contact.
    """
    risk = 0

    if number_of_screens > 16:
        risk += 3
    elif number_of_screens > 10:
        risk += 2
    elif number_of_screens > 6:
        risk += 1

    # High speed: no drying between screens (continuous, screens adjacent)
    if printing_speed_m_per_hour > 3600:
        risk += 2
    elif printing_speed_m_per_hour > 2400:
        risk += 1

    # Pigment pastes more vulnerable (Miles Ch. 5.2.3)
    if colorant_type.lower() == "pigment":
        risk += 1

    if risk <= 2:
        return "low"
    elif risk <= 4:
        return "medium"
    else:
        return "high"


def predict_paste_level_instability_risk(
    level_control_type: str,
    paste_pump_type: str,
    paste_distribution_quality: str,
    paste_viscosity_Pa_s: float,
    design_coverage_pct: float
) -> str:
    """
    Predicts paste level instability risk inside the rotating screen.

    Source: Miles, Textile Printing, Ch. 2.4.
    'A sensor (level control) actuates the pump when the paste level falls
    below a preset height.' (Ch. 2.4)
    'Holes in the pipe allow the paste to run down... the holes need to be
    larger at the end furthest from the pump to achieve an even spread across
    the full width.' (Ch. 2.4)
    Variable paste level → variable squeeze-force on paste → variable colour
    depth along fabric length (unlevel prints).
    Manual level control: operator-dependent → highly variable.
    High coverage: paste consumed faster → larger level fluctuations.
    High viscosity: pump struggles to maintain level, especially at far end.
    """
    risk = 0

    if level_control_type.lower() == "manual":
        risk += 3  # inherently irregular
    else:
        risk += 0  # sensor automatic: much better

    # Pump type: peristaltic most consistent at low flow
    if paste_pump_type.lower() == "peristaltic":
        risk += 0
    elif paste_pump_type.lower() == "gear":
        risk += 1   # slight pulsing at low RPM
    else:
        risk += 1

    # Paste distribution quality
    if paste_distribution_quality.lower() == "variable":
        risk += 2   # holes not sized correctly → far-end starvation
    else:
        risk += 0

    # High viscosity: harder to push to far end against gravity
    if paste_viscosity_Pa_s > 3.0:
        risk += 1

    # High coverage: faster paste consumption → more level fluctuation
    if design_coverage_pct > 70:
        risk += 1

    if risk <= 2:
        return "low"
    elif risk <= 4:
        return "medium"
    else:
        return "high"


def predict_screen_creasing_risk(
    screen_type: str,
    screen_wall_thickness_mm: float,
    squeegee_pressure_setting: str,
    squeegee_type: str,
    screen_working_width_cm: float
) -> str:
    """
    Predicts risk of screen creasing (permanent deformation of nickel cylinder).

    Source: Miles, Textile Printing, Ch. 2.4.1, Ch. 2.7.3.
    'With high magnetic-field settings or when large rods are used the screen
    is likely to be distorted.' (Ch. 2.4.1)
    Lacquer screens: wall 0.08–0.10 mm → more susceptible to creasing.
    NovaScreens: slightly thicker → less creasing (Ch. 2.7.3).
    Galvano screens: stronger solid walls → lower crease risk.
    Wide screens: greater bending moment at centre under squeegee load.
    High squeegee pressure on thin-walled screen → distortion.
    """
    risk = 0

    # Screen type / wall thickness
    if screen_type.lower() in ("lacquer_rotary",):
        if screen_wall_thickness_mm <= 0.10:
            risk += 3
        elif screen_wall_thickness_mm <= 0.12:
            risk += 2
        else:
            risk += 1
    elif screen_type.lower() == "penta_screen":
        risk += 2  # thin walls like lacquer
    elif screen_type.lower() == "nova_screen":
        risk += 1  # slightly thicker walls (Ch. 2.7.3)
    else:  # galvano_rotary
        risk += 0  # strongest walls

    # Squeegee type: magnetic rod can distort screen (Ch. 2.4.1)
    if squeegee_type.lower() == "magnetic_rod":
        risk += 2
    elif squeegee_type.lower() == "airflow_rod":
        risk += 0  # gentle, uniform

    # Pressure setting
    if squeegee_pressure_setting == "high":
        risk += 2
    elif squeegee_pressure_setting == "medium":
        risk += 0

    # Wide screens: more bending moment at centre
    if screen_working_width_cm > 280:
        risk += 1

    if risk <= 2:
        return "low"
    elif risk <= 4:
        return "medium"
    else:
        return "high"


def predict_registration_accuracy(
    independent_screen_speed_control: bool,
    laser_registration: bool,
    number_of_screens: int,
    adhesive_type: str,
    blanket_type: str,
    printing_speed_m_per_hour: float,
    operating_hours_since_maintenance: float,
    maintenance_interval_hours: float
) -> str:
    """
    Predicts colour registration accuracy for rotary printing.

    Source: Miles, Textile Printing, Ch. 2.4.2, 2.4.3, 2.4.5.
    Rotary advantage over flat: continuous motion, both-end screen drive,
    shorter blanket, no intermittent advance inertia (Ch. 2.4.3).
    'Some rotary screens are driven from both sides to avoid the danger of
    twisting and buckling.' (Ch. 2.4.3)
    Independent speed control (stepper/servo motors): compensates fabric drag
    causing screens to be pulled slightly forward (Ch. 2.4.3, Zimmer reference).
    Laser registration (MBK): screens pre-aligned before run → 'several metres
    of fabric wasted... has been overcome' (Ch. 2.4.2).
    'Fitting of patterns during an extended printing run is sometimes less than
    satisfactory, especially with wide fabrics or pile fabrics.' (Ch. 2.4.3)
    Worn blanket bearings → sideways slip → local pattern misfit.
    More screens → more cumulative registration error.
    """
    score = 0

    # Base: rotary always better than flat due to continuous motion
    score += 4

    # Independent screen speed control (Ch. 2.4.3)
    if independent_screen_speed_control:
        score += 3

    # Laser registration (Ch. 2.4.2)
    if laser_registration:
        score += 2

    # Number of screens: more → more potential misfit
    if number_of_screens <= 6:
        score += 2
    elif number_of_screens <= 12:
        score += 1
    elif number_of_screens > 16:
        score -= 1

    # Adhesive type
    if adhesive_type.lower() == "thermoplastic":
        score += 2   # heated plate, durable tack, standard for rotary
    elif adhesive_type.lower() == "semi_permanent":
        score += 1
    else:
        score += 0   # water-based: inconsistent at high speed

    # Blanket type
    if blanket_type.lower() == "low_extensibility_synthetic":
        score += 1   # Miles Ch. 2.4.3: 'blankets of low extensibility required'

    # Speed: very high speed → blanket overrun on ramp-up/ramp-down
    if printing_speed_m_per_hour > 3600:
        score -= 1

    # Maintenance
    maint_ratio = operating_hours_since_maintenance / max(1.0, maintenance_interval_hours)
    if maint_ratio > 1.0:
        score -= 2
    elif maint_ratio > 0.85:
        score -= 1

    if score >= 10:
        return "excellent"
    elif score >= 6:
        return "good"
    else:
        return "poor"


def predict_repeat_fitting_quality(
    screen_circumference_mm: float,
    design_repeat_length_cm: float
) -> str:
    """
    Predicts design repeat fitting quality for rotary screen.

    Source: Miles, Textile Printing, Ch. 2.5.4 (Step and repeat).
    'Thus for a 64 cm circumference screen, for example, the repeat must be
    64 cm or a whole number fraction of this (32, 21.33, 16 cm and so forth).'
    (Ch. 2.5.4)
    If the repeat does not divide evenly into the circumference, a join line
    appears at every revolution of the screen, ruining the design continuity.
    The large-repeat solution uses intermittent screen lifting (Zimmer jumper
    technique, Ch. 2.4.4) for designs exceeding the standard circumference.
    """
    if design_repeat_length_cm <= 0 or screen_circumference_mm <= 0:
        return "poor"

    circumference_cm = screen_circumference_mm / 10.0
    ratio = circumference_cm / design_repeat_length_cm

    # Check if ratio is close to a whole number
    rounded_ratio = round(ratio)
    if rounded_ratio < 1:
        rounded_ratio = 1

    deviation = abs(ratio - rounded_ratio) / max(0.01, rounded_ratio)

    if deviation < 0.005:
        return "excellent"  # very close to whole-number fit
    elif deviation < 0.02:
        return "good"       # small discrepancy; minor join line possible
    else:
        return "poor"       # significant join line will be visible


def predict_fixation_pct(
    colorant_type: str,
    fiber_type: str,
    fixation_method: str,
    fixation_temperature_C: float,
    fixation_time_min: float,
    urea_concentration_g_per_kg: float,
    alkali_type: str,
    alkali_concentration_g_per_kg: float,
    paste_penetration_depth: str,
    steamer_type: str
) -> float:
    """
    Predicts fixation efficiency (% of applied colorant fixed to fabric).

    Source: Miles, Textile Printing, Ch. 8.3.5 (Dye fixation in steam),
    Ch. 8.3.6 (High-temperature steaming), Ch. 8.2 (Pigment prints).
    Festoon steamer: 800 m capacity, 80 m/min throughput, 10 min steam
    at 100°C; star/roller ager options for shorter treatments.
    HT steam reactive cotton: 1 min at 150°C if 100–200 g/kg urea included
    (Lockett, cited Miles Ch. 8.3.6); same dyes need 5 min at 100°C.
    Disperse/polyester HT: 1 min at 180°C vs 30 min pressure steam at 120°C.
    Pigment: binder crosslinks in hot air 140–160°C, 3–5 min; steam adverse.
    Full penetration → better fibre–dye contact → higher fixation.
    """
    # Base fixation by colorant-fibre system (optimum conditions)
    base_map = {
        ("reactive_dye", "cotton"): 75.0,
        ("reactive_dye", "viscose"): 70.0,
        ("reactive_dye", "blend_PES_CO"): 65.0,
        ("disperse_dye", "polyester"): 72.0,
        ("disperse_dye", "blend_PES_CO"): 68.0,
        ("acid_dye", "nylon"): 80.0,
        ("acid_dye", "wool"): 82.0,
        ("acid_dye", "silk"): 78.0,
        ("vat_dye", "cotton"): 85.0,
        ("pigment", "cotton"): 92.0,
        ("pigment", "polyester"): 90.0,
        ("pigment", "blend_PES_CO"): 90.0,
        ("pigment", "nylon"): 88.0,
        ("discharge", "cotton"): 78.0,
        ("azoic", "cotton"): 80.0,
    }
    base = base_map.get((colorant_type.lower(), fiber_type.lower()), 68.0)
    method_bonus = 0.0

    # Fixation method adjustments
    if colorant_type.lower() == "reactive_dye":
        if fixation_method == "saturated_steam":
            # 10 min target at 100°C (Miles Ch. 8.3.5)
            if fixation_time_min >= 10.0:
                method_bonus = 0.0
            elif fixation_time_min >= 5.0:
                method_bonus = -8.0
            else:
                method_bonus = -15.0
            if alkali_concentration_g_per_kg < 10.0:
                method_bonus -= 15.0
            elif alkali_concentration_g_per_kg < 18.0:
                method_bonus -= 5.0
        elif fixation_method == "high_temp_steam":
            # Urea essential for HT steam (Miles Ch. 8.3.6)
            if urea_concentration_g_per_kg >= 100.0:
                method_bonus = 5.0
                if fixation_time_min < 1.0:
                    method_bonus -= 15.0
                if alkali_concentration_g_per_kg < 10.0:
                    method_bonus -= 15.0
            else:
                method_bonus = -12.0  # urea absent → poor yield (Miles 8.3.6)
        elif fixation_method == "baking_hot_air":
            method_bonus = -8.0   # steam preferred for reactive
        else:
            method_bonus = -18.0

    elif colorant_type.lower() == "disperse_dye":
        if fixation_method == "high_temp_steam":
            if fixation_temperature_C >= 175.0:
                method_bonus = 8.0
                if fixation_time_min < 1.0:
                    method_bonus -= 20.0
            else:
                method_bonus = 2.0
        elif fixation_method == "pressure_steam":
            method_bonus = 12.0   # most efficient (Miles Ch. 8.3.6)
        elif fixation_method == "baking_hot_air":
            method_bonus = -5.0
        else:
            method_bonus = -20.0

    elif colorant_type.lower() == "pigment":
        if fixation_method in ("baking_hot_air", "none_pigment_curing"):
            if 140.0 <= fixation_temperature_C <= 165.0:
                method_bonus = 0.0
            elif fixation_temperature_C < 120.0:
                method_bonus = -15.0
            else:
                method_bonus = 0.0
            if fixation_time_min < 3.0:
                method_bonus -= 10.0
        elif fixation_method == "saturated_steam":
            method_bonus = -8.0   # steam adverse for binder crosslinking (Ch. 8.2)
        else:
            method_bonus = -5.0

    elif colorant_type.lower() == "acid_dye":
        if fixation_method == "saturated_steam":
            method_bonus = 0.0
            if fixation_time_min < 15.0:
                method_bonus -= 10.0
        elif fixation_method == "pressure_steam":
            method_bonus = 5.0
        else:
            method_bonus = -10.0

    elif colorant_type.lower() == "vat_dye":
        if fixation_method == "saturated_steam":
            # Needs 8–20 min in air-free steam (Miles Recipe 8.1)
            if fixation_time_min < 8.0:
                method_bonus = -15.0
            else:
                method_bonus = 0.0
        else:
            method_bonus = -15.0

    # Steamer type consistency
    if colorant_type.lower() in ("reactive_dye", "vat_dye", "acid_dye"):
        if steamer_type == "festoon":
            method_bonus += 2.0   # optimal for continuous high-speed (Ch. 8.3.2)
        elif steamer_type == "star_batch":
            method_bonus += 1.0

    # Penetration depth
    pen_bonus = {"full": 3.0, "partial": 0.0, "surface_only": -5.0}
    method_bonus += pen_bonus.get(paste_penetration_depth, 0.0)

    return round(max(30.0, min(98.0, base + method_bonus)), 1)


def predict_wash_fastness(
    colorant_type: str,
    fiber_type: str,
    estimated_fixation_pct: float,
    wash_off_applied: bool,
    wash_off_temperature_C: float,
    wash_off_stages: int,
    counterflow_washing: bool,
    paste_penetration_depth: str,
    binder_concentration_pct: float
) -> float:
    """
    Predicts wash fastness rating (ISO 1–5) of the print.

    Source: Miles, Textile Printing, Ch. 8.5.3 (Reactive dyes on cellulosic):
    'At 90°C the same dyes can be completely cleared in 90 s and the difference
    due to variations in affinity is very much reduced.' (Ch. 8.5.3, Fig. 8.12)
    Miles Table 8.2: at 30 m/min on 8-box range, hot dwell = 120 s;
    at 60 m/min = 60 s; at 100 m/min = 36 s.
    Counterflow principle (Miles Ch. 8.6, Parish Eqn 8.2): maximises removal
    efficiency at same water usage.
    Unfixed dye remaining → wash fastness deteriorates.
    Pigment: binder film quality governs fastness.
    """
    base_map = {
        ("reactive_dye", "cotton"): 4.5,
        ("reactive_dye", "viscose"): 4.0,
        ("disperse_dye", "polyester"): 4.5,
        ("acid_dye", "nylon"): 4.0,
        ("acid_dye", "wool"): 4.0,
        ("vat_dye", "cotton"): 5.0,
        ("pigment", "cotton"): 4.0,
        ("pigment", "polyester"): 3.5,
        ("pigment", "blend_PES_CO"): 3.5,
    }
    base = base_map.get((colorant_type.lower(), fiber_type.lower()), 3.5)

    # Low fixation → more unfixed dye → poor wash fastness
    if estimated_fixation_pct < 60:
        base -= 1.5
    elif estimated_fixation_pct < 75:
        base -= 0.5

    # Wash-off quality
    if colorant_type.lower() != "pigment":
        if not wash_off_applied:
            base -= 1.5
        else:
            # Temperature: 90°C clears in 90 s vs >4 min at 60°C (Ch. 8.5.3)
            if wash_off_temperature_C >= 90:
                base += 0.3
            elif wash_off_temperature_C < 60:
                base -= 0.5
            # Stages
            if wash_off_stages >= 8:
                base += 0.2
            elif wash_off_stages < 4:
                base -= 0.4
            # Counterflow
            if counterflow_washing:
                base += 0.2  # Miles Ch. 8.6: maximises removal efficiency

    # Pigment: binder concentration
    if colorant_type.lower() == "pigment":
        if binder_concentration_pct < 7.0:
            base -= 1.0
        elif binder_concentration_pct >= 10.0:
            base += 0.2

    # Surface-only penetration → less bond
    if paste_penetration_depth == "surface_only":
        base -= 0.5

    return round(max(1.0, min(5.0, base)), 1)


def predict_light_fastness(
    colorant_type: str,
    fiber_type: str,
    paste_colorant_conc_g_per_kg: float,
    estimated_fixation_pct: float
) -> float:
    """
    Predicts light fastness rating (ISO 1–8) of the print.

    Source: Miles, Textile Printing, Ch. 5 (colorant classes).
    Pigment: 'unsurpassed fastness to light' (Ch. 5.2.5 advantage 2).
    Vat dyes: highest light fastness of dye classes.
    Reactive: typically 5.5–6.5; Acid: 5–6; Disperse: 5.5–7.
    Low fixation → some loose surface dye → fades faster.
    Very pale shades: lower apparent light fastness (smaller depth change
    more perceptible).
    """
    base_map = {
        ("reactive_dye", "cotton"): 6.0,
        ("reactive_dye", "viscose"): 5.5,
        ("disperse_dye", "polyester"): 6.5,
        ("acid_dye", "nylon"): 5.5,
        ("acid_dye", "wool"): 5.5,
        ("vat_dye", "cotton"): 7.5,
        ("pigment", "cotton"): 7.0,
        ("pigment", "polyester"): 7.0,
        ("pigment", "blend_PES_CO"): 7.0,
        ("azoic", "cotton"): 6.5,
    }
    base = base_map.get((colorant_type.lower(), fiber_type.lower()), 5.5)

    if estimated_fixation_pct < 70:
        base -= 0.5
    if paste_colorant_conc_g_per_kg < 10.0:
        base -= 0.5

    return round(max(1.0, min(8.0, base)), 1)


def predict_rub_fastness(
    colorant_type: str,
    paste_penetration_depth: str,
    binder_concentration_pct: float,
    estimated_fixation_pct: float,
    design_coverage_pct: float
) -> tuple:
    """
    Predicts dry and wet rubbing fastness (ISO 1–5).

    Source: Miles, Textile Printing, Ch. 5.2.5 (Pigment disadvantages).
    'Depending upon the pigment and binder... prints can show rub marks and/or
    loss in colour depth.' (Ch. 5.2.5)
    Dark pigment prints at high coverage most susceptible.
    Dye prints: rub fastness depends on wash-off; unfixed surface dye crocks.
    Full penetration → less surface colorant → better rub.
    Wet rub always 0.5–1.0 grade lower than dry.
    Returns (dry_rub, wet_rub).
    """
    if colorant_type.lower() == "pigment":
        base_dry = 4.0
        if binder_concentration_pct < 7.0:
            base_dry -= 1.5
        elif binder_concentration_pct >= 10.0:
            base_dry += 0.2
        if design_coverage_pct > 70:
            base_dry -= 0.5
    else:
        base_dry = 4.0
        if estimated_fixation_pct < 70:
            base_dry -= 1.0
        elif estimated_fixation_pct >= 85:
            base_dry += 0.2

    if paste_penetration_depth == "surface_only":
        base_dry -= 0.5
    elif paste_penetration_depth == "full":
        base_dry += 0.2

    dry = round(max(1.0, min(5.0, base_dry)), 1)
    wet = round(max(1.0, min(5.0, base_dry - 0.7)), 1)
    return dry, wet


def predict_colour_yield(
    colorant_type: str,
    thickener_type: str,
    paste_colorant_conc_g_per_kg: float,
    estimated_fixation_pct: float,
    paste_penetration_depth: str
) -> float:
    """
    Predicts relative colour yield (0–1).

    Source: Miles, Textile Printing, Ch. 7.2.3, Ch. 7.6.
    'The highest colour yield... is only obtained when penetration... is at
    a minimum.' (Ch. 7.2.3) — dye/pigment concentrated at surface → maximum
    apparent depth.
    Synthetic polyacrylic thickeners: 'significantly higher fixation and colour
    yields with disperse dyes on polyester' than natural polymers (Ch. 7.6).
    Starch-based thickeners give high colour yield by restricting penetration.
    High fixation directly drives usable colour yield.
    """
    base = (estimated_fixation_pct / 100.0) * 0.85

    # Thickener effect (Ch. 7.2.3, 7.6)
    high_yield = {"starch_ether", "crystal_gum", "guar_locust_bean"}
    if thickener_type.lower() in high_yield:
        base *= 1.10
    elif thickener_type.lower() == "synthetic_polyacrylic":
        base *= 1.08   # thinner film → more dye transfer (Ch. 7.6)
    elif thickener_type.lower() == "alginate":
        base *= 0.97

    # Penetration: surface-only → highest apparent yield
    if paste_penetration_depth == "surface_only":
        base *= 1.05
    elif paste_penetration_depth == "full":
        base *= 0.95

    # Concentration saturation
    if paste_colorant_conc_g_per_kg > 100:
        base *= 0.93
    elif paste_colorant_conc_g_per_kg < 10:
        base *= 0.90

    return round(max(0.1, min(1.0, base)), 3)


def predict_unfixed_staining_risk(
    colorant_type: str,
    estimated_fixation_pct: float,
    wash_off_applied: bool,
    wash_off_temperature_C: float,
    wash_off_stages: int,
    counterflow_washing: bool,
    residual_unfixed_dye_pct: float
) -> str:
    """
    Predicts unfixed dye staining risk of white/pale ground areas.

    Source: Miles, Textile Printing, Ch. 8.5.
    'Staining of unprinted areas by adsorption of dyes from the wash liquor
    is a major hazard where the concentration of unfixed dye is allowed to
    build up in the washing-off process.' (Ch. 8.5)
    Counterflow (Parish Eqn 8.2) minimises liquor contamination build-up.
    At 90°C the risk is greatly reduced vs 60°C (Ch. 8.5.3, Fig. 8.12).
    Miles Table 8.2: at 30 m/min 8-box range, hot dwell = 120 s (adequate);
    at 100 m/min = 36 s (borderline for heavy shades).
    """
    if colorant_type.lower() == "pigment":
        return "low"

    risk = 0
    unfixed_pct = 100.0 - estimated_fixation_pct
    if unfixed_pct > 35:
        risk += 3
    elif unfixed_pct > 20:
        risk += 2
    elif unfixed_pct > 10:
        risk += 1

    if residual_unfixed_dye_pct > 5.0:
        risk += 2
    elif residual_unfixed_dye_pct > 2.0:
        risk += 1

    if not wash_off_applied:
        risk += 4
    else:
        if wash_off_temperature_C >= 90:
            risk -= 2
        elif wash_off_temperature_C < 60:
            risk += 2
        if wash_off_stages < 4:
            risk += 1
        if counterflow_washing:
            risk -= 1  # counterflow keeps fresh liquor at fabric exit

    risk = max(0, risk)
    if risk <= 2:
        return "low"
    elif risk <= 4:
        return "medium"
    else:
        return "high"


def predict_binder_crosslink_quality(
    colorant_type: str,
    binder_concentration_pct: float,
    fixation_method: str,
    fixation_temperature_C: float,
    fixation_time_min: float,
    alkali_type: str
) -> str:
    """
    Predicts binder crosslink quality for pigment prints.

    Source: Miles, Textile Printing, Ch. 8.2, Ch. 5.2.2.
    'Times of 3–5 min at temperatures in the range 140–160°C have been
    generally preferred.' (Ch. 8.2, Miles, roller baker oven)
    Synthetic polyacrylic thickener with ammonia → free acid on drying →
    autocatalysis of crosslinking, no external catalyst needed (Ch. 7.6).
    Steam adverse for binder crosslinking (Ch. 5.2.2).
    """
    if colorant_type.lower() != "pigment":
        return "good"

    score = 0
    if binder_concentration_pct >= 10.0:
        score += 3
    elif binder_concentration_pct >= 7.0:
        score += 2
    elif binder_concentration_pct >= 4.0:
        score += 1

    if fixation_method in ("baking_hot_air", "none_pigment_curing"):
        score += 3
    elif fixation_method == "high_temp_steam":
        score += 1
    # saturated steam: adverse (Ch. 5.2.2) → score += 0

    if 140.0 <= fixation_temperature_C <= 165.0:
        score += 2
    elif fixation_temperature_C < 120.0:
        score += 0
    else:
        score += 1

    if fixation_time_min >= 3.0:
        score += 1

    # Acid condition promotes crosslinking
    acid_types = {"diammonium_phosphate", "none", "ammonium_sulphate"}
    if alkali_type.lower() in acid_types:
        score += 1
    elif alkali_type.lower() in {"sodium_bicarbonate", "sodium_carbonate", "caustic_soda"}:
        score -= 1

    if score >= 8:
        return "good"
    elif score >= 5:
        return "adequate"
    else:
        return "poor"


def predict_machine_efficiency(
    printing_speed_m_per_hour: float,
    number_of_screens: int,
    dryer_capacity: str,
    design_coverage_pct: float,
    colorant_type: str,
    independent_screen_speed_control: bool,
    laser_registration: bool,
    operating_hours_since_maintenance: float,
    maintenance_interval_hours: float
) -> float:
    """
    Predicts machine efficiency % (ratio of productive to total machine time).

    Source: Miles, Textile Printing, Ch. 2.4.5.
    'Rotary-screen printing machines are expensive, and it therefore pays to
    keep downtime to a minimum.' (Ch. 2.4.5)
    Reggiani: washing screens between colourways on machine → faster changeover.
    Independent speed control, laser registration → less start-up fabric waste.
    Dryer limits speed → at inadequate dryer capacity, speed must be reduced,
    reducing effective capacity (not reflected in efficiency% directly, but
    causes sub-optimal operation and colour faults → stoppages).
    More screens → more colour changes, screen washes, and possible faults.
    Pigment prints need no steaming → faster cycle per metre → better OEE.
    """
    # Base efficiency: rotary is highest of all screen types at scale
    base_eff = 88.0  # rotary: continuous, less changeover than flat

    # Number of screens penalty
    if number_of_screens > 16:
        base_eff -= (number_of_screens - 16) * 0.6
    elif number_of_screens > 10:
        base_eff -= (number_of_screens - 10) * 0.4

    # Dryer capacity: limits print speed, causes colour faults at high coverage
    if dryer_capacity == "low":
        base_eff -= 12.0
    elif dryer_capacity == "adequate":
        base_eff -= 3.0

    # High coverage: more paste, more drying requirement → forced speed reduction
    if design_coverage_pct > 70:
        base_eff -= 5.0
    elif design_coverage_pct > 50:
        base_eff -= 2.0

    # Registration/control features reduce start-up waste
    if independent_screen_speed_control:
        base_eff += 2.0
    if laser_registration:
        base_eff += 1.5

    # Pigment: no steaming machine cycle → slightly higher OEE for throughput
    if colorant_type.lower() == "pigment":
        base_eff += 2.0

    # Maintenance overdue
    maint_ratio = operating_hours_since_maintenance / max(1.0, maintenance_interval_hours)
    if maint_ratio > 1.0:
        base_eff -= 8.0
    elif maint_ratio > 0.85:
        base_eff -= 3.0

    return round(max(30.0, min(96.0, base_eff)), 1)


# ─────────────────────────────────────────────────────────────────────────────
# MASTER SIMULATION FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def simulate_rotary_printing(
    fabric: InputDyedFabric,
    params: RotaryPrintingOperationalParams
) -> RotaryPrintedFabricOutput:
    """
    Master simulation function for Rotary Screen Printing.

    Takes Layer 2 (InputDyedFabric — output of a dyeing simulation) and
    Layer 3 (RotaryPrintingOperationalParams), runs all prediction models, and
    returns Layer 4 (RotaryPrintedFabricOutput).

    Performs parameter validation and generates warnings for out-of-range
    conditions based on limits documented in Miles (2003).
    """
    warnings = []

    # ── PARAMETER VALIDATION ─────────────────────────────────────────────

    # Screen mesh vs screen type compatibility (Miles Ch. 2.7.3)
    if params.screen_type == "lacquer_rotary":
        if params.screen_mesh_holes_per_inch > 100:
            warnings.append(
                f"Lacquer (electroformed) rotary screens cannot be reliably "
                f"produced finer than 100 mesh due to nickel bridging across "
                f"insulators (Miles Ch. 2.7.3). Specified {params.screen_mesh_holes_per_inch} "
                f"mesh exceeds this limit. Use PentaScreen or NovaScreen for "
                f"finer mesh requirements."
            )
    elif params.screen_type == "galvano_rotary":
        if params.screen_mesh_holes_per_inch > 80:
            warnings.append(
                f"Galvano screens have a practical maximum of 80 mesh for reliable "
                f"manufacture (Miles Ch. 2.7.3). Specified {params.screen_mesh_holes_per_inch} "
                f"mesh exceeds this. Use lacquer or PentaScreen technology."
            )
        if params.screen_open_area_pct > 15:
            warnings.append(
                f"Galvano screen open area ({params.screen_open_area_pct:.0f}%) seems "
                f"high. Typical galvano screens for textiles: <13% inside measure. "
                f"Verify screen specification."
            )

    # Screen circumference vs repeat (Miles Ch. 2.5.4)
    if params.screen_circumference_mm > 0 and params.design_repeat_length_cm > 0:
        circ_cm = params.screen_circumference_mm / 10.0
        ratio = circ_cm / params.design_repeat_length_cm
        rounded = round(ratio)
        if rounded < 1:
            rounded = 1
        dev = abs(ratio - rounded) / max(0.01, rounded)
        if dev > 0.02:
            warnings.append(
                f"Design repeat ({params.design_repeat_length_cm:.1f} cm) does not fit "
                f"as a whole-number fraction of screen circumference "
                f"({circ_cm:.1f} cm). Required: circumference = N × repeat for integer N. "
                f"'For a 64 cm circumference screen the repeat must be 64 cm or a "
                f"whole number fraction of this.' (Miles Ch. 2.5.4) "
                f"A join line will be visible across fabric every screen revolution. "
                f"Standard circumferences: 518, 537, 640, 668, 688, 725, 801, 914 mm."
            )

    # Standard circumference check (Miles Ch. 2.4.4)
    standard_circumferences = {518, 537, 640, 668, 688, 725, 801, 819, 914, 1018}
    circ_int = int(round(params.screen_circumference_mm))
    if circ_int not in standard_circumferences and params.screen_circumference_mm > 0:
        warnings.append(
            f"Screen circumference {params.screen_circumference_mm:.0f} mm is not one "
            f"of the standard sizes (518, 537, 640, 668, 688, 725, 801, 819, 914, "
            f"1018 mm, Miles Ch. 2.4.4). Non-standard circumferences may require "
            f"custom mandrels and limit design options. Verify this is intentional."
        )

    # Printing speed vs dryer capacity (Miles Ch. 2.4)
    if params.printing_speed_m_per_hour > 4200:
        warnings.append(
            f"Printing speed {params.printing_speed_m_per_hour:.0f} m/h exceeds the "
            f"typical operational range of 1800–4200 m/h (30–70 m/min) for rotary "
            f"screen machines. 'It is quite possible to run the machine faster... "
            f"the limitations often being the length and efficiency of the cloth "
            f"and blanket dryers.' (Miles Ch. 2.4) Verify dryer capacity."
        )

    if params.design_coverage_pct > 70 and params.dryer_capacity == "low":
        warnings.append(
            f"High design coverage ({params.design_coverage_pct:.0f}%) with low dryer "
            f"capacity will force printing speed reduction to ensure adequate drying "
            f"before steaming/fixation. Consider either reducing speed, increasing "
            f"dryer temperature, or using a longer dryer (Miles Ch. 2.4)."
        )

    # Fabric width vs screen width
    if fabric.fabric_width_cm > params.screen_working_width_cm:
        warnings.append(
            f"Fabric width ({fabric.fabric_width_cm:.0f} cm) exceeds screen working "
            f"width ({params.screen_working_width_cm:.0f} cm). Selvedges will be "
            f"unprinted or the screen will be damaged at the edges. "
            f"Use a wider screen or narrower fabric."
        )

    # Magnetic rod + thin lacquer screen (Miles Ch. 2.4.1)
    if (params.squeegee_type == "magnetic_rod"
            and params.screen_type in ("lacquer_rotary", "penta_screen")
            and params.screen_wall_thickness_mm <= 0.10):
        warnings.append(
            f"Magnetic rod squeegee with thin lacquer/PentaScreen (wall "
            f"{params.screen_wall_thickness_mm:.2f} mm) risks screen distortion. "
            f"'With high magnetic-field settings or when large rods are used "
            f"the screen is likely to be distorted.' (Miles Ch. 2.4.1) "
            f"Use a steel blade or airflow squeegee on fine-mesh thin-walled screens."
        )

    # Thickener compatibility (Miles Ch. 5.3.5)
    if (params.colorant_type == "reactive_dye"
            and params.thickener_type.lower() not in
            {"alginate", "synthetic_polyacrylic", "half_emulsion"}):
        warnings.append(
            f"Thickener '{params.thickener_type}' is not recommended for reactive dye "
            f"printing. Only sodium alginate, synthetic polyacrylic, or half-emulsion "
            f"systems are compatible — starch and guar react with the dye, giving low "
            f"colour yields (Miles Ch. 5.3.5). Use alginate (natural choice for "
            f"reactive) or synthetic polyacrylic (highest colour yield, Ch. 7.6)."
        )

    # Reactive dye alkali check
    if params.colorant_type == "reactive_dye":
        if (params.alkali_type == "none"
                or params.alkali_concentration_g_per_kg < 10.0):
            warnings.append(
                f"Reactive dye printing requires alkali (typically NaHCO3 ≥20 g/kg) "
                f"to ionise cellulose for covalent dye–fibre bond formation "
                f"(Miles Ch. 5.3.5). Insufficient alkali → very low fixation "
                f"and poor wash fastness."
            )
        if (params.fixation_method == "high_temp_steam"
                and params.urea_concentration_g_per_kg < 100.0):
            warnings.append(
                f"HT steam fixation of reactive dyes requires 100–200 g/kg urea "
                f"to hold moisture for dye–fibre reaction (Lockett, cited Miles "
                f"Ch. 8.3.6). Without urea, 'fixation in 1 min at 150°C' is not "
                f"achievable and colour yields will be poor."
            )

    # Pigment binder check
    if (params.colorant_type == "pigment"
            and params.binder_concentration_pct < 7.0):
        warnings.append(
            f"Pigment print binder concentration ({params.binder_concentration_pct:.1f}%) "
            f"is below the minimum of 7% required for adequate fastness "
            f"(Miles Recipe 5.1). Poor wash and rub fastness will result."
        )

    # Pigment + steam fixation (Miles Ch. 5.2.2, Ch. 8.2)
    if (params.colorant_type == "pigment"
            and params.fixation_method == "saturated_steam"):
        warnings.append(
            "Pigment prints must be fixed with hot air (140–160°C, 3–5 min), "
            "not saturated steam. 'Steam can have adverse effects on crosslinking' "
            "of binder N-methylol groups (Miles Ch. 5.2.2). Use a roller baker "
            "or hot-air curing oven."
        )

    # Disperse dye fixation check (Miles Ch. 8.3.6)
    if (params.colorant_type == "disperse_dye"
            and params.fixation_method == "saturated_steam"
            and params.fixation_temperature_C < 120):
        warnings.append(
            "Disperse dyes on polyester cannot be fixed in saturated steam at "
            "100°C without carrier. Use high-temperature steam at ≥175°C for "
            "1 min, or pressure steam at 120°C for 30 min (Miles Ch. 8.3.6)."
        )

    # Vat dye fixation time (Miles Ch. 8.3.5, Recipe 8.1)
    if (params.colorant_type == "vat_dye"
            and params.fixation_method == "saturated_steam"
            and params.fixation_time_min < 8.0):
        warnings.append(
            f"Vat dye prints require 8–20 min in air-free saturated steam for "
            f"adequate reduction and fixation (Miles Recipe 8.1). Specified "
            f"{params.fixation_time_min:.0f} min is insufficient."
        )

    # Steamer type for high-speed rotary (Miles Ch. 8.3.2)
    if (params.fixation_method == "saturated_steam"
            and params.steamer_type == "star_batch"
            and params.printing_speed_m_per_hour > 1200):
        warnings.append(
            f"A batch star steamer is not suitable for high-speed continuous "
            f"rotary printing at {params.printing_speed_m_per_hour:.0f} m/h. "
            f"A continuous festoon steamer (800 m capacity, 80 m/min throughput) "
            f"is required to match rotary machine output (Miles Ch. 8.3.2)."
        )

    # Festoon steamer speed limit (Miles Ch. 8.3.2: 800 m at 80 m/min = 10 min)
    if (params.steamer_type == "festoon"
            and params.printing_speed_m_per_hour > 4800):  # 80 m/min × 60 = 4800
        warnings.append(
            f"Festoon steamer throughput is limited to ~4800 m/h (80 m/min) for "
            f"10 min steaming time in 800 m capacity machines (Miles Ch. 8.3.2). "
            f"At {params.printing_speed_m_per_hour:.0f} m/h, steaming time will "
            f"be less than 10 min, risking underfixation."
        )

    # Wash-off temperature vs speed (Miles Table 8.2)
    if (params.wash_off_applied
            and params.wash_off_temperature_C < 80
            and params.printing_speed_m_per_hour > 3000):
        warnings.append(
            f"At {params.printing_speed_m_per_hour:.0f} m/h and "
            f"{params.wash_off_stages} wash stages, hot dwell time may be only "
            f"36–60 s (Miles Table 8.2). Wash temperature of "
            f"{params.wash_off_temperature_C:.0f}°C is too low for complete "
            f"hydrolysed dye removal in this time — raise to ≥90°C where "
            f"clearing occurs in 90 s (Miles Fig. 8.12)."
        )

    # Substrate damage risk carried forward
    if fabric.substrate_damage_risk == "high":
        warnings.append(
            "Input fabric: substrate damage risk from dyeing is HIGH. Fabric with "
            "reduced tensile strength may tear at blanket adhesive points under "
            "the tension applied at high printing speeds (Miles Ch. 2.3.1)."
        )

    # Residual unfixed dye from dyeing (Miles Ch. 8.5.3)
    if fabric.residual_unfixed_dye_pct > 5.0:
        warnings.append(
            f"Residual unfixed dye from dyeing stage ({fabric.residual_unfixed_dye_pct:.1f}%) "
            f"is high. This dye will become mobile during steaming and bleed into "
            f"printed areas, causing contamination of white grounds and reduced "
            f"colour definition (Miles Ch. 8.5.3). Improve dyeing wash-off."
        )

    # Maintenance overdue
    maint_ratio = (params.operating_hours_since_maintenance
                   / max(1.0, params.maintenance_interval_hours))
    if maint_ratio > 1.0:
        warnings.append(
            f"Machine is overdue for maintenance ({params.operating_hours_since_maintenance:.0f} h "
            f"since service; interval {params.maintenance_interval_hours:.0f} h). "
            "'Rotary-screen printing machines are expensive, and it therefore pays "
            "to keep downtime to a minimum.' (Miles Ch. 2.4.5). Worn end-ring "
            "bearings, squeegee assemblies, and blanket-drive components will "
            "cause stripe faults, registration errors, and increased stop rate."
        )

    # ── RUN SIMULATION MODELS ────────────────────────────────────────────

    paste_volume = predict_paste_volume_applied(
        params.screen_open_area_pct,
        params.screen_mesh_holes_per_inch,
        params.squeegee_type,
        params.squeegee_pressure_setting,
        params.squeegee_blade_curvature,
        fabric.fabric_surface_texture,
        fabric.fabric_weight_g_per_m2,
        params.paste_viscosity_Pa_s,
        params.printing_speed_m_per_hour
    )

    penetration = predict_paste_penetration(
        paste_volume,
        params.paste_viscosity_Pa_s,
        params.paste_yield_value,
        fabric.fabric_cover_factor,
        fabric.fabric_surface_texture,
        params.printing_speed_m_per_hour
    )

    sharpness = predict_sharpness_of_mark(
        params.paste_viscosity_Pa_s,
        params.paste_yield_value,
        params.screen_mesh_holes_per_inch,
        params.thickener_type,
        fabric.fabric_surface_texture,
        params.printing_speed_m_per_hour,
        params.design_coverage_pct
    )

    saw_tooth = predict_saw_tooth_risk(
        params.screen_mesh_holes_per_inch,
        params.design_coverage_pct
    )

    stripe_risk = predict_stripe_fault_risk(
        params.squeegee_type,
        params.squeegee_pressure_setting,
        params.screen_working_width_cm,
        fabric.fabric_width_cm,
        params.paste_viscosity_Pa_s,
        params.operating_hours_since_maintenance,
        params.maintenance_interval_hours
    )

    crushing_risk = predict_colour_crushing_risk(
        params.number_of_screens,
        params.printing_speed_m_per_hour,
        params.colorant_type
    )

    paste_level_risk = predict_paste_level_instability_risk(
        params.level_control_type,
        params.paste_pump_type,
        params.paste_distribution_quality,
        params.paste_viscosity_Pa_s,
        params.design_coverage_pct
    )

    creasing_risk = predict_screen_creasing_risk(
        params.screen_type,
        params.screen_wall_thickness_mm,
        params.squeegee_pressure_setting,
        params.squeegee_type,
        params.screen_working_width_cm
    )

    registration = predict_registration_accuracy(
        params.independent_screen_speed_control,
        params.laser_registration,
        params.number_of_screens,
        params.adhesive_type,
        params.blanket_type,
        params.printing_speed_m_per_hour,
        params.operating_hours_since_maintenance,
        params.maintenance_interval_hours
    )

    repeat_fit = predict_repeat_fitting_quality(
        params.screen_circumference_mm,
        params.design_repeat_length_cm
    )

    fixation_pct = predict_fixation_pct(
        params.colorant_type,
        fabric.fiber_type,
        params.fixation_method,
        params.fixation_temperature_C,
        params.fixation_time_min,
        params.urea_concentration_g_per_kg,
        params.alkali_type,
        params.alkali_concentration_g_per_kg,
        penetration,
        params.steamer_type
    )

    wash_fastness = predict_wash_fastness(
        params.colorant_type,
        fabric.fiber_type,
        fixation_pct,
        params.wash_off_applied,
        params.wash_off_temperature_C,
        params.wash_off_stages,
        params.counterflow_washing,
        penetration,
        params.binder_concentration_pct
    )

    light_fastness = predict_light_fastness(
        params.colorant_type,
        fabric.fiber_type,
        params.paste_colorant_conc_g_per_kg,
        fixation_pct
    )

    dry_rub, wet_rub = predict_rub_fastness(
        params.colorant_type,
        penetration,
        params.binder_concentration_pct,
        fixation_pct,
        params.design_coverage_pct
    )

    colour_yield_rel = predict_colour_yield(
        params.colorant_type,
        params.thickener_type,
        params.paste_colorant_conc_g_per_kg,
        fixation_pct,
        penetration
    )
    colour_yield_pct = round(colour_yield_rel * 100.0, 1)

    unfixed_stain_risk = predict_unfixed_staining_risk(
        params.colorant_type,
        fixation_pct,
        params.wash_off_applied,
        params.wash_off_temperature_C,
        params.wash_off_stages,
        params.counterflow_washing,
        fabric.residual_unfixed_dye_pct
    )

    binder_quality = predict_binder_crosslink_quality(
        params.colorant_type,
        params.binder_concentration_pct,
        params.fixation_method,
        params.fixation_temperature_C,
        params.fixation_time_min,
        params.alkali_type
    )

    # Water consumption
    if not params.wash_off_applied:
        print_water = 0.0
    else:
        # Miles Table 8.2: 8-box range; simplified 5 L/kg per stage
        # Counterflow reduces water per stage by ~30%
        water_per_stage = 4.0 if params.counterflow_washing else 5.5
        print_water = water_per_stage * params.wash_off_stages
    total_water = round(fabric.upstream_water_L_per_kg + print_water, 1)

    # Effluent dye load
    print_unfixed = 100.0 - fixation_pct if params.colorant_type != "pigment" else 0.0
    total_effluent = round(
        (100.0 - fabric.dye_fixation_pct) / 100.0 * 50.0 + print_unfixed * 0.5, 1
    )

    # Energy index
    if params.colorant_type == "pigment":
        energy_index = 0.6   # no steaming, no wash-off
    elif params.fixation_method == "high_temp_steam":
        energy_index = 1.25  # HT steamers energy-intensive
    else:
        energy_index = 1.0

    machine_efficiency = predict_machine_efficiency(
        params.printing_speed_m_per_hour,
        params.number_of_screens,
        params.dryer_capacity,
        params.design_coverage_pct,
        params.colorant_type,
        params.independent_screen_speed_control,
        params.laser_registration,
        params.operating_hours_since_maintenance,
        params.maintenance_interval_hours
    )

    effective_production = round(
        params.printing_speed_m_per_hour * machine_efficiency / 100.0, 1
    )

    # ── POST-SIMULATION WARNINGS ─────────────────────────────────────────

    if sharpness == "poor":
        warnings.append(
            "Sharpness of mark is POOR. Capillary spread is dominating the "
            "paste movement. At rotary printing speeds the contact time is very "
            "short — increase paste viscosity, use a short-flow synthetic "
            "polyacrylic thickener, or increase printing speed further to reduce "
            "lateral spread time (Miles Ch. 7.7.5)."
        )

    if stripe_risk == "high":
        warnings.append(
            "Longitudinal stripe fault risk is HIGH. Uneven squeegee pressure "
            "across the fabric width will produce visible colour depth variation "
            "along the printing direction. Calibrate squeegee bearings, reduce "
            "squeegee pressure, or switch to an airflow (air-sack) squeegee for "
            "uniform pressure (Miles Ch. 2.4.1)."
        )

    if fixation_pct < 60:
        warnings.append(
            f"CRITICAL: Estimated fixation is only {fixation_pct:.0f}%. Most of the "
            f"applied colorant will be washed off, producing weak colours, heavy "
            f"effluent dye load, and high staining risk. Review fixation conditions "
            f"immediately (temperature, time, alkali, urea, steamer type)."
        )

    if paste_level_risk == "high":
        warnings.append(
            "Paste level instability risk is HIGH. Variable paste level inside "
            "the rotating screen will produce unlevel printing (colour depth "
            "variation across the fabric length). Install automatic sensor-based "
            "level control and verify internal pipe hole sizing is graduated "
            "correctly (larger holes at far end from pump, Miles Ch. 2.4)."
        )

    if creasing_risk == "high":
        warnings.append(
            "Screen creasing risk is HIGH. The combination of thin nickel walls "
            "and high squeegee pressure may permanently deform the screen. "
            "Reduce squeegee pressure, use a steel blade instead of magnetic rod, "
            "or switch to galvano screens with thicker walls for this application "
            "(Miles Ch. 2.4.1)."
        )

    if repeat_fit == "poor":
        warnings.append(
            "Design repeat fitting quality is POOR. The repeat length does not "
            "divide evenly into the screen circumference — a visible join line "
            "will appear across the fabric at every screen revolution. Select a "
            "repeat that is a whole-number fraction of the circumference (e.g. for "
            "64 cm circumference: 64, 32, 21.3, 16 cm, etc.) or choose a different "
            "screen circumference (Miles Ch. 2.5.4)."
        )

    if unfixed_stain_risk == "high":
        warnings.append(
            "Unfixed dye staining risk is HIGH. Raise wash-off temperature to "
            "≥90°C (clears reactive dye in 90 s vs >4 min at 60°C, Miles "
            "Fig. 8.12), increase number of wash stages, and implement counterflow "
            "washing. At very high printing speeds ensure the wash range provides "
            "adequate dwell time (Miles Table 8.2)."
        )

    return RotaryPrintedFabricOutput(
        paste_volume_applied_g_per_m2=paste_volume,
        paste_penetration_depth=penetration,
        colour_yield_pct=colour_yield_pct,
        sharpness_of_mark=sharpness,
        saw_tooth_risk=saw_tooth,
        registration_accuracy=registration,
        stripe_fault_risk=stripe_risk,
        colour_crushing_risk=crushing_risk,
        paste_level_instability_risk=paste_level_risk,
        screen_creasing_risk=creasing_risk,
        repeat_fitting_quality=repeat_fit,
        print_wash_fastness=wash_fastness,
        print_light_fastness=light_fastness,
        print_rub_fastness_dry=dry_rub,
        print_rub_fastness_wet=wet_rub,
        colour_yield_relative=colour_yield_rel,
        estimated_fixation_pct=fixation_pct,
        unfixed_dye_staining_risk=unfixed_stain_risk,
        binder_crosslink_quality=binder_quality,
        total_water_L_per_kg=total_water,
        total_effluent_dye_load_pct=total_effluent,
        energy_index=energy_index,
        effective_production_m_per_hour=effective_production,
        machine_efficiency_pct=machine_efficiency,
        warnings=warnings
    )


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE USAGE AND VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    print("=" * 72)
    print("ROTARY SCREEN PRINTING SIMULATION")
    print("Based on Miles, L.W.C. (Ed.), Textile Printing, SDC, 2003")
    print("=" * 72)

    # ── SCENARIO 1: High-speed reactive dye print on cotton, lacquer screen ──
    # Optimally configured standard production run.
    print("\n--- SCENARIO 1: Reactive 12-colour on cotton — standard rotary, 40 m/min ---\n")

    fabric_1 = InputDyedFabric(
        fiber_type="cotton",
        fabric_weight_g_per_m2=130.0,
        fabric_cover_factor=0.92,
        fabric_width_cm=152.0,
        fabric_surface_texture="smooth",
        substrate_pH=7.2,
        dye_exhaustion_pct=82.0,
        dye_fixation_pct=74.0,
        unfixed_hydrolysed_dye_pct=8.0,
        residual_unfixed_dye_pct=2.0,
        ground_colour_yield=0.78,
        ground_wash_fastness=4.5,
        ground_light_fastness=6.0,
        ground_levelness_risk="low",
        ground_dye_penetration="full",
        upstream_water_L_per_kg=38.0,
        upstream_salt_g_per_kg=65.0,
        substrate_damage_risk="low",
    )

    params_1 = RotaryPrintingOperationalParams(
        printing_speed_m_per_hour=2400.0,   # 40 m/min — standard rotary
        screen_working_width_cm=165.0,
        number_of_screens=12,
        screen_type="lacquer_rotary",
        screen_mesh_holes_per_inch=60,       # standard blotch/motif mesh
        screen_open_area_pct=11.0,           # standard lacquer inside measure
        screen_wall_thickness_mm=0.09,
        screen_circumference_mm=640.0,       # standard circumference
        design_repeat_length_cm=32.0,        # 2 per revolution: 640/10/2 = 32 ✓
        squeegee_type="steel_blade",
        squeegee_blade_length_mm=1700.0,
        squeegee_pressure_setting="medium",
        squeegee_blade_curvature="standard",
        blanket_type="laminated_neoprene",
        adhesive_type="thermoplastic",
        independent_screen_speed_control=True,   # Stork/Zimmer stepper motors
        laser_registration=True,                 # MBK laser system
        paste_pump_type="peristaltic",
        level_control_type="sensor_automatic",
        paste_distribution_quality="uniform",
        colorant_type="reactive_dye",
        paste_colorant_conc_g_per_kg=45.0,
        thickener_type="alginate",
        thickener_concentration_pct=3.5,
        paste_viscosity_Pa_s=1.8,
        paste_yield_value="long_flow",           # alginate: near-Newtonian
        binder_concentration_pct=0.0,
        urea_concentration_g_per_kg=120.0,
        alkali_type="sodium_bicarbonate",
        alkali_concentration_g_per_kg=20.0,
        design_coverage_pct=40.0,
        fixation_method="saturated_steam",
        fixation_temperature_C=102.0,
        fixation_time_min=10.0,
        steamer_type="festoon",
        dryer_capacity="high",
        wash_off_applied=True,
        wash_off_temperature_C=92.0,
        wash_off_stages=8,
        counterflow_washing=True,
        ambient_temperature_C=24.0,
        ambient_humidity_pct=62.0,
        last_maintenance_date="2025-10-01",
        maintenance_interval_hours=1500.0,
        operating_hours_since_maintenance=400.0,
    )

    r1 = simulate_rotary_printing(fabric_1, params_1)

    print(f"  Paste Volume Applied:         {r1.paste_volume_applied_g_per_m2} g/m²")
    print(f"  Paste Penetration:            {r1.paste_penetration_depth.upper()}")
    print(f"  Colour Yield:                 {r1.colour_yield_pct}%")
    print(f"  Sharpness of Mark:            {r1.sharpness_of_mark.upper()}")
    print(f"  Saw-Tooth Risk:               {r1.saw_tooth_risk.upper()}")
    print(f"  Registration Accuracy:        {r1.registration_accuracy.upper()}")
    print(f"  Repeat Fitting:               {r1.repeat_fitting_quality.upper()}")
    print(f"  Stripe Fault Risk:            {r1.stripe_fault_risk.upper()}")
    print(f"  Colour Crushing Risk:         {r1.colour_crushing_risk.upper()}")
    print(f"  Paste Level Stability:        {r1.paste_level_instability_risk.upper()}")
    print(f"  Screen Creasing Risk:         {r1.screen_creasing_risk.upper()}")
    print(f"  Estimated Fixation:           {r1.estimated_fixation_pct}%")
    print(f"  Wash Fastness (ISO):          {r1.print_wash_fastness} / 5")
    print(f"  Light Fastness (ISO):         {r1.print_light_fastness} / 8")
    print(f"  Rub Fastness Dry/Wet:         {r1.print_rub_fastness_dry} / {r1.print_rub_fastness_wet}")
    print(f"  Unfixed Dye Staining Risk:    {r1.unfixed_dye_staining_risk.upper()}")
    print(f"  Total Water Used:             {r1.total_water_L_per_kg} L/kg")
    print(f"  Machine Efficiency:           {r1.machine_efficiency_pct}%")
    print(f"  Effective Production:         {r1.effective_production_m_per_hour} m/h")
    if r1.warnings:
        print(f"\n  WARNINGS:")
        for w in r1.warnings:
            print(f"    ⚠  {w}")
    else:
        print("\n  No warnings — all parameters within recommended ranges.")

    # ── SCENARIO 2: Pigment print on PES/CO blend, galvano screens, 60 m/min ─
    # High-speed pigment production: no steaming needed, continuous output.
    print("\n--- SCENARIO 2: Pigment 8-colour on PES/CO — galvano screens, 60 m/min ---\n")

    fabric_2 = InputDyedFabric(
        fiber_type="blend_PES_CO",
        fabric_weight_g_per_m2=110.0,
        fabric_cover_factor=0.88,
        fabric_width_cm=150.0,
        fabric_surface_texture="smooth",
        substrate_pH=7.0,
        dye_exhaustion_pct=0.0,            # undyed ecru ground
        dye_fixation_pct=0.0,
        unfixed_hydrolysed_dye_pct=0.0,
        residual_unfixed_dye_pct=0.0,
        ground_colour_yield=0.0,
        ground_wash_fastness=5.0,
        ground_light_fastness=8.0,
        ground_levelness_risk="low",
        ground_dye_penetration="full",
        upstream_water_L_per_kg=4.0,       # scouring water only
        upstream_salt_g_per_kg=0.0,
        substrate_damage_risk="low",
    )

    params_2 = RotaryPrintingOperationalParams(
        printing_speed_m_per_hour=3600.0,   # 60 m/min — high speed
        screen_working_width_cm=170.0,
        number_of_screens=8,
        screen_type="galvano_rotary",
        screen_mesh_holes_per_inch=60,
        screen_open_area_pct=12.0,
        screen_wall_thickness_mm=0.12,      # slightly thicker galvano walls
        screen_circumference_mm=640.0,
        design_repeat_length_cm=64.0,       # 1 per revolution ✓
        squeegee_type="airflow_rod",         # even pressure for wide fabric
        squeegee_blade_length_mm=1800.0,
        squeegee_pressure_setting="medium",
        squeegee_blade_curvature="standard",
        blanket_type="low_extensibility_synthetic",
        adhesive_type="thermoplastic",
        independent_screen_speed_control=True,
        laser_registration=True,
        paste_pump_type="peristaltic",
        level_control_type="sensor_automatic",
        paste_distribution_quality="uniform",
        colorant_type="pigment",
        paste_colorant_conc_g_per_kg=70.0,
        thickener_type="synthetic_polyacrylic",  # best for pigment at high speed
        thickener_concentration_pct=1.0,
        paste_viscosity_Pa_s=2.5,
        paste_yield_value="short_flow",      # synthetic polyacrylic has yield value
        binder_concentration_pct=10.0,
        urea_concentration_g_per_kg=10.0,
        alkali_type="diammonium_phosphate",
        alkali_concentration_g_per_kg=10.0,
        design_coverage_pct=45.0,
        fixation_method="baking_hot_air",
        fixation_temperature_C=152.0,
        fixation_time_min=4.0,
        steamer_type="roller_baker",
        dryer_capacity="high",
        wash_off_applied=False,             # pigment: no wash-off required
        wash_off_temperature_C=0.0,
        wash_off_stages=0,
        counterflow_washing=False,
        ambient_temperature_C=23.0,
        ambient_humidity_pct=58.0,
        last_maintenance_date="2025-09-15",
        maintenance_interval_hours=1200.0,
        operating_hours_since_maintenance=350.0,
    )

    r2 = simulate_rotary_printing(fabric_2, params_2)

    print(f"  Paste Volume Applied:         {r2.paste_volume_applied_g_per_m2} g/m²")
    print(f"  Colour Yield:                 {r2.colour_yield_pct}%")
    print(f"  Sharpness of Mark:            {r2.sharpness_of_mark.upper()}")
    print(f"  Registration Accuracy:        {r2.registration_accuracy.upper()}")
    print(f"  Stripe Fault Risk:            {r2.stripe_fault_risk.upper()}")
    print(f"  Screen Creasing Risk:         {r2.screen_creasing_risk.upper()}")
    print(f"  Estimated Fixation:           {r2.estimated_fixation_pct}%")
    print(f"  Binder Crosslink Quality:     {r2.binder_crosslink_quality.upper()}")
    print(f"  Wash Fastness (ISO):          {r2.print_wash_fastness} / 5")
    print(f"  Light Fastness (ISO):         {r2.print_light_fastness} / 8")
    print(f"  Rub Fastness Dry/Wet:         {r2.print_rub_fastness_dry} / {r2.print_rub_fastness_wet}")
    print(f"  Total Water Used:             {r2.total_water_L_per_kg} L/kg")
    print(f"  Energy Index:                 {r2.energy_index} (vs 1.0 conventional)")
    print(f"  Machine Efficiency:           {r2.machine_efficiency_pct}%")
    print(f"  Effective Production:         {r2.effective_production_m_per_hour} m/h")
    if r2.warnings:
        print(f"\n  WARNINGS:")
        for w in r2.warnings:
            print(f"    ⚠  {w}")
    else:
        print("\n  No warnings — all parameters within recommended ranges.")

    # ── SCENARIO 3: Stress test — multiple critical faults ───────────────────
    # Wrong repeat, magnetic rod on thin screen, no alkali, bad repeat fit.
    print("\n--- SCENARIO 3: Stress test — misconfigured rotary print ---\n")

    fabric_3 = InputDyedFabric(
        fiber_type="cotton",
        fabric_weight_g_per_m2=140.0,
        fabric_cover_factor=0.95,
        fabric_width_cm=180.0,             # wider than screen!
        fabric_surface_texture="textured",
        substrate_pH=9.5,                  # residual alkali from dyeing
        dye_exhaustion_pct=70.0,
        dye_fixation_pct=55.0,
        unfixed_hydrolysed_dye_pct=15.0,   # poor dyeing wash-off
        residual_unfixed_dye_pct=8.0,
        ground_colour_yield=0.60,
        ground_wash_fastness=3.5,
        ground_light_fastness=5.5,
        ground_levelness_risk="high",
        ground_dye_penetration="partial",
        upstream_water_L_per_kg=55.0,
        upstream_salt_g_per_kg=90.0,
        substrate_damage_risk="high",
    )

    params_3 = RotaryPrintingOperationalParams(
        printing_speed_m_per_hour=4800.0,   # exceeds dryer capacity
        screen_working_width_cm=165.0,      # narrower than fabric!
        number_of_screens=20,
        screen_type="lacquer_rotary",
        screen_mesh_holes_per_inch=120,     # exceeds lacquer limit of 100!
        screen_open_area_pct=11.0,
        screen_wall_thickness_mm=0.08,      # thinnest lacquer walls
        screen_circumference_mm=640.0,
        design_repeat_length_cm=25.0,       # 640/10/25 = 2.56 — not whole number!
        squeegee_type="magnetic_rod",       # risky with thin screens
        squeegee_blade_length_mm=1800.0,
        squeegee_pressure_setting="high",
        squeegee_blade_curvature="shallow", # extra paste (but blotch issues)
        blanket_type="neoprene_rubber",     # higher extensibility → slip
        adhesive_type="water_based",        # inconsistent tack at high speed
        independent_screen_speed_control=False,
        laser_registration=False,
        paste_pump_type="gear",
        level_control_type="manual",        # operator-dependent
        paste_distribution_quality="variable",
        colorant_type="reactive_dye",
        paste_colorant_conc_g_per_kg=80.0,
        thickener_type="starch_ether",      # WRONG for reactive dyes!
        thickener_concentration_pct=8.0,
        paste_viscosity_Pa_s=0.4,           # too thin → bleeding
        paste_yield_value="long_flow",
        binder_concentration_pct=0.0,
        urea_concentration_g_per_kg=200.0,
        alkali_type="none",                 # NO ALKALI → zero fixation!
        alkali_concentration_g_per_kg=0.0,
        design_coverage_pct=80.0,           # heavy blotch
        fixation_method="saturated_steam",
        fixation_temperature_C=102.0,
        fixation_time_min=3.0,              # too short for reactive
        steamer_type="star_batch",          # wrong steamer for high-speed rotary!
        dryer_capacity="low",
        wash_off_applied=False,             # no wash-off applied
        wash_off_temperature_C=0.0,
        wash_off_stages=0,
        counterflow_washing=False,
        ambient_temperature_C=32.0,
        ambient_humidity_pct=30.0,          # too dry → paste stability issues
        last_maintenance_date="2023-01-01",
        maintenance_interval_hours=800.0,
        operating_hours_since_maintenance=2000.0,  # severely overdue
    )

    r3 = simulate_rotary_printing(fabric_3, params_3)

    print(f"  Paste Volume Applied:         {r3.paste_volume_applied_g_per_m2} g/m²")
    print(f"  Paste Penetration:            {r3.paste_penetration_depth.upper()}")
    print(f"  Sharpness of Mark:            {r3.sharpness_of_mark.upper()}")
    print(f"  Repeat Fitting:               {r3.repeat_fitting_quality.upper()}")
    print(f"  Registration Accuracy:        {r3.registration_accuracy.upper()}")
    print(f"  Stripe Fault Risk:            {r3.stripe_fault_risk.upper()}")
    print(f"  Screen Creasing Risk:         {r3.screen_creasing_risk.upper()}")
    print(f"  Paste Level Stability:        {r3.paste_level_instability_risk.upper()}")
    print(f"  Estimated Fixation:           {r3.estimated_fixation_pct}%")
    print(f"  Wash Fastness (ISO):          {r3.print_wash_fastness} / 5")
    print(f"  Unfixed Dye Staining Risk:    {r3.unfixed_dye_staining_risk.upper()}")
    print(f"  Machine Efficiency:           {r3.machine_efficiency_pct}%")
    print(f"  Effective Production:         {r3.effective_production_m_per_hour} m/h")
    if r3.warnings:
        print(f"\n  WARNINGS ({len(r3.warnings)} issues detected):")
        for w in r3.warnings:
            print(f"    ⚠  {w}")

    print("\n" + "=" * 72)
    print("Simulation complete.")
    print("=" * 72)
