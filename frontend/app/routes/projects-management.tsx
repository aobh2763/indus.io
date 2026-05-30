import { Protect } from '~/features/auth/components/protect';
import { ProjectList } from '~/components/projects/project-list';
import { ProjectStats } from '~/components/projects/project-stats';
import { ProjectFormDialog } from '~/components/projects/project-form';
import { ProjectsSidebar } from '~/components/projects/project-sidebar';
import { ProjectAccessDialog } from '~/components/projects/project-access';
import { ProjectDetailSheet } from '~/components/projects/project-detail-sheet';
import { ProjectNotifications } from '~/components/projects/project-notifications';
import Navbar from '~/components/navbar';
import { Button } from '~/components/ui/button';
import { Plus } from 'lucide-react';
import { useProjectUIStore } from '~/features/projects/project.store';

export default function ProjectsPage() {
  const { openCreateDialog } = useProjectUIStore();

  return (
    <Protect>
      <Navbar />
      <div className="min-h-screen bg-black text-neutral-200">
        {/*<ProjectsSidebar />*/}
        <main className="mx-auto flex max-w-[1600px] flex-col gap-6 px-5 py-6">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-white">Projects</h1>
              <p className="mt-1 text-sm text-neutral-500">
                Manage your production projects and team access.
              </p>
            </div>

            <Button
              className="gap-2 border border-neutral-700 bg-white text-black hover:bg-neutral-200"
              size="sm"
              onClick={openCreateDialog}
            >
              <Plus className="h-4 w-4" />
              Create Project
            </Button>
          </div>

          <ProjectStats />
          <div className="grid grid-cols-1 gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
            <ProjectList />
            <ProjectNotifications />
          </div>
        </main>
        <ProjectFormDialog />
        <ProjectAccessDialog />
        <ProjectDetailSheet />
      </div>
    </Protect>
  );
}
