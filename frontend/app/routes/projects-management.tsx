import { ProjectsSidebar } from '~/components/projects/project-sidebar';
import { ProjectStats } from '~/components/projects/project-stats';
import { ProjectList } from '~/components/projects/project-list';
import { ProjectFormDialog } from '~/components/projects/project-form';
import { ProjectAccessDialog } from '~/components/projects/project-access';
import { ProjectDetailSheet } from '~/components/projects/project-detail-sheet';


export default function ProjectsPage() {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <ProjectsSidebar />
      <main className="flex flex-1 flex-col overflow-y-auto p-6 gap-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Projects</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Manage your production projects and team access.
          </p>
        </div>
        <ProjectStats />
        <ProjectList />
      </main>
      <ProjectFormDialog />
      <ProjectAccessDialog />
      <ProjectDetailSheet />
    </div>
  );
}