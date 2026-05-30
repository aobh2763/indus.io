import {
  CalendarDays,
  Edit2,
  Globe,
  Lock,
  MoreHorizontal,
  Shield,
  Trash2,
} from 'lucide-react';

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '~/components/ui/alert-dialog';
import { Avatar, AvatarFallback } from '~/components/ui/avatar';
import { Badge } from '~/components/ui/badge';
import { Button } from '~/components/ui/button';
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from '~/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '~/components/ui/dropdown-menu';
import { Skeleton } from '~/components/ui/skeleton';

import { useProjectUIStore } from '../../features/projects/project.store';
import { useDeleteProject } from '../../features/projects/project.hooks';
import type { ProjectResponse } from '../../features/projects/project.schema';
import { productionLinesApi } from '~/features/pipeline/pipeline.api';
import { PipelineStatus } from '~/features/pipeline/pipeline.schema';
import { useNavigate } from 'react-router';
import { usePipelineStore } from '~/features/pipeline/pipeline.store';


interface ProjectCardProps {
  project: ProjectResponse;
}

export function ProjectCard({ project: p }: ProjectCardProps) {
  const navigate = useNavigate();
  const { setLineId } = usePipelineStore();

  const { selectProject, openEditDialog, openAccessDialog } = useProjectUIStore();
  const deleteProject = useDeleteProject();

  const formattedDate = new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
  }).format(new Date(p.created_at));

  const isPublic = p.visibility === 'PUBLIC';

  async function handleOpenInPipelineEditor(project: ProjectResponse) {
    let pId: string | null = null;
    const productionLines = await productionLinesApi.get(project.id);

    if (productionLines.length === 0) {
      const productionLine = await productionLinesApi.create(project.id, {
        name: "default",
        status: PipelineStatus.DRAFT,
      });

      pId = productionLine.id;
    } else {
      const sorted = productionLines.sort((a, b) => Number(a.id > b.id));
      pId = sorted[0].id;
    }

    if (pId) {
      setLineId(pId);
      navigate('/pipeline-builder');
    }
  }

  return (
    <Card
      className={[
        'group relative flex flex-col transition-all duration-200 cursor-pointer',
        'hover:shadow-md hover:-translate-y-0.5',
        'border-border/60 hover:border-border',
      ].join(' ')}
    >
      <CardHeader
        className="pb-3"
        onClick={() => selectProject(p)}
      >
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2.5 min-w-0">
            <Avatar className="h-9 w-9 shrink-0">
              <AvatarFallback className="bg-primary/10 text-primary font-semibold">
                {p.name.charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div className="min-w-0">
              <p className="font-semibold text-sm leading-tight truncate">
                {p.name}
              </p>
              <Badge
                variant={isPublic ? 'default' : 'secondary'}
                className="mt-1 gap-1 text-[11px] py-0 h-4"
              >
                {isPublic ? (
                  <Globe className="h-2.5 w-2.5" />
                ) : (
                  <Lock className="h-2.5 w-2.5" />
                )}
                {isPublic ? 'Public' : 'Private'}
              </Badge>
            </div>
          </div>

          {/* Kebab menu — stops propagation so clicking it doesn't open the Sheet */}
          <AlertDialog>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={(e) => e.stopPropagation()}
                >
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>

              <DropdownMenuContent
                align="end"
                className="w-44"
                onClick={(e) => e.stopPropagation()}
              >
                <DropdownMenuItem
                  onClick={() => openEditDialog(p)}
                  className="gap-2"
                >
                  <Edit2 className="h-3.5 w-3.5" /> Edit
                </DropdownMenuItem>

                <DropdownMenuItem
                  onClick={() => openAccessDialog(p)}
                  className="gap-2"
                >
                  <Shield className="h-3.5 w-3.5" /> Manage Access
                </DropdownMenuItem>

                <DropdownMenuSeparator />

                <AlertDialogTrigger asChild>
                  <DropdownMenuItem
                    className="gap-2 text-destructive focus:text-destructive"
                    onSelect={(e) => e.preventDefault()}
                  >
                    <Trash2 className="h-3.5 w-3.5" /> Delete
                  </DropdownMenuItem>
                </AlertDialogTrigger>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Delete confirmation */}
            <AlertDialogContent onClick={(e) => e.stopPropagation()}>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete "{p.name}"?</AlertDialogTitle>
                <AlertDialogDescription>
                  This cannot be undone. All project data will be permanently
                  removed.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction
                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                  onClick={() => deleteProject.mutate(p.id)}
                >
                  Delete
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </CardHeader>

      {/* ── Description ─────────────────────────────────────────────────── */}
      <CardContent className="flex-1 pb-3">
        {p.description ? (
          <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
            {p.description}
          </p>
        ) : (
          <p className="text-xs text-muted-foreground/40 italic">
            No description provided.
          </p>
        )}
      </CardContent>

      {/* ── Footer ──────────────────────────────────────────────────────── */}
      <CardFooter className='flex justify-between'>
        <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
          <CalendarDays className="h-3 w-3" />
          <span>Created {formattedDate}</span>
        </div>
        <Button
          size="sm"
          variant="outline"
          onClick={() => handleOpenInPipelineEditor(p)}
        >
          Open in pipeline editor
        </Button>
      </CardFooter>
    </Card>
  );
}

export function ProjectCardSkeleton() {
  return (
    <Card className="flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2.5">
          <Skeleton className="h-9 w-9 rounded-full" />
          <div className="space-y-1.5 flex-1">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3.5 w-16" />
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-1 pb-3 space-y-1.5">
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-2/3" />
      </CardContent>
      <CardFooter className="pb-3">
        <Skeleton className="h-3 w-28" />
      </CardFooter>
    </Card>
  );
}
