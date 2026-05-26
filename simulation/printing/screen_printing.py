"""
Screen Printing Simulation Module
Process: Printing > Screen Printing

Layer 1 — Machine Identity
    Type            : Screen Printing Machine
    Subprocess      : Screen Printing (Flat-screen and Rotary-screen variants)
    Technology      : A viscous print paste is forced through open areas of a
                      photopatterned screen (flat mesh or seamless electroformed
                      nickel cylinder) onto the fabric surface using a squeegee
                      (rubber blade, steel blade, or magnetic rod). One screen
                      per colour in the design. The fabric is held on an endless
                      blanket by adhesive during printing, then passed through a
                      dryer before steam fixation and wash-off.
    Machine classes :
        Hand / Semi-automatic flat-screen  : fabric stationary on table; one
            colour printed at a time; speeds 50–150 m/h; used for small runs,
            high-fashion, silk.
        Fully automatic flat-screen        : all colours printed simultaneously
            while fabric is stationary; then blanket advances one repeat;
            intermittent motion; speeds 300–600 m/h; furnishing fabrics,
            large repeats.
        Rotary-screen (cylindrical nickel screen) : continuous fabric and screen
            rotation; speeds 1 800–4 200 m/h (30–70 m/min); dominant
            worldwide method; standard screen circumference 640 mm.
    Squeegee types  : double-blade rubber, stainless-steel blade, magnetic rod
                      (Zimmer), Airflow (Stork). Rod squeegee applies more
                      paste than blade.
    Screen types    : Flat polyester mesh (19–100 threads/cm); lacquer rotary
                      (60–80 mesh, 9–13% open area); galvano rotary (up to
                      80 mesh, stronger walls, 0.35 mm thick for carpets).
    Colorant scope  : Pigment (>50% of all textile prints), reactive dyes on
                      cellulosics, disperse dyes on polyester, acid dyes on
                      nylon/wool, vat dyes, azoic colorants, discharge pastes.

All parameter relationships derived from:
    Miles, L.W.C. (Ed.), "Textile Printing", Revised 2nd Edition, Society of
    Dyers and Colourists, Bradford, 2003.
    Chapters 2 (Screen Printing), 5 (Direct Print Coloration),
    7 (Print Paste Properties), 8 (Fixation and Aftertreatment).

Layer 5: Interdependency and behaviour simulation functions.
These functions take the dyed fabric input (Layer 2) and machine / paste
operational parameters (Layer 3), and predict printed fabric quality metrics
(Layer 4).

Layer 2 note:
    Printing input = Colouring (dyeing) output.
    The InputDyedFabric dataclass mirrors DyedFabricOutput from the reactive
    dyeing simulation (and analogous dyeing subprocess modules), using the
    fields that are physically meaningful at the printing stage:

        dyeing.DyedFabricOutput          →  printing.InputDyedFabric
        ─────────────────────────────────────────────────────────────
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
        warnings (passed through)        →  upstream_warnings

    Additional substrate identity fields required at the printing stage:
        fiber_type, fabric_weight_g_per_m2, fabric_cover_factor,
        fabric_width_cm, fabric_surface_texture
"""

import math
from dataclasses import dataclass
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# DATA CLASSES — Layers 2, 3, and 4
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class InputDyedFabric:
    """
    Layer 2 — Input dyed fabric properties for Screen Printing.

    These fields correspond directly to Layer 4 (DyedFabricOutput) of the
    reactive dyeing (or other colouring) subprocess simulation.
    """
    # ── SUBSTRATE IDENTITY ──────────────────────────────────────────────────
    fiber_type: str                     # "cotton", "polyester", "nylon",
                                        # "blend_PES_CO", "viscose", "wool",
                                        # "silk", "acrylic"
    fabric_weight_g_per_m2: float       # Fabric weight in g/m². Affects paste
                                        # uptake volume and penetration depth.
    fabric_cover_factor: float          # Cover factor (0–2). Dense fabrics
                                        # (high cover) restrict paste penetration.
    fabric_width_cm: float              # Fabric width in cm. Determines screen
                                        # width requirement and blanket width.
    fabric_surface_texture: str         # "smooth", "textured", or "pile".
                                        # Smooth fabrics need finer-mesh screens
                                        # and less paste; pile needs coarser mesh
                                        # and multiple squeegee passes
                                        # (Miles Ch. 2.3.4).

    # ── DYE BATH EQUILIBRIUM (from dyeing Layer 4) ──────────────────────────
    substrate_pH: float                 # Fabric pH after dyeing and washing.
                                        # Residual alkali or acid affects
                                        # discharge-resist compatibility and
                                        # binder crosslinking in pigment printing.
    dye_exhaustion_pct: float           # % of dye taken up by fabric during dyeing.
    dye_fixation_pct: float             # % of applied dye covalently bonded
                                        # (reactive) or permanently fixed.
    unfixed_hydrolysed_dye_pct: float   # % of hydrolysed reactive dye that
                                        # was not washed off — can interfere with
                                        # discharge printing and reduce discharge
                                        # crispness (Miles Ch. 6.2).
    residual_unfixed_dye_pct: float     # % of physically adsorbed, unfixed dye
                                        # still on fabric — risk of bleeding into
                                        # white printed areas (Miles Ch. 8.5.3).

    # ── SHADE AND FASTNESS (from dyeing Layer 4) ────────────────────────────
    ground_colour_yield: float          # Relative ground colour yield (0–1).
                                        # Low yield → pale ground → fall-on
                                        # colours may dominate visually.
    ground_wash_fastness: float         # ISO wash fastness of ground (1–5).
                                        # Affects colour matching and fastness of
                                        # final printed article.
    ground_light_fastness: float        # ISO light fastness of ground (1–8).
    ground_levelness_risk: str          # "low", "medium", "high" — uneven ground
                                        # dyeing will make print look unlevel.
    ground_dye_penetration: str         # "full", "partial", "surface_only" —
                                        # surface-only dyeing → sharp demarcation
                                        # between printed and ground areas.

    # ── SUSTAINABILITY METRICS (from dyeing Layer 4) ────────────────────────
    upstream_water_L_per_kg: float      # Water used in dyeing (L/kg fabric).
    upstream_salt_g_per_kg: float       # Salt discharged in dyeing (g/kg fabric).

    # ── RISK FLAGS (from dyeing Layer 4) ────────────────────────────────────
    substrate_damage_risk: str          # "low", "medium", "high" — fabric damage
                                        # from dyeing alkali / temperature.
                                        # Damaged fabric has reduced tensile
                                        # strength → tears on blanket adhesive
                                        # tension. (Miles Ch. 2.3.1)


@dataclass
class ScreenPrintingOperationalParams:
    """
    Layer 3 — Operational parameters for Screen Printing.

    Source: Miles, Textile Printing (2003), Ch. 2 and 7.
    """
    # ── MACHINE TYPE AND SPEED ───────────────────────────────────────────────
    machine_type: str                   # "hand", "semi_automatic_flat",
                                        # "automatic_flat", or "rotary".
    printing_speed_m_per_hour: float    # Fabric speed in m/h.
                                        # Hand/semi-auto: 50–200 m/h.
                                        # Automatic flat: 300–600 m/h.
                                        # Rotary: 1800–4200 m/h (30–70 m/min).
                                        # Miles Ch. 2.3.4: "typically 30–70 m/min".
    number_of_colours: int              # Number of screens in the design.
                                        # One screen per colour (Miles Ch. 2.2).
                                        # Flat auto: up to 15 screens;
                                        # Rotary: up to 20+ screens.

    # ── SCREEN SPECIFICATION ─────────────────────────────────────────────────
    screen_type: str                    # "flat_polyester_mesh", "lacquer_rotary",
                                        # or "galvano_rotary".
    screen_mesh_threads_per_cm: float   # Screen fabric count (threads/cm).
                                        # Table 2.1: Terry towelling 19–34;
                                        # Large blotches 43–49; Small motifs 49–62;
                                        # Fine details 55–100 threads/cm.
    screen_open_area_pct: float         # % open area of screen.
                                        # Coarser mesh → more open → more paste.
                                        # Table 2.1: range 27–47%.
                                        # Lacquer rotary: 9–13% (inside measure).
    screen_circumference_mm: float      # For rotary screens only. Standard: 640 mm.
                                        # Other standards: 518, 537, 668, 725,
                                        # 801, 914 mm (Miles Ch. 2.4.4).
                                        # Set to 0 for flat screens.
    design_repeat_length_cm: float      # Length of one design repeat in cm.
                                        # Must divide evenly into screen
                                        # circumference for rotary printing.

    # ── SQUEEGEE SPECIFICATION ───────────────────────────────────────────────
    squeegee_type: str                  # "rubber_blade", "steel_blade",
                                        # "magnetic_rod", or "airflow_rod".
                                        # Rod squeegee applies more paste than blade
                                        # (Miles Ch. 2.4.1, Ch. 2.8.1).
    squeegee_angle_deg: float           # Squeegee blade angle in degrees.
                                        # Smaller angle → higher hydrodynamic
                                        # pressure → more paste applied
                                        # (Miles Ch. 2.8.1). Typical: 60–80°.
    squeegee_hardness_shore: int        # Shore A hardness. Hard (70–80 Shore):
                                        # fine outlines; Soft (50–60 Shore):
                                        # blotches (Miles Ch. 2.2).
    number_of_squeegee_passes: int      # Passes per screen per repeat.
                                        # 1 for rotary (continuous); 1–4 for flat.
                                        # More passes → more paste → better
                                        # penetration on thick fabrics
                                        # (Miles Ch. 2.3.4).
    flood_stroke: bool                  # True if a flood stroke fills the screen
                                        # mesh before the printing stroke.
                                        # Improves colour uniformity in blotch areas
                                        # (Miles Ch. 2.3.4).

    # ── BLANKET AND ADHESIVE ─────────────────────────────────────────────────
    adhesive_type: str                  # "water_based", "thermoplastic",
                                        # or "semi_permanent".
                                        # Thermoplastic: serviceable for hundreds
                                        # of thousands of metres (Miles Ch. 2.3.1).
    blanket_type: str                   # "neoprene_rubber", "laminated_neoprene",
                                        # or "metal_strip_edge".
    off_contact_printing: bool          # True if screen is raised slightly above
                                        # blanket during print stroke.
                                        # Reduces frame marks and colour crushing
                                        # (Miles Ch. 2.3.5).

    # ── PRINT PASTE FORMULATION ──────────────────────────────────────────────
    colorant_type: str                  # "pigment", "reactive_dye",
                                        # "disperse_dye", "acid_dye", "vat_dye",
                                        # "azoic", or "discharge".
    paste_colorant_concentration_g_per_kg: float  # Colorant (dye or pigment) in
                                        # g per kg of print paste.
                                        # Pigment paste: 1–200 g/kg (Miles 5.2.4).
                                        # Reactive dye: 10–100 g/kg typical.
    thickener_type: str                 # "alginate", "starch_ether",
                                        # "guar_locust_bean", "emulsion_o_in_w",
                                        # "synthetic_polyacrylic", "crystal_gum",
                                        # or "half_emulsion".
                                        # Alginate: essential for reactive dyes
                                        # (Miles 5.3.5); Crystal gum: sharp
                                        # outlines; Emulsion: no stiff film;
                                        # Polyacrylic: electrolyte-sensitive.
    thickener_concentration_pct: float  # % of thickening agent in paste stock.
                                        # Alginate: 2–6%; Guar: 2%; Starch ether
                                        # 6%; Synthetic: 1% (Miles Ch. 7).
    paste_viscosity_Pa_s: float         # Print paste viscosity in Pa·s at working
                                        # shear. Typical: 0.5–5 Pa·s.
                                        # Pseudoplastic (shear-thinning) behaviour:
                                        # viscosity drops under squeegee pressure
                                        # (Miles Ch. 7.7.3).
    binder_concentration_pct: float     # % binder in paste (for pigment printing).
                                        # Recipe 5.1: minimum 7% (Miles 5.2.4);
                                        # 0.0 for dye-based pastes.
    urea_concentration_g_per_kg: float  # Urea (g/kg paste). Improves dye solution
                                        # and maintains moisture in HT steam.
                                        # Reactive on cellulose: 100–200 g/kg;
                                        # Disperse on polyester: 0–50 g/kg
                                        # (Miles Ch. 5.3.5, 5.4.3, 8.3.6).
    alkali_type: str                    # "sodium_bicarbonate", "sodium_carbonate",
                                        # "caustic_soda", "ammonium_sulphate",
                                        # "none", or "diammonium_phosphate".
    alkali_concentration_g_per_kg: float  # Alkali (g/kg paste).
                                        # Reactive/cotton: NaHCO3 20 g/kg typical
                                        # (Miles Recipe 5.2). 0.0 for pigment.
    design_coverage_pct: float          # % of fabric area printed (design cover).
                                        # Low cover (<30%): suitable for pigment;
                                        # High cover (>70%, blotch): needs efficient
                                        # dryer and may cause frame marks
                                        # (Miles Ch. 2.3.4, 5.2.5).

    # ── FIXATION PARAMETERS ──────────────────────────────────────────────────
    fixation_method: str                # "baking_hot_air", "saturated_steam",
                                        # "high_temp_steam", "pressure_steam",
                                        # or "none_pigment_curing".
                                        # Reactive/cotton: saturated steam 100°C,
                                        # 10 min or HT steam 150°C, 1 min.
                                        # Pigment: hot air 140–160°C, 3–5 min
                                        # (Miles Ch. 8.2, 8.3.5, 8.3.6).
    fixation_temperature_C: float       # Fixation temperature in °C.
    fixation_time_min: float            # Fixation duration in minutes.
    dryer_efficiency: str               # "high", "adequate", or "low".
                                        # Low efficiency → must reduce printing
                                        # speed (Miles Ch. 2.3.4).

    # ── WASH-OFF ─────────────────────────────────────────────────────────────
    wash_off_applied: bool              # True for dye-based prints; False for
                                        # pigment (normally no wash-off needed).
    wash_off_temperature_C: float       # Wash-off water temperature in °C.
                                        # Reactive dyes: 90°C removes hydrolysed
                                        # dye in 90 s vs >4 min at 60°C
                                        # (Miles Fig. 8.12, Table 8.2).
    wash_off_stages: int                # Number of wash boxes/baths.
                                        # 8-box range standard (Miles Ch. 8.6).

    # ── AMBIENT AND MAINTENANCE ──────────────────────────────────────────────
    ambient_temperature_C: float        # Room temperature in °C.
    ambient_humidity_pct: float         # Relative humidity in %.
                                        # Low humidity → paste dries in screen
                                        # (blocking); High humidity → blocking of
                                        # some thickener systems.
    last_maintenance_date: str          # ISO date string.
    maintenance_interval_hours: float   # Recommended machine service interval.
    operating_hours_since_maintenance: float  # Hours since last full service.


@dataclass
class PrintedFabricOutput:
    """
    Layer 4 — Predicted output quality metrics for Screen Printing.
    """
    # ── PASTE APPLICATION METRICS ────────────────────────────────────────────
    paste_volume_applied_g_per_m2: float    # Estimated paste volume applied in
                                            # g/m² of printed area.
                                            # Rotary screen: ~15 g/m² paper
                                            # (Table 2.3); fabric absorbs more.
    paste_penetration_depth: str            # "full", "partial", or "surface_only".
                                            # Full penetration → better handle and
                                            # wash fastness; surface only → risk of
                                            # crocking / rubbing faults.
    colour_yield_pct: float                 # Estimated colour yield as % of
                                            # theoretical maximum for the dye
                                            # concentration and fiber type.

    # ── PRINT DEFINITION METRICS ─────────────────────────────────────────────
    sharpness_of_mark: str                  # "excellent", "good", "acceptable",
                                            # or "poor". Governed by paste
                                            # viscosity, screen mesh, and
                                            # capillary spread (Miles Ch. 7.7.5).
    saw_tooth_effect_risk: str              # "negligible", "minor", or "significant".
                                            # Boundary stepped where design edge is
                                            # not parallel to screen threads
                                            # (Miles Ch. 2.7.2).
    registration_accuracy: str             # "excellent", "good", or "poor".
                                            # Depends on blanket control, adhesion,
                                            # and number of screens (Miles Ch. 2.3.3).

    # ── PRINT FAULTS RISK ────────────────────────────────────────────────────
    frame_mark_risk: str                    # "low", "medium", or "high".
                                            # Screen frame falls on wet print
                                            # (Miles Ch. 2.3.5).
    colour_crushing_risk: str              # "low", "medium", or "high".
                                            # Subsequent screens crushing wet
                                            # printed colour (Miles Ch. 2.3.5).
    screen_blockage_risk: str               # "low", "medium", or "high".
                                            # Paste drying in screen pores.
    paste_bleeding_risk: str                # "low", "medium", or "high".
                                            # Capillary spread beyond design edge.

    # ── FASTNESS METRICS ─────────────────────────────────────────────────────
    print_wash_fastness: float              # Predicted wash fastness of print (1–5).
    print_light_fastness: float             # Predicted light fastness of print (1–8).
    print_rub_fastness_dry: float           # Predicted dry rubbing fastness (1–5).
    print_rub_fastness_wet: float           # Predicted wet rubbing fastness (1–5).
    colour_yield_relative: float            # Relative colour yield vs theoretical
                                            # (0–1). Driven by fixation efficiency
                                            # and dye–fibre affinity.

    # ── FIXATION QUALITY ─────────────────────────────────────────────────────
    estimated_fixation_pct: float           # % of applied colorant fixed to fabric.
    unfixed_dye_staining_risk: str          # "low", "medium", or "high".
                                            # Risk of hydrolysed dye staining
                                            # white ground during wash-off.
    binder_crosslink_quality: str           # "good", "adequate", or "poor".
                                            # Relevant for pigment prints.
                                            # Poor crosslinking → weak wash fastness.

    # ── SUSTAINABILITY METRICS ───────────────────────────────────────────────
    total_water_L_per_kg: float             # Total process water: upstream
                                            # dyeing + printing wash-off (L/kg).
    total_effluent_dye_load_pct: float      # % of applied colorant discharged.
    energy_index: float                     # Relative energy (1.0 = conventional).

    # ── PRODUCTION METRICS ───────────────────────────────────────────────────
    effective_production_m_per_hour: float  # Actual throughput accounting for
                                            # machine efficiency losses.
    machine_efficiency_pct: float           # Estimated uptime % including colour
                                            # changes, screen cleaning, faults.

    warnings: list                          # Out-of-range parameter warnings.


# ─────────────────────────────────────────────────────────────────────────────
# CORE SIMULATION FUNCTIONS — Layer 5
# Each function models one specific cause-effect relationship from the manual.
# ─────────────────────────────────────────────────────────────────────────────

def predict_paste_volume_applied(
    screen_open_area_pct: float,
    screen_mesh_threads_per_cm: float,
    squeegee_type: str,
    squeegee_angle_deg: float,
    number_of_squeegee_passes: int,
    flood_stroke: bool,
    fabric_surface_texture: str,
    fabric_weight_g_per_m2: float
) -> float:
    """
    Predicts the volume of print paste applied in g/m² of printed area.

    Source: Miles, Textile Printing, Ch. 2.8 (Fundamental mechanism of screen
    printing), Ch. 7.7.5 (Paste flow in screen printing).
    - Paste volume ∝ screen pore radius³ (Poiseuille-derived from Eqn 2.1).
      Larger pore radius (coarser mesh / more open area) → exponentially more
      paste. More open area directly allows more paste to pass (Ch. 2.8.2).
    - Rod/magnetic squeegee applies more paste than blade; two moving surfaces
      create a higher pressure wedge (Ch. 2.8.1, Fig. 2.11).
    - Smaller squeegee angle → higher hydrodynamic pressure → more paste
      (Ch. 2.8.1). Volume can increase 5× by reducing squeegee angle (Ch. 7.7.5).
    - Each additional squeegee pass adds approximately the mesh volume.
    - Flood stroke pre-fills the mesh, increasing paste in first printing stroke.
    - Pile and textured fabrics absorb more paste due to their 3-D structure.
    - Heavier fabrics absorb more paste volumetrically.

    Reference calibration: rotary screen applies ~15 g/m² on paper (Table 2.3);
    on fabric, absorption is higher, typically 30–120 g/m² depending on fabric.
    """
    # Base volume from screen open area (proportional to pore size effect)
    # At 30% open area and 40 threads/cm → reference 40 g/m²
    base_volume = (screen_open_area_pct / 30.0) * (40.0 / max(1.0, screen_mesh_threads_per_cm)) * 40.0

    # Squeegee type factor: rod > blade
    squeegee_factors = {
        "magnetic_rod": 1.35,   # two moving surfaces → highest pressure
        "airflow_rod": 1.25,
        "rubber_blade": 1.0,    # reference
        "steel_blade": 0.90,    # less deformation → slightly less paste
    }
    squeegee_factor = squeegee_factors.get(squeegee_type.lower(), 1.0)

    # Squeegee angle: smaller angle → more paste (non-linear)
    # Reference angle 75°; at 60° roughly 1.5× more; at 45° roughly 2.5× more
    angle_factor = (75.0 / max(30.0, squeegee_angle_deg)) ** 0.8
    angle_factor = max(0.5, min(3.0, angle_factor))

    # Multiple passes: each pass adds ~80% of first pass volume (some paste
    # already transferred)
    pass_factor = 1.0 + (number_of_squeegee_passes - 1) * 0.75

    # Flood stroke pre-fills screen → ~15% more paste on first actual stroke
    flood_factor = 1.15 if flood_stroke else 1.0

    # Fabric texture absorption factor
    texture_factors = {
        "smooth": 1.0,      # minimal capillary absorption
        "textured": 1.4,    # more surface area and capillaries
        "pile": 2.0,        # very high absorption into pile structure
    }
    texture_factor = texture_factors.get(fabric_surface_texture.lower(), 1.0)

    # Fabric weight: heavier fabrics absorb more (normalised to 150 g/m²)
    weight_factor = (fabric_weight_g_per_m2 / 150.0) ** 0.4

    volume = base_volume * squeegee_factor * angle_factor * pass_factor * flood_factor * texture_factor * weight_factor
    return round(max(5.0, min(400.0, volume)), 1)


def predict_paste_penetration(
    paste_volume_g_per_m2: float,
    paste_viscosity_Pa_s: float,
    fabric_cover_factor: float,
    fabric_surface_texture: str,
    number_of_squeegee_passes: int
) -> str:
    """
    Predicts depth of paste penetration through fabric cross-section.

    Source: Miles, Textile Printing, Ch. 2.8.3 (Uptake of paste by fabric),
    Ch. 7.7.5 (Paste flow in screen printing).
    - Penetration ∝ paste volume applied and inversely ∝ viscosity.
    - Capillary pressure draws paste through inter-fibre spaces; the
      Washburn equation shows penetration distance ∝ √(r × γ × t / η)
      where r = capillary radius, γ = surface tension, η = viscosity.
    - Dense fabrics (high cover factor) restrict penetration.
    - Pile fabrics trap paste in pile before it reaches base structure.
    - More squeegee passes → more time and pressure → deeper penetration.
    - 'Short' flow pastes (yield value) resist penetration more than
      'long' Newtonian pastes (Miles Ch. 7.7.3 and Ch. 2.8.3).
    """
    # Penetration index: higher = deeper penetration
    penetration_index = (paste_volume_g_per_m2 / max(0.1, paste_viscosity_Pa_s)) \
                        / max(0.5, fabric_cover_factor) \
                        * (1.0 + (number_of_squeegee_passes - 1) * 0.3)

    # Pile fabric: paste first fills pile; penetration to base structure limited
    if fabric_surface_texture == "pile":
        penetration_index *= 0.4
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
    screen_mesh_threads_per_cm: float,
    design_coverage_pct: float,
    printing_speed_m_per_hour: float,
    fabric_surface_texture: str,
    thickener_type: str
) -> str:
    """
    Predicts sharpness of the printed mark (edge definition).

    Source: Miles, Textile Printing, Ch. 7.1 (Requirements), Ch. 7.7.5.
    - The viscosity of the paste must be high enough to prevent uncontrolled
      capillary spread beyond the design boundary (Ch. 7.1).
    - Finer mesh screens → smaller pores → sharper outlines (Ch. 2.7.2).
    - Higher printing speed → less time for capillary spread → sharper mark.
    - Blotch (high coverage) designs always show some spreading; fine outlines
      require tight paste control.
    - Pile/textured surfaces cause more lateral spread.
    - Crystal gum gives sharper marks than alginate at same viscosity because
      its gel structure resists penetration (Miles Ch. 7.2.3).
    - Emulsion and synthetic thickeners have high yield values → short flow →
      sharp marks (Miles Ch. 5.2.3, Ch. 7.7.3).
    """
    sharpness_score = 0

    # Paste viscosity: higher → sharper (up to a point where paste volume drops)
    if paste_viscosity_Pa_s >= 3.0:
        sharpness_score += 3
    elif paste_viscosity_Pa_s >= 1.5:
        sharpness_score += 2
    elif paste_viscosity_Pa_s >= 0.8:
        sharpness_score += 1

    # Screen mesh: finer → sharper
    if screen_mesh_threads_per_cm >= 62:
        sharpness_score += 3
    elif screen_mesh_threads_per_cm >= 49:
        sharpness_score += 2
    elif screen_mesh_threads_per_cm >= 34:
        sharpness_score += 1

    # Design coverage: blotch designs inherently less sharp at edges
    if design_coverage_pct < 30:
        sharpness_score += 2
    elif design_coverage_pct < 60:
        sharpness_score += 1
    else:
        sharpness_score += 0  # blotch: harder to control spread

    # Printing speed: higher speed → less time for spread → sharper
    if printing_speed_m_per_hour >= 2000:
        sharpness_score += 2
    elif printing_speed_m_per_hour >= 600:
        sharpness_score += 1

    # Fabric surface
    if fabric_surface_texture == "smooth":
        sharpness_score += 2
    elif fabric_surface_texture == "textured":
        sharpness_score += 1

    # Thickener type: crystal gum / emulsion → sharper
    sharp_thickeners = {"crystal_gum", "emulsion_o_in_w", "synthetic_polyacrylic",
                        "half_emulsion"}
    if thickener_type.lower() in sharp_thickeners:
        sharpness_score += 2
    elif thickener_type.lower() in {"starch_ether", "guar_locust_bean"}:
        sharpness_score += 1

    if sharpness_score >= 12:
        return "excellent"
    elif sharpness_score >= 8:
        return "good"
    elif sharpness_score >= 5:
        return "acceptable"
    else:
        return "poor"


def predict_saw_tooth_risk(
    screen_mesh_threads_per_cm: float,
    design_coverage_pct: float
) -> str:
    """
    Predicts saw-tooth effect risk at design boundaries.

    Source: Miles, Textile Printing, Ch. 2.7.2.
    'In many screen-printed fabrics the edges of the printed areas appear
    serrated... known as the "saw-tooth effect"... an almost inevitable
    consequence of the design area consisting of a regular array of threads
    and spaces.'
    - Coarser screen mesh → larger steps → more visible saw-tooth.
    - Fine-mesh screens enable small quantities of low-viscosity paste →
      good coverage with minimal saw-tooth effect (Ch. 2.7.2).
    - Blotch (high coverage) designs: boundary between print and unprinted
      areas has more opportunity to show saw-tooth than fine motifs.
    """
    if screen_mesh_threads_per_cm >= 62:
        base = "negligible"
    elif screen_mesh_threads_per_cm >= 49:
        base = "minor"
    else:
        base = "significant"

    # Blotch designs make saw-tooth more visible at boundary
    if design_coverage_pct > 60 and base == "minor":
        return "significant"
    return base


def predict_registration_accuracy(
    machine_type: str,
    number_of_colours: int,
    adhesive_type: str,
    blanket_type: str,
    printing_speed_m_per_hour: float,
    operating_hours_since_maintenance: float,
    maintenance_interval_hours: float
) -> str:
    """
    Predicts colour registration accuracy (fitting of colours in design).

    Source: Miles, Textile Printing, Ch. 2.3.3 (Intermittent movement),
    Ch. 2.3.5 (Printing faults), Ch. 2.4.3 (Blanket and screen drives).
    - Rotary screen: continuous movement, driven screens, shorter blanket →
      better registration than automatic flat (Ch. 2.4.3).
    - Flat automatic: blanket must advance exactly one repeat → hydraulic
      clamps required (Ch. 2.3.3).
    - More screens → more cumulative registration error.
    - Poor adhesive → fabric slips on blanket → local misfit (Ch. 2.3.5).
    - High speed → overrun inertia → more slip. Blanket extensibility critical
      at high speeds (Ch. 2.4.3).
    - Overdue maintenance → worn clamp mechanisms / eccentric drives.
    """
    score = 0

    # Machine type base score
    if machine_type == "rotary":
        score += 4   # continuous, driven screens, laser registration systems
    elif machine_type == "automatic_flat":
        score += 2   # hydraulic clamps but intermittent movement
    elif machine_type == "semi_automatic_flat":
        score += 1   # stop marks at each stop
    else:  # hand
        score += 0   # operator-dependent

    # Number of colours: more screens → more potential misfit
    if number_of_colours <= 4:
        score += 2
    elif number_of_colours <= 8:
        score += 1
    elif number_of_colours > 12:
        score -= 1

    # Adhesive quality
    if adhesive_type == "thermoplastic":
        score += 2   # durable, consistent tack
    elif adhesive_type == "semi_permanent":
        score += 1
    else:
        score += 0   # water-based: inconsistent tack especially at high speed

    # Speed: higher speed → more overrun potential for flat screens
    if machine_type in ("automatic_flat", "semi_automatic_flat"):
        if printing_speed_m_per_hour > 500:
            score -= 1

    # Maintenance
    maint_ratio = operating_hours_since_maintenance / max(1.0, maintenance_interval_hours)
    if maint_ratio > 1.0:
        score -= 2
    elif maint_ratio > 0.85:
        score -= 1

    if score >= 6:
        return "excellent"
    elif score >= 3:
        return "good"
    else:
        return "poor"


def predict_frame_mark_risk(
    machine_type: str,
    design_coverage_pct: float,
    printing_speed_m_per_hour: float,
    off_contact_printing: bool,
    number_of_colours: int
) -> str:
    """
    Predicts risk of screen frame marks on the printed fabric.

    Source: Miles, Textile Printing, Ch. 2.3.5 (Frame marks).
    'When printing consecutive screen repeats, the screen frame inevitably
    falls on part of the area most recently printed and may leave an impression.
    This is a particularly difficult problem for blotch screens where large
    amounts of print paste are applied.' (Ch. 2.3.5)
    - Off-contact printing reduces the problem (Ch. 2.3.5).
    - More screens → more potential for successive frame crushing.
    - Higher speed → less drying time between screens → more crushing.
    - Rotary screens: cylinders can be very close → blanket is shorter →
      frame marks not applicable; crushing risk is lower (Ch. 2.4).
    """
    if machine_type == "rotary":
        # No frame marks in rotary (no flat frame); crushing of adjacent
        # colour by cylinder still possible but much reduced
        base_risk = 0
    elif machine_type in ("automatic_flat", "semi_automatic_flat"):
        base_risk = 3  # inherent intermittent process issue
    else:
        base_risk = 1  # hand: alternate repeats technique avoids most frame marks

    # Blotch designs (high coverage) → more paste → more crushing
    if design_coverage_pct > 70:
        base_risk += 2
    elif design_coverage_pct > 40:
        base_risk += 1

    # Off-contact printing reduces frame marks
    if off_contact_printing:
        base_risk -= 2

    # More screens means more opportunity for frames to fall on wet areas
    if number_of_colours > 10:
        base_risk += 1

    # High speed: less intermediate drying → more crushing
    if machine_type == "automatic_flat" and printing_speed_m_per_hour > 500:
        base_risk += 1

    base_risk = max(0, base_risk)
    if base_risk <= 1:
        return "low"
    elif base_risk <= 3:
        return "medium"
    else:
        return "high"


def predict_colour_crushing_risk(
    machine_type: str,
    printing_speed_m_per_hour: float,
    number_of_colours: int,
    colorant_type: str,
    off_contact_printing: bool
) -> str:
    """
    Predicts risk of colour crushing (loss of depth when wet colour is
    re-compressed by subsequent screens).

    Source: Miles, Textile Printing, Ch. 2.3.5, Ch. 5.2.3.
    'Pigments are sensitive to crushing during roller printing... In screen
    printing the decrease in colour depth as a result of crushing is not nearly
    so pronounced, but for this reason there is the risk that uneven prints will
    be obtained on smooth, hydrophobic textiles.' (Miles Ch. 5.2.3)
    - More colours → more sequential crushing.
    - High speed → less drying between colours.
    - Pigment pastes: more crushing sensitive than dye pastes (disperse thickeners
      with yield values resist crushing — but pigment at high cover is vulnerable).
    - Off-contact printing leaves less paste to be crushed.
    """
    score = 0

    # Number of colours
    if number_of_colours > 12:
        score += 3
    elif number_of_colours > 8:
        score += 2
    elif number_of_colours > 5:
        score += 1

    # Machine type × speed interaction
    if machine_type in ("automatic_flat",) and printing_speed_m_per_hour > 500:
        score += 2
    elif machine_type == "rotary" and printing_speed_m_per_hour > 3000:
        score += 1

    # Pigment pastes are more vulnerable
    if colorant_type == "pigment":
        score += 1

    # Off-contact reduces crushing
    if off_contact_printing:
        score -= 1

    score = max(0, score)
    if score <= 1:
        return "low"
    elif score <= 3:
        return "medium"
    else:
        return "high"


def predict_screen_blockage_risk(
    thickener_type: str,
    paste_viscosity_Pa_s: float,
    screen_mesh_threads_per_cm: float,
    ambient_temperature_C: float,
    ambient_humidity_pct: float,
    printing_speed_m_per_hour: float,
    machine_type: str
) -> str:
    """
    Predicts risk of paste drying and blocking screen pores.

    Source: Miles, Textile Printing, Ch. 7.2.1 (Print paste stability).
    - Insoluble matter (pigments, some thickeners) blocks fine pores more
      readily at low speeds (paste sits in screen longer between strokes).
    - Low humidity → paste dries faster in open screen areas.
    - High temperature → faster drying.
    - Fine-mesh screens have smaller pores → block more easily.
    - Emulsion thickeners (white spirit-based) are more prone to emulsion
      breakdown and blocking than aqueous systems.
    - Rotary: paste is continuously moving → less blockage risk.
    """
    risk = 0

    # Thickener type: emulsions less stable than polymer solutions
    if thickener_type in ("emulsion_o_in_w", "half_emulsion"):
        risk += 2   # emulsion can break down, blocking pores
    elif thickener_type == "synthetic_polyacrylic":
        risk += 1   # gel-like structure can set in fine pores

    # Viscosity: very high viscosity paste is harder to pump through pores
    if paste_viscosity_Pa_s > 4.0:
        risk += 1

    # Fine mesh: smaller pores → block more easily
    if screen_mesh_threads_per_cm >= 80:
        risk += 2
    elif screen_mesh_threads_per_cm >= 55:
        risk += 1

    # Ambient conditions
    if ambient_humidity_pct < 40:
        risk += 2   # dry conditions → rapid surface drying in screen
    elif ambient_humidity_pct < 55:
        risk += 1

    if ambient_temperature_C > 30:
        risk += 1

    # Low printing speed → paste sits in screen longer between passes
    if printing_speed_m_per_hour < 200:
        risk += 2
    elif printing_speed_m_per_hour < 600:
        risk += 1

    # Rotary: continuous movement keeps paste mobile
    if machine_type == "rotary":
        risk -= 2

    risk = max(0, risk)
    if risk <= 2:
        return "low"
    elif risk <= 4:
        return "medium"
    else:
        return "high"


def predict_paste_bleeding_risk(
    paste_viscosity_Pa_s: float,
    thickener_type: str,
    design_coverage_pct: float,
    fabric_cover_factor: float,
    residual_unfixed_dye_pct: float
) -> str:
    """
    Predicts risk of print paste bleeding beyond design boundaries.

    Source: Miles, Textile Printing, Ch. 7.1, Ch. 7.7.5.
    - Bleeding (spread) occurs when paste viscosity is too low to counter
      capillary forces in the fabric structure.
    - Higher fabric cover factor → smaller capillaries → more restriction
      on lateral spread but also draws paste in more strongly if the
      thickener is not well-matched.
    - Blotch designs force more paste onto the fabric; the excess must spread.
    - Residual unfixed dye from the dyeing stage can act as an additional
      mobile colorant that bleeds during steaming (Miles Ch. 5.3.5).
    - 'Short' flow thickeners (crystal gum, synthetic polyacrylic with yield
      value) resist spreading under low shear (Miles Ch. 7.7.3).
    """
    risk = 0

    # Paste viscosity: lower → more bleed
    if paste_viscosity_Pa_s < 0.8:
        risk += 3
    elif paste_viscosity_Pa_s < 1.5:
        risk += 2
    elif paste_viscosity_Pa_s < 3.0:
        risk += 1

    # Thickener type: alginates and locust bean gum have less yield value →
    # more bleed potential than short-flow crystal gum or synthetics
    long_flow_thickeners = {"alginate", "starch_ether", "guar_locust_bean"}
    short_flow_thickeners = {"crystal_gum", "synthetic_polyacrylic", "emulsion_o_in_w"}
    if thickener_type.lower() in long_flow_thickeners:
        risk += 1
    elif thickener_type.lower() in short_flow_thickeners:
        risk -= 1

    # High coverage design → more paste volume → more potential bleed
    if design_coverage_pct > 70:
        risk += 1

    # Residual unfixed dye → bleeds during steaming
    if residual_unfixed_dye_pct > 5.0:
        risk += 2
    elif residual_unfixed_dye_pct > 2.0:
        risk += 1

    risk = max(0, risk)
    if risk <= 1:
        return "low"
    elif risk <= 3:
        return "medium"
    else:
        return "high"


def predict_fixation_pct(
    colorant_type: str,
    fiber_type: str,
    fixation_method: str,
    fixation_temperature_C: float,
    fixation_time_min: float,
    urea_concentration_g_per_kg: float,
    alkali_type: str,
    alkali_concentration_g_per_kg: float,
    paste_penetration_depth: str
) -> float:
    """
    Predicts fixation efficiency (% of applied colorant fixed to fabric).

    Source: Miles, Textile Printing, Ch. 5 (fixation by dye class) and
    Ch. 8 (fixation mechanisms).
    - Reactive dyes on cotton: saturated steam 100°C, 10 min → ~70–80% fixation.
      Bifunctional dyes → up to 90% (Miles Ch. 5.3.5).
    - Disperse dyes on polyester: HT steam 180°C → fixation in 1 min vs
      30 min at 120°C pressure steam (Miles Ch. 8.3.6).
    - Pigment: binder curing in hot air 140–160°C, 3–5 min → binder crosslinks;
      'fixation' is mechanical not chemical (Miles Ch. 8.2).
    - Acid dyes on nylon: saturated steam 100°C, 20–30 min → good fixation.
    - Urea: essential for HT steam reactive fixation; holds moisture for dye
      diffusion (Miles Ch. 8.3.6). Without urea → poor yields.
    - Full penetration → dye in optimal contact with fibre → better fixation.
    """
    # Base fixation by colorant-fibre system
    base_fixation = {
        ("reactive_dye", "cotton"): 75.0,
        ("reactive_dye", "viscose"): 70.0,
        ("reactive_dye", "blend_PES_CO"): 65.0,
        ("disperse_dye", "polyester"): 72.0,
        ("disperse_dye", "blend_PES_CO"): 68.0,
        ("acid_dye", "nylon"): 80.0,
        ("acid_dye", "wool"): 82.0,
        ("acid_dye", "silk"): 78.0,
        ("vat_dye", "cotton"): 85.0,
        ("pigment", "cotton"): 92.0,     # mechanical binder curing
        ("pigment", "polyester"): 90.0,
        ("pigment", "blend_PES_CO"): 90.0,
        ("pigment", "nylon"): 88.0,
        ("discharge", "cotton"): 78.0,
        ("azoic", "cotton"): 80.0,
    }
    base = base_fixation.get((colorant_type.lower(), fiber_type.lower()), 68.0)

    # Fixation method bonus/penalty
    if colorant_type == "reactive_dye":
        if fixation_method == "high_temp_steam":
            # HT steam + urea can fix reactive faster (Miles Ch. 8.3.6)
            if urea_concentration_g_per_kg >= 100:
                method_bonus = 5.0
                # But urea needed otherwise yields are poor
            else:
                method_bonus = -10.0  # HT steam without urea: poor yield
        elif fixation_method == "saturated_steam":
            method_bonus = 0.0
        elif fixation_method == "baking_hot_air":
            # Some reactive dyes can be baked but less efficient than steam
            method_bonus = -8.0
        else:
            method_bonus = -15.0
    elif colorant_type == "disperse_dye":
        if fixation_method == "high_temp_steam":
            if fixation_temperature_C >= 175:
                method_bonus = 8.0
            else:
                method_bonus = 2.0
        elif fixation_method == "pressure_steam":
            method_bonus = 10.0   # most efficient for polyester
        elif fixation_method == "baking_hot_air":
            method_bonus = -5.0   # only 50-70% without carrier (Miles Ch. 5.4.3)
        else:
            method_bonus = -20.0
    elif colorant_type == "pigment":
        if fixation_method in ("baking_hot_air", "none_pigment_curing"):
            method_bonus = 0.0   # standard for pigment
        else:
            method_bonus = -5.0  # steam can inhibit binder crosslinking (Miles 5.2.2)
    elif colorant_type == "acid_dye":
        if fixation_method == "saturated_steam":
            method_bonus = 0.0
        elif fixation_method == "pressure_steam":
            method_bonus = 5.0
        else:
            method_bonus = -10.0
    elif colorant_type == "vat_dye":
        if fixation_method == "saturated_steam":
            method_bonus = 0.0
        else:
            method_bonus = -10.0
    else:
        method_bonus = 0.0

    # Fixation time: insufficient time → lower fixation
    if colorant_type == "reactive_dye" and fixation_method == "saturated_steam":
        target_time = 10.0  # minutes for reactive on cotton
        if fixation_time_min < target_time * 0.5:
            method_bonus -= 15.0
        elif fixation_time_min < target_time:
            method_bonus -= 8.0
    elif colorant_type == "disperse_dye" and fixation_method == "high_temp_steam":
        if fixation_time_min < 1.0:
            method_bonus -= 20.0
        elif fixation_time_min < 5.0:
            method_bonus -= 5.0
    elif colorant_type == "pigment":
        if fixation_time_min < 3.0:
            method_bonus -= 10.0  # insufficient binder crosslinking

    # Alkali for reactive dyes
    if colorant_type == "reactive_dye":
        if alkali_concentration_g_per_kg < 10.0:
            method_bonus -= 15.0   # insufficient alkali → poor fixation
        elif alkali_concentration_g_per_kg < 18.0:
            method_bonus -= 5.0

    # Penetration depth: full penetration means more fibre-dye contact
    penetration_bonus = {"full": 3.0, "partial": 0.0, "surface_only": -5.0}
    method_bonus += penetration_bonus.get(paste_penetration_depth, 0.0)

    fixation = base + method_bonus
    return round(max(30.0, min(98.0, fixation)), 1)


def predict_wash_fastness(
    colorant_type: str,
    fiber_type: str,
    estimated_fixation_pct: float,
    wash_off_applied: bool,
    wash_off_temperature_C: float,
    wash_off_stages: int,
    paste_penetration_depth: str,
    binder_concentration_pct: float
) -> float:
    """
    Predicts wash fastness rating (ISO 1–5) of the print.

    Source: Miles, Textile Printing, Ch. 5.2.5, 5.3.5, 8.5.
    - Reactive dyes: 'very good wash fastness with rating 4–5' when properly
      fixed and washed. Unfixed hydrolysed dye must be removed completely or
      wash fastness deteriorates. (Miles, based on Mahapatra reference, Ch. 5.)
    - Pigment: 'generally acceptable fastness'; dark pigment prints have lower
      wash fastness especially on synthetics (Miles Ch. 5.2.5 disadvantages).
    - Insufficient binder → weak binder film → poor mechanical bonding.
    - Wash-off temperature critical: 90°C removes reactive hydrolysed dye in
      90 s; at 60°C needs >4 min (Miles Fig. 8.12).
    - Surface-only penetration → less mechanical bonding → lower wash fastness.
    """
    # Base wash fastness by colorant-fibre system (optimum conditions)
    base_fastness = {
        ("reactive_dye", "cotton"): 4.5,
        ("reactive_dye", "viscose"): 4.0,
        ("reactive_dye", "blend_PES_CO"): 4.0,
        ("disperse_dye", "polyester"): 4.5,
        ("acid_dye", "nylon"): 4.0,
        ("acid_dye", "wool"): 4.0,
        ("vat_dye", "cotton"): 5.0,
        ("pigment", "cotton"): 4.0,
        ("pigment", "polyester"): 3.5,
        ("pigment", "blend_PES_CO"): 3.5,
    }
    base = base_fastness.get((colorant_type.lower(), fiber_type.lower()), 3.5)

    # Fixation efficiency penalty
    if estimated_fixation_pct < 60:
        base -= 1.5
    elif estimated_fixation_pct < 75:
        base -= 0.5

    # Wash-off: crucial for dye-based prints
    if colorant_type != "pigment" and not wash_off_applied:
        base -= 1.5  # unfixed dye left on fabric massively reduces fastness

    if wash_off_applied:
        if wash_off_temperature_C >= 90:
            base += 0.3   # efficient removal of hydrolysed dye
        elif wash_off_temperature_C < 60:
            base -= 0.5   # insufficient removal
        if wash_off_stages < 4:
            base -= 0.3   # too few wash stages

    # Pigment: binder concentration critical
    if colorant_type == "pigment":
        if binder_concentration_pct < 7.0:
            base -= 1.0   # below minimum (Miles Recipe 5.1)
        elif binder_concentration_pct >= 10.0:
            base += 0.2

    # Penetration: surface-only → lower mechanical bond
    if paste_penetration_depth == "surface_only":
        base -= 0.5

    return round(max(1.0, min(5.0, base)), 1)


def predict_light_fastness(
    colorant_type: str,
    fiber_type: str,
    paste_colorant_concentration_g_per_kg: float,
    estimated_fixation_pct: float
) -> float:
    """
    Predicts light fastness rating (ISO 1–8) of the print.

    Source: Miles, Textile Printing, Ch. 5 and coloration references.
    - Pigment prints: 'unsurpassed fastness to light' (Miles Ch. 5.2.5
      advantages point 2) — typically rating 6–8 for selected organic pigments.
    - Reactive dyes: 'very good light fastness with rating about 6'
      (Mahapatra reference in coloring module).
    - Vat dyes: excellent light fastness (7–8).
    - Acid dyes on nylon: variable; some achieve 5–6.
    - Low fixation → less covalently bonded dye → some surface dye fades faster.
    - Pale shades (low concentration) can have apparently lower light fastness
      because the depth of shade change is more perceptible at low starting depth.
    """
    base_light_fastness = {
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
    base = base_light_fastness.get((colorant_type.lower(), fiber_type.lower()), 5.5)

    # Low fixation → some surface dye → faster fade
    if estimated_fixation_pct < 70:
        base -= 0.5

    # Very pale shade → perceptible change is worse
    if paste_colorant_concentration_g_per_kg < 10.0:
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
    Predicts dry and wet rubbing fastness ratings (ISO 1–5).

    Source: Miles, Textile Printing, Ch. 5.2.5.
    - 'No pigment print is completely fast to dry cleaning. Depending upon the
      pigment and binder... prints can show rub marks and/or loss in colour depth.'
    - Dark pigment prints on synthetic blends are especially susceptible to
      abrasion (Miles Ch. 5.2.5 disadvantage 1).
    - Dye-based prints: rub fastness depends on wash-off efficiency. Unfixed
      dye on surface causes crocking on rubbing.
    - Full penetration → less surface dye → better rub fastness.
    - Binder quality/quantity crucial for pigment; insufficient binder → weak
      mechanical bond → poor rub fastness.
    - Wet rub fastness is always 0.5–1.0 grade lower than dry.

    Returns: (dry_rub, wet_rub) tuple.
    """
    # Base dry rub fastness
    if colorant_type == "pigment":
        base_dry = 4.0
        if binder_concentration_pct < 7.0:
            base_dry -= 1.5
        elif binder_concentration_pct >= 10.0:
            base_dry += 0.2
        # High coverage blotch → more pigment surface → rub marks
        if design_coverage_pct > 70:
            base_dry -= 0.5
    else:
        # Dye-based
        base_dry = 4.0
        if estimated_fixation_pct < 70:
            base_dry -= 1.0
        elif estimated_fixation_pct >= 85:
            base_dry += 0.2

    # Penetration: surface-only → more surface dye / pigment → crocking
    if paste_penetration_depth == "surface_only":
        base_dry -= 0.5
    elif paste_penetration_depth == "full":
        base_dry += 0.2

    dry_rub = round(max(1.0, min(5.0, base_dry)), 1)
    wet_rub = round(max(1.0, min(5.0, base_dry - 0.7)), 1)
    return dry_rub, wet_rub


def predict_colour_yield(
    colorant_type: str,
    thickener_type: str,
    paste_colorant_concentration_g_per_kg: float,
    estimated_fixation_pct: float,
    paste_penetration_depth: str,
    ground_colour_yield: float
) -> float:
    """
    Predicts relative colour yield (0–1) of the printed design.

    Source: Miles, Textile Printing, Ch. 7.2.3 (Effect on colour yield).
    - High colour yield requires minimum penetration into yarn (dye/pigment
      stays on surface) — but not so little as to cause surface crocking.
    - 'The highest colour yield (depth of colour for a given mass of colorant
      per unit area) is only obtained when penetration... is at a minimum.'
      (Miles Ch. 7.2.3).
    - Starch-based thickeners: high colour yield due to their gel structure
      restricting penetration (Ch. 7.2.3).
    - Synthetic polyacrylic thickeners: significantly higher fixation and colour
      yields with disperse dyes on polyester than natural polymer thickeners
      (Ch. 7.6).
    - Fixation efficiency directly drives colour yield.
    - Ground colour yield from dyeing affects the visual contrast of the print.
    """
    # Base from fixation
    base = estimated_fixation_pct / 100.0 * 0.85  # fixation efficiency drives yield

    # Thickener: starch-based restrict penetration → higher surface yield
    high_yield_thickeners = {"starch_ether", "crystal_gum", "guar_locust_bean"}
    if thickener_type.lower() in high_yield_thickeners:
        base *= 1.10
    elif thickener_type.lower() == "synthetic_polyacrylic":
        base *= 1.08   # thinner film → better dye transfer (Miles Ch. 7.6)
    elif thickener_type.lower() == "alginate":
        base *= 0.97   # slightly lower surface yield, good for reactive

    # Penetration: surface-only actually gives highest colour yield visually
    # (dye concentrated at surface) — but risks crocking
    if paste_penetration_depth == "surface_only":
        base *= 1.05
    elif paste_penetration_depth == "full":
        base *= 0.95

    # Colorant concentration: very high concentration → diminishing yield
    if paste_colorant_concentration_g_per_kg > 100:
        base *= 0.93
    elif paste_colorant_concentration_g_per_kg < 10:
        base *= 0.90

    return round(max(0.1, min(1.0, base)), 3)


def predict_unfixed_dye_staining_risk(
    colorant_type: str,
    estimated_fixation_pct: float,
    wash_off_applied: bool,
    wash_off_temperature_C: float,
    wash_off_stages: int,
    residual_unfixed_dye_pct: float
) -> str:
    """
    Predicts risk of unfixed dye staining white or pale ground areas during
    wash-off.

    Source: Miles, Textile Printing, Ch. 8.5 (Washing-off processes).
    'Staining of unprinted areas by adsorption of dyes from the wash liquor is
    a major hazard where the concentration of unfixed dye is allowed to build up
    in the washing-off process.' (Miles Ch. 8.5)
    - Low fixation → more unfixed dye to remove → higher staining risk.
    - Residual unfixed dye from dyeing stage adds to the burden.
    - Wash-off at 90°C dramatically accelerates removal vs 60°C (Fig. 8.12).
    - Insufficient wash stages → dye builds up in final baths → staining.
    - Pigment: no wash-off → no liquid-phase dye → no staining risk.
    """
    if colorant_type == "pigment":
        return "low"  # no mobile dye phase in wash

    risk = 0

    # Low fixation → more unfixed dye in wash bath
    unfixed_pct = 100.0 - estimated_fixation_pct
    if unfixed_pct > 35:
        risk += 3
    elif unfixed_pct > 20:
        risk += 2
    elif unfixed_pct > 10:
        risk += 1

    # Residual unfixed dye from dyeing stage
    if residual_unfixed_dye_pct > 5.0:
        risk += 2
    elif residual_unfixed_dye_pct > 2.0:
        risk += 1

    # Wash-off quality
    if not wash_off_applied:
        risk += 4  # no wash-off: all unfixed dye stays on fabric
    else:
        if wash_off_temperature_C >= 90:
            risk -= 2  # fast and efficient removal
        elif wash_off_temperature_C < 60:
            risk += 2  # slow removal: dye builds up in wash baths
        if wash_off_stages < 4:
            risk += 1

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

    Source: Miles, Textile Printing, Ch. 5.2.2 (Binder systems).
    - Self-crosslinking N-methylol groups activated by hot air in acid medium
      at >120°C (Miles Scheme 5.1).
    - 'Steam can have adverse effects on crosslinking' (Miles Ch. 5.2.2).
    - Baking 140–160°C, 3–5 min is optimal (Miles Ch. 8.2).
    - 'Overcrosslinking' (>2% methylol groups) → brittle film → poor rub
      fastness. Insufficient crosslinking → poor wash fastness.
    - Acid condition needed: synthetic thickeners neutralised with ammonia
      re-form free acid during drying → auto-catalysis (Miles Ch. 7.6).
    - External crosslinking agents (methylolmelamines) at 0–10% on binder.
    """
    if colorant_type != "pigment":
        return "good"  # N/A for non-pigment; return "good" as placeholder

    score = 0

    # Binder concentration
    if binder_concentration_pct >= 10.0:
        score += 3
    elif binder_concentration_pct >= 7.0:
        score += 2  # minimum adequate (Miles Recipe 5.1)
    elif binder_concentration_pct >= 4.0:
        score += 1
    else:
        score += 0  # insufficient binder

    # Fixation method: hot air is optimal for binder crosslinking
    if fixation_method in ("baking_hot_air", "none_pigment_curing"):
        score += 3
    elif fixation_method == "high_temp_steam":
        score += 1   # possible but less efficient
    else:
        score += 0   # saturated steam inhibits crosslinking (Miles 5.2.2)

    # Fixation temperature and time
    if 140 <= fixation_temperature_C <= 160:
        score += 2  # optimal range (Miles Ch. 8.2)
    elif fixation_temperature_C < 120:
        score += 0  # too low: crosslinking incomplete
    else:
        score += 1

    if fixation_time_min >= 3.0:
        score += 1
    else:
        score += 0  # too short

    # Alkali should not be present in pigment pastes during fixation
    acid_promoting = {"diammonium_phosphate", "none"}
    if alkali_type.lower() in acid_promoting:
        score += 1  # acid condition promotes crosslinking
    elif alkali_type.lower() in {"sodium_bicarbonate", "sodium_carbonate", "caustic_soda"}:
        score -= 1  # alkaline inhibits crosslinking

    if score >= 8:
        return "good"
    elif score >= 5:
        return "adequate"
    else:
        return "poor"


def predict_water_consumption(
    upstream_water_L_per_kg: float,
    wash_off_applied: bool,
    wash_off_stages: int,
    colorant_type: str
) -> float:
    """
    Predicts total water consumption in L/kg (dyeing + printing wash-off).

    Source: Miles, Textile Printing, Ch. 8.6 (Washing-off equipment).
    Conventional printing + wash-off on an 8-box range uses significant water.
    Parish's analysis: performance ∝ water flow (Miles Ch. 8.6, Eqn 8.2).
    Pigment: no wash-off → saves ~15–30 L/kg vs dye-based (Miles Ch. 5.2.5).
    """
    if not wash_off_applied:
        print_water = 0.0
    else:
        # Approximate 8-box range at 30 m/min uses 15–25 L/kg
        # More stages → more water but also better removal
        print_water = 5.0 * wash_off_stages  # simplified estimate

    total = upstream_water_L_per_kg + print_water
    return round(total, 1)


def predict_machine_efficiency(
    machine_type: str,
    number_of_colours: int,
    colorant_type: str,
    dryer_efficiency: str,
    design_coverage_pct: float,
    operating_hours_since_maintenance: float,
    maintenance_interval_hours: float
) -> float:
    """
    Predicts machine efficiency % including downtime for colour changes, screen
    cleaning, paste preparation, and fault correction.

    Source: Miles, Textile Printing, Ch. 2.3.4 (Production rate), Ch. 2.4.5.
    - Rotary: 'expensive machines pay to keep downtime to a minimum' (Ch. 2.4.5).
    - Colour changes and screen washing reduce effective production time.
    - Dryer limitations force speed reduction at high design coverage (Ch. 2.3.4).
    - Screen blockage and paste printing faults cause stoppages.
    - Overdue maintenance → blocked screens, worn blankets, registration errors.
    """
    # Base efficiency by machine type
    base_eff = {
        "rotary": 85.0,             # continuous process, fast colour changes
        "automatic_flat": 78.0,     # intermittent, slower colour changes
        "semi_automatic_flat": 65.0,
        "hand": 50.0,
    }
    eff = base_eff.get(machine_type.lower(), 70.0)

    # More colours → more screen changes / adjustments
    colour_penalty = max(0.0, (number_of_colours - 6) * 0.8)
    eff -= colour_penalty

    # Dryer efficiency: if inadequate, must slow down
    if dryer_efficiency == "low":
        eff -= 15.0
    elif dryer_efficiency == "adequate":
        eff -= 3.0

    # High coverage: more paste volume → longer dryer dwell needed
    if design_coverage_pct > 70:
        eff -= 5.0
    elif design_coverage_pct > 50:
        eff -= 2.0

    # Maintenance overdue
    maint_ratio = operating_hours_since_maintenance / max(1.0, maintenance_interval_hours)
    if maint_ratio > 1.0:
        eff -= 8.0
    elif maint_ratio > 0.85:
        eff -= 3.0

    return round(max(25.0, min(95.0, eff)), 1)


# ─────────────────────────────────────────────────────────────────────────────
# MASTER SIMULATION FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def simulate_screen_printing(
    fabric: InputDyedFabric,
    params: ScreenPrintingOperationalParams
) -> PrintedFabricOutput:
    """
    Master simulation function for Screen Printing.

    Takes Layer 2 (InputDyedFabric — the output of a dyeing simulation) and
    Layer 3 (ScreenPrintingOperationalParams), runs all prediction models, and
    returns Layer 4 (PrintedFabricOutput).

    Also performs parameter validation and generates warnings for out-of-range
    conditions based on limits documented in Miles (2003).
    """
    warnings = []

    # ── PARAMETER VALIDATION ─────────────────────────────────────────────────

    # Screen type vs mesh compatibility (Miles Ch. 2.7.3, Table 2.2)
    if params.screen_type == "lacquer_rotary":
        if params.screen_open_area_pct > 15:
            warnings.append(
                f"Lacquer rotary screen open area ({params.screen_open_area_pct:.0f}%) "
                "exceeds the typical range of 9–13% for lacquer nickel screens "
                "(Miles Ch. 2.7.3). Verify screen specification."
            )
        if params.screen_mesh_threads_per_cm > 100:
            warnings.append(
                "Screen mesh of >100 threads/cm is not achievable with electroformed "
                "lacquer screens (nickel bridging limits fine mesh, Miles Ch. 2.7.3). "
                "The finest practical lacquer mesh is ~80 mesh (31 threads/cm)."
            )
    elif params.screen_type == "flat_polyester_mesh":
        if params.screen_open_area_pct < 27 or params.screen_open_area_pct > 47:
            warnings.append(
                f"Flat polyester screen open area ({params.screen_open_area_pct:.0f}%) "
                "is outside the typical range of 27–47% shown in Miles Table 2.1. "
                "Verify screen fabric specification."
            )

    # Screen circumference vs design repeat (Miles Ch. 2.4.4, 2.5.4)
    if params.machine_type == "rotary" and params.screen_circumference_mm > 0:
        circumference_cm = params.screen_circumference_mm / 10.0
        if circumference_cm > 0 and params.design_repeat_length_cm > 0:
            remainder = circumference_cm % params.design_repeat_length_cm
            # Allow small rounding tolerance
            if remainder > 0.05 and (params.design_repeat_length_cm - remainder) > 0.05:
                warnings.append(
                    f"Design repeat ({params.design_repeat_length_cm:.1f} cm) does not "
                    f"divide evenly into screen circumference ({circumference_cm:.1f} cm). "
                    "A whole number of repeats must fit around the rotary screen "
                    "(Miles Ch. 2.5.4). Adjust repeat size or select a different screen "
                    f"circumference (standard: 64.0 cm)."
                )

    # Squeegee angle check (Miles Ch. 2.8.1)
    if params.squeegee_angle_deg < 45:
        warnings.append(
            f"Squeegee angle of {params.squeegee_angle_deg:.0f}° is very shallow. "
            "Extremely small angles develop high hydrodynamic pressure and apply "
            "very large volumes of paste (Miles Ch. 2.8.1). Verify this is intentional "
            "(e.g., heavy blotch on pile fabric)."
        )
    elif params.squeegee_angle_deg > 85:
        warnings.append(
            f"Squeegee angle of {params.squeegee_angle_deg:.0f}° is very steep. "
            "Sharp blades at steep angles apply minimal paste. Fine outlines only — "
            "not suitable for blotch printing or thick fabrics (Miles Ch. 2.2)."
        )

    # Thickener compatibility checks (Miles Ch. 5.3.5, Ch. 7.2.1)
    if params.colorant_type == "reactive_dye" and params.thickener_type not in (
            "alginate", "synthetic_polyacrylic", "half_emulsion"):
        warnings.append(
            f"Thickener '{params.thickener_type}' is not recommended for reactive dyes. "
            "Alginates are the only natural thickeners suitable for reactive dye printing "
            "because carbohydrates react with the dye, giving low colour yields "
            "(Miles Ch. 5.3.5). Use sodium alginate or a compatible synthetic thickener."
        )

    if params.colorant_type == "pigment" and params.binder_concentration_pct < 7.0:
        warnings.append(
            f"Binder concentration ({params.binder_concentration_pct:.1f}%) is below "
            "the minimum of 7% required for adequate adhesion of pigment particles "
            "(Miles Recipe 5.1). Insufficient binder → poor wash and rub fastness."
        )

    # Reactive dye alkali check (Miles Ch. 5.3.5)
    if params.colorant_type == "reactive_dye":
        if params.alkali_type == "none" or params.alkali_concentration_g_per_kg < 10.0:
            warnings.append(
                "Reactive dye printing requires alkali (typically NaHCO3 at 20 g/kg) "
                "to ionise cellulose hydroxyl groups for covalent dye-fibre bond formation "
                "(Miles Ch. 5.3.5). Without adequate alkali, fixation will be very low."
            )
        if params.urea_concentration_g_per_kg < 50.0 and params.fixation_method == "high_temp_steam":
            warnings.append(
                f"Urea concentration ({params.urea_concentration_g_per_kg:.0f} g/kg) is "
                "below the 100–200 g/kg required for HT steam fixation of reactive dyes. "
                "Urea holds moisture as a eutectic mixture, enabling dye-fibre reaction at "
                "superheated steam temperatures (Miles Ch. 8.3.6). Without urea, colour "
                "yields will be very poor."
            )

    # Pigment with steam fixation warning (Miles Ch. 5.2.2)
    if params.colorant_type == "pigment" and params.fixation_method == "saturated_steam":
        warnings.append(
            "Pigment prints should be fixed with hot air (baking), not saturated steam. "
            "'Steam can have adverse effects on crosslinking' of binder N-methylol groups "
            "(Miles Ch. 5.2.2). Use hot air at 140–160°C for 3–5 min."
        )

    # Disperse dye fixation check (Miles Ch. 5.4.3)
    if params.colorant_type == "disperse_dye":
        if params.fixation_method == "saturated_steam" and params.fixation_temperature_C < 120:
            warnings.append(
                "Disperse dyes on polyester cannot be adequately fixed in saturated "
                "steam at 100°C without a carrier — and even then fixation is incomplete. "
                "Use high-temperature steam (160–185°C, 5–20 min) or pressure steam "
                "(0.25–0.30 MPa, 20–30 min) for satisfactory fixation (Miles Ch. 5.4.3)."
            )

    # Dryer efficiency vs coverage (Miles Ch. 2.3.4)
    if params.design_coverage_pct > 70 and params.dryer_efficiency == "low":
        warnings.append(
            f"High design coverage ({params.design_coverage_pct:.0f}%) combined with "
            "low dryer efficiency will force a significant reduction in printing speed. "
            "Miles Ch. 2.3.4: 'If the dryer is short... the printing speed will have to "
            "be reduced.' Upgrade dryer capacity or reduce printing speed."
        )

    # Speed vs automatic flat screen limitation (Miles Ch. 2.3.6)
    if params.machine_type == "automatic_flat" and params.printing_speed_m_per_hour > 600:
        warnings.append(
            f"Automatic flat-screen printing speed of {params.printing_speed_m_per_hour:.0f} m/h "
            "exceeds the practical range of 300–600 m/h (Miles Ch. 2.3.6). "
            "At high speed, blanket overrun and inadequate intermediate drying "
            "cause registration errors and colour crushing."
        )

    # Rotary screen speed check (Miles Ch. 2.4, 30–70 m/min = 1800–4200 m/h)
    if params.machine_type == "rotary" and params.printing_speed_m_per_hour > 4500:
        warnings.append(
            f"Rotary screen printing speed of {params.printing_speed_m_per_hour:.0f} m/h "
            "exceeds typical operational limits (30–70 m/min, 1800–4200 m/h). "
            "'It is quite possible to run the machine faster... the limitations often being "
            "the length and efficiency of the cloth and blanket dryers' (Miles Ch. 2.4)."
        )

    # Substrate damage risk from dyeing stage
    if fabric.substrate_damage_risk == "high":
        warnings.append(
            "Input fabric: substrate damage risk from dyeing stage is HIGH. "
            "Fabric with reduced tensile strength (oxycellulose from alkali/heat "
            "treatment) may tear at blanket adhesive tension points or under "
            "squeegee pressure (Miles Ch. 2.3.1)."
        )

    # Residual unfixed dye from dyeing stage (Miles Ch. 6.2 discharge, 5.3.5)
    if fabric.residual_unfixed_dye_pct > 5.0:
        warnings.append(
            f"Residual unfixed dye from dyeing ({fabric.residual_unfixed_dye_pct:.1f}%) "
            "is high. This dye will become mobile during steam fixation and will "
            "bleed into printed areas, reducing colour definition and contaminating "
            "white grounds (Miles Ch. 5.3.5, Ch. 8.5.3). Improve dyeing wash-off."
        )

    # pH check for discharge printing (Miles Ch. 6.2.1)
    if params.colorant_type == "discharge":
        if fabric.substrate_pH > 8.0:
            warnings.append(
                f"Substrate pH ({fabric.substrate_pH:.1f}) is alkaline. Discharge printing "
                "relies on reducing agents that work under specific pH conditions. "
                "Residual alkali from dyeing can interfere with the discharging agent "
                "and reduce discharge crispness (Miles Ch. 6.2.1)."
            )
        if fabric.unfixed_hydrolysed_dye_pct > 3.0:
            warnings.append(
                f"High residual hydrolysed dye ({fabric.unfixed_hydrolysed_dye_pct:.1f}%) "
                "will interfere with discharge printing. Incomplete discharge will result "
                "because hydrolysed dye not linked to fibre is harder to destroy. "
                "Ensure ground dyeing was fully washed off (Miles Ch. 6.2.2)."
            )

    # Maintenance overdue
    maint_ratio = (params.operating_hours_since_maintenance
                   / max(1.0, params.maintenance_interval_hours))
    if maint_ratio > 1.0:
        warnings.append(
            f"Machine is overdue for maintenance ({params.operating_hours_since_maintenance:.0f} h "
            f"since service; interval {params.maintenance_interval_hours:.0f} h). "
            "Worn blankets lose adhesive tack → fabric slips → registration errors. "
            "Blocked screen pores, worn squeegee holders and blanket washing systems "
            "degrade print quality and increase downtime."
        )

    # ── RUN SIMULATION MODELS ─────────────────────────────────────────────────

    paste_volume = predict_paste_volume_applied(
        params.screen_open_area_pct,
        params.screen_mesh_threads_per_cm,
        params.squeegee_type,
        params.squeegee_angle_deg,
        params.number_of_squeegee_passes,
        params.flood_stroke,
        fabric.fabric_surface_texture,
        fabric.fabric_weight_g_per_m2
    )

    penetration = predict_paste_penetration(
        paste_volume,
        params.paste_viscosity_Pa_s,
        fabric.fabric_cover_factor,
        fabric.fabric_surface_texture,
        params.number_of_squeegee_passes
    )

    sharpness = predict_sharpness_of_mark(
        params.paste_viscosity_Pa_s,
        params.screen_mesh_threads_per_cm,
        params.design_coverage_pct,
        params.printing_speed_m_per_hour,
        fabric.fabric_surface_texture,
        params.thickener_type
    )

    saw_tooth = predict_saw_tooth_risk(
        params.screen_mesh_threads_per_cm,
        params.design_coverage_pct
    )

    registration = predict_registration_accuracy(
        params.machine_type,
        params.number_of_colours,
        params.adhesive_type,
        params.blanket_type,
        params.printing_speed_m_per_hour,
        params.operating_hours_since_maintenance,
        params.maintenance_interval_hours
    )

    frame_mark_risk = predict_frame_mark_risk(
        params.machine_type,
        params.design_coverage_pct,
        params.printing_speed_m_per_hour,
        params.off_contact_printing,
        params.number_of_colours
    )

    crushing_risk = predict_colour_crushing_risk(
        params.machine_type,
        params.printing_speed_m_per_hour,
        params.number_of_colours,
        params.colorant_type,
        params.off_contact_printing
    )

    blockage_risk = predict_screen_blockage_risk(
        params.thickener_type,
        params.paste_viscosity_Pa_s,
        params.screen_mesh_threads_per_cm,
        params.ambient_temperature_C,
        params.ambient_humidity_pct,
        params.printing_speed_m_per_hour,
        params.machine_type
    )

    bleeding_risk = predict_paste_bleeding_risk(
        params.paste_viscosity_Pa_s,
        params.thickener_type,
        params.design_coverage_pct,
        fabric.fabric_cover_factor,
        fabric.residual_unfixed_dye_pct
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
        penetration
    )

    wash_fastness = predict_wash_fastness(
        params.colorant_type,
        fabric.fiber_type,
        fixation_pct,
        params.wash_off_applied,
        params.wash_off_temperature_C,
        params.wash_off_stages,
        penetration,
        params.binder_concentration_pct
    )

    light_fastness = predict_light_fastness(
        params.colorant_type,
        fabric.fiber_type,
        params.paste_colorant_concentration_g_per_kg,
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
        params.paste_colorant_concentration_g_per_kg,
        fixation_pct,
        penetration,
        fabric.ground_colour_yield
    )

    # Colour yield as pct of maximum theoretical
    colour_yield_pct = round(colour_yield_rel * 100.0, 1)

    unfixed_staining_risk = predict_unfixed_dye_staining_risk(
        params.colorant_type,
        fixation_pct,
        params.wash_off_applied,
        params.wash_off_temperature_C,
        params.wash_off_stages,
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

    total_water = predict_water_consumption(
        fabric.upstream_water_L_per_kg,
        params.wash_off_applied,
        params.wash_off_stages,
        params.colorant_type
    )

    # Effluent dye load: dyeing stage effluent + printing unfixed dye
    print_unfixed_pct = 100.0 - fixation_pct
    if params.colorant_type == "pigment":
        print_unfixed_pct = 0.0  # pigment: no soluble dye discharged
    total_effluent_pct = round(
        (100.0 - fabric.dye_fixation_pct) / 100.0 * 50.0 +  # dyeing contribution (simplified)
        print_unfixed_pct * 0.5,  # printing contribution
        1
    )

    # Energy index: pigment saves energy (no steaming, no washing)
    if params.colorant_type == "pigment":
        energy_index = 0.6
    elif params.fixation_method == "high_temp_steam":
        energy_index = 1.2  # HT steamers are more energy-intensive
    else:
        energy_index = 1.0

    machine_efficiency = predict_machine_efficiency(
        params.machine_type,
        params.number_of_colours,
        params.colorant_type,
        params.dryer_efficiency,
        params.design_coverage_pct,
        params.operating_hours_since_maintenance,
        params.maintenance_interval_hours
    )

    effective_production = round(
        params.printing_speed_m_per_hour * machine_efficiency / 100.0, 1
    )

    # ── POST-SIMULATION WARNINGS ──────────────────────────────────────────────

    if sharpness == "poor":
        warnings.append(
            "Sharpness of mark is rated POOR. The combination of low paste viscosity, "
            "coarse screen mesh, and/or high design coverage is allowing excessive "
            "capillary spread. Consider increasing thickener concentration, switching "
            "to a 'short' flow thickener (crystal gum or synthetic polyacrylic), or "
            "using a finer-mesh screen (Miles Ch. 7.1, Ch. 2.7.2)."
        )

    if fixation_pct < 60:
        warnings.append(
            f"CRITICAL: Estimated fixation is only {fixation_pct:.0f}%. This is very low. "
            "A large proportion of the colorant will be washed off, producing weak colours "
            "and heavy effluent dye load. Review fixation conditions: temperature, time, "
            "alkali concentration (reactive), and steam quality (Miles Ch. 8.3.5)."
        )

    if unfixed_staining_risk == "high":
        warnings.append(
            "Unfixed dye staining risk is HIGH. White and pale areas of the design are "
            "at serious risk of being contaminated with the hydrolysed/unfixed dye "
            "removed during wash-off. Increase wash-off temperature to ≥90°C and ensure "
            "≥6 wash stages with counterflow (Miles Ch. 8.5, Fig. 8.12)."
        )

    if binder_quality == "poor" and params.colorant_type == "pigment":
        warnings.append(
            "CRITICAL: Binder crosslink quality is POOR for this pigment print. "
            "Insufficient binder and/or suboptimal curing conditions will result in "
            "weak wash and rub fastness. Increase binder to ≥7% on paste weight and "
            "cure at 140–160°C for ≥3 min in hot air (Miles Ch. 5.2.2, Ch. 8.2)."
        )

    if blockage_risk == "high":
        warnings.append(
            "Screen blockage risk is HIGH. Print paste is likely to dry in the screen "
            "pores, especially at slow printing speeds and low humidity. Use print paste "
            "with better stability (add preservative), increase printing speed, maintain "
            "ambient humidity at 55–65%, and schedule regular screen flushing."
        )

    if bleeding_risk == "high":
        warnings.append(
            "Paste bleeding risk is HIGH. Excessive capillary spread will produce "
            "blurred outlines and colour mixing at boundaries. Increase paste viscosity, "
            "use a 'short' flow thickener, reduce the amount of paste applied, or "
            "increase printing speed to reduce contact time (Miles Ch. 7.1, 7.7.5)."
        )

    return PrintedFabricOutput(
        paste_volume_applied_g_per_m2=paste_volume,
        paste_penetration_depth=penetration,
        colour_yield_pct=colour_yield_pct,
        sharpness_of_mark=sharpness,
        saw_tooth_effect_risk=saw_tooth,
        registration_accuracy=registration,
        frame_mark_risk=frame_mark_risk,
        colour_crushing_risk=crushing_risk,
        screen_blockage_risk=blockage_risk,
        paste_bleeding_risk=bleeding_risk,
        print_wash_fastness=wash_fastness,
        print_light_fastness=light_fastness,
        print_rub_fastness_dry=dry_rub,
        print_rub_fastness_wet=wet_rub,
        colour_yield_relative=colour_yield_rel,
        estimated_fixation_pct=fixation_pct,
        unfixed_dye_staining_risk=unfixed_staining_risk,
        binder_crosslink_quality=binder_quality,
        total_water_L_per_kg=total_water,
        total_effluent_dye_load_pct=total_effluent_pct,
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
    print("SCREEN PRINTING SIMULATION")
    print("Based on Miles, L.W.C. (Ed.), Textile Printing, SDC, 2003")
    print("=" * 72)

    # ── SCENARIO 1: Reactive dye print on cotton using rotary screen ─────────
    # Input: mercerised cotton, reactive-dyed mid-blue ground (from dyeing
    # simulation output), now to receive a multi-colour floral design.
    print("\n--- SCENARIO 1: Reactive dye 8-colour floral on cotton, rotary screen ---\n")

    fabric_1 = InputDyedFabric(
        fiber_type="cotton",
        fabric_weight_g_per_m2=130.0,
        fabric_cover_factor=0.92,
        fabric_width_cm=152.0,
        fabric_surface_texture="smooth",
        # From reactive dyeing Layer 4 output:
        substrate_pH=7.2,               # well washed, near neutral
        dye_exhaustion_pct=82.0,
        dye_fixation_pct=74.0,
        unfixed_hydrolysed_dye_pct=8.0, # properly washed off
        residual_unfixed_dye_pct=2.0,   # small residual acceptable
        ground_colour_yield=0.78,
        ground_wash_fastness=4.5,
        ground_light_fastness=6.0,
        ground_levelness_risk="low",
        ground_dye_penetration="full",
        upstream_water_L_per_kg=38.0,
        upstream_salt_g_per_kg=65.0,
        substrate_damage_risk="low",
    )

    params_1 = ScreenPrintingOperationalParams(
        machine_type="rotary",
        printing_speed_m_per_hour=2400.0,   # 40 m/min — standard rotary
        number_of_colours=8,
        screen_type="lacquer_rotary",
        screen_mesh_threads_per_cm=60.0,    # standard 60 mesh for motifs
        screen_open_area_pct=11.0,          # lacquer screen: 9–13%
        screen_circumference_mm=640.0,      # standard rotary circumference
        design_repeat_length_cm=32.0,       # 2 repeats per screen revolution ✓
        squeegee_type="steel_blade",
        squeegee_angle_deg=70.0,
        squeegee_hardness_shore=65,
        number_of_squeegee_passes=1,
        flood_stroke=False,
        adhesive_type="thermoplastic",
        blanket_type="laminated_neoprene",
        off_contact_printing=False,
        colorant_type="reactive_dye",
        paste_colorant_concentration_g_per_kg=45.0,
        thickener_type="alginate",          # required for reactive dyes
        thickener_concentration_pct=3.5,
        paste_viscosity_Pa_s=2.0,
        binder_concentration_pct=0.0,       # no binder for dye-based
        urea_concentration_g_per_kg=120.0,
        alkali_type="sodium_bicarbonate",
        alkali_concentration_g_per_kg=20.0,
        design_coverage_pct=35.0,           # multi-colour floral: moderate coverage
        fixation_method="saturated_steam",
        fixation_temperature_C=102.0,
        fixation_time_min=12.0,
        dryer_efficiency="high",
        wash_off_applied=True,
        wash_off_temperature_C=92.0,
        wash_off_stages=8,
        ambient_temperature_C=24.0,
        ambient_humidity_pct=60.0,
        last_maintenance_date="2025-10-01",
        maintenance_interval_hours=1200.0,
        operating_hours_since_maintenance=300.0,
    )

    result_1 = simulate_screen_printing(fabric_1, params_1)

    print(f"  Paste Volume Applied:         {result_1.paste_volume_applied_g_per_m2} g/m²")
    print(f"  Paste Penetration:            {result_1.paste_penetration_depth.upper()}")
    print(f"  Colour Yield:                 {result_1.colour_yield_pct}%")
    print(f"  Relative Colour Yield:        {result_1.colour_yield_relative}")
    print(f"  Sharpness of Mark:            {result_1.sharpness_of_mark.upper()}")
    print(f"  Saw-Tooth Effect Risk:        {result_1.saw_tooth_effect_risk.upper()}")
    print(f"  Registration Accuracy:        {result_1.registration_accuracy.upper()}")
    print(f"  Frame Mark Risk:              {result_1.frame_mark_risk.upper()}")
    print(f"  Colour Crushing Risk:         {result_1.colour_crushing_risk.upper()}")
    print(f"  Screen Blockage Risk:         {result_1.screen_blockage_risk.upper()}")
    print(f"  Paste Bleeding Risk:          {result_1.paste_bleeding_risk.upper()}")
    print(f"  Estimated Fixation:           {result_1.estimated_fixation_pct}%")
    print(f"  Wash Fastness (ISO):          {result_1.print_wash_fastness} / 5")
    print(f"  Light Fastness (ISO):         {result_1.print_light_fastness} / 8")
    print(f"  Rub Fastness Dry/Wet:         {result_1.print_rub_fastness_dry} / {result_1.print_rub_fastness_wet}")
    print(f"  Unfixed Dye Staining Risk:    {result_1.unfixed_dye_staining_risk.upper()}")
    print(f"  Total Water Used:             {result_1.total_water_L_per_kg} L/kg")
    print(f"  Machine Efficiency:           {result_1.machine_efficiency_pct}%")
    print(f"  Effective Production:         {result_1.effective_production_m_per_hour} m/h")
    if result_1.warnings:
        print(f"\n  WARNINGS:")
        for w in result_1.warnings:
            print(f"    ⚠  {w}")
    else:
        print("\n  No warnings — all parameters within recommended ranges.")

    # ── SCENARIO 2: Pigment print, automatic flat-screen, furnishing fabric ──
    # Input: undyed (ecru) or lightly dyed cotton furnishing fabric.
    print("\n--- SCENARIO 2: Pigment blotch print, auto flat-screen, furnishing fabric ---\n")

    fabric_2 = InputDyedFabric(
        fiber_type="cotton",
        fabric_weight_g_per_m2=220.0,       # heavy furnishing weight
        fabric_cover_factor=1.05,
        fabric_width_cm=140.0,
        fabric_surface_texture="textured",   # slub texture, irregular surface
        substrate_pH=7.0,
        dye_exhaustion_pct=0.0,             # undyed substrate (ecru)
        dye_fixation_pct=0.0,
        unfixed_hydrolysed_dye_pct=0.0,
        residual_unfixed_dye_pct=0.0,
        ground_colour_yield=0.0,            # white/natural ground
        ground_wash_fastness=5.0,
        ground_light_fastness=8.0,
        ground_levelness_risk="low",
        ground_dye_penetration="full",
        upstream_water_L_per_kg=5.0,        # only scouring water
        upstream_salt_g_per_kg=0.0,
        substrate_damage_risk="low",
    )

    params_2 = ScreenPrintingOperationalParams(
        machine_type="automatic_flat",
        printing_speed_m_per_hour=400.0,    # mid-range for flat-screen furnishing
        number_of_colours=12,               # typical for furnishing repeat
        screen_type="flat_polyester_mesh",
        screen_mesh_threads_per_cm=43.0,    # large blotches: 43–49 threads/cm
        screen_open_area_pct=41.0,
        screen_circumference_mm=0.0,        # N/A for flat screen
        design_repeat_length_cm=64.0,       # large furnishing repeat
        squeegee_type="rubber_blade",
        squeegee_angle_deg=75.0,
        squeegee_hardness_shore=55,         # softer blade for blotch areas
        number_of_squeegee_passes=2,        # 2 passes for thick fabric coverage
        flood_stroke=True,
        adhesive_type="thermoplastic",
        blanket_type="laminated_neoprene",
        off_contact_printing=True,          # reduce frame marks
        colorant_type="pigment",
        paste_colorant_concentration_g_per_kg=80.0,  # medium-deep colour
        thickener_type="synthetic_polyacrylic",
        thickener_concentration_pct=1.0,
        paste_viscosity_Pa_s=3.5,
        binder_concentration_pct=12.0,      # generous binder for fastness
        urea_concentration_g_per_kg=10.0,   # small amount to prevent drying
        alkali_type="diammonium_phosphate",  # acid-promoting for crosslinking
        alkali_concentration_g_per_kg=20.0,
        design_coverage_pct=65.0,           # moderate-high blotch coverage
        fixation_method="baking_hot_air",
        fixation_temperature_C=150.0,
        fixation_time_min=4.0,
        dryer_efficiency="adequate",
        wash_off_applied=False,             # pigment: no wash-off required
        wash_off_temperature_C=0.0,
        wash_off_stages=0,
        ambient_temperature_C=22.0,
        ambient_humidity_pct=55.0,
        last_maintenance_date="2025-09-15",
        maintenance_interval_hours=1000.0,
        operating_hours_since_maintenance=450.0,
    )

    result_2 = simulate_screen_printing(fabric_2, params_2)

    print(f"  Paste Volume Applied:         {result_2.paste_volume_applied_g_per_m2} g/m²")
    print(f"  Colour Yield:                 {result_2.colour_yield_pct}%")
    print(f"  Sharpness of Mark:            {result_2.sharpness_of_mark.upper()}")
    print(f"  Registration Accuracy:        {result_2.registration_accuracy.upper()}")
    print(f"  Frame Mark Risk:              {result_2.frame_mark_risk.upper()}")
    print(f"  Colour Crushing Risk:         {result_2.colour_crushing_risk.upper()}")
    print(f"  Estimated Fixation:           {result_2.estimated_fixation_pct}%")
    print(f"  Binder Crosslink Quality:     {result_2.binder_crosslink_quality.upper()}")
    print(f"  Wash Fastness (ISO):          {result_2.print_wash_fastness} / 5")
    print(f"  Light Fastness (ISO):         {result_2.print_light_fastness} / 8")
    print(f"  Rub Fastness Dry/Wet:         {result_2.print_rub_fastness_dry} / {result_2.print_rub_fastness_wet}")
    print(f"  Total Water Used:             {result_2.total_water_L_per_kg} L/kg")
    print(f"  Energy Index:                 {result_2.energy_index} (vs 1.0 conventional)")
    print(f"  Machine Efficiency:           {result_2.machine_efficiency_pct}%")
    print(f"  Effective Production:         {result_2.effective_production_m_per_hour} m/h")
    if result_2.warnings:
        print(f"\n  WARNINGS:")
        for w in result_2.warnings:
            print(f"    ⚠  {w}")
    else:
        print("\n  No warnings — all parameters within recommended ranges.")

    # ── SCENARIO 3: Stress test — multiple deliberate faults ─────────────────
    # Reactive dye without alginate, no alkali, wrong fixation, no wash-off.
    print("\n--- SCENARIO 3: Stress test — misconfigured reactive print ---\n")

    fabric_3 = InputDyedFabric(
        fiber_type="cotton",
        fabric_weight_g_per_m2=100.0,
        fabric_cover_factor=0.85,
        fabric_width_cm=150.0,
        fabric_surface_texture="smooth",
        substrate_pH=9.5,               # alkaline residue from dyeing
        dye_exhaustion_pct=70.0,
        dye_fixation_pct=55.0,
        unfixed_hydrolysed_dye_pct=15.0,  # poor wash-off in dyeing
        residual_unfixed_dye_pct=8.0,    # high residual unfixed dye
        ground_colour_yield=0.60,
        ground_wash_fastness=3.5,
        ground_light_fastness=5.5,
        ground_levelness_risk="high",
        ground_dye_penetration="partial",
        upstream_water_L_per_kg=55.0,
        upstream_salt_g_per_kg=90.0,
        substrate_damage_risk="high",    # high from poor dyeing control
    )

    params_3 = ScreenPrintingOperationalParams(
        machine_type="automatic_flat",
        printing_speed_m_per_hour=700.0,    # too fast for auto flat screen
        number_of_colours=15,
        screen_type="flat_polyester_mesh",
        screen_mesh_threads_per_cm=30.0,    # coarse mesh — wrong for fine design
        screen_open_area_pct=47.0,          # very open → too much paste
        screen_circumference_mm=0.0,
        design_repeat_length_cm=80.0,       # very large repeat
        squeegee_type="rubber_blade",
        squeegee_angle_deg=42.0,            # too shallow → excessive paste
        squeegee_hardness_shore=50,
        number_of_squeegee_passes=3,
        flood_stroke=True,
        adhesive_type="water_based",        # poor adhesion at high speed
        blanket_type="neoprene_rubber",
        off_contact_printing=False,
        colorant_type="reactive_dye",
        paste_colorant_concentration_g_per_kg=80.0,
        thickener_type="starch_ether",      # WRONG for reactive dyes
        thickener_concentration_pct=8.0,
        paste_viscosity_Pa_s=0.5,           # too thin → bleeding
        binder_concentration_pct=0.0,
        urea_concentration_g_per_kg=200.0,
        alkali_type="none",                 # NO ALKALI — critical fault
        alkali_concentration_g_per_kg=0.0,
        design_coverage_pct=80.0,           # heavy blotch
        fixation_method="baking_hot_air",   # WRONG for reactive dyes
        fixation_temperature_C=150.0,
        fixation_time_min=4.0,
        dryer_efficiency="low",             # inadequate dryer
        wash_off_applied=False,             # no wash-off applied
        wash_off_temperature_C=0.0,
        wash_off_stages=0,
        ambient_temperature_C=32.0,         # too hot → paste dries in screen
        ambient_humidity_pct=30.0,          # too dry → screen blockage
        last_maintenance_date="2023-06-01",
        maintenance_interval_hours=500.0,
        operating_hours_since_maintenance=1200.0,  # severely overdue
    )

    result_3 = simulate_screen_printing(fabric_3, params_3)

    print(f"  Paste Volume Applied:         {result_3.paste_volume_applied_g_per_m2} g/m²")
    print(f"  Paste Penetration:            {result_3.paste_penetration_depth.upper()}")
    print(f"  Sharpness of Mark:            {result_3.sharpness_of_mark.upper()}")
    print(f"  Estimated Fixation:           {result_3.estimated_fixation_pct}%")
    print(f"  Wash Fastness (ISO):          {result_3.print_wash_fastness} / 5")
    print(f"  Light Fastness (ISO):         {result_3.print_light_fastness} / 8")
    print(f"  Rub Fastness Dry/Wet:         {result_3.print_rub_fastness_dry} / {result_3.print_rub_fastness_wet}")
    print(f"  Screen Blockage Risk:         {result_3.screen_blockage_risk.upper()}")
    print(f"  Paste Bleeding Risk:          {result_3.paste_bleeding_risk.upper()}")
    print(f"  Frame Mark Risk:              {result_3.frame_mark_risk.upper()}")
    print(f"  Registration Accuracy:        {result_3.registration_accuracy.upper()}")
    print(f"  Unfixed Dye Staining Risk:    {result_3.unfixed_dye_staining_risk.upper()}")
    print(f"  Machine Efficiency:           {result_3.machine_efficiency_pct}%")
    print(f"  Effective Production:         {result_3.effective_production_m_per_hour} m/h")
    if result_3.warnings:
        print(f"\n  WARNINGS ({len(result_3.warnings)} issues detected):")
        for w in result_3.warnings:
            print(f"    ⚠  {w}")

    print("\n" + "=" * 72)
    print("Simulation complete.")
    print("=" * 72)
