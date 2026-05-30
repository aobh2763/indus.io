import { Search, X } from 'lucide-react';
import { Input } from '~/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '~/components/ui/select';

import { useProjectUIStore } from '../../features/projects/project.store';

export function ProjectToolbar() {
  const { filters, setFilters } = useProjectUIStore();

  return (
    <div className="flex flex-wrap items-center gap-3">
      {/* Search */}
      <div className="relative flex-1 min-w-[240px]">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground pointer-events-none" />
        <Input
          value={filters.search}
          onChange={(e) => setFilters({ search: e.target.value })}
          placeholder="Search projects…"
          className="pl-9 pr-9"
        />
        {filters.search && (
          <button
            onClick={() => setFilters({ search: '' })}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
            aria-label="Clear search"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Access Level filter */}
      <Select
        value={filters.accessLevel}
        onValueChange={(v) =>
          setFilters({ accessLevel: v as typeof filters.accessLevel })
        }
      >
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="Access Level" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Access Levels</SelectItem>
          <SelectItem value="OWNER">Owner</SelectItem>
          <SelectItem value="SUPERVISOR">Supervisor</SelectItem>
          <SelectItem value="COLLABORATOR">Collaborator</SelectItem>
          <SelectItem value="VIEWER">Viewer</SelectItem>
        </SelectContent>
      </Select>

      {/* Visibility filter */}
      <Select
        value={filters.visibility}
        onValueChange={(v) =>
          setFilters({ visibility: v as typeof filters.visibility })
        }
      >
        <SelectTrigger className="w-[140px]">
          <SelectValue placeholder="Visibility" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Projects</SelectItem>
          <SelectItem value="PUBLIC">Public</SelectItem>
          <SelectItem value="PRIVATE">Private</SelectItem>
        </SelectContent>
      </Select>

      {/* Date range filter */}
      <Select
        value={filters.dateRange}
        onValueChange={(v) =>
          setFilters({ dateRange: v as typeof filters.dateRange })
        }
      >
        <SelectTrigger className="w-[140px]">
          <SelectValue placeholder="Date Range" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Time</SelectItem>
          <SelectItem value="7days">Last 7 Days</SelectItem>
          <SelectItem value="30days">Last 30 Days</SelectItem>
          <SelectItem value="90days">Last 90 Days</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}