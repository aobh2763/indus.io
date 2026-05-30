import { Activity, FolderKanban, Globe, Lock } from 'lucide-react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '~/components/ui/card';
import { Skeleton } from '~/components/ui/skeleton';

import { useGetProjects } from '../../features/projects/project.hooks';

interface StatCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  description?: string;
  loading?: boolean;
}

function StatCard({ title, value, icon, description, loading }: StatCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <div className="text-muted-foreground">{icon}</div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <Skeleton className="h-8 w-16" />
        ) : (
          <>
            <div className="text-3xl font-bold tabular-nums">{value}</div>
            {description && (
              <p className="mt-1 text-xs text-muted-foreground">{description}</p>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export function ProjectStats() {
  const { data: projects = [], isLoading } = useGetProjects();

  const loading = isLoading && projects.length === 0;

  const total = projects.length;

  const active = projects.filter((p) => {
    const thirtyDaysAgo = Date.now() - 30 * 24 * 60 * 60 * 1000;
    return new Date(p.created_at).getTime() > thirtyDaysAgo;
  }).length;

  const publicCount = projects.filter((p) => p.visibility === 'PUBLIC').length;
  const privateCount = projects.filter((p) => p.visibility === 'PRIVATE').length;

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <StatCard
        title="Total Projects"
        value={total}
        icon={<FolderKanban className="h-4 w-4" />}
        description="All projects in workspace"
        loading={loading}
      />
      <StatCard
        title="Active Projects"
        value={active}
        icon={<Activity className="h-4 w-4" />}
        description="Created in last 30 days"
        loading={loading}
      />
      <StatCard
        title="Public"
        value={publicCount}
        icon={<Globe className="h-4 w-4" />}
        description="Visible to everyone"
        loading={loading}
      />
      <StatCard
        title="Private"
        value={privateCount}
        icon={<Lock className="h-4 w-4" />}
        description="Restricted access"
        loading={loading}
      />
    </div>
  );
}