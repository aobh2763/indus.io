import { Layers } from "lucide-react";
import Navbar from "~/components/navbar";
import { Protect } from "~/features/auth/components/protect";
import { ProjectsDataTable } from "~/features/projects/components/projects.datatable";

export default function ProjectsManagementPage() {
  return (
    <Protect>
      <div className="min-h-screen bg-black text-neutral-200 font-sans">
        <Navbar />

        <main className="mx-auto max-w-[1600px] px-5 py-6">
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-neutral-800 bg-neutral-900/50">
              <Layers className="h-5 w-5 text-neutral-400" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-white">Projects Management</h1>
              <p className="text-sm text-neutral-500">Track and manage your manufacturing projects</p>
            </div>
          </div>

          <div className="rounded-xl border border-neutral-800 bg-neutral-950/50 p-5 shadow-sm">
            <ProjectsDataTable />
          </div>
        </main>
      </div>
    </Protect>
  );
}
