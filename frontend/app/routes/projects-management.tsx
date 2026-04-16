import { ClipboardList, FolderKanban, Plus, Users } from "lucide-react";

export default function ProjectsManagementPage() {
  return (
    <section className="space-y-6">
      <header className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-white">Projects Management</h1>
          <p className="mt-1 text-sm text-zinc-400">Track manufacturing projects, owners, and progress.</p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-md border border-zinc-800 bg-zinc-950 px-3 py-2 text-xs font-medium text-zinc-100 transition hover:border-zinc-700 hover:bg-zinc-900">
          <Plus className="h-4 w-4" />
          New Project
        </button>
      </header>

      <div className="grid gap-4 md:grid-cols-3">
        <InfoCard icon={<FolderKanban className="h-4 w-4" />} title="Total Projects" value="24" />
        <InfoCard icon={<ClipboardList className="h-4 w-4" />} title="In Progress" value="9" />
        <InfoCard icon={<Users className="h-4 w-4" />} title="Assigned Teams" value="6" />
      </div>

      <div className="rounded-xl border border-zinc-900 bg-zinc-950 p-5">
        <p className="text-sm text-zinc-300">Project management module is ready for your CRUD integration.</p>
      </div>
    </section>
  );
}

function InfoCard({ icon, title, value }: { icon: React.ReactNode; title: string; value: string }) {
  return (
    <article className="rounded-xl border border-zinc-900 bg-zinc-950 p-4">
      <div className="flex items-center justify-between text-zinc-400">
        <span className="text-xs uppercase tracking-wider">{title}</span>
        {icon}
      </div>
      <p className="mt-3 text-2xl font-semibold text-white">{value}</p>
    </article>
  );
}
