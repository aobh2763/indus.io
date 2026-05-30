import { AlertCircle, FolderOpen, Search, X } from 'lucide-react';

import { Alert, AlertDescription, AlertTitle } from '~/components/ui/alert';
import { Button } from '~/components/ui/button';
import { Input } from '~/components/ui/input';
import { Tabs, TabsList, TabsTrigger } from '~/components/ui/tabs';

import { useProjectUIStore, filterProjects } from '../../features/projects/project.store';
import { useGetProjects } from '../../features/projects/project.hooks';
import { ProjectCard, ProjectCardSkeleton } from './project-card';

function EmptyState({ hasFilters }: { hasFilters: boolean }) {
  const { openCreateDialog, resetFilters } = useProjectUIStore();

  return (
    <div className="col-span-full flex flex-col items-center justify-center rounded-xl border border-dashed py-16 px-4 text-center">
      <div className="mb-4 rounded-full bg-muted p-3">
        <FolderOpen className="h-6 w-6 text-muted-foreground" />
      </div>
      {hasFilters ? (
        <>
          <p className="font-medium text-sm">No projects match your filters</p>
          <p className="mt-1 text-xs text-muted-foreground max-w-[240px]">
            Try adjusting your search or changing the visibility filter.
          </p>
          <Button
            variant="outline"
            size="sm"
            className="mt-4"
            onClick={resetFilters}
          >
            <X className="mr-2 h-3.5 w-3.5" />
            Clear Filters
          </Button>
        </>
      ) : (
        <>
          <p className="font-medium text-sm">No projects yet</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Create your first project to get started.
          </p>
          <Button size="sm" className="mt-4" onClick={openCreateDialog}>
            Create Project
          </Button>
        </>
      )}
    </div>
  );
}
export function ProjectList() {
  const { filters, setFilters } = useProjectUIStore();
  const { data: allProjects = [], isLoading, isError, error } = useGetProjects();

  const projects = filterProjects(allProjects, filters);
  const hasActiveFilters =
    filters.search.trim() !== '' || filters.visibility !== 'all';

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center gap-3">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground pointer-events-none" />
          <Input
            value={filters.search}
            onChange={(e) => setFilters({ search: e.target.value })}
            placeholder="Search projects…"
            className="pl-8"
          />
          {filters.search && (
            <button
              onClick={() => setFilters({ search: '' })}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
              aria-label="Clear search"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>

        {/* Visibility filter tabs */}
        <Tabs
          value={filters.visibility}
          onValueChange={(v) =>
            setFilters({ visibility: v as typeof filters.visibility })
          }
        >
          <TabsList>
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="PUBLIC">Public</TabsTrigger>
            <TabsTrigger value="PRIVATE">Private</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {isError && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Something went wrong</AlertTitle>
          <AlertDescription>
            {error instanceof Error ? error.message : 'Failed to load projects.'}
          </AlertDescription>
        </Alert>
      )}

      {/* ── Card grid ──────────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {isLoading && allProjects.length === 0
          ? Array.from({ length: 6 }).map((_, i) => (
              <ProjectCardSkeleton key={i} />
            ))
          : projects.length === 0
          ? <EmptyState hasFilters={hasActiveFilters} />
          : projects.map((p) => <ProjectCard key={p.id} project={p} />)}
      </div>

      {/* ── Results count ──────────────────────────────────────────────────── */}
      {!isLoading && projects.length > 0 && (
        <p className="text-xs text-muted-foreground">
          Showing {projects.length} project{projects.length !== 1 ? 's' : ''}
          {hasActiveFilters ? ' matching your filters' : ''}
        </p>
      )}
    </div>
  );
}