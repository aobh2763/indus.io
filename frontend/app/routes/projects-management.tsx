import { Protect } from '~/features/auth/components/protect';
import { ProjectList } from '~/components/projects/project-list';
import { ProjectStats } from '~/components/projects/project-stats';
import { ProjectFormDialog } from '~/components/projects/project-form';
import { ProjectsSidebar } from '~/components/projects/project-sidebar';
import { ProjectAccessDialog } from '~/components/projects/project-access';
import { ProjectDetailSheet } from '~/components/projects/project-detail-sheet';
import Navbar from '~/components/navbar';
import { Button } from '~/components/ui/button';
import { Plus } from 'lucide-react';
import { useProjectUIStore } from '~/features/projects/project.store';

export default function ProjectsPage() {
  const { openCreateDialog } = useProjectUIStore();

  return (
    <Protect>
      <Navbar />
      <div className="flex h-screen overflow-hidden bg-black">
        {/*<ProjectsSidebar />*/}
        <main className="flex flex-1 flex-col overflow-y-auto p-6 gap-6">
          <div className='flex flex-wrap justify-between'>
            <div>
              <h1 className="text-2xl font-semibold tracking-tight">Projects</h1>
              <p className="text-sm text-muted-foreground mt-1">
                Manage your production projects and team access.
              </p>
            </div>

            <Button
              className="gap-2 font-medium"
              size="lg"
              onClick={openCreateDialog}
            >
              <Plus className="h-4 w-4" />
              Create New Project
            </Button>
          </div>

          <ProjectStats />
          <ProjectList />
        </main>
        <ProjectFormDialog />
        <ProjectAccessDialog />
        <ProjectDetailSheet />
      </div>
    </Protect>
  );
}
