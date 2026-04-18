
export type Visibility = "private" | "public";

export type Project = {
  project_id: string;                 
  name: string;
  project_manager: string;           
  visibility: Visibility;
  production_lines: string[];
  shift_supervisors: string[];      
  created_at: string;               
  updated_at: string;               
};

export type CreateProjectDTO = {
  name: string;
  project_manager: string;
  visibility: Visibility;
  production_lines: string[];
  shift_supervisors?: string[];
};

export type UpdateProjectDTO = {
  name?: string;
  project_manager?: string;
  visibility?: Visibility;
  production_lines?: string[];
  shift_supervisors?: string[];
};