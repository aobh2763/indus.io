import type { Project } from "../../types/project";

type Props = {
  project: Project;
  onDelete: (id: string) => void;
  onAddSupervisor: (id: string) => void;
};

export default function ProjectCard({
  project,
  onDelete,
  onAddSupervisor,
}: Props) {
  return (
    <div className="bg-gray-900 p-5 rounded-2xl flex flex-col gap-4 shadow-md hover:shadow-lg transition">
      <div className="flex justify-between items-start">
        <h2 className="text-lg font-semibold text-white">
          {project.name}
        </h2>

        <span className="text-xs px-2 py-1 rounded bg-gray-800 text-gray-300">
          {project.visibility}
        </span>
      </div>
      <div className="space-y-2 text-sm text-gray-300">
        <p>
          <span className="text-gray-500">Manager:</span>{" "}
          {project.project_manager}
        </p>
        <p>
          <span className="text-gray-500">Production Lines:</span>{" "}
          {project.production_lines.length > 0
            ? project.production_lines.join(", ")
            : "None"}
        </p>

        <p>
          <span className="text-gray-500">Supervisors:</span>{" "}
          {project.shift_supervisors.length > 0
            ? project.shift_supervisors.join(", ")
            : "None"}
        </p>
      </div>

      <div className="flex justify-between items-center mt-2">

        <div className="text-xs text-gray-500">
          <p>Created: {new Date(project.created_at).toLocaleDateString()}</p>
          <p>Updated: {new Date(project.updated_at).toLocaleDateString()}</p>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => onAddSupervisor(project.project_id)}
            className="bg-blue-600 px-3 py-1 rounded-lg text-sm hover:bg-blue-700 transition"
          >
            + Supervisor
          </button>

          <button
            onClick={() => onDelete(project.project_id)}
            className="bg-red-500 px-3 py-1 rounded-lg text-sm hover:bg-red-600 transition"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}