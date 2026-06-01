import z from "zod";
import {
  Factory,
  type LucideIcon,
  Bot,
  Hammer,
  Move3d,
  Scan,
  Wrench,
  Zap,
} from "lucide-react";

export const ICON_MAP: Record<string, LucideIcon> = {
  Factory,
  Hammer,
  Move3d,
  Bot,
  Scan,
  Zap,
  Wrench,
};

export enum MachineProcess {
  SPINNING = "spinning",
  WEAVING = "weaving",
  KNITTING = "knitting",
  COLORING = "coloring",
  PRINTING = "printing",
  FINISHING = "finishing",
  SEWING = "sewing",
  COATING = "coating",
  LAMINATING = "laminating",
  EMBROIDERY = "embroidery",
  FELTING = "felting",
}

export type AttributeType = "number" | "string" | "boolean" | "enum";

export interface AttributeDefinition {
  id: string;
  name: string;
  type: AttributeType;
  unit?: string;
  description?: string;
  options?: string[]; // for enum
  defaultValue?: any;
}

export interface AttributeInstance {
  definition: AttributeDefinition;
  value: any;
}

export interface ProcessAttributes {
  inputs: Record<string, AttributeInstance>;
  configs: Record<string, AttributeInstance>;
  outputs: Record<string, AttributeInstance>;
}

export interface BaseMachine {
  id: string;
  name: string;
  process: MachineProcess;
  sub_process?: string;
  manufacturer?: string;
  model_reference?: string;
  release_year?: number;
  description: string;
  icon: string;
  color: string; // UI property
}

export interface Machine extends BaseMachine {
  attributes: ProcessAttributes;
}

export interface MachineTypeConfig {
  process: MachineProcess;
  subprocess: string;
  name: string;
  description: string;
  color: string;
  icon: string;
  defaultAttributes: ProcessAttributes;
}

export const ROTOR_SPINNING_INPUT_DEFS: Record<string, AttributeDefinition> = {
  fiber_type: { id: "fiber_type", name: "Fiber Type", type: "string" },
  fiber_length_mm: {
    id: "fiber_length_mm",
    name: "Fiber Length Mm",
    type: "number",
  },
  fiber_fineness_dtex: {
    id: "fiber_fineness_dtex",
    name: "Fiber Fineness Dtex",
    type: "number",
  },
  short_fiber_content_pct: {
    id: "short_fiber_content_pct",
    name: "Short Fiber Content Pct",
    type: "number",
  },
  fiber_tensile_strength_cN_tex: {
    id: "fiber_tensile_strength_cN_tex",
    name: "Fiber Tensile Strength Cn Tex",
    type: "number",
  },
  sliver_count_ktex: {
    id: "sliver_count_ktex",
    name: "Sliver Count Ktex",
    type: "number",
  },
  moisture_content_pct: {
    id: "moisture_content_pct",
    name: "Moisture Content Pct",
    type: "number",
  },
  trash_content_pct: {
    id: "trash_content_pct",
    name: "Trash Content Pct",
    type: "number",
  },
};
export const ROTOR_SPINNING_CONFIG_DEFS: Record<string, AttributeDefinition> = {
  rotor_diameter_mm: {
    id: "rotor_diameter_mm",
    name: "Rotor Diameter Mm",
    type: "number",
  },
  rotor_speed_rpm: {
    id: "rotor_speed_rpm",
    name: "Rotor Speed Rpm",
    type: "number",
  },
  twist_factor_am: {
    id: "twist_factor_am",
    name: "Twist Factor Am",
    type: "number",
  },
  opening_roller_speed_rpm: {
    id: "opening_roller_speed_rpm",
    name: "Opening Roller Speed Rpm",
    type: "number",
  },
  opening_roller_wire_type: {
    id: "opening_roller_wire_type",
    name: "Opening Roller Wire Type",
    type: "string",
  },
  navel_type: { id: "navel_type", name: "Navel Type", type: "string" },
  rotor_groove_type: {
    id: "rotor_groove_type",
    name: "Rotor Groove Type",
    type: "string",
  },
  total_draft_ratio: {
    id: "total_draft_ratio",
    name: "Total Draft Ratio",
    type: "number",
  },
  delivery_speed_m_min: {
    id: "delivery_speed_m_min",
    name: "Delivery Speed M Min",
    type: "number",
  },
  yarn_count_Ne: { id: "yarn_count_Ne", name: "Yarn Count Ne", type: "number" },
  yarn_count_tex: {
    id: "yarn_count_tex",
    name: "Yarn Count Tex",
    type: "number",
  },
  ambient_temperature_C: {
    id: "ambient_temperature_C",
    name: "Ambient Temperature C",
    type: "number",
  },
  ambient_humidity_pct: {
    id: "ambient_humidity_pct",
    name: "Ambient Humidity Pct",
    type: "number",
  },
  last_maintenance_date: {
    id: "last_maintenance_date",
    name: "Last Maintenance Date",
    type: "string",
  },
  maintenance_interval_hours: {
    id: "maintenance_interval_hours",
    name: "Maintenance Interval Hours",
    type: "number",
  },
  operating_hours_since_maintenance: {
    id: "operating_hours_since_maintenance",
    name: "Operating Hours Since Maintenance",
    type: "number",
  },
};
export const ROTOR_SPINNING_OUTPUT_DEFS: Record<string, AttributeDefinition> = {
  actual_twist_turns_per_m: {
    id: "actual_twist_turns_per_m",
    name: "Actual Twist Turns Per M",
    type: "number",
  },
  back_doubling_index: {
    id: "back_doubling_index",
    name: "Back Doubling Index",
    type: "number",
  },
  yarn_tenacity_cN_tex: {
    id: "yarn_tenacity_cN_tex",
    name: "Yarn Tenacity Cn Tex",
    type: "number",
  },
  yarn_evenness_CVm_pct: {
    id: "yarn_evenness_CVm_pct",
    name: "Yarn Evenness Cvm Pct",
    type: "number",
  },
  hairiness_H: { id: "hairiness_H", name: "Hairiness H", type: "number" },
  neps_per_km: { id: "neps_per_km", name: "Neps Per Km", type: "number" },
  spinning_tension_cN: {
    id: "spinning_tension_cN",
    name: "Spinning Tension Cn",
    type: "number",
  },
  waste_fiber_pct: {
    id: "waste_fiber_pct",
    name: "Waste Fiber Pct",
    type: "number",
  },
  ends_down_risk: {
    id: "ends_down_risk",
    name: "Ends Down Risk",
    type: "string",
  },
  production_rate_g_rotor_h: {
    id: "production_rate_g_rotor_h",
    name: "Production Rate G Rotor H",
    type: "number",
  },
  warnings: { id: "warnings", name: "Warnings", type: "string" },
};

export const AIRJET_SPINNING_INPUT_DEFS: Record<string, AttributeDefinition> = {
  fiber_type: { id: "fiber_type", name: "Fiber Type", type: "string" },
  fiber_length_mm: {
    id: "fiber_length_mm",
    name: "Fiber Length Mm",
    type: "number",
  },
  fiber_fineness_dtex: {
    id: "fiber_fineness_dtex",
    name: "Fiber Fineness Dtex",
    type: "number",
  },
  short_fiber_content_pct: {
    id: "short_fiber_content_pct",
    name: "Short Fiber Content Pct",
    type: "number",
  },
  fiber_tensile_strength_cN_tex: {
    id: "fiber_tensile_strength_cN_tex",
    name: "Fiber Tensile Strength Cn Tex",
    type: "number",
  },
  sliver_count_ktex: {
    id: "sliver_count_ktex",
    name: "Sliver Count Ktex",
    type: "number",
  },
  moisture_content_pct: {
    id: "moisture_content_pct",
    name: "Moisture Content Pct",
    type: "number",
  },
  trash_content_pct: {
    id: "trash_content_pct",
    name: "Trash Content Pct",
    type: "number",
  },
};
export const AIRJET_SPINNING_CONFIG_DEFS: Record<string, AttributeDefinition> =
{
  total_draft_ratio: {
    id: "total_draft_ratio",
    name: "Total Draft Ratio",
    type: "number",
  },
  pre_draft_ratio: {
    id: "pre_draft_ratio",
    name: "Pre Draft Ratio",
    type: "number",
  },
  break_draft_ratio: {
    id: "break_draft_ratio",
    name: "Break Draft Ratio",
    type: "number",
  },
  main_draft_ratio: {
    id: "main_draft_ratio",
    name: "Main Draft Ratio",
    type: "number",
  },
  draft_zone_distance_A_mm: {
    id: "draft_zone_distance_A_mm",
    name: "Draft Zone Distance A Mm",
    type: "number",
  },
  draft_zone_distance_B_mm: {
    id: "draft_zone_distance_B_mm",
    name: "Draft Zone Distance B Mm",
    type: "number",
  },
  air_pressure_bar: {
    id: "air_pressure_bar",
    name: "Air Pressure Bar",
    type: "number",
  },
  distance_L_mm: {
    id: "distance_L_mm",
    name: "Distance L Mm",
    type: "number",
  },
  delivery_speed_m_min: {
    id: "delivery_speed_m_min",
    name: "Delivery Speed M Min",
    type: "number",
  },
  spinning_draft: {
    id: "spinning_draft",
    name: "Spinning Draft",
    type: "number",
  },
  package_diameter_mm: {
    id: "package_diameter_mm",
    name: "Package Diameter Mm",
    type: "number",
  },
  yarn_count_Ne: {
    id: "yarn_count_Ne",
    name: "Yarn Count Ne",
    type: "number",
  },
  yarn_count_tex: {
    id: "yarn_count_tex",
    name: "Yarn Count Tex",
    type: "number",
  },
  ambient_temperature_C: {
    id: "ambient_temperature_C",
    name: "Ambient Temperature C",
    type: "number",
  },
  ambient_humidity_pct: {
    id: "ambient_humidity_pct",
    name: "Ambient Humidity Pct",
    type: "number",
  },
  last_maintenance_date: {
    id: "last_maintenance_date",
    name: "Last Maintenance Date",
    type: "string",
  },
  maintenance_interval_hours: {
    id: "maintenance_interval_hours",
    name: "Maintenance Interval Hours",
    type: "number",
  },
  operating_hours_since_maintenance: {
    id: "operating_hours_since_maintenance",
    name: "Operating Hours Since Maintenance",
    type: "number",
  },
};
export const AIRJET_SPINNING_OUTPUT_DEFS: Record<string, AttributeDefinition> =
{
  wrapping_twist_am: {
    id: "wrapping_twist_am",
    name: "Wrapping Twist Am",
    type: "number",
  },
  wrapping_fiber_pct: {
    id: "wrapping_fiber_pct",
    name: "Wrapping Fiber Pct",
    type: "number",
  },
  yarn_tenacity_cN_tex: {
    id: "yarn_tenacity_cN_tex",
    name: "Yarn Tenacity Cn Tex",
    type: "number",
  },
  yarn_evenness_CVm_pct: {
    id: "yarn_evenness_CVm_pct",
    name: "Yarn Evenness Cvm Pct",
    type: "number",
  },
  hairiness_H: { id: "hairiness_H", name: "Hairiness H", type: "number" },
  neps_per_km: { id: "neps_per_km", name: "Neps Per Km", type: "number" },
  spinning_tension_cN: {
    id: "spinning_tension_cN",
    name: "Spinning Tension Cn",
    type: "number",
  },
  waste_fiber_pct: {
    id: "waste_fiber_pct",
    name: "Waste Fiber Pct",
    type: "number",
  },
  ends_down_risk: {
    id: "ends_down_risk",
    name: "Ends Down Risk",
    type: "string",
  },
  production_rate_g_spi_h: {
    id: "production_rate_g_spi_h",
    name: "Production Rate G Spi H",
    type: "number",
  },
  warnings: { id: "warnings", name: "Warnings", type: "string" },
};

export const PLAIN_WEAVING_INPUT_DEFS: Record<string, AttributeDefinition> = {
  warp_yarn_count_tex: {
    id: "warp_yarn_count_tex",
    name: "Warp Yarn Count Tex",
    type: "number",
  },
  warp_yarn_count_Ne: {
    id: "warp_yarn_count_Ne",
    name: "Warp Yarn Count Ne",
    type: "number",
  },
  warp_yarn_tenacity_cN_tex: {
    id: "warp_yarn_tenacity_cN_tex",
    name: "Warp Yarn Tenacity Cn Tex",
    type: "number",
  },
  warp_yarn_CVm_pct: {
    id: "warp_yarn_CVm_pct",
    name: "Warp Yarn Cvm Pct",
    type: "number",
  },
  warp_yarn_hairiness_H: {
    id: "warp_yarn_hairiness_H",
    name: "Warp Yarn Hairiness H",
    type: "number",
  },
  warp_yarn_twist_t_per_m: {
    id: "warp_yarn_twist_t_per_m",
    name: "Warp Yarn Twist T Per M",
    type: "number",
  },
  warp_yarn_type: {
    id: "warp_yarn_type",
    name: "Warp Yarn Type",
    type: "string",
  },
  weft_yarn_count_tex: {
    id: "weft_yarn_count_tex",
    name: "Weft Yarn Count Tex",
    type: "number",
  },
  weft_yarn_count_Ne: {
    id: "weft_yarn_count_Ne",
    name: "Weft Yarn Count Ne",
    type: "number",
  },
  weft_yarn_tenacity_cN_tex: {
    id: "weft_yarn_tenacity_cN_tex",
    name: "Weft Yarn Tenacity Cn Tex",
    type: "number",
  },
  weft_yarn_CVm_pct: {
    id: "weft_yarn_CVm_pct",
    name: "Weft Yarn Cvm Pct",
    type: "number",
  },
  weft_yarn_hairiness_H: {
    id: "weft_yarn_hairiness_H",
    name: "Weft Yarn Hairiness H",
    type: "number",
  },
  weft_yarn_twist_t_per_m: {
    id: "weft_yarn_twist_t_per_m",
    name: "Weft Yarn Twist T Per M",
    type: "number",
  },
  weft_yarn_type: {
    id: "weft_yarn_type",
    name: "Weft Yarn Type",
    type: "string",
  },
};
export const PLAIN_WEAVING_CONFIG_DEFS: Record<string, AttributeDefinition> = {
  ends_per_cm: { id: "ends_per_cm", name: "Ends Per Cm", type: "number" },
  picks_per_cm: { id: "picks_per_cm", name: "Picks Per Cm", type: "number" },
  reed_width_cm: { id: "reed_width_cm", name: "Reed Width Cm", type: "number" },
  loom_speed_picks_per_min: {
    id: "loom_speed_picks_per_min",
    name: "Loom Speed Picks Per Min",
    type: "number",
  },
  loom_type: { id: "loom_type", name: "Loom Type", type: "string" },
  warp_tension_cN_per_end: {
    id: "warp_tension_cN_per_end",
    name: "Warp Tension Cn Per End",
    type: "number",
  },
  let_off_type: { id: "let_off_type", name: "Let Off Type", type: "string" },
  take_up_type: { id: "take_up_type", name: "Take Up Type", type: "string" },
  shed_depth_cm: { id: "shed_depth_cm", name: "Shed Depth Cm", type: "number" },
  heald_shaft_count: {
    id: "heald_shaft_count",
    name: "Heald Shaft Count",
    type: "number",
  },
  temple_type: { id: "temple_type", name: "Temple Type", type: "string" },
  ambient_temperature_C: {
    id: "ambient_temperature_C",
    name: "Ambient Temperature C",
    type: "number",
  },
  ambient_humidity_pct: {
    id: "ambient_humidity_pct",
    name: "Ambient Humidity Pct",
    type: "number",
  },
  maintenance_interval_hours: {
    id: "maintenance_interval_hours",
    name: "Maintenance Interval Hours",
    type: "number",
  },
  operating_hours_since_maintenance: {
    id: "operating_hours_since_maintenance",
    name: "Operating Hours Since Maintenance",
    type: "number",
  },
};
export const PLAIN_WEAVING_OUTPUT_DEFS: Record<string, AttributeDefinition> = {
  yarn_diameter_warp_mm: {
    id: "yarn_diameter_warp_mm",
    name: "Yarn Diameter Warp Mm",
    type: "number",
  },
  yarn_diameter_weft_mm: {
    id: "yarn_diameter_weft_mm",
    name: "Yarn Diameter Weft Mm",
    type: "number",
  },
  warp_cover_factor: {
    id: "warp_cover_factor",
    name: "Warp Cover Factor",
    type: "number",
  },
  weft_cover_factor: {
    id: "weft_cover_factor",
    name: "Weft Cover Factor",
    type: "number",
  },
  total_cover_factor: {
    id: "total_cover_factor",
    name: "Total Cover Factor",
    type: "number",
  },
  warp_crimp_pct: {
    id: "warp_crimp_pct",
    name: "Warp Crimp Pct",
    type: "number",
  },
  weft_crimp_pct: {
    id: "weft_crimp_pct",
    name: "Weft Crimp Pct",
    type: "number",
  },
  crimp_balance: { id: "crimp_balance", name: "Crimp Balance", type: "string" },
  fell_displacement_mm: {
    id: "fell_displacement_mm",
    name: "Fell Displacement Mm",
    type: "number",
  },
  beat_up_force_cN_per_cm: {
    id: "beat_up_force_cN_per_cm",
    name: "Beat Up Force Cn Per Cm",
    type: "number",
  },
  fabric_areal_weight_g_m2: {
    id: "fabric_areal_weight_g_m2",
    name: "Fabric Areal Weight G M2",
    type: "number",
  },
  weft_tension_at_fell_cN: {
    id: "weft_tension_at_fell_cN",
    name: "Weft Tension At Fell Cn",
    type: "number",
  },
  warp_break_risk: {
    id: "warp_break_risk",
    name: "Warp Break Risk",
    type: "string",
  },
  weft_break_risk: {
    id: "weft_break_risk",
    name: "Weft Break Risk",
    type: "string",
  },
  cloth_defect_risk: {
    id: "cloth_defect_risk",
    name: "Cloth Defect Risk",
    type: "string",
  },
  production_rate_m_per_min: {
    id: "production_rate_m_per_min",
    name: "Production Rate M Per Min",
    type: "number",
  },
  production_rate_m2_per_hour: {
    id: "production_rate_m2_per_hour",
    name: "Production Rate M2 Per Hour",
    type: "number",
  },
  warnings: { id: "warnings", name: "Warnings", type: "string" },
};

export const DOBBY_WEAVING_INPUT_DEFS: Record<string, AttributeDefinition> = {
  yarn_count_tex: {
    id: "yarn_count_tex",
    name: "Yarn Count Tex",
    type: "number",
  },
  yarn_count_Ne: { id: "yarn_count_Ne", name: "Yarn Count Ne", type: "number" },
  fiber_type: { id: "fiber_type", name: "Fiber Type", type: "string" },
  twist_multiplier: {
    id: "twist_multiplier",
    name: "Twist Multiplier",
    type: "number",
  },
  yarn_tenacity_cN_tex: {
    id: "yarn_tenacity_cN_tex",
    name: "Yarn Tenacity Cn Tex",
    type: "number",
  },
  yarn_evenness_CVm_pct: {
    id: "yarn_evenness_CVm_pct",
    name: "Yarn Evenness Cvm Pct",
    type: "number",
  },
  hairiness_H: { id: "hairiness_H", name: "Hairiness H", type: "number" },
  neps_per_km: { id: "neps_per_km", name: "Neps Per Km", type: "number" },
  warp_sizing_applied: {
    id: "warp_sizing_applied",
    name: "Warp Sizing Applied",
    type: "boolean",
  },
  size_add_on_pct: {
    id: "size_add_on_pct",
    name: "Size Add On Pct",
    type: "number",
  },
  moisture_regain_pct: {
    id: "moisture_regain_pct",
    name: "Moisture Regain Pct",
    type: "number",
  },
};
export const DOBBY_WEAVING_CONFIG_DEFS: Record<string, AttributeDefinition> = {
  number_of_heald_shafts: {
    id: "number_of_heald_shafts",
    name: "Number Of Heald Shafts",
    type: "number",
  },
  weave_repeat_ends: {
    id: "weave_repeat_ends",
    name: "Weave Repeat Ends",
    type: "number",
  },
  weave_repeat_picks: {
    id: "weave_repeat_picks",
    name: "Weave Repeat Picks",
    type: "number",
  },
  ends_per_cm_per_shaft: {
    id: "ends_per_cm_per_shaft",
    name: "Ends Per Cm Per Shaft",
    type: "number",
  },
  shed_depth_mm: { id: "shed_depth_mm", name: "Shed Depth Mm", type: "number" },
  shed_type: { id: "shed_type", name: "Shed Type", type: "string" },
  dobby_type: { id: "dobby_type", name: "Dobby Type", type: "string" },
  loom_speed_picks_per_min: {
    id: "loom_speed_picks_per_min",
    name: "Loom Speed Picks Per Min",
    type: "number",
  },
  weft_insertion_type: {
    id: "weft_insertion_type",
    name: "Weft Insertion Type",
    type: "string",
  },
  reed_space_cm: { id: "reed_space_cm", name: "Reed Space Cm", type: "number" },
  shuttle_mass_g: {
    id: "shuttle_mass_g",
    name: "Shuttle Mass G",
    type: "number",
  },
  warp_ends_per_cm: {
    id: "warp_ends_per_cm",
    name: "Warp Ends Per Cm",
    type: "number",
  },
  weft_picks_per_cm: {
    id: "weft_picks_per_cm",
    name: "Weft Picks Per Cm",
    type: "number",
  },
  float_length_warp: {
    id: "float_length_warp",
    name: "Float Length Warp",
    type: "number",
  },
  float_length_weft: {
    id: "float_length_weft",
    name: "Float Length Weft",
    type: "number",
  },
  interlacement_ratio: {
    id: "interlacement_ratio",
    name: "Interlacement Ratio",
    type: "number",
  },
  warp_tension_cN_per_end: {
    id: "warp_tension_cN_per_end",
    name: "Warp Tension Cn Per End",
    type: "number",
  },
  let_off_type: { id: "let_off_type", name: "Let Off Type", type: "string" },
  take_up_picks_per_cm: {
    id: "take_up_picks_per_cm",
    name: "Take Up Picks Per Cm",
    type: "number",
  },
  reed_count_dents_per_cm: {
    id: "reed_count_dents_per_cm",
    name: "Reed Count Dents Per Cm",
    type: "number",
  },
  ends_per_dent: { id: "ends_per_dent", name: "Ends Per Dent", type: "number" },
  temple_type: { id: "temple_type", name: "Temple Type", type: "string" },
  selvedge_type: { id: "selvedge_type", name: "Selvedge Type", type: "string" },
  ambient_temperature_C: {
    id: "ambient_temperature_C",
    name: "Ambient Temperature C",
    type: "number",
  },
  ambient_humidity_pct: {
    id: "ambient_humidity_pct",
    name: "Ambient Humidity Pct",
    type: "number",
  },
  last_maintenance_date: {
    id: "last_maintenance_date",
    name: "Last Maintenance Date",
    type: "string",
  },
  maintenance_interval_hours: {
    id: "maintenance_interval_hours",
    name: "Maintenance Interval Hours",
    type: "number",
  },
  operating_hours_since_maintenance: {
    id: "operating_hours_since_maintenance",
    name: "Operating Hours Since Maintenance",
    type: "number",
  },
};
export const DOBBY_WEAVING_OUTPUT_DEFS: Record<string, AttributeDefinition> = {
  fabric_width_cm: {
    id: "fabric_width_cm",
    name: "Fabric Width Cm",
    type: "number",
  },
  weft_crimp_pct: {
    id: "weft_crimp_pct",
    name: "Weft Crimp Pct",
    type: "number",
  },
  warp_crimp_pct: {
    id: "warp_crimp_pct",
    name: "Warp Crimp Pct",
    type: "number",
  },
  fabric_weight_g_per_m2: {
    id: "fabric_weight_g_per_m2",
    name: "Fabric Weight G Per M2",
    type: "number",
  },
  cloth_cover_factor: {
    id: "cloth_cover_factor",
    name: "Cloth Cover Factor",
    type: "number",
  },
  warp_end_break_risk: {
    id: "warp_end_break_risk",
    name: "Warp End Break Risk",
    type: "string",
  },
  weft_break_risk: {
    id: "weft_break_risk",
    name: "Weft Break Risk",
    type: "string",
  },
  shedding_quality: {
    id: "shedding_quality",
    name: "Shedding Quality",
    type: "string",
  },
  beat_up_resistance: {
    id: "beat_up_resistance",
    name: "Beat Up Resistance",
    type: "string",
  },
  expected_nep_visibility: {
    id: "expected_nep_visibility",
    name: "Expected Nep Visibility",
    type: "string",
  },
  pick_spacing_regularity: {
    id: "pick_spacing_regularity",
    name: "Pick Spacing Regularity",
    type: "string",
  },
  selvedge_quality: {
    id: "selvedge_quality",
    name: "Selvedge Quality",
    type: "string",
  },
  theoretical_production_m_per_hour: {
    id: "theoretical_production_m_per_hour",
    name: "Theoretical Production M Per Hour",
    type: "number",
  },
  loom_efficiency_pct: {
    id: "loom_efficiency_pct",
    name: "Loom Efficiency Pct",
    type: "number",
  },
  actual_production_m_per_hour: {
    id: "actual_production_m_per_hour",
    name: "Actual Production M Per Hour",
    type: "number",
  },
  warnings: { id: "warnings", name: "Warnings", type: "string" },
};

export const WEFT_KNITTING_INPUT_DEFS: Record<string, AttributeDefinition> = {
  yarn_diameter_warp_mm: {
    id: "yarn_diameter_warp_mm",
    name: "Yarn Diameter Warp Mm",
    type: "number",
  },
  yarn_diameter_weft_mm: {
    id: "yarn_diameter_weft_mm",
    name: "Yarn Diameter Weft Mm",
    type: "number",
  },
  warp_cover_factor: {
    id: "warp_cover_factor",
    name: "Warp Cover Factor",
    type: "number",
  },
  weft_cover_factor: {
    id: "weft_cover_factor",
    name: "Weft Cover Factor",
    type: "number",
  },
  total_cover_factor: {
    id: "total_cover_factor",
    name: "Total Cover Factor",
    type: "number",
  },
  warp_crimp_pct: {
    id: "warp_crimp_pct",
    name: "Warp Crimp Pct",
    type: "number",
  },
  weft_crimp_pct: {
    id: "weft_crimp_pct",
    name: "Weft Crimp Pct",
    type: "number",
  },
  crimp_balance: { id: "crimp_balance", name: "Crimp Balance", type: "string" },
  fell_displacement_mm: {
    id: "fell_displacement_mm",
    name: "Fell Displacement Mm",
    type: "number",
  },
  beat_up_force_cN_per_cm: {
    id: "beat_up_force_cN_per_cm",
    name: "Beat Up Force Cn Per Cm",
    type: "number",
  },
  fabric_areal_weight_g_m2: {
    id: "fabric_areal_weight_g_m2",
    name: "Fabric Areal Weight G M2",
    type: "number",
  },
  weft_tension_at_fell_cN: {
    id: "weft_tension_at_fell_cN",
    name: "Weft Tension At Fell Cn",
    type: "number",
  },
  warp_break_risk: {
    id: "warp_break_risk",
    name: "Warp Break Risk",
    type: "string",
  },
  weft_break_risk: {
    id: "weft_break_risk",
    name: "Weft Break Risk",
    type: "string",
  },
  cloth_defect_risk: {
    id: "cloth_defect_risk",
    name: "Cloth Defect Risk",
    type: "string",
  },
  production_rate_m_per_min: {
    id: "production_rate_m_per_min",
    name: "Production Rate M Per Min",
    type: "number",
  },
  production_rate_m2_per_hour: {
    id: "production_rate_m2_per_hour",
    name: "Production Rate M2 Per Hour",
    type: "number",
  },
};
export const WEFT_KNITTING_CONFIG_DEFS: Record<string, AttributeDefinition> = {
  machine_gauge_npi: {
    id: "machine_gauge_npi",
    name: "Machine Gauge Npi",
    type: "number",
  },
  cylinder_diameter_inch: {
    id: "cylinder_diameter_inch",
    name: "Cylinder Diameter Inch",
    type: "number",
  },
  number_of_feeds: {
    id: "number_of_feeds",
    name: "Number Of Feeds",
    type: "number",
  },
  stitch_length_mm: {
    id: "stitch_length_mm",
    name: "Stitch Length Mm",
    type: "number",
  },
  machine_rpm: { id: "machine_rpm", name: "Machine Rpm", type: "number" },
  yarn_input_tension_cN: {
    id: "yarn_input_tension_cN",
    name: "Yarn Input Tension Cn",
    type: "number",
  },
  take_down_tension_cN_per_cm: {
    id: "take_down_tension_cN_per_cm",
    name: "Take Down Tension Cn Per Cm",
    type: "number",
  },
  needle_type: { id: "needle_type", name: "Needle Type", type: "string" },
  structure_type: {
    id: "structure_type",
    name: "Structure Type",
    type: "string",
  },
  relaxation_state: {
    id: "relaxation_state",
    name: "Relaxation State",
    type: "string",
  },
  ambient_temperature_C: {
    id: "ambient_temperature_C",
    name: "Ambient Temperature C",
    type: "number",
  },
  ambient_humidity_pct: {
    id: "ambient_humidity_pct",
    name: "Ambient Humidity Pct",
    type: "number",
  },
  maintenance_interval_hours: {
    id: "maintenance_interval_hours",
    name: "Maintenance Interval Hours",
    type: "number",
  },
  operating_hours_since_maintenance: {
    id: "operating_hours_since_maintenance",
    name: "Operating Hours Since Maintenance",
    type: "number",
  },
};
export const WEFT_KNITTING_OUTPUT_DEFS: Record<string, AttributeDefinition> = {
  yarn_count_tex: {
    id: "yarn_count_tex",
    name: "Yarn Count Tex",
    type: "number",
  },
  yarn_count_Ne: { id: "yarn_count_Ne", name: "Yarn Count Ne", type: "number" },
  tightness_factor: {
    id: "tightness_factor",
    name: "Tightness Factor",
    type: "number",
  },
  courses_per_cm: {
    id: "courses_per_cm",
    name: "Courses Per Cm",
    type: "number",
  },
  wales_per_cm: { id: "wales_per_cm", name: "Wales Per Cm", type: "number" },
  stitch_density_per_cm2: {
    id: "stitch_density_per_cm2",
    name: "Stitch Density Per Cm2",
    type: "number",
  },
  loop_shape_factor: {
    id: "loop_shape_factor",
    name: "Loop Shape Factor",
    type: "number",
  },
  fabric_areal_weight_g_m2: {
    id: "fabric_areal_weight_g_m2",
    name: "Fabric Areal Weight G M2",
    type: "number",
  },
  width_relaxation_pct: {
    id: "width_relaxation_pct",
    name: "Width Relaxation Pct",
    type: "number",
  },
  length_relaxation_pct: {
    id: "length_relaxation_pct",
    name: "Length Relaxation Pct",
    type: "number",
  },
  total_needles: { id: "total_needles", name: "Total Needles", type: "number" },
  courses_per_minute: {
    id: "courses_per_minute",
    name: "Courses Per Minute",
    type: "number",
  },
  fabric_production_rate_m_min: {
    id: "fabric_production_rate_m_min",
    name: "Fabric Production Rate M Min",
    type: "number",
  },
  fabric_production_rate_m2_hr: {
    id: "fabric_production_rate_m2_hr",
    name: "Fabric Production Rate M2 Hr",
    type: "number",
  },
  fabric_width_m: {
    id: "fabric_width_m",
    name: "Fabric Width M",
    type: "number",
  },
  needle_break_risk: {
    id: "needle_break_risk",
    name: "Needle Break Risk",
    type: "string",
  },
  yarn_break_risk: {
    id: "yarn_break_risk",
    name: "Yarn Break Risk",
    type: "string",
  },
  fabric_defect_risk: {
    id: "fabric_defect_risk",
    name: "Fabric Defect Risk",
    type: "string",
  },
  pilling_propensity: {
    id: "pilling_propensity",
    name: "Pilling Propensity",
    type: "string",
  },
  warnings: { id: "warnings", name: "Warnings", type: "string" },
};

export const WARP_KNITTING_INPUT_DEFS: Record<string, AttributeDefinition> = {
  fabric_width_cm: {
    id: "fabric_width_cm",
    name: "Fabric Width Cm",
    type: "number",
  },
  fabric_weight_g_per_m2: {
    id: "fabric_weight_g_per_m2",
    name: "Fabric Weight G Per M2",
    type: "number",
  },
  cloth_cover_factor: {
    id: "cloth_cover_factor",
    name: "Cloth Cover Factor",
    type: "number",
  },
  weft_crimp_pct: {
    id: "weft_crimp_pct",
    name: "Weft Crimp Pct",
    type: "number",
  },
  warp_crimp_pct: {
    id: "warp_crimp_pct",
    name: "Warp Crimp Pct",
    type: "number",
  },
  warp_yarn_quality_risk: {
    id: "warp_yarn_quality_risk",
    name: "Warp Yarn Quality Risk",
    type: "string",
  },
  weft_yarn_quality_risk: {
    id: "weft_yarn_quality_risk",
    name: "Weft Yarn Quality Risk",
    type: "string",
  },
  substrate_nep_visibility: {
    id: "substrate_nep_visibility",
    name: "Substrate Nep Visibility",
    type: "string",
  },
  substrate_regularity: {
    id: "substrate_regularity",
    name: "Substrate Regularity",
    type: "string",
  },
  substrate_selvedge_quality: {
    id: "substrate_selvedge_quality",
    name: "Substrate Selvedge Quality",
    type: "string",
  },
  upstream_process_efficiency_pct: {
    id: "upstream_process_efficiency_pct",
    name: "Upstream Process Efficiency Pct",
    type: "number",
  },
  upstream_feed_rate_m_per_hour: {
    id: "upstream_feed_rate_m_per_hour",
    name: "Upstream Feed Rate M Per Hour",
    type: "number",
  },
  yarn_count_dtex: {
    id: "yarn_count_dtex",
    name: "Yarn Count Dtex",
    type: "number",
  },
  fiber_type: { id: "fiber_type", name: "Fiber Type", type: "string" },
  yarn_tenacity_cN_tex: {
    id: "yarn_tenacity_cN_tex",
    name: "Yarn Tenacity Cn Tex",
    type: "number",
  },
  yarn_evenness_CVm_pct: {
    id: "yarn_evenness_CVm_pct",
    name: "Yarn Evenness Cvm Pct",
    type: "number",
  },
  yarn_hairiness_H: {
    id: "yarn_hairiness_H",
    name: "Yarn Hairiness H",
    type: "number",
  },
};
export const WARP_KNITTING_CONFIG_DEFS: Record<string, AttributeDefinition> = {
  machine_class: { id: "machine_class", name: "Machine Class", type: "string" },
  gauge_E: { id: "gauge_E", name: "Gauge E", type: "number" },
  needle_type: { id: "needle_type", name: "Needle Type", type: "string" },
  knitting_width_cm: {
    id: "knitting_width_cm",
    name: "Knitting Width Cm",
    type: "number",
  },
  number_of_guide_bars: {
    id: "number_of_guide_bars",
    name: "Number Of Guide Bars",
    type: "number",
  },
  threading_density: {
    id: "threading_density",
    name: "Threading Density",
    type: "string",
  },
  underlap_span_needles: {
    id: "underlap_span_needles",
    name: "Underlap Span Needles",
    type: "number",
  },
  lapping_type: { id: "lapping_type", name: "Lapping Type", type: "string" },
  overlap_direction: {
    id: "overlap_direction",
    name: "Overlap Direction",
    type: "string",
  },
  pattern_control: {
    id: "pattern_control",
    name: "Pattern Control",
    type: "string",
  },
  machine_speed_cpm: {
    id: "machine_speed_cpm",
    name: "Machine Speed Cpm",
    type: "number",
  },
  let_off_type: { id: "let_off_type", name: "Let Off Type", type: "string" },
  run_in_ratio_front_back: {
    id: "run_in_ratio_front_back",
    name: "Run In Ratio Front Back",
    type: "number",
  },
  warp_tension_cN_per_end: {
    id: "warp_tension_cN_per_end",
    name: "Warp Tension Cn Per End",
    type: "number",
  },
  take_down_tension_cN_per_cm: {
    id: "take_down_tension_cN_per_cm",
    name: "Take Down Tension Cn Per Cm",
    type: "number",
  },
  stitch_length_mm: {
    id: "stitch_length_mm",
    name: "Stitch Length Mm",
    type: "number",
  },
  sinker_depth_mm: {
    id: "sinker_depth_mm",
    name: "Sinker Depth Mm",
    type: "number",
  },
  shed_swing_angle_deg: {
    id: "shed_swing_angle_deg",
    name: "Shed Swing Angle Deg",
    type: "number",
  },
  ambient_temperature_C: {
    id: "ambient_temperature_C",
    name: "Ambient Temperature C",
    type: "number",
  },
  ambient_humidity_pct: {
    id: "ambient_humidity_pct",
    name: "Ambient Humidity Pct",
    type: "number",
  },
  last_maintenance_date: {
    id: "last_maintenance_date",
    name: "Last Maintenance Date",
    type: "string",
  },
  maintenance_interval_hours: {
    id: "maintenance_interval_hours",
    name: "Maintenance Interval Hours",
    type: "number",
  },
  operating_hours_since_maintenance: {
    id: "operating_hours_since_maintenance",
    name: "Operating Hours Since Maintenance",
    type: "number",
  },
};
export const WARP_KNITTING_OUTPUT_DEFS: Record<string, AttributeDefinition> = {
  fabric_width_finished_cm: {
    id: "fabric_width_finished_cm",
    name: "Fabric Width Finished Cm",
    type: "number",
  },
  courses_per_cm: {
    id: "courses_per_cm",
    name: "Courses Per Cm",
    type: "number",
  },
  wales_per_cm: { id: "wales_per_cm", name: "Wales Per Cm", type: "number" },
  stitch_density_per_cm2: {
    id: "stitch_density_per_cm2",
    name: "Stitch Density Per Cm2",
    type: "number",
  },
  fabric_weight_g_per_m2: {
    id: "fabric_weight_g_per_m2",
    name: "Fabric Weight G Per M2",
    type: "number",
  },
  tightness_factor: {
    id: "tightness_factor",
    name: "Tightness Factor",
    type: "number",
  },
  loop_formation_quality: {
    id: "loop_formation_quality",
    name: "Loop Formation Quality",
    type: "string",
  },
  yarn_tension_balance: {
    id: "yarn_tension_balance",
    name: "Yarn Tension Balance",
    type: "string",
  },
  underlap_regularity: {
    id: "underlap_regularity",
    name: "Underlap Regularity",
    type: "string",
  },
  fabric_stability: {
    id: "fabric_stability",
    name: "Fabric Stability",
    type: "string",
  },
  surface_nep_visibility: {
    id: "surface_nep_visibility",
    name: "Surface Nep Visibility",
    type: "string",
  },
  barre_risk: { id: "barre_risk", name: "Barre Risk", type: "string" },
  selvedge_security: {
    id: "selvedge_security",
    name: "Selvedge Security",
    type: "string",
  },
  cover_adequacy: {
    id: "cover_adequacy",
    name: "Cover Adequacy",
    type: "string",
  },
  extensibility_rating: {
    id: "extensibility_rating",
    name: "Extensibility Rating",
    type: "string",
  },
  fabric_curling_tendency: {
    id: "fabric_curling_tendency",
    name: "Fabric Curling Tendency",
    type: "string",
  },
  theoretical_production_m_per_hour: {
    id: "theoretical_production_m_per_hour",
    name: "Theoretical Production M Per Hour",
    type: "number",
  },
  machine_efficiency_pct: {
    id: "machine_efficiency_pct",
    name: "Machine Efficiency Pct",
    type: "number",
  },
  actual_production_m_per_hour: {
    id: "actual_production_m_per_hour",
    name: "Actual Production M Per Hour",
    type: "number",
  },
  warnings: { id: "warnings", name: "Warnings", type: "string" },
};

export const REACTIVE_DYEING_INPUT_DEFS: Record<string, AttributeDefinition> = {
  yarn_diameter_warp_mm: {
    id: "yarn_diameter_warp_mm",
    name: "Yarn Diameter Warp Mm",
    type: "number",
  },
  yarn_diameter_weft_mm: {
    id: "yarn_diameter_weft_mm",
    name: "Yarn Diameter Weft Mm",
    type: "number",
  },
  warp_cover_factor: {
    id: "warp_cover_factor",
    name: "Warp Cover Factor",
    type: "number",
  },
  weft_cover_factor: {
    id: "weft_cover_factor",
    name: "Weft Cover Factor",
    type: "number",
  },
  total_cover_factor: {
    id: "total_cover_factor",
    name: "Total Cover Factor",
    type: "number",
  },
  warp_crimp_pct: {
    id: "warp_crimp_pct",
    name: "Warp Crimp Pct",
    type: "number",
  },
  weft_crimp_pct: {
    id: "weft_crimp_pct",
    name: "Weft Crimp Pct",
    type: "number",
  },
  crimp_balance: { id: "crimp_balance", name: "Crimp Balance", type: "string" },
  fell_displacement_mm: {
    id: "fell_displacement_mm",
    name: "Fell Displacement Mm",
    type: "number",
  },
  beat_up_force_cN_per_cm: {
    id: "beat_up_force_cN_per_cm",
    name: "Beat Up Force Cn Per Cm",
    type: "number",
  },
  fabric_areal_weight_g_m2: {
    id: "fabric_areal_weight_g_m2",
    name: "Fabric Areal Weight G M2",
    type: "number",
  },
  weft_tension_at_fell_cN: {
    id: "weft_tension_at_fell_cN",
    name: "Weft Tension At Fell Cn",
    type: "number",
  },
  warp_break_risk: {
    id: "warp_break_risk",
    name: "Warp Break Risk",
    type: "string",
  },
  weft_break_risk: {
    id: "weft_break_risk",
    name: "Weft Break Risk",
    type: "string",
  },
  cloth_defect_risk: {
    id: "cloth_defect_risk",
    name: "Cloth Defect Risk",
    type: "string",
  },
  production_rate_m_per_min: {
    id: "production_rate_m_per_min",
    name: "Production Rate M Per Min",
    type: "number",
  },
  production_rate_m2_per_hour: {
    id: "production_rate_m2_per_hour",
    name: "Production Rate M2 Per Hour",
    type: "number",
  },
};
export const REACTIVE_DYEING_CONFIG_DEFS: Record<string, AttributeDefinition> =
{
  dye_type: { id: "dye_type", name: "Dye Type", type: "string" },
  dye_concentration_owf_pct: {
    id: "dye_concentration_owf_pct",
    name: "Dye Concentration Owf Pct",
    type: "number",
  },
  salt_concentration_g_L: {
    id: "salt_concentration_g_L",
    name: "Salt Concentration G L",
    type: "number",
  },
  alkali_type: { id: "alkali_type", name: "Alkali Type", type: "string" },
  alkali_concentration_g_L: {
    id: "alkali_concentration_g_L",
    name: "Alkali Concentration G L",
    type: "number",
  },
  dyeing_temperature_C: {
    id: "dyeing_temperature_C",
    name: "Dyeing Temperature C",
    type: "number",
  },
  exhaustion_time_min: {
    id: "exhaustion_time_min",
    name: "Exhaustion Time Min",
    type: "number",
  },
  fixation_time_min: {
    id: "fixation_time_min",
    name: "Fixation Time Min",
    type: "number",
  },
  wash_off_time_min: {
    id: "wash_off_time_min",
    name: "Wash Off Time Min",
    type: "number",
  },
  liquor_ratio: { id: "liquor_ratio", name: "Liquor Ratio", type: "number" },
  machine_type: { id: "machine_type", name: "Machine Type", type: "string" },
  water_hardness_ppm: {
    id: "water_hardness_ppm",
    name: "Water Hardness Ppm",
    type: "number",
  },
  fabric_is_mercerized: {
    id: "fabric_is_mercerized",
    name: "Fabric Is Mercerized",
    type: "boolean",
  },
  fabric_is_scoured: {
    id: "fabric_is_scoured",
    name: "Fabric Is Scoured",
    type: "boolean",
  },
  ambient_temperature_C: {
    id: "ambient_temperature_C",
    name: "Ambient Temperature C",
    type: "number",
  },
  maintenance_interval_hours: {
    id: "maintenance_interval_hours",
    name: "Maintenance Interval Hours",
    type: "number",
  },
  operating_hours_since_maintenance: {
    id: "operating_hours_since_maintenance",
    name: "Operating Hours Since Maintenance",
    type: "number",
  },
};
export const REACTIVE_DYEING_OUTPUT_DEFS: Record<string, AttributeDefinition> =
{
  dye_bath_pH: { id: "dye_bath_pH", name: "Dye Bath Ph", type: "number" },
  exhaustion_pct: {
    id: "exhaustion_pct",
    name: "Exhaustion Pct",
    type: "number",
  },
  fixation_pct: { id: "fixation_pct", name: "Fixation Pct", type: "number" },
  hydrolysis_pct: {
    id: "hydrolysis_pct",
    name: "Hydrolysis Pct",
    type: "number",
  },
  unfixed_dye_on_fabric_pct: {
    id: "unfixed_dye_on_fabric_pct",
    name: "Unfixed Dye On Fabric Pct",
    type: "number",
  },
  colour_yield_relative: {
    id: "colour_yield_relative",
    name: "Colour Yield Relative",
    type: "number",
  },
  wash_fastness_rating: {
    id: "wash_fastness_rating",
    name: "Wash Fastness Rating",
    type: "number",
  },
  light_fastness_rating: {
    id: "light_fastness_rating",
    name: "Light Fastness Rating",
    type: "number",
  },
  rubbing_fastness_dry: {
    id: "rubbing_fastness_dry",
    name: "Rubbing Fastness Dry",
    type: "number",
  },
  rubbing_fastness_wet: {
    id: "rubbing_fastness_wet",
    name: "Rubbing Fastness Wet",
    type: "number",
  },
  levelness_risk: {
    id: "levelness_risk",
    name: "Levelness Risk",
    type: "string",
  },
  dye_penetration_quality: {
    id: "dye_penetration_quality",
    name: "Dye Penetration Quality",
    type: "string",
  },
  water_consumption_L_per_kg: {
    id: "water_consumption_L_per_kg",
    name: "Water Consumption L Per Kg",
    type: "number",
  },
  salt_load_g_per_kg: {
    id: "salt_load_g_per_kg",
    name: "Salt Load G Per Kg",
    type: "number",
  },
  total_process_time_min: {
    id: "total_process_time_min",
    name: "Total Process Time Min",
    type: "number",
  },
  energy_relative: {
    id: "energy_relative",
    name: "Energy Relative",
    type: "number",
  },
  effluent_dye_load_pct: {
    id: "effluent_dye_load_pct",
    name: "Effluent Dye Load Pct",
    type: "number",
  },
  unlevel_dyeing_risk: {
    id: "unlevel_dyeing_risk",
    name: "Unlevel Dyeing Risk",
    type: "string",
  },
  fabric_damage_risk: {
    id: "fabric_damage_risk",
    name: "Fabric Damage Risk",
    type: "string",
  },
  warnings: { id: "warnings", name: "Warnings", type: "string" },
};

export const ROTARY_PRINTING_INPUT_DEFS: Record<string, AttributeDefinition> = {
  fiber_type: { id: "fiber_type", name: "Fiber Type", type: "string" },
  fabric_weight_g_per_m2: {
    id: "fabric_weight_g_per_m2",
    name: "Fabric Weight G Per M2",
    type: "number",
  },
  fabric_cover_factor: {
    id: "fabric_cover_factor",
    name: "Fabric Cover Factor",
    type: "number",
  },
  fabric_width_cm: {
    id: "fabric_width_cm",
    name: "Fabric Width Cm",
    type: "number",
  },
  fabric_surface_texture: {
    id: "fabric_surface_texture",
    name: "Fabric Surface Texture",
    type: "string",
  },
  substrate_pH: { id: "substrate_pH", name: "Substrate Ph", type: "number" },
  dye_exhaustion_pct: {
    id: "dye_exhaustion_pct",
    name: "Dye Exhaustion Pct",
    type: "number",
  },
  dye_fixation_pct: {
    id: "dye_fixation_pct",
    name: "Dye Fixation Pct",
    type: "number",
  },
  unfixed_hydrolysed_dye_pct: {
    id: "unfixed_hydrolysed_dye_pct",
    name: "Unfixed Hydrolysed Dye Pct",
    type: "number",
  },
  residual_unfixed_dye_pct: {
    id: "residual_unfixed_dye_pct",
    name: "Residual Unfixed Dye Pct",
    type: "number",
  },
  ground_colour_yield: {
    id: "ground_colour_yield",
    name: "Ground Colour Yield",
    type: "number",
  },
  ground_wash_fastness: {
    id: "ground_wash_fastness",
    name: "Ground Wash Fastness",
    type: "number",
  },
  ground_light_fastness: {
    id: "ground_light_fastness",
    name: "Ground Light Fastness",
    type: "number",
  },
  ground_levelness_risk: {
    id: "ground_levelness_risk",
    name: "Ground Levelness Risk",
    type: "string",
  },
  ground_dye_penetration: {
    id: "ground_dye_penetration",
    name: "Ground Dye Penetration",
    type: "string",
  },
  upstream_water_L_per_kg: {
    id: "upstream_water_L_per_kg",
    name: "Upstream Water L Per Kg",
    type: "number",
  },
  upstream_salt_g_per_kg: {
    id: "upstream_salt_g_per_kg",
    name: "Upstream Salt G Per Kg",
    type: "number",
  },
  substrate_damage_risk: {
    id: "substrate_damage_risk",
    name: "Substrate Damage Risk",
    type: "string",
  },
};
export const ROTARY_PRINTING_CONFIG_DEFS: Record<string, AttributeDefinition> =
{
  printing_speed_m_per_hour: {
    id: "printing_speed_m_per_hour",
    name: "Printing Speed M Per Hour",
    type: "number",
  },
  screen_working_width_cm: {
    id: "screen_working_width_cm",
    name: "Screen Working Width Cm",
    type: "number",
  },
  number_of_screens: {
    id: "number_of_screens",
    name: "Number Of Screens",
    type: "number",
  },
  screen_type: { id: "screen_type", name: "Screen Type", type: "string" },
  screen_mesh_holes_per_inch: {
    id: "screen_mesh_holes_per_inch",
    name: "Screen Mesh Holes Per Inch",
    type: "number",
  },
  screen_open_area_pct: {
    id: "screen_open_area_pct",
    name: "Screen Open Area Pct",
    type: "number",
  },
  screen_wall_thickness_mm: {
    id: "screen_wall_thickness_mm",
    name: "Screen Wall Thickness Mm",
    type: "number",
  },
  screen_circumference_mm: {
    id: "screen_circumference_mm",
    name: "Screen Circumference Mm",
    type: "number",
  },
  design_repeat_length_cm: {
    id: "design_repeat_length_cm",
    name: "Design Repeat Length Cm",
    type: "number",
  },
  squeegee_type: {
    id: "squeegee_type",
    name: "Squeegee Type",
    type: "string",
  },
  squeegee_blade_length_mm: {
    id: "squeegee_blade_length_mm",
    name: "Squeegee Blade Length Mm",
    type: "number",
  },
  squeegee_pressure_setting: {
    id: "squeegee_pressure_setting",
    name: "Squeegee Pressure Setting",
    type: "string",
  },
  squeegee_blade_curvature: {
    id: "squeegee_blade_curvature",
    name: "Squeegee Blade Curvature",
    type: "string",
  },
  blanket_type: { id: "blanket_type", name: "Blanket Type", type: "string" },
  adhesive_type: {
    id: "adhesive_type",
    name: "Adhesive Type",
    type: "string",
  },
  independent_screen_speed_control: {
    id: "independent_screen_speed_control",
    name: "Independent Screen Speed Control",
    type: "boolean",
  },
  laser_registration: {
    id: "laser_registration",
    name: "Laser Registration",
    type: "boolean",
  },
  paste_pump_type: {
    id: "paste_pump_type",
    name: "Paste Pump Type",
    type: "string",
  },
  level_control_type: {
    id: "level_control_type",
    name: "Level Control Type",
    type: "string",
  },
  paste_distribution_quality: {
    id: "paste_distribution_quality",
    name: "Paste Distribution Quality",
    type: "string",
  },
  colorant_type: {
    id: "colorant_type",
    name: "Colorant Type",
    type: "string",
  },
  paste_colorant_conc_g_per_kg: {
    id: "paste_colorant_conc_g_per_kg",
    name: "Paste Colorant Conc G Per Kg",
    type: "number",
  },
  thickener_type: {
    id: "thickener_type",
    name: "Thickener Type",
    type: "string",
  },
  thickener_concentration_pct: {
    id: "thickener_concentration_pct",
    name: "Thickener Concentration Pct",
    type: "number",
  },
  paste_viscosity_Pa_s: {
    id: "paste_viscosity_Pa_s",
    name: "Paste Viscosity Pa S",
    type: "number",
  },
  paste_yield_value: {
    id: "paste_yield_value",
    name: "Paste Yield Value",
    type: "string",
  },
  binder_concentration_pct: {
    id: "binder_concentration_pct",
    name: "Binder Concentration Pct",
    type: "number",
  },
  urea_concentration_g_per_kg: {
    id: "urea_concentration_g_per_kg",
    name: "Urea Concentration G Per Kg",
    type: "number",
  },
  alkali_type: { id: "alkali_type", name: "Alkali Type", type: "string" },
  alkali_concentration_g_per_kg: {
    id: "alkali_concentration_g_per_kg",
    name: "Alkali Concentration G Per Kg",
    type: "number",
  },
  design_coverage_pct: {
    id: "design_coverage_pct",
    name: "Design Coverage Pct",
    type: "number",
  },
  fixation_method: {
    id: "fixation_method",
    name: "Fixation Method",
    type: "string",
  },
  fixation_temperature_C: {
    id: "fixation_temperature_C",
    name: "Fixation Temperature C",
    type: "number",
  },
  fixation_time_min: {
    id: "fixation_time_min",
    name: "Fixation Time Min",
    type: "number",
  },
  steamer_type: { id: "steamer_type", name: "Steamer Type", type: "string" },
  dryer_capacity: {
    id: "dryer_capacity",
    name: "Dryer Capacity",
    type: "string",
  },
  wash_off_applied: {
    id: "wash_off_applied",
    name: "Wash Off Applied",
    type: "boolean",
  },
  wash_off_temperature_C: {
    id: "wash_off_temperature_C",
    name: "Wash Off Temperature C",
    type: "number",
  },
  wash_off_stages: {
    id: "wash_off_stages",
    name: "Wash Off Stages",
    type: "number",
  },
  counterflow_washing: {
    id: "counterflow_washing",
    name: "Counterflow Washing",
    type: "boolean",
  },
  ambient_temperature_C: {
    id: "ambient_temperature_C",
    name: "Ambient Temperature C",
    type: "number",
  },
  ambient_humidity_pct: {
    id: "ambient_humidity_pct",
    name: "Ambient Humidity Pct",
    type: "number",
  },
  last_maintenance_date: {
    id: "last_maintenance_date",
    name: "Last Maintenance Date",
    type: "string",
  },
  maintenance_interval_hours: {
    id: "maintenance_interval_hours",
    name: "Maintenance Interval Hours",
    type: "number",
  },
  operating_hours_since_maintenance: {
    id: "operating_hours_since_maintenance",
    name: "Operating Hours Since Maintenance",
    type: "number",
  },
};
export const ROTARY_PRINTING_OUTPUT_DEFS: Record<string, AttributeDefinition> =
{
  paste_volume_applied_g_per_m2: {
    id: "paste_volume_applied_g_per_m2",
    name: "Paste Volume Applied G Per M2",
    type: "number",
  },
  paste_penetration_depth: {
    id: "paste_penetration_depth",
    name: "Paste Penetration Depth",
    type: "string",
  },
  colour_yield_pct: {
    id: "colour_yield_pct",
    name: "Colour Yield Pct",
    type: "number",
  },
  sharpness_of_mark: {
    id: "sharpness_of_mark",
    name: "Sharpness Of Mark",
    type: "string",
  },
  saw_tooth_risk: {
    id: "saw_tooth_risk",
    name: "Saw Tooth Risk",
    type: "string",
  },
  registration_accuracy: {
    id: "registration_accuracy",
    name: "Registration Accuracy",
    type: "string",
  },
  stripe_fault_risk: {
    id: "stripe_fault_risk",
    name: "Stripe Fault Risk",
    type: "string",
  },
  colour_crushing_risk: {
    id: "colour_crushing_risk",
    name: "Colour Crushing Risk",
    type: "string",
  },
  paste_level_instability_risk: {
    id: "paste_level_instability_risk",
    name: "Paste Level Instability Risk",
    type: "string",
  },
  screen_creasing_risk: {
    id: "screen_creasing_risk",
    name: "Screen Creasing Risk",
    type: "string",
  },
  repeat_fitting_quality: {
    id: "repeat_fitting_quality",
    name: "Repeat Fitting Quality",
    type: "string",
  },
  print_wash_fastness: {
    id: "print_wash_fastness",
    name: "Print Wash Fastness",
    type: "number",
  },
  print_light_fastness: {
    id: "print_light_fastness",
    name: "Print Light Fastness",
    type: "number",
  },
  print_rub_fastness_dry: {
    id: "print_rub_fastness_dry",
    name: "Print Rub Fastness Dry",
    type: "number",
  },
  print_rub_fastness_wet: {
    id: "print_rub_fastness_wet",
    name: "Print Rub Fastness Wet",
    type: "number",
  },
  colour_yield_relative: {
    id: "colour_yield_relative",
    name: "Colour Yield Relative",
    type: "number",
  },
  estimated_fixation_pct: {
    id: "estimated_fixation_pct",
    name: "Estimated Fixation Pct",
    type: "number",
  },
  unfixed_dye_staining_risk: {
    id: "unfixed_dye_staining_risk",
    name: "Unfixed Dye Staining Risk",
    type: "string",
  },
  binder_crosslink_quality: {
    id: "binder_crosslink_quality",
    name: "Binder Crosslink Quality",
    type: "string",
  },
  total_water_L_per_kg: {
    id: "total_water_L_per_kg",
    name: "Total Water L Per Kg",
    type: "number",
  },
  total_effluent_dye_load_pct: {
    id: "total_effluent_dye_load_pct",
    name: "Total Effluent Dye Load Pct",
    type: "number",
  },
  energy_index: { id: "energy_index", name: "Energy Index", type: "number" },
  effective_production_m_per_hour: {
    id: "effective_production_m_per_hour",
    name: "Effective Production M Per Hour",
    type: "number",
  },
  machine_efficiency_pct: {
    id: "machine_efficiency_pct",
    name: "Machine Efficiency Pct",
    type: "number",
  },
  warnings: { id: "warnings", name: "Warnings", type: "string" },
};

export const SCREEN_PRINTING_INPUT_DEFS: Record<string, AttributeDefinition> = {
  fiber_type: { id: "fiber_type", name: "Fiber Type", type: "string" },
  fabric_weight_g_per_m2: {
    id: "fabric_weight_g_per_m2",
    name: "Fabric Weight G Per M2",
    type: "number",
  },
  fabric_cover_factor: {
    id: "fabric_cover_factor",
    name: "Fabric Cover Factor",
    type: "number",
  },
  fabric_width_cm: {
    id: "fabric_width_cm",
    name: "Fabric Width Cm",
    type: "number",
  },
  fabric_surface_texture: {
    id: "fabric_surface_texture",
    name: "Fabric Surface Texture",
    type: "string",
  },
  substrate_pH: { id: "substrate_pH", name: "Substrate Ph", type: "number" },
  dye_exhaustion_pct: {
    id: "dye_exhaustion_pct",
    name: "Dye Exhaustion Pct",
    type: "number",
  },
  dye_fixation_pct: {
    id: "dye_fixation_pct",
    name: "Dye Fixation Pct",
    type: "number",
  },
  unfixed_hydrolysed_dye_pct: {
    id: "unfixed_hydrolysed_dye_pct",
    name: "Unfixed Hydrolysed Dye Pct",
    type: "number",
  },
  residual_unfixed_dye_pct: {
    id: "residual_unfixed_dye_pct",
    name: "Residual Unfixed Dye Pct",
    type: "number",
  },
  ground_colour_yield: {
    id: "ground_colour_yield",
    name: "Ground Colour Yield",
    type: "number",
  },
  ground_wash_fastness: {
    id: "ground_wash_fastness",
    name: "Ground Wash Fastness",
    type: "number",
  },
  ground_light_fastness: {
    id: "ground_light_fastness",
    name: "Ground Light Fastness",
    type: "number",
  },
  ground_levelness_risk: {
    id: "ground_levelness_risk",
    name: "Ground Levelness Risk",
    type: "string",
  },
  ground_dye_penetration: {
    id: "ground_dye_penetration",
    name: "Ground Dye Penetration",
    type: "string",
  },
  upstream_water_L_per_kg: {
    id: "upstream_water_L_per_kg",
    name: "Upstream Water L Per Kg",
    type: "number",
  },
  upstream_salt_g_per_kg: {
    id: "upstream_salt_g_per_kg",
    name: "Upstream Salt G Per Kg",
    type: "number",
  },
  substrate_damage_risk: {
    id: "substrate_damage_risk",
    name: "Substrate Damage Risk",
    type: "string",
  },
};
export const SCREEN_PRINTING_CONFIG_DEFS: Record<string, AttributeDefinition> =
{
  machine_type: { id: "machine_type", name: "Machine Type", type: "string" },
  printing_speed_m_per_hour: {
    id: "printing_speed_m_per_hour",
    name: "Printing Speed M Per Hour",
    type: "number",
  },
  number_of_colours: {
    id: "number_of_colours",
    name: "Number Of Colours",
    type: "number",
  },
  screen_type: { id: "screen_type", name: "Screen Type", type: "string" },
  screen_mesh_threads_per_cm: {
    id: "screen_mesh_threads_per_cm",
    name: "Screen Mesh Threads Per Cm",
    type: "number",
  },
  screen_open_area_pct: {
    id: "screen_open_area_pct",
    name: "Screen Open Area Pct",
    type: "number",
  },
  screen_circumference_mm: {
    id: "screen_circumference_mm",
    name: "Screen Circumference Mm",
    type: "number",
  },
  design_repeat_length_cm: {
    id: "design_repeat_length_cm",
    name: "Design Repeat Length Cm",
    type: "number",
  },
  squeegee_type: {
    id: "squeegee_type",
    name: "Squeegee Type",
    type: "string",
  },
  squeegee_angle_deg: {
    id: "squeegee_angle_deg",
    name: "Squeegee Angle Deg",
    type: "number",
  },
  squeegee_hardness_shore: {
    id: "squeegee_hardness_shore",
    name: "Squeegee Hardness Shore",
    type: "number",
  },
  number_of_squeegee_passes: {
    id: "number_of_squeegee_passes",
    name: "Number Of Squeegee Passes",
    type: "number",
  },
  flood_stroke: { id: "flood_stroke", name: "Flood Stroke", type: "boolean" },
  adhesive_type: {
    id: "adhesive_type",
    name: "Adhesive Type",
    type: "string",
  },
  blanket_type: { id: "blanket_type", name: "Blanket Type", type: "string" },
  off_contact_printing: {
    id: "off_contact_printing",
    name: "Off Contact Printing",
    type: "boolean",
  },
  colorant_type: {
    id: "colorant_type",
    name: "Colorant Type",
    type: "string",
  },
  paste_colorant_concentration_g_per_kg: {
    id: "paste_colorant_concentration_g_per_kg",
    name: "Paste Colorant Concentration G Per Kg",
    type: "number",
  },
  thickener_type: {
    id: "thickener_type",
    name: "Thickener Type",
    type: "string",
  },
  thickener_concentration_pct: {
    id: "thickener_concentration_pct",
    name: "Thickener Concentration Pct",
    type: "number",
  },
  paste_viscosity_Pa_s: {
    id: "paste_viscosity_Pa_s",
    name: "Paste Viscosity Pa S",
    type: "number",
  },
  binder_concentration_pct: {
    id: "binder_concentration_pct",
    name: "Binder Concentration Pct",
    type: "number",
  },
  urea_concentration_g_per_kg: {
    id: "urea_concentration_g_per_kg",
    name: "Urea Concentration G Per Kg",
    type: "number",
  },
  alkali_type: { id: "alkali_type", name: "Alkali Type", type: "string" },
  alkali_concentration_g_per_kg: {
    id: "alkali_concentration_g_per_kg",
    name: "Alkali Concentration G Per Kg",
    type: "number",
  },
  design_coverage_pct: {
    id: "design_coverage_pct",
    name: "Design Coverage Pct",
    type: "number",
  },
  fixation_method: {
    id: "fixation_method",
    name: "Fixation Method",
    type: "string",
  },
  fixation_temperature_C: {
    id: "fixation_temperature_C",
    name: "Fixation Temperature C",
    type: "number",
  },
  fixation_time_min: {
    id: "fixation_time_min",
    name: "Fixation Time Min",
    type: "number",
  },
  dryer_efficiency: {
    id: "dryer_efficiency",
    name: "Dryer Efficiency",
    type: "string",
  },
  wash_off_applied: {
    id: "wash_off_applied",
    name: "Wash Off Applied",
    type: "boolean",
  },
  wash_off_temperature_C: {
    id: "wash_off_temperature_C",
    name: "Wash Off Temperature C",
    type: "number",
  },
  wash_off_stages: {
    id: "wash_off_stages",
    name: "Wash Off Stages",
    type: "number",
  },
  ambient_temperature_C: {
    id: "ambient_temperature_C",
    name: "Ambient Temperature C",
    type: "number",
  },
  ambient_humidity_pct: {
    id: "ambient_humidity_pct",
    name: "Ambient Humidity Pct",
    type: "number",
  },
  last_maintenance_date: {
    id: "last_maintenance_date",
    name: "Last Maintenance Date",
    type: "string",
  },
  maintenance_interval_hours: {
    id: "maintenance_interval_hours",
    name: "Maintenance Interval Hours",
    type: "number",
  },
  operating_hours_since_maintenance: {
    id: "operating_hours_since_maintenance",
    name: "Operating Hours Since Maintenance",
    type: "number",
  },
};
export const SCREEN_PRINTING_OUTPUT_DEFS: Record<string, AttributeDefinition> =
{
  paste_volume_applied_g_per_m2: {
    id: "paste_volume_applied_g_per_m2",
    name: "Paste Volume Applied G Per M2",
    type: "number",
  },
  paste_penetration_depth: {
    id: "paste_penetration_depth",
    name: "Paste Penetration Depth",
    type: "string",
  },
  colour_yield_pct: {
    id: "colour_yield_pct",
    name: "Colour Yield Pct",
    type: "number",
  },
  sharpness_of_mark: {
    id: "sharpness_of_mark",
    name: "Sharpness Of Mark",
    type: "string",
  },
  saw_tooth_effect_risk: {
    id: "saw_tooth_effect_risk",
    name: "Saw Tooth Effect Risk",
    type: "string",
  },
  registration_accuracy: {
    id: "registration_accuracy",
    name: "Registration Accuracy",
    type: "string",
  },
  frame_mark_risk: {
    id: "frame_mark_risk",
    name: "Frame Mark Risk",
    type: "string",
  },
  colour_crushing_risk: {
    id: "colour_crushing_risk",
    name: "Colour Crushing Risk",
    type: "string",
  },
  screen_blockage_risk: {
    id: "screen_blockage_risk",
    name: "Screen Blockage Risk",
    type: "string",
  },
  paste_bleeding_risk: {
    id: "paste_bleeding_risk",
    name: "Paste Bleeding Risk",
    type: "string",
  },
  print_wash_fastness: {
    id: "print_wash_fastness",
    name: "Print Wash Fastness",
    type: "number",
  },
  print_light_fastness: {
    id: "print_light_fastness",
    name: "Print Light Fastness",
    type: "number",
  },
  print_rub_fastness_dry: {
    id: "print_rub_fastness_dry",
    name: "Print Rub Fastness Dry",
    type: "number",
  },
  print_rub_fastness_wet: {
    id: "print_rub_fastness_wet",
    name: "Print Rub Fastness Wet",
    type: "number",
  },
  colour_yield_relative: {
    id: "colour_yield_relative",
    name: "Colour Yield Relative",
    type: "number",
  },
  estimated_fixation_pct: {
    id: "estimated_fixation_pct",
    name: "Estimated Fixation Pct",
    type: "number",
  },
  unfixed_dye_staining_risk: {
    id: "unfixed_dye_staining_risk",
    name: "Unfixed Dye Staining Risk",
    type: "string",
  },
  binder_crosslink_quality: {
    id: "binder_crosslink_quality",
    name: "Binder Crosslink Quality",
    type: "string",
  },
  total_water_L_per_kg: {
    id: "total_water_L_per_kg",
    name: "Total Water L Per Kg",
    type: "number",
  },
  total_effluent_dye_load_pct: {
    id: "total_effluent_dye_load_pct",
    name: "Total Effluent Dye Load Pct",
    type: "number",
  },
  energy_index: { id: "energy_index", name: "Energy Index", type: "number" },
  effective_production_m_per_hour: {
    id: "effective_production_m_per_hour",
    name: "Effective Production M Per Hour",
    type: "number",
  },
  machine_efficiency_pct: {
    id: "machine_efficiency_pct",
    name: "Machine Efficiency Pct",
    type: "number",
  },
  warnings: { id: "warnings", name: "Warnings", type: "string" },
};

// ---------------------------------------------------------------------------
// Sane default values for every known machine attribute.
// Used by buildInstances so forms/simulations start with realistic numbers.
// ---------------------------------------------------------------------------
export const ATTRIBUTE_DEFAULTS: Record<string, any> = {
  // ── shared fiber / yarn inputs ──────────────────────────────────────────
  fiber_type: "Cotton",
  fiber_length_mm: 28,
  fiber_fineness_dtex: 1.7,
  short_fiber_content_pct: 10,
  fiber_tensile_strength_cN_tex: 25,
  sliver_count_ktex: 5.0,
  moisture_content_pct: 8,
  trash_content_pct: 2,
  moisture_regain_pct: 8,

  // ── shared ambient / maintenance ────────────────────────────────────────
  ambient_temperature_C: 25,
  ambient_humidity_pct: 60,
  last_maintenance_date: "",
  maintenance_interval_hours: 500,
  operating_hours_since_maintenance: 0,

  // ── shared yarn counts ──────────────────────────────────────────────────
  yarn_count_Ne: 20,
  yarn_count_tex: 30,
  yarn_count_dtex: 167,
  yarn_tenacity_cN_tex: 20,
  yarn_evenness_CVm_pct: 12,
  hairiness_H: 4,
  yarn_hairiness_H: 1,
  neps_per_km: 100,
  twist_multiplier: 3.8,

  // ── rotor spinning config ───────────────────────────────────────────────
  rotor_diameter_mm: 33,
  rotor_speed_rpm: 80000,
  twist_factor_am: 130,
  opening_roller_speed_rpm: 8000,
  opening_roller_wire_type: "OK-40",
  navel_type: "T-3",
  rotor_groove_type: "SH",
  total_draft_ratio: 150,
  delivery_speed_m_min: 120,

  // ── rotor spinning outputs ──────────────────────────────────────────────
  actual_twist_turns_per_m: 870,
  back_doubling_index: 1.5,
  yarn_tenacity_cN_tex_out: 12,
  yarn_evenness_CVm_pct_out: 14,
  spinning_tension_cN: 8,
  waste_fiber_pct: 3,
  ends_down_risk: "low",
  production_rate_g_rotor_h: 150,

  // ── airjet spinning config ──────────────────────────────────────────────
  pre_draft_ratio: 1.2,
  break_draft_ratio: 3.0,
  main_draft_ratio: 55,
  draft_zone_distance_A_mm: 43,
  draft_zone_distance_B_mm: 48,
  air_pressure_bar: 5,
  distance_L_mm: 20,
  spinning_draft: 200,
  package_diameter_mm: 300,

  // ── airjet spinning outputs ─────────────────────────────────────────────
  wrapping_twist_am: 130,
  wrapping_fiber_pct: 15,
  production_rate_g_spi_h: 400,

  // ── plain / dobby weaving inputs ────────────────────────────────────────
  warp_yarn_count_tex: 30,
  warp_yarn_count_Ne: 20,
  warp_yarn_tenacity_cN_tex: 20,
  warp_yarn_CVm_pct: 12,
  warp_yarn_hairiness_H: 4,
  warp_yarn_twist_t_per_m: 700,
  warp_yarn_type: "Cotton",
  weft_yarn_count_tex: 30,
  weft_yarn_count_Ne: 20,
  weft_yarn_tenacity_cN_tex: 20,
  weft_yarn_CVm_pct: 12,
  weft_yarn_hairiness_H: 4,
  weft_yarn_twist_t_per_m: 700,
  weft_yarn_type: "Cotton",
  warp_sizing_applied: true,
  size_add_on_pct: 12,

  // ── plain weaving config ────────────────────────────────────────────────
  ends_per_cm: 25,
  picks_per_cm: 23,
  reed_width_cm: 180,
  loom_speed_picks_per_min: 700,
  loom_type: "Rapier",
  warp_tension_cN_per_end: 15,
  let_off_type: "Electronic",
  take_up_type: "Electronic",
  shed_depth_cm: 12,
  heald_shaft_count: 4,
  temple_type: "Ring",

  // ── plain weaving outputs ───────────────────────────────────────────────
  yarn_diameter_warp_mm: 0.18,
  yarn_diameter_weft_mm: 0.18,
  warp_cover_factor: 0.80,
  weft_cover_factor: 0.75,
  total_cover_factor: 0.94,
  warp_crimp_pct: 8,
  weft_crimp_pct: 4,
  crimp_balance: "balanced",
  fell_displacement_mm: 2,
  beat_up_force_cN_per_cm: 400,
  fabric_areal_weight_g_m2: 150,
  weft_tension_at_fell_cN: 5,
  warp_break_risk: "low",
  weft_break_risk: "low",
  cloth_defect_risk: "low",
  production_rate_m_per_min: 0.58,
  production_rate_m2_per_hour: 62,

  // ── dobby weaving config ────────────────────────────────────────────────
  number_of_heald_shafts: 8,
  weave_repeat_ends: 8,
  weave_repeat_picks: 8,
  ends_per_cm_per_shaft: 3,
  shed_depth_mm: 120,
  shed_type: "Positive",
  dobby_type: "Electronic",
  weft_insertion_type: "Rapier",
  reed_space_cm: 180,
  shuttle_mass_g: 0,
  warp_ends_per_cm: 25,
  weft_picks_per_cm: 20,
  float_length_warp: 3,
  float_length_weft: 3,
  interlacement_ratio: 0.5,
  take_up_picks_per_cm: 20,
  reed_count_dents_per_cm: 12,
  ends_per_dent: 2,
  selvedge_type: "Leno",

  // ── dobby weaving outputs ───────────────────────────────────────────────
  fabric_width_cm: 150,
  fabric_weight_g_per_m2: 180,
  cloth_cover_factor: 0.94,
  warp_end_break_risk: "low",
  shedding_quality: "good",
  beat_up_resistance: "normal",
  expected_nep_visibility: "low",
  pick_spacing_regularity: "good",
  selvedge_quality: "good",
  theoretical_production_m_per_hour: 30,
  loom_efficiency_pct: 85,
  actual_production_m_per_hour: 25.5,

  // ── weft knitting config ────────────────────────────────────────────────
  machine_gauge_npi: 24,
  cylinder_diameter_inch: 30,
  number_of_feeds: 96,
  stitch_length_mm: 2.8,
  machine_rpm: 25,
  yarn_input_tension_cN: 15,
  take_down_tension_cN_per_cm: 8,
  needle_type: "Latch",
  structure_type: "Single Jersey",
  relaxation_state: "Dry relaxed",

  // ── weft knitting outputs ───────────────────────────────────────────────
  tightness_factor: 14,
  courses_per_cm: 14,
  wales_per_cm: 12,
  stitch_density_per_cm2: 168,
  loop_shape_factor: 1.17,
  width_relaxation_pct: 5,
  length_relaxation_pct: 8,
  total_needles: 2256,
  courses_per_minute: 350,
  fabric_production_rate_m_min: 0.025,
  fabric_production_rate_m2_hr: 3.6,
  fabric_width_m: 1.5,
  needle_break_risk: "low",
  yarn_break_risk: "low",
  fabric_defect_risk: "low",
  pilling_propensity: "moderate",

  // ── warp knitting inputs ────────────────────────────────────────────────
  warp_yarn_quality_risk: "low",
  weft_yarn_quality_risk: "low",
  substrate_nep_visibility: "low",
  substrate_regularity: "good",
  substrate_selvedge_quality: "good",
  upstream_process_efficiency_pct: 85,
  upstream_feed_rate_m_per_hour: 25,

  // ── warp knitting config ────────────────────────────────────────────────
  machine_class: "Tricot",
  gauge_E: 28,
  knitting_width_cm: 430,
  number_of_guide_bars: 3,
  threading_density: "Full",
  underlap_span_needles: 2,
  lapping_type: "Closed",
  overlap_direction: "Reverse",
  pattern_control: "Electronic",
  machine_speed_cpm: 1800,
  run_in_ratio_front_back: 1.2,
  sinker_depth_mm: 3,
  shed_swing_angle_deg: 12,

  // ── warp knitting outputs ───────────────────────────────────────────────
  fabric_width_finished_cm: 400,
  fabric_stability: "good",
  loop_formation_quality: "good",
  yarn_tension_balance: "balanced",
  underlap_regularity: "good",
  surface_nep_visibility: "low",
  barre_risk: "low",
  selvedge_security: "good",
  cover_adequacy: "good",
  extensibility_rating: "moderate",
  fabric_curling_tendency: "low",
  machine_efficiency_pct: 88,

  // ── reactive dyeing config ──────────────────────────────────────────────
  dye_type: "Reactive",
  dye_concentration_owf_pct: 3,
  salt_concentration_g_L: 60,
  alkali_type: "Soda ash",
  alkali_concentration_g_L: 15,
  dyeing_temperature_C: 60,
  exhaustion_time_min: 45,
  fixation_time_min: 45,
  wash_off_time_min: 30,
  liquor_ratio: 10,
  machine_type: "Jet",
  water_hardness_ppm: 50,
  fabric_is_mercerized: false,
  fabric_is_scoured: true,

  // ── reactive dyeing outputs ─────────────────────────────────────────────
  dye_bath_pH: 11.5,
  exhaustion_pct: 65,
  fixation_pct: 60,
  hydrolysis_pct: 10,
  unfixed_dye_on_fabric_pct: 5,
  colour_yield_relative: 85,
  wash_fastness_rating: 4,
  light_fastness_rating: 4,
  rubbing_fastness_dry: 4,
  rubbing_fastness_wet: 3,
  levelness_risk: "low",
  dye_penetration_quality: "good",
  water_consumption_L_per_kg: 80,
  salt_load_g_per_kg: 600,
  total_process_time_min: 180,
  energy_relative: 75,
  effluent_dye_load_pct: 30,
  unlevel_dyeing_risk: "low",
  fabric_damage_risk: "low",

  // ── rotary / screen printing inputs ─────────────────────────────────────
  fabric_cover_factor: 0.94,
  fabric_surface_texture: "smooth",
  substrate_pH: 7,
  dye_exhaustion_pct: 65,
  dye_fixation_pct: 60,
  unfixed_hydrolysed_dye_pct: 10,
  residual_unfixed_dye_pct: 5,
  ground_colour_yield: 85,
  ground_wash_fastness: 4,
  ground_light_fastness: 4,
  ground_levelness_risk: "low",
  ground_dye_penetration: "good",
  upstream_water_L_per_kg: 80,
  upstream_salt_g_per_kg: 600,
  substrate_damage_risk: "low",

  // ── rotary printing config ──────────────────────────────────────────────
  printing_speed_m_per_hour: 80,
  screen_working_width_cm: 160,
  number_of_screens: 8,
  screen_type: "Rotary",
  screen_mesh_holes_per_inch: 125,
  screen_open_area_pct: 20,
  screen_wall_thickness_mm: 0.1,
  screen_circumference_mm: 641,
  design_repeat_length_cm: 64,
  squeegee_type: "Magnetic",
  squeegee_blade_length_mm: 160,
  squeegee_pressure_setting: "medium",
  squeegee_blade_curvature: "straight",
  blanket_type: "Rubber",
  adhesive_type: "Thermoplastic",
  independent_screen_speed_control: true,
  laser_registration: true,
  paste_pump_type: "Gear",
  level_control_type: "Automatic",
  paste_distribution_quality: "good",
  colorant_type: "Reactive dye",
  paste_colorant_conc_g_per_kg: 30,
  thickener_type: "Sodium alginate",
  thickener_concentration_pct: 2,
  paste_viscosity_Pa_s: 8,
  paste_yield_value: "medium",
  binder_concentration_pct: 0,
  urea_concentration_g_per_kg: 100,
  alkali_concentration_g_per_kg: 15,
  design_coverage_pct: 30,
  fixation_method: "Steam",
  fixation_temperature_C: 102,
  steamer_type: "Star",
  dryer_capacity: "adequate",
  wash_off_applied: true,
  wash_off_temperature_C: 60,
  wash_off_stages: 4,
  counterflow_washing: true,

  // ── rotary printing outputs ─────────────────────────────────────────────
  paste_volume_applied_g_per_m2: 40,
  paste_penetration_depth: "medium",
  colour_yield_pct: 85,
  sharpness_of_mark: "good",
  saw_tooth_risk: "low",
  registration_accuracy: "good",
  stripe_fault_risk: "low",
  colour_crushing_risk: "low",
  paste_level_instability_risk: "low",
  screen_creasing_risk: "low",
  repeat_fitting_quality: "good",
  print_wash_fastness: 4,
  print_light_fastness: 4,
  print_rub_fastness_dry: 4,
  print_rub_fastness_wet: 3,
  estimated_fixation_pct: 70,
  unfixed_dye_staining_risk: "low",
  binder_crosslink_quality: "good",
  total_water_L_per_kg: 100,
  total_effluent_dye_load_pct: 30,
  energy_index: 75,
  effective_production_m_per_hour: 68,

  // ── screen printing config (overrides / additions) ───────────────────────
  number_of_colours: 6,
  screen_mesh_threads_per_cm: 55,
  squeegee_angle_deg: 70,
  squeegee_hardness_shore: 65,
  number_of_squeegee_passes: 1,
  flood_stroke: true,
  off_contact_printing: false,
  paste_colorant_concentration_g_per_kg: 30,
  dryer_efficiency: "good",

  // ── screen printing outputs (overrides / additions) ──────────────────────
  saw_tooth_effect_risk: "low",
  frame_mark_risk: "low",
  screen_blockage_risk: "low",
  paste_bleeding_risk: "low",

  // ── shared output fields ────────────────────────────────────────────────
  warnings: "",
};

export function buildInstances(
  defs: Record<string, AttributeDefinition>,
): Record<string, AttributeInstance> {
  const instances: Record<string, AttributeInstance> = {};
  for (const [key, def] of Object.entries(defs)) {
    let fallback: any = "";
    if (def.type === "number") fallback = 0;
    else if (def.type === "boolean") fallback = false;
    const value = def.defaultValue ?? ATTRIBUTE_DEFAULTS[key] ?? fallback;
    instances[key] = { definition: def, value };
  }
  return instances;
}

export const AVAILABLE_MACHINES: MachineTypeConfig[] = [
  {
    process: MachineProcess.SPINNING,
    subprocess: "rotor spinning",
    name: "Rotor Spinning",
    description: "Rotor Spinning machine",
    color: "#2563EB",
    icon: "Factory",
    defaultAttributes: {
      inputs: buildInstances(ROTOR_SPINNING_INPUT_DEFS),
      configs: buildInstances(ROTOR_SPINNING_CONFIG_DEFS),
      outputs: buildInstances(ROTOR_SPINNING_OUTPUT_DEFS),
    },
  },
  {
    process: MachineProcess.SPINNING,
    subprocess: "air-jet spinning",
    name: "Air-Jet Spinning",
    description: "Air-Jet Spinning machine",
    color: "#1D4ED8",
    icon: "Zap",
    defaultAttributes: {
      inputs: buildInstances(AIRJET_SPINNING_INPUT_DEFS),
      configs: buildInstances(AIRJET_SPINNING_CONFIG_DEFS),
      outputs: buildInstances(AIRJET_SPINNING_OUTPUT_DEFS),
    },
  },
  {
    process: MachineProcess.WEAVING,
    subprocess: "plain weaving",
    name: "Plain Weaving",
    description: "Plain Weaving machine",
    color: "#EF4444",
    icon: "Move3d",
    defaultAttributes: {
      inputs: buildInstances(PLAIN_WEAVING_INPUT_DEFS),
      configs: buildInstances(PLAIN_WEAVING_CONFIG_DEFS),
      outputs: buildInstances(PLAIN_WEAVING_OUTPUT_DEFS),
    },
  },
  {
    process: MachineProcess.WEAVING,
    subprocess: "dobby weaving",
    name: "Dobby Weaving",
    description: "Dobby Weaving machine",
    color: "#DC2626",
    icon: "Move3d",
    defaultAttributes: {
      inputs: buildInstances(DOBBY_WEAVING_INPUT_DEFS),
      configs: buildInstances(DOBBY_WEAVING_CONFIG_DEFS),
      outputs: buildInstances(DOBBY_WEAVING_OUTPUT_DEFS),
    },
  },
  {
    process: MachineProcess.KNITTING,
    subprocess: "weft knitting",
    name: "Weft Knitting",
    description: "Weft Knitting machine",
    color: "#22C55E",
    icon: "Wrench",
    defaultAttributes: {
      inputs: buildInstances(WEFT_KNITTING_INPUT_DEFS),
      configs: buildInstances(WEFT_KNITTING_CONFIG_DEFS),
      outputs: buildInstances(WEFT_KNITTING_OUTPUT_DEFS),
    },
  },
  {
    process: MachineProcess.KNITTING,
    subprocess: "warp knitting",
    name: "Warp Knitting",
    description: "Warp Knitting machine",
    color: "#15803D",
    icon: "Move3d",
    defaultAttributes: {
      inputs: buildInstances(WARP_KNITTING_INPUT_DEFS),
      configs: buildInstances(WARP_KNITTING_CONFIG_DEFS),
      outputs: buildInstances(WARP_KNITTING_OUTPUT_DEFS),
    },
  },
  {
    process: MachineProcess.COLORING,
    subprocess: "reactive dyeing",
    name: "Reactive Dyeing",
    description: "Reactive Dyeing machine",
    color: "#8B5CF6",
    icon: "Zap",
    defaultAttributes: {
      inputs: buildInstances(REACTIVE_DYEING_INPUT_DEFS),
      configs: buildInstances(REACTIVE_DYEING_CONFIG_DEFS),
      outputs: buildInstances(REACTIVE_DYEING_OUTPUT_DEFS),
    },
  },
  {
    process: MachineProcess.PRINTING,
    subprocess: "rotary printing",
    name: "Rotary Printing",
    description: "Rotary Printing machine",
    color: "#0891B2",
    icon: "Scan",
    defaultAttributes: {
      inputs: buildInstances(ROTARY_PRINTING_INPUT_DEFS),
      configs: buildInstances(ROTARY_PRINTING_CONFIG_DEFS),
      outputs: buildInstances(ROTARY_PRINTING_OUTPUT_DEFS),
    },
  },
  {
    process: MachineProcess.PRINTING,
    subprocess: "screen printing",
    name: "Screen Printing",
    description: "Screen Printing machine",
    color: "#06B6D4",
    icon: "Scan",
    defaultAttributes: {
      inputs: buildInstances(SCREEN_PRINTING_INPUT_DEFS),
      configs: buildInstances(SCREEN_PRINTING_CONFIG_DEFS),
      outputs: buildInstances(SCREEN_PRINTING_OUTPUT_DEFS),
    },
  },
];

export enum PipelineStatus {
  DRAFT = "DRAFT",
  RUNNING = "RUNNING",
  ARCHIVED = "ARCHIVED",
}

export const createProductionLineRequestSchema = z.object({
  name: z.string(),
  status: z.enum(PipelineStatus),
});
export type CreateProductionLineRequest = z.infer<
  typeof createProductionLineRequestSchema
>;

export const updateProductionLineRequestSchema =
  createProductionLineRequestSchema.partial();
export type UpdateProductionLineRequest = z.infer<
  typeof updateProductionLineRequestSchema
>;

export const productionLineResponseSchema =
  createProductionLineRequestSchema.extend({
    id: z.string(),
    project_id: z.string(),
    created_at: z.coerce.date(),
    updated_at: z.coerce.date(),
  });
export type ProductionLineResponse = z.infer<
  typeof productionLineResponseSchema
>;

export const productionLineListResponseSchema = z.array(
  productionLineResponseSchema,
);
export type ProductionLineListResponse = z.infer<
  typeof productionLineListResponseSchema
>;

/**
 * Derive the UI color for a machine based on its process type.
 * Falls back to the first AVAILABLE_MACHINES entry for that process, or a default gray.
 */
export function getColorForProcess(process: string): string {
  const machine = AVAILABLE_MACHINES.find((m) => m.process === process);
  return machine?.color ?? "#6B7280";
}

/**
 * Derive the UI icon name for a machine based on its process type.
 * Falls back to "Factory".
 */
export function getIconForProcess(process: string): string {
  const machine = AVAILABLE_MACHINES.find((m) => m.process === process);
  return machine?.icon ?? "Factory";
}
