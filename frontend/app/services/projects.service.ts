import type {
  Project,
  CreateProjectDTO,
  UpdateProjectDTO,
} from "../../types/project";

const BASE_URL = "http://localhost:8000/projects";
function normalizeProject(raw: any): Project {
  return {
    project_id: raw.project_id,
    name: raw.name,
    project_manager: raw.project_manager,
    visibility: raw.visibility,
    production_lines: raw.production_lines ?? [],
    shift_supervisors: raw.shift_supervisors
      ? raw.shift_supervisors.map((s: any) => s.user_id)
      : [],
    created_at: raw.created_at,
    updated_at: raw.updated_at,
  };
}

export const ProjectsService = {
  async getAll(): Promise<Project[]> {
    const res = await fetch(BASE_URL);
    const data = await res.json();
    return data.map(normalizeProject);
  },

  async getOne(id: string): Promise<Project> {
    const res = await fetch(`${BASE_URL}/${id}`);
    const data = await res.json();
    return normalizeProject(data);
  },

  async create(dto: CreateProjectDTO): Promise<Project> {
    const res = await fetch(BASE_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dto),
    });

    const data = await res.json();
    return normalizeProject(data);
  },

  async update(id: string, dto: UpdateProjectDTO): Promise<Project> {
    const res = await fetch(`${BASE_URL}/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dto),
    });

    const data = await res.json();
    return normalizeProject(data);
  },

  async remove(id: string): Promise<void> {
    await fetch(`${BASE_URL}/${id}`, { method: "DELETE" });
  },
};