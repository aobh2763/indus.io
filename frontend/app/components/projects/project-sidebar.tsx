import {
  AlertTriangle,
  Archive,
  Cog,
  Factory,
  FileText,
  Lightbulb,
  Plus,
  Users,
} from 'lucide-react';
import { Button } from '~/components/ui/button';
import { ScrollArea } from '~/components/ui/scroll-area';
import { Separator } from '~/components/ui/separator';

import { useProjectUIStore } from '../../features/projects/project.store';

interface NavItemProps {
  icon: React.ReactNode;
  label: string;
  active?: boolean;
  onClick?: () => void;
}

function NavItem({ icon, label, active, onClick }: NavItemProps) {
  return (
    <Button
      variant={active ? 'secondary' : 'ghost'}
      className="w-full justify-start gap-3 px-4 py-2.5 h-auto font-normal"
      onClick={onClick}
    >
      <span className="text-muted-foreground">{icon}</span>
      <span>{label}</span>
    </Button>
  );
}

export function ProjectsSidebar() {
  const { openCreateDialog } = useProjectUIStore();

  return (
    <aside className="flex h-full w-64 flex-col border-r bg-card">
      {/* Header */}
      <div className="p-4">
        <Button
          className="w-full gap-2 font-medium"
          size="lg"
          onClick={openCreateDialog}
        >
          <Plus className="h-4 w-4" />
          Create New Project
        </Button>
      </div>

      <Separator />

      {/* Navigation */}
      <ScrollArea className="flex-1 px-2 py-4">
        <nav className="space-y-1">
          <NavItem icon={<FileText className="h-4 w-4" />} label="Drafts" />

          <Separator className="my-3" />

          <p className="px-4 py-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Organization
          </p>

          <NavItem icon={<Users className="h-4 w-4" />} label="Supervisors" />
          <NavItem icon={<Factory className="h-4 w-4" />} label="Production Lines" />

          <Separator className="my-3" />

          <p className="px-4 py-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Management
          </p>

          <NavItem icon={<AlertTriangle className="h-4 w-4" />} label="Alerts" />
          <NavItem icon={<Lightbulb className="h-4 w-4" />} label="Suggestions" />
          <NavItem icon={<Archive className="h-4 w-4" />} label="Archive" />
        </nav>
      </ScrollArea>

      <Separator />

      {/* Footer */}
      <div className="p-2">
        <NavItem icon={<Cog className="h-4 w-4" />} label="Settings" />
      </div>
    </aside>
  );
}