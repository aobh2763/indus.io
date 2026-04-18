import type { Project } from "../../types/project";
import ProjectCard from "./project-card";

type Props = {
  projects: Project[];
  onDelete: (id: string) => void;
  onAddSupervisor: (id: string) => void;
};

export default function ProjectList({
  projects,
  onDelete,
  onAddSupervisor,
}: Props) {
  if (projects.length === 0) {
    return (
      <div className="text-center text-gray-500 mt-10">
        No projects yet.
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {projects.map((p) => (
        <ProjectCard
          key={p.project_id}
          project={p}
          onDelete={onDelete}
          onAddSupervisor={onAddSupervisor}
        />
      ))}
    </div>
  );
}