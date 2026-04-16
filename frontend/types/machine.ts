export enum MachineParameterType {
  NUMBER = "number",
}

export interface Metadata {
  name: string;
  description: string;
}

export interface MachineParameter {
  metadata: Metadata;
  type: MachineParameterType;
  value: number;
  unit?: string;
}

export interface Machine {
  metadata: Metadata;
  parameters: MachineParameter[];
}

export enum MachineType {
  CNC = "cnc",
  PRESS = "press",
  CONVEYOR = "conveyor",
  ROBOT = "robot",
  SCANNER = "scanner",
  WELDER = "welder",
  ASSEMBLER = "assembler",
}

export interface MachineTypeConfig {
  type: MachineType;
  name: string;
  description: string;
  color: string;
  icon: string;
  defaultParameters: MachineParameter[];
}

export const MACHINE_CONFIGS: Record<MachineType, MachineTypeConfig> = {
  [MachineType.CNC]: {
    type: MachineType.CNC,
    name: "CNC Machine",
    description: "Computer Numerical Control machine for precision cutting",
    color: "#3B82F6",
    icon: "Factory",
    defaultParameters: [
      {
        metadata: { name: "Spindle Speed", description: "Rotation speed of the spindle" },
        type: MachineParameterType.NUMBER,
        value: 3000,
        unit: "RPM",
      },
      {
        metadata: { name: "Feed Rate", description: "Feed rate of the cutting tool" },
        type: MachineParameterType.NUMBER,
        value: 500,
        unit: "mm/min",
      },
    ],
  },
  [MachineType.PRESS]: {
    type: MachineType.PRESS,
    name: "Hydraulic Press",
    description: "Industrial press for shaping and forming materials",
    color: "#EF4444",
    icon: "Hammer",
    defaultParameters: [
      {
        metadata: { name: "Force", description: "Pressing force" },
        type: MachineParameterType.NUMBER,
        value: 100,
        unit: "kN",
      },
      {
        metadata: { name: "Stroke", description: "Press stroke length" },
        type: MachineParameterType.NUMBER,
        value: 200,
        unit: "mm",
      },
    ],
  },
  [MachineType.CONVEYOR]: {
    type: MachineType.CONVEYOR,
    name: "Conveyor Belt",
    description: "Automated material handling system",
    color: "#22C55E",
    icon: "Move3d",
    defaultParameters: [
      {
        metadata: { name: "Speed", description: "Belt speed" },
        type: MachineParameterType.NUMBER,
        value: 1.5,
        unit: "m/s",
      },
      {
        metadata: { name: "Width", description: "Belt width" },
        type: MachineParameterType.NUMBER,
        value: 600,
        unit: "mm",
      },
    ],
  },
  [MachineType.ROBOT]: {
    type: MachineType.ROBOT,
    name: "Industrial Robot",
    description: "Programmable robotic arm for automation",
    color: "#8B5CF6",
    icon: "Bot",
    defaultParameters: [
      {
        metadata: { name: "Reach", description: "Maximum reach radius" },
        type: MachineParameterType.NUMBER,
        value: 1850,
        unit: "mm",
      },
      {
        metadata: { name: "Payload", description: "Maximum payload capacity" },
        type: MachineParameterType.NUMBER,
        value: 6,
        unit: "kg",
      },
    ],
  },
  [MachineType.SCANNER]: {
    type: MachineType.SCANNER,
    name: "3D Scanner",
    description: "3D scanning system for quality inspection",
    color: "#06B6D4",
    icon: "Scan",
    defaultParameters: [
      {
        metadata: { name: "Resolution", description: "Scan resolution" },
        type: MachineParameterType.NUMBER,
        value: 0.1,
        unit: "mm",
      },
      {
        metadata: { name: "Accuracy", description: "Measurement accuracy" },
        type: MachineParameterType.NUMBER,
        value: 0.05,
        unit: "mm",
      },
    ],
  },
  [MachineType.WELDER]: {
    type: MachineType.WELDER,
    name: "Welding Station",
    description: "Automated welding system",
    color: "#F59E0B",
    icon: "Zap",
    defaultParameters: [
      {
        metadata: { name: "Amperage", description: "Welding amperage" },
        type: MachineParameterType.NUMBER,
        value: 200,
        unit: "A",
      },
      {
        metadata: { name: "Wire Speed", description: "Wire feed speed" },
        type: MachineParameterType.NUMBER,
        value: 8,
        unit: "m/min",
      },
    ],
  },
  [MachineType.ASSEMBLER]: {
    type: MachineType.ASSEMBLER,
    name: "Assembly Station",
    description: "Automated assembly and fastening system",
    color: "#EC4899",
    icon: "Wrench",
    defaultParameters: [
      {
        metadata: { name: "Torque", description: "Fastening torque" },
        type: MachineParameterType.NUMBER,
        value: 10,
        unit: "Nm",
      },
      {
        metadata: { name: "Cycle Time", description: "Assembly cycle time" },
        type: MachineParameterType.NUMBER,
        value: 5,
        unit: "s",
      },
    ],
  },
};

export const AVAILABLE_MACHINES = Object.values(MACHINE_CONFIGS);
