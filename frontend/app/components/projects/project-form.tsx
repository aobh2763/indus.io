import { useEffect, useState } from 'react';
import { Loader2 } from 'lucide-react';

import { Badge } from '~/components/ui/badge';
import { Button } from '~/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '~/components/ui/dialog';
import { Input } from '~/components/ui/input';
import { Label } from '~/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '~/components/ui/select';
import { Textarea } from '~/components/ui/textarea';

import { useProjectUIStore } from '../../features/projects/project.store';
import { useCreateProject, useUpdateProject } from '../../features/projects/project.hooks';
import type { CreateProjectRequest, UpdateProjectRequest, Visibility } from '../../features/projects/project.schema';

interface FormState {
  name: string;
  description: string;
  visibility: Visibility;
}

const DEFAULT_FORM: FormState = {
  name: '',
  description: '',
  visibility: 'PRIVATE',
};

export function ProjectFormDialog() {
  const {
    isFormDialogOpen,
    editingProject,
    closeFormDialog,
  } = useProjectUIStore();

  const createProject = useCreateProject();
  const updateProject = useUpdateProject();

  const isEditing = editingProject !== null;
  const isSubmitting = createProject.isPending || updateProject.isPending;

  const [form, setForm] = useState<FormState>(DEFAULT_FORM);

  useEffect(() => {
    if (editingProject) {
      setForm({
        name: editingProject.name,
        description: editingProject.description ?? '',
        visibility: editingProject.visibility,
      });
    } else {
      setForm(DEFAULT_FORM);
    }
  }, [editingProject, isFormDialogOpen]);

  const set = <K extends keyof FormState>(key: K, value: FormState[K]) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const handleSubmit = () => {
    if (isEditing && editingProject) {
      const dto: UpdateProjectRequest = {
        name: form.name.trim(),
        description: form.description.trim() || undefined,
        visibility: form.visibility,
      };
      updateProject.mutate(
        { id: editingProject.id, data: dto },
        { onSuccess: closeFormDialog },
      );
    } else {
      const dto: CreateProjectRequest = {
        name: form.name.trim(),
        description: form.description.trim() || undefined,
        visibility: form.visibility,
      };
      createProject.mutate(dto, { onSuccess: closeFormDialog });
    }
  };

  return (
    <Dialog open={isFormDialogOpen} onOpenChange={(o) => !o && closeFormDialog()}>
      <DialogContent className="sm:max-w-[480px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {isEditing ? 'Edit Project' : 'Create New Project'}
            {isEditing && (
              <Badge variant="outline" className="text-xs font-normal">
                Editing
              </Badge>
            )}
          </DialogTitle>
          <DialogDescription>
            {isEditing
              ? 'Update the project details below.'
              : 'Fill in the details to create a new project in your workspace.'}
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-5 py-2">
          {/* Name */}
          <div className="grid gap-1.5">
            <Label htmlFor="proj-name">
              Name <span className="text-destructive">*</span>
            </Label>
            <Input
              id="proj-name"
              value={form.name}
              onChange={(e) => set('name', e.target.value)}
              placeholder="e.g. Q4 Production Run"
              maxLength={200}
              autoFocus
            />
            <p className="text-xs text-muted-foreground">
              {form.name.length}/200 characters
            </p>
          </div>

          {/* Description */}
          <div className="grid gap-1.5">
            <Label htmlFor="proj-desc">Description</Label>
            <Textarea
              id="proj-desc"
              value={form.description}
              onChange={(e) => set('description', e.target.value)}
              placeholder="What is this project about?"
              className="resize-none"
              rows={3}
            />
          </div>

          {/* Visibility */}
          <div className="grid gap-1.5">
            <Label htmlFor="proj-vis">Visibility</Label>
            <Select
              value={form.visibility}
              onValueChange={(v) => set('visibility', v as Visibility)}
            >
              <SelectTrigger id="proj-vis">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="PRIVATE">
                  <div className="flex flex-col">
                    <span>Private</span>
                    <span className="text-xs text-muted-foreground">
                      Only visible to invited members
                    </span>
                  </div>
                </SelectItem>
                <SelectItem value="PUBLIC">
                  <div className="flex flex-col">
                    <span>Public</span>
                    <span className="text-xs text-muted-foreground">
                      Visible to everyone in your workspace
                    </span>
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={closeFormDialog} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting || form.name.trim().length === 0}
          >
            {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {isEditing ? 'Save Changes' : 'Create Project'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}