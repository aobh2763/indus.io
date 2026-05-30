import {
  CalendarDays,
  Clock,
  Edit2,
  Globe,
  Lock,
  Shield,
  Copy,
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
import { ScrollArea } from '~/components/ui/scroll-area';
import { Separator } from '~/components/ui/separator';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '~/components/ui/sheet';

import { useProjectUIStore } from '../../features/projects/project.store';
import { useDeleteProject } from '../../features/projects/project.hooks';
function DetailRow({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className="flex items-start gap-3 py-2.5">
      <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-muted text-muted-foreground">
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-0.5">
          {label}
        </p>
        <div className="text-sm text-foreground">{value}</div>
      </div>
    </div>
  );
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground py-1">
      {children}
    </p>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export function ProjectDetailSheet() {
  const {
    selectedProject,
    isSheetOpen,
    selectProject,
    openEditDialog,
    openAccessDialog,
  } = useProjectUIStore();

  const deleteProject = useDeleteProject();

  if (!selectedProject) return null;

  const p = selectedProject;
  const isDeleting = deleteProject.isPending;
  const isPublic = p.visibility === 'PUBLIC';
  const canEditPipeline = p.current_user_access_level === 'OWNER' || p.current_user_access_level === 'COLLABORATOR';
  const canManageProject = p.current_user_access_level === 'OWNER';

  const fmt = (date: Date | string) =>
    new Intl.DateTimeFormat('en-US', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(date));

  return (
    <Sheet open={isSheetOpen} onOpenChange={(o) => !o && selectProject(null)}>
      <SheetContent className="w-[400px] sm:w-[440px] p-0 flex flex-col">
        <SheetHeader className="px-6 pt-6 pb-4">
          <div className="flex items-center gap-3">
            <Avatar className="h-10 w-10">
              <AvatarFallback className="bg-primary/10 text-primary font-semibold text-base">
                {p.name.charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <SheetTitle className="truncate text-base">{p.name}</SheetTitle>
              <SheetDescription className="mt-0.5">
                Project details and access management
              </SheetDescription>
            </div>
          </div>
          <div className="mt-3">
            <Badge
              variant={isPublic ? 'default' : 'secondary'}
              className="gap-1.5"
            >
              {isPublic ? (
                <Globe className="h-3 w-3" />
              ) : (
                <Lock className="h-3 w-3" />
              )}
              {isPublic ? 'Public' : 'Private'}
            </Badge>
          </div>
        </SheetHeader>

        <Separator />

        <ScrollArea className="flex-1 px-6">
          <div className="py-4 space-y-1">
            {p.description && (
              <>
                <SectionTitle>Description</SectionTitle>
                <p className="text-sm text-muted-foreground leading-relaxed pb-3">
                  {p.description}
                </p>
                <Separator className="my-3" />
              </>
            )}

            <SectionTitle>Details</SectionTitle>

            <DetailRow
              icon={isPublic ? <Globe className="h-4 w-4" /> : <Lock className="h-4 w-4" />}
              label="Visibility"
              value={<span className="capitalize">{isPublic ? 'Public' : 'Private'}</span>}
            />

            <DetailRow
              icon={<Shield className="h-4 w-4" />}
              label="Your Access"
              value={p.current_user_access_level ?? (isPublic ? 'Public viewer' : 'No direct access')}
            />

            <DetailRow
              icon={<Copy className="h-4 w-4" />}
              label="Clone Permission"
              value={p.current_user_can_clone || p.current_user_access_level === 'OWNER' ? 'Allowed' : 'Not allowed'}
            />

            <DetailRow
              icon={<Edit2 className="h-4 w-4" />}
              label="Pipeline Access"
              value={canEditPipeline ? 'Can modify original pipeline' : 'View only'}
            />

            <DetailRow
              icon={<CalendarDays className="h-4 w-4" />}
              label="Created"
              value={fmt(p.created_at)}
            />

            <DetailRow
              icon={<Clock className="h-4 w-4" />}
              label="Last Updated"
              value={fmt(p.updated_at)}
            />

            <Separator className="my-3" />
            <SectionTitle>Identifier</SectionTitle>

            <DetailRow
              icon={<span className="font-mono text-[10px] font-bold">#</span>}
              label="Project ID"
              value={
                <code className="block rounded bg-muted px-2 py-1 font-mono text-xs break-all text-muted-foreground">
                  {p.id}
                </code>
              }
            />
          </div>
        </ScrollArea>

        <Separator />

        {/* ── Footer actions ───────────────────────────────────────────────── */}
        <div className="px-6 py-4 flex flex-col gap-2">
          {canManageProject && (
            <>
              <Button
                variant="default"
                className="w-full justify-start gap-2"
                onClick={() => openEditDialog(p)}
              >
                <Edit2 className="h-4 w-4" />
                Edit Project
              </Button>

              <Button
                variant="outline"
                className="w-full justify-start gap-2"
                onClick={() => openAccessDialog(p)}
              >
                <Shield className="h-4 w-4" />
                Manage Access
              </Button>

              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button
                    variant="ghost"
                    className="w-full justify-start gap-2 text-destructive hover:text-destructive hover:bg-destructive/10"
                    disabled={isDeleting}
                  >
                    <Trash2 className="h-4 w-4" />
                    Delete Project
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Delete "{p.name}"?</AlertDialogTitle>
                    <AlertDialogDescription>
                      This action cannot be undone. The project and all its
                      associated data will be permanently removed.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction
                      className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                      onClick={() => {
                        deleteProject.mutate(p.id, {
                          onSuccess: () => selectProject(null),
                        });
                      }}
                    >
                      Delete Project
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </>
          )}

          {!canManageProject && (
            <Button
              variant="outline"
              className="w-full justify-start gap-2"
              disabled
            >
              <Shield className="h-4 w-4" />
              Project settings are owner-only
            </Button>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
