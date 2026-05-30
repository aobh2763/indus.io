
import { create } from 'zustand';
import type { ProjectResponse, ProjectListResponse } from './project.schema';

export type VisibilityFilter = 'all' | 'PUBLIC' | 'PRIVATE';
export type AccessLevelFilter = 'all' | 'OWNER' | 'SUPERVISOR' | 'COLLABORATOR' | 'VIEWER';
export type DateRangeFilter = 'all' | '7days' | '30days' | '90days';

export interface ProjectFilters {
  search: string;
  visibility: VisibilityFilter;
  accessLevel: AccessLevelFilter;
  dateRange: DateRangeFilter;
}

interface ProjectUIStore {
  selectedProject: ProjectResponse | null;
  isSheetOpen: boolean;
  selectProject: (project: ProjectResponse | null) => void;

  // ── Create / Edit dialog ─
  isFormDialogOpen: boolean;
  editingProject: ProjectResponse | null;
  openCreateDialog: () => void;
  openEditDialog: (project: ProjectResponse) => void;
  closeFormDialog: () => void;

  // ── Access dialog ──
  isAccessDialogOpen: boolean;
  accessProjectId: string | null;
  openAccessDialog: (project: ProjectResponse) => void;
  closeAccessDialog: () => void;

  // ── Filters ──
  filters: ProjectFilters;
  setFilters: (partial: Partial<ProjectFilters>) => void;
  resetFilters: () => void;
}

const DEFAULT_FILTERS: ProjectFilters = {
  search: '',
  visibility: 'all',
  accessLevel: 'all',
  dateRange: 'all',
};

export const useProjectUIStore = create<ProjectUIStore>((set) => ({
  // ── Detail sheet ───
  selectedProject: null,
  isSheetOpen: false,
  selectProject: (project) =>
    set({ selectedProject: project, isSheetOpen: project !== null }),

  // ── Form dialog ────
  isFormDialogOpen: false,
  editingProject: null,
  openCreateDialog: () =>
    set({ isFormDialogOpen: true, editingProject: null }),
  openEditDialog: (project) =>
    set({ isFormDialogOpen: true, editingProject: project }),
  closeFormDialog: () =>
    set({ isFormDialogOpen: false, editingProject: null }),

  // ── Access dialog ──
  isAccessDialogOpen: false,
  accessProjectId: null,
  openAccessDialog: (project) =>
    set({ isAccessDialogOpen: true, accessProjectId: project.id }),
  closeAccessDialog: () =>
    set({ isAccessDialogOpen: false, accessProjectId: null }),

  // ── Filters ──
  filters: DEFAULT_FILTERS,
  setFilters: (partial) =>
    set((s) => ({ filters: { ...s.filters, ...partial } })),
  resetFilters: () => set({ filters: DEFAULT_FILTERS }),
}));

export function filterProjects(
  projects: ProjectListResponse,
  filters: ProjectFilters,
): ProjectListResponse {
  const search = filters.search.trim().toLowerCase();

  const cutoff: Record<Exclude<DateRangeFilter, 'all'>, number> = {
    '7days': 7,
    '30days': 30,
    '90days': 90,
  };

  return projects.filter((p) => {
    if (search && !p.name.toLowerCase().includes(search) && !p.description?.toLowerCase().includes(search)) {
      return false;
    }
    if (filters.visibility !== 'all' && p.visibility !== filters.visibility) {
      return false;
    }
    if (filters.dateRange !== 'all') {
      const days = cutoff[filters.dateRange];
      const threshold = Date.now() - days * 24 * 60 * 60 * 1000;
      if (new Date(p.created_at).getTime() < threshold) return false;
    }
    return true;
  });
}