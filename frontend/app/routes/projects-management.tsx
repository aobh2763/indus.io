import { useEffect, useState } from "react";
import { ProjectsService } from "../services/projects.service";
import ProjectForm from "../../components/project/project-form";
import ProjectList from "../../components/project/project-list";
import type {
  Project,
  CreateProjectDTO,
} from "../../types/project";

export default function ProjectManagementPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  const [form, setForm] = useState<CreateProjectDTO>({
    name: "",
    project_manager: "",
    visibility: "private",
    production_lines: [],
    shift_supervisors: [],
  });

  const fetchProjects = async () => {
    setLoading(true);
    const data = await ProjectsService.getAll();
    setProjects(data);
    setLoading(false);
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreate = async () => {
    const created = await ProjectsService.create(form);
    setProjects((prev) => [created, ...prev]); // new on top
  };

  const handleDelete = async (id: string) => {
    await ProjectsService.remove(id);
    setProjects((prev) =>
      prev.filter((p) => p.project_id !== id)
    );
  };

  const handleAddSupervisor = (id: string) => {
    console.log("Add supervisor to project:", id);
  };

  return (
    <div className="p-6 text-white space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-semibold tracking-tight">
          Project Management
        </h1>

        <span className="text-sm text-gray-400">
          {projects.length} project{projects.length !== 1 && "s"}
        </span>
      </div>

      {/* Form Section */}
      <div className="bg-gray-900 rounded-2xl p-5 shadow-md">
        <h2 className="text-lg font-medium mb-4 text-gray-200">
          Create New Project
        </h2>

        <ProjectForm
          form={form}
          setForm={setForm}
          onSubmit={handleCreate}
        />
      </div>
      <div className="space-y-4">
        <h2 className="text-lg font-medium text-gray-200">
          Projects
        </h2>

        {loading ? (
          <div className="text-gray-400 text-sm animate-pulse">
            Loading projects...
          </div>
        ) : (
          <ProjectList
            projects={projects}
            onDelete={handleDelete}
            onAddSupervisor={handleAddSupervisor}
          />
        )}
      </div>
    </div>
  );
}