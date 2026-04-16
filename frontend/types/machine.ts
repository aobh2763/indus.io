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
  name: string;
  description: string;
  color: string;
  icon: string;
  defaultAttributes: ProcessAttributes;
}

export const SPINNING_INPUT_DEFS: Record<string, AttributeDefinition> = {
  fiber_type: { id: "fiber_type", name: "Fiber Type", type: "string" },
  fiber_blend: { id: "fiber_blend", name: "Fiber Blend", type: "string" },
  blend_composition: { id: "blend_composition", name: "Blend Composition", type: "string" },
  fiber_length: { id: "fiber_length", name: "Fiber Length", type: "number", unit: "mm" },
  fiber_fineness: { id: "fiber_fineness", name: "Fiber Fineness", type: "number" },
  fiber_tensile_strength: { id: "fiber_tensile_strength", name: "Fiber Tensile Strength", type: "number" },
  fiber_elongation: { id: "fiber_elongation", name: "Fiber Elongation", type: "number", unit: "%" },
  fiber_maturity: { id: "fiber_maturity", name: "Fiber Maturity", type: "number" },
  fiber_uniformity_index: { id: "fiber_uniformity_index", name: "Fiber Uniformity Index", type: "number" },
  moisture_content: { id: "moisture_content", name: "Moisture Content", type: "number", unit: "%" },
  trash_content: { id: "trash_content", name: "Trash Content", type: "number", unit: "%" },
  fiber_entanglement_level: { id: "fiber_entanglement_level", name: "Fiber Entanglement Level", type: "number" },
  input_form: { id: "input_form", name: "Input Form", type: "string" },
  input_linear_density: { id: "input_linear_density", name: "Input Linear Density", type: "number" },
  input_feed_rate: { id: "input_feed_rate", name: "Input Feed Rate", type: "number" },
};

export const SPINNING_OUTPUT_DEFS: Record<string, AttributeDefinition> = {
  yarn_count: { id: "yarn_count", name: "Yarn Count", type: "number" },
  yarn_type: { id: "yarn_type", name: "Yarn Type", type: "string" },
  twist_direction: { id: "twist_direction", name: "Twist Direction", type: "string" },
  yarn_evenness_cvm: { id: "yarn_evenness_cvm", name: "Yarn Evenness CVM", type: "number" },
  yarn_tensile_strength: { id: "yarn_tensile_strength", name: "Yarn Tensile Strength", type: "number" },
  yarn_elongation_at_break: { id: "yarn_elongation_at_break", name: "Yarn Elongation at Break", type: "number", unit: "%" },
  yarn_hairiness_index: { id: "yarn_hairiness_index", name: "Yarn Hairiness Index", type: "number" },
  yarn_twist_per_meter: { id: "yarn_twist_per_meter", name: "Yarn Twist per Meter", type: "number" },
  thick_placer_per_km: { id: "thick_placer_per_km", name: "Thick Places per km", type: "number" },
  neps_per_km: { id: "neps_per_km", name: "Neps per km", type: "number" },
  yarn_breakage_rate: { id: "yarn_breakage_rate", name: "Yarn Breakage Rate", type: "number", unit: "%" },
  production_rate: { id: "production_rate", name: "Production Rate", type: "number" },
  waste_percentage: { id: "waste_percentage", name: "Waste Percentage", type: "number", unit: "%" },
};

export function buildInstances(defs: Record<string, AttributeDefinition>): Record<string, AttributeInstance> {
  const instances: Record<string, AttributeInstance> = {};
  for (const [key, def] of Object.entries(defs)) {
    let defaultValue: any = "";
    if (def.type === "number") defaultValue = 0;
    else if (def.type === "boolean") defaultValue = false;
    instances[key] = { definition: def, value: defaultValue };
  }
  return instances;
}

export const AVAILABLE_MACHINES: MachineTypeConfig[] = [
  // SPINNING
  {
    process: MachineProcess.SPINNING,
    name: "Ring Spinning Frame",
    description: "The most versatile method for producing high-quality, strong yarn for various applications.",
    color: "#3B82F6",
    icon: "Factory",
    defaultAttributes: {
      inputs: buildInstances(SPINNING_INPUT_DEFS),
      configs: {},
      outputs: buildInstances(SPINNING_OUTPUT_DEFS),
    },
  },
  {
    process: MachineProcess.SPINNING,
    name: "Rotor Spinning Machine",
    description: "High-speed production method ideal for producing coarser yarns efficiently.",
    color: "#2563EB",
    icon: "Factory",
    defaultAttributes: {
      inputs: buildInstances(SPINNING_INPUT_DEFS),
      configs: {},
      outputs: buildInstances(SPINNING_OUTPUT_DEFS),
    },
  },
  {
    process: MachineProcess.SPINNING,
    name: "Air-Jet Spinning Machine",
    description: "Uses compressed air for ultra-high-speed yarn formation with low hairiness.",
    color: "#1D4ED8",
    icon: "Zap",
    defaultAttributes: {
      inputs: buildInstances(SPINNING_INPUT_DEFS),
      configs: {},
      outputs: buildInstances(SPINNING_OUTPUT_DEFS),
    },
  },

  // WEAVING
  {
    process: MachineProcess.WEAVING,
    name: "Air-Jet Loom",
    description: "High-speed weaving machine using air pulses to insert the weft yarn.",
    color: "#EF4444",
    icon: "Move3d",
    defaultAttributes: { inputs: {}, configs: {}, outputs: {} },
  },
  {
    process: MachineProcess.WEAVING,
    name: "Rapier Loom",
    description: "Highly versatile weaving machine suitable for complex patterns and diverse yarn types.",
    color: "#DC2626",
    icon: "Move3d",
    defaultAttributes: { inputs: {}, configs: {}, outputs: {} },
  },
  {
    process: MachineProcess.WEAVING,
    name: "Projectile Loom",
    description: "Specialized for wide-width fabrics and heavy industrial textiles.",
    color: "#B91C1C",
    icon: "Move3d",
    defaultAttributes: { inputs: {}, configs: {}, outputs: {} },
  },

  // KNITTING
  {
    process: MachineProcess.KNITTING,
    name: "Circular Knitting Machine",
    description: "Continuous production of seamless tubular fabrics for garments like t-shirts.",
    color: "#22C55E",
    icon: "Wrench",
    defaultAttributes: { inputs: {}, configs: {}, outputs: {} },
  },
  {
    process: MachineProcess.KNITTING,
    name: "Flat Knitting Machine",
    description: "Perfect for producing sweaters, collars, and sophisticated technical 3D knits.",
    color: "#16A34A",
    icon: "Wrench",
    defaultAttributes: { inputs: {}, configs: {}, outputs: {} },
  },
  {
    process: MachineProcess.KNITTING,
    name: "Warp Knitting Machine",
    description: "Produces stable, run-proof fabrics like lace, tulle, and technical mesh.",
    color: "#15803D",
    icon: "Move3d",
    defaultAttributes: { inputs: {}, configs: {}, outputs: {} },
  },

  // COLORING
  {
    process: MachineProcess.COLORING,
    name: "Jet Dyeing Machine",
    description: "High-pressure, low-liquor ratio dyeing for synthetic and blended fabrics.",
    color: "#8B5CF6",
    icon: "Zap",
    defaultAttributes: { inputs: {}, configs: {}, outputs: {} },
  },
  {
    process: MachineProcess.COLORING,
    name: "Beam Dyeing Machine",
    description: "Ideal for delicate or high-density fabrics processed in open-width form.",
    color: "#7C3AED",
    icon: "Zap",
    defaultAttributes: { inputs: {}, configs: {}, outputs: {} },
  },
  {
    process: MachineProcess.COLORING,
    name: "Package Dyeing Machine",
    description: "Directly dyes yarn wound on perforated tubes for maximum efficiency.",
    color: "#6D28D9",
    icon: "Zap",
    defaultAttributes: { inputs: {}, configs: {}, outputs: {} },
  },

  // PRINTING
  {
    process: MachineProcess.PRINTING,
    name: "Digital Inkjet Printer",
    description: "High-precision photographic quality printing for complex designs and small runs.",
    color: "#06B6D4",
    icon: "Scan",
    defaultAttributes: { inputs: {}, configs: {}, outputs: {} },
  },
  {
    process: MachineProcess.PRINTING,
    name: "Rotary Screen Printer",
    description: "Continuous high-speed printing process for large volume multi-color production.",
    color: "#0891B2",
    icon: "Scan",
    defaultAttributes: { inputs: {}, configs: {}, outputs: {} },
  },

  // FINISHING
  {
    process: MachineProcess.FINISHING,
    name: "Stenter Frame Machine",
    description: "Essential for drying, heat-setting, and controlling fabric width and alignment.",
    color: "#F59E0B",
    icon: "Zap",
    defaultAttributes: { inputs: {}, configs: {}, outputs: {} },
  },
  {
    process: MachineProcess.FINISHING,
    name: "Calender Machine",
    description: "Applies intense pressure and heat to create smooth, glossy, or embossed finishes.",
    color: "#D97706",
    icon: "Zap",
    defaultAttributes: { inputs: {}, configs: {}, outputs: {} },
  },

  // SEWING
  {
    process: MachineProcess.SEWING,
    name: "Industrial Lockstitch Machine",
    description: "The fundamental machine for creating high-strength, basic seams in apparel.",
    color: "#EC4899",
    icon: "Hammer",
    defaultAttributes: { inputs: {}, configs: {}, outputs: {} },
  },
  {
    process: MachineProcess.SEWING,
    name: "Overlock Serger Machine",
    description: "Trims edges and provides professional overcasting for knit and stretch fabrics.",
    color: "#DB2777",
    icon: "Hammer",
    defaultAttributes: { inputs: {}, configs: {}, outputs: {} },
  },

  // Technical Processes
  {
    process: MachineProcess.COATING,
    name: "Knife-over-Roll Coater",
    description: "Precision application of chemical coatings for waterproof and technical textiles.",
    color: "#F43F5E",
    icon: "Wrench",
    defaultAttributes: { inputs: {}, configs: {}, outputs: {} },
  },
  {
    process: MachineProcess.LAMINATING,
    name: "Hot Melt Laminator",
    description: "Eco-friendly bonding of fabric layers using thermoplastic adhesives.",
    color: "#10B981",
    icon: "Move3d",
    defaultAttributes: { inputs: {}, configs: {}, outputs: {} },
  },
  {
    process: MachineProcess.EMBROIDERY,
    name: "Multi-head Embroidery Machine",
    description: "Automated pattern stitching across multiple garments simultaneously.",
    color: "#EAB308",
    icon: "Bot",
    defaultAttributes: { inputs: {}, configs: {}, outputs: {} },
  },
  {
    process: MachineProcess.FELTING,
    name: "Needle Punching Machine",
    description: "Mechanical entanglement of fibers to produce durable non-woven industrial felt.",
    color: "#6366F1",
    icon: "Factory",
    defaultAttributes: { inputs: {}, configs: {}, outputs: {} },
  },
];
